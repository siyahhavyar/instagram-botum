# bot.py  →  Instagram için sınırsız AI bot (2025 güncel)
import os
import requests
import random
import io
import base64
from PIL import Image
import google.generativeai as genai

# Tek gereken secret → GEMINI_KEY (ücretsiz alınıyor)
GEMINI_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_KEY:
    print("EKSİK: GEMINI_KEY → GitHub Secrets'e ekle!")
    exit(1)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')   # en hızlı ve ucuz

def create_prompt_and_caption():
    themes = ["Pastel kahve masası","Neon Tokyo gece","Dreamy bulutlar","Minimalist beyaz oda","Golden hour gün batımı","Crystal deniz altı"]
    theme = random.choice(themes)
    text = f"""
    Tema: {theme}
    Görev: Instagram post’u için ultra kaliteli, estetik bir AI resim prompt’u yaz.
    Aynı zamanda 1-2 cümlelik Türkçe cool bir caption da yaz.
    Format tam olarak şöyle olsun:
    PROMPT: [buraya detaylı İngilizce prompt]
    CAPTION: [buraya Türkçe caption + 6-8 emoji]
    """
    resp = model.generate_content(text).text
    try:
        prompt_part = resp.split("PROMPT:")[1].split("CAPTION:")[0].strip()
        caption_part = resp.split("CAPTION:")[1].strip()
        prompt = prompt_part + ", highly detailed, sharp focus, 8k, instagram aesthetic, perfect composition"
        return prompt, caption_part
    except:
        return "aesthetic coffee on pastel table, morning light, 8k, ultra detailed", "Sabahın en güzel anı ☕✨ #CoffeeTime #Aesthetic"

# 1. Puter.js (en güçlü, en hızlı, sınırsız)
def puter_image(prompt):
    print("Puter.js ile üretiliyor... (SD3 + Flux)")
    try:
        url = f"https://image.puter.com/v2/generate?prompt={requests.utils.quote(prompt)}&width=1024&height=1024&model=sd3"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            return r.content
    except: pass
    return None

# 2. Perchance (asla kapanmaz)
def perchance_image(prompt):
    print("Perchance yedek...")
    try:
        url = f"https://perchance.org/ai-text-to-image-generator-image?query={requests.utils.quote(prompt + ' --ar 1:1')}&width=1024&height=1024"
        r = requests.get(url, timeout=60)
        if len(r.content) > 5000:  # boş resim değilse
            return r.content
    except: pass
    return None

# 3. Raphael
def raphael_image(prompt):
    print("Raphael yedek...")
    try:
        r = requests.get(f"https://raphael.app/api/generate?prompt={requests.utils.quote(prompt)}&width=1024&height=1024", timeout=60)
        data = r.json()
        if 'image' in data:
            return requests.get(data['image']).content
    except: pass
    return None

# Basit 2× upscale (PIL ile)
def upscale_2x(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    w, h = img.size
    img = img.resize((w*2, h*2), Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format='PNG', quality=95)
    return output.getvalue()

# ANA
def main():
    print("\nINSTAGRAM SINIRSIZ AI BOT ÇALIŞIYOR\n")
    prompt, caption = create_prompt_and_caption()
    print(f"Prompt: {prompt[:100]}...")
    print(f"Caption: {caption}\n")

    img = puter_image(prompt) or perchance_image(prompt) or raphael_image(prompt)
    if not img:
        print("Tüm servisler başarısız!")
        exit(1)

    final_img = upscale_2x(img)  # 2048×2048 yapıyoruz
    filename = "instagram_post.png"
    with open(filename, "wb") as f:
        f.write(final_img)

    print(f"Resim kaydedildi → {filename}")
    print(f"Caption → {caption}")
    print("Şimdi bunu telefonundan Instagram’a atabilirsin!")

if __name__ == "__main__":
    main()
