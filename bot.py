import os
import json
import time
import datetime
import requests
import random
import google.generativeai as genai
from instagrapi import Client as InstaClient

# --- ŞİFRELER (HF_TOKEN ARTIK YOK) ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_time_context():
    try:
        tr_saat = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).hour
        if 6 <= tr_saat < 12: return "Günaydın tarih meraklıları."
        elif 12 <= tr_saat < 18: return "Günün ortasından bir tarih yolculuğu."
        elif 18 <= tr_saat < 22: return "İyi akşamlar."
        else: return "Gecenin sessizliğinde bir gizem."
    except:
        return "Merhaba."

def get_smart_content():
    print("🧠 Gemini (Belgesel Modu) düşünüyor...")
    zaman_selami = get_time_context()
    
    prompt_emir = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yazarısın.
    Konsept: Antik Uygarlıklar, Mitoloji, Çözülememiş Gizemler, Uzay Tarihi, Korku Hikayeleri.
    Zaman Selamı: {zaman_selami}
    
    Görevin:
    1. Bu konulardan derinlemesine anlatılacak, insanların okuyunca bilgileneceği ilginç bir olay seç.
    2. Bana SADECE aşağıdaki JSON formatında bir çıktı ver.
    
    {{
      "caption": "Buraya seçtiğin konuyu detaylıca anlatan UZUN bir Türkçe metin yaz. Paragraflara böl. Belgesel anlatımı gibi olsun. {zaman_selami} ile başla. En sona ilgili etiketleri ekle.",
      "image_prompt_1": "Hikayenin ilk kısmını görselleştirecek İNGİLİZCE, cinematic, photorealistic, vertical prompt.",
      "image_prompt_2": "Hikayenin ikinci kısmını görselleştirecek İNGİLİZCE, cinematic, photorealistic, vertical prompt."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu. Caption uzunluğu: {len(data['caption'])} karakter.")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu devreye giriyor.")
        return {
            "caption": f"{zaman_selami}\n\nAtlantis'in gizemi binlerce yıldır çözülemedi. Platon'un bahsettiği bu ileri uygarlık gerçekten var mıydı?\n\n#Tarih #Gizem",
            "image_prompt_1": "Ancient glorious city of Atlantis, golden temples, advanced architecture, cinematic, 8k",
            "image_prompt_2": "Atlantis sinking into ocean, big waves, storm, cinematic, 8k"
        }

# --- YENİ SINIRSIZ RESSAM (POLLINATIONS) ---
def generate_image_pollinations(prompt, filename):
    print(f"🎨 Pollinations (Flux) Çiziyor: {filename}...")
    
    # URL Uyumlu Yap
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical wallpaper, 8k resolution, masterpiece, high quality, sharp focus")
    
    # Model: Flux (En Kalitelisi) | Seed: Rastgelelik
    seed = random.randint(1, 1000000)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=768&height=1344&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        # İndirme (Zaman aşımı 120 saniye)
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ BAŞARILI! {filename} indirildi.")
            return True
        else:
            print(f"❌ Sunucu Hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ İndirme Hatası: {e}")
        return False

def main_job():
    content = get_smart_content()
    paths_to_upload = []

    # 1. Resim
    if generate_image_pollinations(content['image_prompt_1'], "image1.jpg"):
        paths_to_upload.append("image1.jpg")
    else:
        print("İlk resim çizilemedi, iptal.")
        return

    # 2. Resim
    if generate_image_pollinations(content['image_prompt_2'], "image2.jpg"):
        paths_to_upload.append("image2.jpg")
    
    # Yükleme
    try:
        print(f"📸 Instagram'a {len(paths_to_upload)} resim yükleniyor...")
        cl = InstaClient()
        
        if INSTA_SESSION:
            try:
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                 cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        if len(paths_to_upload) > 1:
            cl.album_upload(paths=paths_to_upload, caption=content['caption'])
        elif len(paths_to_upload) == 1:
             cl.photo_upload(path=paths_to_upload[0], caption=content['caption'])

        print("🚀 INSTAGRAM BAŞARILI! Kaydırmalı post atıldı.")
        
    except Exception as e:
        print(f"❌ Instagram Yükleme Hatası: {e}")

if __name__ == "__main__":
    main_job()
