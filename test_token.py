import requests

TOKEN = "8523995546:AAGeWFFpTeh6dsK-DKlSolJclNQB9St_GxE"

try:
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print("✅ Token VÁLIDO")
    else:
        print("❌ Token INVÁLIDO o bloqueado")
except Exception as e:
    print(f"❌ Error de conexión: {e}")