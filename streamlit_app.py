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

# --- Selecteer type aandeel en criteria via de sidebar ---
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
    default=standaard_criteria
)

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
        debt_to_ebitda = info.get("debtToEquity", None)  # tijdelijke benadering
        revenue_cagr = None  # geen historische omzet via yfinance

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
                continue  # Placeholder - niet beschikbaar
            elif metrics[crit] > CRITERIA[crit]:
                score += 1
    return score

# --- Homepage voorbeeldsuggesties per type (dynamisch gegenereerd) ---
if st.session_state.page == "Home":
    st.title("📊 Beleggingsdashboard - Overzicht")

    st.subheader("💡 Voorbeelden per aandelentype (automatisch geselecteerd)")
    top_scores = []
    for ticker in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "V", "MA", "KO", "PG", "VZ", "SHOP", "IBM", "SNOW"]:
        metrics = get_stock_metrics(ticker)
        if metrics:
            score = score_stock(metrics)
            top_scores.append({"Ticker": ticker, "Score": score, **metrics})

    df = pd.DataFrame(top_scores).sort_values("Score", ascending=False)

    def suggest(df, criteria):
        return df[[c for c in criteria if c in df.columns] + ["Ticker", "Score"]].sort_values("Score", ascending=False).head(3)["Ticker"].tolist()

    st.markdown(f"**Waarde aandelen:** {', '.join(suggest(df, criteria_per_type['Waarde']))}")
    st.markdown(f"**Groei aandelen:** {', '.join(suggest(df, criteria_per_type['Groei']))}")
    st.markdown(f"**Kwaliteit aandelen:** {', '.join(suggest(df, criteria_per_type['Kwaliteit']))}")
    for groep, tickers in voorbeeldsuggesties.items():
        st.markdown(f"**{groep} aandelen:** {', '.join(tickers)}")

# De rest van de code blijft ongewijzigd...
