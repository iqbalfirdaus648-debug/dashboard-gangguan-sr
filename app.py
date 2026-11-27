# ============================================================
# DASHBOARD PERAMALAN GANGGUAN KABEL SR - PLN UP3 SERPONG
# Desain: Tasklyn Modern (Floating, Pastel, Clean)
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
    page_title="Dashboard Gangguan Kabel SR",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. PALET WARNA (Pastel & Clean)
# ============================================================
TEXT_DARK = "#1E1E2F"
TEXT_GRAY = "#6B7280"

PASTEL_BLUE   = "#E0F2FE"
PASTEL_PURPLE = "#F3E8FF"
PASTEL_PEACH  = "#FFEDD5"
PASTEL_GREEN  = "#DCFCE7"

ACCENT_BLUE   = "#0369A1"
ACCENT_PURPLE = "#7E22CE"
ACCENT_PEACH  = "#C2410C"
ACCENT_GREEN  = "#15803D"

NAV_ACTIVE    = "#1E1E2F"
NAV_INACTIVE  = "#F3F4F6"
APP_BG        = "#F8FAFC"

# ============================================================
# 3. CSS KUSTOM (Tasklyn Style)
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family:'Plus Jakarta Sans', sans-serif; }}

.stApp {{
    background: linear-gradient(135deg, #E0E7FF 0%, #F3F4F6 50%, #ECFDF5 100%);
}}

.block-container {{
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 32px;
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 24px 48px -12px rgba(0,0,0,0.1);
    padding: 2rem 3rem !important;
    margin: 2rem auto !important;
    max-width: 1400px;
}}

#MainMenu, footer, header {{ visibility:hidden; }}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {{ display:none !important; }}

/* ---------- Sidebar Tasklyn ---------- */
section[data-testid="stSidebar"] {{
    background: transparent !important;
    border-right: none !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    background: transparent !important;
    padding-top: 2rem !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 8px; }}

section[data-testid="stSidebar"] button {{
    border-radius: 12px !important;
    padding: 0 20px !important;
    height: 44px !important;
    width: 100% !important;
    border: none !important;
    transition: all 0.2s ease;
    justify-content: flex-start !important;
}}
section[data-testid="stSidebar"] button p {{
    font-size: 13.5px !important;
    font-weight: 600 !important;
    margin: 0 !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background: transparent !important;
    color: {TEXT_GRAY} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background: {NAV_INACTIVE} !important;
    color: {TEXT_DARK} !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] {{
    background: {NAV_ACTIVE} !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(30, 30, 47, 0.2) !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] p {{
    color: #FFFFFF !important;
}}

/* ---------- Header Atas (Search & Profile) ---------- */
.top-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(0,0,0,0.05);
}}
.header-title {{ font-size: 24px; font-weight: 800; color: {TEXT_DARK}; letter-spacing: -0.5px; }}
.header-subtitle {{ font-size: 13px; color: {TEXT_GRAY}; font-weight: 500; margin-top: 4px; }}
.header-icons {{ display: flex; gap: 12px; align-items: center; }}
.icon-btn {{
    width: 40px; height: 40px; border-radius: 50%;
    background: #FFFFFF; display: flex; justify-content: center; align-items: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05); cursor: pointer;
}}

/* ---------- KARTU KPI PASTEL (Tasklyn Style) ---------- */
[data-testid="stMetric"] {{
    border-radius: 24px;
    padding: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    transition: transform 0.2s ease;
}}
[data-testid="stMetric"]:hover {{ transform: translateY(-3px); }}

[data-testid="column"]:nth-of-type(1) [data-testid="stMetric"] {{ background: {PASTEL_BLUE}; }}
[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"] {{ background: {PASTEL_PURPLE}; }}
[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"] {{ background: {PASTEL_PEACH}; }}
[data-testid="column"]:nth-of-type(4) [data-testid="stMetric"] {{ background: {PASTEL_GREEN}; }}

[data-testid="stMetricLabel"] p {{
    font-size: 12px !important;
    font-weight: 600 !important;
    color: {TEXT_GRAY} !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
[data-testid="stMetricValue"] {{
    font-size: 38px !important;
    font-weight: 800 !important;
    color: {TEXT_DARK} !important;
    letter-spacing: -1px;
    margin-top: 8px;
}}
[data-testid="stMetricDelta"] {{ margin-top: 12px; }}
[data-testid="stMetricDelta"] * {{
    color: {TEXT_DARK} !important;
    font-size: 11px !important;
    font-weight: 600;
    background: rgba(255,255,255,0.6) !important;
    padding: 4px 10px;
    border-radius: 12px;
    display: inline-block;
}}
[data-testid="stMetricDelta"] svg {{ display: none; }}

/* ---------- Grafik & Tabel (Card Putih Bersih) ---------- */
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{
    background: #FFFFFF;
    border-radius: 24px;
    padding: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    border: 1px solid rgba(0,0,0,0.02);
}}

/* ---------- Judul Section ---------- */
.judul-seksi {{
    font-size: 16px; font-weight: 700; color: {TEXT_DARK};
    margin-bottom: 4px;
}}
.sub-seksi {{
    font-size: 12px; color: {TEXT_GRAY}; font-weight: 500;
    margin-bottom: 16px;
}}

/* ---------- Tombol & Input Utama ---------- */
.main button {{
    border-radius: 12px !important;
    font-weight: 600 !important;
    border: none !important;
}}
.main button[kind="secondary"] {{
    background: #FFFFFF !important;
    color: {TEXT_DARK} !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}}
.main [data-baseweb="select"] > div {{
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
}}
[data-testid="stFileUploader"] section {{
    background: #FFFFFF !important;
    border: 1px dashed rgba(0,0,0,0.15) !important;
    border-radius: 16px !important;
}}
[data-testid="stExpander"] {{
    background: #FFFFFF; border: 1px solid rgba(0,0,0,0.05);
    border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}}
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

def _cari_kolom(df, kandidat):
    def normal(s):
        return (str(s).lower().replace('²', '2').replace('^', '')
                .replace(' ', '').replace('_', '').replace('-', '')
                .replace('(', '').replace(')', '').replace('%', ''))
    peta = {normal(c): c for c in df.columns}
    for k in kandidat:
        if normal(k) in peta: return peta[normal(k)]
    return None

def _alias(df, kandidat, label=None):
    if label is None: label = kandidat[0]
    if label in df.columns: return
    asli = _cari_kolom(df, kandidat)
    if asli is not None: df[label] = df[asli]

_alias(metrik, ['R2', 'R²', 'R^2', 'R-Squared', 'RSquared', 'R2 (%)'], 'R2')
_alias(metrik, ['sMAPE(%)', 'sMAPE', 'sMAPE (%)', 'SMAPE'], 'sMAPE(%)')
_alias(metrik, ['MAE'], 'MAE')
_alias(metrik, ['RMSE'], 'RMSE')
_alias(metrik, ['MASE'], 'MASE')

# ============================================================
# 5. SESSION STATE
# ============================================================
if 'halaman' not in st.session_state: st.session_state.halaman = 'Ringkasan'
if 'model_terpilih' not in st.session_state: st.session_state.model_terpilih = 'ARIMA Dasar'
if 'hasil_ramalan_baru' not in st.session_state: st.session_state.hasil_ramalan_baru = None
if 'ts_baru_terakhir' not in st.session_state: st.session_state.ts_baru_terakhir = None
if 'info_model_baru' not in st.session_state: st.session_state.info_model_baru = None

# ============================================================
# 6. SIDEBAR (Model Navigasi Melengkung)
# ============================================================
with st.sidebar:
    if os.path.exists('logo_haleyora.png'):
        with open('logo_haleyora.png', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="padding:0 0 24px 12px;">'
            f'<img src="data:image/png;base64,{b64}" style="height:38px;">'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="padding:0 0 24px 12px;font-size:20px;font-weight:800;color:#1E1E2F;">'
            'haleyora<span style="color:#F59E0B;">power</span></div>', 
            unsafe_allow_html=True)

    st.markdown('<div style="color:#9CA3AF;font-size:11px;font-weight:700;padding:0 12px 12px;letter-spacing:1px;">MENU UTAMA</div>', unsafe_allow_html=True)
    
    for nama in ["Ringkasan", "Tren Harian", "Peramalan", "Perbarui & Ramalkan", 
                 "Analisis Penyebab", "Perbandingan Model", "Akurasi Model"]:
        aktif = st.session_state.halaman == nama
        if st.button(nama, key=f"nav_{nama}", use_container_width=True,
                     type="primary" if aktif else "secondary"):
            st.session_state.halaman = nama
            st.rerun()

    st.markdown('<div style="color:#9CA3AF;font-size:11px;font-weight:700;padding:24px 12px 12px;letter-spacing:1px;">FILTER</div>', unsafe_allow_html=True)
    opsi = ['Semua'] + list(pd.to_datetime(hist.iloc[:, 0]).dt.strftime('%b %Y').unique())
    pilih_bulan = st.selectbox("p", opsi, label_visibility="collapsed")

# ============================================================
# 7. HEADER & KONTEN
# ============================================================
st.markdown(f"""
<div class="top-header">
    <div>
        <div class="header-title">Dashboard Peramalan Gangguan</div>
        <div class="header-subtitle">PT. Haleyora Power Serpong · Metode ARIMA & SARIMAX</div>
    </div>
    <div class="header-icons">
        <div class="icon-btn">🔍</div>
        <div class="icon-btn">🔔</div>
        <div class="icon-btn" style="background:#FCD34D;">👤</div>
    </div>
</div>
""", unsafe_allow_html=True)

hist_f = hist.copy()
hist_f.iloc[:, 0] = pd.to_datetime(hist_f.iloc[:, 0])
if pilih_bulan != 'Semua':
    hist_f = hist_f[hist_f.iloc[:, 0].dt.strftime('%b %Y') == pilih_bulan]

kol_tgl, kol_val = hist_f.columns[0], hist_f.columns[1]

# ============================================================
# 8. HELPER FUNCTIONS
# ============================================================
TRANSPARAN = 'rgba(0,0,0,0)'

def tata(t=280):
    return dict(
        plot_bgcolor=TRANSPARAN, paper_bgcolor=TRANSPARAN,
        font=dict(color=TEXT_GRAY, size=11, family='Plus Jakarta Sans'),
        height=t, margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_GRAY), showline=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0.04)', tickfont=dict(size=11, color=TEXT_GRAY), zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, x=0, font=dict(size=11, color=TEXT_GRAY)),
        hoverlabel=dict(bgcolor=TEXT_DARK, font=dict(color='white', size=12))
    )

def judul(teks, sub=""):
    st.markdown(f'<div class="judul-seksi">{teks}</div><div class="sub-seksi">{sub}</div>', unsafe_allow_html=True)

# ============================================================
# 9. KPI CARDS (Pastel)
# ============================================================
def kpi():
    k1, k2, k3, k4 = st.columns(4)
    total = f"{int(hist_f[kol_val].sum()):,}".replace(",", ".")
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    mase = float(baris_terbaik['MASE'])

    with k1:
        st.metric("TOTAL GANGGUAN", total, "kasus tercatat ↗")
    with k2:
        st.metric("RATA-RATA HARIAN", f"{hist_f[kol_val].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
    with k3:
        st.metric("AKURASI MASE", f"{mase:.3f}".replace(".", ","), "belum unggul dari naive")
    with k4:
        st.metric("PROYEKSI 30 HARI", f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","), "kategori sedang ↗")

# ============================================================
# 10. FUNGSI GRAFIK
# ============================================================
def g_tren(t=320):
    f = go.Figure()
    f.add_trace(go.Scatter(
        x=hist_f[kol_tgl], y=hist_f[kol_val], name='Aktual',
        line=dict(color='#818CF8', width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(129, 140, 248, 0.1)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y} gangguan<extra></extra>'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'], name='Prediksi',
        line=dict(color='#F97316', width=3, dash='dot', shape='spline'),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y:.1f}<extra></extra>'))
    f.update_layout(**tata(t))
    return f

def g_penyebab(t=320):
    d = penyebab.head(5).copy()
    d['Lengkap'] = d['Penyebab'].astype(str)
    d['Penyebab'] = d['Lengkap'].apply(lambda x: x if len(x) <= 22 else x[:20] + '…')
    
    f = px.pie(d, values='Jumlah', names='Penyebab', hole=.65, custom_data=['Lengkap'],
               color_discrete_sequence=['#A78BFA', '#C4B5FD', '#DDD6FE', '#F3E8FF', '#F8FAFC'])
    f.update_traces(
        textposition='inside', textinfo='percent',
        textfont=dict(size=11, color='white'),
        hovertemplate='<b>%{customdata[0]}</b><br>%{value:,}<extra></extra>',
        marker=dict(line=dict(color='#FFFFFF', width=3)))
    f.update_layout(
        paper_bgcolor=TRANSPARAN, height=t, margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color=TEXT_GRAY, family='Plus Jakarta Sans'),
        legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5, font=dict(size=11, color=TEXT_GRAY)),
        hoverlabel=dict(bgcolor=TEXT_DARK, font=dict(color='white')))
    return f

