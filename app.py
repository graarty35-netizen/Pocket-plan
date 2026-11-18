"""
Kalkulator Keuangan - aplikasi Streamlit satu file.

Cara menjalankan:
    pip install streamlit pandas altair
    streamlit run app.py
"""

import pandas as pd
import altair as alt
import streamlit as st

# ----------------------------------------------------------------------------
# Konfigurasi halaman
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kalkulator Keuangan",
    page_icon="💰",
    layout="wide",
)

INK = "#10324A"        # teks utama
BLUE = "#0A84C6"       # warna utama
GREEN = "#12A150"      # pemasukan
RED = "#E5484D"        # pengeluaran
AMBER = "#F59E0B"      # tabungan
BG = "#F3F8FC"         # latar halaman
LINE = "#D9E5EF"       # garis pembatas
PALETTE = [BLUE, "#14B8A6", AMBER, "#8B5CF6", RED, "#EC4899", "#64748B", "#84CC16"]

JENIS_OPTIONS = ["Kebutuhan", "Keinginan", "Tabungan & Utang"]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: {INK};
    }}
    .stApp {{ background: {BG}; }}
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.6rem; max-width: 1180px; }}

    .hero {{
        background: {BLUE};
        color: #fff;
        padding: 1.5rem 1.8rem;
        border-radius: 18px;
        margin-bottom: 1.4rem;
    }}
    .hero h1 {{ color: #fff; font-size: 1.9rem; font-weight: 800; margin: 0 0 .25rem 0; padding: 0; }}
    .hero p  {{ color: #E6F4FC; margin: 0; font-size: 0.98rem; }}

    .section-title {{
        font-size: 1.15rem; font-weight: 700; color: {INK};
        margin: 1.6rem 0 .6rem 0;
    }}
    .hint {{ color: #5B7488; font-size: .88rem; margin: -.2rem 0 .6rem 0; }}

    .card {{
        background: #fff;
        border: 1px solid {LINE};
        border-radius: 14px;
        padding: 1rem 1.2rem;
        height: 100%;
    }}
    .card .label {{ color: #5B7488; font-size: .85rem; font-weight: 600; }}
    .card .value {{ font-size: 1.55rem; font-weight: 800; margin-top: .15rem; }}
    .card .sub   {{ color: #5B7488; font-size: .8rem; margin-top: .15rem; }}

    .panel {{
        background: #fff;
        border: 1px solid {LINE};
        border-radius: 14px;
        padding: 1rem 1.2rem;
    }}

    section[data-testid="stSidebar"] {{ background: #fff; border-right: 1px solid {LINE}; }}
    .stButton > button, .stDownloadButton > button {{
        border-radius: 10px; font-weight: 600; border: 1px solid {LINE};
    }}
    .stButton > button[kind="primary"] {{ background: {BLUE}; border-color: {BLUE}; color: #fff; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Data awal & state
# ----------------------------------------------------------------------------
def empty_income() -> pd.DataFrame:
    return pd.DataFrame(
        {"Sumber": pd.Series(dtype="str"), "Jumlah": pd.Series(dtype="float")}
    )


def empty_expense() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Kategori": pd.Series(dtype="str"),
            "Jenis": pd.Series(dtype="str"),
            "Jumlah": pd.Series(dtype="float"),
        }
    )


def sample_income() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Sumber": ["Gaji", "Pekerjaan sampingan"],
            "Jumlah": [8_000_000.0, 1_500_000.0],
        }
    )


def sample_expense() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Kategori": [
                "Sewa / KPR", "Makan & belanja", "Transportasi", "Listrik & internet",
                "Hiburan", "Nongkrong & jajan", "Dana darurat", "Cicilan",
            ],
            "Jenis": [
                "Kebutuhan", "Kebutuhan", "Kebutuhan", "Kebutuhan",
                "Keinginan", "Keinginan", "Tabungan & Utang", "Tabungan & Utang",
            ],
            "Jumlah": [
                2_200_000.0, 1_800_000.0, 600_000.0, 450_000.0,
                400_000.0, 500_000.0, 800_000.0, 500_000.0,
            ],
        }
    )


def init_state() -> None:
    if "ver" not in st.session_state:
        st.session_state.ver = 0
        st.session_state.income_base = sample_income()
        st.session_state.expense_base = sample_expense()


def reset_all() -> None:
    """Kosongkan semua input. Versi key dinaikkan agar editor benar-benar bersih."""
    st.session_state.income_base = empty_income()
    st.session_state.expense_base = empty_expense()
    st.session_state.ver += 1


def load_sample() -> None:
    st.session_state.income_base = sample_income()
    st.session_state.expense_base = sample_expense()
    st.session_state.ver += 1


init_state()

# ----------------------------------------------------------------------------
# Fungsi bantu
# ----------------------------------------------------------------------------
def rp(x: float) -> str:
    """Format angka ke Rupiah, contoh: Rp 1.250.000"""
    sign = "-" if x < 0 else ""
    return f"{sign}Rp {abs(x):,.0f}".replace(",", ".")


def pct(part: float, whole: float) -> float:
    return (part / whole * 100) if whole > 0 else 0.0


def clean_income(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0.0)
    df["Sumber"] = df["Sumber"].fillna("").astype(str).str.strip()
    df = df[(df["Jumlah"] != 0) | (df["Sumber"] != "")]
    df.loc[df["Sumber"] == "", "Sumber"] = "Tanpa nama"
    return df


def clean_expense(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors="coerce").fillna(0.0)
    df["Kategori"] = df["Kategori"].fillna("").astype(str).str.strip()
    df["Jenis"] = df["Jenis"].where(df["Jenis"].isin(JENIS_OPTIONS), "Kebutuhan")
    df = df[(df["Jumlah"] != 0) | (df["Kategori"] != "")]
    df.loc[df["Kategori"] == "", "Kategori"] = "Tanpa nama"
    return df


def card(label: str, value: str, color: str, sub: str = "") -> str:
    return (
        f'<div class="card"><div class="label">{label}</div>'
        f'<div class="value" style="color:{color}">{value}</div>'
        f'<div class="sub">{sub}</div></div>'
    )


def show_editor(df, **kwargs):
    """Kompatibel dengan versi Streamlit lama maupun baru."""
    try:
        return st.data_editor(df, width="stretch", **kwargs)
    except TypeError:
        return st.data_editor(df, use_container_width=True, **kwargs)


def show_chart(chart):
    try:
        st.altair_chart(chart, width="stretch")
    except TypeError:
        st.altair_chart(chart, use_container_width=True)


def show_table(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Pengaturan")
    periode = st.text_input("Nama periode", value="November 2026")
    target_tabungan = st.slider(
        "Target tabungan (% dari pemasukan)", min_value=0, max_value=60, value=20, step=1
    )
    st.markdown("---")
    st.markdown("### Aksi cepat")
    c1, c2 = st.columns(2)
    c1.button("🔄 Reset", on_click=reset_all, help="Kosongkan semua pemasukan dan pengeluaran")
    c2.button("✨ Contoh", on_click=load_sample, help="Isi dengan data contoh")
    st.caption(
        "Hasil dihitung otomatis setiap kali kamu mengubah angka. "
        "Tambah baris dengan klik baris kosong di bawah tabel, hapus dengan memilih baris lalu tekan Delete."
    )

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>Kalkulator Keuangan</h1>
        <p>Catat pemasukan dan pengeluaran {periode or "bulan ini"}, lalu lihat sisa uang dan rasio tabunganmu secara langsung.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Form input
# ----------------------------------------------------------------------------
col_in, col_out = st.columns(2, gap="large")

with col_in:
    st.markdown('<div class="section-title">Pemasukan</div>', unsafe_allow_html=True)
    st.markdown('<div class="hint">Gaji, bonus, usaha sampingan, dan sumber lainnya.</div>', unsafe_allow_html=True)
    income_raw = show_editor(
        st.session_state.income_base,
        num_rows="dynamic",
        key=f"income_editor_{st.session_state.ver}",
        column_config={
            "Sumber": st.column_config.TextColumn("Sumber pemasukan", required=False),
            "Jumlah": st.column_config.NumberColumn(
                "Jumlah (Rp)", min_value=0, step=50_000, format="Rp %d"
            ),
        },
    )

with col_out:
    st.markdown('<div class="section-title">Pengeluaran</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hint">Pilih jenisnya agar bisa dibandingkan dengan pola 50/30/20.</div>',
        unsafe_allow_html=True,
    )
    expense_raw = show_editor(
        st.session_state.expense_base,
        num_rows="dynamic",
        key=f"expense_editor_{st.session_state.ver}",
        column_config={
            "Kategori": st.column_config.TextColumn("Kategori", required=False),
            "Jenis": st.column_config.SelectboxColumn(
                "Jenis", options=JENIS_OPTIONS, default="Kebutuhan"
            ),
            "Jumlah": st.column_config.NumberColumn(
                "Jumlah (Rp)", min_value=0, step=50_000, format="Rp %d"
            ),
        },
    )

# ----------------------------------------------------------------------------
# Perhitungan
# ----------------------------------------------------------------------------
income = clean_income(income_raw)
expense = clean_expense(expense_raw)

total_income = float(income["Jumlah"].sum())
total_expense = float(expense["Jumlah"].sum())
balance = total_income - total_expense

by_jenis = expense.groupby("Jenis")["Jumlah"].sum().reindex(JENIS_OPTIONS).fillna(0.0)
needs = float(by_jenis["Kebutuhan"])
wants = float(by_jenis["Keinginan"])
saved_items = float(by_jenis["Tabungan & Utang"])

# Tabungan efektif = uang yang dialokasikan ke tabungan/utang + sisa uang bulan ini
savings_total = saved_items + balance
savings_rate = pct(savings_total, total_income)
expense_ratio = pct(total_expense, total_income)

# ----------------------------------------------------------------------------
# Ringkasan
# ----------------------------------------------------------------------------
st.markdown('<div class="section-title">Ringkasan keuangan</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4, gap="medium")
k1.markdown(card("Total pemasukan", rp(total_income), GREEN, f"{len(income)} sumber"), unsafe_allow_html=True)
k2.markdown(
    card("Total pengeluaran", rp(total_expense), RED, f"{expense_ratio:.1f}% dari pemasukan"),
    unsafe_allow_html=True,
)
k3.markdown(
    card(
        "Selisih (sisa uang)",
        rp(balance),
        GREEN if balance >= 0 else RED,
        "Surplus" if balance >= 0 else "Defisit",
    ),
    unsafe_allow_html=True,
)
k4.markdown(
    card("Rasio tabungan", f"{savings_rate:.1f}%", AMBER, f"Target {target_tabungan}%"),
    unsafe_allow_html=True,
)

st.write("")
if total_income <= 0:
    st.info("Masukkan minimal satu sumber pemasukan untuk melihat analisis.")
elif balance < 0:
    st.error(
        f"Pengeluaranmu melebihi pemasukan sebesar {rp(abs(balance))}. "
        "Coba kurangi kategori berjenis Keinginan terlebih dahulu."
    )
elif savings_rate >= target_tabungan:
    st.success(
        f"Bagus! Rasio tabunganmu {savings_rate:.1f}% sudah mencapai target {target_tabungan}%."
    )
else:
    kurang = pct(target_tabungan - savings_rate, 100) * total_income
    st.warning(
        f"Rasio tabunganmu {savings_rate:.1f}%, masih di bawah target {target_tabungan}%. "
        f"Tambahkan sekitar {rp(kurang)} ke tabungan agar target tercapai."
    )

# ----------------------------------------------------------------------------
# Grafik & pola 50/30/20
# ----------------------------------------------------------------------------
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="section-title">Ke mana uangmu pergi</div>', unsafe_allow_html=True)
    by_cat = (
        expense[expense["Jumlah"] > 0]
        .groupby("Kategori", as_index=False)["Jumlah"]
        .sum()
        .sort_values("Jumlah", ascending=False)
    )
    if by_cat.empty:
        st.caption("Belum ada pengeluaran untuk ditampilkan.")
    else:
        by_cat["Persen"] = by_cat["Jumlah"] / by_cat["Jumlah"].sum()
        donut = (
            alt.Chart(by_cat)
            .mark_arc(innerRadius=70, stroke="#fff", strokeWidth=2)
            .encode(
                theta=alt.Theta("Jumlah:Q"),
                color=alt.Color(
                    "Kategori:N",
                    scale=alt.Scale(range=PALETTE),
                    legend=alt.Legend(orient="bottom", columns=2, title=None),
                ),
                tooltip=[
                    alt.Tooltip("Kategori:N"),
                    alt.Tooltip("Jumlah:Q", format=",.0f", title="Jumlah (Rp)"),
                    alt.Tooltip("Persen:Q", format=".1%", title="Porsi"),
                ],
            )
            .properties(height=340)
            .configure_view(strokeWidth=0)
            .configure(background="transparent")
        )
        show_chart(donut)

with right:
    st.markdown('<div class="section-title">Cek pola 50 / 30 / 20</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hint">Acuan umum: 50% kebutuhan, 30% keinginan, 20% tabungan.</div>',
        unsafe_allow_html=True,
    )
    if total_income <= 0:
        st.caption("Isi pemasukan dulu untuk melihat perbandingan.")
    else:
        rows = [
            ("Kebutuhan", pct(needs, total_income), 50, "maks"),
            ("Keinginan", pct(wants, total_income), 30, "maks"),
            ("Tabungan", savings_rate, 20, "min"),
        ]
        for name, actual, ideal, mode in rows:
            ok = actual <= ideal if mode == "maks" else actual >= ideal
            badge = "✅ sesuai" if ok else "⚠️ perlu dicek"
            st.markdown(
                f"**{name}** &nbsp; {actual:.1f}% dari pemasukan "
                f"<span style='color:#5B7488'>(acuan {ideal}%)</span> &nbsp; {badge}",
                unsafe_allow_html=True,
            )
            st.progress(max(0.0, min(actual / 100, 1.0)))

# ----------------------------------------------------------------------------
# Rincian & unduh
# ----------------------------------------------------------------------------
st.markdown('<div class="section-title">Rincian pengeluaran per kategori</div>', unsafe_allow_html=True)

if expense.empty:
    st.caption("Belum ada data pengeluaran.")
else:
    detail = expense.copy()
    detail["% dari pemasukan"] = detail["Jumlah"].apply(lambda v: round(pct(v, total_income), 1))
    detail["% dari pengeluaran"] = detail["Jumlah"].apply(lambda v: round(pct(v, total_expense), 1))
    detail = detail.sort_values("Jumlah", ascending=False)
    show = detail.copy()
    show["Jumlah"] = show["Jumlah"].apply(rp)
    show_table(show)

    summary = pd.DataFrame(
        {
            "Keterangan": [
                "Periode", "Total pemasukan", "Total pengeluaran",
                "Selisih", "Rasio tabungan (%)",
            ],
            "Nilai": [
                periode, total_income, total_expense, balance, round(savings_rate, 1),
            ],
        }
    )
    csv = summary.to_csv(index=False) + "\n" + detail.to_csv(index=False)
    st.download_button(
        "⬇️ Unduh ringkasan (CSV)",
        data=csv.encode("utf-8"),
        file_name=f"ringkasan_keuangan_{(periode or 'periode').replace(' ', '_')}.csv",
        mime="text/csv",
    )

st.caption("Kalkulator ini hanya alat bantu perencanaan dan bukan nasihat keuangan profesional.")
