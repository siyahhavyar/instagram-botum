   import os
import time
import requests
import random
import urllib.parse
import json
import google.generativeai as genai
from datetime import datetime
from instagrapi import Client

# -----------------------------
# ENV KEYS
# -----------------------------
INSTA_USER    = os.getenv("INSTA_USER")
INSTA_PASS    = os.getenv("INSTA_PASS")
INSTA_SESSION = os.getenv("INSTA_SESSION")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
HORDE_KEY     = os.getenv("HORDE_API_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# --- KEY TEMİZLİĞİ (Görünmez boşlukları siler) ---
if HORDE_KEY: HORDE_KEY = HORDE_KEY.strip()
if GROQ_KEY: GROQ_KEY = GROQ_KEY.strip()
if GEMINI_KEY: GEMINI_KEY = GEMINI_KEY.strip()

if not HORDE_KEY or len(HORDE_KEY) < 10:
    print(f"⚠️ UYARI: Horde Key yok. Anonim mod (Yavaş).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif!", flush=True)

# -----------------------------
# 1. BELGESEL YAZARI (GROQ ÖNCELİKLİ)
# -----------------------------
def get_documentary_content():
    # Rastgele kategori seçimi
    categories = [
        "Lost Mayan Temples in Jungle",
        "Deep Sea Titanic-like Shipwrecks",
        "Cursed Egyptian Tombs",
        "Cyberpunk Neon City Alleys",
        "Victorian London Mystery",
        "Alien Pyramids on Mars",
        "Steampunk Flying Cities",
        "Post-Apocalyptic New York",
        "Viking Valhalla Halls",
        "Samurai Temples in Snow"
    ]
    chosen_cat = random.choice(categories)
    print(f"🎲 Kategori: {chosen_cat}", flush=True)

    # Yapay Zekaya Emir
    instructions = f"""
    Act as a Documentary Director. TOPIC: {chosen_cat}
    
    TASK 1: Create 10 DISTINCT image prompts for a visual story.
    TASK 2: Write an Instagram Caption (Title, Story, Hashtags).
    
    OUTPUT FORMAT (Strictly):
    SCENE_1: <Visual prompt 1>
    SCENE_2: <Visual prompt 2>
    ...
    SCENE_10: <Visual prompt 10>
    CAPTION: <Full caption text>
    """

    # --- PLAN A: GROQ (LLAMA 3.3 - FAVORİ) ---
    if GROQ_KEY:
        try:
            print("🧠 Plan A: Groq (Llama 3.3) öncelikli olarak deneniyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_KEY}", 
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile", # Groq'un en iyi modeli
                "messages": [{"role": "user", "content": instructions}],
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                text = response.json()['choices'][0]['message']['content']
                if "SCENE_1" in text:
                    print("   ✅ BAŞARILI: Groq senaryoyu yazdı!", flush=True)
                    return parse_ai_response(text)
            else:
                print(f"   ⚠️ Groq Hatası: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Groq Bağlantı Hatası: {e}")
    else:
        print("   ℹ️ Groq Key tanımlı değil, diğer plana geçiliyor.")

    # --- PLAN B: POLLINATIONS (BEDAVA & SINIRSIZ) ---
    try:
        print("🧠 Plan B: Pollinations (Sınırsız) deneniyor...", flush=True)
        seed = random.randint(1, 999999)
        encoded_prompt = urllib.parse.quote(instructions)
        url = f"https://text.pollinations.ai/{encoded_prompt}?seed={seed}&model=openai"
        
        response = requests.get(url, timeout=60)
        text = response.text
        
        if "SCENE_1" in text:
            print("   ✅ BAŞARILI: Pollinations senaryoyu yazdı!", flush=True)
            return parse_ai_response(text)
            
    except Exception as e:
        print(f"   ❌ Pollinations Hatası: {e}")

    # --- PLAN C: GEMINI (YEDEK) ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan C: Gemini deneniyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            # En son çıkan modelleri dener
            models = ["gemini-2.0-flash", "gemini-1.5-flash"]
            for m in models:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(instructions)
                    if "SCENE_1" in response.text:
                         print(f"   ✅ BAŞARILI: {m} senaryoyu yazdı!", flush=True)
                         return parse_ai_response(response.text)
                except: continue
        except: pass

    # --- PLAN D: MANUEL YEDEK ---
    print("⚠️ Tüm yapay zekalar meşgul. Manuel yedek devreye girdi.", flush=True)
    fallback_prompts = [f"Cinematic shot of {chosen_cat}, scene {i}, highly detailed" for i in range(1, 11)]
    return fallback_prompts, f"The mystery of {chosen_cat}... #Mystery #History"

def parse_ai_response(text):
    """Yapay zeka çıktısını parçalar"""
    prompts = []
    caption_lines = []
    is_caption = False
    
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        
        if "SCENE_" in line and ":" in line:
            parts = line.split(":", 1)
            if len(parts) > 1: prompts.append(parts[1].strip())
        elif "CAPTION:" in line:
            is_caption = True
            parts = line.split(":", 1)
            if len(parts) > 1: caption_lines.append(parts[1].strip())
        elif is_caption:
            caption_lines.append(line)
            
    while len(prompts) < 10:
        prompts.append(prompts[-1] if prompts else "Mysterious dark cinematic scene")
        
    return prompts[:10], "\n".join(caption_lines)

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ
# -----------------------------
def generate_album_images(prompt_list):
    global HORDE_KEY
    print(f"🎨 {len(prompt_list)} Farklı Sahne Çiziliyor...", flush=True)
    generated_files = []
    
    for i, specific_prompt in enumerate(prompt_list):
        print(f"   🎬 Sahne {i+1}/10: {specific_prompt[:40]}...", flush=True)
        
        final_prompt = (
            f"{specific_prompt}, "
            "photorealistic, 8k, cinematic lighting, highly detailed, "
            "dramatic shadows, vertical aspect ratio 4:5"
        )
        
        unique_seed = str(random.randint(1, 9999999999))
        
        params = {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 832,      
            "height": 1024,
            "steps": 30,          
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"]
        }
        
        # Anonim mod ayarı
        if HORDE_KEY == "0000000000":
            params["post_processing"] = []
            params["steps"] = 25

        payload = {
            "prompt": final_prompt,
            "params": params,
            "nsfw": False,
            "censor_nsfw": True,
            "models": ["Juggernaut XL", "AlbedoBase XL (SDXL)"]
        }
        
        try:
            req = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v16.0"}, timeout=30)
            
            if req.status_code == 401:
                print("   ⚠️ Key hatası (401). Anonim moda geçiliyor.")
                HORDE_KEY = "0000000000"
                payload["params"]["post_processing"] = []
                req = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers={"apikey": HORDE_KEY}, timeout=30)

            if req.status_code != 202: continue
            task_id = req.json()['id']
            
            img_done = False
            for _ in range(60): 
                time.sleep(15)
                try:
                    chk = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
                    
                    # Sıra bilgisini göster
                    if 'queue_position' in chk:
                        qp = chk['queue_position']
                        if qp > 0: print(f"      ⏳ Sıra: {qp}...", flush=True)

                    if chk['done'] and len(chk['generations']) > 0:
                        img_data = requests.get(chk['generations'][0]['img'], timeout=60).content
                        fname = f"slide_{i+1}.jpg"
                        with open(fname, "wb") as f: f.write(img_data)
                        generated_files.append(fname)
                        print(f"      ✅ İndirildi.", flush=True)
                        img_done = True
                        break
                except: pass
        except: pass

    return generated_files

# -----------------------------
# 3. INSTAGRAM PAYLAŞIMI
# -----------------------------
def upload_album(paths, caption):
    if not paths: return False
    try:
        print("📸 Instagram oturumu açılıyor...", flush=True)
        cl = Client()
        session_loaded = False
        if INSTA_SESSION:
            try:
                cl.load_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
                print("✅ Session ile giriş başarılı!", flush=True)
                session_loaded = True
            except: 
                print("⚠️ Session geçersiz, normal giriş deneniyor.")
        
        if not session_loaded: 
            cl.login(INSTA_USER, INSTA_PASS)
        
        print(f"📤 {len(paths)} Parçalı Albüm Yükleniyor...", flush=True)
        cl.album_upload(paths=paths, caption=caption)
        print("✅ ALBÜM PAYLAŞILDI!", flush=True)
        return True
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}", flush=True)
        return False
    finally:
        for p in paths:
            if os.path.exists(p): os.remove(p)

if __name__ == "__main__":
    print("🚀 GİZEMLİ TARİH BOTU (V16 - GROQ GÜCÜ)...", flush=True)
    prompts, caption = get_documentary_content()
    print(f"\n📝 BAŞLIK: {caption.splitlines()[0]}")
    print(f"🎬 SAHNE SAYISI: {len(prompts)}")
    
    images = generate_album_images(prompts)
    if len(images) >= 2: upload_album(images, caption)
    else: print("⚠️ Yeterli resim yok.")
        
