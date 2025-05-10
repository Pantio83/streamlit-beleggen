# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
import os
import matplotlib.pyplot as plt

# --- Algemene instellingen ---
st.set_page_config(page_title='Beleggingsdashboard', layout='wide')

# --- Screenercriteria (zachter, met scoresysteem) ---
CRITERIA = {
    "P/E": 35.0,
    "P/B": 10.0,
    "ROE": 15.0,
    "FCF Yield": 2.0,
    "Gross Margin": 50.0,
    "Net Margin": 10.0,
    "ROIC": 15.0,
    "Revenue CAGR": 7.0,
    "Net Debt/EBITDA": 3.0
}

CRITERIA_UITLEG = {
    "P/E": "P/E (Price to Earnings): Lager dan 35 wijst op redelijke waardering t.o.v. winst",
    "P/B": "P/B (Price to Book): Lager dan 10 betekent niet te duur in verhouding tot boekwaarde",
    "ROE": "ROE (Return on Equity): Hoger dan 15% toont aan dat het bedrijf efficiënt winst genereert",
    "FCF Yield": "FCF Yield (Free Cash Flow): Meer dan 2% betekent goede kasstroom ten opzichte van beurswaarde",
    "Buybacks": "Aandeleninkoop: Bedrijf koopt actief eigen aandelen terug, wat aandeelhouderswaarde verhoogt (bonuspunt)",
    "Gross Margin": "Brutomarge: Toont hoe winstgevend een bedrijf is na directe kosten; hoger dan 50% is sterk",
    "Net Margin": "Nettowinstmarge: Aandeel van de omzet dat als winst overblijft; >10% wijst op sterke winstgevendheid",
    "ROIC": "ROIC (Return on Invested Capital): Meet rendement op geïnvesteerd kapitaal; >15% toont kapitaalefficiëntie",
    "Revenue CAGR": "Omzetgroei (CAGR): Samengestelde jaarlijkse omzetgroei over 5 jaar; >7% is solide groei",
    "Net Debt/EBITDA": "Netto schuld / EBITDA: Lager dan 3 duidt op beheersbare schuldenlast"
}

# --- Sidebar selectie ---
st.sidebar.header("📊 Analyse-instellingen")
aandeeltype = st.sidebar.selectbox("Kies type aandeel:", ["Waarde", "Groei", "Kwaliteit"])

criteria_per_type = {
    "Waarde": ["P/E", "P/B", "FCF Yield", "Buybacks", "Net Debt/EBITDA"],
    "Groei": ["Revenue CAGR", "Gross Margin", "Net Margin", "ROIC"],
    "Kwaliteit": ["ROE", "ROIC", "Net Margin", "Gross Margin", "FCF Yield"]
}

standaard_criteria = criteria_per_type[aandeeltype]
selected_criteria = st.sidebar.multiselect(
    "✅ Selecteer criteria voor analyse:",
    options=list(CRITERIA.keys()),
    default=[c for c in standaard_criteria if c in CRITERIA.keys()]
)),
    default=standaard_criteria
)

# --- Pagina selectie ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("Navigatie")
st.session_state.page = st.sidebar.radio("Ga naar", ["Home", "Screener", "Portefeuille", "Evaluatie"])

# --- Hulpfuncties ---
def get_stock_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        pe = info.get("trailingPE", None)
        pb = info.get("priceToBook", None)
        roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None
        fcf = info.get("freeCashflow", 0)
        mc = info.get("marketCap", 1)
        fcf_yield = (fcf / mc * 100) if mc > 0 else None
        buybacks = info.get("buyBacks", 0) > 0
        gross_margin = info.get("grossMargins", None) * 100 if info.get("grossMargins") else None
        net_margin = info.get("netMargins", None) * 100 if info.get("netMargins") else None
        roic = info.get("returnOnAssets", None) * 100 if info.get("returnOnAssets") else None
        debt_to_ebitda = info.get("debtToEquity", None)
        revenue_cagr = None
        return {
            "P/E": pe,
            "P/B": pb,
            "ROE": roe,
            "FCF Yield": fcf_yield,
            "Buybacks": buybacks,
            "Gross Margin": gross_margin,
            "Net Margin": net_margin,
            "ROIC": roic,
            "Net Debt/EBITDA": debt_to_ebitda,
            "Revenue CAGR": revenue_cagr
        }
    except:
        return None

