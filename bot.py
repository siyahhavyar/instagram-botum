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

# Key kontrolü (Başlangıç)
if not HORDE_KEY or len(HORDE_KEY) < 5:
    print("⚠️ UYARI: Horde Key yok veya kısa. Anonim mod başlatılıyor.", flush=True)
    HORDE_KEY = "0000000000"

# -----------------------------
# 1. BELGESEL YAZARI (FİKİR ÜRETİCİ)
# -----------------------------
def get_documentary_content():
    """
    Gizemli, Tarihi, Mitolojik bir konu seçer ve Instagram için uzun,
    belgesel tadında bir açıklama metni hazırlar.
    """
    instructions = """
    Act as a professional Documentary Narrator (National Geographic / History Channel style).
    
    STEP 1: Choose a mysterious topic. 
    (Ideas: Lost Civilizations, Dark Mythology, Cursed Artifacts, Deep Sea Mysteries, Abandoned Places, Occult History).
    
    STEP 2: Create a visual description for AI images. 
    (Keywords: Cinematic, Atmospheric, Dark, Hyper-realistic, 8k).
    
    STEP 3: Write an Instagram Caption in ENGLISH. Structure:
    - 🛑 TITLE: Catchy & Scary Title (Uppercase)
    - 📖 THE STORY: Explain the history/legend in 2-3 engaging paragraphs.
    - 🔍 THE MYSTERY: What makes it unexplainable or creepy?
    - 🧠 DID YOU KNOW?: A surprising fact.
    - #️⃣ HASHTAGS: 15 relevant hashtags.
    
    OUTPUT FORMAT (Strictly):
    PROMPT: <Visual description>
    CAPTION: <The full text>
    """

    # --- PLAN A: GEMINI (1.5 Flash - En İyisi) ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini (Belgeselci) yazıyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.1)
            model = genai.GenerativeModel("gemini-1.5-flash", generation_config=config)
            
            response = model.generate_content(instructions)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception as e:
            print(f"⚠️ Gemini Pas: {e}", flush=True)

    # --- PLAN B: GROQ (Llama 3.3 - En Hızlısı) ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq yazıyor...", flush=True)
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

    # --- PLAN C: POLLINATIONS (Yedek) ---
    return "Ancient ruins in fog", "Mystery of the Ancients... 🌑 #History #Mystery"

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ (AKILLI MOD)
# -----------------------------
def generate_album_images(base_prompt, count=10):
    global HORDE_KEY
    print(f"🎨 {count} karelik Albüm çizimi başlıyor...", flush=True)
    
    generated_files = []
    
    # Base prompt'u Horde için süslüyoruz
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
            "height": 1024, # 4:5 Oranına yakın (Instagram Feed için en iyisi)
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
                headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v8.0"},
                timeout=30
            )
            
            # --- HATA YAKALAMA VE KURTARMA ---
            if req.status_code == 401: # 401 = KEY GEÇERSİZ
                print("⚠️ HATA: Horde Key geçersiz! Anonim moda geçiliyor...", flush=True)
                HORDE_KEY = "0000000000" # Key'i sıfırla
                payload["params"]["post_processing"] = [] # HD'yi kapat
                
                # Tekrar dene (Anonim olarak)
                req = requests.post(
                    "https://stablehorde.net/api/v2/generate/async",
                    json=payload,
                    headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v8.0-Anon"},
                    timeout=30
                )
            
            if req.status_code != 202:
                print(f"      ⚠️ Sunucu hatası ({req.status_code}), bu kare atlanıyor.", flush=True)
                continue
                
            task_id = req.json()['id']
            
            # Bekleme Döngüsü (Max 20dk)
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
# 3. INSTAGRAM PAYLAŞIMI (GÜVENLİ)
# -----------------------------
def upload_album(paths, caption):
    if not paths: return False
    
    try:
        print("📸 Instagram oturumu açılıyor...", flush=True)
        cl = Client()
        
        session_loaded = False
        
        # 1. Önce Session (Varsa)
        if INSTA_SESSION:
            try:
                print("🍪 Kayıtlı Session yükleniyor...", flush=True)
                settings = json.loads(INSTA_SESSION)
                cl.load_settings(settings)
                cl.login(INSTA_USER, INSTA_PASS)
                print("✅ Session ile giriş başarılı!", flush=True)
                session_loaded = True
            except Exception as e:
                print(f"⚠️ Session yüklenemedi: {e}. Normal giriş deneniyor...", flush=True)
        
        # 2. Yoksa Şifre
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
    print("🚀 GİZEMLİ TARİH BOTU BAŞLATILIYOR (V8 - Ultimate)...", flush=True)
    
    # 1. Konuyu Bul ve Yazıyı Yaz
    prompt, full_caption = get_documentary_content()
    
    print("\n------------------------------------------------")
    print(f"💀 KONU: {prompt[:100]}...")
    print("------------------------------------------------\n")
    print("📝 MAKALE ÖNİZLEMESİ:")
    print(full_caption[:200] + "...\n")

    # 2. 10 Resimlik Albümü Çiz
    # NOT: 10 resim uzun sürer. Test için bu sayıyı 3 yapabilirsin.
    images = generate_album_images(prompt, count=10)
    
    # 3. Paylaş
    if len(images) >= 2:
        upload_album(images, full_caption)
    else:
        print("⚠️ Yeterli resim üretilemedi (En az 2 lazım), iptal.", flush=True)
