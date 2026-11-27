# ============================================================
# DASHBOARD PERAMALAN GANGGUAN KABEL SR - PLN UP3 SERPONG
# Metode: ARIMA(1,1,1) | Kerangka: CRISP-DM
# Data: Januari - Desember 2025 (365 hari)
# ============================================================
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import base64, os
import holidays as hol
from datetime import datetime
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Dashboard Gangguan Kabel SR - PLN",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. PALET WARNA (Tema SalesPulse - Glassmorphism)
# ============================================================
NAVY   = "#1A1A1A"                 # Teks utama (hampir hitam)
BIRU   = "#7C6BFA"                 # Periwinkle/Ungu aksen utama
TOSKA  = "#A29BFE"                 # Ungu terang (garis data)
KUNING = "#F5A524"                 # Oranye terang (sorotan)
ORANYE = "#F08A1C"                 # Oranye (prediksi)
MERAH  = "#E5484D"
HIJAU  = "#2E9E5B"                 # Hijau untuk indikator positif
ABU    = "#76767C"
GARIS  = "rgba(0,0,0,.05)"

# Kartu Glassmorphism
KARTU_BG = "rgba(255, 255, 255, 0.65)"
KARTU = (f"background: {KARTU_BG}; backdrop-filter: blur(24px); "
         "-webkit-backdrop-filter: blur(24px); border: 1px solid rgba(255, 255, 255, 0.8); "
         "box-shadow: 0 4px 20px rgba(0,0,0,.03);")

# ============================================================
# 3. CSS KUSTOM (Meniru Layout SalesPulse)
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {{ font-family:'Inter', sans-serif; }}
span[data-testid="stIconMaterial"] {{ font-family:'Material Symbols Rounded' !important; }}

/* Background Gradasi Mesh */
.stApp {{
    background-color: #E8F0EC;
    background-image: 
        radial-gradient(at 0% 0%, rgba(124, 107, 250, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(46, 158, 91, 0.1) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(232, 240, 236, 1) 0px, transparent 50%),
        radial-gradient(at 0% 100%, rgba(232, 240, 236, 1) 0px, transparent 50%);
}}

/* Sembunyikan elemen bawaan Streamlit */
#MainMenu, footer {{ visibility:hidden; }}
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stAppDeployButton,
[class*="viewerBadge"] {{ display:none !important; }}
header[data-testid="stHeader"] {{ background:transparent; height:2.5rem; }}

.block-container {{
    padding-top: 2rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100%;
}}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {{
    background: #F4F7F6; /* Sidebar terang seperti referensi */
    border-right: 1px solid rgba(0,0,0,0.05);
    width: 260px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{ padding-top: 0 !important; }}
[data-testid="stSidebarHeader"] {{ height: 3rem; min-height: 0; padding: .5rem 1rem 0; }}
[data-testid="stSidebarUserContent"] {{ padding: 0 1rem 1.5rem !important; }}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 6px; }}

