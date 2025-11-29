import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# --- ŞİFRELER ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
INSTA_SESSION = os.environ.get('INSTA_SESSION')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- KONULAR ---
KONULAR = [
    "Tarihin Çözülememiş Gizemleri", "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları", "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler", "Paranormal Olaylar", "Arkeolojik Keşifler"
]

def icerik_uret():
    print("🧠 Gemini içerik üretiyor...")
    konu = random.choice(KONULAR)
    
    prompt = f"""
    Sen bir belgesel yapımcısısın. Konu: {konu}.
    Görevin: İnsanları şok edecek, çok detaylı bir Instagram kaydırmalı post içeriği hazırla.
    
    SADECE şu JSON formatında cevap ver:
    {{
      "baslik": "Türkçe Başlık",
      "aciklama": "Konuyu anlatan çok detaylı Türkçe metin. En sona hashtagler.",
      "gorsel_komutlari": [
        "1. resim için İngilizce prompt (vertical, 8k, cinematic)",
        "2. resim için İngilizce prompt (vertical)",
        "3. resim için İngilizce prompt (vertical)",
        "4. resim için İngilizce prompt (vertical)",
        "5. resim için İngilizce prompt (vertical)",
        "6. resim için İngilizce prompt (vertical)",
        "7. resim için İngilizce prompt (vertical)",
        "8. resim için İngilizce prompt (vertical)",
        "9. resim için İngilizce prompt (vertical)",
        "10. resim için İngilizce prompt (vertical)"
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return None

def resim_ciz(prompt, dosya_adi):
    print(f"🎨 Çiziliyor: {dosya_adi}...")
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k, photorealistic, cinematic")
    seed = random.randint(1, 1000000)
    # Pollinations Flux Modeli
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        # Zaman aşımını 120 saniyeye çıkardık (Daha sabırlı olsun diye)
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def main_job():
    data = icerik_uret()
    if not data: return

    resim_listesi = []
    print("📸 10 Resim hazırlanıyor (Sabırlı olun)...")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        # Her resim çizildikten sonra 5 saniye dinlen (Hata vermemesi için)
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            time.sleep(5) 
        else:
            print(f"⚠️ {dosya_adi} çizilemedi, atlanıyor.")

    if len(resim_listesi) < 2:
        print("❌ Yeterli resim yok, işlem iptal.")
        return

    print(f"🚀 {len(resim_listesi)} resim Instagram'a yükleniyor...")
    cl = Client()
    
    try:
        if INSTA_SESSION:
            try:
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)

        cl.album_upload(
            paths=resim_listesi,
            caption=f"📢 {data['baslik']}\n\n{data['aciklama']}"
        )
        print("✅ BAŞARIYLA PAYLAŞILDI!")
        
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
