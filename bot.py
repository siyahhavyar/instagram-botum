# bot.py  →  Instagram için sınırsız AI bot (Aralık 2025 güncel - Servisler düzeltildi!)
import os
import requests
import random
import io
from PIL import Image
import google.generativeai as genai
import asyncio

# Tek gereken secret → GEMINI_KEY (ücretsiz alınıyor)
GEMINI_KEY = os.getenv("GEMINI_KEY")
if not GEMINI_KEY:
    print("EKSİK: GEMINI_KEY → GitHub Secrets'e ekle!")
    exit(1)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')   # GÜNCEL MODEL: Stabil ve hızlı

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

# 1. Pollination (en stabil, sınırsız, direkt URL API - ana servis)
def pollination_image(prompt):
    print("Pollinations ile üretiliyor... (Sınırsız & Hızlı)")
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&nologo=true&seed={random.randint(1,1000000)}"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        print(f"Pollinations hata: {e}")
    return None

# 2. Perchance (GitHub unofficial API ile)
def perchance_image(prompt):
    print("Perchance yedek... (Unofficial API)")
    try:
        # Unofficial perchance kütüphanesi yüklü değilse, basit web hack fallback
        # Önce kütüphane dene (requirements'a ekle: pip install perchance)
        try:
            import perchance
            gen = perchance.ImageGenerator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async def gen_img():
                async with await gen.image(prompt) as result:
                    return await result.download()
            binary = loop.run_until_complete(gen_img())
            return binary
        except ImportError:
            # Fallback: Web scraping ile (ama yavaş, sadece test için)
            url = f"https://perchance.org/ai-text-to-image-generator"
            # Basit GET ile prompt gönder, ama unofficial yok - alternatif kullan
            print("Perchance kütüphanesi yok, atlanıyor.")
            return None
    except Exception as e:
        print(f"Perchance hata: {e}")
    return None

# 3. Vheer (yedek, sınırsız)
def vheer_image(prompt):
    print("Vheer yedek... (Flux tabanlı)")
    try:
        url = f"https://vheer.com/generate?prompt={requests.utils.quote(prompt)}&model=flux&width=1024&height=1024"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            data = r.json()
            if 'url' in data:
                return requests.get(data['url'], timeout=60).content
    except Exception as e:
        print(f"Vheer hata: {e}")
    return None

# Basit 2× upscale (PIL ile, daha kaliteli)
def upscale_2x(img_bytes):
    print("PIL ile 2x upscale...")
    try:
        img = Image.open(io.BytesIO(img_bytes))
        w, h = img.size
        img = img.resize((w*2, h*2), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='PNG', quality=95, optimize=True)
        return output.getvalue()
    except:
        return img_bytes  # Hata olursa orijinal dön

# ANA
def main():
    print("\nINSTAGRAM SINIRSIZ AI BOT ÇALIŞIYOR (Pollinations + Perchance + Vheer)\n")
    prompt, caption = create_prompt_and_caption()
    print(f"Prompt: {prompt[:100]}...")
    print(f"Caption: {caption}\n")

    img = pollination_image(prompt) or perchance_image(prompt) or vheer_image(prompt)
    if not img:
        print("Tüm servisler başarısız! İnternet veya servis yoğunluğu olabilir.")
        exit(1)

    final_img = upscale_2x(img)  # 2048×2048 yapıyoruz
    filename = "instagram_post.png"
    with open(filename, "wb") as f:
        f.write(final_img)

    print(f"✅ Resim kaydedildi → {filename}")
    print(f"📝 Caption → {caption}")
    print("📱 Şimdi bunu telefonundan Instagram’a atabilirsin! (Actions > Artifacts'tan indir)")

if __name__ == "__main__":
    main()
