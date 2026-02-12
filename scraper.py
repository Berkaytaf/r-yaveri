import asyncio
import json
import re
import random
from playwright.async_api import async_playwright

def temizle(text):
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu|Anlamı|Diyanet', '', text)
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def main():
    async with async_playwright() as p:
        # Bot korumalarını aşmak için Stealth benzeri ayarlar
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="tr-TR",
            timezone_id="Europe/Istanbul"
        )
        
        kutuphane = set()
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"
        
        # Bu sefer hedefi sadece ana dizinlere çeviriyoruz
        targets = [
            "https://www.diyadinnet.com/ruya-tabirleri-",
            "https://ruyatabirleri.ihya.co/r/"
        ]

        page = await context.new_page()

        for harf in alfabe:
            for base_url in targets:
                url = f"{base_url}{harf}"
                print(f"Bacı {harf.upper()} harfine bakıyor: {url}")
                
                try:
                    # Sayfayı yükle ve "insansı" bir bekleme yap
                    await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    await asyncio.sleep(random.uniform(3, 7))
                    
                    # Sayfadaki tüm rüya linklerini tek seferde yakala
                    links = await page.query_selector_all("a")
                    count = 0
                    for link in links:
                        t = await link.inner_text()
                        cleaned = temizle(t)
                        if len(cleaned) > 3:
                            kutuphane.add(cleaned)
                            count += 1
                    print(f"-> {count} tane yeni kavram hafızaya alındı.")
                except:
                    print(f"!! {harf} harfinde bir engel var, atlanıyor...")

        # Sonuçları kaydet
        final_list = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        
        print(f"\nZAFER! Toplam {len(final_list)} kavram kütüphaneye eklendi.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
