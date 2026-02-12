import asyncio
import json
import os
from playwright.async_api import async_playwright

async def scrape_concepts():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"
        kutuphane = set()

        # Örnek Hedef Site: Diyadinnet ve benzeri dizin yapısı
        # Not: Gerçek sitelerin URL yapılarına göre burası özelleştirilir
        base_url = "https://www.diyadinnet.com/ruya-tabirleri-"
        
        for harf in alfabe:
            print(f"{harf.upper()} harfi taranıyor...")
            try:
                await page.goto(f"{base_url}{harf}", timeout=60000)
                # Sitedeki rüya linklerini yakalıyoruz (Genelde <a> etiketleri)
                elements = await page.query_selector_all(".list-group-item a") 
                
                for el in elements:
                    text = await el.inner_text()
                    # Temizlik: "Rüyada" ve "Görmek" kelimelerini at, sadece ana kavramı al
                    temiz = text.replace("Rüyada", "").replace("görmek", "").replace("Görmek", "").strip()
                    if temiz:
                        kutuphane.add(temiz.capitalize())
            except Exception as e:
                print(f"{harf} harfinde hata: {e}")

        # Veriyi alfabetik sırala ve JSON olarak kaydet
        sonuc = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=4)
            
        await browser.close()
        print(f"İşlem tamam! Toplam {len(sonuc)} kavram toplandı.")

if __name__ == "__main__":
    asyncio.run(scrape_concepts())
