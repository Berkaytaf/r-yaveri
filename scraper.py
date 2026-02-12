import asyncio
import json
import re
import random
from playwright.async_api import async_playwright

def temizle(text):
    # Gereksiz kelimeleri ve takıları temizle
    text = re.sub(r'Rüyada|görmek|Görmek|Nedir|nedir|Tabiri|Yorumu|Anlamı', '', text)
    text = re.sub(r'[^a-zA-ZçğıöşüÇĞİÖŞÜ\s]', '', text)
    return text.strip().capitalize()

async def main():
    async with async_playwright() as p:
        # Gerçek kullanıcı gibi görünmek için User-Agent ve diğer ayarlar
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        kutuphane = set()
        alfabe = "abcçdefgğhıijklmnoöprsştuüvyz"

        # Adresleri ve Seçicileri Güncelledik
        siteler = [
            {"name": "Diyadinnet", "url": "https://www.diyadinnet.com/ruya-tabirleri-", "selector": ".list-group-item a"},
            {"name": "Ihya", "url": "https://ruyatabirleri.ihya.co/r/", "selector": ".list-unstyled a"}
        ]

        for harf in alfabe:
            print(f"--- {harf.upper()} Harfi İşleniyor ---")
            for site in siteler:
                # Her site için yeni bir sayfa açıp kapatmak "interruption" hatasını çözer
                page = await context.new_page()
                target = f"{site['url']}{harf}"
                print(f"{site['name']} taranıyor: {target}")
                
                try:
                    # Sayfaya git ve yüklenmesini bekle
                    await page.goto(target, timeout=45000, wait_until="domcontentloaded")
                    # Kısa bir rastgele bekleme (Bot korumasına takılmamak için)
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    elements = await page.query_selector_all(site['selector'])
                    count = 0
                    for el in elements:
                        txt = await el.inner_text()
                        t_txt = temizle(txt)
                        if len(t_txt) > 2:
                            kutuphane.add(t_txt)
                            count += 1
                    print(f"-> {site['name']} sitesinden {count} kavram alındı.")
                    
                except Exception as e:
                    print(f"Hata ({site['name']}): Sayfa yüklenemedi. Atlanıyor...")
                
                # Sayfayı kapatıp bir sonrakine geç
                await page.close()

        # Sonuçları Kaydet
        son_liste = sorted(list(kutuphane))
        with open("kutuphane.json", "w", encoding="utf-8") as f:
            json.dump(son_liste, f, ensure_ascii=False, indent=4)
        
        print(f"\nBitti! TOPLAM {len(son_liste)} BENZERSİZ KAVRAM TOPLANDI.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
