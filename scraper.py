import asyncio
import json
import re
from playwright.async_api import async_playwright

# Rüya başlıklarını temizleme fonksiyonu
def temizle(text):
    # "Rüyada", "Görmek", "Nedir" gibi kelimeleri ve gereksiz ekleri atar
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu', '', text)
    # Rakamları ve özel karakterleri temizle
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def scrape_site(page, url, selector):
    try:
        await page.goto(url, timeout=60000)
        elements = await page.query_selector_all(selector)
        results = []
        for el in elements:
            raw_text = await el.inner_text()
            temiz_text = temizle(raw_text)
            if len(temiz_text) > 2: # Çok kısa (hatalı) verileri ele
                results.append(temiz_text)
        return results
    except Exception as e:
        print(f"Hata oluştu ({url}): {e}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        kutuphane = set()
        alfabe = "abcdefghijklmnoprstuvyz"

        # Hedef Site Yapılandırmaları
        siteler = [
            {"name": "Diyadinnet", "url": "https://www.diyadinnet.com/ruya-tabirleri-", "selector": ".list-group-item a"},
            {"name": "Ihya", "url": "https://ruya-tabirleri.ihya.co/r/", "selector": ".list-unstyled a"},
            {"name": "Sabah", "url": "https://www.sabah.com.tr/ruya-tabirleri/", "selector": ".list-content a"},
            {"name": "Mahmure", "url": "https://www.hurriyet.com.tr/mahmure/ruya-tabirleri/", "selector": ".category-list a"}
        ]

        for harf in alfabe:
            print(f"--- {harf.upper()} Harfi İşleniyor ---")
            for site in siteler:
                # Her sitenin URL yapısı farklı olabilir, genelde harf sonuna eklenir
                full_url = f"{site['url']}{harf}"
                print(f"{site['name']} taranıyor...")
                veriler = await scrape_site(page, full_url, site['selector'])
                kutuphane.update(veriler)

        # Sonuçları Kaydet
        son_liste = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(son_liste, f, ensure_ascii=False, indent=4)
        
        print(f"Bitti! Toplam {len(son_liste)} benzersiz kavram heybeye atıldı.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
