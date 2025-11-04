# app.py
# ---------------------------------------------------
# AI Brand Monitoring - Budget Estimator (Lead Magnet)
# Versione "light" e tool-agnostica (nessun brand citato)
# ---------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------
# Configurazione pagina
# -----------------------------
st.set_page_config(
    page_title="AI Brand Monitoring - Budget Estimator",
    page_icon="🔎",
    layout="wide"
)

# -----------------------------
# Stili minimi
# -----------------------------
HINT = """
<small style="opacity:0.75">
Stima indicativa basata su benchmark di mercato e complessità del setup. 
Non sostituisce un preventivo ufficiale.
</small>
"""

def currency_fmt(val, currency="€"):
    try:
        return f"{currency}{val:,.0f}".replace(",", ".")
    except Exception:
        return f"{currency}{val}"

# -----------------------------
# Heuristics di pricing (tool-agnostiche)
# NOTE: semplici regole per stimare un range in base alla complessità
# -----------------------------
FREQUENCY_MULTIPLIER = {
    "Settimanale": 1.00,
    "Giornaliero": 1.35,
    "Real-time": 1.90
}

PLATFORM_COMPLEXITY = {
    # Pondera la difficoltà media di integrazione/monitoraggio per piattaforma
    "ChatGPT": 1.0,
    "Perplexity": 1.0,
    "Google AI Overviews": 1.15,
    "Gemini": 1.0,
    "Copilot": 1.05
}

