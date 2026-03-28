# fasih analytics - Survey Monitoring

Tool untuk mengambil data progres dan assignment petugas survei dari platform FASIH (https://fasih-sm.bps.go.id) dan menghasilkan grafik monitoring serta laporan pivot Excel.

## Fitur

- Login otomatis dengan session cache (Selenium)
- Fetch data progres pencacahan dan pemutakhiran secara paralel (async)
- Interaktif memilih survei yang ingin di-scrape
- Generate grafik stacked bar per survei dan per provinsi
- Generate laporan pivot Excel
- Mendukung kustomisasi judul grafik via argumen CLI


## Instalasi

```bash
# Clone repo dan masuk ke folder
cd fasih-scrapping

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Penggunaan

### Cara 1: Double-click (macOS)
Jalankan `launch.command` langsung dari Finder.

### Cara 2: Terminal

```bash
source venv/bin/activate
python main.py
```

### Opsi CLI

| Argumen | Keterangan |
|---|---|
| `--relogin` | Hapus session cache dan login ulang |
| `--title "Judul"` | Set judul grafik progres (disimpan permanen) |
| `--user-title "Judul"` | Set judul grafik penugasan user (disimpan permanen) |

Contoh:
```bash
python main.py --relogin
python main.py --title "Monitoring Maret 2026"
```

## Output

- `outputs/csv/report_assignment.csv` — data progres & penugasan terbaru
- `outputs/csv/report_pemutakhiran.csv` — data pemutakhiran terbaru
- `outputs/csv/survey_collection_deadline_adjusted.csv` — metadata survei
- `outputs/pivot_report.xlsx` — laporan pivot Excel
- `images/progress_assignment.png` — grafik progres pencacahan
- `images/user_assignment.png` — grafik penugasan user

## Dependencies

| Package | Versi |
|---|---|
| httpx | 0.28.1 |
| InquirerPy | 0.3.4 |
| matplotlib | 3.10.8 |
| numpy | 2.4.3 |
| openpyxl | 3.1.5 |
| pandas | 3.0.1 |
| selenium | 4.41.0 |
