import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import time

# --- KONFIGURASI HALAMAN WEB ---
st.set_page_config(page_title="Cek Tren YouTube", layout="wide")

st.title("📈 Analisis YouTube Search Trends")
st.markdown("Cek seberapa sering kata kunci dicari di YouTube dalam 24 jam terakhir.")

# --- SIDEBAR (INPUT) ---
st.sidebar.header("Konfigurasi")

# [FITUR BARU] Pesan Peringatan Penggunaan
st.sidebar.warning(
    "⚠️ **PENTING: Aturan Pakai**\n\n"
    "Google membatasi jumlah request.\n"
    "Mohon **beri jeda sekitar 1 menit** setelah menekan tombol 'Analisa Tren'.\n"
    "Jika terlalu cepat, Google akan memblokir sementara."
)

input_text = st.sidebar.text_area(
    "Masukkan Keyword (Max 5, pisah koma)", 
    "Jokowi, Prabowo, Banjarmasin"
)

btn_submit = st.sidebar.button("Analisa Tren 🚀")

# --- LOGIKA UTAMA ---
if btn_submit:
    # 1. Bersihkan Input User
    kw_list = [x.strip() for x in input_text.split(',')]
    
    # Validasi jumlah keyword
    if len(kw_list) > 5:
        st.error("⚠️ Maksimal 5 kata kunci sekaligus agar tidak error.")
    elif len(kw_list) == 0 or kw_list == ['']:
        st.error("⚠️ Kata kunci tidak boleh kosong.")
    else:
        with st.spinner('Sedang menghubungi Google Trends... Mohon tunggu...'):
            try:
                # 2. Request Data
                # Menambahkan timeout agar tidak hanging
                pytrends = TrendReq(hl='id-ID', tz=420, timeout=(10,25))
                
                pytrends.build_payload(
                    kw_list, 
                    cat=0, 
                    timeframe='now 1-d', 
                    geo='ID', 
                    gprop='youtube'
                )
                
                data = pytrends.interest_over_time()

                if not data.empty:
                    if 'isPartial' in data.columns:
                        data = data.drop(columns=['isPartial'])
                        
                    if data.index.tz is None:
                        data.index = data.index.tz_localize('UTC')
                    data.index = data.index.tz_convert('Asia/Jakarta')
                    tabel_view = data.copy()
                    tabel_view.index = tabel_view.index.strftime('%d-%m %H:%M')
                    
                    # 3. Tampilkan Grafik
                    st.subheader("📊 Grafik Minat (24 Jam Terakhir)")
                    st.line_chart(data)

                    # 4. Statistik Rata-rata
                    st.subheader("🏆 Skor Popularitas (0-100)")
                    mean_scores = data.mean().sort_values(ascending=False)
                    
                    cols = st.columns(len(kw_list))
                    for idx, (kw, score) in enumerate(mean_scores.items()):
                        with cols[idx]:
                            st.metric(label=kw, value=f"{score:.1f}")

                    # 5. Data Mentah
                    with st.expander("Lihat Data Tabel"):
                        st.dataframe(data)
                    
                    # [FITUR BARU] Pesan Sukses & Reminder Jeda
                    st.success("✅ Data berhasil diambil!")
                    st.info("⏳ Mohon tunggu minimal **1 menit** sebelum melakukan pencarian baru agar IP tidak diblokir.")

                else:
                    st.warning("Data kosong. Kata kunci mungkin terlalu spesifik/jarang dicari.")

            except Exception as e:
                # [FITUR BARU] Deteksi Error Spesifik (429 Too Many Requests)
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("⛔ **TERLALU BANYAK REQUEST!**")
                    st.write("Google memblokir sementara karena tombol ditekan terlalu sering. Mohon tunggu **5-10 menit** sebelum mencoba lagi.")
                else:
                    st.error(f"Terjadi Kesalahan: {error_msg}")
else:
    st.info("👈 Masukkan kata kunci di sidebar kiri, baca peringatan jeda, lalu klik tombol. oke")