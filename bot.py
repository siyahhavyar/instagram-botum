import os
import json
import time
import requests
import random
import google.generativeai as genai
from instagrapi import Client

# --- ŞİFRELERİ KASADAN ÇEKİYORUZ ---
GEMINI_KEY = os.environ['GEMINI_KEY']
INSTA_USER = os.environ['INSTA_USER']
INSTA_PASS = os.environ['INSTA_PASS']
# Session opsiyoneldir, varsa kullanır yoksa şifreyle girer
INSTA_SESSION = os.environ.get('INSTA_SESSION')

# --- AYARLAR ---
genai.configure(api_key=GEMINI_KEY)
# Daha karmaşık görev için 'gemini-pro' modeli uygundur
model = genai.GenerativeModel('gemini-pro')

# --- KONU HAVUZU ---
KONULAR = [
    "Tarihin Çözülememiş Gizemleri",
    "Korkunç Mitolojik Yaratıklar",
    "Uzay ve Evrenin Sırları",
    "Antik Uygarlıkların Teknolojileri",
    "Lanetli Yerler ve Olaylar",
    "Paranormal Fenomenler",
    "Arkeolojik Keşifler"
]

def icerik_uret():
    print("🧠 Gemini (Belgesel Editörü) 10 sayfalık dev konuyu araştırıyor...")
    secilen_konu = random.choice(KONULAR)
    
    # --- GÜNCELLENEN KISIM BURASI (10 Görsel İsteği) ---
    prompt = f"""
    Sen profesyonel bir tarih ve gizem belgeseli yapımcısısın.
    Konu: {secilen_konu}.
    
    Görevin:
    1. Bu konuda çok detaylı, insanı şok edecek bir olay seç.
    2. Instagram için 10 GÖRSELLİ, hikaye anlatan bir kaydırmalı (Carousel) post hazırla.
    3. Bana SADECE aşağıdaki JSON formatında cevap ver:
    
    {{
      "baslik": "İlgi çekici bir başlık (Türkçe)",
      "aciklama": "Konuyu çok detaylı anlatan, 6-7 paragraflık ansiklopedik bir yazı (Türkçe). En sona etiketleri ekle.",
      "gorsel_komutlari": [
        "1. görsel (Kapak) için İngilizce prompt (Çok etkileyici, 8k, cinematic, vertical)",
        "2. görsel (Giriş) için İngilizce prompt (Olayın başlangıcı, vertical)",
        "3. görsel (Detay 1) için İngilizce prompt (vertical)",
        "4. görsel (Detay 2) için İngilizce prompt (vertical)",
        "5. görsel (Atmosfer) için İngilizce prompt (vertical)",
        "6. görsel (Karakter/Mekan) için İngilizce prompt (vertical)",
        "7. görsel (Gizem unsuru) için İngilizce prompt (vertical)",
        "
