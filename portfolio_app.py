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

.dashboard-toggle:checked + .glossy-header-label .pull-indicator .eye-open { display: block; }
.dashboard-toggle:checked + .glossy-header-label .pull-indicator .eye-closed { display: none; }
.dashboard-toggle:checked + .glossy-header-label .pull-indicator { color: #ffffff; }

.stats-layer {
    position: relative;
    z-index: 1;
    margin-top: -60px !important; 
    transition: margin-top 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 24px;
}
.dashboard-toggle:checked ~ .stats-layer {
    margin-top: 14px !important; /* Drops down */
}
.stats-layer-inner {
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(98px, 1fr)); 
    gap: 14px;
}

/* Tucked Text Fade Out */
.dash-value {
    font-size: 24px !important; /* Elegant size on PC */
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
}
.dashboard-toggle:not(:checked) ~ .stats-layer .dash-value {
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
.dashboard-toggle:checked + .glossy-header-label .glossy-header {
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
    height: 80px !important;
    min-height: 80px !important;
    max-height: 80px !important;
    padding: 0;
    display: block;
}

.usdc-banner {
    position: relative;
    overflow: hidden;
    background: #0f172a;
    border: 2px solid rgba(39, 117, 202, 0.4);
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    padding: 20px 26px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.usdc-banner-left {
    display: flex;
    align-items: center;
    gap: 16px;
}
.usdc-banner-left img {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    object-fit: contain;
}
.usdc-banner-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
}
.usdc-banner-subtitle {
    font-size: 0.95rem;
    font-weight: 500;
    color: #94a3b8;
}
.usdc-banner-amount {
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
}

/* ==============================================================
   1. REDESIGNED COMPACT FORMS & SWITCH
   ============================================================== */
div[data-testid="stForm"]:has(.form-compact) {
    background: #0f172a !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
    margin-bottom: 24px !important;
}
div[data-testid="stForm"]:has(.form-compact) label {
    font-size: 0.85rem !important;
    min-height: 0 !important;
    padding-bottom: 2px !important;
}
div[data-testid="stForm"]:has(.form-compact) .stNumberInput, 
div[data-testid="stForm"]:has(.form-compact) .stTextInput, 
div[data-testid="stForm"]:has(.form-compact) .stDateInput {
    margin-bottom: 2px !important;
}

/* Modern Segmented Control for Buy/Sell Radio inside forms */
div[data-testid="stForm"]:has(.form-compact) div[role="radiogroup"] {
    display: flex;
    flex-direction: row;
    background: #1e293b;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 40px;
    padding: 4px;
    width: 100%;
    max-width: 300px;
    margin: 15px auto 20px auto;
    gap: 0px;
}
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"] {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px 0;
    border-radius: 36px;
    margin: 0;
    background: transparent;
    transition: all 0.3s ease;
    cursor: pointer !important;
}
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"] div:first-child {
    display: none; /* Hide the native circle dot completely */
}
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"] p {
    font-weight: 700 !important;
    color: #64748b !important;
    margin: 0 !important;
    font-size: 1.05rem !important;
    transition: color 0.3s ease;
}
/* Buy Active */
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"][aria-checked="true"] {
    background: #00ff9d;
    box-shadow: 0 4px 12px rgba(0, 255, 157, 0.3);
}
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"][aria-checked="true"] p {
    color: #0f172a !important;
}
/* Sell Active */
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"][aria-checked="true"]:nth-child(2) {
    background: #ff4d4d;
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.3);
}
div[data-testid="stForm"]:has(.form-compact) label[data-baseweb="radio"][aria-checked="true"]:nth-child(2) p {
    color: white !important; 
}

/* Form Submit Button */
div[data-testid="stForm"]:has(.form-compact) .stButton > button {
    background: #1e2a44 !important;
    color: #e0e0e0 !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    height: auto !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stForm"]:has(.form-compact) .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(255, 255, 255, 0.2) !important;
    background: #263b5e !important;
    color: white !important;
}

