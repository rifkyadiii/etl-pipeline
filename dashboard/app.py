from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import logging
import os
from utils.extract import scrape_main
from utils.transform import transform_data
from utils.load import load_data, prepare_dataframe_for_export

# ==========================================
# KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="ETL Pipeline Portfolio", page_icon="⚙️", layout="wide")

SOURCE_URL = "https://fashion-studio.dicoding.dev"

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    .main-header {
        padding: 1.6rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p { margin: 0.4rem 0 0 0; opacity: 0.85; line-height: 1.5; }
    .main-header a { color: #93C5FD; text-decoration: none; font-weight: 600; }

    .info-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .stat-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        text-align: center;
    }
    .stat-card .label { font-size: 0.8rem; color: #64748B; margin: 0; }
    .stat-card .value { font-size: 1.6rem; font-weight: 700; margin: 0.2rem 0 0 0; color: #0F172A; }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 8px 18px; font-weight: 600; }
    .stButton>button { border-radius: 10px; font-weight: 600; padding: 0.6rem 1.2rem; }

    .terminal-bar {
        background: #E2E8F0; border-radius: 8px 8px 0 0; padding: 6px 10px;
        display: flex; gap: 6px; border: 1px solid #E2E8F0; border-bottom: none;
    }
    .terminal-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================
st.markdown(f"""
<div class="main-header">
    <h1>⚙️ ETL Pipeline Simulation</h1>
    <p>Simulasi proses <b>Extract, Transform, dan Load (ETL)</b> dari sebuah situs e-commerce fiktif,
    dibuat sebagai portofolio interaktif untuk mendemonstrasikan alur rekayasa data secara real-time.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# STATE
# ==========================================
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'transformed_data' not in st.session_state:
    st.session_state.transformed_data = None
if 'loaded' not in st.session_state:
    st.session_state.loaded = False

# ==========================================
# SIDEBAR — STATUS PIPELINE
# ==========================================
def stage_badge(done, label):
    icon = "✅" if done else "⬜"
    color = "#16A34A" if done else "#94A3B8"
    return f'<p style="margin:0.3rem 0; color:{color}; font-weight:600;">{icon} {label}</p>'

def render_pipeline_status():
    """Menulis ulang status pipeline ke placeholder sidebar dengan data session_state terkini."""
    html = (
        stage_badge(st.session_state.extracted_data is not None, "1. Extract")
        + stage_badge(st.session_state.transformed_data is not None, "2. Transform")
        + stage_badge(st.session_state.loaded, "3. Load")
    )
    status_placeholder.markdown(html, unsafe_allow_html=True)

with st.sidebar:
    st.header("📌 Status Pipeline")
    status_placeholder = st.empty()
    render_pipeline_status()

    st.divider()
    if st.button("🔄 Reset Pipeline", width='stretch'):
        st.session_state.extracted_data = None
        st.session_state.transformed_data = None
        st.session_state.loaded = False
        st.rerun()

    st.divider()
    st.link_button("🌐 Buka Sumber Data", SOURCE_URL, width='stretch')
    st.caption("Dibuat dengan Streamlit • BeautifulSoup • PostgreSQL • Google Sheets")

# ==========================================
# LOG HANDLER (AUTO-SCROLL, LIGHT MODE, TAMPILAN TERMINAL)
# ==========================================
class StreamlitLogHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        log_html = "<br>".join(self.logs)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background-color: transparent; }}
                #terminal-bar {{
                    background: #E2E8F0; border-radius: 8px 8px 0 0; padding: 7px 10px;
                    display: flex; gap: 6px; box-sizing: border-box;
                }}
                .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
                #log-container {{
                    background-color: #ffffff;
                    color: #334155;
                    font-family: 'SFMono-Regular', Consolas, monospace;
                    font-size: 12.5px;
                    padding: 10px 12px;
                    height: 350px;
                    overflow-y: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                    border-radius: 0 0 8px 8px;
                    box-shadow: inset 0 1px 3px rgba(0,0,0,0.03);
                }}
                #log-container::-webkit-scrollbar {{ width: 8px; }}
                #log-container::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 4px; }}
                #log-container::-webkit-scrollbar-thumb {{ background: #c1c1c1; border-radius: 4px; }}
                #log-container::-webkit-scrollbar-thumb:hover {{ background: #a8a8a8; }}
            </style>
        </head>
        <body>
            <div id="terminal-bar">
                <div class="dot" style="background:#FF5F56;"></div>
                <div class="dot" style="background:#FFBD2E;"></div>
                <div class="dot" style="background:#27C93F;"></div>
            </div>
            <div id="log-container">{log_html}</div>
            <script>
                var logDiv = document.getElementById("log-container");
                logDiv.scrollTop = logDiv.scrollHeight;
            </script>
        </body>
        </html>
        """
        with self.placeholder:
            components.html(html_content, height=400)


def standby_terminal():
    return """
    <div id="terminal-bar" style="background:#E2E8F0; border-radius:8px 8px 0 0; padding:7px 10px; display:flex; gap:6px;">
        <div style="width:10px;height:10px;border-radius:50%;background:#FF5F56;"></div>
        <div style="width:10px;height:10px;border-radius:50%;background:#FFBD2E;"></div>
        <div style="width:10px;height:10px;border-radius:50%;background:#27C93F;"></div>
    </div>
    <div style='height: 350px; background-color: #ffffff; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0; border-top: none;
                display: flex; align-items: center; justify-content: center; color: #94A3B8; font-family: monospace; font-size: 13px;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.03);'>
        ⏳ Waiting for process to start...
    </div>
    """


def stat_card(label, value):
    return f"""
    <div class="stat-card">
        <p class="label">{label}</p>
        <p class="value">{value}</p>
    </div>
    """


# --- Fungsi Bantuan untuk Generate SQL Dump ---
def generate_sql_insert(df, table_name):
    """Menghasilkan teks skrip SQL INSERT dari DataFrame."""
    sql_statements = [f"-- Data dump for table: {table_name}", ""]
    for _, row in df.iterrows():
        vals = []
        for val in row:
            if pd.isna(val):
                vals.append("NULL")
            elif isinstance(val, (int, float)):
                vals.append(str(val))
            else:
                safe_val = str(val).replace("'", "''")
                vals.append(f"'{safe_val}'")

        cols = ", ".join(df.columns)
        vals_str = ", ".join(vals)
        sql_statements.append(f"INSERT INTO {table_name} ({cols}) VALUES ({vals_str});")
    return "\n".join(sql_statements)


# ==========================================
# TAB UTAMA
# ==========================================
tab1, tab2, tab3 = st.tabs(["📥 1. Extract", "🔄 2. Transform", "📤 3. Load"])

# ==========================================
# TAB 1: EXTRACT
# ==========================================
with tab1:
    st.subheader("Data Extraction")

    col_left, col_right = st.columns([6, 4])

    with col_right:
        st.markdown("##### 📝 Process Logs")
        log_placeholder1 = st.empty()
        log_placeholder1.markdown(standby_terminal(), unsafe_allow_html=True)

    with col_left:
        st.write("Mengambil data mentah (raw data) dari website menggunakan **BeautifulSoup**.")
        if st.button("▶️ Run Extract Phase", type="primary", key="btn_ext", width='stretch'):
            st_handler = StreamlitLogHandler(log_placeholder1)
            st_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            logging.getLogger().addHandler(st_handler)

            with st.spinner("Scraping data from website..."):
                df_raw = scrape_main()
                st.session_state.extracted_data = df_raw
                st.session_state.transformed_data = None
                st.session_state.loaded = False

            logging.getLogger().removeHandler(st_handler)
            st.success("✅ Extraction Complete!")
            render_pipeline_status()

        if st.session_state.extracted_data is not None:
            df_raw = st.session_state.extracted_data
            st.markdown("###### Ringkasan Data Mentah")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(stat_card("Total Baris", f"{len(df_raw):,}"), unsafe_allow_html=True)
            with sc2:
                st.markdown(stat_card("Total Kolom", f"{df_raw.shape[1]}"), unsafe_allow_html=True)
            with sc3:
                st.markdown(stat_card("Baris Duplikat", f"{df_raw.duplicated().sum():,}"), unsafe_allow_html=True)

            st.markdown("")
            st.markdown("###### Raw Data Preview")
            st.dataframe(df_raw, width='stretch')

# ==========================================
# TAB 2: TRANSFORM
# ==========================================
with tab2:
    st.subheader("Data Transformation")

    col_left, col_right = st.columns([6, 4])

    with col_right:
        st.markdown("##### 📝 Process Logs")
        log_placeholder2 = st.empty()
        log_placeholder2.markdown(standby_terminal(), unsafe_allow_html=True)

    with col_left:
        st.write("Membersihkan data, mengonversi mata uang ke IDR, menangani nilai kosong "
                 "(*missing values*), dan menghapus duplikat.")

        if st.session_state.extracted_data is None:
            st.warning("⚠️ Silakan jalankan proses Extract di Tab 1 terlebih dahulu.")
        else:
            if st.button("▶️ Run Transform Phase", type="primary", key="btn_tf", width='stretch'):
                st_handler = StreamlitLogHandler(log_placeholder2)
                st_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
                logging.getLogger().addHandler(st_handler)

                with st.spinner("Cleaning and transforming data..."):
                    df_clean = transform_data(st.session_state.extracted_data.copy())
                    st.session_state.transformed_data = df_clean
                    st.session_state.loaded = False

                logging.getLogger().removeHandler(st_handler)
                st.success("✅ Transformation Complete!")
                render_pipeline_status()

            if st.session_state.transformed_data is not None:
                df_before = st.session_state.extracted_data
                df_after = st.session_state.transformed_data
                rows_removed = len(df_before) - len(df_after)
                pct_removed = (rows_removed / len(df_before) * 100) if len(df_before) else 0

                st.markdown("###### Ringkasan Pembersihan Data")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(stat_card("Baris Sebelum", f"{len(df_before):,}"), unsafe_allow_html=True)
                with m2:
                    st.markdown(stat_card("Baris Sesudah", f"{len(df_after):,}"), unsafe_allow_html=True)
                with m3:
                    st.markdown(stat_card("Baris Dihapus", f"{rows_removed:,} ({pct_removed:.1f}%)"), unsafe_allow_html=True)

                st.markdown("")
                st.markdown("###### Cleaned Data Preview")
                st.dataframe(df_after, width='stretch')

# ==========================================
# TAB 3: LOAD
# ==========================================
with tab3:
    st.subheader("Data Loading")

    col_left, col_right = st.columns([6, 4])

    with col_right:
        st.markdown("##### 📝 Process Logs")
        log_placeholder3 = st.empty()
        log_placeholder3.markdown(standby_terminal(), unsafe_allow_html=True)

    with col_left:
        st.write("Memuat data bersih ke **Cloud PostgreSQL** dan **Google Sheets**.")

        if st.session_state.transformed_data is None:
            st.warning("⚠️ Silakan jalankan proses Transform di Tab 2 terlebih dahulu.")
        else:
            if st.button("▶️ Run Load Phase", type="primary", key="btn_ld", width='stretch'):
                st_handler = StreamlitLogHandler(log_placeholder3)
                st_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
                logging.getLogger().addHandler(st_handler)

                with st.spinner("Uploading data to Cloud Database and Google Sheets..."):
                    success = load_data(st.session_state.transformed_data.copy())

                logging.getLogger().removeHandler(st_handler)
                st.session_state.loaded = bool(success)
                render_pipeline_status()

                if success:
                    st.success("✅ Data berhasil dimuat ke semua target destinasi!")
                    st.balloons()
                else:
                    st.error("❌ Terjadi kesalahan saat memuat data. Periksa log di atas.")

            if st.session_state.loaded:
                df_export = prepare_dataframe_for_export(st.session_state.transformed_data)

                st.markdown("###### Ringkasan Data Termuat")
                l1, l2 = st.columns(2)
                with l1:
                    st.markdown(stat_card("Total Baris Termuat", f"{len(df_export):,}"), unsafe_allow_html=True)
                with l2:
                    st.markdown(stat_card("Total Kolom", f"{df_export.shape[1]}"), unsafe_allow_html=True)

                st.markdown("")
                st.markdown("###### 🔗 Akses Hasil Data")

                dc1, dc2 = st.columns(2)
                with dc1:
                    csv_data = df_export.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Cleaned CSV",
                        data=csv_data,
                        file_name='products_cleaned.csv',
                        mime='text/csv',
                        width='stretch'
                    )
                with dc2:
                    db_table = os.getenv('DB_TABLE', 'productstoscrape')
                    sql_data = generate_sql_insert(df_export, db_table)
                    st.download_button(
                        label="💾 Download products.sql",
                        data=sql_data,
                        file_name='products.sql',
                        mime='application/sql',
                        width='stretch'
                    )

                gsheet_link = os.getenv('GSHEET_URL')
                if gsheet_link:
                    st.link_button("📊 Lihat Live di Google Sheets", url=gsheet_link, width='stretch')