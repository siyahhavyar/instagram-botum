import time
import json
import os
import random
import requests
import schedule
import google.generativeai as genai
from instagrapi import Client

# ==========================================
# AYARLAR (BURAYI KENDİNE GÖRE DOLDUR)
# ==========================================
INSTA_USER = "darkhistory.archive"
INSTA_PASS = "13136e2cc2"
GEMINI_KEY = "AIzaSyDASgA0ibvI6RRLt0aweAcGEzh_fn5EUeQ" # Google'dan aldığın uzun anahtar

# PAYLAŞIM SAATLERİ (Bilgisayarın açık olduğu saatler)
SAATLER = ["10:30", "15:00", "19:00", "23:00"]
# ==========================================

# --- DÜZELTME: EN SAĞLAM MODEL SEÇİLDİ ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
# -----------------------------------------

KONULAR = [
    "Tarihin Çözülememiş Gizemleri", "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları", "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler", "Paranormal Olaylar", "Arkeolojik Keşifler"
]

def icerik_uret():
    print("🧠 Gemini (Pro Modeli) içerik düşünüyor...")
    konu = random.choice(KONULAR)
    
    prompt = f"""
    Sen bir belgeselcisin. Konu: {konu}.
    Görevin: İnsanları şok edecek, çok detaylı bir Instagram kaydırmalı post içeriği hazırla.
    
    SADECE VE SADECE şu JSON formatında cevap ver (Başka hiçbir kelime etme):
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
        # JSON temizliği
        text = response.text.replace("```json", "").replace("```", "").strip()
        # Bazen başında fazladan boşluk olur, temizleyelim
        if text.startswith("json"): text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return None

def resim_ciz(prompt, dosya_adi):
    print(f"🎨 Çiziliyor: {dosya_adi}...")
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k, photorealistic")
    seed = random.randint(1, 1000000)
    # Pollinations Flux Modeli (Sınırsız)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def gorevi_baslat():
    print("\n⏰ SAAT GELDİ! İşlem başlıyor...")
    data = icerik_uret()
    if not data: return

    resim_listesi = []
    print("📸 10 Resim hazırlanıyor (Sabırlı ol)...")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            time.sleep(3) 

    if len(resim_listesi) < 2: 
        print("❌ Yeterli resim yok.")
        return

    print("🚀 Instagram'a yükleniyor...")
    cl = Client()
    try:
        # Önceki session'ı sil (Temiz giriş)
        if os.path.exists("session.json"): os.remove("session.json")
        
        cl.login(INSTA_USER, INSTA_PASS)
        cl.album_upload(paths=resim_listesi, caption=f"📢 {data['baslik']}\n\n{data['aciklama']}")
        print("✅ PAYLAŞILDI!")
        
        # Temizlik
        for r in resim_listesi: 
            if os.path.exists(r): os.remove(r)
    except Exception as e:
        print(f"❌ Instagram Hata: {e}")

# --- HEMEN ŞİMDİ TEST ET ---
print("🤖 Bot Başlatıldı! İlk test yapılıyor...")
gorevi_baslat() 

# --- SONRA ZAMANLAYICIYA GEÇ ---
for saat in SAATLER:
    schedule.every().day.at(saat).do(gorevi_baslat)

print(f"✅ Zamanlayıcı kuruldu. Pencereyi kapatma.")

while True:
    schedule.run_pending()
    time.sleep(60)