/* Tombol Sidebar */
section[data-testid="stSidebar"] button {{
    border-radius: 12px !important;
    padding: 0 16px !important;
    height: 42px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: all 0.2s ease;
}}
section[data-testid="stSidebar"] button > div {{
    width: 100% !important;
    display: flex !important;
    justify-content: flex-start !important;
}}
section[data-testid="stSidebar"] button p {{
    font-size: 13.5px !important;
    margin: 0 !important;
    color: inherit !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background: transparent !important;
    color: #5C5F62 !important;
    border: none !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background: rgba(0,0,0,0.04) !important;
    color: #1A1A1A !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] {{
    background: #FFFFFF !important;
    color: #1A1A1A !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] p {{ font-weight: 600 !important; }}

/* Selectbox Sidebar */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 12px !important;
    min-height: 40px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] * {{
    color: #1A1A1A !important;
    font-size: 12.5px !important;
}}

/* ---------- Kartu KPI (Mirip SalesPulse) ---------- */
[data-testid="stMetric"] {{
    {KARTU}
    border-radius: 20px;
    padding: 24px;
}}
[data-testid="stMetricLabel"] p {{
    color: {ABU} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin-bottom: 8px;
}}
[data-testid="stMetricValue"] {{
    color: {NAVY} !important;
    font-size: 36px !important;
    font-weight: 500 !important;
    letter-spacing: -1px;
    line-height: 1.1;
}}
[data-testid="stMetricDelta"] {{
    background: transparent !important;
    padding: 0 !important;
    font-size: 12px !important;
    margin-top: 8px;
}}
[data-testid="stMetricDelta"] * {{
    color: {HIJAU} !important; /* Teks hijau untuk delta */
    background: transparent !important;
    font-weight: 500;
}}
[data-testid="stMetricDelta"] svg {{ display: none; }}

/* ---------- Grafik & Tabel ---------- */
[data-testid="stPlotlyChart"] {{
    {KARTU}
    border-radius: 20px;
    padding: 16px;
}}
[data-testid="stDataFrame"] {{
    {KARTU}
    border-radius: 20px;
    padding: 12px;
    overflow: hidden;
}}

/* ---------- Tombol Area Utama ---------- */
.main button {{
    border-radius: 20px !important;
    height: 40px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}}
.main button[kind="secondary"] {{
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    color: {NAVY} !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
}}
.main button[kind="secondary"]:hover {{
    background: #F8F9FA !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}}
.main button[kind="primary"] {{
    background: {NAVY} !important; /* Tombol hitam pekat seperti referensi */
    border: none !important;
    color: #FFFFFF !important;
}}
.main button[kind="primary"]:hover {{
    background: #333333 !important;
    transform: translateY(-1px);
}}
.main [data-testid="stDownloadButton"] button {{
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    color: {NAVY} !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
}}

/* ---------- Input & Uploader ---------- */
.main [data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 12px !important;
    min-height: 44px;
}}
[data-testid="stFileUploader"] section {{
    background: rgba(255,255,255,0.6) !important;
    border: 1px dashed rgba(0,0,0,0.15) !important;
    border-radius: 16px !important;
}}
[data-testid="stExpander"] {{
    background: rgba(255,255,255,0.6);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 16px;
}}
[data-testid="stAlert"] {{ border-radius: 12px; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. PEMUATAN DATA
# ============================================================
@st.cache_data
def load_data():
    xl = pd.ExcelFile('ARIMA_PLN_PowerBI.xlsx')
    return (
        pd.read_excel(xl, sheet_name='Historis'),
        pd.read_excel(xl, sheet_name='Metrik'),
        pd.read_excel(xl, sheet_name='Peramalan'),
        pd.read_excel(xl, sheet_name='Penyebab'),
        pd.read_excel(xl, sheet_name='Sumber'),
    )

hist, metrik, peramalan, penyebab, sumber = load_data()

# ============================================================
# 5. SESSION STATE
# ============================================================
if 'halaman' not in st.session_state:
    st.session_state.halaman = 'Ringkasan'
if 'model_terpilih' not in st.session_state:
    st.session_state.model_terpilih = 'ARIMA Dasar'
if 'hasil_ramalan_baru' not in st.session_state:
    st.session_state.hasil_ramalan_baru = None
if 'ts_baru_terakhir' not in st.session_state:
    st.session_state.ts_baru_terakhir = None
if 'info_model_baru' not in st.session_state:
    st.session_state.info_model_baru = None

# ============================================================
# 6. SIDEBAR
# ============================================================
with st.sidebar:
    # Logo
    if os.path.exists('logo_haleyora.png'):
        with open('logo_haleyora.png', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="padding:10px 0 20px;text-align:left;">'
            f'<img src="data:image/png;base64,{b64}" style="width:120px;">'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="padding:10px 0 20px;text-align:left;">'
            '<span style="color:#1A1A1A;font-size:16px;font-weight:700;">'
            'haleyora</span><span style="color:#F5A524;font-size:16px;'
            'font-weight:700;">power</span></div>', unsafe_allow_html=True)

    # Judul
    st.markdown(
        '<div style="padding:0 0 16px;">'
        '<div style="color:#1A1A1A;font-size:14px;font-weight:600;'
        'line-height:1.4;">Gangguan Kabel SR</div>'
        '<div style="color:#76767C;font-size:11px;margin-top:2px;">'
        'Peramalan ARIMA &amp; SARIMAX</div></div>', unsafe_allow_html=True)

    # Label Navigasi
    st.markdown(
        '<div style="color:#8D8D93;font-size:10px;letter-spacing:1px;'
        'font-weight:600;padding:0 0 8px;">MENU UTAMA</div>', unsafe_allow_html=True)

    # Menu Navigasi
    for nama in ["Ringkasan", "Tren Harian", "Peramalan",
                 "Perbarui & Ramalkan", "Analisis Penyebab",
                 "Perbandingan Model", "Akurasi Model"]:
        aktif = st.session_state.halaman == nama
        if st.button(nama, key=f"menu_{nama}", use_container_width=True,
                     type="primary" if aktif else "secondary"):
            st.session_state.halaman = nama
            st.rerun()

    # Label Filter
    st.markdown(
        '<div style="color:#8D8D93;font-size:10px;letter-spacing:1px;'
        'font-weight:600;padding:24px 0 8px;">PILIH PERIODE</div>',
        unsafe_allow_html=True)

    # Dropdown Filter
    with st.container():
        opsi = ['Semua'] + list(
            pd.to_datetime(hist.iloc[:, 0]).dt.strftime('%b %Y').unique())
        pilih_bulan = st.selectbox("p", opsi, label_visibility="collapsed")

    # Status Model
    st.markdown(
        '<div style="margin-top:24px;padding-top:16px;'
        'border-top:1px solid rgba(0,0,0,0.08);">'
        '<div style="background:#FFFFFF;border:1px solid rgba(0,0,0,0.05);'
        'border-radius:16px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.02);">'
        '<div style="display:flex;align-items:center;gap:8px;'
        'margin-bottom:8px;">'
        '<div style="width:8px;height:8px;border-radius:50%;'
        'background:#2E9E5B;"></div>'
        '<span style="color:#2E9E5B;font-size:11px;font-weight:600;">'
        'Model Tervalidasi</span></div>'
        '<div style="color:#76767C;font-size:11px;line-height:1.8;">'
        'Ljung-Box p &gt; 0,05<br>ARIMA(1,1,1)<br>MASE 1,548<br>'
        'Belum unggul dari naive</div>'
        '</div></div>', unsafe_allow_html=True)

# ============================================================
# 7. HEADER
# ============================================================
hist_f = hist.copy()
hist_f.iloc[:, 0] = pd.to_datetime(hist_f.iloc[:, 0])
if pilih_bulan != 'Semua':
    hist_f = hist_f[hist_f.iloc[:, 0].dt.strftime('%b %Y') == pilih_bulan]

kol_tgl, kol_val = hist_f.columns[0], hist_f.columns[1]

kiri, kanan = st.columns([7, 3])
with kiri:
    st.markdown(
        f'<div style="color:{NAVY};font-size:28px;font-weight:600;'
        f'line-height:1.2;letter-spacing:-.5px;">'
        f'Dashboard Peramalan Gangguan Kabel SR</div>'
        f'<div style="color:{ABU};font-size:13px;margin-top:6px;">'
        f'PT. Haleyora Power Serpong &nbsp;&nbsp; Metode ARIMA &amp; SARIMAX '
        f'Berbasis Time Series &nbsp;&nbsp; '
        f'<span style="background:#FFFFFF;color:{NAVY};border:1px solid rgba(0,0,0,0.05);'
        f'box-shadow:0 2px 6px rgba(0,0,0,0.02);font-weight:500;padding:4px 12px;border-radius:20px;">'
        f'{pilih_bulan}</span>'
        f'</div>', unsafe_allow_html=True)

with kanan:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    with t1:
        if st.button("Muat Ulang", key="reload", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with t2:
        st.download_button(
            "Unduh Data", key="unduh",
            data=hist_f.to_csv(index=False).encode('utf-8'),
            file_name=f"gangguan_SR_{datetime.now():%Y%m%d}.csv",
            mime="text/csv", use_container_width=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ============================================================
# 8. HELPER FUNCTIONS
# ============================================================
TRANSPARAN = 'rgba(0,0,0,0)'

def tata(t=280):
    return dict(
        plot_bgcolor=TRANSPARAN, paper_bgcolor=TRANSPARAN,
        font=dict(color=ABU, size=11, family='Inter,sans-serif'),
        height=t, margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=ABU),
                   linecolor=GARIS, showline=True),
        yaxis=dict(gridcolor=GARIS, tickfont=dict(size=11, color=ABU),
                   zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, x=0,
                    font=dict(size=11, color=ABU), bgcolor=TRANSPARAN),
        hoverlabel=dict(bgcolor=NAVY, font=dict(color='white', size=12))
    )

def judul(teks, sub=""):
    baris = (f'<div style="color:{ABU};font-size:12px;margin-top:4px;">'
             f'{sub}</div>') if sub else ''
    st.markdown(
        f'<div style="margin:0 0 16px;">'
        f'<div style="color:{NAVY};font-size:16px;font-weight:600;'
        f'letter-spacing:-.2px;">'
        f'{teks}</div>{baris}</div>',
        unsafe_allow_html=True)

# ============================================================
# 9. KPI CARDS
# ============================================================
def kpi():
    k1, k2, k3, k4 = st.columns(4)
    total = f"{int(hist_f[kol_val].sum()):,}".replace(",", ".")
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    mase = float(baris_terbaik['MASE'])
    
    with k1:
        st.metric("Total Gangguan", total, "kasus tercatat ↗")
    with k2:
        st.metric("Rata-rata Harian",
                  f"{hist_f[kol_val].mean():.2f}".replace(".", ","),
                  "gangguan / hari ↗")
    with k3:
        st.metric("Akurasi MASE", f"{mase:.3f}".replace(".", ","),
                  "belum unggul dari naive")
    with k4:
        st.metric("Proyeksi 30 Hari",
                  f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","),
                  "kategori sedang ↗")

# ============================================================
# 10. FUNGSI GRAFIK (Diperhalus ala SalesPulse)
# ============================================================
def g_tren(t=320):
    f = go.Figure()
    
    # Area chart untuk aktual (gradasi ungu muda)
    f.add_trace(go.Scatter(
        x=hist_f[kol_tgl], y=hist_f[kol_val], name='Aktual',
        line=dict(color=TOSKA, width=2.5, shape='spline'),
        fill='tozeroy', fillcolor='rgba(124, 107, 250, 0.1)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y} gangguan<extra></extra>'))
    
    # Garis putus-putus untuk prediksi
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'],
        name='Prediksi ARIMA(1,1,1)',
        line=dict(color=ORANYE, width=2.5, dash='dot', shape='spline'),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y:.1f}<extra></extra>'))
    
    f.update_layout(**tata(t))
    return f

def g_penyebab(t=320):
    d = penyebab.head(5).copy()
    d['Lengkap'] = d['Penyebab'].astype(str)
    d['Penyebab'] = d['Lengkap'].apply(
        lambda x: x if len(x) <= 22 else x[:20] + '…')
        
    # Menggunakan palet warna ungu/neutral
    f = px.pie(d, values='Jumlah', names='Penyebab', hole=.65,
               custom_data=['Lengkap'],
               color_discrete_sequence=['#7C6BFA', '#A29BFE', '#D1CCFF', '#E5E1FF', '#F4F4F5'])
    f.update_traces(
        textposition='inside', textinfo='percent',
        textfont=dict(size=11, color='white', weight='bold'),
        hovertemplate='<b>%{customdata[0]}</b><br>%{value:,}<extra></extra>',
        marker=dict(line=dict(color='#FFFFFF', width=3)))
    f.update_layout(
        paper_bgcolor=TRANSPARAN, height=t,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color=ABU, family='Inter,sans-serif'),
        legend=dict(orientation='h', yanchor='top', y=-0.05,
                    xanchor='left', x=0, font=dict(size=11, color=ABU),
                    bgcolor=TRANSPARAN),
        hoverlabel=dict(bgcolor=NAVY, font=dict(color='white')))
    return f

def g_ramal(t=250):
    f = go.Figure()
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['CI_Atas'],
        mode='lines', line=dict(color='rgba(0,0,0,0)'),
        showlegend=False, hoverinfo='skip'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['CI_Bawah'],
        fill='tonexty', mode='lines',
        fillcolor='rgba(124, 107, 250, 0.15)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Interval 95%', hoverinfo='skip'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'],
        name='Prediksi',
        line=dict(color=BIRU, width=2.5, shape='spline'),
        hovertemplate='<b>%{x|%d %b}</b><br>%{y:.1f}<extra></extra>'))
    L = tata(t)
    L['yaxis']['range'] = [0, 55]
    f.update_layout(**L)
    return f

