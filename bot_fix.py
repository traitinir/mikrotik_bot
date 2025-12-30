import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Cargar configuración desde variables de entorno
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8523995546:AAGeWFFpTeh6dsK-DKlSolJclNQB9St_GxE')
ALLOWED_CHAT_IDS = os.getenv('ALLOWED_CHAT_IDS', '-1003633043572').split(',')

# Configuración MikroTik con PUERTO 8754
MIKROTIK_HOST = os.getenv('MIKROTIK_HOST', '152.231.27.30')
MIKROTIK_PORT = int(os.getenv('MIKROTIK_PORT', '8754'))  # ← TU PUERTO 8754
MIKROTIK_USER = os.getenv('MIKROTIK_USER', 'apii')
MIKROTIK_PASS = os.getenv('MIKROTIK_PASS', '')

print("=" * 50)
print("🤖 BOT MIKROTIK - RENDER.COM (PUERTO 8754)")
print("=" * 50)
print(f"✅ Token: {TOKEN[:10]}...")
print(f"✅ MikroTik: {MIKROTIK_HOST}:{MIKROTIK_PORT}")
print(f"✅ Usuario: {MIKROTIK_USER}")
print("=" * 50)

def check_access(chat_id):
    """Verifica acceso del usuario"""
    if not ALLOWED_CHAT_IDS or ALLOWED_CHAT_IDS == ['']:
        return True
    return str(chat_id) in ALLOWED_CHAT_IDS

def start(update: Update, context: CallbackContext):
    """Comando /start"""
    if not check_access(update.effective_chat.id):
        update.message.reply_text("❌ No tienes acceso.")
        return
    
    update.message.reply_text(
        "🤖 *Bot MikroTik en Render.com*\n\n"
        f"🔌 Puerto configurado: {MIKROTIK_PORT}\n"
        f"📡 IP: {MIKROTIK_HOST}\n\n"
        "📋 *Comandos disponibles:*\n"
        "/start - Este mensaje\n"
        "/ping - Probar bot\n"
        "/test - Probar conexión MikroTik\n"
        "/port - Ver puerto configurado",
        parse_mode='Markdown'
    )

def ping(update: Update, context: CallbackContext):
    """Comando /ping - Prueba básica"""
    update.message.reply_text("🏓 ¡Pong! Bot activo desde Render")

def port_info(update: Update, context: CallbackContext):
    """Comando /port - Ver configuración de puerto"""
    update.message.reply_text(
        f"🔌 *Configuración de Puerto*\n\n"
        f"IP: `{MIKROTIK_HOST}`\n"
        f"Puerto: `{MIKROTIK_PORT}`\n"
        f"Usuario: `{MIKROTIK_USER}`\n\n"
        f"_Esta es la configuración actual en Render_",
        parse_mode='Markdown'
    )

def test(update: Update, context: CallbackContext):
    """Comando /test - Probar conexión a MikroTik"""
    if not check_access(update.effective_chat.id):
        return
    
    update.message.reply_text(f"🔍 Probando conexión a {MIKROTIK_HOST}:{MIKROTIK_PORT}...")
    
    try:
        # Intentar conectar directamente con socket
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        result = sock.connect_ex((MIKROTIK_HOST, MIKROTIK_PORT))
        
        if result == 0:
            update.message.reply_text(f"✅ *Puerto {MIKROTIK_PORT} ABIERTO*\n\nEl puerto responde correctamente.", parse_mode='Markdown')
            sock.close()
            
            # Ahora probar con la API
            try:
                from mikrotik import MikroTik
                router = MikroTik()
                connected = router.connect(MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASS, MIKROTIK_PORT)
                
                if connected:
                    info = router.get_status()
                    if info:
                        update.message.reply_text(
                            f"🎉 *¡Conexión API exitosa!*\n\n"
                            f"Router: {info['model']}\n"
                            f"Versión: {info['version']}\n"
                            f"CPU: {info['cpu']}%\n"
                            f"Uptime: {info['uptime']}",
                            parse_mode='Markdown'
                        )
                    else:
                        update.message.reply_text("⚠️ Conectado pero no se pudieron obtener datos")
                else:
                    update.message.reply_text("❌ Error en autenticación API (usuario/contraseña)")
                    
            except ImportError:
                update.message.reply_text("ℹ️ Puerto abierto pero módulo API no disponible")
            except Exception as e:
                update.message.reply_text(f"⚠️ Error API: {str(e)[:100]}")
                
        else:
            update.message.reply_text(
                f"❌ *Puerto {MIKROTIK_PORT} CERRADO*\n\n"
                f"Error código: {result}\n\n"
                f"Verifica en tu MikroTik:\n"
                f"1. API habilitada en puerto {MIKROTIK_PORT}\n"
                f"2. Firewall permite puerto {MIKROTIK_PORT}\n"
                f"3. IP {MIKROTIK_HOST} es accesible desde Internet",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        update.message.reply_text(f"🔥 Error de prueba: {str(e)[:150]}")

def main():
    """Función principal"""
    try:
        # Crear updater (versión 13.15)
        updater = Updater(token=TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Agregar comandos
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("ping", ping))
        dispatcher.add_handler(CommandHandler("test", test))
        dispatcher.add_handler(CommandHandler("port", port_info))
        
        print("🤖 Bot iniciado correctamente")
        print("📱 Escribe /start en Telegram para probar")
        
        # Iniciar polling
        updater.start_polling()
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error iniciando bot: {e}")
        print(f"🔧 Tipo: {type(e).__name__}")

if __name__ == '__main__':
    main()
