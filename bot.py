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
HORDE_KEY     = os.getenv("HORDE_API_KEY")
GROQ_KEY      = os.getenv("GROQ_API_KEY")

if not HORDE_KEY or HORDE_KEY.strip() == "":
    print("UYARI: Horde Key yok, kalite düşebilir.", flush=True)
    HORDE_KEY = "0000000000"

# -----------------------------
# 1. FİKİR VE MAKALENİN YAZILMASI
# -----------------------------
def get_documentary_content():
    """
    Gizemli bir konu bulur ve bununla ilgili hem 10 resimlik görsel prompt
    hem de detaylı, blog tarzı bir Instagram açıklaması yazar.
    """
    
    # Yapay Zekaya Giden Emir (Prompt)
    instructions = """
    Act as a professional Documentary Narrator and Historian (like National Geographic or History Channel).
    
    STEP 1: Choose a mysterious, historical, or mythological topic.
    Examples:
    - The Lost City of Atlantis (Underwater ruins)
    - The Curse of Tutankhamun (Ancient Egypt)
    - The Antikythera Mechanism (Out of place artifacts)
    - The Legend of the Wendigo (Dark folklore)
    - Ghost Ships of the Pacific (Thalassophobia)
    - Secret rituals of the Druids (Ancient history)
    
    STEP 2: Create a visual description for an AI image generator.
    The images must be atmospheric, cinematic, photorealistic, and highly detailed.
    
    STEP 3: Write a LONG, EDUCATIONAL, and ENGAGING Instagram Caption.
    Structure of the Caption:
    - 🛑 TITLE: A catchy, scary, or mysterious title (Uppercase).
    - 📖 THE STORY: Explain the history, legend, or event in detail. (2-3 Paragraphs).
    - 🔍 THE MYSTERY: What makes it unexplainable or strange?
    - 🧠 DID YOU KNOW?: A fun/creepy fact about it.
    - #️⃣ HASHTAGS: 15 relevant hashtags.
    
    OUTPUT FORMAT (Return exactly this structure):
    PROMPT: <Visual description>
    CAPTION: <The long documentary text>
    """

    # --- PLAN A: GEMINI (2.0 Flash) ---
    if GEMINI_KEY:
        try:
            print("🧠 Plan A: Gemini (Belgeselci) yazıyor...", flush=True)
            genai.configure(api_key=GEMINI_KEY)
            config = genai.types.GenerationConfig(temperature=1.1)
            model = genai.GenerativeModel("gemini-2.0-flash", generation_config=config)
            
            response = model.generate_content(instructions)
            parts = response.text.split("CAPTION:")
            if len(parts) >= 2:
                return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception as e:
            print(f"⚠️ Gemini Pas: {e}", flush=True)

    # --- PLAN B: GROQ (Tarihçi) ---
    if GROQ_KEY:
        try:
            print("🧠 Plan B: Groq yazıyor...", flush=True)
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.3-70b-versatile", # Llama 3 çok iyi yazar
                "messages": [{"role": "user", "content": instructions}]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                parts = content.split("CAPTION:")
                if len(parts) >= 2:
                    return parts[0].replace("PROMPT:", "").strip(), parts[1].strip()
        except Exception:
            pass

    # Yedek (Pollinations uzun yazı yazamaz, o yüzden basit kalır)
    return "Mysterious ancient ruins in fog", "Mystery of the Ancients... 🌑 #History #Mystery"

# -----------------------------
# 2. 10 RESİMLİK ALBÜM ÜRETİMİ
# -----------------------------
def generate_album_images(base_prompt, count=10):
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
        
        # Her kare için farklı seed (tohum) = Aynı konunun farklı açısı
        unique_seed = str(random.randint(1, 9999999999))
        
        payload = {
            "prompt": final_prompt,
            "params": {
                "sampler_name": "k_dpmpp_2m", 
                "cfg_scale": 6,               
                "width": 832,      # 4:5 Oranına yakın
                "height": 1024,          
                "steps": 30,                 
                "seed": unique_seed, 
                "post_processing": ["RealESRGAN_x4plus"] 
            },
            "nsfw": False,
            "censor_nsfw": True,
            "models": ["Juggernaut XL", "AlbedoBase XL (SDXL)"]
        }
        
        # Horde İsteği
        try:
            req = requests.post(
                "https://stablehorde.net/api/v2/generate/async",
                json=payload,
                headers={"apikey": HORDE_KEY, "Client-Agent": "MysteryBot:v3.0"},
                timeout=30
            )
            if req.status_code != 202:
                print("      ⚠️ Sunucu hatası, bu kare atlanıyor.", flush=True)
                continue
                
            task_id = req.json()['id']
            
            # Bekleme Döngüsü
            img_downloaded = False
            for _ in range(40): # Max 13-14 dk bekle
                time.sleep(20)
                try:
                    chk = requests.get(f"https://stablehorde.net/api/v2/generate/status/{task_id}", timeout=30).json()
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
        print("📸 Instagram'a bağlanılıyor...", flush=True)
        cl = Client()
        cl.login(INSTA_USER, INSTA_PASS)
        
        print(f"📤 {len(paths)} Parçalı Albüm Yükleniyor...", flush=True)
        print("📝 Açıklama Yazılıyor...")
        
        cl.album_upload(
            paths=paths,
            caption=caption
        )
        print("✅ GÖNDERİ BAŞARIYLA PAYLAŞILDI!", flush=True)
        return True
    except Exception as e:
        print(f"❌ Instagram Hatası: {e}", flush=True)
        if "challenge" in str(e).lower():
            print("⚠️ DOĞRULAMA GEREKİYOR: Lütfen Instagram uygulamasından girişi onaylayın.", flush=True)
        return False
    finally:
        for p in paths:
            if os.path.exists(p): os.remove(p)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("🚀 GİZEM VE TARİH BELGESELİ BAŞLIYOR...", flush=True)
    
    # 1. Konuyu ve Yazıyı Hazırla
    prompt, full_caption = get_documentary_content()
    
    print("\n------------------------------------------------")
    print(f"💀 KONU: {prompt[:100]}...")
    print("------------------------------------------------\n")
    
    # Yazıyı konsola bas (Kontrol için)
    print("📝 HAZIRLANAN MAKALE (Önizleme):")
    print(full_caption[:300] + "...\n[Devamı Instagram'da]\n")

    # 2. Albümü Çiz
    images = generate_album_images(prompt, count=10)
    
    # 3. Paylaş (En az 2 resim varsa albüm olur)
    if len(images) >= 2:
        upload_album(images, full_caption)
    else:
        print("⚠️ Yeterli resim üretilemedi, paylaşım iptal.", flush=True)
