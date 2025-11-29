import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# ==========================================
# 1. GÜVENLİK VE AYARLAR (KASADAN ÇEKİLİR)
# ==========================================
# Bu bilgileri GitHub > Settings > Secrets kısmına eklemiş olman lazım.
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
INSTA_SESSION = os.environ.get('INSTA_SESSION') # Pasaport (Bilet)

# Gemini Başlat
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# Konu Havuzu
KONULAR = [
    "Tarihin Çözülememiş Gizemleri", "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları", "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler", "Paranormal Olaylar", "Arkeolojik Keşifler",
    "Kayıp Kıtalar ve Şehirler", "Simya ve Yasaklı Bilgiler"
]

# ==========================================
# 2. BEYİN: GEMINI (İÇERİK ÜRETİCİ)
# ==========================================
def icerik_uret():
    print("🧠 Gemini (Belgesel Editörü) çalışıyor...")
    secilen_konu = random.choice(KONULAR)
    
    prompt = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yapımcısısın.
    Konu: {secilen_konu}.
    
    Görevin:
    1. Bu konuda çok az bilinen, insanı şok edecek bir olay seç.
    2. Instagram için 10 GÖRSELLİ, hikaye anlatan bir kaydırmalı (Carousel) post hazırla.
    3. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {{
      "baslik": "İlgi çekici bir başlık (Türkçe)",
      "aciklama": "Konuyu detaylı anlatan, 5-6 paragraflık ansiklopedik, doyurucu bir yazı (Türkçe). En sona etiketleri ekle.",
      "gorsel_komutlari": [
        "1. görsel (Kapak) için İngilizce prompt (Çok etkileyici, 8k, cinematic, vertical)",
        "2. görsel için İngilizce prompt (vertical)",
        "3. görsel için İngilizce prompt (vertical)",
        "4. görsel için İngilizce prompt (vertical)",
        "5. görsel için İngilizce prompt (vertical)",
        "6. görsel için İngilizce prompt (vertical)",
        "7. görsel için İngilizce prompt (vertical)",
        "8. görsel için İngilizce prompt (vertical)",
        "9. görsel için İngilizce prompt (vertical)",
        "10. görsel (Final) için İngilizce prompt (vertical)"
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu: {data['baslik']}")
        return data
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        return None

# ==========================================
# 3. RESSAM: POLLINATIONS FLUX (SINIRSIZ)
# ==========================================
def resim_ciz(prompt, dosya_adi):
    print(f"🎨 Çiziliyor: {dosya_adi}...")
    
    # Promptu URL uyumlu hale getir ve kalite ekle
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical, 8k resolution, photorealistic, masterpiece, cinematic lighting, sharp focus")
    seed = random.randint(1, 1000000)
    
    # Pollinations Flux Modeli (1080x1350 Instagram Dikey)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        # İndirme işlemi (90 saniye bekleme süresi)
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            with open(dosya_adi, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

# ==========================================
# 4. ANA PROGRAM VE PAYLAŞIM
# ==========================================
def main_job():
    # A) İçeriği Al
    data = icerik_uret()
    if not data: return

    # B) 10 Resmi Çiz
    resim_listesi = []
    print("📸 10 Resim hazırlanıyor (Sabırlı olun)...")
    
    for i, prompt in enumerate(data['gorsel_komutlari']):
        dosya_adi = f"resim_{i+1}.jpg"
        # Resmi çiz, başarısız olursa tekrar dene (basit retry)
        if resim_ciz(prompt, dosya_adi):
            resim_listesi.append(dosya_adi)
            time.sleep(3) # Sunucuyu yormamak için bekle
        else:
            print(f"⚠️ {dosya_adi} çizilemedi.")

    if len(resim_listesi) < 2:
        print("❌ Yeterli resim yok, işlem iptal.")
        return

    # C) Instagram'a Yükle
    print(f"🚀 {len(resim_listesi)} resim Instagram'a yükleniyor...")
    cl = Client()
    
    try:
        # PASAPORT (SESSION) İLE GİRİŞ - EN KRİTİK KISIM
        if INSTA_SESSION:
            try:
                print("🎫 Pasaport ile giriliyor...")
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                print("⚠️ Pasaport eski, normal giriş deneniyor...")
                cl.login(INSTA_USER, INSTA_PASS)
        else:
            print("🔑 Şifre ile giriliyor (Riskli)...")
            cl.login(INSTA_USER, INSTA_PASS)

        print("✅ Giriş Başarılı!")

        # Albüm Paylaşımı
        cl.album_upload(
            paths=resim_listesi,
            caption=f"📢 {data['baslik']}\n\n{data['aciklama']}"
        )
        print("🎉 TEBRİKLER! GÖNDERİ PAYLAŞILDI!")
        
        # Temizlik (Resimleri sil)
        for r in resim_listesi:
            if os.path.exists(r):
                os.remove(r)
            
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()