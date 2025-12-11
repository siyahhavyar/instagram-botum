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

# --- KEY TEMİZLİĞİ ---
if HORDE_KEY: HORDE_KEY = HORDE_KEY.strip()
if GROQ_KEY: GROQ_KEY = GROQ_KEY.strip()
if GEMINI_KEY: GEMINI_KEY = GEMINI_KEY.strip()

if not HORDE_KEY or len(HORDE_KEY) < 10:
    print(f"⚠️ UYARI: Horde Key yok. Anonim mod (Yavaş).", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key aktif!", flush=True)

# -----------------------------
# 1. BELGESEL YAZARI (AYDINLIK & ÇEŞİTLİ)
# -----------------------------
def get_documentary_content():
    categories = [
        "Lost Mayan Temples in Jungle (Daylight)",
        "Deep Sea Titanic-like Shipwrecks (Clear water)",
        "Cursed Egyptian Tombs (Golden hour)",
        "Cyberpunk Neon City Alleys (Colorful)",
        "Victorian London Mystery (Foggy but bright)",
        "Alien Pyramids on Mars (Red sunset)",
        "Steampunk Flying Cities (Blue sky)",
        "Post-Apocalyptic New York (Overgrown)",
        "Viking Valhalla Halls (Epic lighting)",
        "Samurai Temples in Snow (Sunny)"
    ]
    chosen_cat = random.choice(categories)
    print(f"🎲 Kategori: {chosen_cat}", flush=True)

    instructions = f"""
    Act as a Professional Documentary Director. TOPIC: {chosen_cat}
    
    TASK 1: Create 10 DISTINCT, VIBRANT, and EPIC image prompts for a visual story.
    - Focus on majestic, cinematic, and awe-inspiring visuals.
    - AVOID overly dark or horror themes. Use words like "majestic," "golden light," "fantasy," "epic scale."
    
    TASK 2: Write an Instagram Caption matching this EXACT structure:
    
    🛑 [CATCHY TITLE IN UPPERCASE]
    
    📖 THE STORY:
    [Write 2 engaging paragraphs about the history or legend.]
    
    🔍 THE MYSTERY:
    [Explain what makes this topic mysterious and fascinating.]
    
    🧠 DID YOU KNOW?:
    [Write one surprising fact about this topic.]
    
    #️⃣ HASHTAGS:
    [List 15 relevant hashtags here]
    
    OUTPUT FORMAT (Strictly):
    SCENE_1: <Visual prompt 1>
    SCENE_2: <Visual prompt 2>
    ...
    SCENE_10: <Visual prompt 10>
    CAPTION: <The full caption starting with the title>
    """

    # --- PLAN A: GROQ (LLAMA 3.3) ---
    if GROQ_KEY:
        try:
            print("🧠 Plan A: Groq (Llama 3.3) öncelikli deneniyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_KEY}", 
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
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

    # --- PLAN B: POLLINATIONS (BEDAVA) ---
    try:
        print("🧠 Plan B: Pollinations deneniyor...", flush=True)
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

    # --- PLAN C: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan C: Gemini deneniyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
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
    fallback_prompts = [f"Cinematic fantasy shot of {chosen_cat}, scene {i}, vibrant colors" for i in range(1, 11)]
    return fallback_prompts, f"🛑 MYSTERY OF {chosen_cat.upper()}\n\n📖 THE STORY:\nA mysterious event...\n\n#Mystery"

def parse_ai_response(text):
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
        prompts.append(prompts[-1] if prompts else "Mysterious bright cinematic scene")
        
    return prompts[:10], "\n".join(caption_lines)

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ (AYDINLIK TARZ)
# -----------------------------
def generate_album_images(prompt_list):
    global HORDE_KEY
    print(f"🎨 {len(prompt_list)} Farklı Sahne Çiziliyor (Aydınlık Tarz)...", flush=True)
    generated_files = []
    
    for i, specific_prompt in enumerate(prompt_list):
        print(f"   🎬 Sahne {i+1}/10: {specific_prompt[:40]}...", flush=True)
        
        # --- İŞTE BURASI DEĞİŞTİ (Daha aydınlık ve epik) ---
        final_prompt = (
            f"{specific_prompt}, "
            "cinematic fantasy style, golden hour lighting, majestic, "
            "vibrant colors, epic scale, highly detailed, vertical aspect ratio 4:5"
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
            req = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v18.0"}, timeout=30)
            
            if req.status_code == 401:
                HORDE_KEY = "0000000000"
                payload["params"]["post_processing"] = []
                req = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers={"apikey": HORDE_KEY}, timeout=30)

            if req.status_code != 202: continue
            task_id = req.json()['id']
            
            for _ in range(60): 
                time.sleep(15)
                try:
                    chk = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
                    
                    if 'queue_position' in chk:
                        qp = chk['queue_position']
                        if qp > 0: print(f"      ⏳ Sıra: {qp}...", flush=True)

                    if chk['done'] and len(chk['generations']) > 0:
                        img_data = requests.get(chk['generations'][0]['img'], timeout=60).content
                        fname = f"slide_{i+1}.jpg"
                        with open(fname, "wb") as f: f.write(img_data)
                        generated_files.append(fname)
                        print(f"      ✅ İndirildi.", flush=True)
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
    print("🚀 GİZEMLİ TARİH BOTU (V18 - AYDINLIK SÜRÜM)...", flush=True)
    prompts, caption = get_documentary_content()
    print(f"\n📝 MAKALE ÖNİZLEMESİ:\n{caption[:300]}...\n")
    
    images = generate_album_images(prompts)
    if len(images) >= 2: upload_album(images, caption)
    else: print("⚠️ Yeterli resim yok.")
