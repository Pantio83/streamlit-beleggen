# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

# --- Algemene instellingen ---
st.set_page_config(page_title='Beleggingsdashboard', layout='wide')

# --- Screenercriteria ---
CRITERIA = {
    "P/E": 21.4,
    "P/B": 4.7,
    "ROE": 20.0,
    "FCF Yield": 4.8,
    "Buybacks": True
}

CRITERIA_UITLEG = {
    "P/E": "P/E (Price to Earnings): Lager dan 21.4 wijst op redelijke waardering t.o.v. winst",
    "P/B": "P/B (Price to Book): Lager dan 4.7 betekent niet te duur in verhouding tot boekwaarde",
    "ROE": "ROE (Return on Equity): Hoger dan 20% toont aan dat het bedrijf efficiënt winst genereert",
    "FCF Yield": "FCF Yield (Free Cash Flow): Meer dan 4.8% betekent goede kasstroom ten opzichte van beurswaarde",
    "Buybacks": "Aandeleninkoop: Bedrijf koopt actief eigen aandelen terug, wat aandeelhouderswaarde verhoogt"
}

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
        return {
            "P/E": pe,
            "P/B": pb,
            "ROE": roe,
            "FCF Yield": fcf_yield,
            "Buybacks": buybacks
        }
    except:
        return None

def passes_criteria(metrics):
    if not metrics:
        return False
    return (
        metrics["P/E"] and metrics["P/E"] < CRITERIA["P/E"] and
        metrics["P/B"] and metrics["P/B"] < CRITERIA["P/B"] and
        metrics["ROE"] and metrics["ROE"] > CRITERIA["ROE"] and
        metrics["FCF Yield"] and metrics["FCF Yield"] > CRITERIA["FCF Yield"] and
        metrics["Buybacks"] == CRITERIA["Buybacks"]
    )

# --- Data: Voorbeeldlijsten van tickers ---
sp500_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
nasdaq_tickers = ["TSLA", "META", "ADBE", "INTC", "CSCO"]
eu_tickers = ["SAP.DE", "ASML.AS", "SIE.DE", "AD.AS", "OR.PA"]
all_tickers = list(set(sp500_tickers + nasdaq_tickers + eu_tickers))

# --- Pagina: Home ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("Navigatie")
st.session_state.page = st.sidebar.radio("Ga naar", ["Home", "Screener", "Portefeuille"])

if st.session_state.page == "Home":
    st.title("📊 Beleggingsdashboard - Overzicht")
    st.markdown("""
    Hier krijg je aanbevelingen op basis van fundamentele criteria, momentum, en macro-economische trends.

    - 🔍 **Nieuwe aanbevelingen**: op basis van Value + Momentum-filter
    - 📈 **Macrovooruitzichten**: inflatie, rente, werkloosheid
    - ⚠️ **Aandachtspunten in portefeuille**: verkoopadvies of waarschuwingssignalen
    """)

elif st.session_state.page == "Screener":
    st.title("📈 Screener: Aandelenfilter")
    results = []
    for ticker in all_tickers:
        metrics = get_stock_metrics(ticker)
        if passes_criteria(metrics):
            results.append({"Ticker": ticker, **metrics})
    if results:
        df = pd.DataFrame(results)
        df["Outlook"] = np.where(df["ROE"] > 25, "🟢 Positief", "🔴 Negatief")
        for i, row in df.iterrows():
            with st.expander(f"ℹ️ {row['Ticker']} - Details en uitleg"):
                st.write(f"**Outlook**: {row['Outlook']}")
                for key in CRITERIA:
                    st.write(f"**{key}**: {row[key]} — {CRITERIA_UITLEG[key]}")
    else:
        st.warning("Geen aandelen gevonden die voldoen aan alle criteria.")

elif st.session_state.page == "Portefeuille":
    st.title("💼 Mijn Portefeuille")
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=["Datum", "Ticker", "Aantal", "Koers", "Type"])

    with st.form("Portefeuilleform"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ticker = st.text_input("Ticker", "AAPL")
        with col2:
            aantal = st.number_input("Aantal", min_value=1, value=10)
        with col3:
            koers = st.number_input("Koers", min_value=1.0, value=100.0)
        trans_type = st.selectbox("Type transactie", ["Aankoop", "Verkoop"])
        submit = st.form_submit_button("Toevoegen")
        if submit:
            nieuwe = pd.DataFrame([[pd.to_datetime("today"), ticker, aantal, koers, trans_type]],
                                  columns=st.session_state.portfolio.columns)
            st.session_state.portfolio = pd.concat([st.session_state.portfolio, nieuwe], ignore_index=True)

    st.subheader("📄 Historiek")
    st.dataframe(st.session_state.portfolio)