import os
import json
import time
import datetime
import requests
import textwrap
import google.generativeai as genai
from huggingface_hub import InferenceClient
from instagrapi import Client as InstaClient
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# --- ŞİFRELER ---
HF_TOKEN = os.environ['HF_TOKEN']
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

# --- YAZI TİPİ (FONT) İNDİRME ---
# GitHub sunucularında güzel font olmadığı için Google'dan indiriyoruz
def download_font():
    font_url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
    response = requests.get(font_url)
    with open("font.ttf", "wb") as f:
        f.write(response.content)

def get_smart_content():
    print("🧠 Gemini içerik ve manşet düşünüyor...")
    
    prompt_emir = """
    Sen bir tarih ve gizem dergisi editörüsün.
    
    Görevin:
    1. Tarihten, arkeolojiden veya mitolojiden çok ilginç, şaşırtıcı ve az bilinen bir olay seç (Örnek: Ming hanedanı mezarı, Voynich yazması, Göbeklitepe'nin sırrı vb.).
    2. Bu olay için resmin ÜZERİNE yazılacak kısa, vurucu, "Clickbait" tarzı bir MANŞET yaz (Maksimum 10-12 kelime).
    3. Instagram açıklaması ve resim promptu hazırla.
    
    Bana sadece şu JSON formatını ver:
    {
      "image_text": "Resmin üzerine yazılacak vurucu başlık buraya (Örn: 2008'de Çinli arkeologlar 15. yüzyıldan kalma mühürlü bir mezar açtılar.)",
      "caption": "Instagram için detaylı, hikayeleştirilmiş Türkçe açıklama. Emojili.",
      "image_prompt": "Resim için İNGİLİZCE, cinematic, 8k, photorealistic, mysterious atmosphere prompt.",
      "tags": "#Etiketler"
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası: {e}")
        return {
            "image_text": "Tarihin En Büyük Gizemi:\nKaybolan Atlantis Uygarlığı",
            "caption": "Okyanusun derinliklerinde bir yerlerde... Atlantis gerçek mi? 👇",
            "image_prompt": "Underwater ruins of Atlantis, glowing blue, ancient greek style, cinematic, 8k",
            "tags": "#Tarih #Gizem"
        }

def add_text_to_image(image_path, text):
    """Resmin üzerine estetik yazı yazar"""
    print("🎨 Resmin üzerine yazı yazılıyor...")
    
    # Fontu indir (yoksa)
    if not os.path.exists("font.ttf"):
        download_font()
        
    img = Image.open(image_path)
    
    # 1. Resmi biraz karart (Yazı daha iyi okunsun diye)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.7) # %30 Karartma
    
    draw = ImageDraw.Draw(img)
    
    # Resim boyutları
    W, H = img.size
    
    # Font Ayarı (Resim genişliğine göre dinamik boyut)
    font_size = int(W / 18) 
    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Metni sar (Satırlara böl)
    # Her satıra yaklaşık 20 karakter sığdır
    lines = textwrap.wrap(text, width=20)
    
    # Metnin toplam yüksekliğini hesapla
    text_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_height += bbox[3] - bbox[1]
    
    # Yazıyı ortalamak için başlangıç Y koordinatı (Biraz yukarıda olsun)
    current_h = (H - text_height) / 4 
    
    # Her satırı yaz
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        # X koordinatı (Ortalamak için)
        x = (W - w) / 2
        
        # Gölge ekle (Okunabilirlik için siyah gölge)
        draw.text((x+3, current_h+3), line, font=font, fill="black")
        
        # Asıl yazı (Beyaz veya Hafif Sarı)
        draw.text((x, current_h), line, font=font, fill="#FFD700") # Altın Sarısı
        
        current_h += h + 15 # Satır aralığı

    img.save("final_post.jpg")
    print("✅ Tasarım tamamlandı!")

def main_job():
    # 1. İçerik ve Manşet Al
    content = get_smart_content()
    
    # 2. Resmi Çiz
    try:
        print(f"🖌️ Çizim: {content['image_prompt'][:30]}...")
        client = InferenceClient(model=repo_id, token=HF_TOKEN)
        image = client.text_to_image(
            f"{content['image_prompt']}, vertical, aspect ratio 2:3, 8k, cinematic lighting, photorealistic, --no text", 
            width=768, height=1344
        )
        image.save("raw_image.jpg")
    except Exception as e:
        print(f"❌ Resim Çizilemedi: {e}")
        return

    # 3. Yazıyı Resme Ekle
    try:
        add_text_to_image("raw_image.jpg", content['image_text'])
    except Exception as e:
        print(f"❌ Yazı Yazılamadı: {e}")
        return

    # 4. Paylaş
    try:
        print("📸 Instagram'a yükleniyor...")
        cl = InstaClient()
        if INSTA_SESSION:
            cl.set_settings(json.loads(INSTA_SESSION))
            cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        full_caption = f"{content['caption']}\n.\n.\n.\n{content['tags']} #Tarih #Bilgi #Gizem #YapayZeka"
        
        cl.photo_upload(path="final_post.jpg", caption=full_caption)
        print("🚀 INSTAGRAM BAŞARILI!")
        
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
