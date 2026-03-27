import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import time
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from pathlib import Path
import hashlib

# ====================== CONFIG ======================
st.set_page_config(page_title="Portfolio", layout="wide", page_icon="💎")

# ====================== GLOBAL CSS ======================
st.markdown("""
<style>
/* Whole app background - lighter elegant navy gradient */
.stApp {
    background: linear-gradient(180deg, #0f1724 0%, #0a0f1c 100%) !important;
}

/* Big navigation cards with glossy shine */
.stButton > button {
    background: #1e2a44 !important;
    color: #e0e0e0 !important;
    padding: 22px 24px !important;
    border-radius: 14px !important;
    margin-bottom: 14px !important;
    font-size: 1.28rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    height: auto !important;
    width: 100% !important;
    display: flex;
    align-items: center;
    gap: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 30px rgba(255, 255, 255, 0.25) !important;
    background: #263b5e !important;
    color: white !important;
}
/* Glossy shine for main content + slightly lighter top summary cards */
.glossy-header,
.glossy-box {
    position: relative;
    overflow: hidden;
    background: #26334f;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.glossy-header:hover,
.glossy-box:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 15px 40px rgba(255,255,255,0.15);
}
.glossy-header::before,
.glossy-box::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -150%;
    width: 60%;
    height: 300%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.28), transparent);
    transform: rotate(25deg);
    opacity: 0;
    transition: all 2.2s cubic-bezier(0.25, 0.1, 0.25, 1);
    pointer-events: none;
}
.glossy-header:hover::before,
.glossy-box:hover::before {
    left: 180%;
    opacity: 1;
}
.glossy-header {
    padding: 32px 40px;
    min-height: 130px;
    font-size: 29px;
    font-weight: 700;
    letter-spacing: 1.8px;
    line-height: 1.1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    width: 100% !important;
    margin-bottom: 45px;
}
.glossy-box {
    padding: 28px 30px;
    text-align: center;
    flex: 1;
    min-width: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.glossy-box > div:first-child {
    font-size: 13.5px;
    font-weight: 500;
    letter-spacing: 1.1px;
    color: #e0e0e0;
    opacity: 0.9;
    margin-bottom: 6px;
    line-height: 1.2;
}
.glossy-box > div:last-child {
    font-size: 27px;
    font-weight: 700;
    line-height: 1.05;
    color: #ffffff;
}

/* MOBILE: Make header smaller */
@media (max-width: 700px) {
    .glossy-header {
        padding: 24px 20px !important;
        font-size: 24px !important;
        min-height: 100px;
    }
}

/* MOBILE RESPONSIVE FIX FOR THE 3 SUMMARY CARDS */
@media (max-width: 600px) {
    .glossy-box {
        min-width: 98px !important;
        padding: 18px 14px !important;
    }
    .glossy-box > div:first-child {
        font-size: 12px !important;
    }
    .glossy-box > div:last-child {
        font-size: 21px !important;
    }
}

/* PRICE PILLS - COMPACT SIZE THAT FITS PERFECTLY + NICER VISUALS */
.price-pills-container {
    display: flex !important;
    gap: 6px !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    padding-bottom: 4px;
    scrollbar-width: none;
}
.price-pills-container::-webkit-scrollbar {
    display: none;
}
.price-pill, .avg-pill, .daily-pill {
    padding: 7px 14px !important;
    border-radius: 9999px !important;
    white-space: nowrap !important;
    flex-shrink: 0;
    background: #0f172a !important;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 1.05rem;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.12);
}
.price-pill span:last-child,
.avg-pill span:last-child {
    font-size: 1.26rem;
}
.daily-pill {
    color: #ff4d4d;
    font-weight: 700;
    padding: 4px 8px !important;
    font-size: 0.88rem !important;
}
@media (max-width: 700px) {
    .price-pills-container { gap: 4px !important; }
    .price-pill, .avg-pill, .daily-pill { padding: 5px 10px !important; }
    .daily-pill { padding: 3px 7px !important; font-size: 0.82rem !important; }
    .price-pill span:first-child,
    .avg-pill span:first-child { font-size: 0.92rem !important; }
    .price-pill span:last-child,
    .avg-pill span:last-child { font-size: 1.18rem !important; }
}

/* TIMEFRAME SELECTBOX - FULL TEXT VISIBLE, CLEAN PILL */
div[data-baseweb="select"] {
    background-color: #1e2a44 !important;
    border-radius: 9999px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
    min-width: 148px !important;
    max-width: 158px !important;
    transition: all 0.2s ease;
}
div[data-baseweb="select"] > div {
    background: transparent !important;
    border: none !important;
    padding: 8px 18px !important;
}
div[data-baseweb="select"] input {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.08rem !important;
    white-space: nowrap !important;
}
div[data-baseweb="select"] svg {
    fill: #ffffff !important;
}
/* No blue highlight */
div[data-baseweb="select"] [aria-selected="true"],
div[data-baseweb="select"]:focus-within {
    background: #1e2a44 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
}
@media (max-width: 700px) {
    div[data-baseweb="select"] {
        min-width: 138px !important;
        max-width: 148px !important;
    }
    div[data-baseweb="select"] > div {
        padding: 7px 14px !important;
    }
}

/* CHART IMPROVEMENTS FOR PHONE */
.stPlotlyChart {
    width: 100% !important;
}
@media (max-width: 700px) {
    .stPlotlyChart {
        margin-bottom: 20px;
    }
    .plotly .modebar {
        padding: 4px 8px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ====================== SVG ICONS ======================
DASHBOARD_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'''
CRYPTO_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M14.5 8.5L9.5 13.5"/><path d="M9.5 8.5L14.5 13.5"/></svg>'''
FIAT_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h12"/><path d="M6 12h12"/><path d="M6 16h12"/></svg>'''

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CRYPTO_JSON = DATA_DIR / "crypto_transactions.json"
FIAT_JSON = DATA_DIR / "fiat_transactions.json"

# ====================== DATE HELPERS ======================
def format_datum(datum_val):
    if pd.isna(datum_val) or datum_val == "":
        return ""
    try:
        excel_base = datetime(1899, 12, 30)
        date_obj = excel_base + timedelta(days=int(float(datum_val)))
        return date_obj.strftime("%d.%m.%Y")
    except:
        return str(datum_val)

def date_to_excel_serial(selected_date: date) -> int:
    base = datetime(1899, 12, 30).date()
    delta = selected_date - base
    return delta.days

# ====================== INITIAL DATA ======================
def get_initial_crypto_df():
    return pd.DataFrame([
        {"Datum": 46098, "USDC": 8.33, "Ticker": "HBAR", "Amount": 83.60159414, "Price": 0.09963924834},
        {"Datum": 46098, "USDC": 8.33, "Ticker": "XRP", "Amount": 5.51291403, "Price": 1.510997624},
        {"Datum": 46098, "USDC": 8.33, "Ticker": "BNB", "Amount": 0.01246729, "Price": 668.1484108},
        {"Datum": 46098, "USDC": 8.33, "Ticker": "LINK", "Amount": 0.84859547, "Price": 9.816220207},
        {"Datum": 46098, "USDC": 8.33, "Ticker": "TRX", "Amount": 27.22422112, "Price": 0.3059775324},
        {"Datum": 46099, "USDC": 50.0, "Ticker": "BTC", "Amount": 0.00067193, "Price": 74412.51321},
        {"Datum": 46099, "USDC": 15.0, "Ticker": "ETH", "Amount": 0.00642259, "Price": 2335.506392},
        {"Datum": 46099, "USDC": 10.0, "Ticker": "SOL", "Amount": 0.1055771, "Price": 94.71750976},
        {"Datum": 46100, "USDC": 50.0, "Ticker": "BTC", "Amount": 0.00071602, "Price": 69830.45166},
        {"Datum": 46100, "USDC": 15.0, "Ticker": "ETH", "Amount": 0.00707709, "Price": 2119.515224},
        {"Datum": 46100, "USDC": 10.0, "Ticker": "SOL", "Amount": 0.11363518, "Price": 88.00091662},
    ])

def get_initial_fiat_df():
    return pd.DataFrame([
        {"Datum": 46098, "CZK": 1010.16, "EUR": 40.0, "Fee": 1.0, "CZK/EUR": 25.254, "USDC": 44.67, "NI": "CZK", "GG": "", "ER": "8972.72"},
        {"Datum": 46098, "CZK": 3156.76, "EUR": 125.0, "Fee": 1.0, "CZK/EUR": 25.25408, "USDC": 142.03, "NI": "USDC", "GG": "", "ER": "402.308"},
        {"Datum": 46098, "CZK": 4174.67, "EUR": 165.0, "Fee": 1.0, "CZK/EUR": 25.3010303, "USDC": 188.188, "NI": "EUR", "GG": "", "ER": "355"},
        {"Datum": 46099, "CZK": 631.13, "EUR": 25.0, "Fee": 1.0, "CZK/EUR": 25.2452, "USDC": 27.42, "NI": "FEEs", "GG": "4", "ER": "101.0543103"},
    ])

# ====================== LOAD / SAVE ======================
def load_or_init_crypto():
    if CRYPTO_JSON.exists():
        return pd.read_json(CRYPTO_JSON)
    df = get_initial_crypto_df()
    save_crypto(df)
    return df

def load_or_init_fiat():
    if FIAT_JSON.exists():
        return pd.read_json(FIAT_JSON)
    df = get_initial_fiat_df()
    save_fiat(df)
    return df

def save_crypto(df):
    df.to_json(CRYPTO_JSON, orient="records", indent=2)

def save_fiat(df):
    df.to_json(FIAT_JSON, orient="records", indent=2)

# ====================== CRYPTOCOMPARE MAPPING ======================
CRYPTOCOMPARE_SYMBOL_MAP = {
    'BTC': 'BTC', 'ETH': 'ETH', 'SOL': 'SOL', 'HBAR': 'HBAR',
    'XRP': 'XRP', 'BNB': 'BNB', 'TRX': 'TRX', 'LINK': 'LINK',
    'SUI': 'SUI', 'USDC': 'USDC',
}

# ====================== HELPER: RETRY WRAPPER ======================
def get_with_retry(url: str, headers: dict, timeout: int = 12, retries: int = 4) -> dict | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(1.3 ** attempt)
    return None

# ====================== LIVE PRICE FUNCTION ======================
@st.cache_data(ttl=15, show_spinner=False)
def get_all_cryptocompare_prices(tickers):
    prices = {"USDC": 1.0}
    symbols = [CRYPTOCOMPARE_SYMBOL_MAP.get(t.upper()) for t in tickers if t.upper() != "USDC"]
    symbols = [s for s in symbols if s]
    if not symbols:
        return prices
    try:
        fsyms = ",".join(symbols)
        url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={fsyms}&tsyms=USD"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
        data = get_with_retry(url, headers)
        if data:
            for sym, price_data in data.items():
                if isinstance(price_data, dict) and "USD" in price_data:
                    ticker = next((k for k, v in CRYPTOCOMPARE_SYMBOL_MAP.items() if v == sym), None)
                    if ticker:
                        prices[ticker] = float(price_data["USD"])
            return prices
    except:
        pass
    for ticker in set(tickers):
        if ticker.upper() == "USDC":
            continue
        sym = CRYPTOCOMPARE_SYMBOL_MAP.get(ticker.upper())
        if not sym:
            continue
        try:
            url = f"https://min-api.cryptocompare.com/data/price?fsym={sym}&tsyms=USD"
            headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
            data = get_with_retry(url, headers)
            if data and "USD" in data:
                prices[ticker] = float(data["USD"])
        except:
            continue
    return prices

# ====================== DAILY OPEN PRICE FUNCTION ======================
@st.cache_data(ttl=300, show_spinner=False)
def get_daily_open(ticker: str):
    sym = CRYPTOCOMPARE_SYMBOL_MAP.get(ticker.upper())
    if not sym:
        return 0.0
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit=1"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
        data = get_with_retry(url, headers)
        if data and "Data" in data and "Data" in data["Data"] and len(data["Data"]["Data"]) > 0:
            return float(data["Data"]["Data"][-1]["open"])
        return 0.0
    except:
        return 0.0

# ====================== CHART FUNCTION ======================
@st.cache_data(ttl=80, show_spinner=False)
def get_cryptocompare_ohlc(ticker: str, candle: str):
    sym = CRYPTOCOMPARE_SYMBOL_MAP.get(ticker.upper())
    if not sym:
        return None
    try:
        if candle in ["5m", "30m"]:
            url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={sym}&tsym=USD&limit=2000"
        else:
            url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={sym}&tsym=USD&limit=2000" if candle != "1D" else \
                  f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit=90"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
        data = get_with_retry(url, headers)
        if not data or "Data" not in data or "Data" not in data["Data"]:
            return None
        df_data = data["Data"]["Data"]
        df = pd.DataFrame(df_data)
        df = df[["time", "open", "high", "low", "close", "volumefrom"]]
        df["timestamp"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("timestamp", inplace=True)
        df = df.drop(columns=["time"])
        if candle == "5m":
            df = df.resample('5T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volumefrom': 'sum'}).dropna()
        elif candle == "30m":
            df = df.resample('30T').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volumefrom': 'sum'}).dropna()
        elif candle == "4h":
            df = df.resample('4H').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volumefrom': 'sum'}).dropna()
        return df
    except:
        return None

# ====================== LOGOS & COLORS ======================
def get_ticker_logo(ticker: str) -> str:
    ticker = ticker.upper()
    known = {
        'USDC': 'https://assets.coingecko.com/coins/images/6319/small/USD_Coin_icon.png',
        'BTC': 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
        'ETH': 'https://assets.coingecko.com/coins/images/279/small/ethereum.png',
        'SOL': 'https://assets.coingecko.com/coins/images/4128/small/Solana.png',
        'HBAR': 'https://assets.coingecko.com/coins/images/3688/small/hbar.png',
        'XRP': 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png',
        'SUI': 'https://logo.svgcdn.com/token-branded/sui.svg',
        'LINK': 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png',
        'BNB': 'https://assets.coingecko.com/coins/images/825/small/binance-coin-logo.png',
        'TRX': 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png',
    }
    if ticker in known:
        return known[ticker]
    return f"https://cryptologos.cc/logos/{ticker.lower()}-logo.png"

def get_ticker_color(ticker: str) -> str:
    ticker = ticker.upper()
    known = {
        'USDC': '#2775ca', 'BTC': '#f7931a', 'ETH': '#627eea',
        'SOL': '#9b59b6', 'HBAR': '#000000', 'XRP': '#000000',
        'SUI': '#60a5fa', 'LINK': '#1e3a8a', 'BNB': '#f4c430',
        'TRX': '#ff2d55'
    }
    if ticker in known:
        return known[ticker]
    return f"#{hashlib.md5(ticker.encode()).hexdigest()[:6]}"

# ====================== FORMATTING ======================
def format_money(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        return f"${val:,.2f}" if val >= 0 else f"-${-val:,.2f}"
    except:
        return ""

def format_crypto_price(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        if val >= 1:
            return f"${val:,.2f}"
        elif val >= 0.01:
            return f"${val:,.4f}"
        else:
            return f"${val:,.6f}"
    except:
        return ""

def format_percent(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        return f"{val:.2f}%"
    except:
        return ""

def format_holdings(val, ticker=None):
    try:
        val = float(val)
        if pd.isna(val): return ""
        if ticker == "BTC":
            return f"{val:,.6f}".replace(',', '.')
        return f"{val:,.4f}".replace(',', '.')
    except:
        return str(val)

# ====================== PORTFOLIO CALC ======================
def calculate_portfolio(crypto_df):
    if 'last_known_prices' not in st.session_state:
        st.session_state.last_known_prices = {"USDC": 1.0}
    if crypto_df.empty:
        return pd.DataFrame(columns=['Ticker','Holdings','USDC','AVG','Live','PnL','PnL %','Value']), 0, 0, 0
    crypto_df = crypto_df.copy()
    crypto_df['Ticker'] = crypto_df['Ticker'].astype(str).str.upper()
    fiat_usdc = pd.to_numeric(st.session_state.fiat_df['USDC'], errors='coerce').fillna(0).sum()
    crypto_spent = pd.to_numeric(crypto_df['USDC'], errors='coerce').fillna(0).sum()
    usdc_holdings = fiat_usdc - crypto_spent
    coin_tickers = [t for t in crypto_df['Ticker'].unique() if t != 'USDC']
    live_prices = get_all_cryptocompare_prices(coin_tickers)
    for t, p in live_prices.items():
        if p > 0:
            st.session_state.last_known_prices[t] = p
    portfolio = []
    for ticker in coin_tickers:
        sub = crypto_df[crypto_df['Ticker'] == ticker]
        total_holdings = sub['Amount'].sum()
        total_invested = sub['USDC'].sum()
        avg_price = total_invested / total_holdings if total_holdings > 0 else 0
        live_price = live_prices.get(ticker, st.session_state.last_known_prices.get(ticker, 0))
        value = total_holdings * live_price
        pnl = value - total_invested
        pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0
        portfolio.append({'Ticker':ticker,'Holdings':total_holdings,'USDC':total_invested,'AVG':avg_price,'Live':live_price,'PnL':pnl,'PnL %':pnl_pct,'Value':value})
    portfolio.append({'Ticker':'USDC','Holdings':usdc_holdings,'USDC':usdc_holdings,'AVG':1.0,'Live':1.0,'PnL':0,'PnL %':0,'Value':usdc_holdings})
    df_port = pd.DataFrame(portfolio)
    df_port = df_port.sort_values(by='USDC', ascending=False).reset_index(drop=True)
    total_value = df_port['Value'].sum()
    total_pnl = df_port['PnL'].sum()
    total_pnl_pct = (total_pnl / (total_value - total_pnl) * 100) if (total_value - total_pnl) != 0 else 0
    return df_port, total_value, total_pnl, total_pnl_pct

# ====================== SESSION STATE ======================
if 'crypto_df' not in st.session_state:
    st.session_state.crypto_df = load_or_init_crypto()
if 'fiat_df' not in st.session_state:
    st.session_state.fiat_df = load_or_init_fiat()
if 'crypto_table_version' not in st.session_state:
    st.session_state.crypto_table_version = 0
if 'fiat_table_version' not in st.session_state:
    st.session_state.fiat_table_version = 0
if 'ui_version' not in st.session_state:
    st.session_state.ui_version = 0
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'last_known_prices' not in st.session_state:
    st.session_state.last_known_prices = {"USDC": 1.0}

# ====================== SIDEBAR ======================
with st.sidebar:
    nav_items = [
        ("🏠 Portfolio Dashboard", "Home"),