def g_ramal(t=250):
    f = go.Figure()
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['CI_Atas'], mode='lines', line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['CI_Bawah'], fill='tonexty', mode='lines', fillcolor='rgba(167, 139, 250, 0.2)', line=dict(color='rgba(0,0,0,0)'), name='Interval 95%', hoverinfo='skip'))
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['Prediksi'], name='Prediksi', line=dict(color='#A78BFA', width=3, shape='spline')))
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
    
    warna = ['#6366F1' if i == len(b['Jumlah']) - 1 else '#C4B5FD' for i in range(len(b['Jumlah']))]
    teks = [f"{v:,}".replace(",", ".") for v in b['Jumlah']]
    
    kw = dict(x=b['Bulan'], y=b['Jumlah'], text=teks, textposition='outside', textfont=dict(size=10, color=TEXT_DARK), cliponaxis=False)
    try:
        f = go.Figure(go.Bar(**kw, marker=dict(color=warna, cornerradius=6, line=dict(color='rgba(0,0,0,0)', width=0))))
    except Exception:
        f = go.Figure(go.Bar(**kw, marker=dict(color=warna)))
        
    L = tata(t)
    L['xaxis'].update(tickangle=0, tickfont=dict(size=11, color=TEXT_GRAY))
    L['yaxis'].update(range=[0, mx * 1.2])
    f.update_layout(**L)
    return f

