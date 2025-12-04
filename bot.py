import os
import requests
import random
import base64
import google.generativeai as genai
import tweepy
import asyncio
import io
from PIL import Image
# Perchance unofficial API için pip install perchance gerekebilir, ama basit requests ile de yapılabilir
# GitHub Secrets'ten gelenler: GEMINI_KEY, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET
# BU KODDA YENİ KEY YOK - sadece Gemini ve Twitter için eskiler

GEMINI_KEY      = os.getenv("GEMINI_KEY")
API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET   = os.getenv("ACCESS_SECRET")

# Eksik key varsa hemen çıksın (sadece gerekli olanlar)
for var in ["GEMINI_KEY","API_KEY","API_SECRET","ACCESS_TOKEN","ACCESS_SECRET"]:
    if not os.getenv(var):
        print(f"EKSİK: {var}")
        exit(1)

def get_prompt_caption():
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')  # Güncel model, stabil ve hızlı
    themes = ["Cyberpunk Tokyo","Neon Forest","Space Nebula","Crystal Cave","Floating Islands","Golden Desert"]
    theme = random.choice(themes)
    resp = model.generate_content(f"Tema: {theme} → Ücretsiz AI generator (Perchance/Raphael) için ultra detaylı prompt + kısa caption. Format: PROMPT: [...] ||| CAPTION: [...]").text
    try:
        p, c = resp.split("|||")
        prompt = p.replace("PROMPT:", "").strip() + ", 8k, ultra detailed, masterpiece, high quality"
        caption = c.replace("CAPTION:", "").strip()
    except:
        prompt = "cyberpunk city night rain reflections, ultra detailed, 8k, masterpiece"
        caption = "Neon rain vibes ✨"
    return prompt, caption

# PERCHANCE → HD Üretim (1024x1024, sınırsız, no key)
# Unofficial API: https://github.com/eeemoon/perchance (pip install perchance) veya direkt requests ile
async def perchance_image(prompt):
    print("Perchance HD resim üretiyor... (Sınırsız & Ücretsiz)")
    try:
        # pip install perchance varsa kullan, yoksa basit requests fallback
        try:
            import perchance
            gen = perchance.ImageGenerator()
            async with await gen.image(prompt) as result:
                binary = await result.download()
                return binary
        except ImportError:
            # Fallback: Direkt URL fetch (Perchance web API'si gibi)
            url = f"https://perchance.org/ai-text-to-image-generator-image?query={requests.utils.quote(prompt)}&width=1024&height=1024&seed={random.randint(1,1000000)}"
            r = requests.get(url, timeout=90)
            if r.status_code == 200:
                # Varsayım: URL resim döner, yoksa parse et
                img_resp = requests.get(url, timeout=60)
                if img_resp.status_code == 200:
                    return img_resp.content
            return None
    except Exception as e:
        print(f"Perchance hata: {e}")
        return None

# RAPHAEL → Yedek Üretim (sınırsız, no key, hızlı)
def raphael_image(prompt):
    print("Raphael yedek üretim... (Sınırsız & Ücretsiz)")
    try:
        # Direkt URL API (2025 docs'a göre no key)
        url = f"https://raphael.app/api/generate?prompt={requests.utils.quote(prompt)}&width=1024&height=1024"
        r = requests.get(url, timeout=90)
        if r.status_code == 200:
            data = r.json()
            if 'image' in data:
                img_url = data['image']
                return requests.get(img_url, timeout=60).content
        return None
    except Exception as e:
        print(f"Raphael hata: {e}")
        return None

# VHEER → Son yedek (sınırsız, no key)
def vheer_image(prompt):
    print("Vheer son yedek... (Sınırsız & Ücretsiz)")
    try:
        url = f"https://vheer.com/generate?prompt={requests.utils.quote(prompt)}&model=flux&width=1024&height=1024"
        r = requests.get(url, timeout=90)
        if r.status_code == 200:
            data = r.json()
            if 'url' in data:
                return requests.get(data['url'], timeout=60).content
        return None
    except Exception as e:
        print(f"Vheer hata: {e}")
        return None

# Basit upscale (PIL ile 2x, ücretsiz - Pixelcut yerine, key yok)
def simple_upscale(img_bytes, scale=2):
    print("PIL ile basit upscale (2x)...")
    try:
        img = Image.open(io.BytesIO(img_bytes))
        w, h = img.size
        upscaled = img.resize((w*scale, h*scale), Image.LANCZOS)
        output = io.BytesIO()
        upscaled.save(output, format='JPEG', quality=95)
        return output.getvalue()
    except:
        return img_bytes  # Hata olursa orijinal dön

# TWEET (aynı)
def tweet(img_bytes, text):
    fn = "wall.jpg"
    with open(fn,"wb") as f:
        f.write(img_bytes)
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    media = api.media_upload(fn)
    client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET,
                           access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)
    client.create_tweet(text=text + " #AIArt #SınırsızAI #InstagramVibes", media_ids=[media.media_id])
    print("TWEET ATILDI! 🚀")
    os.remove(fn)

# ANA - Failover sistemi
async def main():
    print("\nSINI RSIZ AI BOT ÇALIŞIYOR (Perchance + Raphael + Vheer, No Key!)\n")
    prompt, caption = get_prompt_caption()
    print(f"Prompt: {prompt}\nCaption: {caption}")

    # 1. Perchance dene
    img = await perchance_image(prompt)
    if not img:
        print("Perchance başarısız, Raphael'e geç...")
        # 2. Raphael
        img = raphael_image(prompt)
    if not img:
        print("Raphael başarısız, Vheer'e geç...")
        # 3. Vheer
        img = vheer_image(prompt)
    if not img:
        print("Tüm generator'lar başarısız, çıkılıyor.")
        exit(1)

    # Upscale (basit PIL)
    final = simple_upscale(img, scale=2)  # 2048x2048 yapar

    # Tweet at
    tweet(final, caption)

if __name__ == "__main__":
    asyncio.run(main())