/* ==============================================================
   2. NATIVE INLINE ROW BUTTONS & ROLLOUT ANIMATION
   ============================================================== */

/* Buttons locked directly in the row */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: none !important;
    border-radius: 8px !important;
    height: 44px !important;
    width: 44px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 !important;
    margin: 0 auto !important;
    font-size: 1.2rem !important;
    box-shadow: none !important;
    transition: all 0.2s;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    transform: scale(1.08);
}

/* Edit Form Smooth Rollout Animation */
@keyframes smoothRollout {
    0% { max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0; margin-top: -20px; overflow: hidden; transform: scaleY(0.95); transform-origin: top; }
    100% { max-height: 500px; opacity: 1; padding-top: 14px; padding-bottom: 4px; margin-top: 0px; overflow: visible; transform: scaleY(1); transform-origin: top; }
}
.edit-rollout-container {
    animation: smoothRollout 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    border-left: 3px solid #00ff9d;
    padding-left: 14px;
    background: linear-gradient(90deg, rgba(255,255,255,0.03) 0%, transparent 100%);
    border-radius: 0 12px 12px 0;
}

/* ==============================================================
   3. MOBILE OVERRIDES (FORCE 2x2 GRID & INLINE ROWS)
   ============================================================== */
@media (max-width: 768px) {
    .stApp { padding-top: 72px !important; }
    .glossy-header { margin-top: 48px !important; margin-bottom: 24px !important; padding: 20px 16px !important; font-size: 22px !important; min-height: 90px; }
    .home-header { margin-bottom: 0 !important; }
    
    /* Force Form inputs to 2-columns (2x2 grid) on mobile */
    div[data-testid="stForm"]:has(.form-compact) div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
    }
    div[data-testid="stForm"]:has(.form-compact) div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 48% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
    
    /* Force Transaction Rows to stay completely horizontal (inline) on mobile */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: auto !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
        padding: 0 2px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
        flex: 0 0 auto !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row-inline) div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
        flex: 0 0 auto !important;
    }
    
    /* Shrink text inside the row to fit nicely */
    .mobile-tx-ticker { font-size: 1rem !important; }
    .mobile-tx-amount { font-size: 0.95rem !important; white-space: nowrap !important; }
    .mobile-tx-sub { font-size: 0.75rem !important; white-space: nowrap !important; }
    .mobile-logo { width: 36px !important; height: 36px !important; }
    
    .stats-layer { margin-top: -60px !important; margin-bottom: 18px; } 
    .glossy-box.swapped { height: 80px !important; min-height: 80px !important; max-height: 80px !important; padding: 0 !important; min-width: 0 !important; }
    .dash-value { font-size: 15px !important; top: 22px; white-space: nowrap; } 
    .dash-label { font-size: 9px !important; bottom: 6px; white-space: nowrap; }
    .usdc-banner { padding: 16px 18px; margin-bottom: 24px; }
    .usdc-banner-left img { width: 36px; height: 36px; }
    .usdc-banner-title { font-size: 1.2rem; }
    .usdc-banner-subtitle { font-size: 0.85rem; }
    .usdc-banner-amount { font-size: 1.4rem; }
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

