# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 02:48:10 2025

@author: Emre
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
import random

# Chrome ayarları
options = Options()
options.add_argument("--start-maximized")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
options.add_argument("--disable-blink-features=AutomationControlled")

# WebDriver yolu
driver_path = r"C:\Users\Emre\Desktop\chromedriver-win64\chromedriver.exe"
service = Service(driver_path)
browser = webdriver.Chrome(service=service, options=options)

# İlan linkleri ve detaylar için listeler
base_url = "https://www.hepsiemlak.com/atakum-satilik"
linkdata = []
adinfos = []

# Sayfalama ile ilan linklerini toplama
def collect_links():
    page = 1
    max_pages = 10  # Gerekirse artırılabilir
    while len(linkdata) < 100 and page <= max_pages:
        url = f"{base_url}?page={page}"
        try:
            browser.get(url)
            time.sleep(random.uniform(5, 8))  # Sayfa yüklenmesi için bekleme
            soup = bs(browser.page_source, "lxml")
            links = soup.find_all("a", {"class": "card-link"})
            if not links:
                print("Daha fazla ilan bulunamadı.")
                break
            for link in links:
                href = link.get("href")
                if href and href not in linkdata:
                    linkdata.append("https://www.hepsiemlak.com" + href)
            print(f"Sayfa {page} tarandı. Toplam {len(linkdata)} ilan linki toplandı.")
            page += 1
            time.sleep(random.uniform(5, 10))  # Sayfalar arası bekleme
        except Exception as e:
            print(f"Link toplama hatası (Sayfa {page}): {e}")
            break

# İlan detaylarını çekme
def collect_details():
    counter = 1
    for url in linkdata:
        try:
            browser.get(url)
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    '//*[@id="__layout"]/div/div/section[3]/div[3]/div[1]/div[1]/div[1]/div[2]'
                ))
            )
            # Temel bilgiler
            ilan_url = url
            price = browser.find_element(
                By.XPATH,
                '//*[@id="__layout"]/div/div/section[3]/div[3]/div[1]/div[1]/div[1]/div[2]/div[1]'
            ).text.strip()

            loc_elem = browser.find_element(
                By.XPATH,
                '//*[@id="__layout"]/div/div/section[3]/div[3]/div[1]/div[1]/div[1]/div[2]/ul'
            )
            parts = [l.strip() for l in loc_elem.text.strip().split("\n") if l.strip()]
            mahalle = parts[2] if len(parts) >= 3 else "-"

            # Diğer detaylar
            ilan_no = son_guncelleme = ilan_durumu = konut_tipi = oda_sayisi = banyo_sayisi = "-"
            brut_m2 = net_m2 = kat_sayisi = bulundu_kat = bina_yasi = isinma_tipi = kredi_durumu = tapu_durumu = esya_durumu = kullanimi_durumu = cephe = aidat = takas = "-"

            details_container = browser.find_element(
                By.XPATH,
                '//*[@id="__layout"]/div/div/section[3]/div[3]/div[1]/div[1]/div[1]/div[2]'
            )
            items = details_container.find_elements(By.XPATH, ".//li[contains(@class, 'spec-item')]")
            for item in items:
                txt = item.text.strip()
                if txt.startswith("İlan no"): ilan_no = txt.replace("İlan no", "").strip()
                if txt.startswith("Son Güncelleme"): son_guncelleme = txt.replace("Son Güncelleme", "").strip()
                if txt.startswith("İlan Durumu"): ilan_durumu = txt.replace("İlan Durumu", "").strip()
                if txt.startswith("Konut Tipi"): konut_tipi = txt.replace("Konut Tipi", "").strip()
                if txt.startswith("Oda Sayısı"): oda_sayisi = txt.replace("Oda Sayısı", "").strip()
                if txt.startswith("Banyo Sayısı"): banyo_sayisi = txt.replace("Banyo Sayısı", "").strip()
                if txt.startswith("Brüt / Net M2"):
                    vals = txt.replace("Brüt / Net M2", "").split("/")
                    brut_m2 = vals[0].replace("m2", "").strip() if vals else "-"
                    net_m2 = vals[1].replace("m2", "").strip() if len(vals) > 1 else "-"
                if txt.startswith("Kat Sayısı"): kat_sayisi = txt.replace("Kat Sayısı", "").strip()
                if txt.startswith("Bulunduğu Kat"): bulundu_kat = txt.replace("Bulunduğu Kat", "").strip()
                if txt.startswith("Bina Yaşı"): bina_yasi = txt.replace("Bina Yaşı", "").strip()
                if txt.startswith("Isınma Tipi"): isinma_tipi = txt.replace("Isınma Tipi", "").strip()
                if txt.startswith("Krediye Uygunluk"): kredi_durumu = txt.replace("Krediye Uygunluk", "").strip()
                if txt.startswith("Tapu Durumu"): tapu_durumu = txt.replace("Tapu Durumu", "").strip()
                if txt.startswith("Eşya Durumu"): esya_durumu = txt.replace("Eşya Durumu", "").strip()
                if txt.startswith("Kullanım Durumu"): kullanimi_durumu = txt.replace("Kullanım Durumu", "").strip()
                if txt.startswith("Cephe"): cephe = txt.replace("Cephe", "").strip()
                if txt.startswith("Aidat"): aidat = txt.replace("Aidat", "").strip()
                if txt.startswith("Takas"): takas = txt.replace("Takas", "").strip()

            row = {
                "Link": ilan_url,
                "Fiyat": price,
                "Mahalle": mahalle,
                "İlan no": ilan_no,
                "Son Güncelleme": son_guncelleme,
                "İlan Durumu": ilan_durumu,
                "Konut Tipi": konut_tipi,
                "Oda Sayısı": oda_sayisi,
                "Banyo Sayısı": banyo_sayisi,
                "Brüt M2": brut_m2,
                "Net M2": net_m2,
                "Kat Sayısı": kat_sayisi,
                "Bulunduğu Kat": bulundu_kat,
                "Bina Yaşı": bina_yasi,
                "Isınma Tipi": isinma_tipi,
                "Krediye Uygunluk": kredi_durumu,
                "Tapu Durumu": tapu_durumu,
                "Eşya Durumu": esya_durumu,
                "Kullanım Durumu": kullanimi_durumu,
                "Cephe": cephe,
                "Aidat": aidat,
                "Takas": takas
            }
            adinfos.append(row)
            print(f"İlan {counter} çekildi.")
            counter += 1

            # İlanlar arasında rastgele uzun bekleme
            sleep_time = random.uniform(8, 15)  # İstersen 10-20 saniye gibi de yapabiliriz
            print(f"{sleep_time:.2f} saniye bekleniyor...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"Hata alındı (İlan {counter}): {e}")
            continue

    # Excel'e kaydet
    df_data = pd.DataFrame(adinfos)
    df_data = df_data.reindex(sorted(df_data.columns), axis=1)
    print("\nTüm İlan Verileri:")
    print(df_data.to_string(index=True))
    df_data.to_excel("ilan_detaylari_finallerinkisi.xlsx", index=False)
    print("Veriler Excel dosyasına kaydedildi: ilan_detaylari_finallerinkisi.xlsx")

# Ana çalıştırma
def main():
    collect_links()
    collect_details()
    browser.quit()
    print("Program sonlandı.")

if __name__ == "__main__":
    main()
