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

# Key Temizliği
if HORDE_KEY: HORDE_KEY = HORDE_KEY.strip()
if GEMINI_KEY: GEMINI_KEY = GEMINI_KEY.strip()

if not HORDE_KEY or len(HORDE_KEY) < 10:
    print(f"⚠️ UYARI: Horde Key yok/kısa. Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key yüklendi! (Uzunluk: {len(HORDE_KEY)})", flush=True)

# -----------------------------
# 1. BELGESEL YAZARI VE SENARİST (10 FARKLI SAHNE)
# -----------------------------
def get_documentary_content():
    """
    Hem Instagram açıklamasını yazar hem de 10 farklı resim promptu üretir.
    """
    
    # Konu çeşitliliği için rastgele kategori
    categories = [
        "Lost Civilizations & Jungle Ruins",
        "Deep Sea Horror & Shipwrecks",
        "Cursed Archeological Artifacts",
        "Victorian Era Murder Mystery",
        "Alien Artifacts found on Earth",
        "Haunted Gothic Castles",
        "Ancient Viking/Norse Mythology",
        "Japanese Folklore & Yokai",
        "Cyberpunk Dystopian Future Ruins",
        "Post-Apocalyptic Overgrown Cities"
    ]
    chosen_category = random.choice(categories)
    print(f"🎲 Seçilen Kategori: {chosen_category}", flush=True)

    instructions = f"""
    Act as a Documentary Director.
    TOPIC CATEGORY: {chosen_category}
    
    TASK 1: Create a cohesive visual story with 10 DISTINCT SCENES.
    - Scene 1 must be an establishing shot (Wide view).
    - Scene 2-9 must be details, characters, artifacts, or action shots (Close-ups, diverse angles).
    - Scene 10 must be a dramatic conclusion or cliffhanger.
    
    TASK 2: Write an Instagram Caption (English).
    - Title (Uppercase)
    - Story (3 paragraphs)
    - Mystery/Fact
    - Hashtags
    
    OUTPUT FORMAT (Strictly follow this):
    SCENE_1: <Visual prompt for scene 1>
    SCENE_2: <Visual prompt for scene 2>
    ...
    SCENE_10: <Visual prompt for scene 10>
    CAPTION: <The full instagram caption text>
    """

    # --- PLAN A: GEMINI (MODERN LİSTE) ---
    if GEMINI_KEY:
        print("🧠 Plan A: Gemini (Senarist) düşünülüyor...", flush=True)
        genai.configure(api_key=GEMINI_KEY)
        
        # Leaked Key hatası almamak için yeni key şart.
        # Yine de en güncel modelleri deniyoruz.
        models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.5-flash-8b"]
        
        for m in models:
            try:
                print(f"   ↳ Model: {m}...", flush=True)
                model = genai.GenerativeModel(m)
                response = model.generate_content(instructions)
                
                text = response.text
                if "SCENE_1:" in text and "CAPTION:" in text:
                    print(f"   ✅ BAŞARILI: {m} senaryoyu yazdı!", flush=True)
                    return parse_gemini_response(text)
            except Exception as e:
                if "403" in str(e):
                    print("   🚨 KRİTİK HATA: API Key 'Leaked' (Sızdırılmış). Lütfen Google AI Studio'dan YENİ KEY al!", flush=True)
                    break # Key patlaksa diğer modelleri denemeye gerek yok.
                print(f"      ❌ {m} hatası: {e}")

    # --- PLAN B: GROQ ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq devreye giriyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": instructions}]}
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                text = response.json()['choices'][0]['message']['content']
                return parse_gemini_response(text)
        except Exception:
            pass

    # YEDEK (FALLBACK) - Eğer her şey bozulursa
    print("⚠️ HATA: Yapay zeka çalışmadı. Yedek senaryo kullanılıyor.", flush=True)
    fallback_prompts = [f"Mysterious {chosen_category}, cinematic shot {i}" for i in range(1, 11)]
    return fallback_prompts, f"Mystery of {chosen_category} #Mystery"