def b_sumber():
    total_s = sumber['Jumlah'].sum()
    html = ""
    for i, (_, r) in enumerate(sumber.head(6).iterrows()):
        pct = r['Jumlah'] / total_s * 100
        jml = f"{r['Jumlah']:,}".replace(",", ".")
        nama = str(r['Sumber_Lapor'])[:22]
        html += (
            f'<div style="margin-bottom:18px;">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:6px;">'
            f'<span style="color:{TEXT_DARK};font-size:12px;font-weight:600;">{nama}</span>'
            f'<span style="color:{TEXT_GRAY};font-size:11px;font-weight:700;">'
            f'{jml} <span style="font-weight:500;">({pct:.1f}%)</span></span></div>'
            f'<div style="background:rgba(0,0,0,.04);border-radius:6px;height:8px;">'
            f'<div style="background:#818CF8;height:8px;border-radius:6px;width:{min(pct, 100):.1f}%;"></div>'
            f'</div></div>')
    return html

def t_metrik():
    def sorot(x):
        return [
            f'background-color:#DCFCE7;color:#15803D;font-weight:800' if v == x.min() else
            f'color:#EF4444;font-weight:700' if v == x.max() else ''
            for v in x
        ]
    st.dataframe(
        metrik.style.apply(sorot, subset=['MASE']).format({
            'MAE': '{:.2f}', 'RMSE': '{:.2f}', 'sMAPE(%)': '{:.2f}%',
            'R2': '{:.4f}', 'MASE': '{:.3f}'}),
        use_container_width=True, hide_index=True)

