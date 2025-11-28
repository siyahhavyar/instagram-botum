import os
import json
import time
import google.generativeai as genai
from huggingface_hub import InferenceClient
from instagrapi import Client as InstaClient

# --- ŞİFRELER ---
HF_TOKEN = os.environ['HF_TOKEN']
GEMINI_KEY = os.environ['GEMINI_KEY']  # Yeni Beyin Anahtarı
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 

repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_smart_content():
    print("🧠 Gemini (Beyin) düşünüyor... Konu aranıyor...")
    
    # Yapay Zekaya Verdiğimiz Emir
    prompt_emir = """
    Sen profesyonel bir içerik üreticisisin. Konsept: Tarih, Gizem, Mitoloji, Uzay ve Bilim.
    
    Görevin:
    1. Bu konulardan rastgele, çok bilinmeyen, ilginç bir olay seç.
    2. Bana şu formatta JSON verisi ver (Sadece JSON):
    
    {
      "caption": "Buraya Instagram için Türkçe, merak uyandıran, emojili bir açıklama yaz.",
      "image_prompt": "Buraya bu olayı anlatacak görsel için İNGİLİZCE, detaylı, sinematik, 8k, photorealistic prompt yaz.",
      "tags": "#Konuyla #İlgili #Etiketler"
    }
    """
    
    try:
        response = model.generate_content(prompt_emir)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_text)
        print(f"✅ Konu Bulundu: {data['caption'][:30]}...")
        return data
    except Exception as e:
        print(f"❌ Gemini Hatası: {e}")
        # Hata olursa yedek içerik
        return {
            "caption": "🌌 Evrenin Sırları: Karadelikler\n\nIşığın bile kaçamadığı o karanlık noktalar... İçine düşsek ne olurdu? 👇",
            "image_prompt": "Black hole in deep space, glowing accretion disk, cinematic, 8k, photorealistic",
            "tags": "#Uzay #Bilim #Gizem"
        }

def main_job():
    # 1. İçerik Üret
    content = get_smart_content()
    
    # 2. Resmi Çiz
    try:
        client = InferenceClient(model=repo_id, token=HF_TOKEN)
        # Dikey Format
        final_prompt = f"{content['image_prompt']}, vertical, aspect ratio 2:3, 8k resolution, photorealistic, masterpiece, dramatic lighting, highly detailed, --no text"
        
        print(f"🎨 Çiziliyor: {content['image_prompt'][:40]}...")
        image = client.text_to_image(final_prompt, width=768, height=1344)
        image.save("insta_post.jpg")
        print("✅ Resim Hazır!")
    except Exception as e:
        print(f"❌ Resim Çizme Hatası: {e}")
        return

    # 3. Paylaş
    try:
        cl = InstaClient()
        if INSTA_SESSION:
            cl.set_settings(json.loads(INSTA_SESSION))
            cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        full_caption = f"{content['caption']}\n.\n.\n.\n{content['tags']} #YapayZeka #AIArt #Kesfet"
        
        cl.photo_upload(path="insta_post.jpg", caption=full_caption)
        print("🚀 INSTAGRAM'A BAŞARIYLA ATILDI!")
        
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}")

if __name__ == "__main__":
    main_job()