def g_bulan(t=300):
    h = hist.copy()
    h.iloc[:, 0] = pd.to_datetime(h.iloc[:, 0])
    h['Bulan'] = h.iloc[:, 0].dt.strftime('%b %Y')
    b = h.groupby('Bulan', sort=False)[h.columns[1]].sum().reset_index()
    b.columns = ['Bulan', 'Jumlah']
    mx = b['Jumlah'].max()
    
    # Batang berwarna putih keperakan dengan ujung membulat (jika didukung)
    warna = []
    for i, v in enumerate(b['Jumlah']):
        if i == len(b['Jumlah']) - 1:
            warna.append(BIRU) # Bar terakhir ungu penuh
        else:
            warna.append('rgba(124, 107, 250, 0.2)') # Bar lain ungu pudar
            
    teks = [f"{v:,}".replace(",", ".") for v in b['Jumlah']]
    kw = dict(
        x=b['Bulan'], y=b['Jumlah'], text=teks, textposition='outside',
        textfont=dict(size=10, color=NAVY), cliponaxis=False,
        hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>')
    try:
        f = go.Figure(go.Bar(**kw, marker=dict(
            color=warna, cornerradius=6,
            line=dict(color='rgba(0,0,0,0)', width=0))))
    except Exception:
        f = go.Figure(go.Bar(**kw, marker=dict(
            color=warna, line=dict(color='rgba(0,0,0,0)', width=0))))
    L = tata(t)
    L['xaxis'].update(tickangle=0, tickfont=dict(size=11, color=ABU))
    L['yaxis'].update(range=[0, mx * 1.2])
    f.update_layout(**L)
    return f

def b_sumber():
    total_s = sumber['Jumlah'].sum()
    warna = [BIRU, TOSKA, KUNING, MERAH, '#A8A8AE', '#76767C']
    html = ""
    for i, (_, r) in enumerate(sumber.head(6).iterrows()):
        pct = r['Jumlah'] / total_s * 100
        jml = f"{r['Jumlah']:,}".replace(",", ".")
        nama = str(r['Sumber_Lapor'])[:22]
        html += (
            f'<div style="margin-bottom:18px;">'
            f'<div style="display:flex;justify-content:space-between;'
            f'margin-bottom:6px;">'
            f'<span style="color:{NAVY};font-size:12px;font-weight:500;">{nama}</span>'
            f'<span style="color:{ABU};font-size:11px;font-weight:600;">'
            f'{jml} <span style="font-weight:400;">({pct:.1f}%)</span></span></div>'
            f'<div style="background:rgba(0,0,0,.04);border-radius:6px;height:8px;">'
            f'<div style="background:{BIRU};height:8px;'
            f'border-radius:6px;width:{min(pct, 100):.1f}%;"></div>'
            f'</div></div>')
    return html

def t_metrik():
    def sorot(x):
        return [
            f'background-color:#DCFCE7;color:{HIJAU};font-weight:700'
            if v == x.min() else
            f'color:{MERAH};font-weight:600' if v == x.max() else ''
            for v in x
        ]
    st.dataframe(
        metrik.style.apply(sorot, subset=['MASE']).format({
            'MAE': '{:.2f}', 'RMSE': '{:.2f}', 'sMAPE(%)': '{:.2f}%',
            'R2': '{:.4f}', 'MASE': '{:.3f}'}),
        use_container_width=True, hide_index=True)

def catatan():
    st.markdown(
        f'<div style="{KARTU}border-left:4px solid {BIRU};'
        f'border-radius:8px 20px 20px 8px;'
        f'padding:20px 24px;margin-top:16px;">'
        f'<div style="color:{NAVY};font-size:14px;font-weight:600;'
        f'margin-bottom:8px;">Interpretasi Hasil</div>'
        f'<div style="color:{ABU};font-size:12.5px;line-height:1.8;">'
        f'Model ARIMA(1,1,1) menghasilkan MASE 1,548. Nilai ini belum '
        f'mengungguli baseline naive (1,527) maupun mean (1,528), dengan '
        f'selisih sangat tipis hanya 0,021 pada skala MASE. Penambahan '
        f'variabel eksogen kalender pada SARIMAX tidak memperbaiki akurasi; '
        f'MASE justru meningkat menjadi 1,653 (kalender dasar) dan 1,670 '
        f'(kalender lengkap). Residual model tetap white noise (p &gt; 0,05 '
        f'pada lag 7, 14, dan 21), sehingga keterbatasan akurasi berasal '
        f'dari sifat data yang overdispersed (rasio 4,60) dan dipengaruhi '
        f'faktor eksogen fisik di luar dataset seperti kondisi cuaca, '
        f'bukan dari kesalahan spesifikasi model.'
        f'</div></div>', unsafe_allow_html=True)

# ============================================================
# 11. SIMULASI SKENARIO
# ============================================================
def simulasi_skenario():
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Simulasi Skenario Faktor Eksternal",
          "Ilustrasi dampak faktor eksogen tambahan di luar model")
    st.markdown(
        f'<div style="{KARTU}border-left:4px solid {BIRU};'
        f'border-radius:8px 20px 20px 8px;'
        f'padding:16px 20px;margin-bottom:20px;">'
        f'<div style="color:{ABU};font-size:12.5px;line-height:1.7;">'
        f'Model ARIMA sudah menangkap pola historis murni dari data. '
        f'Simulasi ini menggeser hasil prediksi secara proporsional untuk '
        f'mengilustrasikan potensi dampak faktor cuaca yang belum '
        f'dimodelkan, bukan hasil pemodelan baru.</div></div>',
        unsafe_allow_html=True)

    skenario = st.select_slider(
        "Skenario Faktor Eksternal",
        options=["Musim Kering (-30%)", "Normal (0%)",
                 "Musim Hujan (+20%)", "Cuaca Ekstrem (+50%)"],
        value="Normal (0%)")

    faktor = {
        "Musim Kering (-30%)": -0.30, "Normal (0%)": 0.0,
        "Musim Hujan (+20%)": 0.20, "Cuaca Ekstrem (+50%)": 0.50
    }[skenario]

    df_sim = peramalan.copy()
    df_sim['Prediksi_Sim'] = (df_sim['Prediksi'] * (1 + faktor)).clip(lower=0)

    f = go.Figure()
    f.add_trace(go.Scatter(
        x=df_sim['Tanggal'], y=df_sim['Prediksi'],
        name='Prediksi ARIMA(1,1,1) (asli)',
        line=dict(color=ABU, width=2, dash='dot', shape='spline')))
    f.add_trace(go.Scatter(
        x=df_sim['Tanggal'], y=df_sim['Prediksi_Sim'],
        name=f'Simulasi: {skenario}',
        line=dict(color=BIRU, width=2.5, shape='spline'),
        fill='tonexty', fillcolor='rgba(124, 107, 250, 0.1)'))
    f.update_layout(**tata(300))
    st.plotly_chart(f, use_container_width=True)

    selisih = df_sim['Prediksi_Sim'].mean() - df_sim['Prediksi'].mean()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Rata-rata Prediksi Asli",
                  f"{df_sim['Prediksi'].mean():.1f}", "gangguan/hari")
    with c2:
        st.metric("Rata-rata Skenario",
                  f"{df_sim['Prediksi_Sim'].mean():.1f}",
                  f"{'+' if selisih >= 0 else ''}{selisih:.1f} vs asli ↗")

