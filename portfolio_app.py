import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import time
import streamlit.components.v1 as components
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
.stApp {
    background: linear-gradient(180deg, #0f1724 0%, #0a0f1c 100%) !important;
}
.main .block-container,
.stMain .block-container,
div[data-testid="stMainBlockContainer"] {
    padding-left: 14px !important;
    padding-right: 14px !important;
    padding-top: 0px !important;
    max-width: 100% !important;
}
@media (min-width: 1200px) {
    .main .block-container,
    div[data-testid="stMainBlockContainer"] {
        padding-left: 18px !important;
        padding-right: 18px !important;
    }
}
@media (max-width: 768px) {
    .main .block-container,
    div[data-testid="stMainBlockContainer"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
}
.main, .block-container, .stMain {
    padding-top: 0px !important;
}

/* Dashboard Pullable Drawer Styles */
.dashboard-wrapper {
    position: relative;
    z-index: 10;
}
.glossy-header-label {
    cursor: pointer;
    display: block;
    position: relative;
    z-index: 3;
    -webkit-tap-highlight-color: transparent;
}
.home-header {
    margin-bottom: 0 !important;
    padding-bottom: 30px !important; /* space for the eye icon */
}
.pull-indicator {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    color: #64748b;
    opacity: 0.8;
    transition: color 0.3s ease;
}
@media (hover: hover) and (pointer: fine) {
    .glossy-header-label:hover .pull-indicator {
        color: #cbd5e1;
    }
}
.pull-indicator .eye-open { display: none; }
.pull-indicator .eye-closed { display: block; }

.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator .eye-open { display: block; }
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator .eye-closed { display: none; }
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator { color: #ffffff; }

.stats-layer {
    position: relative;
    z-index: 1;
    margin-top: -60px !important; 
    transition: margin-top 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 24px;
}
.dashboard-toggle:checked ~ .dashboard-wrapper .stats-layer {
    margin-top: 14px !important; /* Drops down */
}

/* Force 3 columns globally without wrapping */
.stats-layer-inner {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 14px;
    width: 100%;
}

/* Tucked Text Fade Out */
.dash-value {
    font-size: clamp(14px, 2.5vw, 24px) !important; /* Fluid typography */
    font-weight: 700;
    line-height: 1.05;
    color: #ffffff;
    position: absolute;
    top: 20px;
    left: 0;
    width: 100%;
    text-align: center;
    margin: 0;
    transition: opacity 0.3s ease;
    padding: 0 4px;
    box-sizing: border-box;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.dashboard-toggle:not(:checked) ~ .dashboard-wrapper .stats-layer .dash-value {
    opacity: 0;
    pointer-events: none;
}

.dash-label {
    font-size: 11px !important;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #94a3b8;
    line-height: 1.2;
    position: absolute;
    bottom: 8px;
    left: 0;
    width: 100%;
    text-align: center;
}

.glossy-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease, border-color 0.4s ease;
    padding: 32px 24px;
    min-height: 130px;
    font-size: 29px;
    font-weight: 700;
    letter-spacing: 1.5px;
    line-height: 1.1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    width: 100% !important;
    margin-top: 68px;
    margin-bottom: 38px;
}

/* PC Hover and Sync with Dashboard Toggle */
@media (hover: hover) and (pointer: fine) {
    .glossy-header-label:hover .glossy-header {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
        border-color: rgba(255, 255, 255, 0.15);
    }
}
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.15);
}

.glossy-box {
    position: relative;
    overflow: hidden;
    background: linear-gradient(180deg, #162032 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 28px 30px;
    text-align: center;
    flex: 1;
    min-width: 220px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.glossy-box:not(.swapped) > div:first-child {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 6px;
    line-height: 1.2;
}
.glossy-box:not(.swapped) > div:last-child {
    font-size: 27px;
    font-weight: 700;
    line-height: 1.05;
    color: #ffffff;
}

.glossy-box.swapped {
    min-width: 0 !important;
    height: 80px !important;
    min-height: 80px !important;
    max-height: 80px !important;
    padding: 0;
    display: block;
}

/* Subdued and Smaller USDC Banner */
.usdc-banner {
    position: relative;
    overflow: hidden;
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(39, 117, 202, 0.2);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 10px 20px;
    width: 90%; 
    max-width: 400px; 
    margin: 0 auto 24px auto; 
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.usdc-banner-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.usdc-banner-left img {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    object-fit: contain;
    opacity: 0.85;
}
.usdc-banner-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.usdc-banner-subtitle {
    font-size: 0.75rem;
    font-weight: 500;
    color: #64748b;
}
.usdc-banner-amount {
    font-size: 1.2rem;
    font-weight: 600;
    color: #e2e8f0;
}

/* Native CSS Privacy Mode for USDC Banner */
.dashboard-toggle:not(:checked) ~ .usdc-banner .usdc-banner-amount {
    font-size: 0 !important; /* Hides text perfectly without shifting layout */
}
.dashboard-toggle:not(:checked) ~ .usdc-banner .usdc-banner-amount::after {
    content: '***';
    font-size: 1.2rem;
    color: #e2e8f0;
}

/* GLOBALLY HIDE NUMBER INPUT STEP BUTTONS (+ / -) */
button[aria-label="Step Up"],
button[aria-label="Step Down"],
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    display: none !important;
}
input[type="number"]::-webkit-inner-spin-button, 
input[type="number"]::-webkit-outer-spin-button { 
    -webkit-appearance: none; 
    margin: 0; 
}
input[type="number"] {
    -moz-appearance: textfield;
}

</style>
""", unsafe_allow_html=True)

# ====================== SVG ICONS ======================
DASHBOARD_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'''
CRYPTO_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M14.5 8.5L9.5 13.5"/><path d="M9.5 8.5L14.5 13.5"/></svg>'''
FIAT_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h12"/><path d="M6 12h12"/><path d="M6 16h12"/></svg>'''
EYE_CLOSED = '''<svg class="eye-closed" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>'''
EYE_OPEN = '''<svg class="eye-open" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'''
EXTERNAL_LINK_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'''
TV_ICON = '''<svg xmlns="http://www.w3.org/2000/svg" width="18" height="14" viewBox="0 0 28 21" fill="currentColor"><path d="M12 21H8V3h4v18zm1.5-6h3.5l3.5-4.5V21h-7v-6zM28 21h-4l-6.5-9L21 6l7 10v5z"/></svg>'''

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

def parse_excel_date(x):
    try:
        return (datetime(1899, 12, 30) + timedelta(days=int(float(x)))).date()
    except:
        return datetime.now().date()

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
            data = resp.json()
            if isinstance(data, dict) and data.get('Response') == 'Error':
                if attempt == retries - 1:
                    return None
                time.sleep(1.5 ** attempt)
                continue
            return data
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(1.5 ** attempt)
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

# ====================== HISTORICAL PORTFOLIO BUILDER ======================
@st.cache_data(ttl=3600, show_spinner=False)
def build_portfolio_history(crypto_df, fiat_df, last_prices, refresh_key):
    if crypto_df.empty and fiat_df.empty: return [], "", pd.DataFrame()

    fiat = fiat_df.copy()
    if not fiat.empty:
        fiat['Date'] = fiat['Datum'].apply(parse_excel_date)
        daily_fiat_usdc = fiat.groupby('Date')['USDC'].sum()
    else:
        daily_fiat_usdc = pd.Series(dtype=float)

    crypto = crypto_df.copy()
    if not crypto.empty:
        crypto['Date'] = crypto['Datum'].apply(parse_excel_date)
        daily_crypto_spent = crypto[crypto['Ticker'].str.upper() != 'USDC'].groupby('Date')['USDC'].sum()
    else:
        daily_crypto_spent = pd.Series(dtype=float)

    all_dates = sorted(set(daily_fiat_usdc.index) | set(crypto['Date'].dropna() if not crypto.empty else []))
    if not all_dates: return [], "", pd.DataFrame()
    
    min_date = min(all_dates)
    today = datetime.now().date()
    if min_date > today: min_date = today
    date_range = pd.date_range(start=min_date, end=today).date

    daily_fiat_usdc = daily_fiat_usdc.reindex(date_range, fill_value=0)
    cum_fiat_usdc = daily_fiat_usdc.cumsum()

    daily_crypto_spent = daily_crypto_spent.reindex(date_range, fill_value=0)
    cum_crypto_spent = daily_crypto_spent.cumsum()

    cum_unused_usdc = cum_fiat_usdc - cum_crypto_spent

    if not crypto.empty:
        crypto_assets = crypto[crypto['Ticker'].str.upper() != 'USDC']
        if not crypto_assets.empty:
            holdings = crypto_assets.groupby(['Date', 'Ticker'])['Amount'].sum().unstack(fill_value=0)
            holdings = holdings.reindex(date_range, fill_value=0).fillna(0)
            cum_holdings = holdings.cumsum()
            coins = crypto_assets['Ticker'].unique()
        else:
            cum_holdings = pd.DataFrame(index=date_range)
            coins = []
    else:
        cum_holdings = pd.DataFrame(index=date_range)
        coins = []

    prices_dict = {}
    fetch_coins = set(coins) | {'BTC'}
    
    headers = {"User-Agent": "Mozilla/5.0 (compatible; StreamlitPortfolio/1.0)"}
    for coin in fetch_coins:
        sym = CRYPTOCOMPARE_SYMBOL_MAP.get(coin.upper(), coin.upper())
        days_diff = (today - min_date).days
        limit = min(2000, days_diff + 5)
        url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit={limit}"
        
        data = get_with_retry(url, headers)
        if data and 'Data' in data and 'Data' in data['Data']:
            prices_dict[coin] = {datetime.fromtimestamp(d['time']).date(): d['close'] for d in data['Data']['Data']}
            
    prices_df = pd.DataFrame(prices_dict)
    if not prices_df.empty:
        prices_df = prices_df.reindex(date_range).ffill().bfill().fillna(0)
    else:
        prices_df = pd.DataFrame(index=date_range)
        
    for coin in fetch_coins:
        live_p = last_prices.get(coin, 0.0)
        if live_p == 0.0 and coin == 'BTC':
            live_p = 65000.0 
            
        if coin not in prices_df.columns:
            prices_df[coin] = live_p
        
        # Inject precise live price directly into the end of history for precise 1D PnL calculation
        prices_df.loc[date_range[-1], coin] = live_p
    
    # Calculate PnL Tracking Dataframe
    pnl_df = pd.DataFrame()
    if not crypto.empty and not crypto_assets.empty:
        invested_daily = crypto_assets.groupby(['Date', 'Ticker'])['USDC'].sum().unstack(fill_value=0)
        invested_daily = invested_daily.reindex(date_range, fill_value=0).fillna(0)
        cum_invested = invested_daily.cumsum()
        
        common_cols = cum_holdings.columns.intersection(prices_df.columns)
        pnl_df = (cum_holdings[common_cols] * prices_df[common_cols]) - cum_invested[common_cols]

    daily_crypto_value = pd.Series(0.0, index=date_range)
    if not common_cols.empty:
        daily_crypto_value = (cum_holdings[common_cols] * prices_df[common_cols]).sum(axis=1)

    total_portfolio_value = daily_crypto_value + cum_unused_usdc

    if 'BTC' in prices_df.columns:
        btc_prices = prices_df['BTC']
        btc_bought = daily_fiat_usdc / btc_prices.replace(0, 1) 
        cum_btc_benchmark_holdings = btc_bought.cumsum()
        btc_benchmark_value = cum_btc_benchmark_holdings * btc_prices
    else:
        btc_benchmark_value = pd.Series(0.0, index=date_range)

    history_data = []
    for d in date_range:
        dt = datetime.combine(d, datetime.min.time())
        ts = int(dt.timestamp()) * 1000
        val = float(total_portfolio_value.loc[d])
        inv = float(cum_fiat_usdc.loc[d])
        btc_val = float(btc_benchmark_value.loc[d])
        history_data.append({'time': ts, 'value': val, 'invested': inv, 'btc': btc_val})
        
    allocation_series_js_list = []
    if not common_cols.empty:
        last_date = date_range[-1]
        coin_values_last_day = {c: (cum_holdings[c].loc[last_date] * prices_df[c].loc[last_date]) for c in common_cols}
        sorted_coins = sorted(coin_values_last_day.keys(), key=lambda c: coin_values_last_day[c], reverse=True)
        
        for coin in sorted_coins:
            coin_val_series = cum_holdings[coin] * prices_df[coin]
            data_points = []
            for d in date_range:
                dt = datetime.combine(d, datetime.min.time())
                ts = int(dt.timestamp()) * 1000
                val = float(coin_val_series.loc[d])
                data_points.append(f"[{ts}, {val}]")
            color = get_ticker_color(coin)
            allocation_series_js_list.append(f"{{ name: '{coin}', data: [{','.join(data_points)}], color: '{color}', marker: {{ enabled: false }} }}")

    allocation_series_js = ",\n".join(allocation_series_js_list)
        
    return history_data, allocation_series_js, pnl_df

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
        'SOL': '#9b59b6', 'HBAR': '#ffffff', 'XRP': '#ffffff', 
        'SUI': '#60a5fa', 'LINK': '#1e3a8a', 'BNB': '#f4c430',
        'TRX': '#ff2d55'
    }
    if ticker in known:
        return known[ticker]
    
    # Fallback dynamic color
    c = f"#{hashlib.md5(ticker.encode()).hexdigest()[:6]}"
    if c == '#000000': 
        return '#ffffff'
    return c

def get_chart_color(ticker: str) -> str:
    color_map = {
        'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9b59b6',
        'HBAR': '#00b4d8', 'XRP': '#1e3a8a', 'BNB': '#f4c430',
        'TRX': '#ff2d55', 'LINK': '#2ecc71', 'SUI': '#60a5fa',
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

def format_price(val):
    try:
        val = float(val)
        if pd.isna(val): return ""
        if abs(val) < 1:
            return f"{val:.4f}"
        else:
            return f"{val:,.2f}"
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
    
    fetch_tickers = list(set(coin_tickers) | {'BTC'})
    
    live_prices = get_all_cryptocompare_prices(fetch_tickers, st.session_state.refresh_key)
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

# ====================== SIDEBAR ======================
with st.sidebar:
    nav_items = [
        ("🏠 Overview", "Home"),
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

with main_container.container(key=f"page_{st.session_state.page}_{st.session_state.ui_version}"):
    if st.session_state.page == "Home":

        df_port, total_value, total_pnl, total_pnl_pct = calculate_portfolio(st.session_state.crypto_df)
        
        usdc_row = df_port[df_port['Ticker'] == 'USDC'].iloc[0] if not df_port[df_port['Ticker'] == 'USDC'].empty else None
        usdc_holdings = usdc_row['Holdings'] if usdc_row is not None else 0

        # ================== 1. DASHBOARD OVERVIEW ==================
        value_box_html = f"""
<input type="checkbox" id="dash-toggle" class="dashboard-toggle" style="display:none;">
<div class="dashboard-wrapper">
<label for="dash-toggle" class="glossy-header-label">
<div class="glossy-header home-header">
{DASHBOARD_ICON}<span style="margin-left:12px;">Overview</span>
<div class="pull-indicator">
{EYE_CLOSED}
{EYE_OPEN}
</div>
</div>
</label>
<div class="stats-layer">
<div class="stats-layer-inner">
<div class="glossy-box swapped"><div class="dash-value"><span id="dash-total-value">{format_money(total_value)}</span></div><div class="dash-label">Total Value</div></div>
<div class="glossy-box swapped"><div class="dash-value"><span id="dash-pnl" style="color:{'#00ff9d' if total_pnl>=0 else '#ff4d4d'}">{"▲" if total_pnl>0 else "▼" if total_pnl<0 else ""} {format_money(abs(total_pnl))}</span></div><div class="dash-label">PnL</div></div>
<div class="glossy-box swapped"><div class="dash-value"><span id="dash-pnl-pct" style="color:{'#00ff9d' if total_pnl_pct>=0 else '#ff4d4d'}">{"▲" if total_pnl_pct>0 else "▼" if total_pnl_pct<0 else ""} {abs(total_pnl_pct):.2f}%</span></div><div class="dash-label">PnL %</div></div>
</div>
</div>
</div>
"""
        st.markdown(value_box_html, unsafe_allow_html=True)

        # ================== 2. ASSEMBLE ALL CHARTS DATA ==================
        last_prices_dict = st.session_state.last_known_prices.copy()
        history_data_raw, allocation_series_js, pnl_df = build_portfolio_history(st.session_state.crypto_df, st.session_state.fiat_df, last_prices_dict, st.session_state.refresh_key)
        
        hist_val_js_list = []
        hist_inv_js_list = []
        hist_btc_js_list = []
        
        if history_data_raw:
            today_ts = int(datetime.combine(datetime.now().date(), datetime.min.time()).timestamp()) * 1000
            fiat_usdc_total = pd.to_numeric(st.session_state.fiat_df['USDC'], errors='coerce').fillna(0).sum()
            
            for idx, d in enumerate(history_data_raw):
                ts = d['time']
                val = d['value']
                inv = d['invested']
                btc = d['btc']
                
                if idx == len(history_data_raw) - 1 and ts == today_ts:
                    val = float(total_value)
                    inv = float(fiat_usdc_total)
                
                hist_val_js_list.append(f"[{ts}, {val}]")
                hist_inv_js_list.append(f"[{ts}, {inv}]")
                hist_btc_js_list.append(f"[{ts}, {btc}]")
                
            hist_val_js = ",\n".join(hist_val_js_list)
            hist_inv_js = ",\n".join(hist_inv_js_list)
            hist_btc_js = ",\n".join(hist_btc_js_list)
        else:
            hist_val_js, hist_inv_js, hist_btc_js = "", "", ""

        # Chart 1: Pie Data
        pie_data_js_lines = []
        for _, r in df_port.iterrows():
            ticker = r['Ticker']
            if ticker == 'USDC':
                continue
            val = r['Value']
            if pd.notna(val) and val > 0:
                chart_color = get_ticker_color(ticker)
                pie_data_js_lines.append(f"{{ name: '{ticker}', y: {val}, color: '{chart_color}' }}")
        pie_data_js = ",\n".join(pie_data_js_lines)

        # Chart 3: PnL Bar Data with Timeframes & Live Baselines
        pnl_data_js_dict = {'all': '[]', '1y': '[]', '30d': '[]', '7d': '[]', '1d': '[]'}
        baselines_dict = {'1d': {}, '7d': {}, '30d': {}, '1y': {}}
        
        if not pnl_df.empty:
            active_tickers = [t for t in df_port['Ticker'] if t != 'USDC']
            valid_cols = [c for c in active_tickers if c in pnl_df.columns]
            pnl_df_active = pnl_df[valid_cols] if valid_cols else pnl_df

            def format_pnl_js(series):
                series = series.dropna().sort_values(ascending=True)
                lines = []
                for ticker, val in series.items():
                    c = get_ticker_color(ticker)
                    lines.append(f"{{ name: '{ticker}', y: {val}, color: '{c}' }}")
                if not lines:
                    return "[]"
                return "[\n" + ",\n".join(lines) + "\n]"

            pnl_all = pnl_df_active.iloc[-1]
            
            idx_1d = -2 if len(pnl_df_active) >= 2 else 0
            idx_7d = -8 if len(pnl_df_active) >= 8 else 0
            idx_30d = -31 if len(pnl_df_active) >= 31 else 0
            idx_1y = -365 if len(pnl_df_active) >= 365 else 0

            pnl_1d = pnl_all - pnl_df_active.iloc[idx_1d]
            pnl_7d = pnl_all - pnl_df_active.iloc[idx_7d]
            pnl_30d = pnl_all - pnl_df_active.iloc[idx_30d]
            pnl_1y = pnl_all - pnl_df_active.iloc[idx_1y]

            pnl_data_js_dict['all'] = format_pnl_js(pnl_all)
            pnl_data_js_dict['1d'] = format_pnl_js(pnl_1d)
            pnl_data_js_dict['7d'] = format_pnl_js(pnl_7d)
            pnl_data_js_dict['30d'] = format_pnl_js(pnl_30d)
            pnl_data_js_dict['1y'] = format_pnl_js(pnl_1y)
            
            for t in valid_cols:
                baselines_dict['1d'][t] = float(pnl_df_active[t].iloc[idx_1d]) if len(pnl_df_active) > idx_1d else 0.0
                baselines_dict['7d'][t] = float(pnl_df_active[t].iloc[idx_7d]) if len(pnl_df_active) > idx_7d else 0.0
                baselines_dict['30d'][t] = float(pnl_df_active[t].iloc[idx_30d]) if len(pnl_df_active) > idx_30d else 0.0
                baselines_dict['1y'][t] = float(pnl_df_active[t].iloc[idx_1y]) if len(pnl_df_active) > idx_1y else 0.0
                
        baselines_js_str = json.dumps(baselines_dict)

        # Chart 5: Invested vs Current Value Data
        df_iv = df_port[df_port['Ticker'] != 'USDC'].sort_values(by='Value', ascending=False)
        inv_val_categories_list = [str(r['Ticker']) for _, r in df_iv.iterrows()]
        inv_val_categories_js = json.dumps(inv_val_categories_list)
        
        inv_data_points = []
        val_data_points = []
        coin_stats_dict = {}
        for _, r in df_iv.iterrows():
            ticker = str(r['Ticker'])
            inv = r['USDC'] if pd.notna(r['USDC']) else 0
            val = r['Value'] if pd.notna(r['Value']) else 0
            holdings = r['Holdings'] if pd.notna(r['Holdings']) else 0
            c = get_ticker_color(ticker)
            inv_data_points.append(f"{{ name: '{ticker}', y: {inv} }}")
            val_data_points.append(f"{{ name: '{ticker}', y: {val}, color: '{c}' }}")
            coin_stats_dict[ticker] = {'holdings': float(holdings), 'invested': float(inv)}
        
        inv_data_js = ",".join(inv_data_points)
        val_data_js = ",".join(val_data_points)
        coin_stats_js = json.dumps(coin_stats_dict)

        charts_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://code.highcharts.com/stock/highstock.js"></script>
            <script src="https://code.highcharts.com/stock/highcharts-3d.js"></script>
            <style>
                body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: system-ui, sans-serif; }}
                
                .charts-scroll-wrapper {{
                    width: 100%;
                    overflow-y: hidden;
                    overflow-x: auto;
                    padding: 6px 0px 6px 0px; 
                    margin-bottom: 0px; 
                    scroll-snap-type: x mandatory;
                    -webkit-overflow-scrolling: touch;
                    scrollbar-width: none; 
                    -ms-overflow-style: none; 
                }}
                .charts-scroll-wrapper::-webkit-scrollbar {{
                    display: none; 
                }}
                .charts-flex {{
                    display: flex;
                    flex-direction: row;
                    flex-wrap: nowrap;
                    gap: 24px;
                    width: max-content;
                    padding: 0 24px;
                }}
                
                .chart-placeholder {{ scroll-snap-align: center; }}
                
                .chart-placeholder[data-type="pie"] {{ width: 350px; flex: 0 0 350px; height: 340px; }}
                .chart-placeholder[data-type="history"] {{ width: 600px; flex: 0 0 600px; height: 340px; }}
                .chart-placeholder[data-type="pnl"] {{ width: 400px; flex: 0 0 400px; height: 340px; }}
                .chart-placeholder[data-type="allocation"] {{ width: 600px; flex: 0 0 600px; height: 340px; }}
                .chart-placeholder[data-type="inv-val"] {{ width: 500px; flex: 0 0 500px; height: 340px; }}
                
                .chart-box {{
                    width: 100%;
                    height: 100%;
                    background: rgba(15, 23, 42, 0.4);
                    border: 1px solid rgba(255,255,255,0.05);
                    border-radius: 16px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    touch-action: pan-x pan-y; 
                    will-change: transform; 
                    position: relative;
                    display: flex;
                    flex-direction: column;
                }}
                
                /* Responsive Custom Headers for Charts */
                .chart-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px 16px 0 16px;
                    width: 100%;
                    box-sizing: border-box;
                }}
                .chart-title {{
                    color: #e2e8f0;
                    font-size: 13px;
                    font-weight: bold;
                    white-space: nowrap;
                }}
                .chart-controls {{
                    display: flex;
                    gap: 4px;
                }}
                .chart-controls button {{
                    background: rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.1);
                    color: #94a3b8;
                    border-radius: 4px;
                    padding: 3px 8px;
                    font-size: 10px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: all 0.2s;
                }}
                .chart-controls button.active {{
                    background: rgba(0, 255, 157, 0.15);
                    color: #00ff9d;
                    border-color: #00ff9d;
                }}
                .chart-body {{
                    flex: 1;
                    width: 100%;
                    position: relative;
                }}

                /* Smooth Fade Overlay */
                #chart-overlay {{
                    visibility: hidden;
                    opacity: 0;
                    position: fixed;
                    top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(10, 15, 28, 0.85); 
                    z-index: 1000;
                    backdrop-filter: blur(5px);
                    -webkit-backdrop-filter: blur(5px);
                    transition: opacity 0.4s ease, visibility 0.4s ease;
                }}
                #chart-overlay.active {{
                    visibility: visible;
                    opacity: 1;
                }}
                
                /* Expanded state strictly overrides visuals */
                .expanded-chart {{
                    background: rgba(15, 23, 42, 0.98) !important; 
                    border: 1px solid rgba(255, 255, 255, 0.08) !important; 
                    box-shadow: 0 15px 50px rgba(0,0,0,0.9) !important;
                    border-radius: 20px !important; 
                }}

                @media (max-width: 768px) {{
                    .chart-placeholder {{ 
                        height: 320px !important; 
                        width: 90vw !important; 
                        flex: 0 0 90vw !important; 
                    }}
                    
                    .charts-flex {{ 
                        padding: 0 5vw; 
                        gap: 16px; 
                    }}
                    
                    /* Shrink buttons slightly on very small phones to prevent overlap */
                    .chart-controls button {{
                        padding: 3px 6px;
                        font-size: 9px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div id="chart-overlay"></div>
            
            <div class="charts-scroll-wrapper" id="chartsScrollContainer">
                <div class="charts-flex">
                    <div class="chart-placeholder" data-type="pie">
                        <div id="pie-container" class="chart-box"></div>
                    </div>
                    
                    <div class="chart-placeholder" data-type="history">
                        <div id="history-wrapper" class="chart-box">
                            <div class="chart-header">
                                <div class="chart-title">Performance</div>
                                <div class="chart-controls hist-controls">
                                    <button class="active" data-range="all">All</button>
                                    <button data-range="1w">1W</button>
                                    <button data-range="1m">1M</button>
                                    <button data-range="1y">1Y</button>
                                    <button data-range="ytd">YTD</button>
                                </div>
                            </div>
                            <div id="history-container" class="chart-body"></div>
                        </div>
                    </div>
                    
                    <div class="chart-placeholder" data-type="pnl">
                        <div id="pnl-wrapper" class="chart-box">
                            <div class="chart-header">
                                <div class="chart-title">Winners & Losers</div>
                                <div class="chart-controls pnl-controls">
                                    <button class="active" data-range="all">All</button>
                                    <button data-range="1d">Today</button>
                                    <button data-range="7d">1W</button>
                                    <button data-range="30d">1M</button>
                                    <button data-range="1y">1Y</button>
                                </div>
                            </div>
                            <div id="pnl-container" class="chart-body"></div>
                        </div>
                    </div>
                    
                    <div class="chart-placeholder" data-type="allocation">
                        <div id="allocation-container" class="chart-box"></div>
                    </div>
                    
                    <div class="chart-placeholder" data-type="inv-val">
                        <div id="inv-val-container" class="chart-box"></div>
                    </div>
                </div>
            </div>
            
            <script>
                Highcharts.setOptions({{ global: {{ useUTC: false }} }});
                
                const baselines = {baselines_js_str};
                const coinStats = {coin_stats_js};
                const usdcHoldings = {usdc_holdings};

                // Chart 1: Pie
                Highcharts.chart('pie-container', {{
                    chart: {{ type: 'pie', options3d: {{ enabled: true, alpha: 55, beta: 0 }}, backgroundColor: 'transparent', margin: [0, 0, 0, 0] }},
                    title: {{ text: 'Current Holdings', style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }}, align: 'left', x: 16, y: 24 }},
                    tooltip: {{
                        formatter: function() {{
                            const isPrivacy = document.body.classList.contains('privacy-mode');
                            if (isPrivacy) return '<b>' + this.point.name + '</b><br/>' + this.point.percentage.toFixed(1) + '%';
                            return '<b>' + this.point.name + '</b><br/>$' + Highcharts.numberFormat(this.point.y, 2) + '<br/>' + this.point.percentage.toFixed(1) + '%';
                        }},
                        backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)'
                    }},
                    plotOptions: {{ pie: {{ allowPointSelect: true, cursor: 'pointer', depth: 40, innerSize: '40%', size: '65%', dataLabels: {{ enabled: true, format: '<b>{{point.name}}</b><br>{{point.percentage:.1f}}%', style: {{ color: '#e2e8f0', textOutline: 'none', fontSize: '10px', fontWeight: '600' }}, connectorColor: 'rgba(255,255,255,0.2)', distance: 10, padding: 0 }}, borderWidth: 0 }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'Holdings', data: [{pie_data_js}] }}]
                }});

                // Chart 2: History Area (Using Highstock)
                Highcharts.stockChart('history-container', {{
                    chart: {{ type: 'areaspline', backgroundColor: 'transparent', marginLeft: 45, marginRight: 15, marginTop: 25, marginBottom: 35 }}, 
                    rangeSelector: {{ enabled: false }}, // Hidden native range selector in favor of our custom header HTML
                    navigator: {{ enabled: false }},
                    scrollbar: {{ enabled: false }},
                    title: {{ text: null }},
                    legend: {{ enabled: true, itemStyle: {{ color: '#94a3b8', fontSize: '11px', fontWeight: 'normal' }}, itemHoverStyle: {{ color: '#ffffff' }}, verticalAlign: 'top', align: 'center', y: -10 }},
                    xAxis: {{ gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, minorGridLineWidth: 0 }},
                    yAxis: {{ opposite: false, title: {{ text: null }}, labels: {{ align: 'right', x: -4, style: {{ color: '#94a3b8', fontSize: '10px', textOverflow: 'none', whiteSpace: 'nowrap' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : '$' + this.axis.defaultLabelFormatter.call(this); }} }}, gridLineColor: 'rgba(255,255,255,0.05)' }},
                    tooltip: {{
                        shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)',
                        formatter: function() {{
                            let s = '<b style="font-size: 11px; color:#cbd5e1;">' + Highcharts.dateFormat('%b %e, %Y', this.x) + '</b>';
                            const isPrivacy = document.body.classList.contains('privacy-mode');
                            this.points.forEach(function(point) {{
                                let val = isPrivacy ? '***' : '$' + Highcharts.numberFormat(point.y, 2);
                                s += '<br/>' + '<span style="color:'+point.series.color+'">\u25CF</span> ' + point.series.name + ': <b style="font-size: 13px;">' + val + '</b>';
                            }});
                            return s;
                        }}
                    }},
                    plotOptions: {{ areaspline: {{ fillOpacity: 0.3, lineWidth: 2 }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'Portfolio Value', data: [{hist_val_js}], color: '#00ff9d', fillColor: {{ linearGradient: {{ x1: 0, y1: 0, x2: 0, y2: 1 }}, stops: [ [0, 'rgba(0, 255, 157, 0.5)'], [1, 'rgba(0, 255, 157, 0.0)'] ] }}, zIndex: 3 }}, 
                             {{ name: 'BTC Benchmark', type: 'line', data: [{hist_btc_js}], color: '#f7931a', lineWidth: 2, zIndex: 2 }}, 
                             {{ name: 'Net Invested', type: 'line', data: [{hist_inv_js}], color: '#64748b', dashStyle: 'Dash', lineWidth: 2, zIndex: 1 }}]
                }});
                
                // Custom Range Logic for History Chart
                document.querySelectorAll('.hist-controls button').forEach(btn => {{
                    btn.addEventListener('click', (e) => {{
                        e.stopPropagation();
                        document.querySelectorAll('.hist-controls button').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        const range = btn.getAttribute('data-range');
                        const chart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'history-container');
                        if (chart) {{
                            const max = chart.xAxis[0].dataMax;
                            const min = chart.xAxis[0].dataMin;
                            const day = 24 * 3600 * 1000;
                            let newMin = min;
                            if (range === 'all') {{
                                chart.xAxis[0].setExtremes(null, null);
                            }} else {{
                                if (range === '1w') newMin = max - 7 * day;
                                else if (range === '1m') newMin = max - 30 * day;
                                else if (range === '1y') newMin = max - 365 * day;
                                else if (range === 'ytd') {{
                                    const d = new Date(max);
                                    newMin = new Date(d.getFullYear(), 0, 1).getTime();
                                }}
                                chart.xAxis[0].setExtremes(Math.max(min, newMin), max);
                            }}
                        }}
                    }});
                }});

                // Chart 3: Winners & Losers (PnL Bar)
                const pnlDataMap = {{
                    'all': {pnl_data_js_dict['all']},
                    '1y': {pnl_data_js_dict['1y']},
                    '30d': {pnl_data_js_dict['30d']},
                    '7d': {pnl_data_js_dict['7d']},
                    '1d': {pnl_data_js_dict['1d']}
                }};
                
                // Helper to cleanly deep-clone our data objects before handing them to Highcharts
                function getPnlDataCopy(range) {{
                    return pnlDataMap[range].map(item => ({{...item}})).sort((a, b) => a.y - b.y);
                }}

                Highcharts.chart('pnl-container', {{
                    chart: {{ type: 'bar', backgroundColor: 'transparent', marginLeft: 55, marginRight: 45, marginTop: 15, marginBottom: 25 }},
                    title: {{ text: null }},
                    xAxis: {{ type: 'category', labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, lineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ enabled: false }}, gridLineColor: 'rgba(255,255,255,0.05)' }},
                    legend: {{ enabled: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)',
                        formatter: function() {{
                            const isPrivacy = document.body.classList.contains('privacy-mode');
                            const val = isPrivacy ? '***' : '$' + Highcharts.numberFormat(this.y, 2);
                            return `<b>${{this.point.name}}</b><br/>PnL: <b style="color:${{this.point.color}}">${{val}}</b>`;
                        }}
                    }},
                    plotOptions: {{ bar: {{ borderRadius: 3, borderWidth: 0, pointPadding: 0.1, groupPadding: 0.1, dataLabels: {{ enabled: true, inside: false, crop: false, overflow: 'none', style: {{ color: '#fff', textOutline: '3px #0f172a', fontWeight: 'bold', fontSize: '10px' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : (this.y < 0 ? '-$' : '$') + Highcharts.numberFormat(Math.abs(this.y), 2); }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'PnL', data: getPnlDataCopy('all') }}]
                }});

                document.querySelectorAll('.pnl-controls button').forEach(btn => {{
                    btn.addEventListener('click', (e) => {{
                        e.stopPropagation(); 
                        document.querySelectorAll('.pnl-controls button').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        const range = btn.getAttribute('data-range');
                        const chart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'pnl-container');
                        if (chart) {{
                            chart.series[0].setData(getPnlDataCopy(range), true, {{ duration: 500 }}, false);
                        }}
                    }});
                }});

                // Chart 4: Portfolio Allocation (Stacked Area)
                Highcharts.chart('allocation-container', {{
                    chart: {{ type: 'area', backgroundColor: 'transparent', marginLeft: 45, marginRight: 15, marginTop: 45, marginBottom: 35 }},
                    title: {{ text: 'Asset Allocation', align: 'left', x: 8, y: 24, style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }} }},
                    xAxis: {{ type: 'datetime', labels: {{ style: {{ color: '#94a3b8', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, minorGridLineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ align: 'right', x: -4, formatter: function() {{ return this.value + '%'; }}, style: {{ color: '#94a3b8', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', max: 100 }},
                    legend: {{ enabled: false }},
                    tooltip: {{
                        shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)',
                        formatter: function() {{
                            let s = '<b style="font-size: 11px; color:#cbd5e1;">' + Highcharts.dateFormat('%b %e, %Y', this.x) + '</b>';
                            this.points.forEach(function(point) {{
                                s += '<br/>' + '<span style="color:'+point.series.color+'">\u25CF</span> ' + point.series.name + ': <b>' + Highcharts.numberFormat(point.percentage, 1) + '%</b>';
                            }});
                            return s;
                        }}
                    }},
                    plotOptions: {{ area: {{ stacking: 'percent', lineWidth: 1, marker: {{ enabled: false, symbol: 'circle', radius: 2, states: {{ hover: {{ enabled: true }} }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{allocation_series_js}]
                }});

                // Chart 5: Invested vs Current Value (Grouped Column)
                Highcharts.chart('inv-val-container', {{
                    chart: {{ type: 'column', backgroundColor: 'transparent', marginLeft: 45, marginRight: 15, marginTop: 45, marginBottom: 35 }},
                    title: {{ text: 'Invested vs Current Value', align: 'left', x: 8, y: 24, style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }} }},
                    xAxis: {{ categories: {inv_val_categories_js}, labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ align: 'right', x: -4, style: {{ color: '#94a3b8', fontSize: '10px', textOverflow: 'none', whiteSpace: 'nowrap' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : '$' + this.axis.defaultLabelFormatter.call(this); }} }}, gridLineColor: 'rgba(255,255,255,0.05)' }},
                    legend: {{ enabled: false }},
                    tooltip: {{
                        shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)',
                        formatter: function() {{
                            let s = '<b style="font-size: 13px;">' + (this.points[0].point.name || this.points[0].key || this.x) + '</b>';
                            const isPrivacy = document.body.classList.contains('privacy-mode');
                            this.points.forEach(function(point) {{
                                let val = isPrivacy ? '***' : '$' + Highcharts.numberFormat(point.y, 2);
                                s += '<br/>' + '<span style="color:'+point.series.color+'">\u25CF</span> ' + point.series.name + ': <b>' + val + '</b>';
                            }});
                            return s;
                        }}
                    }},
                    plotOptions: {{ column: {{ borderRadius: 3, borderWidth: 0 }} }},
                    credits: {{ enabled: false }},
                    series: [
                        {{ name: 'Invested', data: [{inv_data_js}], color: '#64748b' }},
                        {{ name: 'Current Value', data: [{val_data_js}] }}
                    ]
                }});

                try {{
                    if (window !== window.parent && window.parent.document) {{
                        if (!window.parent.document.getElementById('chart-fullscreen-css')) {{
                            const style = window.parent.document.createElement('style');
                            style.id = 'chart-fullscreen-css';
                            style.innerHTML = `
                                iframe.fullscreen-mode {{
                                    position: fixed !important;
                                    top: 0 !important;
                                    left: 0 !important;
                                    width: 100vw !important;
                                    height: 100vh !important;
                                    max-width: 100vw !important;
                                    max-height: 100vh !important;
                                    z-index: 999999 !important;
                                    border: none !important;
                                    background: transparent !important;
                                }}
                            `;
                            window.parent.document.head.appendChild(style);
                        }}
                    }}
                }} catch(e) {{}}

                function toggleExpandChart(wrapperId) {{
                    // BLOCK PC COMPLETELY - Only runs on Mobile
                    if (window.innerWidth > 768) return;
                
                    const el = document.getElementById(wrapperId);
                    const overlay = document.getElementById('chart-overlay');
                    const wrapper = document.getElementById('chartsScrollContainer');

                    let parentIframe = null;
                    try {{
                        const iframes = window.parent.document.querySelectorAll('iframe');
                        for (let ifr of iframes) {{ if (ifr.contentWindow === window) parentIframe = ifr; }}
                    }} catch(e) {{}}
                    
                    const screenW = window.parent ? window.parent.innerWidth : window.innerWidth;
                    const screenH = window.parent ? window.parent.innerHeight : window.innerHeight;

                    if (el.classList.contains('expanded-chart')) {{
                        // ==========================================
                        // CLOSING MECHANICS (Seamless settle Fix)
                        // ==========================================
                        overlay.classList.remove('active');
                        
                        // Re-calculate the current layout position to avoid scroll-shift blinks
                        const placeholder = el.parentElement;
                        const targetRect = placeholder.getBoundingClientRect();
                        let targetTop = targetRect.top;
                        let targetLeft = targetRect.left;
                        if (parentIframe) {{
                            const iframeRect = parentIframe.getBoundingClientRect();
                            targetTop += iframeRect.top;
                            targetLeft += iframeRect.left;
                        }}

                        // Phase 1: Keep it position: fixed, but set its standard visual coordinates. 
                        // Crossfade the class instantly to lose expanded background while traveling.
                        el.classList.remove('expanded-chart');
                        el.style.transition = 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.4s ease, box-shadow 0.4s ease';
                        el.style.transform = `translate(${{targetLeft}}px, ${{targetTop}}px) scale(1)`;

                        // Phase 2: Once the visual transition finishes, silently revert CSS layout from fixed to standard flow
                        const finishClose = (e) => {{
                            if (e && e.propertyName !== 'transform') return;
                            el.removeEventListener('transitionend', finishClose);
                            clearTimeout(el._closeTimeout);
                            if (parentIframe) parentIframe.classList.remove('fullscreen-mode');
                            
                            el.style.transition = 'none';
                            el.style.cssText = ''; // Full layout revert
                            
                            // Prevent layout thrashing: Highcharts Redraw SILENTLY to correct slot dimensions
                            Highcharts.charts.forEach(c => {{ 
                                if(c && c.renderTo && el.contains(c.renderTo)) {{
                                    c.setSize(null, null, false);
                                }}
                            }});
                            
                            // Reveal siblings smoothly
                            document.querySelectorAll('.chart-box').forEach(c => {{
                                c.style.opacity = '1';
                                c.style.pointerEvents = 'auto';
                            }});
                        }};
                        el.addEventListener('transitionend', finishClose);
                        el._closeTimeout = setTimeout(() => {{ finishClose(); }}, 450); // Fallback

                        return;
                    }}
                    
                    // ==========================================
                    // OPENING MECHANICS (Retained seamless flow)
                    // ==========================================
                    
                    // 1. SILENT VANISH: instantly hide siblings to prevent bleeding
                    document.querySelectorAll('.chart-box').forEach(c => {{
                        if (c.id !== wrapperId) {{
                            c.style.transition = 'opacity 0.15s ease';
                            c.style.opacity = '0';
                            c.style.pointerEvents = 'none';
                        }}
                    }});

                    const chartRect = el.getBoundingClientRect();
                    let visualTop = chartRect.top;
                    let visualLeft = chartRect.left;
                    if (parentIframe) {{
                        const iframeRect = parentIframe.getBoundingClientRect();
                        visualTop += iframeRect.top;
                        visualLeft += iframeRect.left;
                    }}

                    if (parentIframe) parentIframe.classList.add('fullscreen-mode');
                    overlay.classList.add('active'); 
                    
                    const origW = chartRect.width;
                    const origH = chartRect.height;
                    
                    let targetW = screenW * 0.95;
                    let targetH = screenH * 0.70;
                    
                    // Calculate perfectly uniform maximum scale
                    const maxScaleX = targetW / origW;
                    const maxScaleY = targetH / origH;
                    const targetScale = Math.min(maxScaleX, maxScaleY);
                    
                    const scaledW = origW * targetScale;
                    const scaledH = origH * targetScale;
                    const centerLeft = (screenW - scaledW) / 2;
                    const centerTop = (screenH - scaledH) / 2;

                    // Save origins
                    el.setAttribute('data-orig-top', visualTop);
                    el.setAttribute('data-orig-left', visualLeft);

                    // Phase 1: Lock the chart in its starting spot natively small, no HC Redraw
                    el.style.position = 'fixed';
                    el.style.top = '0px';
                    el.style.left = '0px';
                    el.style.width = origW + 'px';
                    el.style.height = origH + 'px';
                    el.style.margin = '0';
                    el.style.zIndex = '1001';
                    el.style.transformOrigin = 'top left'; 
                    el.style.transition = 'none';
                    el.style.transform = `translate(${{visualLeft}}px, ${{visualTop}}px) scale(1)`;
                    
                    void el.offsetWidth; // Force CSS Engine Reflow

                    // Phase 2: Travel to center while scaling using native browser hardware acceleration
                    el.classList.add('expanded-chart');
                    el.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.4s ease, box-shadow 0.4s ease';
                    el.style.transform = `translate(${{centerLeft}}px, ${{centerTop}}px) scale(${{targetScale}})`;
                }}

                function setupDoubleTap(elementId) {{
                    const el = document.getElementById(elementId);
                    if (!el) return;
                    let lastTap = 0;

                    el.addEventListener('touchend', function(e) {{
                        const currentTime = new Date().getTime();
                        const tapLength = currentTime - lastTap;
                        if (tapLength < 400 && tapLength > 0) {{
                            toggleExpandChart(elementId);
                            e.preventDefault(); 
                            e.stopPropagation();
                        }}
                        lastTap = currentTime;
                    }});
                }}

                setupDoubleTap('pie-container');
                setupDoubleTap('history-wrapper');
                setupDoubleTap('pnl-wrapper');
                setupDoubleTap('allocation-container');
                setupDoubleTap('inv-val-container');

                document.getElementById('chart-overlay').addEventListener('click', () => {{
                    document.querySelectorAll('.expanded-chart').forEach(el => {{
                        if (el.classList.contains('expanded-chart')) {{
                            toggleExpandChart(el.id);
                        }}
                    }});
                }});

                const chartScroll = document.getElementById('chartsScrollContainer');
                if (chartScroll) {{
                    chartScroll.addEventListener('wheel', (evt) => {{
                        if (Math.abs(evt.deltaY) > Math.abs(evt.deltaX)) {{
                            evt.preventDefault();
                            chartScroll.scrollBy({{ left: evt.deltaY > 0 ? 200 : -200, behavior: 'smooth' }});
                        }}
                    }}, {{ passive: false }});
                }}

                // ---- LIVE UPDATE SCRIPT INJECTION ----
                async function updateLivePricesCharts() {{
                    const tickers = Object.keys(coinStats);
                    if (tickers.length === 0) return;
                    const url = `https://min-api.cryptocompare.com/data/pricemulti?fsyms=${{tickers.join(',')}}&tsyms=USD`;
                    try {{
                        const resp = await fetch(url);
                        const data = await resp.json();
                        
                        let totalCoinValue = 0;
                        let totalCoinInvested = 0;
                        
                        const pieChart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'pie-container');
                        const invChart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'inv-val-container');
                        const allocChart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'allocation-container');

                        tickers.forEach(ticker => {{
                            if (data[ticker] && data[ticker].USD) {{
                                const price = data[ticker].USD;
                                const stats = coinStats[ticker];
                                const value = stats.holdings * price;
                                const pnl = value - stats.invested;
                                
                                totalCoinValue += value;
                                totalCoinInvested += stats.invested;
                                
                                if (pieChart && pieChart.series[0]) {{
                                    const pt = pieChart.series[0].points.find(p => p.name === ticker);
                                    if (pt) pt.update({{y: value}}, false);
                                }}

                                if (invChart && invChart.series[1]) {{ 
                                    const pt = invChart.series[1].points.find(p => (p.category || p.name) === ticker);
                                    if (pt) pt.update({{y: value}}, false);
                                }}

                                if (allocChart) {{
                                    const series = allocChart.series.find(s => s.name === ticker);
                                    if (series && series.points.length > 0) {{
                                        const lastPt = series.points[series.points.length - 1];
                                        lastPt.update({{y: value}}, false);
                                    }}
                                }}

                                ['all', '1d', '7d', '30d', '1y'].forEach(tf => {{
                                    const mapArray = pnlDataMap[tf];
                                    if (mapArray) {{
                                        const pt = mapArray.find(p => p.name === ticker);
                                        if (pt) {{
                                            if (tf === 'all') {{
                                                pt.y = pnl;
                                            }} else {{
                                                const baseline = baselines[tf][ticker] || 0;
                                                pt.y = pnl - baseline;
                                            }}
                                        }}
                                    }}
                                }});
                            }}
                        }});
                        
                        const totalPortfolioValue = totalCoinValue + usdcHoldings;
                        
                        const histChart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'history-container');
                        if (histChart && histChart.series[0] && histChart.series[0].points.length > 0) {{
                            const pvSeries = histChart.series[0];
                            const lastPt = pvSeries.points[pvSeries.points.length - 1];
                            lastPt.update({{y: totalPortfolioValue}}, false);
                        }}

                        const pnlChart = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === 'pnl-container');
                        if (pnlChart) {{
                            const activeBtn = document.querySelector('.pnl-controls button.active');
                            const range = activeBtn ? activeBtn.getAttribute('data-range') : 'all';
                            const freshData = getPnlDataCopy(range);
                            pnlChart.series[0].setData(freshData, false);
                        }}

                        if (pieChart) pieChart.redraw(true);
                        if (invChart) invChart.redraw(true);
                        if (allocChart) allocChart.redraw(true);
                        if (histChart) histChart.redraw(true);
                        if (pnlChart) pnlChart.redraw(true);
                        
                    }} catch (e) {{
                        console.error('Auto-refresh error charts:', e);
                    }}
                }}
                setInterval(updateLivePricesCharts, 10000);

                setInterval(() => {{
                    try {{
                        const saved = localStorage.getItem('dashboardOpen');
                        const isPrivacy = (saved === 'false');
                        const currentlyPrivacy = document.body.classList.contains('privacy-mode');
                        
                        if (isPrivacy !== currentlyPrivacy) {{
                            if (isPrivacy) {{
                                document.body.classList.add('privacy-mode');
                            }} else {{
                                document.body.classList.remove('privacy-mode');
                            }}
                            ['history-container', 'pnl-container', 'inv-val-container'].forEach(id => {{
                                const hc = Highcharts.charts.find(c => c && c.renderTo && c.renderTo.id === id);
                                if (hc && hc.yAxis && hc.yAxis[0]) {{ hc.yAxis[0].isDirty = true; hc.redraw(); }}
                            }});
                        }}
                    }} catch(e) {{}}
                }}, 200);
            </script>
        </body>
        </html>
        """
        components.html(charts_html, height=355, scrolling=False)

        # ================== 3. SUBDUED USDC BANNER ==================
        usdc_banner_html = f"""
<input type="checkbox" id="dash-toggle-usdc" class="dashboard-toggle" style="display:none;">
<div class="usdc-banner" style="--border: #2775ca;">
<div class="usdc-banner-left">
<img src="{get_ticker_logo('USDC')}" onerror="this.src='https://via.placeholder.com/42/1e2a44/ffffff?text=U';">
<div class="usdc-banner-title">USDC <span class="usdc-banner-subtitle">(Available Cash)</span></div>
</div>
<div class="usdc-banner-amount">{format_holdings(usdc_holdings, 'USDC')}</div>
</div>
"""
        st.markdown(usdc_banner_html, unsafe_allow_html=True)

        # ================== 4. FLIP CARDS ==================
        cards_html = ""
        for _, r in df_port.iterrows():
            ticker = r['Ticker']
            if ticker == 'USDC':
                continue
                
            pnl = r['PnL']
            pnl_color = "#00ff9d" if pnl > 0 else "#ff4d4d" if pnl < 0 else "#aaaaaa"
            arrow = "▲" if pnl > 0 else "▼" if pnl < 0 else ""
            base_color = get_ticker_color(ticker)
            border_color = base_color if base_color != '#000000' else '#ffffff'
            logo_url = get_ticker_logo(ticker)
            pnl_pct_formatted = format_percent(abs(r['PnL %'])) if pd.notna(r['PnL %']) else ""
            live_price = r['Live']
            avg_price = r['AVG']
            live_price_formatted = format_price(live_price)
            avg_price_formatted = format_price(avg_price)
            chart_color = border_color
            
            cards_html += f"""
<div class="flip-card" data-ticker="{ticker}" data-holdings="{r['Holdings']}" data-invested="{r['USDC']}" data-current-price="{live_price}" data-avg-price="{avg_price}" data-refresh="{st.session_state.refresh_key}" data-border="{border_color}" data-chart-color="{chart_color}" data-logo="{logo_url}">
    <div class="flip-card-inner">
        <div class="flip-card-front">
            <div class="card-header">
                <div class="header-left-container">
                    <div class="header-logo-row">
                        <img src="{logo_url}" style="height:44px;width:44px;border-radius:50%;object-fit:contain;" onerror="this.src='https://via.placeholder.com/44/1e2a44/ffffff?text={ticker[0]}';">
                        <span style="font-weight:700;font-size:1.3rem;margin-left:12px;color:#ffffff;">{ticker}</span>
                    </div>
                    <div class="header-price-row">
                        <div class="stat-group" style="align-items: flex-start;">
                            <div class="stat-label">Current</div>
                            <div class="current-value">${live_price_formatted}</div>
                        </div>
                        <div class="stat-group" style="align-items: flex-start;">
                            <div class="stat-label">24h</div>
                            <div class="change-value" id="change-{ticker}">...</div>
                        </div>
                    </div>
                </div>
                <div class="header-right">
                    <div class="stat-group">
                        <div class="stat-label">Avg</div>
                        <div class="stat-value privacy-val">${avg_price_formatted}</div>
                    </div>
                </div>
            </div>
            <div class="card-content">
                <div class="label-value-row"><span class="label">Holdings</span><span class="value privacy-val">{format_holdings(r['Holdings'], ticker)}</span></div>
                <div class="label-value-row"><span class="label">Invested</span><span class="value privacy-val">{format_money(r['USDC'])}</span></div>
                <div class="label-value-row"><span class="label">PnL</span><span class="value card-pnl privacy-val" style="color:{pnl_color};">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</span></div>
                <div class="label-value-row"><span class="label">PnL %</span><span class="value card-pnl-pct privacy-val" style="color:{pnl_color};">{arrow} {pnl_pct_formatted}</span></div>
                <div class="label-value-row total"><span class="label">Value</span><span class="value total-value privacy-val">{format_money(r['Value'])}</span></div>
            </div>
        </div>
        <div class="flip-card-back">
            <a href="https://www.tradingview.com/chart/?symbol=BINANCE:{ticker}USDT" target="_blank" class="tv-external-btn" title="Open in TradingView App/Web to save drawings">
                {TV_ICON}
                <div style="margin-left: 6px; display:flex;">{EXTERNAL_LINK_ICON}</div>
            </a>
            <div class="chart-container">
                <canvas id="chart-{ticker}"></canvas>
                <div class="chart-loading" id="loading-{ticker}">Loading chart...</div>
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
        
        /* Privacy Mode CSS */
        body.privacy-mode .privacy-val {{ color: transparent !important; position: relative; }}
        body.privacy-mode .privacy-val::after {{ content: '***'; position: absolute; right: 0; top: 0; color: #94a3b8; font-size: 1rem; font-weight: 700; }}
        body.privacy-mode .total-value::after {{ color: #ffffff; font-size: 1.15rem; }}

        .flip-card-front, .flip-card-back, .flip-card {{
            outline: none;
            -webkit-tap-highlight-color: transparent;
        }}
        .scroll-wrapper {{
            width: 100%;
            overflow-y: hidden;
            overflow-x: auto;
            padding: 12px 0px 20px 0px;
            margin-bottom: 20px;
            scroll-snap-type: x mandatory; 
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none; 
            -ms-overflow-style: none; 
        }}
        
        .scroll-wrapper::-webkit-scrollbar {{
            display: none; 
        }}

        .coin-grid {{
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            gap: 24px;
            width: max-content;
            padding: 0 24px; 
            background: transparent !important;
            overflow: visible !important;
        }}
        .flip-card {{
            flex: 0 0 420px; 
            background-color: transparent;
            height: 290px;
            perspective: 1200px;
            cursor: pointer;
            scroll-snap-align: center; 
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
            padding: 14px 18px;
            background: #0f172a;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            border: 2px solid transparent;
            overflow: hidden; 
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
            padding: 24px 16px 16px 16px; 
        }}
        
        .tv-external-btn {{
            position: absolute;
            top: 10px;
            right: 12px;
            color: #64748b;
            cursor: pointer;
            z-index: 20;
            transition: color 0.2s ease;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
        }}
        .tv-external-btn:hover {{ color: #ffffff; }}
        
        @media (hover: hover) and (pointer: fine) {{
            .flip-card:hover .flip-card-front,
            .flip-card:hover .flip-card-back {{
                border-color: var(--border);
                box-shadow: 0 12px 28px rgba(0,0,0,0.5), 0 0 12px var(--border);
            }}
        }}
        
        .flip-card.touch-hover .flip-card-front,
        .flip-card.touch-hover .flip-card-back {{
            border-color: var(--border);
            box-shadow: 0 12px 28px rgba(0,0,0,0.5), 0 0 12px var(--border);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            width: 100%;
        }}
        .header-left-container {{
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            flex-shrink: 0;
        }}
        .header-logo-row {{
            display: flex;
            align-items: center;
        }}
        .header-price-row {{
            display: flex;
            flex-direction: row;
            gap: 16px;
            margin-top: 10px;
        }}
        .header-right {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            text-align: right;
            flex: 1;
        }}
        .stat-group {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }}
        .stat-label {{
            font-size: 0.7rem;
            color: #aaa;
            margin-bottom: 2px;
            font-weight: 500;
        }}
        .current-value, .stat-value, .change-value {{
            font-size: 0.98rem;
            font-weight: 700;
            color: white;
            white-space: nowrap;
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
        
        .chart-container {{
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        canvas {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100% !important;
            height: 100% !important;
        }}
        .chart-loading {{
            position: absolute;
            color: #ccc;
            font-size: 0.85rem;
            z-index: 10;
        }}
        
        @media (max-width: 700px) {{
            .flip-card {{ flex: 0 0 85vw; height: 280px; }}
            .coin-grid {{ padding: 0 7.5vw; gap: 16px; }}
            
            .flip-card-front, .flip-card-back {{ padding: 12px 10px; }}
            .header-price-row {{ gap: 10px; margin-top: 8px; }}
            .current-value, .stat-value, .change-value {{ font-size: min(3.8vw, 0.95rem); letter-spacing: -0.3px; }}
            .stat-label {{ font-size: min(2.5vw, 0.65rem); }}
            .header-logo-row span {{ font-size: min(4vw, 1.1rem) !important; margin-left: 6px !important; }}
            .header-logo-row img {{ height: 32px !important; width: 32px !important; }}
        }}
    </style>
</head>
<body>

<div class="scroll-wrapper" id="scrollContainer">
    <div class="coin-grid">
        {cards_html}
    </div>
</div>

<script>
    (function() {{
        function closeAllOpenUI(e) {{
            const isCardClick = e && e.target && typeof e.target.closest === 'function' && e.target.closest('.flip-card');
            
            if (!isCardClick) {{
                document.querySelectorAll('.flip-card.flipped').forEach(card => {{
                    card.classList.remove('flipped');
                    card.classList.remove('touch-hover');
                }});
            }}
        }}

        ['click', 'touchstart'].forEach(evt => {{
            document.addEventListener(evt, (e) => {{
                closeAllOpenUI(e);
            }}, {{ passive: true }});
        }});

        let lastDashState = null;
        setInterval(() => {{
            try {{
                const dt = window.parent.document.getElementById('dash-toggle');
                const dtUsdc = window.parent.document.getElementById('dash-toggle-usdc');
                if (dt) {{
                    const isChecked = dt.checked;
                    
                    if (dtUsdc && dtUsdc.checked !== isChecked) {{
                        dtUsdc.checked = isChecked;
                    }}

                    if (isChecked !== lastDashState) {{
                        lastDashState = isChecked;
                        if (isChecked) {{
                            document.body.classList.remove('privacy-mode');
                            localStorage.setItem('dashboardOpen', 'true');
                        }} else {{
                            document.body.classList.add('privacy-mode');
                            localStorage.setItem('dashboardOpen', 'false');
                        }}
                    }}
                }}
            }} catch(e) {{}}
        }}, 150);

        try {{
            const dt = window.parent.document.getElementById('dash-toggle');
            const dtUsdc = window.parent.document.getElementById('dash-toggle-usdc');
            if (dt) {{
                const saved = localStorage.getItem('dashboardOpen');
                if (saved === 'true') {{
                    dt.checked = true;
                    if(dtUsdc) dtUsdc.checked = true;
                    document.body.classList.remove('privacy-mode');
                    lastDashState = true;
                }} else {{
                    dt.checked = false;
                    if(dtUsdc) dtUsdc.checked = false;
                    document.body.classList.add('privacy-mode');
                    lastDashState = false;
                }}
            }}
        }} catch(e) {{}}

        try {{
            ['click', 'touchstart'].forEach(evt => {{
                window.parent.document.addEventListener(evt, (e) => {{
                    closeAllOpenUI(e); 
                }}, {{ passive: true }});
            }});
        }} catch(err) {{
            console.log("Cannot bind to parent document");
        }}

        const scrollContainer = document.getElementById('scrollContainer');
        if (scrollContainer) {{
            scrollContainer.addEventListener('wheel', (evt) => {{
                if (Math.abs(evt.deltaY) > Math.abs(evt.deltaX)) {{
                    evt.preventDefault();
                    scrollContainer.scrollBy({{ left: evt.deltaY > 0 ? 200 : -200, behavior: 'smooth' }});
                }}
            }}, {{ passive: false }});
        }}

        const usdcHoldings = {usdc_holdings};
        async function updateLivePrices() {{
            const cards = Array.from(document.querySelectorAll('.flip-card'));
            if (cards.length === 0) return;
            const tickers = cards.map(card => card.getAttribute('data-ticker'));
            
            const url = `https://min-api.cryptocompare.com/data/pricemulti?fsyms=${{tickers.join(',')}}&tsyms=USD`;
            try {{
                const resp = await fetch(url);
                const data = await resp.json();
                
                let totalCoinValue = 0;
                let totalCoinInvested = 0;
                cards.forEach(card => {{
                    const ticker = card.getAttribute('data-ticker');
                    const holdings = parseFloat(card.getAttribute('data-holdings'));
                    const invested = parseFloat(card.getAttribute('data-invested'));
                    let price = parseFloat(card.getAttribute('data-current-price'));
                    
                    if (data[ticker] && data[ticker].USD) {{
                        price = data[ticker].USD;
                        card.setAttribute('data-current-price', price);
                        
                        const priceFmt = price < 1 ? price.toFixed(4) : price.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                        const currentEl = card.querySelector('.current-value');
                        if (currentEl) currentEl.innerText = '$' + priceFmt;
                        
                        const value = holdings * price;
                        const pnl = value - invested;
                        const pnlPct = invested > 0 ? (pnl / invested) * 100 : 0;
                        const valStr = '$' + value.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                        const pnlStr = (pnl >= 0 ? '▲ $' : '▼ $') + Math.abs(pnl).toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                        const pnlPctStr = (pnl >= 0 ? '▲ ' : '▼ ') + Math.abs(pnlPct).toFixed(2) + '%';
                        const color = pnl >= 0 ? '#00ff9d' : '#ff4d4d';
                        
                        const valEl = card.querySelector('.total-value');
                        if (valEl) valEl.innerText = valStr;
                        const pnlEl = card.querySelector('.card-pnl');
                        if (pnlEl) {{
                            pnlEl.innerText = pnlStr;
                            pnlEl.style.color = color;
                        }}
                        
                        const pnlPctEl = card.querySelector('.card-pnl-pct');
                        if (pnlPctEl) {{
                            pnlPctEl.innerText = pnlPctStr;
                            pnlPctEl.style.color = color;
                        }}
                        
                        if (window.chartCache && window.chartCache[ticker] && window.chartCache[ticker].chartObj) {{
                            const chart = window.chartCache[ticker].chartObj;
                            const dataLen = chart.data.datasets[0].data.length;
                            if (dataLen > 0) {{
                                chart.data.datasets[0].data[dataLen - 1] = price;
                                chart.update('none'); 
                            }}
                        }}
                    }}
                    
                    totalCoinValue += (holdings * price);
                    totalCoinInvested += invested;
                }});
                
                const totalPortfolioValue = totalCoinValue + usdcHoldings;
                const totalPnL = totalCoinValue - totalCoinInvested; 
                const totalInvestedBase = totalPortfolioValue - totalPnL;
                const totalPnLPct = totalInvestedBase !== 0 ? (totalPnL / totalInvestedBase) * 100 : 0;
                
                const dashValStr = '$' + totalPortfolioValue.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                const dashPnlStr = (totalPnL >= 0 ? '▲ $' : '▼ $') + Math.abs(totalPnL).toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                const dashPnlPctStr = (totalPnL >= 0 ? '▲ ' : '▼ ') + Math.abs(totalPnLPct).toFixed(2) + '%';
                const dashColor = totalPnL >= 0 ? '#00ff9d' : '#ff4d4d';
                
                const parentDoc = window.parent.document;
                const dValue = parentDoc.getElementById('dash-total-value');
                const dPnl = parentDoc.getElementById('dash-pnl');
                const dPnlPct = parentDoc.getElementById('dash-pnl-pct');
                
                if (dValue) dValue.innerText = dashValStr;
                if (dPnl) {{ dPnl.innerText = dashPnlStr; dPnl.style.color = dashColor; }}
                if (dPnlPct) {{ dPnlPct.innerText = dashPnlPctStr; dPnlPct.style.color = dashColor; }}
                
            }} catch (e) {{
                console.error('Auto-refresh error:', e);
            }}
        }}
        setInterval(updateLivePrices, 10000);

        function saveFlippedState() {{
            const flippedCards = [];
            document.querySelectorAll('.flip-card').forEach(card => {{
                if (card.classList.contains('flipped')) {{
                    const ticker = card.getAttribute('data-ticker');
                    if (ticker) flippedCards.push(ticker);
                }}
            }});
            localStorage.setItem('flippedCards', JSON.stringify(flippedCards));
        }}
        
        function restoreFlippedState() {{
            const saved = localStorage.getItem('flippedCards');
            if (!saved) return;
            const flippedTickers = JSON.parse(saved);
            document.querySelectorAll('.flip-card').forEach(card => {{
                const ticker = card.getAttribute('data-ticker');
                if (flippedTickers.includes(ticker)) {{
                    card.classList.add('flipped');
                    card.classList.add('touch-hover');
                    const currentPrice = parseFloat(card.getAttribute('data-current-price'));
                    const avgPrice = parseFloat(card.getAttribute('data-avg-price'));
                    const chartColor = card.getAttribute('data-chart-color');
                    if (!chartCache[ticker] || !chartCache[ticker].chartObj) {{
                        renderChart(card, ticker, currentPrice, avgPrice, chartColor);
                        update24hChange(card, ticker);
                    }}
                }}
            }});
            localStorage.removeItem('flippedCards');
        }}

        const flipCards = document.querySelectorAll('.flip-card');
        window.chartCache = window.chartCache || {{}};
        const chartCache = window.chartCache;
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
            
            hist.prices[hist.prices.length - 1] = currentPrice;
            const ctx = canvas.getContext('2d');
            if (chartCache[ticker] && chartCache[ticker].chartObj) {{
                chartCache[ticker].chartObj.destroy();
            }}
            const datasets = [
                {{
                    label: 'Close Price ($)',
                    data: hist.prices,
                    borderColor: chartColor,
                    backgroundColor: chartColor + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.2,
                    pointRadius: 2,
                    pointBackgroundColor: chartColor
                }},
                {{
                    label: 'Avg Price ($)',
                    data: new Array(hist.labels.length).fill(avgPrice),
                    borderColor: '#ffaa00',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    type: 'line'
                }}
            ];
            const newChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: hist.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false, 
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
            const changeSpan = card.querySelector(`#change-${{ticker}}`);
            if (!changeSpan) return;
            const change = await fetch24hChange(ticker);
            if (change !== null) {{
                const sign = change >= 0 ? '▲' : '▼';
                const color = change >= 0 ? '#00ff9d' : '#ff4d4d';
                changeSpan.innerHTML = `<span style="color:${{color}};">${{sign}} ${{Math.abs(change).toFixed(2)}}%</span>`;
            }} else {{
                changeSpan.innerHTML = `N/A`;
            }}
        }}
        
        flipCards.forEach(card => {{
            const ticker = card.getAttribute('data-ticker');
            const currentPrice = parseFloat(card.getAttribute('data-current-price'));
            const avgPrice = parseFloat(card.getAttribute('data-avg-price'));
            const chartColor = card.getAttribute('data-chart-color');
            const border = card.getAttribute('data-border');
            card.style.setProperty('--border', border);
            
            update24hChange(card, ticker);
            
            const front = card.querySelector('.flip-card-front');
            front.addEventListener('click', (e) => {{
                e.stopPropagation();
                if (!card.classList.contains('flipped')) {{
                    card.classList.add('flipped');
                    card.classList.add('touch-hover');
                    if (!chartCache[ticker] || !chartCache[ticker].chartObj) {{
                        renderChart(card, ticker, currentPrice, avgPrice, chartColor);
                    }}
                }}
            }});
            const backDiv = card.querySelector('.flip-card-back');
            backDiv.addEventListener('click', (e) => {{
                card.classList.remove('flipped');
                card.classList.remove('touch-hover');
            }});
            const extBtn = card.querySelector('.tv-external-btn');
            if (extBtn) {{
                extBtn.addEventListener('click', (e) => {{
                    e.stopPropagation();
                }});
            }}
        }});
        
        restoreFlippedState();
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
        components.html(full_html, height=340, scrolling=False)

    # ====================== CRYPTO TRANSACTIONS ======================
    elif st.session_state.page == "Crypto Transactions":
        glossy_header("Crypto Transactions", CRYPTO_ICON)

        st.markdown("""
        <style>
        /* 1. NEW ADD TRANSACTION CARD */
        div[data-testid="stForm"]:has(.add-tx-card) {
            background: #0f172a !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
            margin-bottom: 24px !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) label { font-size: 0.85rem !important; color: #94a3b8 !important; padding-bottom: 2px !important; }
        
        div[data-testid="stForm"]:has(.add-tx-card) .stTextInput input,
        div[data-testid="stForm"]:has(.add-tx-card) .stNumberInput input,
        div[data-testid="stForm"]:has(.add-tx-card) .stDateInput input {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            color: #fff !important;
            border-radius: 8px !important;
            margin-bottom: 0px !important;
        }

        /* 1a. FIRST ROW (4 columns): Inputs */
        div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) {
            display: flex !important;
            gap: 12px !important;
        }
        
        /* 1b. SECOND ROW (2 columns): Action (Switch + Button) */
        div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            margin-top: 12px !important;
            gap: 12px !important;
        }
        /* Make switch column hug content, make button column take rest */
        div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"]:nth-child(1) {
            flex: 0 0 auto !important;
            width: auto !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"]:nth-child(2) {
            flex: 1 1 auto !important;
            width: auto !important;
        }

        /* BEAUTIFUL BUY/SELL SWITCH */
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] {
            background: rgba(0,0,0,0.3) !important;
            padding: 6px !important;
            border-radius: 12px !important;
            display: flex !important;
            flex-direction: row !important;
            gap: 8px !important;
            align-items: center !important;
            margin: 0 !important;
            height: 48px !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            min-width: 200px !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label {
            margin: 0 !important;
            cursor: pointer !important; 
            padding: 0 !important; 
            border-radius: 8px !important;
            border: 1px solid transparent !important; 
            transition: all 0.3s ease !important;
            background: transparent !important;
            flex: 1 !important; 
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100% !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:hover { background: rgba(255,255,255,0.05) !important; }
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label > div:first-child { display: none !important; } 
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label p {
            font-weight: bold !important;
            font-size: 1.05rem !important; color: #94a3b8 !important; margin: 0 !important; padding: 0 !important; white-space: nowrap !important; line-height: 1 !important;
        }
        /* Active Buy */
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):first-child,
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:first-child {
            background: rgba(0, 255, 157, 0.15) !important;
            border-color: #00ff9d !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):first-child p,
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:first-child p { color: #00ff9d !important; }
        
        /* Active Sell */
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):last-child,
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:last-child {
            background: rgba(255, 77, 77, 0.15) !important;
            border-color: #ff4d4d !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):last-child p,
        div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:last-child p { color: #ff4d4d !important; }

        /* 3. RIGHT ALIGNED SUBMIT BUTTON */
        div[data-testid="stForm"]:has(.add-tx-card) .stButton {
            display: flex !important;
            justify-content: flex-end !important; /* Force to right side */
            align-items: center !important;
            margin: 0 !important; padding: 0 !important;
            width: 100% !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) .stButton > button {
            background: #1e2a44 !important;
            color: #e0e0e0 !important; padding: 0 24px !important;
            border-radius: 10px !important; font-size: 1.05rem !important; font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important; transition: all 0.3s ease !important;
            border: none !important; margin: 0 !important; width: auto !important;
            height: 48px !important; min-height: 48px !important;
        }
        div[data-testid="stForm"]:has(.add-tx-card) .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.2) !important; color: white !important;
        }

        /* 4. TRANSACTION ROW STYLING & INLINE BUTTONS */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) {
            background: #0f172a !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin-bottom: 12px !important;
            position: relative;
            z-index: 2;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div { padding: 0 !important; } 
        
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button {
            background: rgba(255,255,255,0.05) !important;
            border-radius: 8px !important; border: none !important;
            height: 40px !important; width: 40px !important; display: flex !important; align-items: center !important;
            justify-content: center !important; padding: 0 !important; margin: 0 auto !important; font-size: 1.2rem !important;
            transition: all 0.2s !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button:hover {
            background: rgba(255,255,255,0.15) !important;
            transform: scale(1.05) !important;
        }

        /* 5. SMOOTH EDIT ROLLOUT */
        @keyframes rollDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        div[data-testid="stForm"]:has(.edit-rollout) {
            animation: rollDown 0.3s ease forwards !important;
            background: rgba(0,0,0,0.2) !important;
            border-left: 3px solid #00ff9d !important; border-radius: 0 0 12px 12px !important;
            border-top: none !important; border-right: none !important;
            border-bottom: none !important;
            padding: 16px !important; margin-top: -24px !important; margin-bottom: 20px !important;
            position: relative; z-index: 1;
            box-shadow: inset 0 4px 10px rgba(0,0,0,0.15) !important;
        }

        /* 6. REDESIGNED DELETE DIALOG */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) {
            border-color: rgba(255, 77, 77, 0.3) !important;
            background: rgba(15, 23, 42, 0.95) !important;
            border-radius: 12px !important; 
            padding: 16px !important; 
            text-align: center !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) .stButton > button {
            border-radius: 8px !important;
            font-weight: 600 !important; 
            transition: all 0.2s !important; 
            width: 100% !important; 
            margin-top: 8px !important;
            padding: 6px 12px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(1) .stButton > button {
            background: rgba(255, 77, 77, 0.1) !important;
            color: #ff4d4d !important; 
            border: 1px solid rgba(255, 77, 77, 0.3) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(1) .stButton > button:hover {
            background: #ff4d4d !important;
            color: white !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(2) .stButton > button {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #cbd5e1 !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(2) .stButton > button:hover {
            background: rgba(255, 255, 255, 0.15) !important;
            color: white !important;
        }

        /* ==============================================================
           7. MOBILE OVERRIDES (IRONCLAD)
           ============================================================== */
        @media (max-width: 768px) {
            .stApp { padding-top: 72px !important; }
            .glossy-header { margin-top: 48px !important; margin-bottom: 24px !important; padding: 20px 16px !important; font-size: 22px !important; min-height: 90px; }
            .home-header { margin-bottom: 0 !important; }
            
            /* Fix Add Form Mobile Grid */
            /* Force all horizontal blocks inside the form to flex explicitly */
            div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important; 
                flex-wrap: wrap !important; 
                gap: 12px !important;
            }
            
            /* The 4-column inputs row -> map exactly to 2x2 grid */
            div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] {
                min-width: calc(50% - 12px) !important;
                width: calc(50% - 12px) !important;
                flex: 1 1 calc(50% - 12px) !important;
            }
            div[data-testid="stForm"]:has(.add-tx-card) input { padding: 6px !important; font-size: 0.95rem !important; }
            
            /* The 2-column action row -> map to the 50/50 split below inputs (Switch left, Button right) */
            div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"] {
                min-width: calc(50% - 12px) !important;
                width: calc(50% - 12px) !important;
                flex: 1 1 calc(50% - 12px) !important;
            }
            div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] {
                min-width: 0 !important;
                width: 100% !important; 
            }
            /* Push the submit button to the absolute right of its column */
            div[data-testid="stForm"]:has(.add-tx-card) .stButton {
                display: flex !important;
                justify-content: flex-end !important;
                width: 100% !important;
            }
            div[data-testid="stForm"]:has(.add-tx-card) .stButton > button {
                width: 100% !important;
                max-width: 120px !important; 
                padding: 0 16px !important;
            }

            /* Force Mobile Transaction Rows to stay perfectly horizontal */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; overflow: hidden !important; gap: 2px !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="column"] {
                min-width: 0 !important;
                padding: 0 !important; width: auto !important; flex-shrink: 1 !important;
            }
            /* Exact layout for the 5 strict columns to prevent ANY dropping/wrapping */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { flex: 0 0 35px !important; width: 35px !important; } /* Logo */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) { flex: 1 1 auto !important; overflow: hidden !important; text-align: left; } /* Ticker */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) { flex: 1.5 1 auto !important; overflow: hidden !important; text-align: center; } /* Amounts */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) { flex: 0 0 36px !important; width: 36px !important; } /* Edit */
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) { flex: 0 0 36px !important; width: 36px !important; } /* Delete */
            
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button {
                width: 30px !important; height: 30px !important; font-size: 0.9rem !important; margin: 0 auto !important;
            }
            
            .mobile-logo { width: 32px !important; height: 32px !important; margin-top: 0 !important; }
            .mobile-tx-ticker { font-size: 0.95rem !important; margin-left: 2px !important;}
            .mobile-tx-amount { font-size: 0.95rem !important; white-space: nowrap !important; }
            .mobile-tx-sub { font-size: 0.7rem !important; white-space: nowrap !important; margin-left: 2px !important;}
            
            /* Dashboard Mobile Stats Override Fix */
            .stats-layer-inner { gap: 6px !important; }
            .stats-layer { margin-top: -60px !important; margin-bottom: 18px; } 
            .glossy-box.swapped { height: 80px !important; min-height: 80px !important; max-height: 80px !important; padding: 0 !important; min-width: 0 !important; }
            .dash-value { font-size: clamp(11px, 3.5vw, 15px) !important; top: 24px !important; } 
            .dash-label { font-size: clamp(8px, 2.5vw, 10px) !important; bottom: 8px !important; white-space: nowrap !important; letter-spacing: 0.5px !important; }
            
            /* Restyled Subdued USDC Banner Mobile */
            .usdc-banner { padding: 8px 14px; width: 92%; margin: 0 auto 20px auto; }
            .usdc-banner-left img { width: 24px; height: 24px; }
            .usdc-banner-title { font-size: 0.95rem; }
            .usdc-banner-subtitle { font-size: 0.7rem; }
            .usdc-banner-amount { font-size: 1.1rem; }
        }
        </style>
        """, unsafe_allow_html=True)

        # 1. ADD NEW TRANSACTION CARD
        with st.form("add_crypto", border=False):
            st.markdown("<div class='add-tx-card'></div><h3 style='text-align: center; color: white; margin-top: 0px; margin-bottom: 10px;'>New Transaction</h3>", unsafe_allow_html=True)
            
            # Row 1: Inputs (Rendered as 4 columns on PC, cleanly wrapped to 2x2 grid by CSS on mobile)
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            with r1c1: selected_date = st.date_input("Date", value=date(2026, 3, 25))
            with r1c2: ticker = st.text_input("Ticker", value="BTC").upper().strip()
            with r1c3: usdc = st.number_input("USDC Amount", value=15.0, step=0.01)
            with r1c4: amount = st.number_input("Coin Amount", value=0.1, step=0.000001, format="%.8f")
            
            # Row 2: Action Row (Always 2 columns mapping naturally under the 2x2 layout above on mobile)
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                tx_type = st.radio("Type", ["Buy", "Sell"], horizontal=True, label_visibility="collapsed")
            with action_col2:
                submitted = st.form_submit_button("+ Add")
            
            if submitted:
                if ticker:
                    final_usdc = usdc if tx_type == "Buy" else -usdc
                    final_amount = amount if tx_type == "Buy" else -amount
                    price = round(usdc / amount, 8) if amount > 0 else 0.0
                    
                    new_row = pd.DataFrame([{"Datum": date_to_excel_serial(selected_date), "USDC": final_usdc, "Ticker": ticker, "Amount": final_amount, "Price": price}])
                    st.session_state.crypto_df = pd.concat([st.session_state.crypto_df, new_row], ignore_index=True)
                    save_crypto(st.session_state.crypto_df)
                    st.session_state.crypto_table_version += 1
                    st.session_state.ui_version += 1
                    st.success(f"✅ Executed {tx_type}: {amount} {ticker}")
                    st.rerun()

        # Preserve original index for accurate editing/deleting, then sort descending by Date
        df_display = st.session_state.crypto_df.copy()
        df_display['orig_idx'] = df_display.index
        df_display = df_display.dropna(how='all')
        df_display = df_display.sort_values(by='Datum', ascending=False)

        st.markdown("<h4 style='color: white; margin-top: 20px; margin-bottom: 15px;'>Transaction History</h4>", unsafe_allow_html=True)
        
        # 2. SCROLLABLE TRANSACTION LIST
        with st.container(height=550, border=False):
            for i, r in df_display.iterrows():
                orig_idx = r['orig_idx']
                logo_url = get_ticker_logo(r['Ticker'])
                amount = r['Amount']
                usdc = r['USDC']
                is_buy = amount >= 0
                
                abs_amount = abs(amount)
                abs_usdc = abs(usdc)
                price = abs_usdc / abs_amount if abs_amount > 0 else 0
                
                sign = "+" if is_buy else "-"
                color = "#00ff9d" if is_buy else "#ff4d4d"
                action_text = "Spent" if is_buy else "Received"
                
                invested_formatted = format_money(abs_usdc)
                amount_formatted = format_holdings(abs_amount, r['Ticker'])
                price_formatted = format_price(price)
                date_str = format_datum(r['Datum'])

                # If user clicked delete, show confirmation dialog replacing the row
                if st.session_state.get('confirm_delete_crypto') == orig_idx:
                    with st.container(border=True):
                        st.markdown("<div class='del-warn'></div><h4 style='color: #ff4d4d; margin-top: 0; margin-bottom: 5px; font-size: 1.1rem; font-weight: 600;'>Delete this transaction?</h4>", unsafe_allow_html=True)
                        c_yes, c_no = st.columns(2)
                        with c_yes:
                            if st.button("Delete", key=f"yes_del_{orig_idx}", use_container_width=True):
                                st.session_state.crypto_df = st.session_state.crypto_df.drop(orig_idx).reset_index(drop=True)
                                save_crypto(st.session_state.crypto_df)
                                st.session_state['confirm_delete_crypto'] = None
                                st.session_state.crypto_table_version += 1
                                st.session_state.ui_version += 1
                                st.rerun()
                        with c_no:
                            if st.button("Cancel", key=f"no_del_{orig_idx}", use_container_width=True):
                                st.session_state['confirm_delete_crypto'] = None
                                st.rerun()
                else:
                    # Standard Row Display
                    with st.container(border=True):
                        st.markdown("<div class='tx-row'></div>", unsafe_allow_html=True)
                        
                        # STRICT 5 COLUMNS: Logo, Ticker/Date, Values, Edit, Delete
                        col_logo, col_ticker, col_vals, col_edit, col_del = st.columns([0.5, 2, 2.5, 0.5, 0.5])
                        
                        with col_logo:
                            st.markdown(f"<img src='{logo_url}' class='mobile-logo' style='width:42px;height:42px;border-radius:50%;object-fit:contain;margin-top:6px;' onerror=\"this.src='https://via.placeholder.com/42/1e2a44/ffffff?text={r['Ticker'][0]}';\">", unsafe_allow_html=True)
                            
                        with col_ticker:
                            st.markdown(f"""
                                <div style="line-height: 1.2; margin-top: 6px; overflow: hidden; text-overflow: ellipsis;">
                                    <div class="mobile-tx-ticker" style="font-weight: 700; font-size: 1.15rem; color: #ffffff; white-space: nowrap;">{r['Ticker']}</div>
                                    <div class="mobile-tx-sub" style="font-size: 0.85rem; color: #94a3b8; white-space: nowrap;">{date_str}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        with col_vals:
                            st.markdown(f"""
                                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; margin-top: 6px;">
                                    <div class="mobile-tx-amount" style="font-weight: 700; font-size: 1.15rem; color: {color}; white-space: nowrap;">{sign}{amount_formatted}</div>
                                    <div class="mobile-tx-sub" style="font-size: 0.85rem; color: #cbd5e1; white-space: nowrap;">{action_text}: {invested_formatted} @ ${price_formatted}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        with col_edit:
                            if st.button("✏️", key=f"edit_btn_{orig_idx}"):
                                if st.session_state.get('edit_crypto_row') == orig_idx:
                                    st.session_state['edit_crypto_row'] = None
                                else:
                                    st.session_state['edit_crypto_row'] = orig_idx
                                st.rerun()
                                
                        with col_del:
                            if st.button("🗑️", key=f"del_btn_{orig_idx}"):
                                st.session_state['confirm_delete_crypto'] = orig_idx
                                st.rerun()

                    # 3. ROLL OUT EDIT FORM Directly Attached
                    if st.session_state.get('edit_crypto_row') == orig_idx:
                        with st.form(f"edit_crypto_form_{orig_idx}", border=False):
                            st.markdown("<div class='edit-rollout form-compact-marker'></div><h4 style='color: #00ff9d; margin-top: 0px; margin-bottom: 15px;'>✏️ Edit Row Details</h4>", unsafe_allow_html=True)
                            
                            e_r1c1, e_r1c2 = st.columns(2)
                            with e_r1c1: new_date = st.date_input("Date", value=datetime(1899, 12, 30) + timedelta(days=int(r['Datum'])))
                            with e_r1c2: new_ticker = st.text_input("Ticker", value=r['Ticker']).upper().strip()
                            
                            e_r2c1, e_r2c2 = st.columns(2)
                            with e_r2c1: new_usdc = st.number_input("USDC Amount", value=float(abs(r['USDC'])), step=0.01)
                            with e_r2c2: new_amount = st.number_input("Coin Amount", value=float(abs(r['Amount'])), step=0.000001, format="%.8f")
                            
                            tx_type_edit = st.radio("Type", ["Buy", "Sell"], horizontal=True, index=0 if is_buy else 1, label_visibility="collapsed")
                            
                            e_save, e_cancel = st.columns(2)
                            with e_save: 
                                if st.form_submit_button("💾 Save Changes"):
                                    final_usdc = new_usdc if tx_type_edit == "Buy" else -new_usdc
                                    final_amount = new_amount if tx_type_edit == "Buy" else -new_amount
                                    new_price = round(new_usdc / new_amount, 8) if new_amount > 0 else 0.0
                                    
                                    st.session_state.crypto_df.loc[orig_idx] = {"Datum": date_to_excel_serial(new_date), "USDC": final_usdc, "Ticker": new_ticker, "Amount": final_amount, "Price": new_price}
                                    save_crypto(st.session_state.crypto_df)
                                    st.session_state['edit_crypto_row'] = None
                                    st.session_state.crypto_table_version += 1
                                    st.session_state.ui_version += 1
                                    st.success("✅ Transaction updated!")
                                    st.rerun()
                                    
                            with e_cancel:
                                if st.form_submit_button("❌ Cancel"):
                                    st.session_state['edit_crypto_row'] = None
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
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-bottom:30px;">
<div class="glossy-box swapped"><div class="dash-value">{total_czk:,.2f}</div><div class="dash-label">Total CZK</div></div>
<div class="glossy-box swapped"><div class="dash-value">{total_eur:,.2f}</div><div class="dash-label">Total EUR</div></div>
<div class="glossy-box swapped"><div class="dash-value">{format_money(total_usdc)}</div><div class="dash-label">Total USDC</div></div>
<div class="glossy-box swapped">
<div class="dash-value" style="font-size:13px !important; white-space:normal;">{fees_eur:,.2f} EUR / {fees_czk:,.2f} CZK</div>
<div class="dash-label">Fees</div>
</div>
</div>
"""
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
                h[6].markdown("**Del**")
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
                        if st.session_state.get(f'confirm_del_fiat_{i}'):
                            if st.button("✅", key=f"yes_fiat_{i}"):
                                st.session_state.fiat_df = st.session_state.fiat_df.drop(i).reset_index(drop=True)
                                save_fiat(st.session_state.fiat_df)
                                st.session_state.fiat_table_version += 1
                                st.session_state.ui_version += 1
                                st.session_state[f'confirm_del_fiat_{i}'] = False
                                st.rerun()
                        else:
                            if st.button("🗑️", key=f"del_{i}_{st.session_state.fiat_table_version}_{st.session_state.ui_version}"):
                                st.session_state[f'confirm_del_fiat_{i}'] = True
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
