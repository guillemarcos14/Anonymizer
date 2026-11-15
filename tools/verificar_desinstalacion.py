"""Exercise uninstall/reinstall only in the synthetic scope created by the installer test."""
from pathlib import Path
import base64,hashlib,json,os,runpy,socket,sqlite3,subprocess,sys,time,uuid,winreg
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verificacion-local/desinstalador'/('ejecucion-'+uuid.uuid4().hex[:8]);OUT.mkdir(parents=True)
# This first checks the exact current installer, model, history, launcher and all packaged bytes.
context=runpy.run_path(str(ROOT/'tools/verificar_instalador.py'),run_name='__main__')
profile=context['test'];installed=context['installed'];env=context['env'];installer=context['installer'];flags=context['flags'];real_state=context['real_state'];real_before=real_state()
data=profile/'Anonimizar';registration=json.loads((profile/'registration-test.json').read_text())
product_key=registration['RegistryPath'];test_id=(profile/'.test-id').read_text().strip()
assert product_key==chr(92).join(['Software','Anonimizar','InstallerTests',test_id,'Uninstall','Anonimizar'])
print('Inicio del ciclo aislado de desinstalacion',flush=True)

def run(command,timeout=180,check=True):
    done=subprocess.run([str(x) for x in command],env=env,cwd=OUT,capture_output=True,text=True,timeout=timeout,creationflags=flags)
    if check and done.returncode!=0:raise RuntimeError('Fallo de comando: '+done.stderr[-2000:])
    return done

def ps(script):
    encoded=base64.b64encode(script.encode('utf-16le')).decode()
    return run(['powershell.exe','-NoProfile','-NonInteractive','-WindowStyle','Hidden','-EncodedCommand',encoded]).stdout

def quoted(value):return "'"+str(value).replace("'","''")+"'"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def key_values(key):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key) as handle:
            values={};i=0
            while True:
                try:name,value,kind=winreg.EnumValue(handle,i);values[name]=(value,kind);i+=1
                except OSError:break
            return values
    except FileNotFoundError:return None

def snapshot():
    return {p.relative_to(data).as_posix():sha(p) for p in data.rglob('*') if p.is_file() and (p.name in ('documents.sqlite3','settings.json') or 'exports' in p.relative_to(data).parts or 'recovery' in p.relative_to(data).parts)}

seed=OUT/'sembrar.py';seed.write_text("""import sys,json
from pathlib import Path
app=Path(sys.argv[1]);sys.path.insert(0,str(app))
from anonimizar_documents import save,move_to_trash,export_history,LOCAL_OWNER
from anonimizar_local import update_settings
update_settings(history_enabled=True,preferences={'doc_operator':'replace','doc_threshold':0.35})
a=save(LOCAL_OWNER,{'text':'FICTICIO CONSERVAR HISTORIAL','settings':{},'review':{}})
b=save(LOCAL_OWNER,{'text':'FICTICIO CONSERVAR PAPELERA','settings':{},'review':{}});move_to_trash(b)
export=Path(sys.argv[2])/'exports/ficticio.json';export.parent.mkdir(exist_ok=True);export.write_text(export_history(),encoding='utf-8')
print(json.dumps({'historial':a,'papelera':b}))
""",encoding='utf-8')
run([installed/'runtime/python.exe','-I',seed,installed/'app',data])
protected=snapshot();assert 'documents.sqlite3' in protected and 'settings.json' in protected and 'exports/ficticio.json' in {k.replace('\\','/') for k in protected}
# The witness inside the program root deliberately has no ownership marker and must survive.
witness_files=[profile/'Programs/OtherApp/keep.txt',profile/'Programs/Anonimizar-extra/keep.txt',profile/'Programs/Anonimizar/keep-user/keep.txt',profile/'StartMenu/Anonimizar/keep-user.txt',profile/'Desktop/OtherProduct.lnk',OUT/'outside-profile/keep.txt']
for p in witness_files:p.parent.mkdir(parents=True,exist_ok=True);p.write_text('TESTIGO FICTICIO '+uuid.uuid4().hex,encoding='utf-8')
witness_hashes={str(p):sha(p) for p in witness_files}
witness_key=product_key.rsplit(chr(92),1)[0]+chr(92)+'Witness'
with winreg.CreateKey(winreg.HKEY_CURRENT_USER,witness_key) as key:winreg.SetValueEx(key,'keep',0,winreg.REG_SZ,'FICTICIO-'+uuid.uuid4().hex)
with winreg.CreateKey(winreg.HKEY_CURRENT_USER,witness_key+(chr(92)+'Child')) as key:winreg.SetValueEx(key,'keep',0,winreg.REG_DWORD,314)
witness_values={witness_key:key_values(witness_key),witness_key+(chr(92)+'Child'):key_values(witness_key+(chr(92)+'Child'))}

