
# streamlit_app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.express as px
import datetime

# --- Functies voor Data Ophalen ---
def get_stock_data(ticker, start_date='2014-01-01'):
    data = yf.download(ticker, start=start_date)
    data.dropna(inplace=True)
    return data

def get_macro_indicators():
    # Placeholder: vervang door echte data of API
    return {
        'Rente': 1.5,
        'Inflatie': 3.2,
        'Werkloosheid': 4.5
    }

# --- Risico Maatstaven ---
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    excess_returns = returns.mean() - risk_free_rate / 252
    return excess_returns / returns.std()

def value_at_risk(returns, confidence_level=0.05):
    return np.percentile(returns, 100 * confidence_level)

# --- Portefeuillebeheer ---
def update_portfolio(portfolio, transaction):
    return portfolio.append(transaction, ignore_index=True)

def calculate_portfolio_value(portfolio):
    total_value = 0
    for index, row in portfolio.iterrows():
        try:
            data = get_stock_data(row['Ticker'])
            price = data['Close'][-1]
            total_value += row['Shares'] * price
        except:
            continue
    return total_value

def portfolio_returns(portfolio):
    returns = []
    for ticker in portfolio['Ticker'].unique():
        data = get_stock_data(ticker)
        ret = data['Close'].pct_change().dropna()
        returns.append(ret)
    return pd.concat(returns, axis=1).mean(axis=1)

# --- Streamlit Layout ---
st.set_page_config(page_title="Langetermijn Beleggen", layout="wide")
st.title("📈 Langetermijn Beleggingsdashboard")

# Macro indicatoren
st.subheader("🌐 Macro Indicatoren")
macro = get_macro_indicators()
st.write(macro)

# Portefeuille Initialisatie
portfolio_cols = ['Date', 'Ticker', 'Shares', 'Price', 'Transaction Type']
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=portfolio_cols)

# Transactie Formulier
st.subheader("💼 Voer Transactie In")
with st.form("transaction_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.text_input("Ticker", value="AAPL")
    with col2:
        shares = st.number_input("Aantal Aandelen", min_value=1, value=10)
    with col3:
        price = st.number_input("Koers", min_value=0.01, value=100.0)
    trans_type = st.selectbox("Type", ["Aankoop", "Verkoop"])
    submitted = st.form_submit_button("Toevoegen")

    if submitted:
        transaction = {
            'Date': pd.to_datetime(datetime.date.today()),
            'Ticker': ticker.upper(),
            'Shares': shares,
            'Price': price,
            'Transaction Type': trans_type
        }
        st.session_state.portfolio = update_portfolio(st.session_state.portfolio, transaction)
        st.success("✅ Transactie toegevoegd!")

# Portfolio Overzicht
st.subheader("📊 Portefeuille Overzicht")
portfolio = st.session_state.portfolio
if not portfolio.empty:
    st.dataframe(portfolio)

    value = calculate_portfolio_value(portfolio)
    st.metric("Totale Portefeuillewaarde", f"€ {value:,.2f}")

    returns = portfolio_returns(portfolio)
    sharpe = calculate_sharpe_ratio(returns)
    var = value_at_risk(returns)
    
    st.write(f"🔍 Sharpe Ratio: {sharpe:.2f}")
    st.write(f"⚠️ Value at Risk (5%): {var:.2%}")

    st.line_chart(returns.cumsum(), use_container_width=True)
else:
    st.info("Voeg eerst een transactie toe om je portefeuille op te bouwen.")
