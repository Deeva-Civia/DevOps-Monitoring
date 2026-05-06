import google.generativeai as genai
import datetime
import requests
import subprocess
import sys
import os
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

# Mengambil kredensial dari environment variable
API_KEY_GEMINI = os.getenv("GEMINI_API_KEY")
TOKEN_FONNTE = os.getenv("FONNTE_TOKEN")
TARGET_WA = os.getenv("WHATSAPP_TARGET")


# Konfigurasi API Gemini
genai.configure(api_key=API_KEY_GEMINI)

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def get_ssh_attempts():
    try:
        result = subprocess.run(
            "grep -Ei 'Failed password|Accepted password|Accepted publickey|error:|warning:' /var/log/auth.log | tail -n 10",
            shell=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error membaca log: {e}")
        return ""

def get_gemini_analysis(log_text):
    try:
        prompt = f"Berikut adalah log aktivitas server terbaru (bisa berisi login berhasil, gagal, error, atau warning):\n{log_text}\n\nTolong analisis secara singkat. Apakah ini aktivitas normal, ancaman keamanan, atau masalah sistem? Berikan satu kalimat kesimpulan dan rekomendasi tindakan."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gagal mendapatkan analisis dari Gemini: {e}"

def send_whatsapp(message):
    token = TOKEN_FONNTE
    payload = {
        "target": TARGET_WA,
        "message": message
    }
    headers = { "Authorization": token}
    r = requests.post("https://api.fonnte.com/send", data=payload, headers=headers)
    return r.status_code

# Eksekusi semua
log = get_ssh_attempts()
if not log:
    print("Tidak ada log 'Failed password' yang ditemukan. Aman.")
    sys.exit(0)

print("Terdeteksi aktivitas mencurigakan, meminta analisis AI...")
ai_response = get_gemini_analysis(log)

full_message = f"[{datetime.datetime.now()}] Server Activity Alert!\n\n{log}\n\n *Gemini Analysis:*\n{ai_response}"

print("Mengirim notifikasi WhatsApp...")
status = send_whatsapp(full_message)
print(f"Status Pengiriman WA: {status}")
