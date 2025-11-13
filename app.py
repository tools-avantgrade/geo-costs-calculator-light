# app_optimized.py
# ---------------------------------------------------
# AI Brand Monitoring - Budget Estimator (ChatGPT Focus)
# Versione ottimizzata con pricing realistico + GTM + CTA
# Basato su analisi Otterly.ai e Profound
# ---------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# Configurazione pagina
# -----------------------------
st.set_page_config(
    page_title="ChatGPT Brand Monitoring - Budget Estimator",
    page_icon="🔎",
    layout="centered"
)

# -----------------------------
# Google Tag Manager
# -----------------------------
gtm_head = """
<!-- Google Tag Manager -->
<script data-cookieconsent="ignore">(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-KJPT9B7');</script>
<!-- End Google Tag Manager -->
"""

components.html(gtm_head, height=0)

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
    .info-box {
        background-color: #FFF9F0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #FFB366;
        margin: 1rem 0;
    }
    .cta-box {
        background: linear-gradient(135deg, #FF8C42 0%, #FF7028 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
    }
    .cta-box h3 {
        color: white;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    .cta-box p {
        color: white;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    .cta-button {
        display: inline-block;
        background-color: white;
        color: #FF8C42;
        padding: 1rem 2.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        color: #FF7028;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Logica di pricing ottimizzata
# -----------------------------

FREQUENCY_MULTIPLIER = {
    "Settimanale": 0.75,   # Sconto per tracking meno frequente
    "Giornaliero": 1.00,   # Baseline (standard di mercato)
    "Real-time": 1.60      # Premium per monitoring continuo
}

def estimate_budget(
    prompts: int,
    frequency: str,
    projects: int,
    billing_cycle: str = "monthly"
):
    """
    Calcola il budget basandosi sui prezzi di mercato reali:
    - Otterly: $189/mese per 100 prompts (daily)
    - Profound: $499/mese per 200 prompts (daily)
    
    Logica:
    - Costo base per prompt: €1.20-1.90 (range competitivo)
    - Frequenza: daily=baseline, settimanale=-25%, real-time=+60%
    - Progetti: 1=baseline, poi +40-60€ per progetto extra
    """
    
    # --- COSTO BASE PER PROMPTS ---
    # Range realistico: €1.20-1.90 per prompt/mese
    if prompts <= 15:
        cost_per_prompt_low = 1.90
        cost_per_prompt_high = 2.50
    elif prompts <= 50:
        cost_per_prompt_low = 1.60
        cost_per_prompt_high = 2.20
    elif prompts <= 100:
        cost_per_prompt_low = 1.40
        cost_per_prompt_high = 1.90
    elif prompts <= 200:
        cost_per_prompt_low = 1.20
        cost_per_prompt_high = 1.70
    elif prompts <= 400:
        cost_per_prompt_low = 1.00
        cost_per_prompt_high = 1.50
    else:
        # Oltre 400: economie di scala
        cost_per_prompt_low = 0.85
        cost_per_prompt_high = 1.30
    
    base_low = prompts * cost_per_prompt_low
    base_high = prompts * cost_per_prompt_high
    
    # --- FREQUENZA ---
    freq_mult = FREQUENCY_MULTIPLIER.get(frequency, 1.0)
    
    # --- PROGETTI EXTRA ---
    # 1 progetto = baseline (incluso)
    # Ogni progetto extra: +€40-60/mese
    project_cost = 0
    if projects > 1:
        extra_projects = projects - 1
        project_cost_low = 40 * extra_projects
        project_cost_high = 60 * extra_projects
    else:
        project_cost_low = 0
        project_cost_high = 0
    
    # --- CALCOLO TOTALE MENSILE ---
    low_month = (base_low + project_cost_low) * freq_mult
    high_month = (base_high + project_cost_high) * freq_mult
    
    # --- ARROTONDAMENTO MARKETING ---
    def round_marketing(x):
        if x < 50:    return int(round(x / 5.0)) * 5
        if x < 100:   return int(round(x / 10.0)) * 10
        if x < 500:   return int(round(x / 25.0)) * 25
        if x < 1000:  return int(round(x / 50.0)) * 50
        return int(round(x / 100.0)) * 100
    
    low_month_rounded = round_marketing(low_month)
    high_month_rounded = round_marketing(max(high_month, low_month_rounded + 20))
    
    # Assicuriamo un minimo ragionevole
    low_month_rounded = max(low_month_rounded, 25)
    high_month_rounded = max(high_month_rounded, low_month_rounded + 20)
    
    # --- CALCOLO ANNUALE CON SCONTO ---
    if billing_cycle == "yearly":
        # Sconto 12-15% per pagamento annuale
        avg_monthly = (low_month_rounded + high_month_rounded) / 2
        
        if avg_monthly < 150:
            discount = 0.88  # -12%
        elif avg_monthly < 400:
            discount = 0.86  # -14%
        else:
            discount = 0.85  # -15%
        
        low_year = int(low_month_rounded * 12 * discount)
        high_year = int(high_month_rounded * 12 * discount)
        
        # Arrotonda annuale
        low_year = round_marketing(low_year)
        high_year = round_marketing(high_year)
        
        return (low_month_rounded, high_month_rounded, low_year, high_year)
    else:
        return (low_month_rounded, high_month_rounded, None, None)

def currency_fmt(val, currency="€"):
    """Formatta il valore come valuta"""
    try:
        return f"{currency}{val:,.0f}".replace(",", ".")
    except Exception:
        return f"{currency}{val}"

# -----------------------------
# UI PRINCIPALE
# -----------------------------

st.title("🔎 AI Brand Monitoring")
st.subheader("Budget Estimator per ChatGPT")
st.markdown("---")

# --- INPUT PARAMETERS ---
col1, col2 = st.columns(2)

with col1:
    prompts = st.number_input(
        "🔍 Domanda (prompt) da monitorare",
        min_value=1, 
        max_value=2000, 
        value=100, 
        step=5,
        help="📌 **Cosa sono i prompt?**\n\nSono le domande/query che vuoi tracciare su ChatGPT.\n\n"
             "**Esempi:**\n"
             "• 'Migliori CRM per PMI'\n"
             "• 'Come fare SEO nel 2025'\n"
             "• 'Differenza tra Ahrefs e Semrush'\n\n"
             "Il tool verifica **se e come il tuo brand viene citato** nelle risposte di ChatGPT."
    )
    
    frequency = st.select_slider(
        "⏱️ Frequenza monitoraggio",
        options=["Settimanale", "Giornaliero", "Real-time"],
        value="Giornaliero",
        help="**Giornaliero** è lo standard di mercato. Real-time è premium (+60%)."
    )

with col2:
    projects = st.number_input(
        "📁 Progetti (domini)",
        min_value=1, 
        max_value=20, 
        value=1, 
        step=1,
        help="📌 **Cosa sono i progetti?**\n\n"
             "Quanti **brand/siti web diversi** vuoi monitorare.\n\n"
             "**Esempi:**\n"
             "• 1 progetto = solo MioSito.com\n"
             "• 3 progetti = MioSito.com + MioBlog.it + Shop.com\n\n"
             "Ogni progetto extra aggiunge €40-60/mese al costo."
    )
    
    billing_cycle = st.radio(
        "💳 Ciclo di fatturazione",
        options=["monthly", "yearly"],
        format_func=lambda x: "📅 Mensile" if x == "monthly" else "📆 Annuale (sconto 12-15%)",
        horizontal=True
    )

currency = "€"

st.markdown("---")

# --- CALCOLO BUDGET ---
if st.button("🧮 Calcola Budget", use_container_width=True):
    
    low_m, high_m, low_y, high_y = estimate_budget(
        prompts=prompts,
        frequency=frequency,
        projects=projects,
        billing_cycle=billing_cycle
    )
    
    st.success("✅ Stima completata")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- METRICHE PRINCIPALI ---
    k1, k2, k3 = st.columns(3)
    
    with k1:
        if billing_cycle == "monthly":
            st.metric(
                "💰 Budget Mensile", 
                f"{currency_fmt(low_m, currency)} - {currency_fmt(high_m, currency)}"
            )
        else:
            monthly_avg = (low_m + high_m) // 2
            savings = (monthly_avg * 12) - ((low_y + high_y) // 2)
            st.metric(
                "💰 Budget Annuale",
                f"{currency_fmt(low_y, currency)} - {currency_fmt(high_y, currency)}",
                delta=f"-{currency_fmt(savings, currency)} vs mensile"
            )
    
    with k2:
        cpp_low = low_m / prompts if prompts > 0 else 0
        cpp_high = high_m / prompts if prompts > 0 else 0
        st.metric(
            "📊 Costo per Prompt",
            f"{currency}{cpp_low:.2f} - {currency}{cpp_high:.2f}",
            help="Costo mensile diviso per numero di prompt monitorati"
        )
    
    with k3:
        st.metric(
            "📈 Copertura",
            f"{prompts} prompt",
            delta=f"{projects} progetto{'i' if projects > 1 else ''}"
        )
    
    # --- RIEPILOGO CONFIGURAZIONE ---
    st.markdown("---")
    st.subheader("📋 Configurazione Selezionata")
    
    recap_col1, recap_col2 = st.columns(2)
    with recap_col1:
        st.markdown(f"**🔍 Prompt monitorati:** {prompts}")
        st.markdown(f"**⏱️ Frequenza:** {frequency}")
    with recap_col2:
        st.markdown(f"**📁 Progetti:** {projects}")
        st.markdown(f"**💳 Fatturazione:** {'Mensile' if billing_cycle=='monthly' else 'Annuale'}")
    
    # --- NOTE FINALI ---
    if frequency == "Real-time":
        st.info("💡 **Real-time monitoring** include aggiornamenti continui e alert istantanei.")
    
    if projects > 3:
        st.warning("⚠️ Per **progetti enterprise** (5+ brand), contatta il sales per pricing personalizzato.")
    
    # --- CTA POST-ANALISI ---
    st.markdown("---")
    cta_html = """
    <div class="cta-box">
        <h3>🚀 Vuoi scoprire come il tuo brand viene percepito dalle AI?</h3>
        <p>Ricevi un'analisi gratuita personalizzata da Avantgrade, agenzia SEO specializzata in AI Brand Monitoring</p>
        <a href="https://www.avantgrade.com/schedule-a-call?utm_source=streamlit" target="_blank" class="cta-button">
            📞 Prenota una Consulenza Gratuita
        </a>
    </div>
    """
    st.markdown(cta_html, unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("🤖 AI Brand Monitoring Budget Estimator | Powered by Avantgrade")
