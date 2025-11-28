import os
import json
import time
import datetime
# Pillow (PIL) kütüphanesini kaldırdık çünkü artık resim üzerine yazı yazmayacağız.
# Temiz resimler ve uzun açıklama olacak.
import google.generativeai as genai
from huggingface_hub import InferenceClient
from instagrapi import Client as InstaClient

# --- ŞİFRELER ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

# --- YEDEK DEPOLU TOKEN SİSTEMİ ---
TOKEN_LISTESI = [
    os.environ.get('HF_TOKEN'),
    os.environ.get('HF_TOKEN_1'),
    os.environ.get('HF_TOKEN_2'),
    os.environ.get('HF_TOKEN_3')
]
TOKEN_LISTESI = [t for t in TOKEN_LISTESI if t is not None]

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Daha uzun ve detaylı metinler için pro modeli şart
model = genai.GenerativeModel('gemini-pro')
repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

def get_time_context():
    # TR Saati (UTC+3)
    try:
        tr_saat = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).hour
        if 6 <= tr_saat < 12: return "Günaydın tarih meraklıları."
        elif 12 <= tr_saat < 18: return "Günün ortasından bir tarih yolculuğu."
        elif 18 <= tr_saat < 22: return "İyi akşamlar."
        else: return "Gecenin sessizliğinde bir gizem."
    except:
        return "Merhaba."

def get_smart_content():
    print("🧠 Gemini (Belgesel Modu) düşünüyor...")
    zaman_selami = get_time_context()
    
    # --- YENİ PROMPT: UZUN VE DETAYLI ANLATIM ---
    prompt_emir = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yazarısın.
    Konsept: Antik Uygarlıklar, Mitoloji, Çözülememiş Gizemler, Uzay Tarihi.
    Zaman Selamı: {zaman_selami}
    
    Görevin:
    1. Bu konulardan derinlemesine anlatılacak, insanların okuyunca bilgileneceği bir olay seç (Örn: Atlantis, Göbeklitepe, İskenderiye Kütüphanesi).
    2. Bana SADECE aşağıdaki JSON formatında bir çıktı ver. Başka hiçbir şey yazma.
    
    {{
      "caption": "Buraya seçtiğin konuyu detaylıca anlatan UZUN bir Türkçe metin yaz. Paragraflara böl. Tıpkı bir belgesel anlatımı gibi bilgi verici olsun, soru sorma. {zaman_selami} ile başla. En sona ilgili etiketleri ekle.",
      "image_prompt_1": "Hikayenin ilk kısmını görselleştirecek İNGİLİZCE, 8k, cinematic, vertical prompt.",
      "image_prompt_2": "Hikayenin ikinci kısmını veya farklı bir açısını görselleştirecek İNGİLİZCE, 8k, cinematic, vertical prompt."
    }}
    """
    
    try:
        response = model.generate_content(prompt_emir)
        # Markdown temizliği
        text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        print(f"✅ Konu Bulundu. Caption uzunluğu: {len(data['caption'])} karakter.")
        return data
    except Exception as e:
        print(f"⚠️ Gemini Hatası ({e}), yedek konu devreye giriyor.")
        # Yedek konu da artık uzun formatta
        return {
            "caption": f"{zaman_selami}\n\nPlaton’un anlattığına göre Atlantis, yaklaşık 11.500 yıl önce Atlas Okyanusu’nda, Cebelitarık Boğazı’nın batısında bulunan çok gelişmiş bir ada uygarlığıydı.\n\nPoseidon’un kurduğu bu ülke 10 krallıktan oluşuyordu. Devasa daire şeklinde şehirler, geniş kanallar, altın ve gümüşle kaplı tapınaklar, güçlü filo ve ileri teknolojiye sahiplerdi.\n\nZamanla Atlantisliler kibirli ve saldırgan oldu. Bunun üzerine tanrılar öfkelendi. Sadece bir gün ve bir gece içinde korkunç depremler ve dev dalgalar adayı tamamen yuttu. Atlantis denizin dibine gömüldü.\n\n#Atlantis #KayıpUygarlık #Tarih #Mitoloji #Gizem",
            "image_prompt_1": "Ancient glorious city of Atlantis, golden temples, advanced architecture, sunny day, wide angle, 8k, cinematic",
            "image_prompt_2": "Atlantis city sinking into the ocean during a massive storm, giant waves, destruction, dark atmosphere, 8k, cinematic"
        }

# --- RESİM ÇİZME FONKSİYONU (Dosya ismi parametreli) ---
def try_generate_image(prompt, filename):
    for i, token in enumerate(TOKEN_LISTESI):
        print(f"🔄 '{filename}' için {i+1}. Anahtar deneniyor...")
        try:
            client = InferenceClient(model=repo_id, token=token)
            # Dikey format (Vertical)
            image = client.text_to_image(
                f"{prompt}, vertical, aspect ratio 2:3, 8k, photorealistic, masterpiece, --no text", 
                width=768, height=1344
            )
            image.save(filename)
            print(f"✅ BAŞARILI! {filename} oluşturuldu.")
            return True
        except Exception as e:
            print(f"❌ {i+1}. Anahtar Hatası: {e}")
            time.sleep(1)
            
    print(f"🚨 HATA: '{filename}' hiçbir anahtarla çizilemedi.")
    return False

def main_job():
    # 1. İçeriği Al (Uzun metin ve 2 resim promptu)
    content = get_smart_content()
    
    paths_to_upload = []

    # 2. Birinci Resmi Çiz
    print("--- 1. Resim Hazırlanıyor ---")
    if try_generate_image(content['image_prompt_1'], "image1.jpg"):
        paths_to_upload.append("image1.jpg")
    else:
        print("İlk resim çizilemediği için işlem iptal.")
        return

    # 3. İkinci Resmi Çiz
    print("--- 2. Resim Hazırlanıyor ---")
    if try_generate_image(content['image_prompt_2'], "image2.jpg"):
        paths_to_upload.append("image2.jpg")
    else:
         print("İkinci resim çizilemedi, sadece ilk resimle devam edilecek.")
         # İkinci çizilemezse iptal etmiyoruz, tek resimle devam ediyoruz.

    # 4. Instagram'a Kaydırmalı (Albüm) Yükle
    try:
        print(f"📸 Instagram'a {len(paths_to_upload)} adet resim yükleniyor...")
        cl = InstaClient()
        
        if INSTA_SESSION:
            try:
                cl.set_settings(json.loads(INSTA_SESSION))
                cl.login(INSTA_USER, INSTA_PASS)
            except:
                 print("Session geçersiz, normal giriş deneniyor...")
                 cl.login(INSTA_USER, INSTA_PASS)
        else:
            cl.login(INSTA_USER, INSTA_PASS)
            
        # --- ÖNEMLİ DEĞİŞİKLİK: photo_upload yerine album_upload ---
        if len(paths_to_upload) > 1:
            # Birden fazla resim varsa ALBÜM yap
            cl.album_upload(
                paths=paths_to_upload,
                caption=content['caption'] # Uzun açıklama
            )
        elif len(paths_to_upload) == 1:
            # Tek resim varsa normal at
             cl.photo_upload(
                path=paths_to_upload[0],
                caption=content['caption']
            )

        print("🚀 INSTAGRAM BAŞARILI! Kaydırmalı post atıldı.")
        
    except Exception as e:
        print(f"❌ Instagram Yükleme Hatası: {e}")

if __name__ == "__main__":
    main_job()
