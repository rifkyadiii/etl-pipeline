import pandas as pd
import logging
import os
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from sqlalchemy import create_engine, text, schema
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from gspread.exceptions import APIError, WorksheetNotFound
import psycopg2
import sys
from dotenv import load_dotenv
import json

load_dotenv()

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurasi untuk CSV
CSV_OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'products.csv'))

# Konfigurasi untuk Google Sheets
GSHEET_URL = os.getenv('GSHEET_URL')
GSHEET_SERVICE_ACCOUNT_PATH = os.getenv('GSHEET_SERVICE_ACCOUNT_PATH')
GSHEET_SHEET_NAME = os.getenv('GSHEET_SHEET_NAME')

def prepare_dataframe_for_export(df):
    """Mempersiapkan DataFrame untuk diekspor ke berbagai format."""
    df_export = df.copy()

    # Konversi kolom timestamp ke string untuk menghindari masalah serialisasi JSON
    if 'timestamp' in df_export.columns:
        df_export['timestamp'] = df_export['timestamp'].astype(str)

    return df_export

def load_to_csv(df):
    """Menyimpan DataFrame ke dalam format CSV."""
    logging.info(f"Loading data to CSV: {CSV_OUTPUT_PATH}")
    try:
        os.makedirs(os.path.dirname(CSV_OUTPUT_PATH), exist_ok=True)
        df.to_csv(CSV_OUTPUT_PATH, index=False, encoding='utf-8')
        logging.info(f"Successfully loaded {len(df)} rows to CSV: {CSV_OUTPUT_PATH}")
        return True
    except Exception as e:
        logging.error(f"Error loading data to CSV {CSV_OUTPUT_PATH}: {e}")
        return False

def load_to_gsheets(df):
    """Menyimpan DataFrame ke Google Sheets."""
    logging.info(f"Loading data to Google Sheets: {GSHEET_URL} - {GSHEET_SHEET_NAME}")

    if Path(GSHEET_SERVICE_ACCOUNT_PATH).exists():
        try:
            creds = Credentials.from_service_account_file(
                GSHEET_SERVICE_ACCOUNT_PATH,
                scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            )
        except Exception as e:
            logging.error(f"Error reading local service account file: {e}")
            return False
            
    else:
        gsheet_json_env = os.getenv('GSHEET_JSON_DATA')
        if gsheet_json_env:
            try:
                info = json.loads(gsheet_json_env)
                creds = Credentials.from_service_account_info(
                    info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                )
            except Exception as e:
                logging.error(f"Gagal memparsing GSHEET_JSON_DATA dari cloud secrets: {e}")
                return False
        else:
            logging.error("Kredensial Google Sheets tidak ditemukan (File JSON lokal tidak ada, dan Cloud Secrets kosong).")
            return False

    try:
        sheet_id = None
        if '/d/' in GSHEET_URL:
            parts = GSHEET_URL.split('/d/')
            if len(parts) > 1:
                sheet_id = parts[1].split('/')[0]

        if not sheet_id:
            logging.error("Invalid Google Sheets URL format")
            return False

        creds = Credentials.from_service_account_file(
            GSHEET_SERVICE_ACCOUNT_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        gc = gspread.authorize(creds)

        try:
            spreadsheet = gc.open_by_key(sheet_id)
        except APIError as e:
            logging.error(f"Error opening Google Sheet with ID '{sheet_id}': {e}")
            return False

        try:
            worksheet = spreadsheet.worksheet(GSHEET_SHEET_NAME)
        except WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=GSHEET_SHEET_NAME, rows=100, cols=20)
            logging.info(f"Created new worksheet: {GSHEET_SHEET_NAME}")
        except APIError as e:
            logging.error(f"Error accessing/creating worksheet '{GSHEET_SHEET_NAME}': {e}")
            return False

        worksheet.clear()

        header = df.columns.tolist()
        values = []
        for _, row in df.iterrows():
            row_values = []
            for val in row:
                if pd.isna(val):
                    row_values.append('')
                elif isinstance(val, pd.Timestamp):
                    row_values.append(val.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    row_values.append(str(val))
            values.append(row_values)

        all_data = [header] + values
        worksheet.update(values=all_data, range_name='A1')

        logging.info(f"Successfully loaded {len(df)} rows to Google Sheets")
        return True
    except APIError as e:
        logging.error(f"Google Sheets API error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error loading data to Google Sheets: {e}")
        return False
    
def load_to_postgres(df):
    """Menyimpan DataFrame ke PostgreSQL."""
    
    POSTGRES_DB_URL = os.getenv('POSTGRES_DB_URL')
    DB_TABLE = os.getenv('DB_TABLE')

    logging.info(f"Loading data to PostgreSQL: postgresql+psycopg2://***:***@***:***/***?sslmode=require - Table: {DB_TABLE}")

    try:
        engine = create_engine(POSTGRES_DB_URL)
        with engine.connect() as conn:
            df.to_sql(DB_TABLE, con=conn, if_exists='append', index=False)
        logging.info(f"Successfully loaded {len(df)} rows to PostgreSQL table '{DB_TABLE}'")
        return True
    except (SQLAlchemyError, ProgrammingError) as e:
        logging.error(f"PostgreSQL error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error saving to PostgreSQL: {e}")
        return False

def load_data(df):
    """Fungsi utama untuk memuat data ke semua repositori."""
    all_loads_successful = True

    df_export = prepare_dataframe_for_export(df)

    # 1. CSV export
    csv_success = load_to_csv(df_export)
    if not csv_success:
        logging.error("Gagal menyimpan ke CSV!")
        all_loads_successful = False

    # 2. PostgreSQL export
    pg_success = load_to_postgres(df_export)
    if not pg_success:
        logging.error("Gagal menyimpan ke PostgreSQL!")
        all_loads_successful = False

    # 3. Google Sheets export
    if Path(GSHEET_SERVICE_ACCOUNT_PATH).exists():
        gsheets_success = load_to_gsheets(df_export)
        if not gsheets_success:
            logging.error("Gagal menyimpan ke Google Sheets!")
            all_loads_successful = False
    else:
        logging.warning(f"Melewati ekspor Google Sheets - file kredensial tidak ditemukan: {GSHEET_SERVICE_ACCOUNT_PATH}")

    return all_loads_successful