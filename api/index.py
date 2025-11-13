# D:\cekfakta-api\api\index.py

import os
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import json

# 1. AMBIL API KEY DARI 'ENVIRONMENT VARIABLES' VERCEL
# Kita tidak menulis API key di sini. Kita akan mengaturnya di Vercel.
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY_DARI_VERCEL')

# 2. KONFIGURASI MODEL (Versi Modern)
# Server Vercel akan meng-install library versi BARU, jadi kode ini akan BERHASIL.
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error Konfigurasi API: {e}")

generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}

# Pengaturan keamanan yang akan BERFUNGSI di library modern
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Kita bisa pakai model modern
    generation_config=generation_config,
    safety_settings=safety_settings
)

# 3. FUNGSI ANALISIS (Logika "Koki")
def analyze_with_gemini(article_text):
    prompt_template = """
    Anda adalah asisten Cek Fakta yang sangat teliti dan objektif.
    Tugas Anda adalah menganalisis teks artikel berita yang diberikan oleh pengguna.
    
    TOLONG ANALISIS TEKS DI BAWAH INI:
    ---
    {artikel}
    ---
    
    Berikan respons Anda dalam format berikut:
    
    1.  **Klasifikasi:** (Berikan satu: HOAKS / KEMUNGKINAN BESAR HOAKS / TIDAK TERBUKTI / FAKTA / KEMUNGKINAN BESAR FAKTA)
    2.  **Skor Kepercayaan:** (Berikan skor dari 0% hingga 100%, di mana 100% berarti "Sangat Terpercaya/Fakta")
    3.  **Ringkasan Analisis:** (Jelaskan *mengapa* Anda memberikan klasifikasi tersebut.)
    4.  **Sumber Pembanding:** (Jika memungkinkan, berikan 1-2 link URL ke sumber kredibel.)
    """
    
    full_prompt = prompt_template.format(artikel=article_text)
    
    try:
        convo = model.start_chat()
        convo.send_message(full_prompt)
        return convo.last.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        return f"Error: Gagal menganalisis teks dengan AI. {e}"

# 4. HANDLER VERCEL (Pintu Masuk API)
# Kode ini yang membuat file ini menjadi "API"
class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # Baca data yang dikirim oleh Streamlit
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        body = json.loads(data.decode('utf-8'))
        
        # Ambil teks artikel dari JSON
        article_text = body.get('artikel', '')
        
        if not article_text:
            self.send_response(400) # Bad Request
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Tidak ada teks 'artikel' ditemukan"}).encode('utf-8'))
            return

        # Panggil "Koki"
        analysis_result = analyze_with_gemini(article_text)
        
        # Kirim balasan (hasil analisis) kembali ke Streamlit
        self.send_response(200) # OK
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"hasil_analisis": analysis_result}).encode('utf-8'))
        returnS