def score_stock(metrics):
    score = 0
    for crit in selected_criteria:
        if crit == "Buybacks":
            if metrics.get("Buybacks"):
                score += 1
        elif crit in metrics and metrics[crit] is not None:
            if crit == "Net Debt/EBITDA":
                if metrics[crit] < CRITERIA[crit]:
                    score += 1
            elif crit == "Revenue CAGR":
            continue  # Revenue CAGR wordt momenteel niet berekend en telt dus niet mee
            elif metrics[crit] > CRITERIA[crit]:
                score += 1
    return score

# --- Home pagina ---
if st.session_state.page == "Home":
    st.title("📊 Beleggingsdashboard - Overzicht")
    st.markdown("""
    Hier krijg je aanbevelingen op basis van fundamentele criteria, momentum, en macro-economische trends.
    """)
    top_scores = []
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "V", "MA", "KO", "PG", "VZ", "SHOP", "IBM", "SNOW"]
    for ticker in tickers:
        metrics = get_stock_metrics(ticker)
        if metrics:
            score = score_stock(metrics)
            top_scores.append({"Ticker": ticker, "Score": score, **metrics})
    df = pd.DataFrame(top_scores).sort_values("Score", ascending=False)
    def suggest(df, criteria):
    kolommen = [c for c in criteria if c in df.columns]
    return df[kolommen + ["Ticker", "Score"]].sort_values("Score", ascending=False).head(3)["Ticker"].tolist() + ["Ticker", "Score"]].sort_values("Score", ascending=False).head(3)["Ticker"].tolist()
    st.subheader("💡 Aandelen per type (top 3)")
    st.markdown(f"**Waarde aandelen:** {', '.join(suggest(df, criteria_per_type['Waarde']))}")
    st.markdown(f"**Groei aandelen:** {', '.join(suggest(df, criteria_per_type['Groei']))}")
    st.markdown(f"**Kwaliteit aandelen:** {', '.join(suggest(df, criteria_per_type['Kwaliteit']))}")

# --- Screener pagina ---
elif st.session_state.page == "Screener":
    st.title("📈 Screener")
    resultaten = []
    for ticker in tickers:
        metrics = get_stock_metrics(ticker)
        if metrics:
            score = score_stock(metrics)
            resultaten.append({"Ticker": ticker, **metrics, "Score": score})
    if resultaten:
        df = pd.DataFrame(resultaten).sort_values("Score", ascending=False)
        st.dataframe(df.set_index("Ticker"))
    else:
        st.info("Geen aandelen voldoen aan de gekozen criteria.")

# --- Portefeuille pagina ---
elif st.session_state.page == "Portefeuille":
    st.title("💼 Mijn Portefeuille")
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=["Datum", "Ticker", "Aantal", "Koers", "Type"])
    with st.form("transacties"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ticker = st.text_input("Ticker", "AAPL")
        with col2:
            aantal = st.number_input("Aantal", 1, step=1)
        with col3:
            koers = st.number_input("Koers", 1.0)
        trans_type = st.selectbox("Type transactie", ["Aankoop", "Verkoop"])
        toevoegen = st.form_submit_button("Toevoegen")
        if toevoegen:
            nieuwe = pd.DataFrame([[pd.to_datetime("today"), ticker, aantal, koers, trans_type]], columns=st.session_state.portfolio.columns)
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, nieuwe], ignore_index=True)
    st.subheader("📄 Historiek")
    st.dataframe(st.session_state.portfolio)

# --- Evaluatie pagina ---
elif st.session_state.page == "Evaluatie":
    st.title("📊 Evaluatie van posities")
    if not st.session_state.get("portfolio", pd.DataFrame()).empty:
        bezit_tickers = st.session_state.portfolio["Ticker"].unique()
        overzicht = []
        for t in bezit_tickers:
            aankopen = st.session_state.portfolio.query("Ticker == @t and Type == 'Aankoop'").sort_values("Datum")
            if aankopen.empty:
                continue
            aankoop_koers = aankopen.iloc[-1]["Koers"]
            metrics = get_stock_metrics(t)
            koers_data = yf.download(t, period="1d", progress=False)
            huidige_koers = koers_data["Close"].iloc[-1] if not koers_data.empty else None
            rendement = ((huidige_koers - aankoop_koers) / aankoop_koers * 100) if huidige_koers else None
            if metrics:
                score = score_stock(metrics)
                overzicht.append({"Ticker": t, **metrics, "Score": score, "Aankoopkoers": aankoop_koers, "Huidige koers": huidige_koers, "Rendement %": rendement})
        if overzicht:
            st.dataframe(pd.DataFrame(overzicht).set_index("Ticker"))
        else:
            st.info("Geen geldige posities gevonden.")
