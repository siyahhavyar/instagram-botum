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
# Eğer kopyalarken boşluk kaldıysa temizler
if HORDE_KEY:
    HORDE_KEY = HORDE_KEY.strip()

if not HORDE_KEY or len(HORDE_KEY) < 10:
    print(f"⚠️ UYARI: Horde Key yok/kısa. Anonim mod.", flush=True)
    HORDE_KEY = "0000000000"
else:
    print(f"BAŞARILI: Horde Key yüklendi! (Uzunluk: {len(HORDE_KEY)})", flush=True)

# -----------------------------
# 1. BELGESEL YAZARI (2025 MODEL ORDUSU)
# -----------------------------
def get_documentary_content():
    instructions = """
    Act as a professional Documentary Narrator (National Geographic style).
    STEP 1: Choose a mysterious topic (Lost Civilizations, Dark Mythology, Deep Sea, Cursed Artifacts).
    STEP 2: Create a visual description for AI images (Cinematic, Dark, Hyper-realistic, 8k).
    STEP 3: Write an Instagram Caption in ENGLISH:
    - 🛑 TITLE: Catchy Title (Uppercase)
    - 📖 THE STORY: 2-3 engaging paragraphs history/legend.
    - 🔍 THE MYSTERY: What makes it unexplainable?
    - 🧠 DID YOU KNOW?: A surprising fact.
    - #️⃣ HASHTAGS: 15 relevant hashtags.
    
    OUTPUT FORMAT:
    PROMPT: <Visual description>
    CAPTION: <The full text>
    """

    # --- PLAN A: GEMINI (YENİ 2025 LİSTESİ) ---
    if GEMINI_KEY:
        print("🧠 Plan A: Gemini (2025 Modelleri) deneniyor...", flush=True)
        genai.configure(api_key=GEMINI_KEY)
        
        # Senin verdiğin güncel liste (En güçlüden en hafife doğru)
        models_to_try = [
            "gemini-2.5-pro", 
            "gemini-2.5-flash", 
            "gemini-2.0-flash", 
            "gemini-2.0-flash-001",
            "gemini-2.0-flash-lite",
            "gemini-2.5-flash-lite",
            "gemini-1.5-pro",   # Eskiler yedek kalsın
            "gemini-1.5-flash"
        ]
        
        for model_name in models_to_try:
            try:
                print(f"   ↳ Deneniyor: {model_name}...", flush=True)
                # Sıcaklık ayarı
                config = genai.types.GenerationConfig(temperature=1.0)
                model = genai.GenerativeModel(model_name, generation_config=config)
                
                response = model.generate_content(instructions)
                
                if response.text:
                    parts = response.text.split("CAPTION:")
                    if len(parts) >= 2:
                        print(f"   ✅ BAŞARILI: {model_name} çalıştı!", flush=True)
                        return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
            except Exception as e:
                # Hata mesajını analiz et
                err = str(e)
                if "404" in err:
                    print(f"      ❌ {model_name} Bulunamadı (404).", flush=True)
                elif "429" in err:
                    print(f"      ❌ {model_name} Kota Dolu (429).", flush=True)
                else:
                    print(f"      ❌ {model_name} Hatası: {err[:50]}...", flush=True)
                continue # Sıradaki modele geç

    # --- PLAN B: GROQ ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq yazıyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": instructions}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=20)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    # --- PLAN C: POLLINATIONS (Yedek Metin Zekası) ---
    try:
        print("🧠 Plan C: Pollinations (Metin) deneniyor...", flush=True)
        seed = random.randint(1, 999999)
        simple_instr = "Write a mystery history story. Format: PROMPT: (visuals) CAPTION: (story)."
        encoded = urllib.parse.quote(simple_instr)
        url = f"https://text.pollinations.ai/{encoded}?seed={seed}&model=openai" 
        response = requests.get(url, timeout=30)
        parts = response.text.split("CAPTION:")
        if len(parts) >= 2:
            print("✅ Pollinations Metin Başarılı!", flush=True)
            return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
    except:
        pass

    return "Ancient ruins in fog", "Mystery of the Ancients... 🌑 #History #Mystery"

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ
# -----------------------------
def generate_album_images(base_prompt, count=10):
    global HORDE_KEY
    print(f"🎨 {count} karelik Albüm çizimi başlıyor...", flush=True)
    
    generated_files = []
    
    final_prompt = (
        f"{base_prompt}, "
        "photorealistic, 8k, cinematic lighting, national geographic style, "
        "mysterious atmosphere, highly detailed, dramatic shadows, "
        "vertical aspect ratio"
    )
    
    for i in range(count):
        print(f"   ↳ Kare {i+1}/{count} işleniyor...", flush=True)
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
                headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v11.0"},
                timeout=30
            )
            
            # --- KEY HATASI OLURSA ANONİM MODA GEÇ ---
            if req.status_code == 401:
                print("⚠️ HATA: Horde Key reddedildi! Anonim moda geçiliyor.", flush=True)
                HORDE_KEY = "0000000000"
                payload["params"]["post_processing"] = []
                req = requests.post(
                    "https://stablehorde.net/api/v2/generate/async",
                    json=payload,
                    headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v11.0-Anon"},
                    timeout=30
                )

            if req.status_code != 202:
                print(f"      ⚠️ Sunucu hatası ({req.status_code}), atlanıyor.", flush=True)
                continue
                
            task_id = req.json()['id']
            
            img_downloaded = False
            for _ in range(60): 
                time.sleep(20)
                try:
                    chk = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
                    
                    if 'queue_position' in chk:
                        print(f"      ⏳ Sıra: {chk['queue_position']}...", flush=True)

                    if chk['done'] and len(chk['generations']) > 0:
                        img_url = chk['generations'][0]['img']
                        img_data = requests.get(img_url, timeout=60).content
                        
                        fname = f"slide_{i+1}.jpg"
                        with open(fname, "wb") as f:
                            f.write(img_data)
                        
                        generated_files.append(fname)
                        print(f"      ✅ İndirildi: {fname}", flush=True)
                        img_downloaded = True
                        break
                except:
                    pass
            
            if not img_downloaded:
                print("      ⚠️ Zaman aşımı.", flush=True)
                
        except Exception as e:
            print(f"      ⚠️ Bağlantı hatası: {e}", flush=True)

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
                print("🍪 Kayıtlı Session yükleniyor...", flush=True)
                settings = json.loads(INSTA_SESSION)
                cl.load_settings(settings)
                cl.login(INSTA_USER, INSTA_PASS)
                print("✅ Session ile giriş başarılı!", flush=True)
                session_loaded = True
            except Exception as e:
                print(f"⚠️ Session hatası: {e}. Normal giriş deneniyor...", flush=True)
        
        if not session_loaded:
            print("🔑 Kullanıcı adı/Şifre ile giriş yapılıyor...", flush=True)
            cl.login(INSTA_USER, INSTA_PASS)
        
        print(f"📤 {len(paths)} Parçalı Albüm Yükleniyor...", flush=True)
        cl.album_upload(paths=paths, caption=caption)
        print("✅ GİZEMLİ ALBÜM PAYLAŞILDI!", flush=True)
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
    print("🚀 GİZEMLİ TARİH BOTU (V11 - 2025 Model)...", flush=True)
    
    prompt, full_caption = get_documentary_content()
    
    print("\n------------------------------------------------")
    print(f"💀 KONU: {prompt[:100]}...")
    print("------------------------------------------------\n")
    
    # 10 Resimlik Albümü Çiz
    images = generate_album_images(prompt, count=10)
    
    if len(images) >= 2:
        upload_album(images, full_caption)
    else:
        print("⚠️ Yeterli resim yok, iptal.", flush=True)
