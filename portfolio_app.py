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

# ====================== GLOBAL CSS (Polished + Closer to Edges) ======================
st.markdown("""
<style>
/* ====================== GLOBAL LAYOUT - CLOSER TO EDGES ====================== */
.stApp {
    background: linear-gradient(180deg, #0f1724 0%, #0a0f1c 100%) !important;
}

/* Remove excessive Streamlit default padding - content hugs the edges */
.main .block-container,
.stMain .block-container,
div[data-testid="stMainBlockContainer"] {
    padding-left: 14px !important;
    padding-right: 14px !important;
    padding-top: 0px !important;
    max-width: 100% !important;
}

/* Slightly more breathing room on very wide screens */
@media (min-width: 1200px) {
    .main .block-container,
    div[data-testid="stMainBlockContainer"] {
        padding-left: 18px !important;
        padding-right: 18px !important;
    }
}

/* Mobile - comfortable but much closer to edges */
@media (max-width: 768px) {
    .main .block-container,
    div[data-testid="stMainBlockContainer"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
}

/* Clean top spacing */
.main, .block-container, .stMain {
    padding-top: 0px !important;
}

/* Glossy Header - Closer to top */
.glossy-header {
    position: relative;
    overflow: hidden;
    background: #26334f;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 32px 24px;
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
    margin-top: 68px;
    margin-bottom: 38px;
}

.glossy-header:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 15px 40px rgba(255,255,255,0.15);
}

.glossy-box {
    position: relative;
    overflow: hidden;
    background: #26334f;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 28px 30px;
    text-align: center;
    flex: 1;
    min-width: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.glossy-box:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 15px 40px rgba(255,255,255,0.15);
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

/* Buttons */
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
}

.stButton > button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 30px rgba(255, 255, 255, 0.25) !important;
    background: #263b5e !important;
    color: white !important;
}

@media (max-width: 700px) {
    .stApp { padding-top: 72px !important; }
    .glossy-header {
        margin-top: 48px !important;
        margin-bottom: 28px !important;
        padding: 24px 16px !important;
        font-size: 24px !important;
        min-height: 100px;
    }
}

@media (max-width: 600px) {
    .glossy-box {
        min-width: 98px !important;
        padding: 18px 14px !important;
    }
    .glossy-box > div:first-child { font-size: 12px !important; }
    .glossy-box > div:last-child { font-size: 21px !important; }
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

def get_chart_color(ticker: str) -> str:
    color_map = {
        'BTC': '#f7931a',   # orange
        'ETH': '#627eea',   # blue
        'SOL': '#9b59b6',   # purple
        'HBAR': '#00b4d8',  # cyan
        'XRP': '#1e3a8a',   # dark blue
        'BNB': '#f4c430',   # yellow
        'TRX': '#ff2d55',   # red
        'LINK': '#2ecc71',  # green
        'SUI': '#60a5fa',   # light blue
    }
    return color_map.get(ticker.upper(), '#00ff9d')

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
    if st.button("💾 Download Backup", use_container_width=True):
        data = {"crypto": json.loads(st.session_state.crypto_df.to_json(orient="records")),
                "fiat": json.loads(st.session_state.fiat_df.to_json(orient="records"))}
        st.download_button("Download JSON", json.dumps(data, indent=2), "portfolio_backup.json", "application/json")

# ====================== MAIN CONTENT ======================
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
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(98px, 1fr)); gap: 14px; margin-bottom: 30px;">
    <div class="glossy-box"><div>Total Value</div><div>{format_money(total_value)}</div></div>
    <div class="glossy-box"><div>PnL</div><div style="color:{'#00ff9d' if total_pnl>=0 else '#ff4d4d'}">{"▲" if total_pnl>0 else "▼" if total_pnl<0 else ""} {format_money(abs(total_pnl))}</div></div>
    <div class="glossy-box"><div>PnL %</div><div style="color:{'#00ff9d' if total_pnl_pct>=0 else '#ff4d4d'}">{"▲" if total_pnl_pct>0 else "▼" if total_pnl_pct<0 else ""} {abs(total_pnl_pct):.2f}%</div></div>
</div>"""
        st.markdown(value_box_html, unsafe_allow_html=True)
       
        cards_html = ""
        for _, r in df_port.iterrows():
            ticker = r['Ticker']
            pnl = r['PnL']
            pnl_color = "#00ff9d" if pnl > 0 else "#ff4d4d" if pnl < 0 else "#aaaaaa"
            arrow = "▲" if pnl > 0 else "▼" if pnl < 0 else ""
            base_color = get_ticker_color(ticker)
            border_color = base_color if base_color != '#000000' else '#ffffff'
            logo_url = get_ticker_logo(ticker)
            pnl_pct_formatted = format_percent(abs(r['PnL %'])) if pd.notna(r['PnL %']) else ""
            live_price = r['Live']
            avg_price = r['AVG']
           
            if ticker == 'USDC':
                cards_html += f"""
<div class="static-card usdc-card" data-border="{border_color}">
    <div class="card-header">
        <img src="{logo_url}" style="height:44px;width:44px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/44/1e2a44/ffffff?text=U';">
        <span style="font-weight:700;font-size:1.4rem;margin-left:12px;color:#ffffff;">{ticker}</span>
    </div>
    <div class="card-content">
        <div class="label-value-row"><span class="label">Holdings</span><span class="value">{format_holdings(r['Holdings'], ticker)}</span></div>
        <div class="label-value-row"><span class="label">Invested</span><span class="value">{format_money(r['USDC'])}</span></div>
        <div class="label-value-row"><span class="label">PnL</span><span class="value" style="color:{pnl_color};">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</span></div>
        <div class="label-value-row"><span class="label">PnL %</span><span class="value" style="color:{pnl_color};">{arrow} {pnl_pct_formatted}</span></div>
        <div class="label-value-row total"><span class="label">Value</span><span class="value total-value">{format_money(r['Value'])}</span></div>
    </div>
</div>
"""
            else:
                chart_color = get_chart_color(ticker)
                cards_html += f"""
<div class="flip-card" data-ticker="{ticker}" data-current-price="{live_price}" data-avg-price="{avg_price}" data-refresh="{st.session_state.refresh_key}" data-border="{border_color}" data-chart-color="{chart_color}" data-logo="{logo_url}">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="card-header">
                <img src="{logo_url}" style="height:44px;width:44px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/44/1e2a44/ffffff?text={ticker[0]}';">
                <span style="font-weight:700;font-size:1.4rem;margin-left:12px;color:#ffffff;">{ticker}</span>
            </div>
            <div class="card-content">
                <div class="label-value-row"><span class="label">Holdings</span><span class="value">{format_holdings(r['Holdings'], ticker)}</span></div>
                <div class="label-value-row"><span class="label">Invested</span><span class="value">{format_money(r['USDC'])}</span></div>
                <div class="label-value-row"><span class="label">PnL</span><span class="value" style="color:{pnl_color};">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</span></div>
                <div class="label-value-row"><span class="label">PnL %</span><span class="value" style="color:{pnl_color};">{arrow} {pnl_pct_formatted}</span></div>
                <div class="label-value-row total"><span class="label">Value</span><span class="value total-value">{format_money(r['Value'])}</span></div>
            </div>
        </div>
        <div class="flip-card-back">
            <div class="back-header">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="{logo_url}" style="height:34px;width:34px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/34/1e2a44/ffffff?text={ticker[0]}';">
                    <span style="color:#ffffff; font-size:1.2rem; font-weight:600;">{ticker}</span>
                </div>
                <span class="back-close">↺</span>
            </div>
            <div class="chart-container">
                <canvas id="chart-{ticker}" width="400" height="160" style="width:100%; height:auto; max-height:160px;"></canvas>
                <div class="chart-loading" id="loading-{ticker}">Loading chart...</div>
            </div>
            <div class="back-stats">
                <div class="stat-item"><div class="stat-label">Current</div><div class="stat-value">${live_price:,.2f}</div></div>
                <div class="stat-item"><div class="stat-label">24h Change</div><div class="stat-value" id="change-{ticker}">loading...</div></div>
                <div class="stat-item"><div class="stat-label">Avg</div><div class="stat-value">${avg_price:,.2f}</div></div>
            </div>
        </div>
    </div>
</div>
"""
       
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            overflow-x: hidden;
            background: transparent;
        }}
        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            color: white;
        }}
        .scroll-wrapper {{
            width: 100%;
            overflow-y: auto;
            overflow-x: visible;
            height: auto;
            max-height: 70vh;
            padding: 12px 0px 20px 0px;
            margin-bottom: 20px;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        .scroll-wrapper::-webkit-scrollbar {{ display: none; }}
        .coin-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
            width: 100%;
            box-sizing: border-box;
            background: transparent !important;
            overflow: visible !important;
        }}
        /* Card sizes - original height */
        .flip-card {{
            background-color: transparent;
            width: 100%;
            height: 280px;
            perspective: 1200px;
            cursor: pointer;
        }}
        .flip-card-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.5s ease-in-out;
            transform-style: preserve-3d;
            border-radius: 18px;
        }}
        .flip-card.flipped .flip-card-inner {{
            transform: rotateY(180deg);
        }}
        .flip-card-front, .flip-card-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 18px;
            padding: 12px 14px;
            background: #0f172a;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border: 2px solid transparent;
            overflow-y: auto;
        }}
        .flip-card-front {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .flip-card-back {{
            transform: rotateY(180deg);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .static-card {{
            background: #0f172a;
            border-radius: 18px;
            padding: 12px 14px;
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border: 2px solid transparent;
            transition: all 0.25s ease;
        }}
        /* No hover pop animation for USDC card */
        .static-card.usdc-card:hover {{
            transform: none;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border-color: var(--border);
        }}
        .static-card:hover {{
            border-color: var(--border);
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(0,0,0,0.5);
        }}
        .flip-card:hover .flip-card-front,
        .flip-card:hover .flip-card-back {{
            border-color: var(--border);
            box-shadow: 0 12px 28px rgba(0,0,0,0.5);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .card-content {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .label-value-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.95rem;
            line-height: 1.3;
        }}
        .label {{ color: #aaa; font-weight: 500; }}
        .value {{ font-weight: 600; color: white; font-size: 1rem; }}
        .total {{
            font-size: 1.05rem;
            margin-top: 6px;
            border-top: 1px solid rgba(255,255,255,0.15);
            padding-top: 6px;
        }}
        .total-value {{ font-size: 1.15rem; font-weight: 700; }}
        .back-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 6px;
            color: #00ff9d;
        }}
        .back-close {{
            font-size: 1.3rem;
            cursor: pointer;
            background: rgba(255,255,255,0.1);
            width: 28px;
            height: 28px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: 0.2s;
            color: white;
        }}
        .back-close:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .chart-container {{
            position: relative;
            margin: 4px 0;
            flex: 1;
            min-height: 160px;
        }}
        .chart-loading {{
            text-align: center;
            color: #ccc;
            padding: 10px;
            font-size: 0.85rem;
        }}
        .back-stats {{
            display: flex;
            justify-content: space-between;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px solid rgba(255,255,255,0.15);
            gap: 12px;
        }}
        .stat-item {{
            text-align: center;
            flex: 1;
        }}
        .stat-label {{
            font-size: 0.7rem;
            color: #aaa;
            margin-bottom: 2px;
            font-weight: 500;
        }}
        .stat-value {{
            font-size: 0.85rem;
            font-weight: 600;
            color: white;
        }}
        @media (max-width: 700px) {{
            .coin-grid {{ grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; }}
            .flip-card, .static-card {{ height: 270px; }}
            .scroll-wrapper {{ padding: 12px 0px 16px 0px; }}
        }}
    </style>
</head>
<body>
<div class="scroll-wrapper">
    <div class="coin-grid">
        {cards_html}
    </div>
</div>
<script>
    (function() {{
        const flipCards = document.querySelectorAll('.flip-card');
        const chartCache = {{}};
        const refreshKey = '{st.session_state.refresh_key}';
        
        async function fetch24hChange(ticker) {{
            const symbolMap = {{
                'BTC':'BTC','ETH':'ETH','SOL':'SOL','HBAR':'HBAR',
                'XRP':'XRP','BNB':'BNB','TRX':'TRX','LINK':'LINK','SUI':'SUI'
            }};
            const sym = symbolMap[ticker.toUpperCase()];
            if (!sym) return null;
            const url = `https://min-api.cryptocompare.com/data/v2/histoday?fsym=${{sym}}&tsym=USD&limit=2`;
            try {{
                const resp = await fetch(url, {{ headers: {{ 'User-Agent': 'Mozilla/5.0' }} }});
                const data = await resp.json();
                if (data && data.Data && data.Data.Data && data.Data.Data.length >= 2) {{
                    const yesterdayClose = data.Data.Data[0].close;
                    const todayClose = data.Data.Data[1].close;
                    const change = ((todayClose - yesterdayClose) / yesterdayClose) * 100;
                    return change;
                }}
                return null;
            }} catch(e) {{
                console.error("24h change error", ticker, e);
                return null;
            }}
        }}
        
        async function fetchHistoricalData(ticker) {{
            const symbolMap = {{
                'BTC':'BTC','ETH':'ETH','SOL':'SOL','HBAR':'HBAR',
                'XRP':'XRP','BNB':'BNB','TRX':'TRX','LINK':'LINK','SUI':'SUI'
            }};
            const sym = symbolMap[ticker.toUpperCase()];
            if (!sym) return null;
            const url = `https://min-api.cryptocompare.com/data/v2/histoday?fsym=${{sym}}&tsym=USD&limit=30`;
            try {{
                const resp = await fetch(url, {{ headers: {{ 'User-Agent': 'Mozilla/5.0' }} }});
                const data = await resp.json();
                if (data && data.Data && data.Data.Data) {{
                    const ohlc = data.Data.Data;
                    const labels = ohlc.map(d => {{
                        const dt = new Date(d.time * 1000);
                        return `${{dt.getDate().toString().padStart(2,'0')}}/${{(dt.getMonth()+1).toString().padStart(2,'0')}}`;
                    }});
                    const prices = ohlc.map(d => d.close);
                    return {{ labels, prices }};
                }}
                return null;
            }} catch(e) {{
                console.error("Fetch error for", ticker, e);
                return null;
            }}
        }}
        
        async function renderChart(card, ticker, currentPrice, avgPrice, chartColor) {{
            const canvas = card.querySelector(`canvas#chart-${{ticker}}`);
            const loadingDiv = card.querySelector(`.chart-loading`);
            if (!canvas) return;
            if (chartCache[ticker] && chartCache[ticker].chart) {{
                if (loadingDiv) loadingDiv.style.display = 'none';
                return;
            }}
            if (loadingDiv) loadingDiv.style.display = 'block';
            const hist = await fetchHistoricalData(ticker);
            if (!hist || hist.prices.length === 0) {{
                if (loadingDiv) loadingDiv.innerText = 'Failed to load chart data';
                return;
            }}
            const ctx = canvas.getContext('2d');
            if (chartCache[ticker] && chartCache[ticker].chartObj) {{
                chartCache[ticker].chartObj.destroy();
            }}
            const datasets = [
                {{
                    label: 'Close Price (USD)',
                    data: hist.prices,
                    borderColor: chartColor,
                    backgroundColor: chartColor + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.2,
                    pointRadius: 2,
                    pointBackgroundColor: chartColor
                }}
            ];
            if (avgPrice > 0) {{
                const avgData = new Array(hist.labels.length).fill(avgPrice);
                datasets.push({{
                    label: 'Avg: $' + avgPrice.toFixed(2),
                    data: avgData,
                    borderColor: '#ffaa00',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    type: 'line'
                }});
            }}
            const newChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: hist.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ mode: 'index', intersect: false }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#ccc', maxRotation: 45, autoSkip: true, maxTicksLimit: 6 }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }},
                        y: {{ ticks: {{ color: '#ccc' }}, grid: {{ color: 'rgba(255,255,255,0.1)' }} }}
                    }}
                }}
            }});
            chartCache[ticker] = {{ chartObj: newChart, data: hist }};
            if (loadingDiv) loadingDiv.style.display = 'none';
        }}
        
        async function update24hChange(card, ticker) {{
            const statDiv = card.querySelector(`#change-${{ticker}}`);
            if (!statDiv) return;
            const change = await fetch24hChange(ticker);
            if (change !== null) {{
                const sign = change >= 0 ? '▲' : '▼';
                const color = change >= 0 ? '#00ff9d' : '#ff4d4d';
                statDiv.innerHTML = `<span style="color:${{color}};">${{sign}} ${{Math.abs(change).toFixed(2)}}%</span>`;
            }} else {{
                statDiv.innerHTML = `N/A`;
            }}
        }}
        
        flipCards.forEach(card => {{
            const ticker = card.getAttribute('data-ticker');
            const currentPrice = parseFloat(card.getAttribute('data-current-price'));
            const avgPrice = parseFloat(card.getAttribute('data-avg-price'));
            const chartColor = card.getAttribute('data-chart-color');
            const border = card.getAttribute('data-border');
            card.style.setProperty('--border', border);
            
            // Front click to flip
            const front = card.querySelector('.flip-card-front');
            front.addEventListener('click', (e) => {{
                e.stopPropagation();
                if (!card.classList.contains('flipped')) {{
                    card.classList.add('flipped');
                    if (!chartCache[ticker] || !chartCache[ticker].chartObj) {{
                        renderChart(card, ticker, currentPrice, avgPrice, chartColor);
                        update24hChange(card, ticker);
                    }}
                }}
            }});
            
            // Back click: flip back when clicking anywhere on the back (except if close button stops propagation)
            const backDiv = card.querySelector('.flip-card-back');
            const closeBtn = backDiv.querySelector('.back-close');
            if (closeBtn) {{
                closeBtn.addEventListener('click', (e) => {{
                    e.stopPropagation();
                    card.classList.remove('flipped');
                }});
            }}
            // Click on back area (not on close button) also flips back
            backDiv.addEventListener('click', (e) => {{
                // If the click target is not the close button (or its children)
                if (e.target === closeBtn || closeBtn.contains(e.target)) {{
                    // Already handled by closeBtn listener
                    return;
                }}
                card.classList.remove('flipped');
            }});
        }});
        
        document.querySelectorAll('.static-card').forEach(card => {{
            const border = card.getAttribute('data-border');
            if (border) card.style.setProperty('--border', border);
        }});
        
        if (window.oldRefreshKey && window.oldRefreshKey !== refreshKey) {{
            for (let key in chartCache) {{
                if (chartCache[key].chartObj) chartCache[key].chartObj.destroy();
            }}
            window.chartCache = {{}};
        }}
        window.oldRefreshKey = refreshKey;
    }})();
