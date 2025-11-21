import servicemanager
import socket
import sys
import os
import win32serviceutil
import win32service
import win32event
import threading
from waitress import serve
from fdbacc import app  # Importa a instância da aplicação Flask

class FlaskService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FdbaccFlaskService"
    _svc_display_name_ = "Fdbacc Flask Service"
    _svc_description_ = "Serviço para executar a aplicação Flask Fdbacc com Waitress."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        servicemanager.LogInfoMsg(f"{self._svc_name_} is stopping.")

    def SvcDoRun(self):
        servicemanager.LogInfoMsg(f"Starting {self._svc_name_}.")
        self.is_running = True
        
        try:
            # 1. Log CWD
            cwd = os.getcwd()
            servicemanager.LogInfoMsg(f"Service CWD: {cwd}")

            # 2. Ativar o ambiente virtual
            project_root = os.path.dirname(os.path.abspath(__file__))
            servicemanager.LogInfoMsg(f"Project root: {project_root}")
            venv_path = os.path.join(project_root, '.venv')
            site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
            servicemanager.LogInfoMsg(f"Expected site-packages: {site_packages}")

            if os.path.exists(site_packages):
                sys.path.insert(0, site_packages)
                servicemanager.LogInfoMsg(f"Successfully added site-packages to sys.path.")
            else:
                servicemanager.LogErrorMsg(f"site-packages directory not found at: {site_packages}")
                self.SvcStop()
                return

            servicemanager.LogInfoMsg(f"sys.path: {sys.path}")

            # 3. Iniciar o servidor
            servicemanager.LogInfoMsg("Preparing to start Waitress server with HTTPS...")
            cert_path = os.path.join(project_root, 'cert.pem')
            key_path = os.path.join(project_root, 'key.pem')

            servicemanager.LogInfoMsg(f"Cert path: {cert_path} (Exists: {os.path.exists(cert_path)})")
            servicemanager.LogInfoMsg(f"Key path: {key_path} (Exists: {os.path.exists(key_path)})")

            if not os.path.exists(cert_path) or not os.path.exists(key_path):
                servicemanager.LogErrorMsg("SSL certificate or key not found. Aborting.")
                self.SvcStop()
                return

            server_args = {
                'host': '0.0.0.0', 
                'port': 5173, 
                'ssl_certificate': cert_path, 
                'ssl_private_key': key_path
            }
            servicemanager.LogInfoMsg(f"Starting server with args: {server_args}")

            server_thread = threading.Thread(
                target=serve, 
                args=(app,),
                kwargs=server_args
            )
            server_thread.start()
            servicemanager.LogInfoMsg("Waitress server started in a background thread.")

            while self.is_running:
                win32event.WaitForSingleObject(self.hWaitStop, 5000) # Check every 5 seconds

        except Exception as e:
            servicemanager.LogErrorMsg(f"CRITICAL SERVICE ERROR: {e}")
            self.SvcStop()
        finally:
            servicemanager.LogInfoMsg(f"{self._svc_name_} has stopped.")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FlaskService)