def parse_gemini_response(text):
    """Gemini'den gelen metni 10 ayrı prompt ve 1 caption olarak ayırır."""
    prompts = []
    caption = ""
    
    lines = text.split('\n')
    current_caption_lines = []
    is_caption = False
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.startswith("SCENE_"):
            # "SCENE_1: Dark forest" -> "Dark forest" kısmını al
            parts = line.split(":", 1)
            if len(parts) > 1:
                prompts.append(parts[1].strip())
        elif line.startswith("CAPTION:"):
            is_caption = True
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_caption_lines.append(parts[1].strip())
        elif is_caption:
            current_caption_lines.append(line)
            
    caption = "\n".join(current_caption_lines)
    
    # Eğer prompt sayısı 10'dan azsa tamamla
    while len(prompts) < 10:
        prompts.append(prompts[-1] if prompts else "Mysterious dark scene, cinematic")
        
    return prompts[:10], caption

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ (HER SAHNE FARKLI)
# -----------------------------
def generate_album_images(prompt_list):
    global HORDE_KEY
    print(f"🎨 {len(prompt_list)} Farklı Sahne Çiziliyor...", flush=True)
    
    generated_files = []
    
    for i, specific_prompt in enumerate(prompt_list):
        print(f"   🎬 Sahne {i+1}/10: {specific_prompt[:50]}...", flush=True)
        
        # Her sahne için özel prompt
        final_prompt = (
            f"{specific_prompt}, "
            "photorealistic, 8k, cinematic lighting, highly detailed, "
            "dramatic shadows, vertical aspect ratio 4:5"
        )
        
        # Tohum yine rastgele olsun
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
            req = requests.post(
                "https://stablehorde.net/api/v2/generate/async",
                json=payload,
                headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v12.0"},
                timeout=30
            )
            
            if req.status_code == 401:
                HORDE_KEY = "0000000000"
                payload["params"]["post_processing"] = []
                req = requests.post("https://stablehorde.net/api/v2/generate/async", json=payload, headers={"apikey": HORDE_KEY}, timeout=30)

            if req.status_code != 202:
                print(f"      ⚠️ Sunucu hatası, bu sahne atlandı.", flush=True)
                continue
                
            task_id = req.json()['id']
            
            # İndirme Döngüsü
            img_downloaded = False
            for _ in range(60): 
                time.sleep(15)
                try:
                    chk = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
                    
                    if chk['done'] and len(chk['generations']) > 0:
                        img_url = chk['generations'][0]['img']
                        img_data = requests.get(img_url, timeout=60).content
                        
                        fname = f"slide_{i+1}.jpg"
                        with open(fname, "wb") as f:
                            f.write(img_data)
                        
                        generated_files.append(fname)
                        print(f"      ✅ İndirildi.", flush=True)
                        img_downloaded = True
                        break
                except: pass
            
            if not img_downloaded:
                print("      ⚠️ Zaman aşımı.", flush=True)
                
        except Exception as e:
            print(f"      ⚠️ Hata: {e}", flush=True)

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
                settings = json.loads(INSTA_SESSION)
                cl.load_settings(settings)
                cl.login(INSTA_USER, INSTA_PASS)
                print("✅ Session ile giriş başarılı!", flush=True)
                session_loaded = True
            except: pass
        
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

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 GİZEMLİ TARİH BOTU (V12 - SENARYO MODU)...", flush=True)
    
    # 1. 10 Farklı Sahne Fikri Al
    prompt_list, full_caption = get_documentary_content()
    
    print("\n------------------------------------------------")
    print(f"📝 MAKALE BAŞLIĞI: {full_caption.splitlines()[0]}")
    print(f"🎬 SAHNE SAYISI: {len(prompt_list)}")
    print("------------------------------------------------\n")
    
    # 2. Resimleri Çiz
    images = generate_album_images(prompt_list)
    
    # 3. Paylaş
    if len(images) >= 2:
        upload_album(images, full_caption)
    else:
        print("⚠️ Yeterli resim yok, iptal.", flush=True)
            
