import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

# Importar configuración DESPUÉS de logging
try:
    # Cargar variables de entorno manualmente primero
    from dotenv import load_dotenv
    load_dotenv()
    
    # Ahora importar Config
    from config import Config
    from mikrotik import MikroTik
except ImportError as e:
    logging.error(f"❌ Error importando módulos: {e}")
    # Configuración manual si falla
    class ConfigManual:
        TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        ALLOWED_CHAT_IDS = [id.strip() for id in os.getenv('ALLOWED_CHAT_IDS', '').split(',') if id.strip()]
        MIKROTIK_HOST = os.getenv('MIKROTIK_HOST', '152.231.27.30')
        MIKROTIK_PORT = int(os.getenv('MIKROTIK_PORT', '8754'))
        MIKROTIK_USER = os.getenv('MIKROTIK_USER', '')
        MIKROTIK_PASS = os.getenv('MIKROTIK_PASS', '')
    
    Config = ConfigManual
    from mikrotik import MikroTik

# Inicializar MikroTik
router = MikroTik()

def check_access(user_id):
    """Verifica si el usuario/chat tiene acceso"""
    if not Config.ALLOWED_CHAT_IDS:
        return True
    return str(user_id) in Config.ALLOWED_CHAT_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    if not update.message:
        return
    
    user_id = str(update.effective_chat.id)
    
    if not check_access(user_id):
        await update.message.reply_text("❌ No tienes acceso a este bot.")
        return
    
    await update.message.reply_text(
        "🤖 *Bot MikroTik en Render.com*\n\n"
        "✅ Conectado desde la nube\n\n"
        "📋 *Comandos disponibles:*\n"
        "/status - Estado del router\n"
        "/test - Probar conexión MikroTik\n"
        "/clients - Clientes WiFi\n"
        "/help - Ayuda",
        parse_mode='Markdown'
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /test - Prueba conexión"""
    if not update.message:
        return
    
    user_id = str(update.effective_chat.id)
    if not check_access(user_id):
        return
    
    await update.message.reply_chat_action(action='typing')
    
    # Probar conexión al MikroTik
    if not router.api:
        connected = router.connect(
            Config.MIKROTIK_HOST,
            Config.MIKROTIK_USER,
            Config.MIKROTIK_PASS,
            Config.MIKROTIK_PORT
        )
        if not connected:
            await update.message.reply_text(
                "❌ *No pude conectar al MikroTik*\n\n"
                f"Detalles:\n"
                f"• IP: {Config.MIKROTIK_HOST}\n"
                f"• Puerto: {Config.MIKROTIK_PORT}\n"
                f"• Usuario: {Config.MIKROTIK_USER}",
                parse_mode='Markdown'
            )
            return
    
    info = router.get_status()
    if info:
        await update.message.reply_text(
            f"✅ *¡Todo funciona!*\n\n"
            f"🤖 Bot: Conectado desde Render.com\n"
            f"📡 MikroTik: {info['model']}\n"
            f"🔧 Versión: {info['version']}\n"
            f"📈 CPU: {info['cpu']}%\n"
            f"⏱️ Uptime: {info['uptime']}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⚠️ Conectado pero sin datos")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    if not update.message:
        return
    
    user_id = str(update.effective_chat.id)
    if not check_access(user_id):
        return
    
    await update.message.reply_chat_action(action='typing')
    
    if not router.api:
        connected = router.connect(
            Config.MIKROTIK_HOST,
            Config.MIKROTIK_USER,
            Config.MIKROTIK_PASS,
            Config.MIKROTIK_PORT
        )
        if not connected:
            await update.message.reply_text("❌ No pude conectar al router")
            return
    
    info = router.get_status()
    if not info:
        await update.message.reply_text("❌ Error al obtener información")
        return
    
    message = (
        f"📊 *Estado del Router*\n\n"
        f"🖥️ Modelo: {info['model']}\n"
        f"🔧 Versión: {info['version']}\n"
        f"⏱️ Uptime: {info['uptime']}\n"
        f"📈 CPU: {info['cpu']}%\n"
        f"💾 Memoria: {info.get('memory_percent', 'N/A')}\n\n"
        f"_Consulta desde Render.com_"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /clients"""
    if not update.message:
        return
    
    user_id = str(update.effective_chat.id)
    if not check_access(user_id):
        return
    
    await update.message.reply_chat_action(action='typing')
    
    if not router.api:
        connected = router.connect(
            Config.MIKROTIK_HOST,
            Config.MIKROTIK_USER,
            Config.MIKROTIK_PASS,
            Config.MIKROTIK_PORT
        )
        if not connected:
            await update.message.reply_text("❌ No pude conectar al router")
            return
    
    clients_list = router.get_wifi_clients()
    
    if not clients_list:
        await update.message.reply_text("📶 *No hay clientes WiFi conectados*", parse_mode='Markdown')
        return
    
    message = "📱 *Clientes WiFi Conectados*\n\n"
    
    for i, client in enumerate(clients_list[:10], 1):
        mac = client.get('mac', client.get('mac-address', 'Desconocido'))
        signal = client.get('signal', '0dBm')
        message += f"{i}. `{mac}`\n"
        message += f"   📶 Señal: {signal}\n\n"
    
    if len(clients_list) > 10:
        message += f"_Y {len(clients_list) - 10} clientes más..._"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    if not update.message:
        return
    
    user_id = str(update.effective_chat.id)
    if not check_access(user_id):
        return
    
    help_text = (
        "📖 *Comandos Disponibles*\n\n"
        "/start - Iniciar el bot\n"
        "/test - Probar conexión MikroTik\n"
        "/status - Estado del router\n"
        "/clients - Clientes WiFi\n"
        "/help - Esta ayuda\n\n"
        "🌐 *Hosteado en:* Render.com"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Función principal para Render"""
    print("=" * 50)
    print("🤖 BOT MIKROTIK - RENDER.COM")
    print("=" * 50)
    
    # Validar configuración básica
    if not Config.TELEGRAM_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN no configurado")
        print("   Agrega la variable de entorno en Render.com")
        return
    
    print(f"✅ Token: {Config.TELEGRAM_TOKEN[:10]}...")
    print(f"✅ MikroTik: {Config.MIKROTIK_HOST}:{Config.MIKROTIK_PORT}")
    print(f"✅ Usuario: {Config.MIKROTIK_USER}")
    
    try:
        # Crear aplicación
        app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Agregar comandos
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("test", test))
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("clients", clients))
        app.add_handler(CommandHandler("help", help_command))
        
        print("✅ Bot configurado")
        print("⏳ Iniciando...")
        print("=" * 50)
        print("📱 Ve a Telegram y escribe /start a tu bot")
        print("=" * 50)
        
        # Configuración para Render
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {e}")
        print("\n🔧 Soluciones comunes:")
        print("   1. Verifica el token de Telegram")
        print("   2. Asegúrate que las variables de entorno estén bien")
        print("   3. El puerto 8757 debe estar abierto en tu MikroTik")

if __name__ == '__main__':
    main()