with main_container.container(key=f"page_{st.session_state.page}_{st.session_state.ui_version}"):
    if st.session_state.page == "Home":

        df_port, total_value, total_pnl, total_pnl_pct = calculate_portfolio(st.session_state.crypto_df)
        
        usdc_row = df_port[df_port['Ticker'] == 'USDC'].iloc[0] if not df_port[df_port['Ticker'] == 'USDC'].empty else None
        usdc_holdings = usdc_row['Holdings'] if usdc_row is not None else 0

        value_box_html = f"""
<div class="dashboard-wrapper">
<input type="checkbox" id="dash-toggle" class="dashboard-toggle" style="display:none;">
<label for="dash-toggle" class="glossy-header-label">
<div class="glossy-header home-header">
{DASHBOARD_ICON}<span style="margin-left:12px;">Portfolio Dashboard</span>
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
<div class="usdc-banner" style="--border: #2775ca;">
<div class="usdc-banner-left">
<img src="{get_ticker_logo('USDC')}" onerror="this.src='https://via.placeholder.com/42/1e2a44/ffffff?text=U';">
<div class="usdc-banner-title">USDC <span class="usdc-banner-subtitle">(Available Cash)</span></div>
</div>
<div class="usdc-banner-amount">{format_holdings(usdc_holdings, 'USDC')}</div>
</div>
"""
        st.markdown(value_box_html, unsafe_allow_html=True)

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
                        <div class="stat-value">${avg_price_formatted}</div>
                    </div>
                </div>
            </div>
            <div class="card-content">
                <div class="label-value-row"><span class="label">Holdings</span><span class="value">{format_holdings(r['Holdings'], ticker)}</span></div>
                <div class="label-value-row"><span class="label">Invested</span><span class="value">{format_money(r['USDC'])}</span></div>
                <div class="label-value-row"><span class="label">PnL</span><span class="value card-pnl" style="color:{pnl_color};">{arrow} {format_money(abs(pnl) if pd.notna(pnl) else "")}</span></div>
                <div class="label-value-row"><span class="label">PnL %</span><span class="value card-pnl-pct" style="color:{pnl_color};">{arrow} {pnl_pct_formatted}</span></div>
                <div class="label-value-row total"><span class="label">Value</span><span class="value total-value">{format_money(r['Value'])}</span></div>
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
            scroll-snap-type: x mandatory; /* Enable scroll snapping */
            -webkit-overflow-scrolling: touch;
            
            /* Completely hide scrollbars */
            scrollbar-width: none; /* Firefox */
            -ms-overflow-style: none;  /* IE and Edge */
        }}
        
        .scroll-wrapper::-webkit-scrollbar {{
            display: none; /* Chrome, Safari, Opera */
        }}

        .coin-grid {{
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap;
            gap: 24px;
            width: max-content;
            padding: 0 24px; /* Default desktop padding */
            background: transparent !important;
            overflow: visible !important;
        }}
        .flip-card {{
            flex: 0 0 420px; /* Made wider */
            background-color: transparent;
            height: 290px;
            perspective: 1200px;
            cursor: pointer;
            scroll-snap-align: center; /* Snap to center */
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
            /* Default slight border glow taking the dynamic color */
            box-shadow: 0 8px 24px rgba(0,0,0,0.3); 
            border: 2px solid transparent;
            overflow: hidden; /* Prevent internal scrolling */
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
            padding: 24px 16px 16px 16px; /* Extra top padding for the TV button */
        }}
        
        /* TradingView External Link Button */
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
        
        /* Interactive dynamic colored border glow - ONLY applies on PC (fine pointers) */
        @media (hover: hover) and (pointer: fine) {{
            .flip-card:hover .flip-card-front,
            .flip-card:hover .flip-card-back {{
                border-color: var(--border);
                box-shadow: 0 12px 28px rgba(0,0,0,0.5), 0 0 12px var(--border);
            }}
        }}
        
        /* Touch Hover explicitly triggered by JS on mobile */
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
            /* Fit phone width perfectly with snapping */
            .flip-card {{ flex: 0 0 85vw; height: 280px; }}
            .coin-grid {{ padding: 0 7.5vw; gap: 16px; }}
            
            /* Responsive fonts and padding to prevent overflow */
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
        // Define the close function for global click-away
        function closeAllOpenUI(e) {{
            // Only run if the click is outside a flip-card inner and outside dashboard wrapper
            const isDashClick = e && e.target && e.target.closest && e.target.closest('.dashboard-wrapper');
            const isCardClick = e && e.target && e.target.closest && e.target.closest('.flip-card');
            
            if (!isDashClick) {{
                const dashToggle = document.getElementById('dash-toggle');
                if (dashToggle && dashToggle.checked) {{
                    dashToggle.checked = false; // Close drawer and inherently remove hover
                }}
            }}
            
            // Unflip cards if clicking completely outside
            if (!isCardClick) {{
                document.querySelectorAll('.flip-card.flipped').forEach(card => {{
                    card.classList.remove('flipped');
                    card.classList.remove('touch-hover');
                }});
            }}
        }}

        // Listen inside the iframe
        ['click', 'touchstart'].forEach(evt => {{
            document.addEventListener(evt, (e) => {{
                closeAllOpenUI(e);
            }}, {{ passive: true }});
        }});

        // Listen outside the iframe (Parent Streamlit Document)
        try {{
            ['click', 'touchstart'].forEach(evt => {{
                window.parent.document.addEventListener(evt, () => {{
                    closeAllOpenUI(null); 
                }}, {{ passive: true }});
            }});
        }} catch(err) {{
            console.log("Cannot bind to parent document");
        }}

        // --- Wheel scrolling for PC ---
        const scrollContainer = document.getElementById('scrollContainer');
        if (scrollContainer) {{
            scrollContainer.addEventListener('wheel', (evt) => {{
                // Detect vertical scroll to convert to horizontal
                if (Math.abs(evt.deltaY) > Math.abs(evt.deltaX)) {{
                    evt.preventDefault();
                    // Using a smaller step (200) makes it slower/more controlled on PC
                    scrollContainer.scrollBy({{ left: evt.deltaY > 0 ? 200 : -200, behavior: 'smooth' }});
                }}
            }}, {{ passive: false }});
        }}

        // --- Live Price Auto Refresh Logic ---
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
                        
                        // Update Current Price Display
                        const priceFmt = price < 1 ? price.toFixed(4) : price.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
                        const currentEl = card.querySelector('.current-value');
                        if (currentEl) currentEl.innerText = '$' + priceFmt;
                        
                        // Recalculate Card PnL & Value
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
                        
                        // Update Live Chart Last Dot dynamically
                        if (window.chartCache && window.chartCache[ticker] && window.chartCache[ticker].chartObj) {{
                            const chart = window.chartCache[ticker].chartObj;
                            const dataLen = chart.data.datasets[0].data.length;
                            if (dataLen > 0) {{
                                chart.data.datasets[0].data[dataLen - 1] = price;
                                chart.update('none'); // Update smoothly without animation restart
                            }}
                        }}
                    }}
                    
                    totalCoinValue += (holdings * price);
                    totalCoinInvested += invested;
                }});
                
                // Update Parent Streamlit Dashboard seamlessly
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
        // Poll every 10 seconds silently
        setInterval(updateLivePrices, 10000);

        // --- State preservation ---
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
        
        // --- Remember Dashboard Drawer State natively across sessions ---
        const dashToggle = document.getElementById('dash-toggle');
        if (dashToggle) {{
            const savedDashState = localStorage.getItem('dashboardOpen');
            if (savedDashState === 'true') {{
                dashToggle.checked = true;
            }}
            dashToggle.addEventListener('change', () => {{
                localStorage.setItem('dashboardOpen', dashToggle.checked);
            }});
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
            
            // Replace the last item of the history array with the LIVE CURRENT PRICE
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
                    maintainAspectRatio: false, /* allows stretching to fill container */
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
            
            // Trigger load data immediately on script execution to populate the front
            update24hChange(card, ticker);
            
            const front = card.querySelector('.flip-card-front');
            front.addEventListener('click', (e) => {{
                e.stopPropagation();
                // Toggle flipped state and touch-hover properly for mobile
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
                // Tapping anywhere on the back flips the card over
                card.classList.remove('flipped');
                card.classList.remove('touch-hover');
            }});
            
            // Prevent the external link from triggering a flip
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

        # 1. ADD NEW TRANSACTION CARD (Compact / 2x2 on Mobile)
        with st.form("add_crypto", border=False):
            st.markdown("<div class='form-compact'></div><h3 style='text-align: center; color: white; margin-top: 0px; margin-bottom: 25px;'>Add New Transaction</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1: selected_date = st.date_input("Date", value=date(2026, 3, 25))
            with col2: ticker = st.text_input("Ticker", value="BTC").upper().strip()
            
            col3, col4 = st.columns(2)
            with col3: usdc = st.number_input("USDC Amount", value=15.0, step=0.01)
            with col4: amount = st.number_input("Coin Amount", value=0.1, step=0.000001, format="%.8f")
            
            tx_type = st.radio("Type", ["Buy", "Sell"], horizontal=True, label_visibility="collapsed")
            
            submitted = st.form_submit_button("Submit Transaction")
                
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

                with st.container(border=True):
                    st.markdown("<div class='tx-row-inline'></div>", unsafe_allow_html=True)
                    col_left, col_mid, col_right = st.columns([1.2, 4, 1.5])
                    
                    with col_left:
                        st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 14px; margin-top: 6px;">
                                <img src="{logo_url}" class="mobile-logo" width="42" height="42" style="border-radius: 50%; object-fit: contain;" onerror="this.src='https://via.placeholder.com/42/1e2a44/ffffff?text={r['Ticker'][0]}';">
                                <div style="line-height: 1.2;">
                                    <div class="mobile-tx-ticker" style="font-weight: 700; font-size: 1.15rem; color: #ffffff;">{r['Ticker']}</div>
                                    <div class="mobile-tx-sub" style="font-size: 0.85rem; color: #94a3b8;">{date_str}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col_mid:
                        st.markdown(f"""
                            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px; margin-top: 6px;">
                                <div class="mobile-tx-amount" style="font-weight: 700; font-size: 1.15rem; color: {color};">{sign}{amount_formatted} {r['Ticker']}</div>
                                <div class="mobile-tx-sub" style="font-size: 0.85rem; color: #cbd5e1;">{action_text}: {invested_formatted}</div>
                                <div class="mobile-tx-sub" style="font-size: 0.75rem; color: #64748b;">@ ${price_formatted}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    with col_right:
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.button("✏️", key=f"edit_btn_{orig_idx}", help="Edit Transaction"):
                                if st.session_state.get('edit_crypto_row') == orig_idx:
                                    st.session_state['edit_crypto_row'] = None
                                else:
                                    st.session_state['edit_crypto_row'] = orig_idx
                                st.rerun()
                                
                        with btn_c2:
                            if st.button("🗑️", key=f"del_btn_{orig_idx}", help="Delete Transaction"):
                                st.session_state.crypto_df = st.session_state.crypto_df.drop(orig_idx).reset_index(drop=True)
                                save_crypto(st.session_state.crypto_df)
                                st.session_state.crypto_table_version += 1
                                st.session_state.ui_version += 1
                                if st.session_state.get('edit_crypto_row') == orig_idx:
                                    st.session_state['edit_crypto_row'] = None
                                st.success("✅ Transaction deleted!")
                                st.rerun()

                # 3. ROLL OUT EDIT FORM Directly Below Selected Transaction
                if st.session_state.get('edit_crypto_row') == orig_idx:
                    with st.container():
                        st.markdown("<div class='edit-rollout-container'>", unsafe_allow_html=True)
                        with st.form(f"edit_crypto_form_{orig_idx}", border=False):
                            st.markdown("<div class='form-compact'></div><h4 style='color: #00ff9d; margin-top: 0px; margin-bottom: 15px;'>✏️ Edit Row Details</h4>", unsafe_allow_html=True)
                            
                            e_col1, e_col2 = st.columns(2)
                            with e_col1: new_date = st.date_input("Date", value=datetime(1899, 12, 30) + timedelta(days=int(r['Datum'])))
                            with e_col2: new_ticker = st.text_input("Ticker", value=r['Ticker']).upper().strip()
                            
                            e_col3, e_col4 = st.columns(2)
                            with e_col3: new_usdc = st.number_input("USDC Amount", value=float(abs(r['USDC'])), step=0.01)
                            with e_col4: new_amount = st.number_input("Coin Amount", value=float(abs(r['Amount'])), step=0.000001, format="%.8f")
                            
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
                        st.markdown("</div>", unsafe_allow_html=True)

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
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin-bottom:30px;">
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
