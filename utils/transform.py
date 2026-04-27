# utils/transform.py
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EXCHANGE_RATE = 16000

def transform_data(df):
    """Melakukan transformasi data."""
    logging.info("Starting data transformation...")

    # 1. Hapus data "Price Unavailable"
    initial_rows = len(df)
    df = df[df['Price'] != 'Price Unavailable'].reset_index(drop=True)
    unavailable_count = initial_rows - len(df)
    logging.info(f"Removed {unavailable_count} rows with 'Price Unavailable'.")

    # 2. Konversi Mata Uang (langsung pada kolom Price)
    df['Price'] = df['Price'].apply(convert_to_idr)

    # 3. Penanganan Nilai Null
    df = handle_missing_values(df)

    # 4. Penanganan Duplikat
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    dropped_count = initial_rows - len(df)
    logging.info(f"Dropped {dropped_count} duplicate rows.")

    # 5. Penanganan Data Invalid ("Unknown Product")
    unknown_product_count = sum(df['Title'] == 'Unknown Product')
    df = df[df['Title'] != 'Unknown Product'].reset_index(drop=True)
    logging.info(f"Removed {unknown_product_count} rows with 'Unknown Product' title.")

    # 6. Konversi Tipe Data
    df = convert_data_types(df)

    logging.info("Data transformation complete.")
    return df

def convert_to_idr(price_str):
    """Mengkonversi harga ke Rupiah."""
    if pd.isna(price_str):
        return None
    try:
        price_usd = float(price_str.replace('$', '').strip())
        return price_usd * EXCHANGE_RATE
    except (ValueError, AttributeError):
        logging.error(f"Could not convert price: {price_str}")
        return None

def handle_missing_values(df):
    """Menangani nilai-nilai yang hilang."""
    # Strategi penanganan missing values:
    # - Title: Tidak ada tindakan spesifik, diasumsikan penting.
    # - Price: Sudah ditangani di convert_to_idr (menjadi NaN).
    # - Rating: Isi dengan nilai mean setelah konversi ke numerik.
    # - Colors: Isi dengan 0 (asumsi 0 jika tidak ada info).
    # - Size: Isi dengan 'Unknown' jika tidak ada info.
    # - Gender: Isi dengan 'Unknown' jika tidak ada info.

    if 'Rating' in df.columns:
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        mean_rating = df['Rating'].mean()
        df['Rating'].fillna(mean_rating, inplace=True)
        logging.info(f"Handled missing values in 'Rating' by filling with mean: {mean_rating:.2f}")

    if 'Colors' in df.columns:
        df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce')
        df['Colors'].fillna(0, inplace=True)
        logging.info("Handled missing values in 'Colors' by filling with 0.")

    if 'Size' in df.columns:
        df['Size'].fillna('Unknown', inplace=True)
        logging.info("Handled missing values in 'Size' by filling with 'Unknown'.")

    if 'Gender' in df.columns:
        df['Gender'].fillna('Unknown', inplace=True)
        logging.info("Handled missing values in 'Gender' by filling with 'Unknown'.")

    return df

def convert_data_types(df):
    """Mengkonversi tipe data kolom."""
    if 'Price' in df.columns:
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        logging.info("Converted 'Price' to numeric.")

    if 'Rating' in df.columns:
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        logging.info("Converted 'Rating' to numeric.")

    if 'Colors' in df.columns:
        # Asumsi 'Colors' selalu bisa diubah menjadi integer (misalnya, '3 Colors' -> 3)
        df['Colors'] = df['Colors'].astype(str).str.replace(' Colors', '', case=False).str.strip()
        df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce').fillna(0).astype(int)
        logging.info("Converted 'Colors' to integer.")

    if 'Size' in df.columns:
        df['Size'] = df['Size'].astype(str).str.strip()
        logging.info("Converted 'Size' to string.")

    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].astype(str).str.strip()
        logging.info("Converted 'Gender' to string.")

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        logging.info("Converted 'timestamp' to datetime.")

    return df