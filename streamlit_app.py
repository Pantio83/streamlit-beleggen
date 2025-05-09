import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Functie om de fundamentele gegevens van een aandeel op te halen
def get_stock_metrics(ticker):
    stock = yf.Ticker(ticker)
    data = stock.info

    # Fundamentele data ophalen
    pe_ratio = data.get('trailingPE', None)
    pb_ratio = data.get('priceToBook', None)
    roe = data.get('returnOnEquity', None)
    fcf_yield = data.get('freeCashflow', None)
    market_cap = data.get('marketCap', 1)
    if fcf_yield is not None:
        fcf_yield = fcf_yield / market_cap * 100  # Free Cash Flow Yield in %

    # Aandeleninkoop controleren
    buybacks = data.get('buyBacks', 0)

    return {
        'P/E': pe_ratio,
        'P/B': pb_ratio,
        'ROE': roe * 100 if roe is not None else None,
        'FCF Yield (%)': fcf_yield,
        'Buybacks': buybacks
    }

# Filter functie op basis van de gegeven selectiecriteria
def filter_stocks(stocks):
    filtered_stocks = []

    for ticker in stocks:
        try:
            metrics = get_stock_metrics(ticker)
            if (metrics['P/E'] is not None and metrics['P/E'] < 21.4 and
                metrics['P/B'] is not None and metrics['P/B'] < 4.7 and
                metrics['ROE'] is not None and metrics['ROE'] > 20 and
                metrics['FCF Yield (%)'] is not None and metrics['FCF Yield (%)'] > 4.8 and
                metrics['Buybacks'] > 0):
                filtered_stocks.append((ticker, metrics))
        except:
            continue

    return filtered_stocks

# Bereken koersmomentum over een bepaalde periode (standaard 6 maanden)
def get_price_momentum(ticker, period='6mo'):
    stock_data = yf.download(ticker, period=period, progress=False)
    if stock_data.empty:
        return None
    price_change = (stock_data['Close'][-1] - stock_data['Close'][0]) / stock_data['Close'][0]
    return price_change * 100

# Functie om een grafiek van de koersbeweging te genereren
def plot_stock_price(ticker, period='6mo'):
    stock_data = yf.download(ticker, period=period, progress=False)
    if stock_data.empty:
        return None
    fig = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker} - Koers over {period}')
    return fig

# Streamlit gebruikersinterface
st.set_page_config(page_title='Beleggingsstrategie Dashboard', layout='wide')
st.title('📈 Value + Momentum Beleggingsfilter')

# Aandeleninvoer van de gebruiker
tickers = st.text_input('Voer tickers in (gescheiden door een komma)', 'AAPL,MSFT,GOOG,AMZN,NVDA,META')

# Verkrijg tickers en filteren op basis van criteria
tickers_list = [ticker.strip().upper() for ticker in tickers.split(',')]
filtered = filter_stocks(tickers_list)

if filtered:
    for ticker, metrics in filtered:
        st.subheader(f'📊 {ticker}')
        st.write('**Fundamentele kenmerken:**')
        st.write(metrics)

        momentum = get_price_momentum(ticker)
        if momentum is not None:
            st.write(f"**Momentum (6 maanden)**: {momentum:.2f}%")
        else:
            st.warning("Geen koersdata beschikbaar voor momentum.")

        fig = plot_stock_price(ticker)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Geen grafiek beschikbaar.")
else:
    st.info("Geen aandelen voldoen aan alle criteria op dit moment.")