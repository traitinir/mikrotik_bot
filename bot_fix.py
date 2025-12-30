import os
import sys
import logging

# Agregar imghdr dummy al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

# Ahora importar telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Cargar configuración
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8523995546:AAGeWFFpTeh6dsK-DKlSolJclNQB9St_GxE')
ALLOWED_CHAT_IDS = os.getenv('ALLOWED_CHAT_IDS', '-1003633043572').split(',')

# MikroTik - PUERTO 8754
MIKROTIK_HOST = os.getenv('MIKROTIK_HOST', '152.231.27.30')
MIKROTIK_PORT = int(os.getenv('MIKROTIK_PORT', '8754'))
MIKROTIK_USER = os.getenv('MIKROTIK_USER', 'apii')
MIKROTIK_PASS = os.getenv('MIKROTIK_PASS', '')

print("=" * 60)
print("🤖 BOT MIKROTIK - RENDER (Python 3.13 Fix)")
print("=" * 60)
print(f"✅ Token: {TOKEN[:10]}...")
print(f"✅ MikroTik: {MIKROTIK_HOST}:{MIKROTIK_PORT}")
print(f"✅ Usuario: {MIKROTIK_USER}")
print(f"✅ Python: {sys.version[:6]}")
print("=" * 60)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user_id = str(update.effective_chat.id)
    
    if ALLOWED_CHAT_IDS and ALLOWED_CHAT_IDS != [''] and user_id not in ALLOWED_CHAT_IDS:
        await update.message.reply_text("❌ No acceso")
        return
    
    await update.message.reply_text(
        "🤖 *Bot MikroTik - Render.com*\n\n"
        f"🔌 Puerto: `{MIKROTIK_PORT}`\n"
        f"📡 IP: `{MIKROTIK_HOST}`\n\n"
        "✅ *Bot funcionando*\n\n"
        "📋 Comandos:\n"
        "/start - Este mensaje\n"
        "/ping - Probar bot\n"
        "/test - Probar MikroTik\n"
        "/port - Ver configuración",
        parse_mode='Markdown'
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ping"""
    await update.message.reply_text("🏓 ¡Pong! Bot activo")

async def port_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /port"""
    await update.message.reply_text(
        f"🔌 *Configuración actual:*\n\n"
        f"• IP: `{MIKROTIK_HOST}`\n"
        f"• Puerto: `{MIKROTIK_PORT}`\n"
        f"• Usuario: `{MIKROTIK_USER}`\n\n"
        f"_Render.com con Python {sys.version[:6]}_",
        parse_mode='Markdown'
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /test"""
    await update.message.reply_text(f"🔍 Probando {MIKROTIK_HOST}:{MIKROTIK_PORT}...")
    
    try:
        # Probar conexión simple
        import socket
        sock = socket.socket()
        sock.settimeout(10)
        
        if sock.connect_ex((MIKROTIK_HOST, MIKROTIK_PORT)) == 0:
            await update.message.reply_text(f"✅ Puerto {MIKROTIK_PORT} responde")
            sock.close()
        else:
            await update.message.reply_text(f"❌ Puerto {MIKROTIK_PORT} no responde")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)[:100]}")

def main():
    """Función principal"""
    try:
        # Crear aplicación (versión 20.x)
        app = Application.builder().token(TOKEN).build()
        
        # Comandos
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("ping", ping))
        app.add_handler(CommandHandler("port", port_info))
        app.add_handler(CommandHandler("test", test))
        
        print("✅ Bot configurado")
        print("⏳ Iniciando...")
        print("📱 Escribe /start en Telegram")
        print("=" * 60)
        
        # Iniciar
        app.run_polling()
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   {e}")

if __name__ == '__main__':
    main()