def catatan():
    st.markdown(
        f'<div style="background:#F3E8FF;border-radius:20px;padding:20px 24px;margin-top:16px;">'
        f'<div style="color:{TEXT_DARK};font-size:14px;font-weight:700;margin-bottom:8px;">Interpretasi Hasil</div>'
        f'<div style="color:{TEXT_GRAY};font-size:12.5px;line-height:1.8;font-weight:500;">'
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
    judul("Simulasi Skenario Faktor Eksternal", "Ilustrasi dampak faktor eksogen tambahan di luar model")
    st.markdown(
        f'<div style="background:#E0F2FE;border-radius:20px;padding:16px 20px;margin-bottom:20px;">'
        f'<div style="color:{TEXT_GRAY};font-size:12.5px;line-height:1.7;font-weight:500;">'
        f'Model ARIMA sudah menangkap pola historis murni dari data. '
        f'Simulasi ini menggeser hasil prediksi secara proporsional untuk '
        f'mengilustrasikan potensi dampak faktor cuaca yang belum '
        f'dimodelkan, bukan hasil pemodelan baru.</div></div>',
        unsafe_allow_html=True)

    skenario = st.select_slider(
        "Skenario Faktor Eksternal",
        options=["Musim Kering (-30%)", "Normal (0%)", "Musim Hujan (+20%)", "Cuaca Ekstrem (+50%)"],
        value="Normal (0%)")

    faktor = {"Musim Kering (-30%)": -0.30, "Normal (0%)": 0.0, "Musim Hujan (+20%)": 0.20, "Cuaca Ekstrem (+50%)": 0.50}[skenario]

    df_sim = peramalan.copy()
    df_sim['Prediksi_Sim'] = (df_sim['Prediksi'] * (1 + faktor)).clip(lower=0)

    f = go.Figure()
    f.add_trace(go.Scatter(x=df_sim['Tanggal'], y=df_sim['Prediksi'], name='Prediksi ARIMA (asli)', line=dict(color=TEXT_GRAY, width=2, dash='dot', shape='spline')))
    f.add_trace(go.Scatter(x=df_sim['Tanggal'], y=df_sim['Prediksi_Sim'], name=f'Simulasi: {skenario}', line=dict(color='#818CF8', width=3, shape='spline'), fill='tonexty', fillcolor='rgba(129, 140, 248, 0.1)'))
    f.update_layout(**tata(300))
    st.plotly_chart(f, use_container_width=True)

    selisih = df_sim['Prediksi_Sim'].mean() - df_sim['Prediksi'].mean()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Rata-rata Prediksi Asli", f"{df_sim['Prediksi'].mean():.1f}", "gangguan/hari")
    with c2:
        st.metric("Rata-rata Skenario", f"{df_sim['Prediksi_Sim'].mean():.1f}", f"{'+' if selisih >= 0 else ''}{selisih:.1f} vs asli ↗")

# ============================================================
# 12. GRAFIK PROGRES OPTIMASI
# ============================================================
def g_progres_optimasi():
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    warna_bar = ['#C4B5FD'] * (len(df_prog) - 1) + ['#6366F1']
    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['MASE'], marker_color=warna_bar,
        text=df_prog['MASE'].round(3), textposition='outside',
        hovertemplate='<b>%{x}</b><br>MASE: %{y:.3f}<extra></extra>'))
    f.add_hline(y=1.0, line_dash='dot', line_color='#EF4444', annotation_text='Ambang unggul dari naive', annotation_font_size=10, annotation_font_color='#EF4444')
    L = tata(320)
    L['yaxis']['title'] = 'MASE'
    f.update_layout(**L)
    return f

