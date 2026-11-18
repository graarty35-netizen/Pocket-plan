"""
Kalkulator Keuangan (tema gelap, minimalis) - aplikasi Streamlit satu file.

Cara menjalankan:
    pip install streamlit pandas
    streamlit run app.py
"""

import html

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kalkulator Keuangan", page_icon="💰", layout="centered")

# ----------------------------------------------------------------------------
# Tema gelap (semua komponen memakai input bawaan agar mudah diberi warna)
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, .stApp, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: #000000 !important;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] { background: #0A0A0A !important; border-right: 1px solid #1F1F1F; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2.2rem; max-width: 820px; }

    h1, h2, h3, p, label, span, li, div { color: #FFFFFF; }
    .muted { color: #8C8C8C !important; font-size: .85rem; }

    .title { font-size: 2rem; font-weight: 800; letter-spacing: -.02em; margin: 0; }
    .subtitle { color: #8C8C8C; margin: .2rem 0 1.6rem 0; }
    .section { font-size: 1.05rem; font-weight: 700; margin: 2rem 0 .7rem 0; }

    /* Input */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background: #111111 !important; border-color: #2A2A2A !important; border-radius: 10px !important;
    }
    input { color: #FFFFFF !important; background: #111111 !important; }
    input::placeholder { color: #5E5E5E !important; }
    .stNumberInput button { background: #111111 !important; color: #FFFFFF !important; border-color: #2A2A2A !important; }

    /* Tombol */
    .stButton > button, .stDownloadButton > button {
        background: #111111; color: #FFFFFF; border: 1px solid #2A2A2A;
        border-radius: 10px; font-weight: 600;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { border-color: #FFFFFF; color: #FFFFFF; }

    /* Kartu angka */
    .card { background: #0D0D0D; border: 1px solid #222222; border-radius: 14px; padding: 1.1rem 1.3rem; }
    .card .label { color: #8C8C8C; font-size: .82rem; font-weight: 600; }
    .card .value { font-size: 1.5rem; font-weight: 800; margin-top: .25rem; }

    /* Tabel rincian */
    table.detail { width: 100%; border-collapse: collapse; }
    table.detail th { text-align: left; color: #8C8C8C; font-weight: 600; font-size: .82rem;
                      padding: .6rem .4rem; border-bottom: 1px solid #2A2A2A; }
    table.detail td { padding: .7rem .4rem; border-bottom: 1px solid #1A1A1A; }
    table.detail .num { text-align: right; font-variant-numeric: tabular-nums; }
    table.detail tr.total td { font-weight: 800; border-bottom: none; border-top: 1px solid #2A2A2A; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------
def new_row(name: str = "", amount: int = 0) -> dict:
    st.session_state.next_id += 1
    return {"id": st.session_state.next_id, "name": name, "amount": amount}


def sample_rows():
    income = [new_row("Gaji", 8_000_000), new_row("Pekerjaan sampingan", 1_500_000)]
    expense = [
        new_row("Sewa / KPR", 2_200_000),
        new_row("Makan & belanja", 1_800_000),
        new_row("Transportasi", 600_000),
        new_row("Listrik & internet", 450_000),
        new_row("Hiburan", 400_000),
    ]
    return income, expense


if "next_id" not in st.session_state:
    st.session_state.next_id = 0
    st.session_state.income, st.session_state.expense = sample_rows()


def add_row(kind: str) -> None:
    st.session_state[kind].append(new_row())


def delete_row(kind: str, rid: int) -> None:
    st.session_state[kind] = [r for r in st.session_state[kind] if r["id"] != rid]


def reset_all() -> None:
    st.session_state.income = [new_row()]
    st.session_state.expense = [new_row()]


def load_sample() -> None:
    st.session_state.income, st.session_state.expense = sample_rows()


# ----------------------------------------------------------------------------
# Fungsi bantu
# ----------------------------------------------------------------------------
def rp(x: float) -> str:
    sign = "-" if x < 0 else ""
    return f"{sign}Rp {abs(x):,.0f}".replace(",", ".")


def render_rows(kind: str, name_label: str, placeholder: str):
    """Tampilkan baris input dan kembalikan (daftar entri, total)."""
    h1, h2, _ = st.columns([5, 3, 1])
    h1.markdown(f'<span class="muted">{name_label}</span>', unsafe_allow_html=True)
    h2.markdown('<span class="muted">Jumlah (Rp)</span>', unsafe_allow_html=True)

    entries = []
    for r in st.session_state[kind]:
        c1, c2, c3 = st.columns([5, 3, 1], vertical_alignment="center")
        name = c1.text_input(
            name_label, value=r["name"], placeholder=placeholder,
            key=f"{kind}_n_{r['id']}", label_visibility="collapsed",
        )
        amount = c2.number_input(
            "Jumlah", min_value=0, value=int(r["amount"]), step=50_000,
            key=f"{kind}_a_{r['id']}", label_visibility="collapsed",
        )
        c3.button("✕", key=f"{kind}_d_{r['id']}", on_click=delete_row, args=(kind, r["id"]),
                  help="Hapus baris")
        if name.strip() or amount:
            entries.append((name.strip() or "Tanpa nama", int(amount)))

    st.button("+ Tambah baris", key=f"add_{kind}", on_click=add_row, args=(kind,))
    return entries, sum(a for _, a in entries)


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Pengaturan")
    periode = st.text_input("Periode", value="November 2026")
    st.button("Reset semua", on_click=reset_all, help="Kosongkan semua input")
    st.button("Isi contoh", on_click=load_sample, help="Isi dengan data contoh")

# ----------------------------------------------------------------------------
# Halaman
# ----------------------------------------------------------------------------
st.markdown('<p class="title">Kalkulator Keuangan</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="subtitle">Catatan keuangan {html.escape(periode) if periode else "bulan ini"}</p>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section">Pemasukan</div>', unsafe_allow_html=True)
income_entries, total_income = render_rows("income", "Sumber", "mis. Gaji")

st.markdown('<div class="section">Pengeluaran</div>', unsafe_allow_html=True)
expense_entries, total_expense = render_rows("expense", "Kategori", "mis. Makan")

balance = total_income - total_expense

# ----------------------------------------------------------------------------
# Ringkasan
# ----------------------------------------------------------------------------
st.markdown('<div class="section">Ringkasan</div>', unsafe_allow_html=True)


def card(label: str, value: str, color: str = "#FFFFFF") -> str:
    return (
        f'<div class="card"><div class="label">{label}</div>'
        f'<div class="value" style="color:{color}">{value}</div></div>'
    )


k1, k2, k3 = st.columns(3)
k1.markdown(card("Total pemasukan", rp(total_income)), unsafe_allow_html=True)
k2.markdown(card("Total pengeluaran", rp(total_expense)), unsafe_allow_html=True)
k3.markdown(
    card("Sisa uang", rp(balance), "#4ADE80" if balance >= 0 else "#F87171"),
    unsafe_allow_html=True,
)

if total_income == 0 and total_expense == 0:
    note = "Isi pemasukan dan pengeluaran untuk melihat ringkasan."
elif balance < 0:
    note = f"Defisit {rp(abs(balance))}. Pengeluaran melebihi pemasukan."
elif balance == 0:
    note = "Pemasukan dan pengeluaran seimbang."
else:
    note = f"Surplus {rp(balance)} setelah semua pengeluaran."
st.markdown(f'<p class="muted" style="margin-top:.8rem">{note}</p>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Rincian pengeluaran
# ----------------------------------------------------------------------------
st.markdown('<div class="section">Rincian pengeluaran</div>', unsafe_allow_html=True)

if not expense_entries:
    st.markdown('<p class="muted">Belum ada pengeluaran.</p>', unsafe_allow_html=True)
else:
    detail = sorted(expense_entries, key=lambda e: e[1], reverse=True)
    rows_html = "".join(
        f'<tr><td>{html.escape(n)}</td><td class="num">{rp(a)}</td></tr>' for n, a in detail
    )
    st.markdown(
        f"""
        <table class="detail">
            <thead><tr><th>Kategori</th><th class="num">Jumlah</th></tr></thead>
            <tbody>{rows_html}
            <tr class="total"><td>Total</td><td class="num">{rp(total_expense)}</td></tr></tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    csv = pd.DataFrame(detail, columns=["Kategori", "Jumlah"]).to_csv(index=False)
    st.write("")
    st.download_button(
        "Unduh rincian (CSV)", data=csv.encode("utf-8"),
        file_name="rincian_pengeluaran.csv", mime="text/csv",
    )
