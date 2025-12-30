from routeros_api import RouterOsApiPool
import time

class MikroTik:
    def __init__(self):
        self.api = None
        self.connection = None
    
    def connect(self, host, user, password, port=8754):  # ← 8754 por defecto
        """Conecta al MikroTik"""
        print(f"🔗 Conectando a {host}:{port}...")
        
        try:
            self.connection = RouterOsApiPool(
                host=host,
                username=user,
                password=password,
                port=port,  # ← Usa el puerto que se pase
                plaintext_login=True,
                use_ssl=False,
                timeout=15
            )
            
            self.api = self.connection.get_api()
            
            # Probar conexión rápida
            test = self.api.get_resource('/system/resource').get()
            if test:
                print(f"✅ Conectado a: {test[0].get('board-name', 'MikroTik')}")
                return True
            
        except Exception as e:
            print(f"❌ Error conexión: {e}")
            return False
    
    def get_status(self):
        """Obtiene estado básico"""
        if not self.api:
            return None
        
        try:
            resource = self.api.get_resource('/system/resource')
            data = resource.get()[0]
            
            return {
                'cpu': data.get('cpu-load', '0'),
                'uptime': data.get('uptime', '0s'),
                'model': data.get('board-name', 'Desconocido'),
                'version': data.get('version', 'Desconocido')
            }
        except:
            return None