def g_progres_r2():
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    warna_bar = ['#DDD6FE' if v >= 0 else '#FEE2E2' for v in df_prog['R2']]
    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['R2'], marker_color=warna_bar,
        text=df_prog['R2'].round(4), textposition='outside',
        hovertemplate='<b>%{x}</b><br>R2: %{y:.4f}<extra></extra>'))
    f.add_hline(y=0, line_dash='dot', line_color=TEXT_GRAY)
    L = tata(320)
    L['yaxis']['title'] = 'R2'
    f.update_layout(**L)
    return f

# ============================================================
# 13. KARTU TOGGLE PERBANDINGAN MODEL
# ============================================================
def kartu_model_toggle():
    opsi_model = {
        'ARIMA Dasar': {
            'nama_metrik': 'ARIMA(1, 1, 1)',
            'deskripsi': 'Model univariat terbaik berdasarkan AIC. Residual white noise, tetapi MASE masih di atas 1,0 sehingga belum mengungguli baseline naive.',
            'warna': '#E0F2FE'
        },
        'SARIMAX Kalender Dasar': {
            'nama_metrik': 'SARIMAX(1, 1, 1) + kalender dasar',
            'deskripsi': 'Penambahan variabel kalender (akhir pekan, awal/akhir bulan). Tidak meningkatkan akurasi; MASE justru lebih tinggi dari ARIMA.',
            'warna': '#F3E8FF'
        },
        'SARIMAX Kalender Lengkap': {
            'nama_metrik': 'SARIMAX(1, 1, 2) + kalender lengkap',
            'deskripsi': 'Order dioptimasi ulang + fitur hari libur nasional. Hasil terburuk; indikasi overfitting terhadap pola kalender.',
            'warna': '#FFEDD5'
        }
    }

    cols = st.columns(3)
    for i, nama_opsi in enumerate(opsi_model.keys()):
        aktif = st.session_state.model_terpilih == nama_opsi
        with cols[i]:
            if st.button(nama_opsi, key=f"toggle_{nama_opsi}", use_container_width=True, type="primary" if aktif else "secondary"):
                st.session_state.model_terpilih = nama_opsi
                st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    pilihan = opsi_model[st.session_state.model_terpilih]
    baris = metrik[metrik['Model'] == pilihan['nama_metrik']]

    if baris.empty:
        st.warning(f"Data untuk model '{pilihan['nama_metrik']}' belum ditemukan pada sheet Metrik.")
        return

    m = baris.iloc[0]
    st.markdown(
        f'<div style="background:{pilihan["warna"]};border-radius:24px;padding:24px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">'
        f'<span style="color:{TEXT_DARK};font-size:16px;font-weight:800;">{st.session_state.model_terpilih}</span>'
        f'<span style="background:rgba(255,255,255,0.7);color:{TEXT_DARK};padding:6px 14px;border-radius:20px;font-size:11px;font-weight:700;">{pilihan["nama_metrik"]}</span></div>'
        f'<div style="color:{TEXT_GRAY};font-size:13px;line-height:1.7;font-weight:500;">{pilihan["deskripsi"]}</div></div>',
        unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    def _nil(series, key, fmt):
        try: return f"{series[key]:{fmt}}".replace(".", ",")
        except Exception: return "-"

    with k1: st.metric("MAE", _nil(m, 'MAE', '.2f'))
    with k2: st.metric("RMSE", _nil(m, 'RMSE', '.2f'))
    with k3: st.metric("sMAPE", _nil(m, 'sMAPE(%)', '.2f') + ("%" if _nil(m, 'sMAPE(%)', '.2f') != "-" else ""))
    with k4: st.metric("R2", _nil(m, 'R2', '.4f'))
    with k5: st.metric("MASE", _nil(m, 'MASE', '.3f'))

# ============================================================
# 14. PERAMALAN BERGULIR
# ============================================================
def proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru, jumlah_hari=30, order_model=(1, 1, 1)):
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
        exog['is_holiday'] = [1 if d in id_hol else 0 for d in index_tanggal.date]
        return exog

    exog_baru = buat_exog(ts_baru.index)
    model_baru = SARIMAX(ts_baru, exog=exog_baru, order=order_model, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=1000, method='powell')

    idx_depan = pd.date_range(ts_baru.index[-1] + pd.Timedelta(days=1), periods=jumlah_hari, freq='D')
    exog_depan = buat_exog(idx_depan)

    fc_baru = model_baru.get_forecast(steps=jumlah_hari, exog=exog_depan)
    ci = fc_baru.conf_int()

    hasil_baru = pd.DataFrame({
        'Tanggal': idx_depan,
        'Prediksi': fc_baru.predicted_mean.clip(lower=0).round(2).values,
        'CI_Bawah': ci.iloc[:, 0].clip(lower=0).round(2).values,
        'CI_Atas': ci.iloc[:, 1].clip(lower=0).round(2).values,
    })

    return {'ts_baru': ts_baru, 'hasil': hasil_baru, 'order': order_model, 'aic': model_baru.aic}

