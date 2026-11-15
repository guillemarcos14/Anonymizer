"""Hidden Windows launcher. Owns only the server it starts; stdlib only."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from anonimizar_local import VERSION, data_dir
from product_upgrade import migrate_data

ROOT = Path(__file__).resolve().parent


def identity(port):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f'http://127.0.0.1:{int(port)}/anonimizar/identity', timeout=1) as response:
            return json.load(response)
    except (OSError, ValueError):
        return {}


def notify(message):
    if sys.platform == 'win32':
        ctypes.windll.user32.MessageBoxW(None, message, 'Anonimizar', 0x10)
    else:
        print(message, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8502)
    parser.add_argument('--stop', action='store_true')
    args = parser.parse_args()
    if not os.environ.get('ANONIMIZAR_DATA_DIR'):
        migrate_data()
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    runtime = root / 'runtime.json'
    try:
        state = json.loads(runtime.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        state = {}
    if args.stop:
        if state and identity(state['port']).get('instance') == state.get('token'):
            (root / 'stop.json').write_text(json.dumps({'token': state['token']}), encoding='utf-8')
        return 0
    lock = open(root / 'launcher.lock', 'a+b')
    try:
        if sys.platform == 'win32':
            import msvcrt
            # Lock beyond EOF is supported. Do not read the byte first: another
            # instance already owns it, and Windows rejects that read.
            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                for _ in range(60):
                    try:
                        state = json.loads(runtime.read_text(encoding='utf-8'))
                    except (OSError, ValueError):
                        state = {}
                    if state and identity(state['port']).get('instance') == state.get('token'):
                        if not args.no_browser:
                            webbrowser.open(f"http://127.0.0.1:{state['port']}/")
                        return 0
                    time.sleep(1)
                raise RuntimeError('Otra apertura no ha terminado de arrancar. Espera un momento y vuelve a abrir Anonimizar.')
        for port in range(args.port, args.port + 20):
            with socket.socket() as probe:
                try:
                    probe.bind(('127.0.0.1', port))
                    break
                except OSError:
                    continue
        else:
            raise RuntimeError('No hay un puerto local disponible. Cierra otras instancias de Anonimizar y vuelve a intentarlo.')
        token = secrets.token_hex(24)
        env = dict(os.environ, ANONIMIZAR_INSTANCE=token, PYTHONNOUSERSITE='1', PYTHONUTF8='1',
                   HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
        python = Path(sys.executable).with_name('python.exe')
        log_dir = root / 'logs'
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / time.strftime('startup-%Y%m%d-%H%M%S.log')
        command = [str(python), '-m', 'streamlit', 'run', str(ROOT / 'anonimizar_server.py'),
                   '--server.address', '127.0.0.1', '--server.port', str(port),
                   '--browser.gatherUsageStats', 'false', '--server.headless', 'true']
        with log_path.open('w', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            state = {'port': port, 'token': token, 'version': VERSION, 'pid': process.pid}
            runtime.write_text(json.dumps(state), encoding='utf-8')
            try:
                for _ in range(90):
                    if process.poll() is not None:
                        raise RuntimeError('El motor no pudo arrancar. Registro de diagnóstico: ' + str(log_path))
                    if identity(port).get('instance') == token:
                        break
                    time.sleep(1)
                else:
                    raise RuntimeError('El arranque ha superado 90 segundos. Registro: ' + str(log_path))
                if not args.no_browser:
                    webbrowser.open(f'http://127.0.0.1:{port}/')
                while process.poll() is None:
                    try:
                        request = json.loads((root / 'stop.json').read_text(encoding='utf-8'))
                    except (OSError, ValueError):
                        request = {}
                    if request.get('token') == token:
                        process.terminate()
                        break
                    time.sleep(1)
                process.wait(timeout=15)
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=15)
                try:
                    if json.loads(runtime.read_text(encoding='utf-8')).get('token') == token:
                        runtime.unlink(missing_ok=True)
                except (OSError, ValueError):
                    pass
    except Exception as error:
        notify(str(error))
        return 1
    finally:
        lock.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
