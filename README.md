# 🛠 DevTools Suite

Aplikasi Python dengan fitur **Selenium Testing** dan **ZIP Compressor**.

## 📁 Struktur Project

```
myapp/
├── main.py               # Entry point aplikasi
├── requirements.txt      # Dependencies
├── src/
│   ├── compressor.py     # Modul kompresi ZIP
│   └── selenium_tests.py # Modul Selenium testing
├── tests/
│   └── test_app.py       # Unit tests
├── sample_files/         # File contoh (auto-generated)
└── output/               # Hasil output (ZIP, laporan)
```

## 🚀 Cara Menjalankan

### Install dependencies
```bash
pip install -r requirements.txt
```

### Jalankan aplikasi
```bash
python main.py
```

### Jalankan unit tests
```bash
python -m pytest tests/ -v
# atau
python tests/test_app.py
```

## ✨ Fitur

### 1. 🧪 Selenium Web Tests
- Load testing halaman web
- Verifikasi elemen HTML (title, h1, links)
- Cek JavaScript errors
- Test aksesibilitas (alt tags)
- SSL verification
- Performance check
- Simpan laporan ke file `.txt`

> **Mode otomatis:** Jika Chrome tersedia, menggunakan Selenium nyata.
> Jika tidak, berjalan dalam **mock mode** yang mensimulasikan hasil realistis.

### 2. 📦 ZIP Compressor
- Kompres file tunggal atau banyak file
- Kompres seluruh folder (rekursif)
- Pilih level kompresi (1-9)
- Tampilkan rasio kompresi
- Sertakan `metadata.txt` otomatis

### 3. 🔍 ZIP Inspector
- Lihat isi file ZIP
- Tampilkan ukuran original vs compressed
- Tanggal modifikasi tiap file

### 4. 📄 Generate Sample Files
- Buat file contoh untuk dicoba langsung

## 🧪 Unit Tests Coverage

| Modul | Tests |
|-------|-------|
| Compressor | 10 tests |
| Selenium | 6 tests |

```bash
python tests/test_app.py
```
