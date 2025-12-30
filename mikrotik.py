from routeros_api import RouterOsApiPool
import time
import logging

logger = logging.getLogger(__name__)

class MikroTik:
    def __init__(self):
        self.api = None
        self.connection = None
    
    def connect(self, host, user, password, port=8754):
        """Conecta al MikroTik - Versión para Render"""
        print(f"🔗 Conectando a {host}:{port}...")
        
        try:
            self.connection = RouterOsApiPool(
                host=host,
                username=user,
                password=password,
                port=port,
                plaintext_login=True,
                use_ssl=False,
                timeout=20,
                max_connections=1
            )
            
            self.api = self.connection.get_api()
            
            # Probar conexión
            test = self.api.get_resource('/system/resource').get()
            if test:
                print(f"✅ Conectado a {test[0].get('board-name', 'MikroTik')}")
                return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg}")
            
            # Diagnóstico específico
            if "Connection refused" in error_msg:
                print("   🔥 Puerto bloqueado o API no habilitada")
            elif "timeout" in error_msg.lower():
                print("   ⏰ Timeout - El router no responde")
            elif "authentication" in error_msg.lower():
                print("   🔐 Error de usuario/contraseña")
            
            return False
    
    def get_status(self):
        """Obtiene estado del sistema"""
        if not self.api:
            return None
        
        try:
            resource = self.api.get_resource('/system/resource')
            data = resource.get()[0]
            
            return {
                'cpu': data.get('cpu-load', '0'),
                'uptime': data.get('uptime', '0s'),
                'model': data.get('board-name', 'Desconocido'),
                'version': data.get('version', 'Desconocido'),
                'memory_percent': 'N/A'
            }
        except:
            return None
    
    def get_wifi_clients(self):
        """Obtiene clientes WiFi"""
        if not self.api:
            return []
        
        try:
            clients = self.api.get_resource('/interface/wireless/registration-table').get()
            return clients
        except:
            return []