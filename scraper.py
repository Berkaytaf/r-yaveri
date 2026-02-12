import asyncio
import json
import re
import random
from playwright.async_api import async_playwright

def temizle(text):
    # Gereksizleri at, anahtar kelimeyi bırak
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu|Anlamı', '', text)
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def main():
    async with async_playwright() as p:
        # Bot olduğumuzu saklamak için tam donanımlı tarayıcı
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        kutuphane = set()
        # İlk aşamada sadece en kolay siteye (Diyadinnet) odaklanalım
        target_base = "https://www.diyadinnet.com/ruya-tabirleri-"
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"

        page = await context.new_page()

        for harf in alfabe:
            url = f"{target_base}{harf}"
            print(f"--- {harf.upper()} taranıyor ---")
            
            try:
                # Sayfaya git ve her şeyin yüklenmesini bekle
                await page.goto(url, timeout=60000, wait_until="networkidle")
                await asyncio.sleep(random.uniform(3, 6)) # İnsansı bekleme
                
                # Sitenin içindeki TÜM linkleri tara (en geniş tarama)
                links = await page.query_selector_all("a")
                count = 0
                for link in links:
                    href = await link.get_attribute("href")
                    if href and "ruya-tabiri-" in href: # Sadece rüya linklerini al
                        txt = await link.inner_text()
                        t_txt = temizle(txt)
                        if len(t_txt) > 2:
                            kutuphane.add(t_txt)
                            count += 1
                print(f"-> {harf} harfinden {count} kelime yakalandı.")
                
            except Exception as e:
                print(f"Hata: {harf} harfi atlandı.")
            
        # JSON'u güncelle
        son_liste = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(son_liste, f, ensure_ascii=False, indent=4)
        
        print(f"\nFinal: {len(son_liste)} kelime heybede!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
