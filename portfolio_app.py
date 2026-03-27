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
st.set_page_config(page_title="Portfolio", layout="wide")

# ====================== GLOBAL CSS ======================
st.markdown("""
<style>
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
/* Glossy shine for main content */
.glossy-header,
.glossy-box {
    position: relative;
    overflow: hidden;
    background: #1e2a44;
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
/* COMPACT TABLE FIX */
[data-testid="stHorizontalBlock"] > div:nth-child(6),
[data-testid="stHorizontalBlock"] > div:nth-child(7),
[data-testid="stHorizontalBlock"] > div:nth-child(8) {
    min-width: 48px !important;
    max-width: 52px !important;
}
.stButton > button {
    padding: 8px 12px !important;
    font-size: 1.1rem !important;
    min-height: 42px !important;
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

# ====================== BINANCE API (gold standard for crypto candles) ======================
BINANCE_BASE = "https://api.binance.com/api/v3"

def get_with_retry(url: str, headers: dict, timeout: int = 12, retries: int = 5) -> dict | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(1.4 ** attempt)
    return None

@st.cache_data(ttl=15, show_spinner=False)
def get_all_binance_prices(tickers):
    prices = {"USDC": 1.0}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for ticker in set(tickers):
        if ticker.upper() == "USDC":
            continue
        symbol = ticker.upper() + "USDT"
        try:
            url = f"{BINANCE_BASE}/ticker/price?symbol={symbol}"
            data = get_with_retry(url, headers)
            if data and "price" in data:
                prices[ticker] = float(data["price"])
        except:
            continue
    return prices

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_open(ticker: str):
    symbol = ticker.upper() + "USDT"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        url = f"{BINANCE_BASE}/klines?symbol={symbol}&interval=1d&limit=2"
        data = get_with_retry(url, headers)
        if data and len(data) >= 2:
            return float(data[-2][1])
        return 0.0
    except:
        return 0.0

@st.cache_data(ttl=80, show_spinner=False)
def get_binance_ohlc(ticker: str, candle: str):
    symbol = ticker.upper() + "USDT"
    interval_map = {"5m": "5m", "30m": "30m", "1h": "1h", "4h": "4h", "1D": "1d"}
    interval = interval_map.get(candle, "4h")
    limit = 1000 if candle != "1D" else 90
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        url = f"{BINANCE_BASE}/klines?symbol={symbol}&interval={interval}&limit={limit}"
        data = get_with_retry(url, headers)
        if not data:
            return None
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'n', 'taker_base', 'taker_quote', 'ignore'])
        df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']].copy()
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        df = df.astype(float)
        df.rename(columns={'volume': 'volumefrom'}, inplace=True)
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
        'LINK': 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png',
        'BNB': 'https://assets.coingecko.com/coins/images/825/small/binance-coin-logo.png',
        'TRX': 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png',
    }
    if ticker in known:
        return known[ticker]
    return f"https://cryptologos.cc/logos/{ticker.lower()}-logo.png"

def get_ticker_color(ticker: str) -> str:
    ticker = ticker.upper()
    known = {'USDC': '#2775ca', 'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9b59b6', 'HBAR': '#000000', 'XRP': '#000000', 'LINK': '#1e3a8a', 'BNB': '#f4c430', 'TRX': '#ff2d55'}
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
    live_prices = get_all_binance_prices(coin_tickers)

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
        st.session_state.ui_version += 1
        st.success("✅ Refreshing prices & charts...")
        st.rerun()

# ====================== MAIN CONTENT ======================
main_container = st.empty()

def glossy_header(title: str, icon_svg: str):
    html = f"""<div class="glossy-header">{icon_svg}<span style="margin-left:12px;">{title}</span></div>"""
    st.markdown(html, unsafe_allow_html=True)

# ====================== PAGES ======================
main_container.empty()
with main_container.container(key=f"page_{st.session_state.page}_{st.session_state.ui_version}"):
    if st.session_state.page == "Home":
        glossy_header("Portfolio Dashboard", DASHBOARD_ICON)
     
        df_port, total_value, total_pnl, total_pnl_pct = calculate_portfolio(st.session_state.crypto_df)
     
        value_box_html = f"""
<div style="display:flex;gap:25px;margin-bottom:30px;flex-wrap:wrap;">
    <div class="glossy-box"><div>Total Value</div><div>{format_money(total_value)}</div></div>
    <div class="glossy-box"><div>PnL</div><div style="color:{'#00ff9d' if total_pnl>=0 else '#ff4d4d'}">{"▲" if total_pnl>0 else "▼" if total_pnl<0 else ""} {format_money(abs(total_pnl))}</div></div>
    <div class="glossy-box"><div>PnL %</div><div style="color:{'#00ff9d' if total_pnl_pct>=0 else '#ff4d4d'}">{"▲" if total_pnl_pct>0 else "▼" if total_pnl_pct<0 else ""} {abs(total_pnl_pct):.2f}%</div></div>
</div>"""
        st.markdown(value_box_html, unsafe_allow_html=True)

        coin_list = [t for t in df_port['Ticker'] if t != 'USDC']
        rows_html = ""
        for _, r in df_port.iterrows():
            pnl = r['PnL']
            pnl_color = "#00ff9d" if pnl > 0 else "#ff4d4d" if pnl < 0 else "#aaaaaa"
            arrow = "▲" if pnl > 0 else "▼" if pnl < 0 else ""
            base_color = get_ticker_color(r['Ticker'])
            glow_color = '#ffffffaa' if base_color == '#000000' else base_color + '99'
            ticker = r['Ticker']
            onclick = f"onclick=\"switchToTab({coin_list.index(ticker)})\" " if ticker != 'USDC' else ""
            row_class = "clickable-row" if ticker != 'USDC' else ""
            logo_url = get_ticker_logo(ticker)
            rows_html += f"""<tr><td colspan="6" style="padding:0;">
                <div class="row-inner {row_class}" data-glow="{glow_color}" style="display:flex;justify-content:space-between;align-items:center;margin:6px auto 6px;" {onclick}>
                    <div style="display:flex;align-items:center;gap:8px;min-width:100px;">
                        <img src="{logo_url}" style="height:36px;width:36px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/36/1e2a44/ffffff?text={ticker[0]}';">
                        <span style="font-weight:600;">{ticker}</span>
                    </div>
                    <div style="flex:1;text-align:center;">{format_holdings(r['Holdings'], r['Ticker'])}</div>
                    <div style="flex:1;text-align:center;">{format_money(r['USDC'])}</div>
                    <div style="flex:1;text-align:center;color:{pnl_color};font-weight:600;">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</div>
                    <div style="flex:1;text-align:center;color:{pnl_color};font-weight:600;">{arrow} {format_percent(abs(r['PnL %']) if pd.notna(r['PnL %']) else "")}</div>
                    <div style="flex:1;text-align:center;">{format_money(r['Value'])}</div>
                </div>
            </td></tr>"""
      
        html = f"""<html><head><style>body{{background:#0b1120;color:white;font-family:sans-serif;margin:0;}}table{{width:100%;border-spacing:0;table-layout:fixed;min-width:850px;}}thead{{position:sticky;top:0;z-index:9999;background:#0f172a;}}thead th{{padding:12px 8px;text-align:center;font-size:0.95rem;}}td{{padding:0;background:transparent;}}.row-inner{{position:relative;z-index:1;width:98%;padding:8px 10px;border-radius:18px;background:#0f172a;display:flex;justify-content:space-between;align-items:center;transition:transform 0.22s cubic-bezier(0.4,0,0.2,1),box-shadow 0.25s cubic-bezier(0.4,0,0.2,1);cursor:default;font-size:0.95rem;}}@media (max-width:900px){{.row-inner{{padding:6px 8px;}}thead th{{font-size:0.85rem;padding:8px 6px;}}}}.clickable-row{{cursor:pointer;}}.row-inner:hover{{transform:translateY(-2px) scale(1.01);box-shadow:0 0 45px var(--glow)!important;z-index:20;}}.scroll-container{{max-height:460px;overflow-y:auto;overflow-x:auto;position:relative;}} .scroll-container::-webkit-scrollbar{{display:none;}}@media (max-height: 800px) {{ .scroll-container {{ max-height: 460px; }} }}</style></head><body><div class="scroll-container"><table><thead><tr><th>Ticker</th><th>Holdings</th><th>USDC</th><th>PnL</th><th>PnL %</th><th>Value</th></tr></thead><tbody>{rows_html}</tbody></table></div><script>function switchToTab(index){{const tabs=window.parent.document.querySelectorAll('.stTabs button');if(tabs&&tabs[index])tabs[index].click();}}document.querySelectorAll('.row-inner').forEach(div=>{{div.style.setProperty('--glow',div.getAttribute('data-glow'));}});</script><!-- VERSION:{st.session_state.ui_version} --></body></html>"""
      
        components.html(html, height=485, scrolling=True)
        st.markdown("""<div class="glossy-box" style="background:#1e2a44;padding:22px 30px;border-radius:18px;margin:35px 0 25px 0;"><div style="color:#ffffff;font-weight:700;font-size:26px;text-align:center;">Price Charts + Volume</div></div>""", unsafe_allow_html=True)
      
        if coin_list:
            selected_tab = st.tabs(coin_list)
            for i, coin in enumerate(coin_list):
                with selected_tab[i]:
                    avg_row = df_port.loc[df_port['Ticker'] == coin, 'AVG']
                    avg_price = avg_row.iloc[0] if not avg_row.empty and pd.notna(avg_row.iloc[0]) else None
                    live_price = df_port.loc[df_port['Ticker'] == coin, 'Live'].iloc[0] if not df_port.loc[df_port['Ticker'] == coin].empty else 0
                    
                    daily_open = get_daily_open(coin)
                    daily_change_pct = ((live_price - daily_open) / daily_open * 100) if daily_open > 0 else 0
                    daily_arrow = "▲" if daily_change_pct > 0 else "▼" if daily_change_pct < 0 else ""
                    daily_color = "#00ff9d" if daily_change_pct > 0 else "#ff4d4d" if daily_change_pct < 0 else "#aaaaaa"
                    
                    color = "#00ff9d" if live_price > 0 else "#ff4d4d"
                    st.markdown(f"""
                    <div style="display:flex;gap:4px;margin-bottom:16px;">
                        <div style="background:#0f172a;padding:8px 18px;border-radius:9999px;display:inline-flex;align-items:center;gap:10px;">
                            <span style="font-size:1.15rem;font-weight:700;">LIVE</span>
                            <span style="font-size:1.45rem;font-weight:700;color:{color};">{format_crypto_price(live_price)}</span>
                        </div>
                        <div style="background:#0f172a;padding:2px 7px;border-radius:9999px;display:inline-flex;align-items:center;gap:2px;">
                            <span style="font-size:0.85rem;font-weight:600;color:{daily_color};">{daily_arrow} {abs(daily_change_pct):.2f}%</span>
                        </div>
                        {f'<div style="background:#0f172a;padding:8px 18px;border-radius:9999px;display:inline-flex;align-items:center;gap:10px;margin-left:16px;"><span style="font-size:1.15rem;font-weight:700;color:#ffffff;">AVG</span><span style="font-size:1.45rem;font-weight:700;color:#ffaa00;">{format_crypto_price(avg_price)}</span></div>' if avg_price is not None else ''}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([0.8, 4.2])
                    with col1:
                        candle = st.selectbox(
                            "Timeframe",
                            options=["5m", "30m", "1h", "4h", "1D"],
                            index=3,
                            key=f"candle_select_{coin}_{st.session_state.ui_version}",
                            label_visibility="collapsed"
                        )
                    
                    title = f"{coin} — {candle} candles"
                    
                    data = get_binance_ohlc(coin, candle)
                    
                    if data is not None and not data.empty:
                        data_local = data.copy()
                        
                        # EXTREMELY THIN VOLUME PANEL + LOCKED AXIS
                        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                                            row_heights=[0.90, 0.10], subplot_titles=("", "Volume"))
                        
                        fig.add_trace(go.Candlestick(
                            x=data_local.index,
                            open=data_local['open'],
                            high=data_local['high'],
                            low=data_local['low'],
                            close=data_local['close'],
                            increasing_line_color='#00ff9d',
                            decreasing_line_color='#ff4d4d',
                            increasing_fillcolor='#00ff9d',
                            decreasing_fillcolor='#ff4d4d',
                            name='Price'
                        ), row=1, col=1)
                        
                        if avg_price is not None:
                            fig.add_trace(go.Scatter(
                                x=[data_local.index.min(), data_local.index.max()],
                                y=[avg_price, avg_price],
                                mode='lines',
                                line=dict(color='#ffaa00', width=2, dash='dash'),
                                name=f'Your AVG: ${avg_price:,.2f}'
                            ), row=1, col=1)
                        
                        colors_volume = ['#00ff9d' if o < c else '#ff4d4d' for o, c in zip(data_local['open'], data_local['close'])]
                        fig.add_trace(go.Bar(
                            x=data_local.index,
                            y=data_local['volumefrom'],
                            marker_color=colors_volume,
                            name='Volume',
                            opacity=0.85
                        ), row=2, col=1)
                        
                        fig.update_layout(
                            title=title,
                            height=700,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='white',
                            hovermode="x unified",
                            xaxis_rangeslider_visible=False,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, bgcolor="rgba(0,0,0,0)"),
                            dragmode='pan'
                        )
                        
                        # VOLUME AXIS: 0 ALWAYS AT BOTTOM + HEAVILY COMPRESSED
                        max_vol = data_local['volumefrom'].max() or 1
                        fig.update_yaxes(
                            rangemode='nonnegative',
                            range=[0, max_vol * 40],      # extreme compression → tiny bars
                            fixedrange=True,               # lock the axis completely
                            showticklabels=False,          # clean TradingView look
                            showgrid=False,
                            row=2, col=1
                        )
                        
                        if len(data_local) > 0:
                            min_time = data_local.index.min()
                            max_time = data_local.index.max()
                            fig.update_xaxes(range=[min_time, max_time], autorange=False, minallowed=min_time, maxallowed=max_time)
                        
                        st.plotly_chart(
                            fig,
                            use_container_width=True,
                            config={
                                'scrollZoom': True,
                                'responsive': True,
                                'displayModeBar': True,
                                'modeBarButtonsToRemove': ['zoom2d', 'select2d', 'lasso2d'],
                                'doubleClick': 'reset'
                            },
                            key=f"chart_{coin}_{candle}_{st.session_state.ui_version}"
                        )
                    else:
                        st.error(f"📉 Could not load {coin} chart. Try the **Refresh** button in sidebar.")

        st.caption("🔴 Live prices update automatically every 30 seconds")
        time.sleep(30)
        st.rerun()

    # ====================== CRYPTO TRANSACTIONS ======================
    elif st.session_state.page == "Crypto Transactions":
        glossy_header("Crypto Transactions", CRYPTO_ICON)
        df_display = st.session_state.crypto_df.copy()
        df_display['Date'] = df_display['Datum'].apply(format_datum)
        df_display = df_display.dropna(how='all').reset_index(drop=True)
      
        table_container = st.container(key=f"crypto_table_container_{st.session_state.ui_version}")
        with table_container:
            with st.container(height=520, border=True):
                h = st.columns([1.0, 0.9, 0.7, 1.0, 1.0, 0.4, 0.4])
                h[0].markdown("**Date**")
                h[1].markdown("**USDC**")
                h[2].markdown("**Ticker**")
                h[3].markdown("**Amount**")
                h[4].markdown("**Price**")
                h[5].markdown("**Delete**")
                h[6].markdown("**Edit**")
                for i, r in df_display.iterrows():
                    cols = st.columns([1.0, 0.9, 0.7, 1.0, 1.0, 0.4, 0.4])
                    with cols[0]: st.write(r['Date'])
                    with cols[1]: st.write(format_money(r['USDC']))
                    with cols[2]: st.write(r['Ticker'])
                    with cols[3]: st.write(format_holdings(r['Amount'], r['Ticker']))
                    with cols[4]: st.write(format_money(r['Price']))
                    with cols[5]:
                        if st.button("🗑️", key=f"del_crypto_{i}_{st.session_state.crypto_table_version}_{st.session_state.ui_version}"):
                            st.session_state.crypto_df = st.session_state.crypto_df.drop(i).reset_index(drop=True)
                            save_crypto(st.session_state.crypto_df)
                            st.session_state.crypto_table_version += 1
                            st.session_state.ui_version += 1
                            st.success("✅ Row deleted!")
                            st.rerun()
                    with cols[6]:
                        if st.button("✏️", key=f"edit_crypto_{i}_{st.session_state.crypto_table_version}_{st.session_state.ui_version}"):
                            st.session_state.editing_row_crypto = i
                            st.rerun()
        if 'editing_row_crypto' in st.session_state:
            edit_idx = st.session_state.editing_row_crypto
            row = st.session_state.crypto_df.loc[edit_idx]
            st.markdown("**Edit row**")
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
                        st.success("✅ Row updated!")
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

# Auto-refresh
time.sleep(600)
st.rerun()
