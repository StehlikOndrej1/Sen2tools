# Mapstron - Sen2tools

## Přehled
Mapstron - Sen2tools je aplikace s grafickým uživatelským rozhraním (GUI), která umožňuje komplexní práci s družicovými snímky Sentinel-2. Obsahuje dva hlavní moduly:

1. **SentinelDownloaderGUI** – autentizace, vyhledávání a stahování dat Sentinel-2 z Copernicus Data Space Ecosystem.
2. **C2RCCProcessorGUI** – zpracování stažených snímků pomocí algoritmu C2RCC v ESA SNAP pro analýzu kvality povrchových vod.

## Určení aplikace
- GIS a DPZ analytici
- Výzkumníci kvality vod
- Správa povodí
- Vývojáři rozšiřující aplikaci

**Důležité:** Vyžaduje internetové připojení a platný účet Copernicus Data Space Ecosystem.

## Instalace

### Systémové požadavky
- **OS:** Windows (doporučeno Windows 11)
- **Python:** 3.8 - 3.10
- **Java JDK:** 11
- **ESA SNAP Desktop:** 10.0+
- **Úložiště:** 10 GB+ volného místa
- **RAM:** Minimálně 16 GB (doporučeno 32 GB)

### Instalace aplikace
1. Vytvořte virtuální prostředí:
```shell
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/macOS
pip install --upgrade pip
```

2. Instalace potřebných knihoven:
```shell
pip install PySide6 requests geopandas shapely esa-snappy jpy
```

### Konfigurace SNAP API
Podrobné kroky viz [SNAP Snappy Installation Guide](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/3114106881/Installation+and+configuration+of+the+SNAP-Python+esa_snappy+interface+SNAP+version+12).

## Použití

### Sentinel Downloader
1. Přihlaste se do Copernicus Data Space.
2. Nastavte parametry vyhledávání (datum, oblast zájmu, max. oblačnost).
3. Vyhledejte a stáhněte data do určeného adresáře.

### C2RCC Processor
1. Zadejte složku s .SAFE soubory Sentinel-2 a cílovou složku.
2. Volitelně přidejte shapefile pro ořez.
3. Vyberte požadované produkty a spusťte zpracování.

## Výstupy C2RCC
- Rrs (Remote sensing reflectance)
- AC reflectance
- IOP (Inherent Optical Properties)
- Bio-IOP
- Kd (Diffuse attenuation coefficient)
- Uncertainty
- Total concentrations

Výsledky jsou uloženy ve formátu BEAM-DIMAP.

## Vývojářská dokumentace
Aplikace využívá PySide6, geopandas, requests a SNAP API. Je strukturována do hlavních modulů (`main_app.py`, `sentinel2_downloader.py`, `c2rcc_processor.py`). Podporuje vícejazyčné GUI.

## Podpora a řešení problémů
Pro běžné chyby a jejich řešení viz dokumentaci. Případně na email: stehlik.on@seznam.cz
Pro další pomoc navštivte:
- [SNAP Tutorials](https://step.esa.int/main/doc/tutorials/)
- [SNAP Fórum](https://forum.step.esa.int/)

## Reference
- [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
- [Uživatelská příručka Sentinel-2](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi)