def estimate_budget(
    prompts: int,
    competitors: int,
    platforms: list,
    frequency: str,
    pages: int,
    domains: int,
    currency: str = "€",
    billing_cycle: str = "monthly"
):
    """
    Crea un range (low-high) tool-agnostico basato su:
    - volume prompt
    - n. piattaforme
    - frequenza monitoraggio
    - n. competitor
    - n. pagine e domini
    """

    # 1) BASE: costo "core" per set-up & tracking
    # -------------------------------------------
    # Curva a tratti per riflettere fasce di utilizzo
    if prompts <= 25:
        base_low, base_high = 80, 140
    elif prompts <= 100:
        base_low, base_high = 180, 320
    elif prompts <= 400:
        base_low, base_high = 360, 740
    else:
        # oltre 400 prompt: base + scaglioni
        extra_blocks = max(0, (prompts - 400 + 99) // 100)
        base_low, base_high = 740 + 90*extra_blocks, 1200 + 150*extra_blocks

    # 2) Piattaforme: maggiori integrazioni ⇒ più complessità
    # -------------------------------------------------------
    platform_factor = sum(PLATFORM_COMPLEXITY.get(p, 1.0) for p in platforms)
    platform_factor = max(1.0, platform_factor)  # minimo 1

    # 3) Frequenza: da weekly a realtime
    # ----------------------------------
    freq_mult = FREQUENCY_MULTIPLIER.get(frequency, 1.0)

    # 4) Competitor: arricchisce le query + reporting
    # -----------------------------------------------
    # (leggera incidenza, scala dolce)
    comp_low  = 10 * competitors
    comp_high = 20 * competitors

    # 5) Pagine/Domain: crawling + audit + integrazione SEO/AI
    # --------------------------------------------------------
    # costo base per crawling & data handling
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

    domain_bucket = 0
    if domains <= 1:
        domain_bucket = 0
    elif domains <= 5:
        domain_bucket = 60
    elif domains <= 10:
        domain_bucket = 120
    else:
        domain_bucket = 120 + 20 * (domains - 10)

    # 6) Aggregazione (mensile)
    # -------------------------
    low_month  = (base_low  + comp_low  + page_bucket + domain_bucket) * platform_factor * freq_mult
    high_month = (base_high + comp_high + page_bucket + domain_bucket) * platform_factor * freq_mult

    # Arrotonda a multipli "marketing-friendly"
    def round_marketing(x):
        if x < 100:   return int(round(x / 10.0)) * 10
        if x < 1000:  return int(round(x / 25.0)) * 25
        if x < 2000:  return int(round(x / 50.0)) * 50
        return int(round(x / 100.0)) * 100

    low_month_rounded  = round_marketing(low_month)
    high_month_rounded = round_marketing(max(high_month, low_month_rounded + 20))

    # 7) Annuale (sconto medio 10–20% in base alla soglia)
    # ----------------------------------------------------
    if billing_cycle == "yearly":
        # sconto dinamico
        avg_m = (low_month_rounded + high_month_rounded) / 2
        if   avg_m < 200: disc = 0.90
        elif avg_m < 800: disc = 0.88
        else:             disc = 0.85
        low_year  = int(low_month_rounded  * 12 * disc)
        high_year = int(high_month_rounded * 12 * disc)
        return (low_month_rounded, high_month_rounded, low_year, high_year)
    else:
        return (low_month_rounded, high_month_rounded, None, None)

def cost_per_prompt_range(low_m, high_m, prompts):
    if prompts <= 0:
        return (0, 0)
    return (low_m / prompts, high_m / prompts)

# -----------------------------
# UI
# -----------------------------
st.title("🔎 AI Brand Monitoring — Budget Estimator")
st.markdown("Strumento minimale, tool-agnostico: inserisci i tuoi dati e ottieni **un range di budget** su cui basarti.")
st.markdown(HINT, unsafe_allow_html=True)
st.markdown("---")

# Colonne input
c1, c2, c3 = st.columns(3)

with c1:
    prompts = st.number_input(
        "Numero di prompt/queries da monitorare",
        min_value=1, max_value=5000, value=100, step=10,
        help="Esempi: 'miglior software...', 'brand vs competitor', 'alternative a...'"
    )
    competitors = st.number_input(
        "Numero di competitor",
        min_value=0, max_value=30, value=3, step=1
    )
    frequency = st.select_slider(
        "Frequenza monitoraggio",
        options=["Settimanale", "Giornaliero", "Real-time"],
        value="Settimanale"
    )

with c2:
    platforms = st.multiselect(
        "Piattaforme AI da includere",
        ["ChatGPT", "Perplexity", "Google AI Overviews", "Gemini", "Copilot"],
        default=["ChatGPT", "Perplexity", "Google AI Overviews"]
    )
    pages = st.number_input(
        "Pagine del/i sito/i da considerare (crawling/analisi)",
        min_value=100, max_value=20000, value=1000, step=100
    )
    domains = st.number_input(
        "Numero di domini/progetti",
        min_value=1, max_value=50, value=1, step=1
    )

with c3:
    billing_cycle = st.radio(
        "Ciclo di fatturazione",
        options=["monthly", "yearly"],
        format_func=lambda x: "Mensile" if x == "monthly" else "Annuale (sconto incluso)",
        horizontal=True
    )
    currency = st.selectbox("Valuta", ["€", "$", "CHF", "£"], index=0)
    st.caption("La valuta è solo etichetta visiva.")

st.markdown("---")

# Calcolo
if st.button("🧮 Calcola Range di Prezzo", type="primary", use_container_width=True):
    low_m, high_m, low_y, high_y = estimate_budget(
        prompts=prompts,
        competitors=competitors,
        platforms=platforms,
        frequency=frequency,
        pages=pages,
        domains=domains,
        currency=currency,
        billing_cycle=billing_cycle
    )

    st.success("✅ Stima completata")

    # KPI principali
    k1, k2, k3 = st.columns(3)
    with k1:
        if billing_cycle == "monthly":
            st.metric("Budget Mensile (range)",
                      f"{currency_fmt(low_m, currency)} — {currency_fmt(high_m, currency)}")
        else:
            st.metric("Budget Annuale (range)",
                      f"{currency_fmt(low_y, currency)} — {currency_fmt(high_y, currency)}",
                      delta=f"{currency_fmt(low_m*12, currency)}–{currency_fmt(high_m*12, currency)} prima dello sconto")

    with k2:
        cpp_low, cpp_high = cost_per_prompt_range(low_m, high_m, prompts)
        st.metric("Costo per Prompt (mensile)",
                  f"{currency}{cpp_low:,.2f} — {currency}{cpp_high:,.2f}".replace(",", "."))

    with k3:
        st.metric("Copertura",
                  f"{len(platforms)} piattaforme / {competitors} competitor",
                  delta=f"{prompts} prompt totali")

    st.markdown("---")
    st.subheader("📋 Riepilogo configurazione")
    left, right = st.columns(2)
    with left:
        st.markdown(f"- Prompt: **{prompts}**")
        st.markdown(f"- Competitor: **{competitors}**")
        st.markdown(f"- Piattaforme: **{', '.join(platforms) if platforms else '—'}**")
    with right:
        st.markdown(f"- Frequenza: **{frequency}**")
        st.markdown(f"- Pagine: **{pages}**")
        st.markdown(f"- Domini: **{domains}**")

    # Tabella breakdown (semplificata, senza brand)
    st.markdown("---")
    st.subheader("📈 Range suggerito per scenario")
    data = []
    # Tre archetipi: Starter, Growth, Enterprise — per dare un riferimento mentale
    scenarios = [
        ("Starter", 0.9, 0.95),
        ("Growth", 1.0, 1.05),
        ("Enterprise", 1.15, 1.30)
    ]
    for name, low_mult, high_mult in scenarios:
        row_low  = int(low_m  * low_mult)
        row_high = int(high_m * high_mult)
        data.append({
            "Scenario": name,
            "Mensile (min)": currency_fmt(row_low, currency),
            "Mensile (max)": currency_fmt(row_high, currency),
            "Annuale (stimato)": currency_fmt(int((row_low + row_high)/2 * 12 * (0.86 if billing_cycle == "yearly" else 1.0)), currency)
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # Export report testo
    st.markdown("---")
    st.subheader("⬇️ Esporta stima (TXT)")
    report = f"""AI BRAND MONITORING — BUDGET ESTIMATOR
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

CONFIGURAZIONE
- Prompt: {prompts}
- Competitor: {competitors}
- Piattaforme: {", ".join(platforms) if platforms else "—"}
- Frequenza: {frequency}
- Pagine: {pages}
- Domini: {domains}

STIMA BUDGET {'MENSILE' if billing_cycle=='monthly' else 'ANNUALE'}
- Range: {currency_fmt(low_m if billing_cycle=='monthly' else low_y, currency)} — {currency_fmt(high_m if billing_cycle=='monthly' else high_y, currency)}
- Costo per prompt (mensile): {currency}{cpp_low:,.2f} — {currency}{cpp_high:,.2f}

NOTE
- Stima indicativa, tool-agnostica, utile come riferimento marketing/benchmark.
- Per un'offerta ufficiale è consigliata un'analisi tecnica più approfondita.
"""
    st.download_button(
        "📥 Scarica TXT",
        data=report,
        file_name=f"ai_brand_monitoring_budget_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer minimale
st.markdown("---")
st.caption("© 2025 — AI Brand Monitoring Budget Estimator (tool-agnostico).")
