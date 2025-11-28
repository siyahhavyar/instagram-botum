import os
import json
import time
import datetime
import requests
import random
import google.generativeai as genai
from instagrapi import Client as InstaClient

# --- ŞİFRELER ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_smart_content():
    print("🧠 Gemini (Belgesel Editörü) çalışıyor...")
    
    konular = [
        "Antik Uygarlıkların Kayıp Teknolojileri", "Mitolojik Tanrılar ve Hikayeleri", 
        "Çözülememiş Tarihi Gizemler", "Korkunç ve Tuhaf Tarihi Olaylar", 
        "Uzay ve Evrenin Korkutucu Sırları", "Mistik ve Paranormal Olaylar",
        "Efsanevi Yaratıklar", "Tarihi Komplo Teorileri", "Arkeolojik Keşifler"
    ]
    secilen_konu = random.choice(konular)

    prompt_emir = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yazarısın.
    GÖREVİN: "{secilen_konu}" kategorisinden rastgele, çok bilinmeyen, ilginç bir konu seç (Sürekli aynı şeyleri seçme).
    
    Bana SADECE aşağıdaki JSON formatında bir çıktı ver. Başka hiçbir şey yazma.
    
    {{
      "baslik": "Konunun Çarpıcı ve İlgi Çekici Başlığı",
      "caption": "Buraya konuyu derinlemesine anlatan, 4-5 paragraftan oluşan, ansiklopedik, bilgi dolu ve sürükleyici bir TÜRKÇE makale yaz. Okuyan kişi yeni bir şey öğrensin.",
      "tags": "Buraya KONUYLA DOĞRUDAN ALAKALI, keşfete düşürecek 15-20 adet Türkçe ve İngilizce hashtag yaz. (Örnek: Konu Mısır ise #Hieroglif #Firavun #AncientEgypt yaz, genel etiket yazma).",
      "image_prompts": [
        "Konuyu anlatan genel atmosfer promptu (İngilizce, 8k, cinematic, photorealistic)",
        "Konunun detayını gösteren close-up prompt (İngilizce)",
        "Konudaki karakterleri veya nesneleri gösteren prompt (İngilizce)",
        "Olayın geçtiği mekanı gösteren prompt (İngilizce)",
        "Dramatik bir anı gösteren prompt (İngilizce)",
        "Mistik ve gizemli bir hava katan prompt (İngilizce)",
        "Tarihi belge veya eski çizim tarzında prompt (İngilizce)",
        "Farklı bir açıdan prompt (İngilizce)",
        "Sinematik ışıklandırmalı epik bir sahne promptu (İngilizce)",
        "Konuyu özetleyen sembolik bir görsel promptu (İngilizce)"
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu: {data['baslik']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu devreye giriyor.")
        return {
            "baslik": "Antik Mısır'ın Kayıp Labirenti",
            "caption": "Mısır piramitlerinin gölgesinde, tarihin tozlu sayfaları arasında kaybolmuş bir yapı: Hawara Labirenti...\n\nHerodot'un anlatımlarına göre bu yapı, piramitlerden bile daha ihtişamlıydı. 3000 odadan oluşan, yer altı ve yer üstü katlarına sahip bu devasa kompleks, antik dünyanın en büyük gizemlerinden biri olarak kabul edilir.",
            "tags": "#Mısır #Tarih #Arkeoloji #Gizem #AntikDünya #AncientEgypt #LostHistory #Herodotus #Piramit",
            "image_prompts": [
                "Ancient Egyptian labyrinth Hawara, massive columns, mystery, cinematic, 8k",
                "Dark underground tunnels of Egypt, torch light, mysterious hieroglyphs, photorealistic",
                "Herodotus looking at the great labyrinth, historical painting style",
                "Golden artifacts inside a hidden chamber, glitter, cinematic lighting",
                "Aerial view of ancient Hawara complex, desert, sunset, 8k",
                "Mysterious door sealed with ancient magic, fantasy style",
                "Archaeologists discovering a secret passage, dramatic light, 1920s style",
                "Statues of crocodile god Sobek, stone texture, realistic",
                "Sandstorm covering ancient ruins, mystery atmosphere",
                "Detailed map of the labyrinth on papyrus, macro shot"
            ]
        }

# --- SINIRSIZ RESSAM (POLLINATIONS) ---
def generate_image_pollinations(prompt, filename):
    print(f"🎨 Çiziliyor: {filename}...")
    # Flux modeli ve kalite ayarları
    prompt_encoded = requests.utils.quote(f"{prompt}, vertical wallpaper, 8k resolution, photorealistic, masterpiece, sharp focus, cinematic lighting")
    seed = random.randint(1, 1000000)
    # Boyut: 1080x1350 (Instagram Portre - En iyi görünüm)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1080&height=1350&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except:
        return False

def main_job():
    content = get_smart_content()
    paths_to_upload = []

    # 10 Resim Çizdirme
    print("📸 10 Adet görsel hazırlanıyor (Flux kalitesiyle)...")
    for i, prompt in enumerate(content['image_prompts']):
        filename = f"image_{i+1}.jpg"
        if generate_image_pollinations(prompt, filename):
            paths_to_upload.append(filename)
            time.sleep(3) # Sunucuyu yormamak için bekleme
    
    if len(paths_to_upload) == 0:
        print("❌ Hiçbir resim çizilemedi.")
        return

    # Instagram'a Yükle (Albüm)
    try:
        print(f"🚀 Instagram'a {len(paths_to_upload)} görsel yükleniyor...")
        cl = InstaClient()
        
        # Giriş
        if INSTA_SESSION:
            try:
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        # Başlık + Metin + Etiketler Birleştirme
        final_caption = f"📢 {content['baslik']}\n\n{content['caption']}\n.\n.\n.\n{content['tags']}"
        
        # Paylaş
        cl.album_upload(
            paths=paths_to_upload,
            caption=final_caption
        )
        print("✅ BAŞARIYLA PAYLAŞILDI!")
        
        # Temizlik
        for path in paths_to_upload:
            if os.path.exists(path):
                os.remove(path)
            
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
