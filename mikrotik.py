#!/usr/bin/env python3
"""
Módulo MikroTik simplificado para Render.com
Versión compatible con Python 3.13
"""

from routeros_api import RouterOsApiPool
import time
import logging

logger = logging.getLogger(__name__)

class MikroTik:
    """Clase simplificada para conexión a MikroTik"""
    
    def __init__(self):
        self.api = None
        self.connection = None
        self.is_connected = False
    
    def connect(self, host, user, password, port=8754):
        """
        Conecta al MikroTik RouterOS
        
        Args:
            host (str): IP o hostname del MikroTik
            user (str): Usuario para API
            password (str): Contraseña
            port (int): Puerto API (8754 en tu caso)
            
        Returns:
            bool: True si conectó correctamente
        """
        print(f"🔗 Conectando a {host}:{port}...")
        
        try:
            # Crear pool de conexión
            self.connection = RouterOsApiPool(
                host=host,
                username=user,
                password=password,
                port=port,
                plaintext_login=True,
                use_ssl=False,
                timeout=15,
                max_connections=1
            )
            
            # Obtener API
            self.api = self.connection.get_api()
            
            # Probar conexión con comando simple
            test_result = self.api.get_resource('/system/resource').get()
            
            if test_result and len(test_result) > 0:
                router_name = test_result[0].get('board-name', 'MikroTik Router')
                print(f"✅ ¡Conectado! Router: {router_name}")
                self.is_connected = True
                return True
            else:
                print("⚠️ Conectado pero sin respuesta de datos")
                return False
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error de conexión: {error_msg}")
            
            # Diagnóstico amigable
            if "Connection refused" in error_msg:
                print("   🔥 Posibles causas:")
                print(f"   1. Puerto {port} no está abierto en el firewall")
                print(f"   2. API no habilitada en el MikroTik")
                print(f"   3. IP {host} no es accesible desde Internet")
            elif "timeout" in error_msg.lower():
                print("   ⏰ El router no responde (timeout)")
            elif "authentication" in error_msg.lower():
                print("   🔐 Error de usuario/contraseña")
            elif "cannot connect" in error_msg.lower():
                print("   🌐 No hay ruta a la red del router")
            
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.connection:
            try:
                self.connection.disconnect()
                print("🔌 Desconectado del MikroTik")
            except:
                pass
            finally:
                self.api = None
                self.connection = None
                self.is_connected = False
    
    def get_status(self):
        """
        Obtiene información básica del sistema
        
        Returns:
            dict: Información del router o None si hay error
        """
        if not self.is_connected or not self.api:
            print("⚠️ No hay conexión activa")
            return None
        
        try:
            # Obtener recursos del sistema
            resource = self.api.get_resource('/system/resource')
            data = resource.get()[0]
            
            # Calcular porcentaje de memoria usado
            free_mem = int(data.get('free-memory', 0))
            total_mem = int(data.get('total-memory', 0))
            
            if total_mem > 0:
                used_percent = ((total_mem - free_mem) / total_mem) * 100
                memory_info = f"{used_percent:.1f}% usado"
            else:
                memory_info = "N/A"
            
            # Formatear respuesta
            status_info = {
                'cpu': data.get('cpu-load', '0'),
                'uptime': data.get('uptime', '0s'),
                'model': data.get('board-name', 'Desconocido'),
                'version': data.get('version', 'Desconocido'),
                'memory': memory_info,
                'free_memory_mb': f"{free_mem / (1024*1024):.1f} MB",
                'total_memory_mb': f"{total_mem / (1024*1024):.1f} MB",
                'architecture': data.get('architecture-name', 'N/A'),
                'platform': data.get('platform', 'N/A')
            }
            
            print(f"📊 Status obtenido: {status_info['model']} - CPU: {status_info['cpu']}%")
            return status_info
            
        except Exception as e:
            print(f"❌ Error obteniendo status: {e}")
            return None
    
    def get_wifi_clients(self):
        """
        Obtiene lista de clientes WiFi conectados
        
        Returns:
            list: Lista de clientes o lista vacía si no hay
        """
        if not self.is_connected or not self.api:
            return []
        
        try:
            clients = self.api.get_resource('/interface/wireless/registration-table').get()
            
            if clients:
                print(f"📶 Encontrados {len(clients)} clientes WiFi")
            
            # Formatear respuesta simple
            client_list = []
            for client in clients[:10]:  # Máximo 10 para no saturar
                client_list.append({
                    'mac': client.get('mac-address', 'Desconocido'),
                    'signal': client.get('signal-strength', '0dBm'),
                    'interface': client.get('interface', 'N/A'),
                    'ssid': client.get('ssid', 'N/A')
                })
            
            return client_list
            
        except Exception as e:
            print(f"⚠️ Error clientes WiFi: {e}")
            return []
    
    def quick_test(self):
        """Prueba rápida de todas las funciones"""
        print("=" * 50)
        print("🧪 PRUEBA RÁPIDA MIKROTIK")
        print("=" * 50)
        
        # Obtener status
        status = self.get_status()
        if status:
            print(f"✅ Status OK: {status['model']}")
        else:
            print("❌ No se pudo obtener status")
        
        # Obtener clientes WiFi
        clients = self.get_wifi_clients()
        print(f"📱 Clientes WiFi: {len(clients)}")
        
        print("=" * 50)
        return status is not None

# Función de prueba independiente
def test_mikrotik_connection():
    """Función para probar desde consola"""
    import os
    
    print("🧪 TEST DE CONEXIÓN MIKROTIK")
    print("=" * 50)
    
    # Cargar configuración desde variables de entorno
    host = os.getenv('MIKROTIK_HOST', '152.231.27.30')
    port = int(os.getenv('MIKROTIK_PORT', '8754'))
    user = os.getenv('MIKROTIK_USER', 'apii')
    password = os.getenv('MIKROTIK_PASS', '')
    
    print(f"🔧 Configuración:")
    print(f"   Host: {host}")
    print(f"   Puerto: {port}")
    print(f"   Usuario: {user}")
    print("=" * 50)
    
    # Crear instancia y conectar
    router = MikroTik()
    
    if router.connect(host, user, password, port):
        print("✅ ¡CONEXIÓN EXITOSA!")
        
        # Obtener información
        info = router.get_status()
        if info:
            print(f"\n📊 INFORMACIÓN DEL ROUTER:")
            print(f"   Modelo: {info['model']}")
            print(f"   Versión: {info['version']}")
            print(f"   CPU: {info['cpu']}%")
            print(f"   Uptime: {info['uptime']}")
            print(f"   Memoria: {info['memory']}")
        
        # Desconectar
        router.disconnect()
        return True
    else:
        print("❌ CONEXIÓN FALLIDA")
        print("\n🔧 Verifica:")
        print(f"   1. Puerto {port} abierto en firewall")
        print(f"   2. API habilitada en MikroTik")
        print(f"   3. IP {host} accesible desde Internet")
        return False

# Si se ejecuta este archivo directamente, hace la prueba
if __name__ == "__main__":
    success = test_mikrotik_connection()
    exit(0 if success else 1)