def preserved():
    assert snapshot()==protected,'Se alteraron datos ficticios protegidos'
    assert all(Path(p).is_file() and sha(Path(p))==h for p,h in witness_hashes.items()),'Se altero un archivo testigo'
    assert all(key_values(key)==expected for key,expected in witness_values.items()),'Se altero una clave testigo'
    assert real_state()==real_before,'Cambio el registro o los punteros habituales'

# Read actual shortcut properties and product registration, using COM rather than a simulated file.
def shortcuts_match(version):
    result=json.loads(ps('$shell=New-Object -ComObject WScript.Shell; @('+','.join(quoted(p) for p in [profile/'Desktop/Anonimizar.lnk',profile/'StartMenu/Anonimizar/Anonimizar.lnk'])+') | ForEach-Object { $link=$shell.CreateShortcut($_); [PSCustomObject]@{target=$link.TargetPath;working=$link.WorkingDirectory;icon=$link.IconLocation} } | ConvertTo-Json -Compress'))
    for row in result:
        assert Path(row['target']).resolve()==(version/'Anonimizar.exe').resolve()
        assert Path(row['working']).resolve()==version.resolve()
        assert str(version/'app/assets/anonimizar-app.ico').lower() in row['icon'].lower()
    values=key_values(product_key);assert values['DisplayVersion'][0]=='0.3.0' and Path(values['InstallLocation'][0]).resolve()==version.resolve()
    assert values['NoModify'][0]==1 and values['NoRepair'][0]==1
shortcuts_match(installed)

request_root=data/'uninstall-work'
def invoke_uninstall(decision='--confirm-test',expected=0,final_status=None):
    prior=set(request_root.glob('*/result.json')) if request_root.exists() else set()
    done=run([installed/'Desinstalar.exe','--quiet-test','--test-root',profile,decision],check=False)
    (OUT/('uninstall-'+uuid.uuid4().hex[:6]+'.log')).write_text(done.stdout+'\n'+done.stderr,encoding='utf-8')
    assert done.returncode==expected,(done.returncode,done.stdout,done.stderr)
    created=set(request_root.glob('*/result.json'))-prior if request_root.exists() else set()
    if final_status is None:
        assert not created,'Se inicio un borrado en un caso cancelado o rechazado'
        return None
    assert len(created)==1,created
    result_file=created.pop();deadline=time.monotonic()+240
    while time.monotonic()<deadline:
        try:
            result=json.loads(result_file.read_text(encoding='utf-8'))
            if result['status']!='pending':break
        except (OSError,ValueError):pass
        time.sleep(0.25)
    else:raise TimeoutError('El auxiliar no produjo un resultado final')
    assert result['status']==final_status,result
    return {'file':str(result_file),'result':result}

program_marker=sha(installed/'installed.ok');registry_before=key_values(product_key)
invoke_uninstall('--cancel-test');preserved();assert sha(installed/'installed.ok')==program_marker and key_values(product_key)==registry_before
print('Cancelacion: programa, datos y claves intactos',flush=True)
# The real packaged launcher is kept active; uninstall must reject it without stopping it.
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
launcher=subprocess.Popen([str(installed/'Anonimizar.exe'),'--no-browser','--port',str(port)],env=env,cwd=installed,creationflags=flags)
try:
    deadline=time.monotonic()+120;runtime=data/'runtime.json'
    while time.monotonic()<deadline:
        try:
            state=json.loads(runtime.read_text())
            if context['identity'] and context['opener']:
                with context['opener'].open(f'http://127.0.0.1:{state["port"]}/anonimizar/identity',timeout=2) as response:active=json.load(response)
                if active.get('instance')==state['token']:break
        except (OSError,ValueError):pass
        time.sleep(0.5)
    else:raise TimeoutError('No arranco el motor para la prueba de bloqueo')
    invoke_uninstall(expected=1);preserved();assert launcher.poll() is None and key_values(product_key)==registry_before