</script>
</body>
</html>
"""
        components.html(full_html, height=680, scrolling=False)
   
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
                    st.session_state.crypto_table_version += 1
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
.transaction-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 16px; padding: 0 6px; }}
.transaction-card {{
    background: #0f172a;
    border-radius: 18px;
    padding: 18px 20px 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    transition: all 0.25s ease;
    position: relative;
    display: flex;
    flex-direction: column;
    min-height: 138px;
}}
.transaction-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 255, 157, 0.3);
}}
.transaction-main-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}}
.transaction-left {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex: 1;
}}
.transaction-ticker {{
    font-size: 1.28rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.05;
}}
.transaction-date {{
    color: #aaa;
    font-size: 0.92rem;
    margin-top: 2px;
}}
.transaction-values {{
    display: flex;
    gap: 24px;
    text-align: right;
    font-size: 1.02rem;
}}
.transaction-values div {{
    min-width: 88px;
}}
.transaction-values small {{
    color: #aaa;
    font-size: 0.82rem;
    font-weight: 500;
    display: block;
}}
.transaction-values strong {{
    font-weight: 700;
    color: #ffffff;
}}
.transaction-amount {{
    font-size: 1.04rem;
    font-weight: 700;
    color: #ffffff;
}}
.transaction-buttons {{
    display: flex;
    gap: 12px;
    margin-top: auto;
}}
.transaction-buttons button {{
    flex: 1;
    padding: 10px 14px;
    border: none;
    border-radius: 11px;
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s ease;
}}
.transaction-buttons .delete-btn {{
    background: #e63939;
    color: white;
}}
.transaction-buttons .delete-btn:hover {{
    background: #c1121f;
}}
.transaction-buttons .edit-btn {{
    background: #00b894;
    color: #0f1724;
}}
.transaction-buttons .edit-btn:hover {{
    background: #00a17a;
}}
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
