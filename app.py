%%writefile app.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64, os
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Gangguan Kabel SR — PLN",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY   = "#0B3B6F"
BIRU   = "#1565C0"
TOSKA  = "#00A9A5"
KUNING = "#F9A825"
ORANYE = "#F57F17"
MERAH  = "#E1121C"
HIJAU  = "#2E9E5B"
ABU    = "#7B8FA8"
GARIS  = "#E3E9F2"
PUTIH  = "#FFFFFF"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
.stApp {{ background:#F4F7FB; }}
#MainMenu, footer {{ visibility:hidden; }}

.block-container {{
    padding-top:4rem !important;
    padding-left:2.2rem !important;
    padding-right:2.2rem !important;
    padding-bottom:2rem !important;
    max-width:100%;
}}

/* ═══════ SIDEBAR ═══════ */
section[data-testid="stSidebar"] {{
    background:{NAVY};
    width:280px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top:0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
    gap:4px;
}}
section[data-testid="stSidebar"] button {{
    border:none !important;
    border-radius:8px !important;
    font-size:12px !important;
    text-align:left !important;
    justify-content:flex-start !important;
    padding:11px 18px !important;
    width:100% !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background:transparent !important;
    color:#A9C4E4 !important;
    font-weight:500 !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background:#17518C !important;
    color:#FFFFFF !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] {{
    background:{BIRU} !important;
    color:#FFFFFF !important;
    font-weight:600 !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background:#0A3260 !important;
    border:1px solid #17518C !important;
    border-radius:8px !important;
    min-height:44px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] div {{
    color:#DCE9F8 !important;
    font-size:12px !important;
}}
[data-baseweb="popover"] li {{
    font-size:12px !important;
    padding:10px 14px !important;
}}

[data-testid="stMetric"] {{
    background:{PUTIH};
    border:1px solid {GARIS};
    border-radius:12px;
    padding:16px 18px;
}}
[data-testid="stMetricLabel"] p {{
    color:{ABU} !important;
    font-size:10px !important;
    font-weight:600 !important;
    text-transform:uppercase;
    letter-spacing:.6px;
}}
[data-testid="stMetricValue"] {{
    color:{NAVY} !important;
    font-size:26px !important;
    font-weight:800 !important;
}}
[data-testid="stMetricDelta"] {{ font-size:10px !important; }}

[data-testid="stPlotlyChart"] {{
    background:{PUTIH};
    border:1px solid {GARIS};
    border-radius:12px;
    padding:4px;
}}
[data-testid="stDataFrame"] {{
    border:1px solid {GARIS};
    border-radius:12px;
}}

.main button[kind="secondary"] {{
    background:{PUTIH} !important;
    border:1px solid #D6DFEC !important;
    color:{NAVY} !important;
    border-radius:8px !important;
    font-size:11px !important;
    font-weight:600 !important;
}}
.main button[kind="secondary"]:hover {{
    background:{NAVY} !important;
    color:#FFFFFF !important;
}}
.main button[kind="primary"] {{
    border-radius:8px !important;
    font-size:11px !important;
    font-weight:700 !important;
}}
.main [data-testid="stDownloadButton"] button {{
    background:{BIRU} !important;
    border:none !important;
    color:#FFFFFF !important;
    border-radius:8px !important;
    font-size:11px !important;
    font-weight:600 !important;
}}
.main [data-testid="stDownloadButton"] button:hover {{
    background:#0D47A1 !important;
}}
.main [data-testid="stFileUploader"] {{
    background:{PUTIH};
    border:1.5px dashed {BIRU};
    border-radius:12px;
    padding:8px;
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    xl = pd.ExcelFile('ARIMA_PLN_PowerBI.xlsx')
    return (pd.read_excel(xl, sheet_name='Historis'),
            pd.read_excel(xl, sheet_name='Metrik'),
            pd.read_excel(xl, sheet_name='Peramalan'),
            pd.read_excel(xl, sheet_name='Penyebab'),
            pd.read_excel(xl, sheet_name='Sumber'))

hist, metrik, peramalan, penyebab, sumber = load_data()

if 'halaman' not in st.session_state:
    st.session_state.halaman = 'Ringkasan'
if 'model_terpilih' not in st.session_state:
    st.session_state.model_terpilih = 'SARIMAX Optimal'
if 'hasil_ramalan_baru' not in st.session_state:
    st.session_state.hasil_ramalan_baru = None
if 'ts_baru_terakhir' not in st.session_state:
    st.session_state.ts_baru_terakhir = None


# ═══════════════ SIDEBAR ═══════════════
with st.sidebar:
    # --- Logo ---
    if os.path.exists('logo_haleyora.png'):
        with open('logo_haleyora.png', 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div style="background:#FFFFFF;padding:18px;text-align:center;'
            f'border-radius:0 0 12px 12px;margin-bottom:18px;">'
            f'<img src="data:image/png;base64,{b64}" style="width:130px;">'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:#FFFFFF;padding:24px;text-align:center;'
            'border-radius:0 0 12px 12px;margin-bottom:18px;">'
            '<span style="color:#0B3B6F;font-size:14px;font-weight:800;">'
            'haleyora</span><span style="color:#F9A825;font-size:14px;'
            'font-weight:800;">power</span></div>', unsafe_allow_html=True)

    # --- Judul Dashboard ---
    st.markdown(
        '<div style="padding:0 8px 16px;">'
        '<div style="color:#FFFFFF;font-size:12.5px;font-weight:700;'
        'line-height:1.4;">Dashboard Gangguan Kabel SR</div>'
        '<div style="color:#7FA6D4;font-size:9.5px;margin-top:3px;">'
        'Peramalan Berbasis ARIMA & SARIMAX</div></div>',
        unsafe_allow_html=True)

    # --- Label Navigasi ---
    st.markdown(
        '<div style="color:#5B87BC;font-size:9px;letter-spacing:1.2px;'
        'font-weight:700;padding:0 8px 22px;'
        'border-top:1px solid #17518C;padding-top:14px;">NAVIGASI</div>',
        unsafe_allow_html=True)

    # --- Menu Navigasi (menu baru: Perbarui & Ramalkan) ---
    for nama in ["Ringkasan", "Tren Harian", "Peramalan", "Perbarui & Ramalkan",
                 "Analisis Penyebab", "Perbandingan Model", "Akurasi Model"]:
        aktif = st.session_state.halaman == nama
        if st.button(nama, key=f"menu_{nama}", use_container_width=True,
                     type="primary" if aktif else "secondary"):
            st.session_state.halaman = nama
            st.rerun()

    # --- Label Filter ---
    st.markdown(
        '<div style="color:#5B87BC;font-size:9px;letter-spacing:1.2px;'
        'font-weight:700;padding:18px 8px 8px;margin-top:8px;'
        'border-top:1px solid #17518C;">PILIH PERIODE</div>',
        unsafe_allow_html=True)

    # --- Dropdown Filter
    with st.container():
        st.markdown('<div style="padding:0 8px;">', unsafe_allow_html=True)
        opsi = ['Semua'] + list(
            pd.to_datetime(hist.iloc[:, 0]).dt.strftime('%b %Y').unique())
        pilih_bulan = st.selectbox("p", opsi, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Status Model ---
    st.markdown(
        '<div style="margin:20px 8px 0;padding-top:16px;'
        'border-top:1px solid #17518C;">'
        '<div style="background:#0A3260;border:1px solid #17518C;'
        'border-radius:10px;padding:14px;">'
        '<div style="display:flex;align-items:center;gap:7px;'
        'margin-bottom:8px;">'
        '<div style="width:7px;height:7px;border-radius:50%;'
        'background:#4ADE80;"></div>'
        '<span style="color:#4ADE80;font-size:10px;font-weight:700;">'
        'Model Tervalidasi</span></div>'
        '<div style="color:#7FA6D4;font-size:9px;line-height:1.9;">'
        'Ljung-Box p &gt; 0,05<br>SARIMAX(0,1,3) + eksogen<br>MASE 1,288</div>'
        '</div></div>', unsafe_allow_html=True)


hist_f = hist.copy()
hist_f.iloc[:, 0] = pd.to_datetime(hist_f.iloc[:, 0])
if pilih_bulan != 'Semua':
    hist_f = hist_f[hist_f.iloc[:, 0].dt.strftime('%b %Y') == pilih_bulan]
kol_tgl, kol_val = hist_f.columns[0], hist_f.columns[1]


kiri, kanan = st.columns([7, 2])
with kiri:
    st.markdown(
        f'<div style="color:{NAVY};font-size:21px;font-weight:800;'
        f'line-height:1.3;">Dashboard Peramalan Gangguan Kabel SR</div>'
        f'<div style="color:{ABU};font-size:11px;margin-top:5px;">'
        f'PT. Haleyora Power Serpong &nbsp;·&nbsp; Metode ARIMA & SARIMAX '
        f'Berbasis Time Series &nbsp;·&nbsp; '
        f'<span style="color:{BIRU};font-weight:600;">{pilih_bulan}</span>'
        f'</div>', unsafe_allow_html=True)
with kanan:
    t1, t2 = st.columns(2)
    with t1:
        if st.button("Muat Ulang", key="reload", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with t2:
        st.download_button(
            "Unduh", key="unduh",
            data=hist_f.to_csv(index=False).encode('utf-8'),
            file_name=f"gangguan_SR_{datetime.now():%Y%m%d}.csv",
            mime="text/csv", use_container_width=True)

st.markdown(f"<hr style='margin:18px 0 22px;border:none;"
            f"border-top:1px solid {GARIS};'>", unsafe_allow_html=True)


def tata(t=280):
    return dict(
        plot_bgcolor=PUTIH, paper_bgcolor=PUTIH,
        font=dict(color=ABU, size=10, family='Inter,sans-serif'),
        height=t, margin=dict(l=20, r=20, t=16, b=40),
        xaxis=dict(showgrid=False, tickfont=dict(size=9.5, color=ABU),
                   linecolor=GARIS, showline=True),
        yaxis=dict(gridcolor=GARIS, tickfont=dict(size=9.5, color=ABU),
                   zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0,
                    font=dict(size=10, color=ABU),
                    bgcolor='rgba(0,0,0,0)'),
        hoverlabel=dict(bgcolor=NAVY, font=dict(color='white', size=11)))


def judul(teks, sub=""):
    baris = (f'<div style="color:{ABU};font-size:10px;margin-top:3px;">'
             f'{sub}</div>') if sub else ''
    st.markdown(
        f'<div style="margin:0 0 12px;">'
        f'<div style="color:{NAVY};font-size:13px;font-weight:700;">'
        f'{teks}</div>{baris}'
        f'<div style="width:26px;height:3px;background:{KUNING};'
        f'border-radius:2px;margin-top:7px;"></div></div>',
        unsafe_allow_html=True)


def kpi():
    k1, k2, k3, k4 = st.columns(4)
    total = f"{int(hist_f[kol_val].sum()):,}".replace(",", ".")
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    mase = float(baris_terbaik['MASE'])
    with k1:
        st.metric("Total Gangguan", total, "kasus tercatat")
    with k2:
        st.metric("Rata-rata Harian",
                  f"{hist_f[kol_val].mean():.2f}".replace(".", ","),
                  "gangguan / hari")
    with k3:
        st.metric("Akurasi MASE", f"{mase:.3f}".replace(".", ","),
                  "model terbaik")
    with k4:
        st.metric("Proyeksi 30 Hari",
                  f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","),
                  "kategori sedang")


def g_tren(t=290):
    f = go.Figure()
    f.add_trace(go.Scatter(
        x=hist_f[kol_tgl], y=hist_f[kol_val], name='Aktual',
        line=dict(color=TOSKA, width=2.2),
        fill='tozeroy', fillcolor='rgba(0,169,165,.08)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y} gangguan<extra></extra>'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'],
        name='Prediksi SARIMAX',
        line=dict(color=ORANYE, width=2, dash='dash'),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>%{y:.1f}<extra></extra>'))
    f.update_layout(**tata(t))
    return f


def g_penyebab(t=290):
    f = px.pie(penyebab.head(5), values='Jumlah', names='Penyebab', hole=.6,
               color_discrete_sequence=[BIRU, TOSKA, KUNING, MERAH, '#94A3B8'])
    f.update_traces(
        textposition='inside', textinfo='percent',
        hovertemplate='<b>%{label}</b><br>%{value:,}<extra></extra>',
        marker=dict(line=dict(color=PUTIH, width=2.5)))
    f.update_layout(
        paper_bgcolor=PUTIH, height=t,
        margin=dict(l=10, r=10, t=16, b=10),
        font=dict(color=ABU, family='Inter,sans-serif'),
        legend=dict(font=dict(size=9, color=ABU)),
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
        fillcolor='rgba(249,168,37,.16)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Interval 95%', hoverinfo='skip'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'],
        name='Prediksi',
        line=dict(color=ORANYE, width=2.5, dash='dash'),
        hovertemplate='<b>%{x|%d %b}</b><br>%{y:.1f}<extra></extra>'))
    L = tata(t)
    L['yaxis']['range'] = [0, 55]
    f.update_layout(**L)
    return f


def g_bulan(t=250):
    h = hist.copy()
    h.iloc[:, 0] = pd.to_datetime(h.iloc[:, 0])
    h['Bulan'] = h.iloc[:, 0].dt.strftime('%b %Y')
    b = h.groupby('Bulan', sort=False)[h.columns[1]].sum().reset_index()
    b.columns = ['Bulan', 'Jumlah']
    mx = b['Jumlah'].max()
    f = go.Figure(go.Bar(
        x=b['Bulan'], y=b['Jumlah'],
        marker_color=[KUNING if v == mx else BIRU for v in b['Jumlah']],
        marker_line_width=0,
        hovertemplate='<b>%{x}</b><br>%{y:,}<extra></extra>'))
    L = tata(t)
    L['xaxis'].update(tickangle=30, tickfont=dict(size=8.5, color=ABU))
    f.update_layout(**L)
    return f


def b_sumber():
    total_s = sumber['Jumlah'].sum()
    warna = [BIRU, TOSKA, KUNING, MERAH, '#94A3B8', '#64748B']
    html = ""
    for i, (_, r) in enumerate(sumber.head(6).iterrows()):
        pct = r['Jumlah'] / total_s * 100
        jml = f"{r['Jumlah']:,}".replace(",", ".")
        nama = str(r['Sumber_Lapor'])[:22]
        html += (
            f'<div style="margin-bottom:14px;">'
            f'<div style="display:flex;justify-content:space-between;'
            f'margin-bottom:5px;">'
            f'<span style="color:{NAVY};font-size:10.5px;">{nama}</span>'
            f'<span style="color:{ABU};font-size:10px;font-weight:600;">'
            f'{jml} · {pct:.1f}%</span></div>'
            f'<div style="background:#EEF2F8;border-radius:5px;height:7px;">'
            f'<div style="background:{warna[i % len(warna)]};height:7px;'
            f'border-radius:5px;width:{min(pct, 100):.1f}%;"></div>'
            f'</div></div>')
    return html


def t_metrik():
    def sorot(x):
        return [f'background-color:#DCFCE7;color:{HIJAU};font-weight:700'
                if v == x.min() else
                f'color:{MERAH};font-weight:600' if v == x.max() else ''
                for v in x]
    st.dataframe(
        metrik.style.apply(sorot, subset=['MASE']).format({
            'MAE': '{:.2f}', 'RMSE': '{:.2f}', 'sMAPE(%)': '{:.2f}%',
            'R²': '{:.4f}', 'MASE': '{:.3f}'}),
        use_container_width=True, hide_index=True)


def catatan():
    st.markdown(
        f'<div style="background:{PUTIH};border:1px solid {GARIS};'
        f'border-left:4px solid {KUNING};border-radius:0 10px 10px 0;'
        f'padding:14px 18px;margin-top:10px;">'
        f'<div style="color:{NAVY};font-size:11px;font-weight:700;'
        f'margin-bottom:6px;">Interpretasi Hasil</div>'
        f'<div style="color:{ABU};font-size:10.5px;line-height:1.8;">'
        f'Model SARIMAX(0,1,3) dengan variabel eksogen kalender menghasilkan '
        f'MASE 1,288 — turun dari ARIMA(1,1,1) yang sebesar 1,592, dan jauh '
        f'lebih baik dibanding naive forecast (2,177). Nilai R² meningkat '
        f'dari negatif menjadi 0,3268, menunjukkan penambahan variabel '
        f'eksogen (kalender, hari libur) memberi kontribusi nyata terhadap '
        f'akurasi peramalan, meski masih terbuka ruang optimasi lebih lanjut '
        f'menggunakan variabel eksogen yang lebih kuat seperti data cuaca.'
        f'</div></div>', unsafe_allow_html=True)


def simulasi_skenario():
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Simulasi Skenario Faktor Eksternal",
          "Ilustrasi dampak faktor eksogen tambahan di luar model")

    st.markdown(
        f'<div style="background:{PUTIH};border:1px solid {GARIS};'
        f'border-left:4px solid {BIRU};border-radius:0 10px 10px 0;'
        f'padding:12px 16px;margin-bottom:14px;">'
        f'<div style="color:{ABU};font-size:10.5px;line-height:1.7;">'
        f'Model SARIMAX sudah menangkap sebagian faktor eksogen (kalender, '
        f'hari libur). Simulasi ini menggeser hasil prediksi secara '
        f'proporsional untuk mengilustrasikan potensi dampak faktor cuaca '
        f'yang belum dimodelkan, bukan hasil pemodelan baru.</div></div>',
        unsafe_allow_html=True)

    skenario = st.select_slider(
        "Skenario Faktor Eksternal",
        options=["Musim Kering (-30%)", "Normal (0%)",
                 "Musim Hujan (+20%)", "Cuaca Ekstrem (+50%)"],
        value="Normal (0%)"
    )

    faktor = {
        "Musim Kering (-30%)": -0.30, "Normal (0%)": 0.0,
        "Musim Hujan (+20%)": 0.20, "Cuaca Ekstrem (+50%)": 0.50
    }[skenario]

    df_sim = peramalan.copy()
    df_sim['Prediksi_Sim'] = (df_sim['Prediksi'] * (1 + faktor)).clip(lower=0)

    f = go.Figure()
    f.add_trace(go.Scatter(
        x=df_sim['Tanggal'], y=df_sim['Prediksi'],
        name='Prediksi SARIMAX (asli)',
        line=dict(color=ABU, width=2, dash='dot')))
    f.add_trace(go.Scatter(
        x=df_sim['Tanggal'], y=df_sim['Prediksi_Sim'],
        name=f'Simulasi: {skenario}',
        line=dict(color=ORANYE, width=2.5),
        fill='tonexty', fillcolor='rgba(245,166,35,.12)'))
    f.update_layout(**tata(280))
    st.plotly_chart(f, use_container_width=True)

    selisih = df_sim['Prediksi_Sim'].mean() - df_sim['Prediksi'].mean()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Rata-rata Prediksi Asli",
                  f"{df_sim['Prediksi'].mean():.1f}", "gangguan/hari")
    with c2:
        st.metric("Rata-rata Skenario",
                  f"{df_sim['Prediksi_Sim'].mean():.1f}",
                  f"{'+' if selisih >= 0 else ''}{selisih:.1f} vs asli")


# ═══════════════ FITUR: TOGGLE PERBANDINGAN MODEL ═══════════════

def g_progres_optimasi():
    """Bar chart penurunan MASE dari ARIMA ke SARIMAX"""
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    palet = [ABU, BIRU, HIJAU, '#94A3B8']
    warna_bar = [palet[i % len(palet)] for i in range(len(df_prog))]

    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['MASE'],
        marker_color=warna_bar,
        text=df_prog['MASE'].round(3),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>MASE: %{y:.3f}<extra></extra>'))
    f.add_hline(y=1.0, line_dash='dot', line_color=MERAH,
                annotation_text='Ambang unggul dari naive (MASE=1,0)',
                annotation_font_size=9, annotation_font_color=MERAH)
    L = tata(300)
    L['yaxis']['title'] = 'MASE'
    L['xaxis']['tickfont'] = dict(size=8, color=ABU)
    f.update_layout(**L)
    return f


def g_progres_r2():
    """Bar chart peningkatan R2 dari ARIMA ke SARIMAX"""
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    warna_bar = [MERAH if v < 0 else HIJAU for v in df_prog['R²']]

    f = go.Figure(go.Bar(
        x=df_prog['Model'], y=df_prog['R²'],
        marker_color=warna_bar,
        text=df_prog['R²'].round(4),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>R²: %{y:.4f}<extra></extra>'))
    f.add_hline(y=0, line_dash='dot', line_color=ABU)
    L = tata(300)
    L['yaxis']['title'] = 'R²'
    L['xaxis']['tickfont'] = dict(size=8, color=ABU)
    f.update_layout(**L)
    return f


def kartu_model_toggle():
    """Tombol interaktif untuk membandingkan model secara dinamis.
    Nama-nama model di sini HARUS SAMA PERSIS dengan isi kolom 'Model'
    pada sheet Metrik hasil ekspor notebook."""

    opsi_model = {
        'ARIMA Dasar': {
            'nama_metrik': 'ARIMA(1, 1, 1)',
            'deskripsi': 'Model dasar tanpa variabel tambahan — hanya mempelajari pola historis data gangguan itu sendiri.',
            'warna': ABU
        },
        'SARIMAX Dasar': {
            'nama_metrik': 'SARIMAX(1, 1, 1) + kalender dasar',
            'deskripsi': 'Ditambahkan variabel kalender (akhir pekan, awal/akhir bulan) sebagai informasi eksternal pertama.',
            'warna': BIRU
        },
        'SARIMAX Optimal': {
            'nama_metrik': 'SARIMAX(0, 1, 3) + kalender lengkap',
            'deskripsi': 'Order model dioptimasi ulang dan ditambahkan fitur hari libur nasional — hasil terbaik dari seluruh eksperimen.',
            'warna': HIJAU
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
            f"pada sheet Metrik. Pastikan nama model di Excel sama persis."
        )
        return

    m = baris.iloc[0]

    st.markdown(
        f'<div style="background:{PUTIH};border:2px solid {pilihan["warna"]};'
        f'border-radius:14px;padding:20px;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">'
        f'<span style="color:{NAVY};font-size:14px;font-weight:800;">'
        f'{st.session_state.model_terpilih}</span>'
        f'<span style="background:{pilihan["warna"]}22;color:{pilihan["warna"]};'
        f'padding:4px 12px;border-radius:20px;font-size:10px;font-weight:700;">'
        f'{pilihan["nama_metrik"]}</span></div>'
        f'<div style="color:{ABU};font-size:11px;line-height:1.7;">'
        f'{pilihan["deskripsi"]}</div>'
        f'</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("MAE", f"{m['MAE']:.2f}".replace(".", ","))
    with k2:
        st.metric("RMSE", f"{m['RMSE']:.2f}".replace(".", ","))
    with k3:
        st.metric("sMAPE", f"{m['sMAPE(%)']:.2f}%".replace(".", ","))
    with k4:
        st.metric("R²", f"{m['R²']:.4f}".replace(".", ","))
    with k5:
        st.metric("MASE", f"{m['MASE']:.3f}".replace(".", ","))


# ═══════════════ FITUR BARU: PERBARUI & RAMALKAN (ROLLING FORECAST) ═══════════════

def proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru, jumlah_hari=30, order_model=(0, 1, 3)):
    """Membersihkan data yang diunggah, melatih ulang model SARIMAX, dan
    menghasilkan peramalan sejumlah 'jumlah_hari' dari titik data terbaru
    yang diunggah. Mengembalikan dict berisi ts_baru, hasil peramalan,
    dan info model."""
    import holidays as hol
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    kerja = df_baru[[kol_tgl_baru, kol_val_baru]].copy()
    kerja[kol_tgl_baru] = pd.to_datetime(kerja[kol_tgl_baru], dayfirst=True, errors='coerce')
    kerja = kerja.dropna(subset=[kol_tgl_baru])

    # Agregasi ke harian apabila data masih berbentuk satu baris per laporan
    if kerja[kol_tgl_baru].duplicated().any():
        agregasi = kerja.groupby(kerja[kol_tgl_baru].dt.normalize()).size()
        ts_baru = agregasi.rename('jumlah')
    else:
        ts_baru = kerja.set_index(kol_tgl_baru)[kol_val_baru]

    ts_baru = ts_baru.asfreq('D')
    ts_baru = ts_baru.interpolate(method='linear').round()

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

    model_baru = SARIMAX(
        ts_baru, exog=exog_baru, order=order_model,
        enforce_stationarity=False, enforce_invertibility=False
    ).fit(disp=False, maxiter=1000, method='powell')

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

    return {
        'ts_baru': ts_baru,
        'hasil': hasil_baru,
        'order': order_model,
        'aic': model_baru.aic,
    }


def halaman_perbarui_ramalkan():
    st.markdown(
        f'<div style="background:{PUTIH};border:1px solid {GARIS};'
        f'border-left:4px solid {BIRU};border-radius:0 10px 10px 0;'
        f'padding:14px 18px;margin-bottom:18px;">'
        f'<div style="color:{NAVY};font-size:11px;font-weight:700;'
        f'margin-bottom:6px;">Peramalan Bergulir (Rolling Forecast)</div>'
        f'<div style="color:{ABU};font-size:10.5px;line-height:1.8;">'
        f'Fitur ini memungkinkan sistem melatih ulang model SARIMAX secara '
        f'otomatis menggunakan data gangguan terbaru yang diunggah, kemudian '
        f'menghasilkan peramalan dari titik data paling akhir. '
        f'Dengan mekanisme ini, dashboard dapat digunakan untuk meramalkan '
        f'periode berikutnya kapan pun data baru tersedia, tanpa perlu '
        f'mengubah kode program.</div></div>', unsafe_allow_html=True)

    # ═══ Panduan rentang yang disarankan (gauge visual) ═══
    st.markdown(
        f'''<div style="background:{PUTIH};border:1px solid {GARIS};
             border-radius:12px;padding:16px 20px;margin-bottom:18px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="color:{NAVY};font-size:11.5px;font-weight:700;">
                    📏 Panduan Rentang Peramalan
                </span>
                <span style="color:{ABU};font-size:9.5px;">berdasarkan panjang data latih 209 hari</span>
            </div>
            <div style="display:flex;height:10px;border-radius:6px;overflow:hidden;margin-bottom:8px;">
                <div style="width:35%;background:{HIJAU};"></div>
                <div style="width:65%;background:{KUNING};"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:9px;color:{ABU};margin-bottom:14px;">
                <span>7 hari</span><span style="margin-left:-10px;">42 hari</span><span>120 hari</span>
            </div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div style="flex:1;min-width:220px;background:#F0FDF4;border-radius:8px;padding:10px 14px;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:{HIJAU};"></div>
                        <span style="color:{HIJAU};font-size:10.5px;font-weight:700;">7–42 HARI · DISARANKAN</span>
                    </div>
                    <div style="color:#166534;font-size:10px;line-height:1.6;">
                        Interval kepercayaan masih wajar. Hasil dapat dijadikan
                        acuan perencanaan operasional.
                    </div>
                </div>
                <div style="flex:1;min-width:220px;background:#FFFBEB;border-radius:8px;padding:10px 14px;">
                    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:{KUNING};"></div>
                        <span style="color:#92400E;font-size:10.5px;font-weight:700;">43–120 HARI · HANYA ILUSTRASI</span>
                    </div>
                    <div style="color:#92400E;font-size:10px;line-height:1.6;">
                        Interval kepercayaan melebar signifikan. Tersedia untuk
                        eksplorasi, bukan untuk acuan keputusan.
                    </div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)

    file_baru = st.file_uploader(
        "Unggah data gangguan (format Excel atau CSV)",
        type=['xlsx', 'csv'],
        help="Data dapat berupa satu baris per laporan (akan diagregasi otomatis) "
             "atau sudah berupa rekap harian."
    )

    if file_baru is not None:
        try:
            if file_baru.name.lower().endswith('.csv'):
                df_baru = pd.read_csv(file_baru)
            else:
                df_baru = pd.read_excel(file_baru)

            st.success(f"✅ Berkas berhasil dimuat — {len(df_baru):,} baris, {df_baru.shape[1]} kolom")

            with st.expander("Pratinjau data yang diunggah", expanded=False):
                st.dataframe(df_baru.head(10), use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                kol_tgl_baru = st.selectbox("Kolom tanggal", df_baru.columns, key="pilih_kol_tgl")
            with c2:
                kol_val_baru = st.selectbox("Kolom jumlah gangguan (isi angka bebas jika data per-laporan)",
                                             df_baru.columns, key="pilih_kol_val")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            jumlah_hari = st.slider(
                "Jumlah hari yang diramalkan ke depan",
                min_value=7, max_value=120, value=30, step=7,
                help="Lihat panduan rentang di bagian atas halaman. Disarankan "
                     "≤ 42 hari untuk hasil yang dapat dijadikan acuan."
            )
            if jumlah_hari <= 42:
                st.markdown(
                    f'<div style="background:#DCFCE7;border-radius:8px;padding:8px 14px;'
                    f'margin-top:6px;margin-bottom:4px;display:flex;align-items:center;gap:6px;">'
                    f'<span style="color:#166534;font-size:11px;font-weight:600;">'
                    f'✅ Dalam rentang disarankan — hasil dapat dijadikan acuan.</span></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="background:#FEF3C7;border-radius:8px;padding:8px 14px;'
                    f'margin-top:6px;margin-bottom:4px;display:flex;align-items:center;gap:6px;">'
                    f'<span style="color:#92400E;font-size:11px;font-weight:600;">'
                    f'⚠️ Melebihi rentang disarankan — hasil hanya untuk ilustrasi, '
                    f'bukan acuan keputusan.</span></div>',
                    unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            jalankan = st.button("🔄 Latih Ulang Model dan Ramalkan",
                                  type="primary", use_container_width=False)

            if jalankan:
                with st.spinner(f"Melatih ulang model SARIMAX dan meramalkan {jumlah_hari} hari ke depan..."):
                    try:
                        out = proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru,
                                                  jumlah_hari=jumlah_hari)
                        st.session_state.hasil_ramalan_baru = out['hasil']
                        st.session_state.ts_baru_terakhir = out['ts_baru']
                        st.session_state.info_model_baru = out
                    except Exception as e:
                        st.error(f"Gagal memproses data: {e}")
                        st.session_state.hasil_ramalan_baru = None

        except Exception as e:
            st.error(f"Terjadi kesalahan membaca berkas: {e}")

    # ═══ Tampilkan hasil apabila sudah ada ═══
    if st.session_state.hasil_ramalan_baru is not None:
        hasil_baru = st.session_state.hasil_ramalan_baru
        ts_baru = st.session_state.ts_baru_terakhir
        info = st.session_state.info_model_baru

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#DCFCE7;border-radius:10px;padding:12px 16px;'
            f'margin-bottom:16px;">'
            f'<div style="color:{HIJAU};font-size:12px;font-weight:700;">'
            f'✅ Model berhasil dilatih ulang dari {len(ts_baru)} hari data '
            f'({ts_baru.index[0].strftime("%d %b %Y")} — {ts_baru.index[-1].strftime("%d %b %Y")})'
            f'</div></div>', unsafe_allow_html=True)

        n_hari = len(hasil_baru)
        lebar_ci = (hasil_baru['CI_Atas'] - hasil_baru['CI_Bawah']).mean()

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Order Model", f"SARIMAX{info['order']}", "otomatis")
        with k2:
            st.metric("Proyeksi Rata-rata",
                       f"{hasil_baru['Prediksi'].mean():.2f}".replace(".", ","),
                       "gangguan / hari")
        with k3:
            st.metric("Periode Peramalan",
                       f"{hasil_baru['Tanggal'].iloc[0].strftime('%d %b')} — {hasil_baru['Tanggal'].iloc[-1].strftime('%d %b %Y')}",
                       f"{n_hari} hari ke depan")
        with k4:
            st.metric("Rata-rata Lebar Interval",
                       f"± {lebar_ci/2:.1f}".replace(".", ","),
                       "kian lebar kian jauh horizon")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        judul(f"Peramalan {n_hari} Hari dari Data Terbaru", "Data aktual dan hasil peramalan bergulir")

        f = go.Figure()
        f.add_trace(go.Scatter(
            x=ts_baru.index[-60:], y=ts_baru.values[-60:],
            name='Data Aktual (Diunggah)', line=dict(color=TOSKA, width=2.2),
            fill='tozeroy', fillcolor='rgba(0,169,165,.08)'))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['CI_Atas'],
            mode='lines', line=dict(color='rgba(0,0,0,0)'),
            showlegend=False, hoverinfo='skip'))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['CI_Bawah'],
            fill='tonexty', mode='lines', fillcolor='rgba(249,168,37,.16)',
            line=dict(color='rgba(0,0,0,0)'), name='Interval 95%', hoverinfo='skip'))
        f.add_trace(go.Scatter(
            x=hasil_baru['Tanggal'], y=hasil_baru['Prediksi'],
            name='Prediksi Baru', line=dict(color=ORANYE, width=2.5, dash='dash')))
        f.update_layout(**tata(380))
        st.plotly_chart(f, use_container_width=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        judul("Tabel Hasil Peramalan Baru", "Rincian prediksi harian")
        tp = hasil_baru.copy()
        tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
        st.dataframe(
            tp.style.format({'Prediksi': '{:.2f}', 'CI_Bawah': '{:.2f}', 'CI_Atas': '{:.2f}'}),
            use_container_width=True, hide_index=True, height=300)

        st.download_button(
            "Unduh Hasil Peramalan Baru", key="unduh_ramalan_baru",
            data=hasil_baru.to_csv(index=False).encode('utf-8'),
            file_name=f"peramalan_bergulir_{datetime.now():%Y%m%d}.csv",
            mime="text/csv")

        st.markdown(
            f'<div style="background:{PUTIH};border:1px solid {GARIS};'
            f'border-left:4px solid {KUNING};border-radius:0 10px 10px 0;'
            f'padding:14px 18px;margin-top:16px;">'
            f'<div style="color:{NAVY};font-size:11px;font-weight:700;'
            f'margin-bottom:6px;">Catatan</div>'
            f'<div style="color:{ABU};font-size:10.5px;line-height:1.8;">'
            f'Hasil di atas dihasilkan dari data yang diunggah pengguna dan '
            f'bersifat demonstrasi mekanisme peramalan bergulir. Apabila '
            f'data yang diunggah berada di luar cakupan periode penelitian '
            f'utama (Januari–September 2025), hasil ini tidak menggantikan '
            f'hasil resmi penelitian, melainkan menunjukkan bahwa sistem '
            f'dapat memproses dan meramalkan data periode mana pun secara '
            f'otomatis.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.info("Unggah berkas data gangguan untuk memulai peramalan bergulir.")


halaman = st.session_state.halaman

if halaman == 'Ringkasan':
    kpi()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        judul("Tren Gangguan Harian", "Aktual vs prediksi SARIMAX")
        st.plotly_chart(g_tren(), use_container_width=True)
    with c2:
        judul("Penyebab Gangguan", "Lima kategori terbanyak")
        st.plotly_chart(g_penyebab(), use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    c3, c4, c5 = st.columns(3)
    with c3:
        judul("Peramalan 30 Hari", "Interval kepercayaan 95%")
        st.plotly_chart(g_ramal(), use_container_width=True)
    with c4:
        judul("Distribusi Bulanan", "Volume per bulan")
        st.plotly_chart(g_bulan(), use_container_width=True)
    with c5:
        judul("Kanal Pelaporan", "Sumber laporan pelanggan")
        st.markdown(b_sumber(), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

elif halaman == 'Tren Harian':
    kpi()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Tren Gangguan Harian", "Data aktual dan prediksi SARIMAX")
    st.plotly_chart(g_tren(420), use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a:
        judul("Distribusi Bulanan", "Volume gangguan per bulan")
        st.plotly_chart(g_bulan(300), use_container_width=True)
    with b:
        judul("Statistik Deskriptif", "Ringkasan periode terpilih")
        s = hist_f[kol_val]
        total = f"{int(s.sum()):,}".replace(",", ".")
        st.markdown(
            f'<div style="background:{PUTIH};border:1px solid {GARIS};'
            f'border-radius:12px;padding:18px;">'
            f'<table style="width:100%;font-size:11.5px;">'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:10px 4px;color:{ABU};">Jumlah observasi</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{NAVY};'
            f'font-weight:700;">{len(s)} hari</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:10px 4px;color:{ABU};">Total gangguan</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{NAVY};'
            f'font-weight:700;">{total}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:10px 4px;color:{ABU};">Rata-rata harian</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{NAVY};'
            f'font-weight:700;">{s.mean():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:10px 4px;color:{ABU};">Standar deviasi</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{NAVY};'
            f'font-weight:700;">{s.std():.2f}</td></tr>'
            f'<tr style="border-bottom:1px solid {GARIS};">'
            f'<td style="padding:10px 4px;color:{ABU};">Nilai minimum</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{NAVY};'
            f'font-weight:700;">{int(s.min())}</td></tr>'
            f'<tr><td style="padding:10px 4px;color:{ABU};">'
            f'Nilai maksimum</td>'
            f'<td style="padding:10px 4px;text-align:right;color:{MERAH};'
            f'font-weight:700;">{int(s.max())}</td></tr>'
            f'</table></div>', unsafe_allow_html=True)

elif halaman == 'Peramalan':
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Proyeksi Rata-rata",
                  f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","),
                  "gangguan / hari")
    with k2:
        st.metric("Batas Bawah CI",
                  f"{peramalan['CI_Bawah'].min():.1f}".replace(".", ","),
                  "interval 95%")
    with k3:
        st.metric("Batas Atas CI",
                  f"{peramalan['CI_Atas'].max():.1f}".replace(".", ","),
                  "interval 95%")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Peramalan 30 Hari ke Depan", "Prediksi beserta interval 95%")
    st.plotly_chart(g_ramal(400), use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
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
        st.markdown(b_sumber(), unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Rincian Penyebab Gangguan", "Seluruh kategori tercatat")
    p = penyebab.copy()
    p['Proporsi (%)'] = (p['Jumlah'] / p['Jumlah'].sum() * 100).round(2)
    st.dataframe(p.head(15), use_container_width=True,
                 hide_index=True, height=380)

elif halaman == 'Perbandingan Model':
    st.markdown(
        f'<div style="background:{PUTIH};border:1px solid {GARIS};'
        f'border-left:4px solid {BIRU};border-radius:0 10px 10px 0;'
        f'padding:14px 18px;margin-bottom:18px;">'
        f'<div style="color:{NAVY};font-size:11px;font-weight:700;'
        f'margin-bottom:6px;">Bandingkan Model Secara Interaktif</div>'
        f'<div style="color:{ABU};font-size:10.5px;line-height:1.8;">'
        f'Klik salah satu tombol di bawah untuk melihat detail performa '
        f'tiap tahap optimasi model, dari ARIMA dasar hingga SARIMAX terbaik.'
        f'</div></div>', unsafe_allow_html=True)

    kartu_model_toggle()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    a, b = st.columns(2)
    with a:
        judul("Perbandingan MASE Seluruh Model", "Semakin rendah semakin baik")
        st.plotly_chart(g_progres_optimasi(), use_container_width=True)
    with b:
        judul("Perbandingan R² Seluruh Model", "Semakin tinggi semakin baik")
        st.plotly_chart(g_progres_r2(), use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Tabel Lengkap Seluruh Model", "ARIMA, SARIMAX, dan baseline")
    t_metrik()

    st.markdown(
        f'<div style="background:{PUTIH};border:1px solid {GARIS};'
        f'border-left:4px solid {HIJAU};border-radius:0 10px 10px 0;'
        f'padding:14px 18px;margin-top:14px;">'
        f'<div style="color:{NAVY};font-size:11px;font-weight:700;'
        f'margin-bottom:6px;">Kesimpulan Optimasi</div>'
        f'<div style="color:{ABU};font-size:10.5px;line-height:1.8;">'
        f'Penambahan variabel eksogen berbasis kalender pada model SARIMAX '
        f'berhasil menurunkan MASE dari 1,592 menjadi 1,288 (turun sekitar '
        f'19%), serta meningkatkan R² dari negatif menjadi 0,3268. Hasil ini '
        f'menunjukkan bahwa faktor di luar pola historis murni turut '
        f'memengaruhi gangguan kabel SR, mendukung rekomendasi penggunaan '
        f'variabel eksogen yang lebih kuat seperti data cuaca pada penelitian '
        f'selanjutnya.</div></div>', unsafe_allow_html=True)

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

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing")
    t_metrik()
    catatan()

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    judul("Validasi Model", "Hasil uji diagnostik residual (model SARIMAX terbaik)")
    v1, v2, v3 = st.columns(3)
    for kol, (label, nilai) in zip(
            [v1, v2, v3],
            [("Ljung-Box Lag 7", "0,812"),
             ("Ljung-Box Lag 14", "0,813"),
             ("Ljung-Box Lag 21", "0,668")]):
        with kol:
            st.markdown(
                f'<div style="background:{PUTIH};border:1px solid {GARIS};'
                f'border-radius:12px;padding:16px;">'
                f'<div style="color:{ABU};font-size:9.5px;'
                f'text-transform:uppercase;letter-spacing:.6px;'
                f'font-weight:600;">{label}</div>'
                f'<div style="color:{HIJAU};font-size:22px;font-weight:800;'
                f'margin:6px 0 4px;">{nilai}</div>'
                f'<div style="color:{ABU};font-size:9.5px;">'
                f'p &gt; 0,05 · white noise</div></div>',
                unsafe_allow_html=True)

st.markdown(
    f'<div style="text-align:center;color:{ABU};font-size:9.5px;'
    f'padding:24px 0 8px;border-top:1px solid {GARIS};margin-top:28px;">'
    f'Dashboard Peramalan Gangguan Kabel Sambungan Rumah &nbsp;·&nbsp; '
    f'PT. Haleyora Power Serpong &nbsp;·&nbsp; SARIMAX(0,1,3) &nbsp;·&nbsp; '
    f'CRISP-DM Framework</div>', unsafe_allow_html=True)