# ============================================================
# 12. GRAFIK PROGRES OPTIMASI
# ============================================================
def g_progres_optimasi():
    df_prog = metrik[~metrik['Model'].str.contains(
        'baseline', case=False, na=False)].copy()
    
    # Warna batang: ungu pudar, batang terakhir ungu penuh
    warna_bar = ['rgba(124, 107, 250, 0.2)'] * (len(df_prog) - 1) + [BIRU]
    
    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['MASE'],
        marker_color=warna_bar,
        text=df_prog['MASE'].round(3),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>MASE: %{y:.3f}<extra></extra>'))
    f.add_hline(y=1.0, line_dash='dot', line_color=MERAH,
                annotation_text='Ambang unggul dari naive (MASE=1,0)',
                annotation_font_size=10, annotation_font_color=MERAH)
    L = tata(320)
    L['yaxis']['title'] = 'MASE'
    L['xaxis']['tickfont'] = dict(size=10, color=ABU)
    f.update_layout(**L)
    return f

def g_progres_r2():
    df_prog = metrik[~metrik['Model'].str.contains(
        'baseline', case=False, na=False)].copy()
    
    # Batang berwarna abu-abu netral
    warna_bar = ['#E5E1FF' if v >= 0 else '#FFE5E5' for v in df_prog['R2']]
    
    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['R2'],
        marker_color=warna_bar,
        text=df_prog['R2'].round(4),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>R2: %{y:.4f}<extra></extra>'))
    f.add_hline(y=0, line_dash='dot', line_color=ABU)
    L = tata(320)
    L['yaxis']['title'] = 'R2'
    L['xaxis']['tickfont'] = dict(size=10, color=ABU)
    f.update_layout(**L)
    return f

