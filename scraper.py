import asyncio
import json
import re
import random
from playwright.async_api import async_playwright

def temizle(text):
    # Rüyada, Görmek gibi kelimeleri temizleyip baş harfi büyük yapıyoruz
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu|Anlamı', '', text)
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def scrape_site(context, target_url, selector):
    page = await context.new_page()
    kavramlar = []
    try:
        # Gerçek bir insan gibi yavaşça git
        await page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 5)) # Sayfanın oturması için bekle
        
        # Seçiciyi daha esnek tutuyoruz: 'a' etiketlerini topla
        elements = await page.query_selector_all(selector)
        for el in elements:
            txt = await el.inner_text()
            temiz_txt = temizle(txt)
            if len(temiz_txt) > 2:
                kavramlar.append(temiz_txt)
    except Exception as e:
        print(f"Hata oluştu ({target_url}): {e}")
    finally:
        await page.close()
    return kavramlar

async def main():
    async with async_playwright() as p:
        # Gizlilik ayarları: Bot olduğumuzu saklıyoruz
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={"Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"}
        )
        
        kutuphane = set()
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"

        # Diyadinnet için seçiciyi '.list-group a' olarak güncelledik
        siteler = [
            {"name": "Diyadinnet", "url": "https://www.diyadinnet.com/ruya-tabirleri-", "selector": "div.list-group a"}
        ]

        for harf in alfabe:
            print(f"--- {harf.upper()} Harfi İşleniyor ---")
            for site in siteler:
                target = f"{site['url']}{harf}"
                print(f"{site['name']} taranıyor...")
                veriler = await scrape_site(context, target, site['selector'])
                kutuphane.update(veriler)
                print(f"-> {len(veriler)} yeni kavram eklendi.")

        # Sonuçları Kaydet
        son_liste = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(son_liste, f, ensure_ascii=False, indent=4)
        
        print(f"\nİşlem Tamam! Toplam {len(son_liste)} benzersiz kavram GitHub'a hazır.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
