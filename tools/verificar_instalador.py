"""Validate the local installer in a marked synthetic profile; no real shell registration.

Run from the repository after packaging/build_local.py. Evidence is retained under
verificacion-local/instalador/ejecucion-*. No user documents are opened or removed.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,mmap,os,re,shutil,socket,sqlite3,subprocess,sys,time,urllib.request,uuid,winreg,zipfile
root=Path(__file__).resolve().parents[1]
base=root/'verificacion-local/instalador'
base.mkdir(parents=True,exist_ok=True)
out=base/('ejecucion-'+uuid.uuid4().hex[:8]);out.mkdir()
build=json.loads((root/'dist-local/build.json').read_text(encoding='utf-8'))
installer=Path(build['installer']);payload=root/'dist-local/payload.zip'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={}
assert sha(installer)==build['sha256']
assert sha(payload)==build['payload_sha256']
assert (installer.with_suffix('.exe.sha256')).read_text(encoding='utf-8').split()[0]==build['sha256']
print('SHA-256 del instalador y payload correctos',flush=True)
with zipfile.ZipFile(payload) as z:
 manifest=json.loads(z.read('manifest.json'));names=z.namelist()
 assert len(names)==len(set(names))
 assert set(names)==set(manifest)|{'manifest.json'}
 forbidden=[]
 for name in names:
  parts=Path(name).parts;lower=name.lower()
  assert not name.startswith(('/','\\')) and '..' not in parts
  if set(p.lower() for p in parts)&{'.data','.git','.venv','wheelhouse','verificacion-local','node_modules','__pycache__'} or lower.endswith(('.sqlite','.sqlite3','.p8','.jwt','.pyc','.pyo')) or Path(name).name.lower() in ('oauth.toml','secrets.toml','oauth-popup.js','.env'):
   forbidden.append(name)
  if name in manifest:
   with z.open(name) as source:actual=hashlib.file_digest(source,'sha256').hexdigest()
   assert actual==manifest[name],name
 assert not forbidden,forbidden
 for name in ['README.md','LOCAL.md','PREPARACION.md','INSTALACION.md','LICENCIAS.md','CONDICIONES-ENTREGA.md','dependencias-publicas.json','tools/verificar_instalacion.py']:
  assert 'app/'+name in manifest,name
 # Check the links of every Markdown document included in app/.
 links=0
 import posixpath
 for name in names:
  if name.startswith('app/') and name.endswith('.md'):
   for target in re.findall(r'\]\(([^)]+)\)',z.read(name).decode('utf-8')):
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
    links+=1
    resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),target.split('#')[0]))
    assert resolved in names or any(n.startswith(resolved.rstrip('/')+'/') for n in names),(name,target)
report['content']={'files':len(manifest),'sha256_entries_verified':len(manifest),'forbidden_files':forbidden,'packaged_local_links_verified':links,'exe_sha256':build['sha256'],'payload_sha256':build['payload_sha256']}
print('Contenido y enlaces internos del paquete verificados',flush=True)
# Snapshot only shell integration/configuration, without opening user documents.
def real_state():
 result={}
 for name in ['Anonimizar','Anonimous']:
  try:
   with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\'+name) as key:
    values=[];i=0
    while True:
     try:values.append(winreg.EnumValue(key,i));i+=1
     except OSError:break
    result['registry-'+name]=hashlib.sha256(repr(sorted(values)).encode()).hexdigest()
  except FileNotFoundError:result['registry-'+name]=None
  pointer=Path(os.environ['LOCALAPPDATA'])/'Programs'/name/'current.txt'
  result['pointer-'+name]=sha(pointer) if pointer.exists() else None
 return result
state=real_state()
test=out/('perfil-'+uuid.uuid4().hex[:8]);test.mkdir()
(test/'.anonimizar-installer-test').write_text('Anonimizar isolated installer test 0.3.0',encoding='utf-8')
legacy=test/'Anonimous';legacy.mkdir();(legacy/'settings.json').write_text(json.dumps({'history_enabled':True,'preferences':{'doc_operator':'replace'}}),encoding='utf-8')
with sqlite3.connect(legacy/'documents.sqlite3') as db:
 db.execute('CREATE TABLE documents (id TEXT PRIMARY KEY, owner TEXT, title TEXT, payload TEXT, updated REAL)')
 db.execute('INSERT INTO documents VALUES (?,?,?,?,?)',('ficticio-1','local','Documento ficticio',json.dumps({'text':'HISTORIAL FICTICIO DE PRUEBA','settings':{},'review':{}}),1.0))
legacy_before={p.name:sha(p) for p in legacy.iterdir() if p.is_file()}
flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
def setup(exe=installer,where=test,expect=0):
 with (out/('setup-'+where.name+'.log')).open('w',encoding='utf-8') as log:
  done=subprocess.run([str(exe),'--quiet-test','--test-root',str(where)],stdout=log,stderr=log,timeout=600,creationflags=flags)
 assert done.returncode==expect,(str(exe),done.returncode)
setup()
print('Instalacion aislada completada',flush=True)
installed=Path((test/'Programs/Anonimizar/current.txt').read_text().strip())
assert installed.is_relative_to(test)
assert (installed/'installed.ok').read_text()==build['payload_sha256']
assert (test/'Anonimizar/settings.json').read_bytes()==(legacy/'settings.json').read_bytes()
with sqlite3.connect(test/'Anonimizar/documents.sqlite3') as db:assert db.execute('SELECT title FROM documents').fetchone()[0]=='Documento ficticio'
assert legacy_before=={p.name:sha(p) for p in legacy.iterdir() if p.is_file()}
assert (test/'Desktop/Anonimizar.lnk').is_file() and (test/'StartMenu/Anonimizar/Anonimizar.lnk').is_file()
registration = json.loads((test/'registration-test.json').read_text())
assert registration['NormalRegistrationModified'] is False and registration['TestRegistryModified'] is True
with winreg.OpenKey(winreg.HKEY_CURRENT_USER,registration['RegistryPath']) as test_key:
 assert winreg.QueryValueEx(test_key,'InstallLocation')[0]==str(installed)
assert real_state()==state
# Verify every installed byte before launching Python (which can create bytecode caches).
def check_installed(item):
 name,expected=item
 return name if sha(installed/name)!=expected else None
with ThreadPoolExecutor(max_workers=8) as pool:bad=[name for name in pool.map(check_installed,manifest.items()) if name]
assert not bad,bad
report['installation']={'isolated_root':str(test),'installed_files_verified':len(manifest),'longest_installed_path':max(len(str(installed/name)) for name in manifest),'legacy_synthetic_history_preserved':True,'legacy_original_bytes_preserved':True,'isolated_shortcuts_created':True,'real_registry_and_pointers_unchanged':True,'separate_test_registry_key_verified':True}
print('Archivos instalados, migracion ficticia y aislamiento verificados',flush=True)
env=dict(os.environ,ANONIMIZAR_DATA_DIR=str(test/'Anonimizar'),LOCALAPPDATA=str(test),PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1',TLDEXTRACT_CACHE=str(test/'cache'),ANONIMIZAR_DOCUMENTS_DB=str(test/'Anonimizar/documents.sqlite3'),ANONIMIZAR_LEGACY_DB=str(test/'legacy-absent.sqlite3'))
env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
python=installed/'runtime/python.exe'
with (out/'runtime-sintetico.log').open('w',encoding='utf-8') as log:
 subprocess.run([str(python),'-I',str(installed/'app/tools/verificar_instalacion.py')],env=env,cwd=installed/'app',stdout=log,stderr=log,timeout=150,check=True,creationflags=flags)
# The installed runtime executes the real copied page and history functions.
check=out/'comprobar_app_instalada.py'
check.write_text("""import json,os,sys,tempfile
from pathlib import Path
app=Path(sys.argv[1]);sys.path.insert(0,str(app));os.chdir(app)
from streamlit.testing.v1 import AppTest
page=AppTest.from_file(str(app/'presidio_streamlit.py'),default_timeout=90).run()
assert not page.exception,[str(e.value) for e in page.exception]
from anonimizar_documents import save,load,move_to_trash,restore_trash,export_history,import_history,LOCAL_OWNER
payload={'text':'DOCUMENTO NUEVO FICTICIO','settings':{},'review':{}}
identifier=save(LOCAL_OWNER,payload);assert load(LOCAL_OWNER,identifier)==payload
backup=export_history();move_to_trash(identifier);assert load(LOCAL_OWNER,identifier) is None
restore_trash();assert load(LOCAL_OWNER,identifier)==payload
assert import_history(backup)>=1
print('AppTest e historial ficticio: guardar, exportar, papelera, restaurar e importar correctos')
""",encoding='utf-8')
with (out/'app-instalada.log').open('w',encoding='utf-8') as log:
 subprocess.run([str(python),'-I',str(check),str(installed/'app')],env=env,cwd=installed/'app',stdout=log,stderr=log,timeout=150,check=True,creationflags=flags)
print('Modelo, pagina e historial ejecutados con el runtime empaquetado',flush=True)
# Start the actual C# launcher, require matching local identity, test instance reuse and graceful stop.
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
launcher=subprocess.Popen([str(installed/'Anonimizar.exe'),'--no-browser','--port',str(port)],env=env,cwd=installed,creationflags=flags)
try:
 deadline=time.monotonic()+120;runtime=test/'Anonimizar/runtime.json';identity=None
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 while time.monotonic()<deadline:
  if launcher.poll() is not None:raise RuntimeError('El lanzador termino antes de arrancar')
  try:
   active=json.loads(runtime.read_text())
   with opener.open(f'http://127.0.0.1:{active["port"]}/anonimizar/identity',timeout=2) as response:identity=json.load(response)
   if identity.get('instance')==active['token']:break
  except (OSError,ValueError):pass
  time.sleep(0.5)
 assert identity and identity['version']=='0.3.0' and identity['instance']==active['token']
 with opener.open(f'http://127.0.0.1:{active["port"]}/',timeout=5) as response:assert response.status==200 and b'anon-initial-canvas' in response.read()
 second=subprocess.run([str(installed/'Anonimizar.exe'),'--no-browser'],env=env,cwd=installed,timeout=30,creationflags=flags)
 assert second.returncode==0 and json.loads(runtime.read_text())['pid']==active['pid']
 stop=subprocess.run([str(installed/'Anonimizar.exe'),'--stop'],env=env,cwd=installed,timeout=30,creationflags=flags)
 assert stop.returncode==0 and launcher.wait(timeout=30)==0 and not runtime.exists()
finally:
 if launcher.poll() is None:
  try:subprocess.run([str(installed/'Anonimizar.exe'),'--stop'],env=env,cwd=installed,timeout=20,creationflags=flags)
  except Exception:pass
  try:launcher.wait(timeout=25)
  except subprocess.TimeoutExpired:launcher.terminate();launcher.wait(timeout=10)
report['runtime']={'packaged_model_synthetic_check':'passed','real_page_apptest':'passed','synthetic_history_round_trip':'passed','csharp_launcher_and_http':'passed','second_launch_reuses_instance':True,'graceful_stop':'passed'}
print('Lanzador, reutilizacion de instancia y cierre correctos',flush=True)
# An altered embedded payload must be rejected by the same installer before it can install an application.
corrupt=out/'instalador-alterado.exe';shutil.copy2(installer,corrupt)
with payload.open('rb') as source:prefix=source.read(128)
with corrupt.open('r+b') as file:
 with mmap.mmap(file.fileno(),0) as data:
  offset=data.find(prefix);assert offset>=0
  data[offset+256:offset+257]=bytes([data[offset+256]^1]);data.flush()
reject=out/('rechazo-'+uuid.uuid4().hex[:8]);reject.mkdir();(reject/'.anonimizar-installer-test').write_text('Anonimizar isolated installer test 0.3.0')
setup(corrupt,reject,1)
assert not list(reject.rglob('installed.ok')) and not (reject/'Anonimizar').exists()
# Quiet testing without an explicit marked directory is rejected as well.
missing=subprocess.run([str(installer),'--quiet-test'],timeout=15,creationflags=flags)
assert missing.returncode==1
assert real_state()==state
assert sha(installer)==build['sha256']
report['negative_tests']={'altered_payload_rejected':True,'quiet_without_test_root_rejected':True}
report['test_directory']=str(out)
report['limits']=['Same Windows machine; no external install','No normal user registry/desktop integration exercised','No interactive uninstall executed','No browser visual review or full detector/privacy audit','Unsigned local installer; not published']
(out/'RESULTADO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
