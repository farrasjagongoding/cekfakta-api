# D:\cekfakta-api\api\index.py

import os
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import json

# 1. AMBIL API KEY DARI 'ENVIRONMENT VARIABLES' VERCEL
# (Ini sudah benar, JANGAN DIGANTI)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY_DARI_VERCEL')

# 2. KONFIGURASI MODEL
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

# Pengaturan keamanan (kita tetap coba kirim, walau mungkin diabaikan)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Nama model yang SUDAH TERBUKTI BISA di environment Anda
model = genai.GenerativeModel(
    model_name="models/gemini-pro-latest", # INI NAMA YANG BENAR
    generation_config=generation_config
    # safety_settings akan kita kirim saat 'send_message'
)

# 3. FUNGSI ANALISIS (Logika "Koki" dengan PROMPT BARU)
def analyze_with_gemini(article_text):
    
    # --- PERBAIKAN DI SINI: PROMPT BARU YANG LEBIH HALUS ---
    prompt_template = """
    Anda adalah asisten riset yang netral dan objektif.
    Tugas Anda adalah membandingkan teks yang diberikan pengguna dengan informasi yang tersedia untuk umum.
    
    TOLONG PERIKSA TEKS DI BAWAH INI:
    ---
    {artikel}
    ---
    
    Tolong berikan respons Anda:
    
    1.  **Ringkasan Klaim:** (Apa klaim utama dari teks di atas? Tulis dalam 1 kalimat)
    2.  **Perbandingan Fakta:** (Berdasarkan informasi yang tersedia untuk umum, apakah klaim tersebut akurat? Jelaskan temuan Anda secara netral. Jika klaim itu tidak akurat, tolong berikan informasi yang benar.)
    3.  **Sumber Kredibel:** (Jika memungkinkan, berikan 1-2 link URL ke sumber kredibel yang membahas klaim ini.)
    """
    # -----------------------------------------------------------
    
    full_prompt = prompt_template.format(artikel=article_text)
    
    try:
        convo = model.start_chat()
        # Mengirim prompt + safety_settings (sintaks library lama)
        convo.send_message(
            full_prompt,
            safety_settings=safety_settings
        )
        return convo.last.text
    except Exception as e:
        print(f"Error saat memanggil Gemini API: {e}")
        # Mengembalikan error ke Streamlit agar kita tahu apa yang salah
        return f"Error: Gagal menganalisis teks dengan AI. {e}"

# 4. HANDLER VERCEL (Pintu Masuk API) - TIDAK BERUBAH
class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # Baca data JSON yang dikirim oleh Streamlit
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

        # Panggil "Koki" (Gemini)
        analysis_result = analyze_with_gemini(article_text)
        
        # Kirim balasan (hasil analisis) kembali ke Streamlit
        self.send_response(200) # OK
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"hasil_analisis": analysis_result}).encode('utf-8'))
        return