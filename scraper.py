import asyncio
import json
import re
import random
from playwright.async_api import async_playwright

def temizle(text):
    # "Rüyada", "Görmek" gibi fazlalıkları atıp saf kavramı bırakır
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu|Anlamı|Diyanet', '', text)
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def scrape_site(context, target_url):
    page = await context.new_page()
    kavramlar = set()
    try:
        # Sayfaya git ve "tamamen" yüklenmesini bekleme, "domcontentloaded" yeterli
        print(f"Bacı bakıyor: {target_url}")
        await page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
        
        # Bazı sitelerdeki "Çerez Kabul" butonlarını atlamak için bir saniye bekle
        await asyncio.sleep(2)
        
        # Sayfadaki TÜM linkleri topla
        links = await page.query_selector_all("a")
        for link in links:
            href = await link.get_attribute("href")
            txt = await link.inner_text()
            
            # Eğer link rüya tabiri içeriyorsa veya metin rüya formatındaysa al
            if href and ("ruya-tabiri" in href or "ruya-tabirleri" in href):
                t_txt = temizle(txt)
                if len(t_txt) > 3 and len(t_txt.split()) < 6: # Çok uzun cümleleri alma
                    kavramlar.add(t_txt)
    except Exception as e:
        print(f"Hata: {target_url} atlandı.")
    finally:
        await page.close()
    return kavramlar

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Daha profesyonel bir tarayıcı kimliği
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        kutuphane = set()
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"

        # Hedef yelpazesini genişlettik
        siteler = [
            "https://www.diyadinnet.com/ruya-tabirleri-",
            "https://www.hurriyet.com.tr/mahmure/ruya-tabirleri/",
            "https://www.sabah.com.tr/ruya-tabirleri/"
        ]

        # Her harf için her siteyi tara
        for harf in alfabe:
            print(f"\n--- {harf.upper()} Harfi İçin Operasyon Başladı ---")
            tasks = [scrape_site(context, f"{site}{harf}") for site in siteler]
            sonuclar = await asyncio.gather(*tasks)
            
            for s in sonuclar:
                kutuphane.update(s)
            
            print(f"Şu ana kadar {len(kutuphane)} benzersiz kavram heybede!")
            
            # GitHub'ı çok yormamak ve sitelerden ban yememek için kısa bir mola
            await asyncio.sleep(random.uniform(1, 3))

        # Sonuçları JSON'a dök
        son_liste = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(son_liste, f, ensure_ascii=False, indent=4)
        
        print(f"\nZAFER: Toplam {len(son_liste)} rüya kavramı hafızaya kazındı!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