# ============================================================
# 13. KARTU TOGGLE PERBANDINGAN MODEL
# ============================================================
def kartu_model_toggle():
    opsi_model = {
        'ARIMA Dasar': {
            'nama_metrik': 'ARIMA(1, 1, 1)',
            'deskripsi': 'Model univariat terbaik berdasarkan AIC. '
                         'Residual white noise, tetapi MASE masih di atas '
                         '1,0 sehingga belum mengungguli baseline naive.',
            'warna': ABU
        },
        'SARIMAX Kalender Dasar': {
            'nama_metrik': 'SARIMAX(1, 1, 1) + kalender dasar',
            'deskripsi': 'Penambahan variabel kalender (akhir pekan, '
                         'awal/akhir bulan). Tidak meningkatkan akurasi; '
                         'MASE justru lebih tinggi dari ARIMA.',
            'warna': BIRU
        },
        'SARIMAX Kalender Lengkap': {
            'nama_metrik': 'SARIMAX(1, 1, 2) + kalender lengkap',
            'deskripsi': 'Order dioptimasi ulang + fitur hari libur '
                         'nasional. Hasil terburuk; indikasi overfitting '
                         'terhadap pola kalender.',
            'warna': ORANYE
        }
    }

    cols = st.columns(3)
    for i, nama_opsi in enumerate(opsi_model.keys()):
        aktif = st.session_state.model_terpilih == nama_opsi
        with cols[i]:
            if st.button(nama_opsi, key=f"toggle_{nama_opsi}",
                         use_container_width=True,
                         type="primary" if aktif else "secondary"):
                st.session_state.model_terpilih = nama_opsi
                st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    pilihan = opsi_model[st.session_state.model_terpilih]
    baris = metrik[metrik['Model'] == pilihan['nama_metrik']]

    if baris.empty:
        st.warning(
            f"Data untuk model '{pilihan['nama_metrik']}' belum ditemukan "
            f"pada sheet Metrik. Pastikan nama model di Excel sama persis.")
        return

    m = baris.iloc[0]
    st.markdown(
        f'<div style="{KARTU}border:2px solid {pilihan["warna"]};'
        f'border-radius:20px;padding:24px;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">'
        f'<span style="color:{NAVY};font-size:16px;font-weight:600;">'
        f'{st.session_state.model_terpilih}</span>'
        f'<span style="background:{pilihan["warna"]}22;color:{pilihan["warna"]};'
        f'padding:6px 14px;border-radius:20px;font-size:11px;font-weight:600;">'
        f'{pilihan["nama_metrik"]}</span></div>'
        f'<div style="color:{ABU};font-size:13px;line-height:1.7;">'
        f'{pilihan["deskripsi"]}</div></div>',
        unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("MAE", f"{m['MAE']:.2f}".replace(".", ","))
    with k2:
        st.metric("RMSE", f"{m['RMSE']:.2f}".replace(".", ","))
    with k3:
        st.metric("sMAPE", f"{m['sMAPE(%)']:.2f}%".replace(".", ","))
    with k4:
        st.metric("R2", f"{m['R2']:.4f}".replace(".", ","))
    with k5:
        st.metric("MASE", f"{m['MASE']:.3f}".replace(".", ","))

# ============================================================
# 14. PERAMALAN BERGULIR
# ============================================================
def proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru,
                        jumlah_hari=30, order_model=(1, 1, 1)):
    kerja = df_baru.copy()
    kerja[kol_tgl_baru] = pd.to_datetime(kerja[kol_tgl_baru], errors='coerce')
    kerja = kerja.dropna(subset=[kol_tgl_baru])

    if kerja[kol_val_baru].dtype == object:
        agregasi = kerja.groupby(kerja[kol_tgl_baru].dt.normalize()).size()
        ts_baru = agregasi.rename('jumlah')
    else:
        ts_baru = kerja.set_index(kol_tgl_baru)[kol_val_baru]

    ts_baru = ts_baru.asfreq('D').interpolate(method='linear').round()

    def buat_exog(index_tanggal):
        exog = pd.DataFrame(index=index_tanggal)
        exog['is_weekend'] = (index_tanggal.dayofweek >= 5).astype(int)
        exog['is_month_start'] = (index_tanggal.day <= 3).astype(int)
        exog['is_month_end'] = (index_tanggal.day >= 28).astype(int)
        exog['day_of_week'] = index_tanggal.dayofweek
        tahun_terlibat = sorted(set(index_tanggal.year))
        id_hol = hol.Indonesia(years=tahun_terlibat)
        exog['is_holiday'] = [1 if d in id_hol else 0
                              for d in index_tanggal.date]
        return exog

    exog_baru = buat_exog(ts_baru.index)
    model_baru = SARIMAX(
        ts_baru, exog=exog_baru, order=order_model,
        enforce_stationarity=False, enforce_invertibility=False
    ).fit(disp=False, maxiter=1000, method='powell')

    idx_depan = pd.date_range(
        ts_baru.index[-1] + pd.Timedelta(days=1),
        periods=jumlah_hari, freq='D')
    exog_depan = buat_exog(idx_depan)

    fc_baru = model_baru.get_forecast(steps=jumlah_hari, exog=exog_depan)
    ci = fc_baru.conf_int()

    hasil_baru = pd.DataFrame({
        'Tanggal': idx_depan,
        'Prediksi': fc_baru.predicted_mean.clip(lower=0).round(2).values,
        'CI_Bawah': ci.iloc[:, 0].clip(lower=0).round(2).values,
        'CI_Atas': ci.iloc[:, 1].clip(lower=0).round(2).values,
    })

    return {'ts_baru': ts_baru, 'hasil': hasil_baru,
            'order': order_model, 'aic': model_baru.aic}

