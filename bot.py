import os
import json
import time
import requests
import random
import google.generativeai as genai

# --- ŞİFRELER (GitHub Secrets'tan Çekilir) ---
GEMINI_KEY = os.environ['GEMINI_KEY']

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 🧱 ÇEKİRDEK İÇERİK KATEGORİLERİ (Gemini'nin evirip çevireceği ana malzemeler) ---
CONTENT_CATEGORIES = [
    "Tarihin çözülememiş en büyük sırları ve gizemleri",
    "İnsan zihnini zorlayan bilim ve uzay gizemleri",
    "Korku filmlerinden fırlamış, gerçek hayattan şehir efsaneleri",
    "Mitolojideki unutulmuş tanrılar ve canavarlar",
    "Arkeologların şok olduğu yasaklı bölgeler ve kalıntılar",
    "Gelecekten gelmiş gibi görünen eski icatlar",
    "Dünyanın en tehlikeli, merak uyandıran 5 yasağı veya bilgisi"
]

def get_instagram_idea():
    # Koda yazdığımız konseptleri alıp evirip çevirip kendisi düşünecek
    broad_category = random.choice(CONTENT_CATEGORIES)
    print(f"🎨 Ana Kategori Seçildi: {broad_category}")

    print("🧠 Gemini konsepti evirip çevirip ŞOK edici fikir üretiyor...")

    # Gemini'ye Mutasyon ve DETAYLI HİKAYE Emri Veriyoruz
    prompt_emir = f"""
    Sen bir Instagram Gizem ve Tarih sayfasının ana içerik üreticisisin. Gönderilerin viral oluyor.
    GÖREVİN: '{broad_category}' ana temasını alıp, takipçilerin kaydırmak zorunda kalacağı, uzun ve şok edici bir içerik taslağı oluşturmak.
    
    Çıktı Formatı SADECE şu JSON yapısında olmalıdır:
    {{
      "caption_title": "İnsanları durduracak, akılda kalıcı bir Başlık (Türkçe)",
      "full_caption": "Konuyu sürükleyici, gizemli ve şok edici bir tonda anlatan, 3-4 paragraftan oluşan TÜRKÇE metin yaz. Metnin sonunda 'Sizce bu gerçek mi? Yorumlarda tartışalım! 🤔' gibi etkileşim çağrısı yap.",
      "image_prompt": "Bu konuya uygun, SİNEMATİK, FOTOĞRAF GERÇEKLİĞİNDE, YÜKSEK KALİTELİ ve KARE (Square) formatta (1:1 aspect ratio) bir resim için İNGİLİZCE prompt.",
      "tags": "Konuyla DOĞRUDAN alakalı, popüler 15-20 adet Türkçe ve İngilizce hashtag yaz (#Tarih #Gizem #Unutulmuş #Korku gibi)."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(text)
        print(f"✅ Yeni Başlık Hazır: {data['caption_title']}")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası: {e}")
        # Yedek içerik
        return {
            "caption_title": "12.000 Yıllık Keşif: Buzun Altındaki Yasaklı Yapı",
            "full_caption": "Antarktika'da buzulların erimesiyle ortaya çıkan devasa bir yapı, bilim dünyasını ikiye böldü. Yapı, bilinen hiçbir medeniyete ait değil ve içinde hala enerji yayan cihazlar bulunuyor. Bu, insanlığın bilinen tarihini tamamen değiştirebilir. Sizce bu yapı kimlere ait? Yorumlarda tartışalım! 🤔",
            "image_prompt": "A massive, black, geometric structure partially exposed under melting Antarctic ice, dramatic lighting, cinematic, square, 8k",
            "tags": "#Antarktika #Gizem #Tarih #Arkeoloji #Bilinmeyen"
        }

# --- SINIRSIZ RESSAM (POLLINATIONS FLUX) ---
def generate_image(prompt):
    print("🎨 Resim Çiziliyor (Flux)...")
    # Instagram için SQUARE (Kare) formatı belirliyoruz
    prompt_encoded = requests.utils.quote(f"{prompt}, square, 8k, cinematic, photorealistic")
    seed = random.randint(1, 1000000)
    # Pollinations.ai Flux servisi kullanılıyor (1:1 format)
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1000&height=1000&model=flux&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=120)
        if response.status_code == 200:
            with open("insta_post.jpg", 'wb') as f:
                f.write(response.content)
            print("✅ Resim başarıyla indirildi: insta_post.jpg")
            return True
        return False
    except:
        return False

def main_job():
    # 1. İçeriği ve Görsel Prompt'u al
    content = get_instagram_idea()
    
    # 2. Resmi Oluştur
    if generate_image(content['image_prompt']):
        print("\n=======================================================")
        print("🎉 INSTAGRAM GÖNDERİ MALZEMENİZ HAZIR!")
        print("=======================================================")
        print(f"RESİM ADI: insta_post.jpg (Bu dosyayı indirip Instagram'a yükleyin)")
        print("\n⭐ GÖNDERİ BAŞLIĞI:")
        print(content['caption_title'])
        print("\n📝 AÇIKLAMA METNİ:")
        print(content['full_caption'])
        print("\n#️⃣ HASHTAG'LER:")
        print(content['tags'])
        print("=======================================================\n")
    else:
        print("❌ HATA: Resim çizilemedi. Tekrar çalıştırmayı deneyin.")

if __name__ == "__main__":
    main_job()