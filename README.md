# ⚙️ ETL Pipeline Simulation

Simulasi interaktif dari proses **Extract, Transform, dan Load (ETL)** yang dibangun menggunakan Python dan Streamlit. Proyek ini dibuat sebagai portofolio *Data Engineering* untuk mendemonstrasikan proses penarikan data secara *real-time*, pembersihan data, hingga pemuatan ke Cloud Database dan Google Sheets.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 🌟 Fitur Utama

- **Antarmuka Interaktif:** UI berbasis Web menggunakan Streamlit yang membagi fase ETL ke dalam tab terpisah.
- **Web Scraping (Extract):** Menarik data produk pakaian secara langsung dari situs web tiruan [*Fashion Studio*](https://fashion-studio.dicoding.dev) menggunakan BeautifulSoup4.
- **Data Cleaning (Transform):** Mengonversi mata uang USD ke IDR, menangani nilai yang hilang (*missing values*), menghapus duplikat, dan standarisasi tipe data menggunakan Pandas (mendukung Copy-on-Write).
- **Multi-Destination (Load):** Memuat data bersih secara paralel ke:
  - 🐘 **Aiven PostgreSQL** (Cloud Database)
  - 📊 **Google Sheets** (menggunakan Google Service Account)
  - 📄 **CSV & SQL Dump** (Fitur *download* lokal)
- **Live Terminal Logging:** Menampilkan proses *backend* secara *real-time* ke layar antarmuka pengguna dengan fitur *auto-scroll* dan *light mode*, dilengkapi sensor keamanan (*regex*) untuk menyembunyikan *password* dan ID.
- **Automated Testing:** Memiliki skrip pengujian unit (*Unit Test*) menggunakan `pytest`.

## 🏗️ Arsitektur Direktori

```text
📦 etl-pipeline/
 ┣ 📂 utils/
 ┃ ┣ 📜 extract.py      # Modul Web Scraping
 ┃ ┣ 📜 transform.py    # Modul Pembersihan & Transformasi Data Pandas
 ┃ ┗ 📜 load.py         # Modul Ekspor ke Postgres, GSheets, & CSV
 ┣ 📂 tests/            # Folder Unit Testing
 ┃ ┣ 📜 test_extract.py
 ┃ ┣ 📜 test_transform.py
 ┃ ┗ 📜 test_load.py
 ┣ 📜 app.py            # Streamlit Frontend Application
 ┣ 📜 main.py           # Skrip eksekusi CLI (opsional)
 ┣ 📜 requirements.txt  # Daftar dependensi library
 ┣ 📜 .env.example      # Contoh variabel lingkungan
 ┗ 📜 README.md         # Dokumentasi proyek

```

## 🚀 Cara Menjalankan di Komputer Lokal

### 1. Kloning Repositori

```bash
git clone [https://github.com/username-anda/etl-pipeline.git](https://github.com/username-anda/etl-pipeline.git)
cd etl-pipeline

```

### 2. Siapkan Virtual Environment & Instalasi

```bash
python -m venv etl-pipeline
source etl-pipeline/bin/activate  # Untuk Linux/Mac
# etl-pipeline\Scripts\activate   # Untuk Windows

pip install -r requirements.txt

```

### 3. Konfigurasi Variabel Lingkungan (.env)

Buat file bernama `.env` di direktori utama, lalu isi dengan kredensial Anda.

```env
POSTGRES_DB_URL="postgresql+psycopg2://<user>:<password>@<host>:<port>/<db_name>?sslmode=require"
DB_TABLE="productstoscrape"
GSHEET_URL="[https://docs.google.com/spreadsheets/d/ID_SHEET_ANDA/edit](https://docs.google.com/spreadsheets/d/ID_SHEET_ANDA/edit)"
GSHEET_SHEET_NAME="Sheet1"
GSHEET_SERVICE_ACCOUNT_PATH="google-sheets-api.json"

```

### 4. Jalankan Aplikasi

```bash
streamlit run app.py

```

## 🧪 Menjalankan Unit Test

Proyek ini mengadopsi prinsip pengembangan yang baik dengan menyertakan tes otomatis. Jalankan perintah berikut untuk menguji *pipeline* dan melihat cakupan kode (*coverage*):

```bash
python -m pytest --cov=utils tests/

```

## ☁️ Deployment Cloud

* **Frontend:** Di-*deploy* menggunakan **Streamlit Community Cloud**. Kredensial `.env` disuntikkan secara aman melalui fitur *Streamlit Secrets*.
* **Database:** Menggunakan PostgreSQL dari **Aiven Cloud**.

---