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
import random

# ====================== CONFIG ======================
st.set_page_config(page_title="Portfolio", layout="wide", page_icon="logo.png")

# ====================== GLOBAL CSS ======================
st.markdown("""
<style>
/* App Background */
.stApp {
    background: linear-gradient(180deg, #0f1724 0%, #0a0f1c 100%) !important;
    padding-top: 95px !important;
}
.main, .block-container, .stMain {
    padding-top: 0px !important;
}

/* Flip Card - Fixed & Polished */
.flip-card {
    perspective: 1500px;
    height: 100%;
    cursor: pointer;
}
.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.85s cubic-bezier(0.23, 1, 0.32, 1);
    transform-style: preserve-3d;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}
.flip-card.flipped .flip-card-inner {
    transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 20px;
    overflow: hidden;
}
.flip-card-front {
    background: #0f172a;
    padding: 20px 18px;
}
.flip-card-back {
    background: #0f172a;
    transform: rotateY(180deg);
    display: flex;
    flex-direction: column;
    padding: 16px;
}
.flip-card-back .mini-chart-wrapper {
    flex: 1;
    min-height: 0;
    border-radius: 14px;
    overflow: hidden;
    background: #1a2338;
}
.flip-card-front:hover {
    box-shadow: 0 0 30px 10px var(--glow) !important;
}
.flip-hint {
    position: absolute;
    bottom: 14px;
    right: 18px;
    font-size: 0.78rem;
    color: #666;
    font-weight: 500;
}

/* Other styles */
.glossy-header, .glossy-box {
    background: #26334f;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35);
}
.glossy-header {
    padding: 32px 40px;
    font-size: 29px;
    font-weight: 700;
    margin-top: 72px;
    margin-bottom: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
}
.price-pills-container {
    display: flex !important;
    gap: 8px !important;
    flex-wrap: nowrap !important;
    overflow-x: auto;
    scrollbar-width: none;
}
.price-pill, .avg-pill {
    padding: 6px 12px !important;
    border-radius: 9999px !important;
    background: #0f172a !important;
    font-size: 1.02rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ====================== SVG ICONS ======================
DASHBOARD_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'''
CRYPTO_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M14.5 8.5L9.5 13.5"/><path d="M9.5 8.5L14.5 13.5"/></svg>'''
FIAT_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h12"/><path d="M6 12h12"/><path d="M6 16h12"/></svg>'''
CHARTS_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M17 17l-4-4-3 3-4-4"/></svg>'''

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

# ====================== CRYPTOCOMPARE ======================
CRYPTOCOMPARE_SYMBOL_MAP = {
    'BTC': 'BTC', 'ETH': 'ETH', 'SOL': 'SOL', 'HBAR': 'HBAR',
    'XRP': 'XRP', 'BNB': 'BNB', 'TRX': 'TRX', 'LINK': 'LINK',
    'SUI': 'SUI', 'USDC': 'USDC',
}

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

@st.cache_data(ttl=15, show_spinner=False)
def get_all_cryptocompare_prices(tickers, refresh_key=0):
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

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_open(ticker: str, refresh_key=0):
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

@st.cache_data(ttl=80, show_spinner=False)
def get_cryptocompare_ohlc(ticker: str, candle: str, refresh_key=0):
    sym = CRYPTOCOMPARE_SYMBOL_MAP.get(ticker.upper())
    if not sym:
        return None
    try:
        if candle in ["5m", "30m"]:
            url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={sym}&tsym=USD&limit=2000"
        else:
            url = f"https://min-api.cryptocompare.com/data/v2/histohour?fsym={sym}&tsym=USD&limit=2000" if candle != "1D" else f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit=90"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
        data = get_with_retry(url, headers)
        if not data or "Data" not in data or "Data" not in data["Data"]:
            return None
        df = pd.DataFrame(data["Data"]["Data"])[["time", "open", "high", "low", "close", "volumefrom"]]
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
        'BTC': 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png',
        'ETH': 'https://assets.coingecko.com/coins/images/279/small/ethereum.png',
        'SOL': 'https://assets.coingecko.com/coins/images/4128/small/Solana.png',
        'HBAR': 'https://assets.coingecko.com/coins/images/3688/small/hbar.png',
        'XRP': 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png',
        'LINK': 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png',
        'BNB': 'https://assets.coingecko.com/coins/images/825/small/binance-coin-logo.png',
        'TRX': 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png',
    }
    return known.get(ticker, f"https://cryptologos.cc/logos/{ticker.lower()}-logo.png")

def get_ticker_color(ticker: str) -> str:
    ticker = ticker.upper()
    known = {
        'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9b59b6', 'HBAR': '#000000',
        'XRP': '#000000', 'LINK': '#1e3a8a', 'BNB': '#f4c430', 'TRX': '#ff2d55'
    }
    return known.get(ticker, f"#{hashlib.md5(ticker.encode()).hexdigest()[:6]}")

# ====================== FORMATTING ======================
def format_money(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        return f"${val:,.2f}" if val >= 0 else f"-${-val:,.2f}"
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

def format_percent(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        return f"{val:.2f}%"
    except:
        return ""

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
    live_prices = get_all_cryptocompare_prices(coin_tickers, st.session_state.refresh_key)
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
if 'ui_version' not in st.session_state:
    st.session_state.ui_version = 0
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'last_known_prices' not in st.session_state:
    st.session_state.last_known_prices = {"USDC": 1.0}
if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = random.randint(100000, 999999)
if 'delete_trigger' not in st.session_state:
    st.session_state.delete_trigger = ""
if 'edit_trigger' not in st.session_state:
    st.session_state.edit_trigger = ""

# ====================== SIDEBAR ======================
with st.sidebar:
    nav_items = [
        ("🏠 Portfolio Dashboard", "Home"),
        ("📊 Crypto Transactions", "Crypto Transactions"),
        ("💰 Fiat Transactions", "Fiat Transactions")
    ]
    for label, key in nav_items:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.session_state.ui_version += 1
            st.rerun()
    st.divider()
    if st.button("🔄 Refresh All Prices & Charts", use_container_width=True):
        st.session_state.refresh_key = random.randint(100000, 999999)
        st.session_state.ui_version += 1
        st.success("✅ Prices & charts refreshed!")
        st.rerun()

# ====================== MAIN ======================
main_container = st.empty()

def glossy_header(title: str, icon_svg: str):
    html = f"""<div class="glossy-header">{icon_svg}<span style="margin-left:12px;">{title}</span></div>"""
    st.markdown(html, unsafe_allow_html=True)

# ====================== PAGES ======================
with main_container.container(key=f"page_{st.session_state.page}_{st.session_state.ui_version}"):
    if st.session_state.page == "Home":
        glossy_header("Portfolio Dashboard", DASHBOARD_ICON)
       
        df_port, total_value, total_pnl, total_pnl_pct = calculate_portfolio(st.session_state.crypto_df)
       
        value_box_html = f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(98px, 1fr)); gap: 14px; margin-bottom: 32px;">
    <div class="glossy-box"><div>Total Value</div><div>{format_money(total_value)}</div></div>
    <div class="glossy-box"><div>PnL</div><div style="color:{'#00ff9d' if total_pnl>=0 else '#ff4d4d'}">{"▲" if total_pnl>0 else "▼" if total_pnl<0 else ""} {format_money(abs(total_pnl))}</div></div>
    <div class="glossy-box"><div>PnL %</div><div style="color:{'#00ff9d' if total_pnl_pct>=0 else '#ff4d4d'}">{"▲" if total_pnl_pct>0 else "▼" if total_pnl_pct<0 else ""} {abs(total_pnl_pct):.2f}%</div></div>
</div>"""
        st.markdown(value_box_html, unsafe_allow_html=True)
       
        coin_list = [t for t in df_port['Ticker'] if t != 'USDC']
       
        cards_html = ""
        for _, r in df_port.iterrows():
            ticker = r['Ticker']
            if ticker == 'USDC':
                continue
            pnl = r['PnL']
            pnl_color = "#00ff9d" if pnl > 0 else "#ff4d4d" if pnl < 0 else "#aaaaaa"
            arrow = "▲" if pnl > 0 else "▼" if pnl < 0 else ""
            glow_color = get_ticker_color(ticker) + '77'
            logo_url = get_ticker_logo(ticker)
            pnl_pct_formatted = format_percent(abs(r['PnL %'])) if pd.notna(r['PnL %']) else ""
            live_price = r['Live']
            avg_price = r.get('AVG', None)

            # Mini chart
            mini_data = get_cryptocompare_ohlc(ticker, "30m", st.session_state.refresh_key)
            mini_chart_html = ""
            if mini_data is not None and not mini_data.empty and len(mini_data) > 5:
                fig_mini = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.15, row_heights=[0.78, 0.22])
                fig_mini.add_trace(go.Candlestick(
                    x=mini_data.index,
                    open=mini_data['open'],
                    high=mini_data['high'],
                    low=mini_data['low'],
                    close=mini_data['close'],
                    increasing_line_color='#00ff9d',
                    decreasing_line_color='#ff4d4d'
                ), row=1, col=1)
                if avg_price and pd.notna(avg_price):
                    fig_mini.add_trace(go.Scatter(
                        x=[mini_data.index.min(), mini_data.index.max()],
                        y=[avg_price, avg_price],
                        mode='lines',
                        line=dict(color='#ffaa00', width=1.5, dash='dash')
                    ), row=1, col=1)
                colors_vol = ['#00ff9d' if o < c else '#ff4d4d' for o, c in zip(mini_data['open'], mini_data['close'])]
                fig_mini.add_trace(go.Bar(
                    x=mini_data.index,
                    y=mini_data['volumefrom'],
                    marker_color=colors_vol,
                    opacity=0.75
                ), row=2, col=1)
                fig_mini.update_layout(
                    height=265,
                    margin=dict(t=8, b=8, l=8, r=8),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#aaa',
                    showlegend=False,
                    xaxis_rangeslider_visible=False,
                    dragmode=False,
                    hovermode="x unified"
                )
                fig_mini.update_xaxes(visible=False)
                fig_mini.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                mini_chart_html = fig_mini.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False})
            else:
                mini_chart_html = '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#555;">Chart unavailable</div>'

            cards_html += f"""
<div class="flip-card" style="--glow:{glow_color};">
    <div class="flip-card-inner">
        <!-- FRONT -->
        <div class="flip-card-front">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <img src="{logo_url}" style="width:42px;height:42px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/42/1e2a44/ffffff?text={ticker[0]}';">
                <div style="font-weight:700;font-size:1.32rem;color:#fff;">{ticker}</div>
            </div>
            <div style="font-size:0.94rem;line-height:1.5;">
                <div><span style="color:#aaa;">Holdings</span> <span style="float:right;font-weight:600;">{format_holdings(r['Holdings'], ticker)}</span></div>
                <div><span style="color:#aaa;">Invested</span> <span style="float:right;font-weight:600;">{format_money(r['USDC'])}</span></div>
                <div><span style="color:#aaa;">PnL</span> <span style="float:right;color:{pnl_color};font-weight:600;">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</span></div>
                <div><span style="color:#aaa;">PnL %</span> <span style="float:right;color:{pnl_color};font-weight:600;">{arrow} {pnl_pct_formatted}</span></div>
            </div>
            <div style="margin-top:18px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.1);">
                <span style="color:#aaa;font-size:0.9rem;">Value</span>
                <span style="float:right;font-size:1.25rem;font-weight:700;color:#fff;">{format_money(r['Value'])}</span>
            </div>
            <div class="flip-hint">Tap to flip</div>
        </div>
        <!-- BACK -->
        <div class="flip-card-back">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-weight:700;color:#fff;">{ticker} • 30m</span>
                <button onclick="flipBack(this)" style="background:none;border:none;color:#00ff9d;font-size:1.45rem;cursor:pointer;">←</button>
            </div>
            <div class="mini-chart-wrapper">
                {mini_chart_html}
            </div>
            <div class="price-pills-container" style="margin-top:12px;justify-content:center;">
                <div class="price-pill">
                    <span>LIVE</span>
                    <span style="color:{'#00ff9d' if live_price > 0 else '#ff4d4d'};">{format_money(live_price)}</span>
                </div>
                {f'<div class="avg-pill"><span>AVG</span><span style="color:#ffaa00;">{format_money(avg_price)}</span></div>' if avg_price and pd.notna(avg_price) else ''}
            </div>
        </div>
    </div>
</div>
"""

        html = f"""<html><head><style>
body{{background:transparent;color:white;font-family:sans-serif;margin:0;padding:0;}}
.coin-grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:18px;padding:20px 24px;max-height:740px;overflow-y:auto;scrollbar-width:none;}}
.coin-grid::-webkit-scrollbar {{display:none;}}
</style></head><body>
<div class="coin-grid">{cards_html}</div>
<script>
function flipBack(btn) {{
    const card = btn.closest('.flip-card');
    if (card) card.classList.remove('flipped');
}}
document.querySelectorAll('.flip-card').forEach(card => {{
    card.addEventListener('click', function(e) {{
        if (!e.target.closest('button')) {{
            this.classList.toggle('flipped');
        }}
    }});
}});
document.addEventListener('keydown', e => {{
    if (e.key === "Escape") {{
        document.querySelectorAll('.flip-card').forEach(c => c.classList.remove('flipped'));
    }}
}});
</script>
</body></html>"""

        components.html(html, height=760, scrolling=True)

        # Full Charts Section
        st.markdown(f"""
<div id="price-charts-section" class="glossy-box" style="background:#1e2a44;padding:18px 30px;border-radius:18px;">
    <div class="charts-header">
        {CHARTS_ICON}
        <span>Full Charts</span>
    </div>
</div>
""", unsafe_allow_html=True)
       
        if coin_list:
            selected_tab = st.tabs(coin_list)
            for i, coin in enumerate(coin_list):
                with selected_tab[i]:
                    avg_row = df_port.loc[df_port['Ticker'] == coin, 'AVG']
                    avg_price = avg_row.iloc[0] if not avg_row.empty and pd.notna(avg_row.iloc[0]) else None
                    live_price = df_port.loc[df_port['Ticker'] == coin, 'Live'].iloc[0] if not df_port.loc[df_port['Ticker'] == coin].empty else 0
                    daily_open = get_daily_open(coin, st.session_state.refresh_key)
                    daily_change_pct = ((live_price - daily_open) / daily_open * 100) if daily_open > 0 else 0
                    daily_arrow = "▲" if daily_change_pct > 0 else "▼" if daily_change_pct < 0 else ""
                    color = "#00ff9d" if live_price > 0 else "#ff4d4d"
                    st.markdown(f"""
                    <div class="price-pills-container">
                        <div class="price-pill">
                            <span>LIVE</span>
                            <span style="color:{color};">{format_money(live_price)}</span>
                        </div>
                        <div class="daily-pill">{daily_arrow} {abs(daily_change_pct):.2f}%</div>
                        {f'<div class="price-pill avg-pill"><span>AVG</span><span style="color:#ffaa00;">{format_money(avg_price)}</span></div>' if avg_price is not None else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    col1, col2 = st.columns([0.95, 4.05])
                    with col1:
                        candle = st.selectbox(
                            "Timeframe",
                            options=["5m", "30m", "1h", "4h", "1D"],
                            index=3,
                            key=f"candle_select_{coin}_{st.session_state.ui_version}",
                            label_visibility="collapsed"
                        )
                    data = get_cryptocompare_ohlc(coin, candle, st.session_state.refresh_key)
                    if data is not None and not data.empty:
                        data_local = data.copy()
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.75, 0.25])
                        fig.add_trace(go.Candlestick(
                            x=data_local.index,
                            open=data_local['open'],
                            high=data_local['high'],
                            low=data_local['low'],
                            close=data_local['close'],
                            increasing_line_color='#00ff9d',
                            decreasing_line_color='#ff4d4d'
                        ), row=1, col=1)
                        if avg_price is not None:
                            fig.add_trace(go.Scatter(
                                x=[data_local.index.min(), data_local.index.max()],
                                y=[avg_price, avg_price],
                                mode='lines',
                                line=dict(color='#ffaa00', width=2, dash='dash')
                            ), row=1, col=1)
                        colors_volume = ['#00ff9d' if o < c else '#ff4d4d' for o, c in zip(data_local['open'], data_local['close'])]
                        fig.add_trace(go.Bar(
                            x=data_local.index,
                            y=data_local['volumefrom'],
                            marker_color=colors_volume,
                            opacity=0.85
                        ), row=2, col=1)
                        fig.update_layout(
                            height=700,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white',
                            hovermode="x unified",
                            xaxis_rangeslider_visible=False,
                            showlegend=False,
                            dragmode='pan',
                            margin=dict(t=20, b=20, l=20, r=20)
                        )
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            key=f"chart_{coin}_{candle}_{st.session_state.ui_version}"
                        )
                    else:
                        st.error(f"📉 Could not load {coin} chart. Try Refresh.")

    # ====================== CRYPTO TRANSACTIONS ======================
    elif st.session_state.page == "Crypto Transactions":
        glossy_header("Crypto Transactions", CRYPTO_ICON)
       
        delete_trigger = st.text_input("delete_trigger", value=st.session_state.delete_trigger, label_visibility="collapsed", key="delete_trigger_hidden")
        edit_trigger = st.text_input("edit_trigger", value=st.session_state.edit_trigger, label_visibility="collapsed", key="edit_trigger_hidden")
       
        if delete_trigger and delete_trigger != st.session_state.delete_trigger:
            try:
                idx = int(delete_trigger)
                if 0 <= idx < len(st.session_state.crypto_df):
                    st.session_state.crypto_df = st.session_state.crypto_df.drop(idx).reset_index(drop=True)
                    save_crypto(st.session_state.crypto_df)
                    st.session_state.crypto_table_version = st.session_state.crypto_table_version + 1
                    st.session_state.ui_version += 1
                    st.success("✅ Transaction deleted!")
                    st.rerun()
            except:
                pass
            st.session_state.delete_trigger = delete_trigger
       
        if edit_trigger and edit_trigger != st.session_state.edit_trigger:
            try:
                idx = int(edit_trigger)
                if 0 <= idx < len(st.session_state.crypto_df):
                    st.session_state.editing_row_crypto = idx
                    st.rerun()
            except:
                pass
            st.session_state.edit_trigger = edit_trigger
       
        df_display = st.session_state.crypto_df.copy()
        df_display['Date'] = df_display['Datum'].apply(format_datum)
        df_display = df_display.dropna(how='all').reset_index(drop=True)
       
        cards_html = ""
        for i, r in df_display.iterrows():
            logo_url = get_ticker_logo(r['Ticker'])
            invested = format_money(r['USDC'])
            amount_val = format_holdings(r['Amount'], r['Ticker'])
            price = format_money(r['Price'])
            date_str = r['Date']
           
            cards_html += f"""
<div class="transaction-card">
    <div class="transaction-main-row">
        <div class="transaction-left">
            <img src="{logo_url}" onerror="this.src='https://via.placeholder.com/42/1e2a44/ffffff?text={r['Ticker'][0]}';">
            <div>
                <div class="transaction-ticker">{r['Ticker']}</div>
                <div class="transaction-date">{date_str}</div>
            </div>
        </div>
        <div class="transaction-values">
            <div><small>Invested</small><br><strong>{invested}</strong></div>
            <div><small>Amount</small><br><strong class="transaction-amount">{amount_val}</strong></div>
            <div><small>Price</small><br><strong>{price}</strong></div>
        </div>
    </div>
    <div class="transaction-buttons">
        <button class="delete-btn" onclick="deleteTransaction({i})">🗑️ Delete</button>
        <button class="edit-btn" onclick="editTransaction({i})">✏️ Edit</button>
    </div>
</div>
"""
       
        full_html = f"""
<html>
<head>
<style>
body {{ background: transparent; margin: 0; padding: 0; }}
.transaction-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 16px; padding: 0 14px; }}
.transaction-card {{ background: #0f172a; border-radius: 18px; padding: 18px 20px 14px; box-shadow: 0 6px 20px rgba(0,0,0,0.3); transition: all 0.25s ease; min-height: 138px; }}
.transaction-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0, 255, 157, 0.3); }}
.transaction-main-row {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }}
.transaction-left {{ display: flex; align-items: center; gap: 14px; flex: 1; }}
.transaction-header img {{ width: 42px; height: 42px; border-radius: 50%; object-fit: contain; }}
.transaction-ticker {{ font-size: 1.28rem; font-weight: 700; color: #ffffff; }}
.transaction-date {{ color: #aaa; font-size: 0.92rem; }}
.transaction-values {{ display: flex; gap: 24px; text-align: right; font-size: 1.02rem; }}
.transaction-values div {{ min-width: 88px; }}
.transaction-values small {{ color: #aaa; font-size: 0.82rem; font-weight: 500; display: block; }}
.transaction-values strong {{ font-weight: 700; color: #ffffff; }}
.transaction-amount {{ font-size: 1.04rem; font-weight: 700; color: #ffffff; }}
.transaction-buttons {{ display: flex; gap: 12px; }}
.transaction-buttons button {{ flex: 1; padding: 10px 14px; border: none; border-radius: 11px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; }}
.transaction-buttons .delete-btn {{ background: #e63939; color: white; }}
.transaction-buttons .delete-btn:hover {{ background: #c1121f; }}
.transaction-buttons .edit-btn {{ background: #00b894; color: #0f1724; }}
.transaction-buttons .edit-btn:hover {{ background: #00a17a; }}
</style>
</head>
<body>
<div class="transaction-grid">
{cards_html}
</div>
<script>
function deleteTransaction(i) {{
    const input = window.parent.document.querySelector('input[aria-label="delete_trigger"]');
    if (input) {{
        input.value = i;
        input.dispatchEvent(new Event('change'));
    }}
}}
function editTransaction(i) {{
    const input = window.parent.document.querySelector('input[aria-label="edit_trigger"]');
    if (input) {{
        input.value = i;
        input.dispatchEvent(new Event('change'));
    }}
}}
</script>
</body>
</html>
"""
        components.html(full_html, height=560, scrolling=True)
       
        if 'editing_row_crypto' in st.session_state:
            edit_idx = st.session_state.editing_row_crypto
            row = st.session_state.crypto_df.loc[edit_idx]
            st.markdown("**Edit transaction**")
            with st.form("edit_crypto_row"):
                col_a, col_b, col_c = st.columns([1.2, 1.2, 1.6])
                with col_a:
                    new_date = st.date_input("Date", value=datetime(1899, 12, 30) + timedelta(days=int(row['Datum'])))
                    new_datum = date_to_excel_serial(new_date)
                with col_b:
                    new_usdc = st.number_input("USDC Spent", value=float(row['USDC']), step=0.01)
                with col_c:
                    new_ticker = st.text_input("Ticker", value=row['Ticker']).upper().strip()
                new_amount = st.number_input("Amount Bought", value=float(row['Amount']), step=0.000001, format="%.8f")
                new_price = round(new_usdc / new_amount, 8) if new_amount > 0 else 0.0
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.crypto_df.loc[edit_idx] = {"Datum": new_datum, "USDC": new_usdc, "Ticker": new_ticker, "Amount": new_amount, "Price": new_price}
                        save_crypto(st.session_state.crypto_df)
                        del st.session_state.editing_row_crypto
                        st.session_state.crypto_table_version += 1
                        st.session_state.ui_version += 1
                        st.success("✅ Transaction updated!")
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state.editing_row_crypto
                        st.rerun()
       
        st.subheader("➕ Add New Transaction")
        with st.form("add_crypto"):
            col1, col2, col3 = st.columns([1.2, 1.2, 1.6])
            with col1:
                selected_date = st.date_input("Date", value=date(2026, 3, 25))
                datum = date_to_excel_serial(selected_date)
            with col2:
                usdc = st.number_input("USDC Spent", value=15.0, step=0.01)
            with col3:
                ticker = st.text_input("Ticker", value="BTC").upper().strip()
            amount = st.number_input("Amount Bought", value=0.1, step=0.000001, format="%.8f")
            price = round(usdc / amount, 8) if amount > 0 else 0.0
            if st.form_submit_button("➕ Add Transaction"):
                if ticker:
                    new_row = pd.DataFrame([{"Datum": datum, "USDC": usdc, "Ticker": ticker, "Amount": amount, "Price": price}])
                    st.session_state.crypto_df = pd.concat([st.session_state.crypto_df, new_row], ignore_index=True)
                    save_crypto(st.session_state.crypto_df)
                    st.session_state.crypto_table_version += 1
                    st.session_state.ui_version += 1
                    st.success(f"✅ Added {amount} {ticker}")
                    st.rerun()

    # ====================== FIAT TRANSACTIONS ======================
    elif st.session_state.page == "Fiat Transactions":
        total_czk = pd.to_numeric(st.session_state.fiat_df['CZK'], errors='coerce').fillna(0).sum()
        total_eur = pd.to_numeric(st.session_state.fiat_df['EUR'], errors='coerce').fillna(0).sum()
        total_usdc = pd.to_numeric(st.session_state.fiat_df['USDC'], errors='coerce').fillna(0).sum()
        fees_eur = pd.to_numeric(st.session_state.fiat_df['Fee'], errors='coerce').fillna(0).sum()
        fees_czk = (pd.to_numeric(st.session_state.fiat_df['Fee'], errors='coerce').fillna(0) *
                    pd.to_numeric(st.session_state.fiat_df['CZK/EUR'], errors='coerce').fillna(0)).sum()
        glossy_header("Fiat Transactions", FIAT_ICON)
        summary_html = f"""
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin-bottom:30px;">
    <div class="glossy-box"><div>Total CZK</div><div>{total_czk:,.2f}</div></div>
    <div class="glossy-box"><div>Total EUR</div><div>{total_eur:,.2f}</div></div>
    <div class="glossy-box"><div>Total USDC</div><div>{format_money(total_usdc)}</div></div>
    <div class="glossy-box"><div>Fees</div><div class="fee-line">{fees_eur:,.2f} EUR</div><div class="fee-line" style="font-size:22px;">{fees_czk:,.2f} CZK</div></div>
</div>"""
        st.markdown(summary_html, unsafe_allow_html=True)
        df_clean = st.session_state.fiat_df.dropna(how='all').reset_index(drop=True)
        table_container = st.container(key=f"fiat_table_container_{st.session_state.ui_version}")
        with table_container:
            with st.container(height=520, border=True):
                h = st.columns([1.0, 0.9, 0.9, 0.6, 0.9, 1.0, 0.4, 0.4])
                h[0].markdown("**Date**")
                h[1].markdown("**CZK**")
                h[2].markdown("**EUR**")
                h[3].markdown("**Fee**")
                h[4].markdown("**CZK/EUR**")
                h[5].markdown("**USDC**")
                h[6].markdown("**Delete**")
                h[7].markdown("**Edit**")
                for i, r in df_clean.iterrows():
                    cols = st.columns([1.0, 0.9, 0.9, 0.6, 0.9, 1.0, 0.4, 0.4])
                    with cols[0]: st.write(format_datum(r['Datum']))
                    with cols[1]: st.write(f"{r['CZK']:,.2f}")
                    with cols[2]: st.write(f"{r['EUR']:,.2f}")
                    with cols[3]: st.write(f"{r['Fee']:,.2f}")
                    with cols[4]: st.write(f"{r['CZK/EUR']:,.5f}")
                    with cols[5]: st.write(format_money(r['USDC']))
                    with cols[6]:
                        if st.button("🗑️", key=f"del_{i}_{st.session_state.fiat_table_version}_{st.session_state.ui_version}"):
                            st.session_state.fiat_df = st.session_state.fiat_df.drop(i).reset_index(drop=True)
                            save_fiat(st.session_state.fiat_df)
                            st.session_state.fiat_table_version += 1
                            st.session_state.ui_version += 1
                            st.success("✅ Row deleted!")
                            st.rerun()
                    with cols[7]:
                        if st.button("✏️", key=f"edit_{i}_{st.session_state.fiat_table_version}_{st.session_state.ui_version}"):
                            st.session_state.editing_row = i
                            st.rerun()
        if 'editing_row' in st.session_state:
            edit_idx = st.session_state.editing_row
            row = st.session_state.fiat_df.loc[edit_idx]
            st.markdown("**Edit row**")
            with st.form("edit_fiat_row"):
                col_a, col_b = st.columns(2)
                with col_a:
                    new_date = st.date_input("Date", value=datetime(1899, 12, 30) + timedelta(days=int(row['Datum'])))
                    new_datum = date_to_excel_serial(new_date)
                with col_b:
                    new_czk = st.number_input("CZK", value=float(row['CZK']), step=0.01)
                new_eur = st.number_input("EUR", value=float(row['EUR']), step=0.01)
                new_fee = st.number_input("Fee", value=float(row['Fee']), step=0.01)
                new_usdc = st.number_input("USDC", value=float(row['USDC']), step=0.01)
                new_czk_eur = round(new_czk / new_eur, 5) if new_eur > 0 else 0.0
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.fiat_df.loc[edit_idx] = {"Datum": new_datum, "CZK": new_czk, "EUR": new_eur, "Fee": new_fee, "CZK/EUR": new_czk_eur, "USDC": new_usdc, "NI": row.get('NI', ""), "GG": row.get('GG', ""), "ER": row.get('ER', "")}
                        save_fiat(st.session_state.fiat_df)
                        del st.session_state.editing_row
                        st.session_state.fiat_table_version += 1
                        st.session_state.ui_version += 1
                        st.success("✅ Row updated!")
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state.editing_row
                        st.rerun()
        st.subheader("➕ Add New Fiat Entry")
        with st.form("add_fiat"):
            col1, col2 = st.columns(2)
            with col1:
                selected_date = st.date_input("Date", value=date(2026, 3, 25))
                datum = date_to_excel_serial(selected_date)
            with col2:
                czk = st.number_input("CZK", value=1000.0, step=0.01)
            eur = st.number_input("EUR", value=40.0, step=0.01)
            fee = st.number_input("Fee", value=1.0, step=0.01)
            usdc = st.number_input("USDC", value=44.67, step=0.01)
            czk_eur = round(czk / eur, 5) if eur > 0 else 0.0
            if st.form_submit_button("➕ Add Entry"):
                new_row = pd.DataFrame([{"Datum": datum, "CZK": czk, "EUR": eur, "Fee": fee, "CZK/EUR": czk_eur, "USDC": usdc, "NI": "", "GG": "", "ER": ""}])
                st.session_state.fiat_df = pd.concat([st.session_state.fiat_df, new_row], ignore_index=True)
                save_fiat(st.session_state.fiat_df)
                st.session_state.fiat_table_version += 1
                st.session_state.ui_version += 1
                st.rerun()