finally:
    run([installed/'Anonimizar.exe','--stop']);launcher.wait(timeout=40)
print('Motor activo: desinstalacion rechazada sin detenerlo ni borrar',flush=True)
# A directory junction inside the owned version must not be followed or deleted.
junction=installed/'guard-link';target=OUT/'outside-profile'
ps('New-Item -ItemType Junction -Path '+quoted(junction)+' -Target '+quoted(target)+' | Out-Null')
assert junction.is_junction() and junction.resolve()==target.resolve()
invoke_uninstall(expected=1);preserved();assert installed.is_dir()
assert junction.is_junction() and junction.parent.resolve()==installed.resolve();os.rmdir(junction)
assert not junction.exists();preserved()
print('Union de directorios rechazada; destino externo conservado',flush=True)
# A registration belonging elsewhere causes a reported failure, not false success.
with winreg.OpenKey(winreg.HKEY_CURRENT_USER,product_key,0,winreg.KEY_SET_VALUE) as key:winreg.SetValueEx(key,'InstallLocation',0,winreg.REG_SZ,str(OUT/'outside-profile'))
failed=invoke_uninstall(final_status='failed');assert failed['result']['deleted']==[];preserved();assert installed.is_dir()
with winreg.OpenKey(winreg.HKEY_CURRENT_USER,product_key,0,winreg.KEY_SET_VALUE) as key:winreg.SetValueEx(key,'InstallLocation',0,winreg.REG_SZ,str(installed))
print('Registro incoherente: fallo final informado, sin borrado',flush=True)
completed=invoke_uninstall(final_status='completed');preserved()
assert not installed.exists() and not (profile/'Programs/Anonimizar/current.txt').exists()
assert not (profile/'Desktop/Anonimizar.lnk').exists() and not (profile/'StartMenu/Anonimizar/Anonimizar.lnk').exists()
assert key_values(product_key) is None
assert (profile/'Programs/Anonimizar/keep-user/keep.txt').exists()
print('Desinstalacion completada; datos y testigos conservados',flush=True)
# Reinstall the exact same artifact; existing data must be untouched byte for byte.
run([installer,'--quiet-test','--test-root',profile],timeout=600)
reinstalled=Path((profile/'Programs/Anonimizar/current.txt').read_text().strip());assert reinstalled.is_relative_to(profile)
preserved();shortcuts_match(reinstalled)
run([reinstalled/'runtime/python.exe','-I',reinstalled/'app/tools/verificar_instalacion.py'])
with sqlite3.connect((data/'documents.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    assert db.execute('SELECT COUNT(*) FROM documents WHERE payload LIKE ?',('%FICTICIO CONSERVAR HISTORIAL%',)).fetchone()[0]==1
    assert db.execute('SELECT COUNT(*) FROM trash WHERE payload LIKE ?',('%FICTICIO CONSERVAR PAPELERA%',)).fetchone()[0]==1
preserved()
report={'installer_sha256':context['build']['sha256'],'profile':str(profile),'cancel_preserves_everything':True,'active_engine_blocks_uninstall':True,'junction_rejected_without_following_target':True,'foreign_registration_fails_with_no_deletion':failed,'uninstall_final_result':completed,'owned_program_and_shortcuts_removed':True,'owned_registry_key_removed':True,'reinstall_completed':True,'reinstalled_model_synthetic_check':True,'history_trash_settings_and_exports_byte_identical':protected,'witness_files_preserved':len(witness_files),'witness_registry_keys_preserved':len(witness_values),'normal_registration_and_pointers_unchanged':True,'application_runtime_code_unchanged':True,'limits':['Same Windows computer','Test registry namespace, not normal Windows Installed apps registration','Confirmation simulated by explicit test flags; no native dialog interaction','No full detector, browser visual or network audit','Original unchanged; not published']}
(OUT/'RESULTADO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Reinstalacion completada; historial, papelera, ajustes, exportaciones y testigos intactos',flush=True)
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