def halaman_perbarui_ramalkan():
    st.markdown(
        f'<div style="{KARTU}border-left:4px solid {BIRU};'
        f'border-radius:8px 20px 20px 8px;'
        f'padding:20px 24px;margin-bottom:24px;">'
        f'<div style="color:{NAVY};font-size:14px;font-weight:600;'
        f'margin-bottom:8px;">Peramalan Bergulir (Rolling Forecast)</div>'
        f'<div style="color:{ABU};font-size:12.5px;line-height:1.8;">'
        f'Fitur ini memungkinkan sistem melatih ulang model SARIMAX '
        f'secara otomatis menggunakan data gangguan terbaru yang diunggah, '
        f'kemudian menghasilkan peramalan dari titik data paling akhir. '
        f'Dengan mekanisme ini, dashboard dapat digunakan untuk meramalkan '
        f'periode berikutnya kapan pun data baru tersedia, tanpa perlu '
        f'mengubah kode program.</div></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="{KARTU}'
        f'border-radius:20px;padding:20px 24px;margin-bottom:24px;">'
        f'<div style="color:{NAVY};font-size:14px;font-weight:600;'
        f'margin-bottom:12px;">Panduan Rentang Peramalan</div>'
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        f'<div style="flex:1;min-width:220px;background:#F0FDF4;'
        f'border-radius:12px;padding:12px 16px;">'
        f'<span style="color:{HIJAU};font-size:12px;font-weight:600;">'
        f'7-42 HARI — DISARANKAN</span>'
        f'<div style="color:#166534;font-size:11px;line-height:1.6;'
        f'margin-top:4px;">Interval kepercayaan masih wajar.</div></div>'
        f'<div style="flex:1;min-width:220px;background:#FFFFEB;'
        f'border-radius:12px;padding:12px 16px;">'
        f'<span style="color:#92400E;font-size:12px;font-weight:600;">'
        f'43-120 HARI — HANYA ILUSTRASI</span>'
        f'<div style="color:#92400E;font-size:11px;line-height:1.6;'
        f'margin-top:4px;">Interval melebar signifikan.</div></div>'
        f'</div></div>', unsafe_allow_html=True)

    file_baru = st.file_uploader(
        "Unggah berkas data gangguan (XLSX / CSV)",
        type=['xlsx', 'csv'], key="upload_ramalan")

    if file_baru is not None:
        try:
            if file_baru.name.lower().endswith('.csv'):
                df_baru = pd.read_csv(file_baru)
            else:
                df_baru = pd.read_excel(file_baru)

            st.success(f"Berkas berhasil dimuat - {len(df_baru):,} baris, "
                       f"{df_baru.shape[1]} kolom")

            with st.expander("Pratinjau data yang diunggah", expanded=False):
                st.dataframe(df_baru.head(10), use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                kol_tgl_baru = st.selectbox(
                    "Kolom tanggal", df_baru.columns, key="pilih_kol_tgl")
            with c2:
                kol_val_baru = st.selectbox(
                    "Kolom jumlah gangguan",
                    df_baru.columns, key="pilih_kol_val")

            st.markdown("<div style='height:12px'></div>",
                        unsafe_allow_html=True)

            jumlah_hari = st.slider(
                "Jumlah hari yang diramalkan ke depan",
                min_value=7, max_value=120, value=30, step=7)

            if jumlah_hari <= 42:
                st.markdown(
                    f'<div style="background:#DCFCE7;border-radius:12px;'
                    f'padding:10px 16px;margin-top:8px;margin-bottom:8px;">'
                    f'<span style="color:#166534;font-size:12px;'
                    f'font-weight:500;">Dalam rentang disarankan.</span>'
                    f'</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="background:#FEF3C7;border-radius:12px;'
                    f'padding:10px 16px;margin-top:8px;margin-bottom:8px;">'
                    f'<span style="color:#92400E;font-size:12px;'
                    f'font-weight:500;">Melebihi rentang disarankan.</span>'
                    f'</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>",
                        unsafe_allow_html=True)

            jalankan = st.button("🔄 Latih Ulang Model dan Ramalkan",
                                 type="primary", use_container_width=False)

            if jalankan:
                with st.spinner(f"Melatih ulang model... {jumlah_hari} hari"):
                    try:
                        out = proses_data_upload(
                            df_baru, kol_tgl_baru, kol_val_baru,
                            jumlah_hari=jumlah_hari)
                        st.session_state.hasil_ramalan_baru = out['hasil']
                        st.session_state.ts_baru_terakhir = out['ts_baru']
                        st.session_state.info_model_baru = out
                    except Exception as e:
                        st.error(f"Gagal memproses data: {e}")
                        st.session_state.hasil_ramalan_baru = None
        except Exception as e:
            st.error(f"Terjadi kesalahan membaca berkas: {e}")

    if st.session_state.hasil_ramalan_baru is not None:
        hasil_baru = st.session_state.hasil_ramalan_baru
        ts_baru = st.session_state.ts_baru_terakhir
        info = st.session_state.info_model_baru

        st.markdown("<div style='height:20px'></div>",
                    unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#DCFCE7;border-radius:12px;'
            f'padding:16px 20px;margin-bottom:20px;">'
            f'<div style="color:{HIJAU};font-size:13px;font-weight:600;">'
            f'Model berhasil dilatih ulang dari {len(ts_baru)} hari data '
            f'({ts_baru.index[0].strftime("%d %b %Y")} - '
            f'{ts_baru.index[-1].strftime("%d %b %Y")})</div></div>',
            unsafe_allow_html=True)

        n_hari = len(hasil_baru)
        lebar_ci = (hasil_baru['CI_Atas'] - hasil_baru['CI_Bawah']).mean()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Order Model", f"SARIMAX{info['order']}", "otomatis ↗")
        with k2:
            st.metric("Proyeksi Rata-rata",
                      f"{hasil_baru['Prediksi'].mean():.2f}".replace(".", ","),
                      "gangguan / hari ↗")
        with k3:
            st.metric("Periode Peramalan",
                      f"{hasil_baru['Tanggal'].iloc[0].strftime('%d %b')} - "
                      f"{hasil_baru['Tanggal'].iloc[-1].strftime('%d %b %Y')}",
                      f"{n_hari} hari ke depan")
        with k4:
            st.metric("Rata-rata Lebar Interval",
                      f"± {lebar_ci/2:.1f}".replace(".", ","),
                      "kian lebar kian jauh horizon")

        st.markdown("<div style='height:20px'></div>",
                    unsafe_allow_html=True)
        judul(f"Peramalan {n_hari} Hari dari Data Terbaru",
              "Data aktual dan hasil peramalan bergulir")

        f = go.Figure()
        f.add_trace(go.Scatter(
            x=ts_baru.index[-60:], y=ts_baru.values[-60:],
            name="Data Aktual (Diunggah)",
            line=dict(color=TOSKA, width=2.5, shape='spline'),
            fill="tozeroy", fillcolor="rgba(124, 107, 250, 0.1)"))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['CI_Atas'],
            mode="lines", line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip"))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['CI_Bawah'],
            fill="tonexty", mode="lines",
            fillcolor="rgba(124, 107, 250, 0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Interval 95%", hoverinfo="skip"))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['Prediksi'],
            name="Prediksi Baru",
            line=dict(color=BIRU, width=2.5, dash="dot", shape='spline')))
        f.update_layout(**tata(380))
        st.plotly_chart(f, use_container_width=True)

        st.markdown("<div style='height:20px'></div>",
                    unsafe_allow_html=True)
        judul("Tabel Hasil Peramalan Baru", "Rincian prediksi harian")

        tp = hasil_baru.copy()
        tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
        st.dataframe(
            tp.style.format({'Prediksi': '{:.2f}',
                             'CI_Bawah': '{:.2f}',
                             'CI_Atas': '{:.2f}'}),
            use_container_width=True, hide_index=True, height=300)

        st.download_button(
            "⬇ Unduh Hasil Peramalan Baru", key="unduh_ramalan_baru",
            data=hasil_baru.to_csv(index=False).encode('utf-8'),
            file_name=f"peramalan_bergulir_{datetime.now():%Y%m%d}.csv",
            mime="text/csv")
    else:
        st.markdown("<div style='height:20px'></div>",
                    unsafe_allow_html=True)
        st.info("Unggah berkas data gangguan untuk memulai peramalan bergulir.")

