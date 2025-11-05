# app.py
# ---------------------------------------------------
# AI Brand Monitoring - Budget Estimator (ChatGPT Focus)
# Versione minimal e focalizzata
# ---------------------------------------------------

import streamlit as st
from datetime import datetime

# -----------------------------
# Configurazione pagina
# -----------------------------
st.set_page_config(
    page_title="ChatGPT Brand Monitoring - Budget Estimator",
    page_icon="🔎",
    layout="centered"
)

# -----------------------------
# Stili custom (toni arancioni)
# -----------------------------
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF8C42;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #FF7028;
    }
    .metric-container {
        background-color: #FFF5EE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF8C42;
    }
</style>
""", unsafe_allow_html=True)

HINT = """
<small style="opacity:0.75">
Stima indicativa basata su benchmark di mercato per il monitoraggio ChatGPT. 
Non sostituisce un preventivo ufficiale.
</small>
"""

def currency_fmt(val, currency="€"):
    try:
        return f"{currency}{val:,.0f}".replace(",", ".")
    except Exception:
        return f"{currency}{val}"

# -----------------------------
# Logica di pricing (ChatGPT focus)
# -----------------------------
FREQUENCY_MULTIPLIER = {
    "Settimanale": 1.00,
    "Giornaliero": 1.35,
    "Real-time": 1.90
}

def estimate_budget(
    prompts: int,
    competitors: int,
    frequency: str,
    pages: int,
    domains: int,
    billing_cycle: str = "monthly"
):
    # Base cost
    if prompts <= 25:
        base_low, base_high = 80, 140
    elif prompts <= 100:
        base_low, base_high = 180, 320
    elif prompts <= 400:
        base_low, base_high = 360, 740
    else:
        extra_blocks = max(0, (prompts - 400 + 99) // 100)
        base_low, base_high = 740 + 90*extra_blocks, 1200 + 150*extra_blocks

    # Frequenza
    freq_mult = FREQUENCY_MULTIPLIER.get(frequency, 1.0)

    # Competitor
    comp_low  = 10 * competitors
    comp_high = 20 * competitors

    # Pagine
    page_bucket = 0
    if pages <= 1000:
        page_bucket = 0
    elif pages <= 3000:
        page_bucket = 60
    elif pages <= 5000:
        page_bucket = 120
    else:
        extra = ((pages - 5000) + 999) // 1000
        page_bucket = 120 + 40 * extra

    # Domini
    domain_bucket = 0
    if domains <= 1:
        domain_bucket = 0
    elif domains <= 5:
        domain_bucket = 60
    elif domains <= 10:
        domain_bucket = 120
    else:
        domain_bucket = 120 + 20 * (domains - 10)

    # Aggregazione mensile
    low_month  = (base_low  + comp_low  + page_bucket + domain_bucket) * freq_mult
    high_month = (base_high + comp_high + page_bucket + domain_bucket) * freq_mult

    # Arrotondamento
    def round_marketing(x):
        if x < 100:   return int(round(x / 10.0)) * 10
        if x < 1000:  return int(round(x / 25.0)) * 25
        if x < 2000:  return int(round(x / 50.0)) * 50
        return int(round(x / 100.0)) * 100

    low_month_rounded  = round_marketing(low_month)
    high_month_rounded = round_marketing(max(high_month, low_month_rounded + 20))

    # Calcolo annuale con sconto
    if billing_cycle == "yearly":
        avg_m = (low_month_rounded + high_month_rounded) / 2
        if   avg_m < 200: disc = 0.90
        elif avg_m < 800: disc = 0.88
        else:             disc = 0.85
        low_year  = int(low_month_rounded  * 12 * disc)
        high_year = int(high_month_rounded * 12 * disc)
        return (low_month_rounded, high_month_rounded, low_year, high_year)
    else:
        return (low_month_rounded, high_month_rounded, None, None)

# -----------------------------
# UI
# -----------------------------
st.title("🔎 ChatGPT Brand Monitoring")
st.subheader("Budget Estimator")
st.markdown(HINT, unsafe_allow_html=True)
st.markdown("---")

# Input in due colonne
col1, col2 = st.columns(2)

with col1:
    prompts = st.number_input(
        "Prompt da monitorare",
        min_value=1, max_value=5000, value=100, step=10,
        help="Quante query vuoi tracciare su ChatGPT"
    )
    competitors = st.number_input(
        "Competitor",
        min_value=0, max_value=30, value=3, step=1
    )
    frequency = st.select_slider(
        "Frequenza monitoraggio",
        options=["Settimanale", "Giornaliero", "Real-time"],
        value="Settimanale"
    )

with col2:
    pages = st.number_input(
        "Pagine sito",
        min_value=100, max_value=20000, value=1000, step=100
    )
    domains = st.number_input(
        "Domini/progetti",
        min_value=1, max_value=50, value=1, step=1
    )
    billing_cycle = st.radio(
        "Fatturazione",
        options=["monthly", "yearly"],
        format_func=lambda x: "Mensile" if x == "monthly" else "Annuale",
        horizontal=True
    )

currency = "€"

st.markdown("---")

# Calcolo
if st.button("🧮 Calcola Budget", use_container_width=True):
    low_m, high_m, low_y, high_y = estimate_budget(
        prompts=prompts,
        competitors=competitors,
        frequency=frequency,
        pages=pages,
        domains=domains,
        billing_cycle=billing_cycle
    )

    st.success("✅ Stima completata")
    st.markdown("<br>", unsafe_allow_html=True)

    # Metriche principali
    k1, k2, k3 = st.columns(3)
    
    with k1:
        if billing_cycle == "monthly":
            st.metric(
                "Budget Mensile", 
                f"{currency_fmt(low_m, currency)} — {currency_fmt(high_m, currency)}"
            )
        else:
            st.metric(
                "Budget Annuale",
                f"{currency_fmt(low_y, currency)} — {currency_fmt(high_y, currency)}"
            )

    with k2:
        cpp_low = low_m / prompts if prompts > 0 else 0
        cpp_high = high_m / prompts if prompts > 0 else 0
        st.metric(
            "Costo per Prompt",
            f"{currency}{cpp_low:.2f} — {currency}{cpp_high:.2f}"
        )

    with k3:
        st.metric(
            "Copertura",
            f"{prompts} prompt",
            delta=f"{competitors} competitor"
        )

    # Riepilogo
    st.markdown("---")
    st.subheader("📋 Configurazione")
    
    recap_col1, recap_col2 = st.columns(2)
    with recap_col1:
        st.markdown(f"**Prompt:** {prompts}")
        st.markdown(f"**Competitor:** {competitors}")
        st.markdown(f"**Frequenza:** {frequency}")
    with recap_col2:
        st.markdown(f"**Pagine:** {pages}")
        st.markdown(f"**Domini:** {domains}")
        st.markdown(f"**Ciclo:** {'Mensile' if billing_cycle=='monthly' else 'Annuale'}")

# Footer
st.markdown("---")
st.caption("🤖 ChatGPT Brand Monitoring Budget Estimator")
