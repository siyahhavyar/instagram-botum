import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# --- ŞİFRELERİ KASADAN ÇEKİYORUZ ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
# Session opsiyoneldir, varsa kullanır yoksa şifreyle girer
INSTA_SESSION = os.environ.get('INSTA_SESSION')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- KONU HAVUZU ---
KONULAR = [
    "Tarihin Çözülememiş Gizemleri",
    "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları",
    "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler ve Olaylar",
    "Paranormal Fenomenler",
    "Arkeolojik Keşifler"
]

def icerik_uret():
    print("🧠 Gemini (Belgesel Editörü) 10 sayfalık dev konuyu araştırıyor...")
    secilen_konu = random.choice(KONULAR)
    
    # --- PROMPT (TAMAMLANMIŞ HALİ) ---
    prompt = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yapımcısısın.
    Konu: {secilen_konu}.
    
    Görevin:
    1. Bu konuda çok detaylı, insanı şok edecek bir olay seç.
    2. Instagram için 10 GÖRSELLİ, hikaye anlatan bir kaydırmalı (Carousel) post hazırla.
    3. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {{
      "baslik": "İlgi çekici bir başlık (Türkçe)",
      "aciklama": "Konuyu çok detaylı anlatan, 6-7 paragraflık ansiklopedik bir yazı (Türkçe). En sona etiketleri ekle.",
      "gorsel_komutlari": [
        "1. görsel (Kapak) için İngilizce prompt (Çok etkileyici, 8k, cinematic, vertical)",
        "2. görsel (Giriş) için İngilizce prompt (Olayın başlangıcı, vertical)",
        "3. görsel (Detay 1) için İngilizce prompt (vertical)",
        "4. görsel (Detay 2) için İngilizce prompt (vertical)",
        "5. görsel (Atmosfer) için İngilizce prompt (vertical)",
        "6. görsel (Karakter/Mekan) için İngilizce prompt (vertical)",
        "7. görsel (Gizem unsuru) için İngilizce prompt (vertical)",
        "8. görsel (Dramatik an) için İngilizce prompt (vertical)",
        "9. görsel (Sonuç/Soru işareti) için İngilizce prompt (vertical)",
        "10. görsel (Final/Sembolik kapak) için İngilizce prompt (vertical)"
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu (10 Görselli): {data['baslik']}")
        return data
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return None

def resim_ciz(prompt, dosya_adi):
    print(f"🎨 Çiziliyor: {dosya_adi}...")
    # Pollinations Flux Modeli (Sınırsız, Ücretsiz, Yüksek Kalite)
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k resolution, photorealistic, masterpiece, cinematic lighting, sharp focus")
    seed = random.randint(1, 1000000)
    # Boyut: 1080x1350 (Instagram Dikey)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=90) # 90 saniye bekleme süresi
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def main_job():
    # 1. İçerik Al
    data = icerik_uret()
    if not data: return

    # 2. Resimleri Çiz
    resim_listesi = []
    print(f"📸 {len(data['gorsel_komutlari'])} adet görsel hazırlanıyor (Bulut Sunucuda)...")
    print("Not: 10 resim çizmek 3-5 dakika sürebilir, lütfen bekleyin.")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            # Her resim arası 3 saniye bekle ki sunucu yorulmasın
            time.sleep(3) 
    
    if len(resim_listesi) < 2:
        print("❌ Yeterli resim çizilemedi (En az 2 lazım).")
        return

    # 3. Instagram'a Yükle
    print(f"🚀 Instagram'a {len(resim_listesi)} adet resim yükleniyor...")
    cl = Client()
    
    try:
        # Önce Session (Bilet) ile girmeyi dene, yoksa Şifre ile
        giris_basarili = False
        
        if INSTA_SESSION:
            try:
                print("🎫 Session ile giriş deneniyor...")
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
                giris_basarili = True
            except Exception as e:
                print(f"⚠️ Session hatası: {e}. Normal giriş deneniyor...")
        
        if not giris_basarili:
            print("🔑 Kullanıcı adı/Şifre ile giriş deneniyor...")
            cl.login(INSTA_USER, INSTA_PASS)

        print("✅ Giriş Başarılı!")
        
        # Albüm Yükle
        cl.album_upload(
            paths=resim_listesi,
            caption=f"📢 {data['baslik']}\n\n{data['aciklama']}"
        )
        print("🎉 TEBRİKLER! 10 GÖRSELLİ ALBÜM PAYLAŞILDI!")
        
    except Exception as e:
        print(f"❌ Instagram Paylaşım Hatası: {e}")
        print("Detaylı hata loglarına bakınız.")

if __name__ == "__main__":
    main_job()