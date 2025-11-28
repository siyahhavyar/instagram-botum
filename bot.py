import os
import json
import time
import datetime
import google.generativeai as genai
from huggingface_hub import InferenceClient
from instagrapi import Client as InstaClient

# --- ŞİFRELER ---
HF_TOKEN = os.environ['HF_TOKEN']
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)

# DÜZELTME: En kararlı model seçildi
model = genai.GenerativeModel('gemini-pro') 

repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_time_context():
    # TR Saati (UTC+3)
    try:
        tr_saat = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).hour
        if 6 <= tr_saat < 12: return "Sabah"
        elif 12 <= tr_saat < 18: return "Öğlen"
        elif 18 <= tr_saat < 22: return "Akşam"
        else: return "Gece Yarısı"
    except:
        return "Günlük"

def get_smart_content():
    print("🧠 Gemini (Beyin) düşünüyor...")
    zaman = get_time_context()
    
    # Çok net ve kısa emir
    prompt_emir = f"""
    Sen sosyal medya içerik üreticisisin. Konsept: Tarih, Gizem, Uzay, Mitoloji.
    Şu an vakit: {zaman}.
    
    Görevin:
    1. İnsanların ilgisini çekecek, az bilinen gizemli bir olay seç.
    2. Sadece ve sadece aşağıdaki JSON formatında cevap ver. Başka hiçbir şey yazma.
    
    {{
      "caption": "Buraya Instagram için Türkçe, merak uyandıran, emojili bir açıklama yaz.",
      "image_prompt": "Buraya görsel için İNGİLİZCE, cinematic, 8k, photorealistic, vertical, highly detailed prompt yaz.",
      "tags": "#Konuyla #İlgili #Etiketler"
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        # Temizlik yapalım (Markdown temizliği)
        text = response.text.replace("```json", "").replace("```", "").strip()
        if "{" not in text: raise Exception("JSON formatı bozuk")
        
        data = json.loads(text)
        print(f"✅ Konu Bulundu: {data['caption'][:30]}...")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu devreye giriyor.")
        return {
            "caption": "🌌 Evrenin Sınırları: Karadelikler\n\nIşık bile kaçamaz. Peki ya zaman? Olay ufkunun ötesinde ne var?\n\nTeorilerinizi yazın. 👇",
            "image_prompt": "Black hole in deep space, glowing accretion disk, cinematic, 8k, vertical, masterpiece",
            "tags": "#Uzay #Bilim #Gizem #Karadelik"
        }

def main_job():
    # 1. İçerik
    content = get_smart_content()
    
    # 2. Resim
    try:
        print(f"🎨 Çiziliyor: {content['image_prompt'][:30]}...")
        client = InferenceClient(model=repo_id, token=HF_TOKEN)
        
        # Dikey Format Zorlaması
        image = client.text_to_image(
            f"{content['image_prompt']}, vertical, aspect ratio 2:3", 
            width=768, height=1344
        )
        image.save("insta_post.jpg")
        print("✅ Resim Hazır!")
    except Exception as e:
        print(f"❌ Resim Hatası (HuggingFace): {e}")
        return

    # 3. Paylaş
    try:
        print("📸 Instagram'a yükleniyor...")
        cl = InstaClient()
        
        # Session varsa onu kullan, yoksa şifreyle dene
        if INSTA_SESSION:
            try:
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                cl.login(INSTA_USER, INSTA_PASS) # Session bozuksa normal gir
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        cl.photo_upload(
            path="insta_post.jpg", 
            caption=f"{content['caption']}\n.\n.\n{content['tags']}"
        )
        print("🚀 INSTAGRAM BAŞARILI!")
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