# ============================================================
# 15. ROUTING HALAMAN
# ============================================================
halaman = st.session_state.halaman

if halaman == 'Ringkasan':
    kpi()
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        judul("Tren Gangguan Harian", "Aktual vs prediksi ARIMA(1,1,1)")
        st.plotly_chart(g_tren(), use_container_width=True)
    with c2:
        judul("Penyebab Gangguan", "Lima kategori terbanyak")
        st.plotly_chart(g_penyebab(), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    c3, c4, c5 = st.columns(3)
    with c3:
        judul("Peramalan 30 Hari", "Interval kepercayaan 95%")
        st.plotly_chart(g_ramal(), use_container_width=True)
    with c4:
        judul("Distribusi Bulanan", "Volume per bulan")
        st.plotly_chart(g_bulan(), use_container_width=True)
    with c5:
        judul("Kanal Pelaporan", "Sumber laporan pelanggan")
        st.markdown(
            f'<div style="{KARTU}border-radius:20px;padding:24px;">'
            f'{b_sumber()}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

elif halaman == 'Tren Harian':
    kpi()
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Tren Gangguan Harian", "Data aktual dan prediksi ARIMA(1,1,1)")
    st.plotly_chart(g_tren(420), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        judul("Distribusi Bulanan", "Volume gangguan per bulan")
        st.plotly_chart(g_bulan(320), use_container_width=True)
    with b:
        judul("Statistik Deskriptif", "Ringkasan periode terpilih")
        s = hist_f[kol_val]
        total = f"{int(s.sum()):,}".replace(",", ".")
        st.markdown(
            f'<div style="{KARTU}'
            f'border-radius:20px;padding:24px;">'
            f'<table style="width:100%;font-size:13px;">'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:12px 0;color:{ABU};">Jumlah observasi</td>'
            f'<td style="padding:12px 0;text-align:right;color:{NAVY};'
            f'font-weight:600;">{len(s)} hari</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:12px 0;color:{ABU};">Total gangguan</td>'
            f'<td style="padding:12px 0;text-align:right;color:{NAVY};'
            f'font-weight:600;">{total}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:12px 0;color:{ABU};">Rata-rata harian</td>'
            f'<td style="padding:12px 0;text-align:right;color:{NAVY};'
            f'font-weight:600;">{s.mean():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:12px 0;color:{ABU};">Standar deviasi</td>'
            f'<td style="padding:12px 0;text-align:right;color:{NAVY};'
            f'font-weight:600;">{s.std():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:12px 0;color:{ABU};">Nilai minimum</td>'
            f'<td style="padding:12px 0;text-align:right;color:{NAVY};'
            f'font-weight:600;">{int(s.min())}</td></tr>'
            f'<tr><td style="padding:12px 0;color:{ABU};">'
            f'Nilai maksimum</td>'
            f'<td style="padding:12px 0;text-align:right;color:{MERAH};'
            f'font-weight:600;">{int(s.max())}</td></tr>'
            f'</table></div>', unsafe_allow_html=True)

elif halaman == 'Peramalan':
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Proyeksi Rata-rata",
                  f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","),
                  "gangguan / hari ↗")
    with k2:
        st.metric("Batas Bawah CI",
                  f"{peramalan['CI_Bawah'].min():.1f}".replace(".", ","),
                  "interval 95%")
    with k3:
        st.metric("Batas Atas CI",
                  f"{peramalan['CI_Atas'].max():.1f}".replace(".", ","),
                  "interval 95%")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Peramalan 30 Hari ke Depan", "Prediksi beserta interval 95%")
    st.plotly_chart(g_ramal(400), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Tabel Hasil Peramalan", "Rincian prediksi harian")
    tp = peramalan.copy()
    tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
    st.dataframe(
        tp.style.format({'Prediksi': '{:.2f}',
                         'CI_Bawah': '{:.2f}',
                         'CI_Atas': '{:.2f}'}),
        use_container_width=True, hide_index=True, height=320)
    simulasi_skenario()

elif halaman == 'Perbarui & Ramalkan':
    judul("Perbarui Data dan Ramalkan Ulang",
          "Unggah data gangguan terbaru untuk peramalan bergulir")
    halaman_perbarui_ramalkan()

elif halaman == 'Analisis Penyebab':
    a, b = st.columns(2)
    with a:
        judul("Distribusi Penyebab", "Lima kategori terbanyak")
        st.plotly_chart(g_penyebab(340), use_container_width=True)
    with b:
        judul("Kanal Pelaporan", "Sumber laporan pelanggan")
        st.markdown(
            f'<div style="{KARTU}border-radius:20px;padding:24px;">'
            f'{b_sumber()}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Rincian Penyebab Gangguan", "Seluruh kategori tercatat")
    p = penyebab.copy()
    p['Proporsi (%)'] = (p['Jumlah'] / p['Jumlah'].sum() * 100).round(2)
    st.dataframe(p.head(15), use_container_width=True,
                 hide_index=True, height=380)

elif halaman == 'Perbandingan Model':
    st.markdown(
        f'<div style="{KARTU}border-left:4px solid {BIRU};'
        f'border-radius:8px 20px 20px 8px;'
        f'padding:20px 24px;margin-bottom:24px;">'
        f'<div style="color:{NAVY};font-size:14px;font-weight:600;'
        f'margin-bottom:8px;">Bandingkan Model Secara Interaktif</div>'
        f'<div style="color:{ABU};font-size:12.5px;line-height:1.8;">'
        f'Klik salah satu tombol di bawah untuk melihat detail performa '
        f'tiap tahap optimasi model. Penambahan variabel eksogen justru '
        f'menurunkan akurasi pada data uji.</div></div>',
        unsafe_allow_html=True)

    kartu_model_toggle()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        judul("Perbandingan MASE Seluruh Model",
              "Semakin rendah semakin baik")
        st.plotly_chart(g_progres_optimasi(), use_container_width=True)
    with b:
        judul("Perbandingan R² Seluruh Model",
              "Semakin tinggi semakin baik")
        st.plotly_chart(g_progres_r2(), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Tabel Lengkap Seluruh Model", "ARIMA, SARIMAX, dan baseline")
    t_metrik()

    st.markdown(
        f'<div style="{KARTU}border-left:4px solid {HIJAU};'
        f'border-radius:8px 20px 20px 8px;'
        f'padding:20px 24px;margin-top:20px;">'
        f'<div style="color:{NAVY};font-size:14px;font-weight:600;'
        f'margin-bottom:8px;">Kesimpulan Optimasi</div>'
        f'<div style="color:{ABU};font-size:12.5px;line-height:1.8;">'
        f'Penambahan variabel eksogen berbasis kalender pada model SARIMAX '
        f'TIDAK berhasil meningkatkan akurasi. MASE ARIMA(1,1,1) sebesar '
        f'1,548 justru lebih rendah dibanding SARIMAX kalender dasar (1,653) '
        f'dan SARIMAX kalender lengkap (1,670). Seluruh model memiliki R² '
        f'negatif. Temuan ini menunjukkan bahwa fluktuasi gangguan kabel SR '
        f'tidak dijelaskan oleh pola kalender, melainkan oleh faktor eksogen '
        f'fisik seperti kondisi cuaca yang tidak tersedia dalam dataset. '
        f'Model final yang digunakan adalah ARIMA(1,1,1).</div></div>',
        unsafe_allow_html=True)

elif halaman == 'Akurasi Model':
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    ar = baris_terbaik

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("MAE", f"{ar['MAE']:.2f}".replace(".", ","),
                  "mean absolute error")
    with k2:
        st.metric("RMSE", f"{ar['RMSE']:.2f}".replace(".", ","),
                  "root mean sq. error")
    with k3:
        st.metric("sMAPE", f"{ar['sMAPE(%)']:.2f}%".replace(".", ","),
                  "symmetric MAPE")
    with k4:
        st.metric("MASE", f"{ar['MASE']:.3f}".replace(".", ","),
                  "model terbaik")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Validasi Model",
          "Hasil uji diagnostik residual (model ARIMA terbaik)")
    v1, v2, v3 = st.columns(3)
    for kol, (label, nilai) in zip(
        [v1, v2, v3],
        [("Ljung-Box Lag 7", "0,609"),
         ("Ljung-Box Lag 14", "0,713"),
         ("Ljung-Box Lag 21", "0,671")]
    ):
        with kol:
            st.markdown(
                f'<div style="{KARTU}'
                f'border-radius:20px;padding:24px;">'
                f'<div style="color:{ABU};font-size:12px;'
                f'font-weight:500;">{label}</div>'
                f'<div style="color:{HIJAU};font-size:36px;font-weight:500;'
                f'margin:8px 0 4px;letter-spacing:-.5px;">{nilai}</div>'
                f'<div style="color:{ABU};font-size:11px;">'
                f'p &gt; 0,05 · white noise</div></div>',
                unsafe_allow_html=True)

# ============================================================
# 16. FOOTER
# ============================================================
st.markdown(
    f'<div style="text-align:center;color:{ABU};font-size:11px;'
    f'padding:30px 0 10px;border-top:1px solid {GARIS};margin-top:30px;">'
    f'Dashboard Peramalan Gangguan Kabel Sambungan Rumah &nbsp;·&nbsp; '
    f'PT. Haleyora Power Serpong &nbsp;·&nbsp; ARIMA(1,1,1) &nbsp;·&nbsp; '
    f'CRISP-DM Framework</div>', unsafe_allow_html=True)
