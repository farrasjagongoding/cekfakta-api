# D:\cekfakta-api\api\index.py
# VERSI TES "HAL LAIN"

import os
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import json

# 1. AMBIL API KEY (Biarkan)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY_DARI_VERCEL')

# 2. KONFIGURASI MODEL (Biarkan)
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error Konfigurasi API: {e}")

generation_config = {
    "temperature": 0.7, # Kita buat sedikit lebih kreatif untuk resep
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}
model = genai.GenerativeModel(
    model_name="models/gemini-pro-latest",
    generation_config=generation_config
)

# 3. FUNGSI ANALISIS (PERUBAHAN BESAR DI SINI)
def analyze_with_gemini(article_text): # Kita abaikan 'article_text'
    
    # --- PERCOBAAN "HAL LAIN" (TIDAK SENSITIF) ---
    # Kita menanyakan sesuatu yang 100% aman (tidak akan diblokir)
    prompt_tes_aman = "Tuliskan resep sederhana untuk membuat nasi goreng spesial."
    # ------------------------------------------------
    
    try:
        convo = model.start_chat()
        # Kita KIRIM PROMPT YANG AMAN (bukan yang 'full_prompt')
        convo.send_message(prompt_tes_aman) 
        return convo.last.text
    except Exception as e:
        # Jika ini masih gagal, kita akan melihat errornya
        print(f"Error saat memanggil Gemini API: {e}")
        return f"Error: Gagal menganalisis teks dengan AI. {e}"

# 4. HANDLER VERCEL (Biarkan, tidak berubah)
class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        body = json.loads(data.decode('utf-8'))
        
        # Kita masih menerima 'artikel', tapi kita akan mengabaikannya
        article_text = body.get('artikel', '')

        # Panggil "Koki" (yang sekarang akan membuat resep)
        analysis_result = analyze_with_gemini(article_text)
        
        # Kirim balasan (resep) kembali ke Streamlit
        self.send_response(200) # OK
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"hasil_analisis": analysis_result}).encode('utf-8'))
        return