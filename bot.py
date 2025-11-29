import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# --- ŞİFRELER (KASADAN ÇEKİLİR) ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
INSTA_SESSION = os.environ.get('INSTA_SESSION')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Hata vermeyen garanti model
model = genai.GenerativeModel('gemini-1.5-flash')

# --- KONULAR ---
KONULAR = [
    "Tarihin Çözülememiş Gizemleri", "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları", "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler", "Paranormal Olaylar", "Arkeolojik Keşifler",
    "Kayıp Kıtalar ve Şehirler", "Simya ve Yasaklı Bilgiler"
]

def icerik_uret():
    print("🧠 Gemini içerik üretiyor...")
    secilen_konu = random.choice(KONULAR)
    
    prompt = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yapımcısısın. Konu: {secilen_konu}.
    
    Görevin:
    1. Bu konuda çok az bilinen, insanı şok edecek bir olay seç.
    2. Instagram için 10 GÖRSELLİ, hikaye anlatan bir kaydırmalı (Carousel) post hazırla.
    3. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {{
      "baslik": "İlgi çekici bir başlık (Türkçe)",
      "aciklama": "Konuyu detaylı anlatan, 5-6 paragraflık ansiklopedik yazı (Türkçe). En sona etiketleri ekle.",
      "gorsel_komutlari": [
        "1. görsel prompt (vertical, 8k, cinematic, photorealistic)",
        "2. görsel prompt (vertical)",
        "3. görsel prompt (vertical)",
        "4. görsel prompt (vertical)",
        "5. görsel prompt (vertical)",
        "6. görsel prompt (vertical)",
        "7. görsel prompt (vertical)",
        "8. görsel prompt (vertical)",
        "9. görsel prompt (vertical)",
        "10. görsel prompt (vertical)"
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
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k resolution, photorealistic")
    seed = random.randint(1, 1000000)
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

def main_job():
    data = icerik_uret()
    if not data: return

    resim_listesi = []
    print("📸 10 Resim hazırlanıyor...")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            time.sleep(2)
        else:
            print(f"⚠️ {dosya_adi} çizilemedi.")

    if len(resim_listesi) < 2:
        print("❌ Yeterli resim yok.")
        return

    print("🚀 Instagram'a yükleniyor...")
    cl = Client()
    
    try:
        # Önce Session (Pasaport) ile gir
        if INSTA_SESSION:
            try:
                print("🎫 Pasaport kullanılıyor...")
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                print("⚠️ Pasaport geçersiz, şifre ile deneniyor...")
                cl.login(INSTA_USER, INSTA_PASS)
        else:
            print("🔑 Şifre ile giriliyor...")
            cl.login(INSTA_USER, INSTA_PASS)

        print("✅ Giriş Başarılı!")
        
        cl.album_upload(
            paths=resim_listesi,
            caption=f"📢 {data['baslik']}\n\n{data['aciklama']}"
        )
        print("🎉 TEBRİKLER! GÖNDERİ PAYLAŞILDI!")
        
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
