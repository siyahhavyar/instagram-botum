import os
import time
import requests
import random
import urllib.parse
import google.generativeai as genai
from datetime import datetime
from instagrapi import Client

# -----------------------------
# ENV KEYS
# -----------------------------
INSTA_USER    = os.getenv("INSTA_USER")
INSTA_PASS    = os.getenv("INSTA_PASS")
GEMINI_KEY    = os.getenv("GEMINI_KEY")
# Kod senin belirlediğin ismi kullanıyor:
HORDE_KEY     = os.getenv("HORDE_API_KEY") 
GROQ_KEY      = os.getenv("GROQ_API_KEY")

# Key kontrolü (Sadece bilgi amaçlı)
if not HORDE_KEY or len(HORDE_KEY) < 5:
    print("⚠️ UYARI: Horde Key yok veya çok kısa. Anonim mod aktif.", flush=True)
    HORDE_KEY = "0000000000"

# -----------------------------
# 1. FİKİR VE MAKALENİN YAZILMASI
# -----------------------------
def get_documentary_content():
    instructions = """
    Act as a professional Documentary Narrator (National Geographic style).
    STEP 1: Choose a mysterious topic (Lost Civilizations, Mythology, Deep Sea, Cursed Artifacts, Paranormal).
    STEP 2: Create a visual description for AI images (Atmospheric, Cinematic, Dark).
    STEP 3: Write an Instagram Caption:
    - 🛑 TITLE: Catchy Title (Uppercase)
    - 📖 THE STORY: 2-3 Paragraphs history/legend detailed.
    - 🔍 THE MYSTERY: What is unexplainable?
    - 🧠 DID YOU KNOW?: A fun/creepy fact.
    - #️⃣ HASHTAGS: 15 relevant tags.
    OUTPUT FORMAT:
    PROMPT: <Visual description>
    CAPTION: <The text>
    """

    # --- PLAN A: GEMINI ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini deneniyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.1)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config=config)
            response = model.generate_content(instructions)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception as e:
            print(f"⚠️ Gemini Pas: {e}", flush=True)

    # --- PLAN B: GROQ ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq deneniyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": instructions}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                parts = response.json()['choices'][0]['message']['content'].split("CAPTION:")
                if len(parts) >= 2:
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    return "Ancient mysterious ruins", "Mystery... #History"

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ (AKILLI HATA YÖNETİMİ)
# -----------------------------
def generate_album_images(base_prompt, count=10):
    global HORDE_KEY # Global değişkeni güncellemek için
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
        
        # Varsayılan ayarlar (HD Açık)
        params = {
            "sampler_name": "k_dpmpp_2m", 
            "cfg_scale": 6,               
            "width": 832,      
            "height": 1024,      
            "steps": 30,          
            "seed": unique_seed, 
            "post_processing": ["RealESRGAN_x4plus"] # Key varsa HD yap
        }

        # Eğer Key Anonim ise HD'yi baştan kapat
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
            # İSTEK GÖNDER
            req = requests.post(
                "https://stablehorde.net/api/v2/generate/async",
                json=payload,
                headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v6.0"},
                timeout=30
            )
            
            # --- HATA YAKALAMA VE KURTARMA (BURASI ÖNEMLİ) ---
            if req.status_code == 401: # 401 = KEY GEÇERSİZ / BOZUK
                print("⚠️ HATA: Horde Key geçersiz çıktı! Otomatik olarak Anonim moda geçiliyor...", flush=True)
                HORDE_KEY = "0000000000" # Key'i sıfırla
                payload["params"]["post_processing"] = [] # HD'yi kapat (Anonimler yapamaz)
                
                # Tekrar dene (Anonim olarak)
                req = requests.post(
                    "https://stablehorde.net/api/v2/generate/async",
                    json=payload,
                    headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v6.0-Anon"},
                    timeout=30
                )
            
            if req.status_code != 202:
                print(f"      ⚠️ Sunucu hatası ({req.status_code}), bu kare atlanıyor.", flush=True)
                try: print(f"      Hata detayı: {req.text}", flush=True)
                except: pass
                continue
                
            task_id = req.json()['id']
            
            # Bekleme Döngüsü
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
                print("      ⚠️ Zaman aşımı, bu kare atlandı.", flush=True)
                
        except Exception as e:
            print(f"      ⚠️ Bağlantı hatası: {e}", flush=True)

    return generated_files

# -----------------------------
# 3. INSTAGRAM PAYLAŞIMI
# -----------------------------
def upload_album(paths, caption):
    if not paths: return False
    
    try:
        print("📸 Instagram'a giriş yapılıyor...", flush=True)
        cl = Client()
        cl.login(INSTA_USER, INSTA_PASS)
        
        print(f"📤 {len(paths)} Parçalı Albüm Yükleniyor...", flush=True)
        cl.album_upload(paths=paths, caption=caption)
        print("✅ GİZEMLİ ALBÜM PAYLAŞILDI!", flush=True)
        return True
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}", flush=True)
        if "challenge" in str(e).lower():
            print("⚠️ DOĞRULAMA GEREKİYOR: Instagram uygulamasından girişi onaylayın.", flush=True)
        return False
    finally:
        for p in paths:
            if os.path.exists(p): os.remove(p)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 GİZEMLİ BOT BAŞLATILIYOR (V6 - Auto-Fix Mode)...", flush=True)
    
    prompt, full_caption = get_documentary_content()
    
    print("\n------------------------------------------------")
    print(f"💀 KONU: {prompt[:100]}...")
    print("------------------------------------------------\n")
    
    images = generate_album_images(prompt, count=10)
    
    if len(images) >= 2:
        upload_album(images, full_caption)
    else:
        print("⚠️ Yeterli resim üretilemedi, paylaşım iptal.", flush=True)
        
