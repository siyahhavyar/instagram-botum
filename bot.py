import os
import random
import json
import time
from huggingface_hub import InferenceClient
from instagrapi import Client as InstaClient

# --- ŞİFRELER (KASADAN OTOMATİK ÇEKİLİR) ---
HF_TOKEN = os.environ['HF_TOKEN']
INSTA_SESSION = os.environ.get('INSTA_SESSION')
INSTA_USER = os.environ.get('INSTA_USER')
INSTA_PASS = os.environ.get('INSTA_PASS')

repo_id = "stabilityai/stable-diffusion-xl-base-1.0"

# --- 🏛️ DEVASA GİZEM VE TARİH HAVUZU 🐉 ---
content_pool = [
    # --- ANTİK VE KAYIP UYGARLIKLAR ---
    {
        "prompt": "Gobeklitepe ancient ruins at night, mysterious glowing carvings, starry sky, cinematic lighting, hyperrealistic, 8k",
        "caption": "🌍 Tarihin Sıfır Noktası: Göbeklitepe\n\n12.000 yıl önce, henüz yerleşik hayata bile geçilmemişken bu devasa tapınakları kim inşa etti? Teknoloji olmadan o taşlar nasıl taşındı?\n\nSizce burası bir tapınak mı yoksa uzaylılarla iletişim merkezi mi? 👇",
        "tags": "#Göbeklitepe #Tarih #Arkeoloji #Gizem #Şanlıurfa"
    },
    {
        "prompt": "The lost city of Atlantis underwater, ancient greek architecture, glowing blue lights, ruins, cinematic, epic scale, 8k",
        "caption": "🌊 Kayıp Kıta: Atlantis\n\nPlaton'un bahsettiği, bir gecede sulara gömülen efsanevi ileri uygarlık. Hala okyanusun derinliklerinde keşfedilmeyi bekliyor olabilir mi?\n\nGerçek mi yoksa sadece bir efsane mi? 🧜‍♂️",
        "tags": "#Atlantis #KayıpKıta #Efsane #Tarih #Undersea"
    },
    {
        "prompt": "Petra Jordan ancient treasury carved into red rock canyon, cinematic sunlight, dust particles, epic travel photography, 8k",
        "caption": "🏜️ Kayaların İçindeki Şehir: Petra\n\nÜrdün'ün çölünde, kayalara oyulmuş devasa bir şehir. Nebatiler bu muazzam mühendisliği nasıl başardı? Hazine binasının içinde ne saklanıyordu?\n\nOraya gitmek ister miydiniz? 👇",
        "tags": "#Petra #Ürdün #Tarih #Seyahat #Gizem"
    },
    {
        "prompt": "Easter Island Moai statues facing the ocean, sunset, mysterious atmosphere, ancient civilization, photorealistic, 8k",
        "caption": "🗿 Paskalya Adası Heykelleri (Moai)\n\nOkyanusun ortasındaki bu izole adada, tonlarca ağırlıktaki bu dev kafalar nasıl taşındı? Ve en önemlisi: Neden hepsi gökyüzüne değil de adanın içine bakıyor?\n\nBir koruma kalkanı mı? 👇",
        "tags": "#Moai #EasterIsland #Tarih #Gizem #Heykel"
    },
    {
        "prompt": "Machu Picchu ancient inca city on mountain top, clouds, mystical atmosphere, morning light, peru, 8k",
        "caption": "☁️ Bulutların Üzerindeki Şehir: Machu Picchu\n\nİnkaların İspanyollardan sakladığı gizli şehir. Bu kadar yüksek bir dağın tepesine bu taşlar nasıl çıkarıldı? Şehrin gerçek amacı neydi?\n\nManzara sizce de büyüleyici değil mi? 👇",
        "tags": "#MachuPicchu #İnka #Tarih #Peru #Dağ"
    },

    # --- MİTOLOJİ VE EFSANEVİ VARLIKLAR ---
    {
        "prompt": "Medusa gorgon with snake hair looking at camera, stone statues in background, dark greek temple, cinematic lighting, horror fantasy art, 8k",
        "caption": "🐍 Lanetli Güzellik: Medusa\n\nBir zamanlar güzelliğiyle tanrıları kıskandıran kadın, saçları yılana dönüşerek lanetlendi. Gözlerine bakan taşa dönüyor.\n\nSizce Medusa bir canavar mı yoksa bir kurban mı? 👇",
        "tags": "#Medusa #Mitoloji #YunanMitolojisi #Sanat #Efsane"
    },
    {
        "prompt": "Anubis egyptian god of death, wolf head, ancient egypt temple, glowing hieroglyphs, mysterious, cinematic, 8k",
        "caption": "⚖️ Ölümün Bekçisi: Anubis\n\nAntik Mısır'da ölüleri yargılayan, çakal başlı tanrı. Kalbinizi bir tüy ile tarttığını düşünün. Eğer kalbiniz tüyden ağırsa, ruhunuz yok olur.\n\nSizce kalbiniz hafif gelir miydi? 🪶",
        "tags": "#Anubis #Mısır #Mitoloji #Tarih #Ölüm"
    },
    {
        "prompt": "Kraken giant sea monster attacking old wooden ship in storm, thunder, huge tentacles, epic scale, cinematic, dark fantasy",
        "caption": "🦑 Denizlerin Korkusu: Kraken\n\nDenizcilerin en büyük kabusu. Gemileri tek hamlede yutan devasa ahtapot. Yüzyıllarca denizciler bu canavarı gördüklerini iddia etti.\n\nOkyanusun keşfedilmemiş derinliklerinde hala yaşıyor olabilir mi? 🌊",
        "tags": "#Kraken #Deniz #Efsane #Canavar #Mitoloji"
    },
    {
        "prompt": "Viking god Thor holding Mjolnir hammer, lightning striking, epic stormy sky, nordic armor, cinematic, hyperrealistic",
        "caption": "⚡ Şimşeklerin Efendisi: Thor\n\nİskandinav mitolojisinin en güçlüsü. Çekici Mjolnir'i ondan başka kimse kaldıramaz. Gök gürlediğinde Thor'un savaştığına inanılırdı.\n\nMarvel'ın Thor'u mu yoksa Gerçek Mitoloji Thor'u mu? 👇",
        "tags": "#Thor #Viking #Mitoloji #Valhalla #Sanat"
    },

    # --- GİZEMLİ VE ÇÖZÜLEMEMİŞ OLAYLAR ---
    {
        "prompt": "Bermuda Triangle mystery, ship and airplane disappearing in vortex, storm, compass spinning, cinematic, ominous atmosphere",
        "caption": "⚠️ Bermuda Şeytan Üçgeni\n\nYüzlerce gemi ve uçağın iz bırakmadan kaybolduğu o lanetli bölge. Manyetik alan mı, uzaylı üssü mü, yoksa sadece kötü hava koşulları mı?\n\nTeoriniz ne? 👇",
        "tags": "#Bermuda #Gizem #Okyanus #Korku #Efsane"
    },
    {
        "prompt": "Dyatlov Pass incident, snowy mountain, torn tent, mysterious lights in sky, night, eerie atmosphere, realistic photography style",
        "caption": "❄️ Dyatlov Geçidi Vakası\n\n1959'da Ural Dağları'nda 9 dağcı gizemli bir şekilde hayatını kaybetti. Çadırları içeriden yırtılmıştı, bazıları radyasyona maruz kalmıştı. Onları çadırdan kaçıran korkunç şey neydi?\n\nHala çözülemeyen en büyük sırlardan biri. 👇",
        "tags": "#Dyatlov #Gizem #Korku #Rusya #Tarih"
    },
    {
        "prompt": "Mary Celeste ghost ship floating in ocean, foggy, eerie atmosphere, empty deck, dramatic lighting, realistic oil painting style, 8k",
        "caption": "👻 Mary Celeste: Hayalet Gemi\n\n1872'de okyanusta sapasağlam ama tamamen BOŞ bulundu. Yemekler masada, eşyalar yerindeydi ama insanlardan iz yoktu.\n\nKorsanlar mı, yoksa başka bir boyut mu? 👇",
        "tags": "#HayaletGemi #Gizem #Deniz #Tarih #Efsane"
    },
    {
        "prompt": "Chernobyl ferris wheel abandoned city pripyat, overgrown, foggy, radioactive atmosphere, cinematic, apocalyptic, 8k",
        "caption": "☢️ Terk Edilmiş Şehir: Çernobil\n\n1986'daki felaketten sonra zamanın durduğu yer: Pripyat. Radyasyon yüzünden binlerce yıl kimse yaşayamayacak. Doğanın şehri geri alması ürkütücü değil mi?\n\nOraya bir turla gitmek ister miydiniz? 👇",
        "tags": "#Çernobil #Pripyat #Tarih #Urkutucu #Radyasyon"
    },

    # --- UZAY VE BİLİM ---
    {
        "prompt": "Black hole in deep space destroying a star, event horizon, glowing accretion disk, epic cosmic scale, cinematic sci-fi art, 8k",
        "caption": "🕳️ Evrenin Canavarı: Karadelikler\n\nIşığın bile kaçamadığı, zamanın durduğu yerler. İçine düşerseniz ne olacağını kimse bilmiyor. Başka bir evrene geçiş kapısı olabilir mi?\n\nUzayın derinlikleri sizi korkutuyor mu? 👇",
        "tags": "#Uzay #Karadelik #Bilim #Evren #Astronomi"
    },
    {
        "prompt": "Nikola Tesla in laboratory with electricity bolts, vintage sci-fi atmosphere, dramatic lighting, genius inventor, cinematic",
        "caption": "⚡ Zamanın Ötesindeki Deha: Nikola Tesla\n\nBugün kullandığımız elektriğin babası. Kablosuz elektrik ve sınırsız enerji üzerinde çalışıyordu. Notlarının çoğu FBI tarafından el konuldu.\n\nSizce Tesla'nın en büyük icadı bizden saklanıyor mu? 👇",
        "tags": "#Tesla #Bilim #Tarih #Teknoloji #Elektrik"
    },
    {
        "prompt": "Mars surface colony, futuristic domes, red planet landscape, earth in sky, cinematic sci-fi, realistic concept art, 8k",
        "caption": "🔴 Yeni Evimiz: Mars\n\nKızıl Gezegen'de yaşam hayal değil, plan. Bir gün Dünya'yı terk edip oraya taşınmak zorunda kalabiliriz.\n\nMars'a giden ilk kolonide olmak ister miydiniz? Evet/Hayır? 👇",
        "tags": "#Mars #Uzay #Gelecek #BilimKurgu #ElonMusk"
    },

    # --- MİSTİK OBJELER VE KİTAPLAR ---
    {
        "prompt": "Voynich manuscript open on wooden table, candlelight, mysterious plants, unreadable text, photorealistic",
        "caption": "📖 Voynich Yazması\n\nDünyanın en gizemli kitabı. İçindeki bitkiler dünyada yok, dili ise hala çözülemedi. Yapay zeka bile kıramıyor.\n\nUzaylılardan bir mesaj olabilir mi? 👇",
        "tags": "#Voynich #Gizem #Kitap #History #Sır"
    },
    {
        "prompt": "Terracotta warriors army in a dark dusty underground tomb, dramatic spotlight, clay soldiers, ancient china, mysterious atmosphere",
        "caption": "🗿 Toprak Askerler Ordusu\n\nİmparatoru korumak için yapılan 8.000 asker