def halaman_perbarui_ramalkan():
    st.markdown(
        f'<div style="background:#E0F2FE;border-radius:20px;padding:20px 24px;margin-bottom:24px;">'
        f'<div style="color:{TEXT_DARK};font-size:14px;font-weight:700;margin-bottom:8px;">Peramalan Bergulir (Rolling Forecast)</div>'
        f'<div style="color:{TEXT_GRAY};font-size:12.5px;line-height:1.8;font-weight:500;">'
        f'Fitur ini memungkinkan sistem melatih ulang model SARIMAX secara otomatis menggunakan data gangguan terbaru yang diunggah, '
        f'kemudian menghasilkan peramalan dari titik data paling akhir. '
        f'Dengan mekanisme ini, dashboard dapat digunakan untuk meramalkan periode berikutnya kapan pun data baru tersedia, tanpa perlu mengubah kode program.</div></div>',
        unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:#FFFFFF;border-radius:24px;padding:20px 24px;margin-bottom:24px;box-shadow:0 4px 20px rgba(0,0,0,0.03);">'
        f'<div style="color:{TEXT_DARK};font-size:14px;font-weight:700;margin-bottom:12px;">Panduan Rentang Peramalan</div>'
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        f'<div style="flex:1;min-width:220px;background:#DCFCE7;border-radius:12px;padding:12px 16px;">'
        f'<span style="color:#15803D;font-size:12px;font-weight:700;">7-42 HARI — DISARANKAN</span>'
        f'<div style="color:#065F46;font-size:11px;line-height:1.6;margin-top:4px;font-weight:500;">Interval kepercayaan masih wajar.</div></div>'
        f'<div style="flex:1;min-width:220px;background:#FFFBEB;border-radius:12px;padding:12px 16px;">'
        f'<span style="color:#D97706;font-size:12px;font-weight:700;">43-120 HARI — HANYA ILUSTRASI</span>'
        f'<div style="color:#92400E;font-size:11px;line-height:1.6;margin-top:4px;font-weight:500;">Interval melebar signifikan.</div></div>'
        f'</div></div>', unsafe_allow_html=True)

    file_baru = st.file_uploader("Unggah berkas data gangguan (XLSX / CSV)", type=['xlsx', 'csv'], key="upload_ramalan")

    if file_baru is not None:
        try:
            if file_baru.name.lower().endswith('.csv'): df_baru = pd.read_csv(file_baru)
            else: df_baru = pd.read_excel(file_baru)

            st.success(f"Berkas berhasil dimuat - {len(df_baru):,} baris, {df_baru.shape[1]} kolom")

            with st.expander("Pratinjau data yang diunggah", expanded=False):
                st.dataframe(df_baru.head(10), use_container_width=True)

            c1, c2 = st.columns(2)
            with c1: kol_tgl_baru = st.selectbox("Kolom tanggal", df_baru.columns, key="pilih_kol_tgl")
            with c2: kol_val_baru = st.selectbox("Kolom jumlah gangguan", df_baru.columns, key="pilih_kol_val")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            jumlah_hari = st.slider("Jumlah hari yang diramalkan ke depan", min_value=7, max_value=120, value=30, step=7)

            if jumlah_hari <= 42:
                st.markdown(f'<div style="background:#DCFCE7;border-radius:12px;padding:10px 16px;margin-top:8px;margin-bottom:8px;"><span style="color:#065F46;font-size:12px;font-weight:600;">Dalam rentang disarankan.</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#FFFBEB;border-radius:12px;padding:10px 16px;margin-top:8px;margin-bottom:8px;"><span style="color:#92400E;font-size:12px;font-weight:600;">Melebihi rentang disarankan.</span></div>', unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            jalankan = st.button("🔄 Latih Ulang Model dan Ramalkan", type="primary", use_container_width=False)

            if jalankan:
                with st.spinner(f"Melatih ulang model... {jumlah_hari} hari"):
                    try:
                        out = proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru, jumlah_hari=jumlah_hari)
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

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#DCFCE7;border-radius:12px;padding:16px 20px;margin-bottom:20px;">'
            f'<div style="color:#15803D;font-size:13px;font-weight:700;">'
            f'Model berhasil dilatih ulang dari {len(ts_baru)} hari data '
            f'({ts_baru.index[0].strftime("%d %b %Y")} - {ts_baru.index[-1].strftime("%d %b %Y")})</div></div>',
            unsafe_allow_html=True)

        n_hari = len(hasil_baru)
        lebar_ci = (hasil_baru['CI_Atas'] - hasil_baru['CI_Bawah']).mean()

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Order Model", f"SARIMAX{info['order']}", "otomatis ↗")
        with k2: st.metric("Proyeksi Rata-rata", f"{hasil_baru['Prediksi'].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
        with k3: st.metric("Periode Peramalan", f"{hasil_baru['Tanggal'].iloc[0].strftime('%d %b')} - {hasil_baru['Tanggal'].iloc[-1].strftime('%d %b %Y')}", f"{n_hari} hari ke depan")
        with k4: st.metric("Rata-rata Lebar Interval", f"± {lebar_ci/2:.1f}".replace(".", ","), "kian lebar kian jauh horizon")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        judul(f"Peramalan {n_hari} Hari dari Data Terbaru", "Data aktual dan hasil peramalan bergulir")

        f = go.Figure()
        f.add_trace(go.Scatter(x=ts_baru.index[-60:], y=ts_baru.values[-60:], name="Data Aktual", line=dict(color='#818CF8', width=3, shape='spline'), fill="tozeroy", fillcolor="rgba(129, 140, 248, 0.1)"))
        f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['CI_Atas'], mode="lines", line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
        f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['CI_Bawah'], fill="tonexty", mode="lines", fillcolor="rgba(167, 139, 250, 0.2)", line=dict(color="rgba(0,0,0,0)"), name="Interval 95%", hoverinfo="skip"))
        f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['Prediksi'], name="Prediksi Baru", line=dict(color='#F97316', width=3, dash="dot", shape='spline')))
        f.update_layout(**tata(380))
        st.plotly_chart(f, use_container_width=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        judul("Tabel Hasil Peramalan Baru", "Rincian prediksi harian")

        tp = hasil_baru.copy()
        tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
        st.dataframe(tp.style.format({'Prediksi': '{:.2f}', 'CI_Bawah': '{:.2f}', 'CI_Atas': '{:.2f}'}), use_container_width=True, hide_index=True, height=300)

        st.download_button("⬇ Unduh Hasil Peramalan Baru", key="unduh_ramalan_baru", data=hasil_baru.to_csv(index=False).encode('utf-8'), file_name=f"peramalan_bergulir_{datetime.now():%Y%m%d}.csv", mime="text/csv")
    else:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
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

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
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
            f'<div style="background:#FFFFFF;border-radius:24px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.03);height:100%;">'
            f'{b_sumber()}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

elif halaman == 'Tren Harian':
    kpi()
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Tren Gangguan Harian", "Data aktual dan prediksi ARIMA(1,1,1)")
    st.plotly_chart(g_tren(420), use_container_width=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        judul("Distribusi Bulanan", "Volume gangguan per bulan")
        st.plotly_chart(g_bulan(320), use_container_width=True)
    with b:
        judul("Statistik Deskriptif", "Ringkasan periode terpilih")
        s = hist_f[kol_val]
        total = f"{int(s.sum()):,}".replace(",", ".")
        st.markdown(
            f'<div style="background:#FFFFFF;border-radius:24px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.03);">'
            f'<table style="width:100%;font-size:13px;font-weight:500;">'
            f'<tr style="border-bottom:1px solid rgba(0,0,0,0.05);"><td style="padding:12px 0;color:{TEXT_GRAY};">Jumlah observasi</td><td style="padding:12px 0;text-align:right;color:{TEXT_DARK};font-weight:700;">{len(s)} hari</td></tr>'
            f'<tr style="border-bottom:1px solid rgba(0,0,0,0.05);"><td style="padding:12px 0;color:{TEXT_GRAY};">Total gangguan</td><td style="padding:12px 0;text-align:right;color:{TEXT_DARK};font-weight:700;">{total}</td></tr>'
            f'<tr style="border-bottom:1px solid rgba(0,0,0,0.05);"><td style="padding:12px 0;color:{TEXT_GRAY};">Rata-rata harian</td><td style="padding:12px 0;text-align:right;color:{TEXT_DARK};font-weight:700;">{s.mean():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid rgba(0,0,0,0.05);"><td style="padding:12px 0;color:{TEXT_GRAY};">Standar deviasi</td><td style="padding:12px 0;text-align:right;color:{TEXT_DARK};font-weight:700;">{s.std():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid rgba(0,0,0,0.05);"><td style="padding:12px 0;color:{TEXT_GRAY};">Nilai minimum</td><td style="padding:12px 0;text-align:right;color:{TEXT_DARK};font-weight:700;">{int(s.min())}</td></tr>'
            f'<tr><td style="padding:12px 0;color:{TEXT_GRAY};">Nilai maksimum</td><td style="padding:12px 0;text-align:right;color:#EF4444;font-weight:700;">{int(s.max())}</td></tr>'
            f'</table></div>', unsafe_allow_html=True)

elif halaman == 'Peramalan':
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("PROYEKSI RATA-RATA", f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
    with k2: st.metric("BATAS BAWAH CI", f"{peramalan['CI_Bawah'].min():.1f}".replace(".", ","), "interval 95%")
    with k3: st.metric("BATAS ATAS CI", f"{peramalan['CI_Atas'].max():.1f}".replace(".", ","), "interval 95%")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Peramalan 30 Hari ke Depan", "Prediksi beserta interval 95%")
    st.plotly_chart(g_ramal(400), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Tabel Hasil Peramalan", "Rincian prediksi harian")
    tp = peramalan.copy()
    tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
    st.dataframe(tp.style.format({'Prediksi': '{:.2f}', 'CI_Bawah': '{:.2f}', 'CI_Atas': '{:.2f}'}), use_container_width=True, hide_index=True, height=320)
    simulasi_skenario()

elif halaman == 'Perbarui & Ramalkan':
    judul("Perbarui Data dan Ramalkan Ulang", "Unggah data gangguan terbaru untuk peramalan bergulir")
    halaman_perbarui_ramalkan()

elif halaman == 'Analisis Penyebab':
    a, b = st.columns(2)
    with a:
        judul("Distribusi Penyebab", "Lima kategori terbanyak")
        st.plotly_chart(g_penyebab(340), use_container_width=True)
    with b:
        judul("Kanal Pelaporan", "Sumber laporan pelanggan")
        st.markdown(f'<div style="background:#FFFFFF;border-radius:24px;padding:24px;box-shadow:0 4px 20px rgba(0,0,0,0.03);">{b_sumber()}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Rincian Penyebab Gangguan", "Seluruh kategori tercatat")
    p = penyebab.copy()
    p['Proporsi (%)'] = (p['Jumlah'] / p['Jumlah'].sum() * 100).round(2)
    st.dataframe(p.head(15), use_container_width=True, hide_index=True, height=380)

elif halaman == 'Perbandingan Model':
    st.markdown(
        f'<div style="background:#E0F2FE;border-radius:20px;padding:20px 24px;margin-bottom:24px;">'
        f'<div style="color:{TEXT_DARK};font-size:14px;font-weight:700;margin-bottom:8px;">Bandingkan Model Secara Interaktif</div>'
        f'<div style="color:{TEXT_GRAY};font-size:12.5px;line-height:1.8;font-weight:500;">Klik salah satu tombol di bawah untuk melihat detail performa tiap tahap optimasi model.</div></div>',
        unsafe_allow_html=True)

    kartu_model_toggle()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        judul("Perbandingan MASE Seluruh Model", "Semakin rendah semakin baik")
        st.plotly_chart(g_progres_optimasi(), use_container_width=True)
    with b:
        judul("Perbandingan R² Seluruh Model", "Semakin tinggi semakin baik")
        st.plotly_chart(g_progres_r2(), use_container_width=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Tabel Lengkap Seluruh Model", "ARIMA, SARIMAX, dan baseline")
    t_metrik()

    st.markdown(
        f'<div style="background:#DCFCE7;border-radius:20px;padding:20px 24px;margin-top:20px;">'
        f'<div style="color:#15803D;font-size:14px;font-weight:700;margin-bottom:8px;">Kesimpulan Optimasi</div>'
        f'<div style="color:{TEXT_GRAY};font-size:12.5px;line-height:1.8;font-weight:500;">'
        f'Penambahan variabel eksogen berbasis kalender pada model SARIMAX TIDAK berhasil meningkatkan akurasi. '
        f'MASE ARIMA(1,1,1) sebesar 1,548 justru lebih rendah dibanding SARIMAX kalender dasar (1,653) dan SARIMAX kalender lengkap (1,670). '
        f'Seluruh model memiliki R² negatif. Model final yang digunakan adalah ARIMA(1,1,1).</div></div>',
        unsafe_allow_html=True)

elif halaman == 'Akurasi Model':
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    ar = baris_terbaik

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("MAE", f"{ar['MAE']:.2f}".replace(".", ","), "mean absolute error")
    with k2: st.metric("RMSE", f"{ar['RMSE']:.2f}".replace(".", ","), "root mean sq. error")
    with k3: st.metric("sMAPE", f"{ar['sMAPE(%)']:.2f}%".replace(".", ","), "symmetric MAPE")
    with k4: st.metric("MASE", f"{ar['MASE']:.3f}".replace(".", ","), "model terbaik")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Validasi Model", "Hasil uji diagnostik residual (model ARIMA terbaik)")
    v1, v2, v3 = st.columns(3)
    for kol, (label, nilai) in zip([v1, v2, v3], [("Ljung-Box Lag 7", "0,609"), ("Ljung-Box Lag 14", "0,713"), ("Ljung-Box Lag 21", "0,671")]):
        with kol:
            st.markdown(
                f'<div style="background:#FFFFFF;border-radius:24px;padding:24px;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,0.03);">'
                f'<div style="color:{TEXT_GRAY};font-size:12px;font-weight:600;text-transform:uppercase;">{label}</div>'
                f'<div style="color:#15803D;font-size:40px;font-weight:800;margin:8px 0 4px;letter-spacing:-1px;">{nilai}</div>'
                f'<div style="color:{TEXT_GRAY};font-size:11px;font-weight:500;">p &gt; 0,05 · white noise</div></div>',
                unsafe_allow_html=True)

# ============================================================
# 16. FOOTER
# ============================================================
st.markdown(
    f'<div style="text-align:center;color:{TEXT_GRAY};font-size:11px;font-weight:500;padding:30px 0 10px;border-top:1px solid rgba(0,0,0,0.05);margin-top:30px;">'
    f'Dashboard Peramalan Gangguan Kabel Sambungan Rumah &nbsp;·&nbsp; '
    f'PT. Haleyora Power Serpong &nbsp;·&nbsp; ARIMA(1,1,1) &nbsp;·&nbsp; '
    f'CRISP-DM Framework</div>', unsafe_allow_html=True)
