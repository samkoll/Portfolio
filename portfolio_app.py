import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import time
import requests
import json
from pathlib import Path
import hashlib
import random
from concurrent.futures import ThreadPoolExecutor
import streamlit.components.v1 as components

# ====================== CONFIG ======================
st.set_page_config(page_title="Portfolio", layout="wide", page_icon="📊")

# ====================== SVG ICONS ======================
DASHBOARD_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
CRYPTO_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M14.5 8.5L9.5 13.5"/><path d="M9.5 8.5L14.5 13.5"/></svg>'
FIAT_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#00ff9d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h12"/><path d="M6 12h12"/><path d="M6 16h12"/></svg>'
EYE_CLOSED = '<svg class="eye-closed" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>'
EYE_OPEN = '<svg class="eye-open" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
EXTERNAL_LINK_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
TV_ICON = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="14" viewBox="0 0 28 21" fill="currentColor"><path d="M12 21H8V3h4v18zm1.5-6h3.5l3.5-4.5V21h-7v-6zM28 21h-4l-6.5-9L21 6l7 10v5z"/></svg>'

# ====================== SESSION STATE INITIALIZATION ======================
if 'crypto_df' not in st.session_state: st.session_state.crypto_df = pd.DataFrame()
if 'fiat_df' not in st.session_state: st.session_state.fiat_df = pd.DataFrame()
if 'crypto_table_version' not in st.session_state: st.session_state.crypto_table_version = 0
if 'fiat_table_version' not in st.session_state: st.session_state.fiat_table_version = 0
if 'ui_version' not in st.session_state: st.session_state.ui_version = 0
if 'last_known_prices' not in st.session_state: st.session_state.last_known_prices = {"USDC": 1.0}
if 'refresh_key' not in st.session_state: st.session_state.refresh_key = random.randint(100000, 999999)
if 'portfolio_cache' not in st.session_state: st.session_state.portfolio_cache = {}

def glossy_header(title: str, icon_svg: str):
    html = f'<div class="glossy-header">{icon_svg}<span style="margin-left:12px;">{title}</span></div>'
    st.markdown(html, unsafe_allow_html=True)

# ====================== TRUE SPA CAROUSEL ARCHITECTURE ======================
# This hides the sidebar and forces the 3 main st.containers to align horizontally
st.markdown("""
<style>
/* Hide Sidebar & Header */
[data-testid="stSidebar"], [data-testid="collapsedControl"], header[data-testid="stHeader"], footer { display: none !important; }

html, body, .stApp {
    overflow: hidden !important; 
    background: linear-gradient(180deg, #0f1724 0%, #0a0f1c 100%) !important;
}
div[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100vw !important;
    overflow: hidden !important;
}

/* Transform Streamlit's Main Block into a Horizontal Drag Carousel */
div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    scroll-snap-type: x mandatory !important;
    scroll-behavior: smooth !important;
    width: 100vw !important;
    height: 100vh !important;
    -webkit-overflow-scrolling: touch !important;
    scrollbar-width: none; 
}
div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"]::-webkit-scrollbar { display: none; }

/* The 3 Individual Pages (Containers) */
div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    min-width: 100vw !important;
    max-width: 100vw !important;
    flex: 0 0 100vw !important;
    height: 100vh !important;
    scroll-snap-align: start !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 20px 14px 120px 14px !important; /* Bottom padding prevents content from hiding behind floating nav */
    box-sizing: border-box !important;
}
@media (min-width: 1200px) {
    div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] { padding-left: 24px !important; padding-right: 24px !important; }
}

/* FLOATING PILL BOTTOM NAVIGATION BAR */
.bottom-nav-pill {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 450px;
    height: 65px;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border-radius: 35px;
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    z-index: 999999;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.nav-item {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #64748b; font-size: 11px; font-weight: 600; cursor: pointer; flex: 1; height: 100%; transition: color 0.3s ease;
    -webkit-tap-highlight-color: transparent;
}
.nav-item.active { color: #00ff9d; }
.nav-item svg { width: 22px; height: 22px; margin-bottom: 4px; stroke: currentColor; fill: none; transition: transform 0.2s ease; }
.nav-item.active svg { transform: translateY(-2px); filter: drop-shadow(0 0 4px rgba(0,255,157,0.4)); }

/* Global UI Elements */
.dashboard-wrapper { position: relative; z-index: 10; }
.glossy-header-label { cursor: pointer; display: block; position: relative; z-index: 3; -webkit-tap-highlight-color: transparent; }
.home-header { margin-bottom: 0 !important; padding-bottom: 30px !important; }
.pull-indicator { position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%); color: #64748b; opacity: 0.8; transition: color 0.3s ease; }
.pull-indicator .eye-open { display: none; }
.pull-indicator .eye-closed { display: block; }
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator .eye-open { display: block; }
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator .eye-closed { display: none; }
.dashboard-toggle:checked ~ .dashboard-wrapper .glossy-header-label .pull-indicator { color: #ffffff; }

.stats-layer { position: relative; z-index: 1; margin-top: -60px !important; transition: margin-top 0.4s cubic-bezier(0.4, 0, 0.2, 1); margin-bottom: 24px; }
.dashboard-toggle:checked ~ .dashboard-wrapper .stats-layer { margin-top: 14px !important; }
.stats-layer-inner { display: grid !important; grid-template-columns: repeat(3, 1fr) !important; gap: 14px; width: 100%; }
.dash-value { font-size: clamp(14px, 2.5vw, 24px) !important; font-weight: 700; line-height: 1.05; color: #ffffff; position: absolute; top: 20px; left: 0; width: 100%; text-align: center; margin: 0; transition: opacity 0.3s ease; padding: 0 4px; box-sizing: border-box; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dashboard-toggle:not(:checked) ~ .dashboard-wrapper .stats-layer .dash-value { opacity: 0; pointer-events: none; }
.dash-label { font-size: 11px !important; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #94a3b8; line-height: 1.2; position: absolute; bottom: 8px; left: 0; width: 100%; text-align: center; }

.glossy-header { position: relative; overflow: hidden; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid rgba(255,255,255,0.05); border-radius: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s ease, border-color 0.4s ease; padding: 32px 24px; min-height: 130px; font-size: 29px; font-weight: 700; letter-spacing: 1.5px; line-height: 1.1; display: flex; align-items: center; justify-content: center; gap: 16px; width: 100% !important; margin-bottom: 38px; }
.glossy-box { position: relative; overflow: hidden; background: linear-gradient(180deg, #162032 0%, #0f172a 100%); border: 1px solid rgba(255,255,255,0.05); border-radius: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); padding: 28px 30px; text-align: center; flex: 1; min-width: 220px; display: flex; flex-direction: column; justify-content: center; }
.glossy-box:not(.swapped) > div:first-child { font-size: 12px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; color: #94a3b8; margin-bottom: 6px; line-height: 1.2; }
.glossy-box:not(.swapped) > div:last-child { font-size: 27px; font-weight: 700; line-height: 1.05; color: #ffffff; }
.glossy-box.swapped { min-width: 0 !important; height: 80px !important; min-height: 80px !important; max-height: 80px !important; padding: 0; display: block; }

/* Subdued and Smaller USDC Banner */
.usdc-banner { position: relative; overflow: hidden; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(39, 117, 202, 0.2); border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); padding: 10px 20px; width: 90%; max-width: 400px; margin: -15px auto 12px auto !important; display: flex; align-items: center; justify-content: space-between; }
.usdc-banner-left { display: flex; align-items: center; gap: 12px; }
.usdc-banner-left img { width: 28px; height: 28px; border-radius: 50%; object-fit: contain; opacity: 0.85; }
.usdc-banner-title { font-size: 1.05rem; font-weight: 600; color: #e2e8f0; display: flex; align-items: center; gap: 8px; }
.usdc-banner-subtitle { font-size: 0.75rem; font-weight: 500; color: #64748b; }
.usdc-banner-amount { font-size: 1.2rem; font-weight: 600; color: #e2e8f0; }

/* Privacy Mode */
.dashboard-toggle:not(:checked) ~ .usdc-banner .usdc-banner-amount { font-size: 0 !important; }
.dashboard-toggle:not(:checked) ~ .usdc-banner .usdc-banner-amount::after { content: '***'; font-size: 1.2rem; color: #e2e8f0; }

button[aria-label="Step Up"], button[aria-label="Step Down"], button[data-testid="stNumberInputStepUp"], button[data-testid="stNumberInputStepDown"] { display: none !important; }
input[type="number"]::-webkit-inner-spin-button, input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
input[type="number"] { -moz-appearance: textfield; }

/* Transaction Row Styling */
div[data-testid="stForm"]:has(.add-tx-card) { background: #0f172a !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 16px !important; padding: 24px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; margin-bottom: 24px !important; }
div[data-testid="stForm"]:has(.add-tx-card) label { font-size: 0.85rem !important; color: #94a3b8 !important; padding-bottom: 2px !important; }
div[data-testid="stForm"]:has(.add-tx-card) .stTextInput input, div[data-testid="stForm"]:has(.add-tx-card) .stNumberInput input, div[data-testid="stForm"]:has(.add-tx-card) .stDateInput input { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #fff !important; border-radius: 8px !important; margin-bottom: 0px !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) { display: flex !important; gap: 12px !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) { display: flex !important; flex-direction: row !important; justify-content: space-between !important; align-items: center !important; margin-top: 12px !important; gap: 12px !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"]:nth-child(1) { flex: 0 0 auto !important; width: auto !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"]:nth-child(2) { flex: 1 1 auto !important; width: auto !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] { background: rgba(0,0,0,0.3) !important; padding: 6px !important; border-radius: 12px !important; display: flex !important; flex-direction: row !important; gap: 8px !important; align-items: center !important; margin: 0 !important; height: 48px !important; border: 1px solid rgba(255,255,255,0.05) !important; min-width: 200px !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label { margin: 0 !important; cursor: pointer !important; padding: 0 !important; border-radius: 8px !important; border: 1px solid transparent !important; transition: all 0.3s ease !important; background: transparent !important; flex: 1 !important; display: flex !important; justify-content: center !important; align-items: center !important; height: 100% !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:hover { background: rgba(255,255,255,0.05) !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label > div:first-child { display: none !important; } 
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label p { font-weight: bold !important; font-size: 1.05rem !important; color: #94a3b8 !important; margin: 0 !important; padding: 0 !important; white-space: nowrap !important; line-height: 1 !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):first-child, div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:first-child { background: rgba(0, 255, 157, 0.15) !important; border-color: #00ff9d !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):first-child p, div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:first-child p { color: #00ff9d !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):last-child, div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:last-child { background: rgba(255, 77, 77, 0.15) !important; border-color: #ff4d4d !important; }
div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label:has(input:checked):last-child p, div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] label[aria-checked="true"]:last-child p { color: #ff4d4d !important; }
div[data-testid="stForm"]:has(.add-tx-card) .stButton { display: flex !important; justify-content: flex-end !important; align-items: center !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }
div[data-testid="stForm"]:has(.add-tx-card) .stButton > button { background: #1e2a44 !important; color: #e0e0e0 !important; padding: 0 24px !important; border-radius: 10px !important; font-size: 1.05rem !important; font-weight: 700 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.25) !important; transition: all 0.3s ease !important; border: none !important; margin: 0 !important; width: auto !important; height: 48px !important; min-height: 48px !important; }
div[data-testid="stForm"]:has(.add-tx-card) .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(255, 255, 255, 0.2) !important; color: white !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) { background: #0f172a !important; border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 12px !important; padding: 12px 16px !important; margin-bottom: 12px !important; position: relative; z-index: 2; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div { padding: 0 !important; } 
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button { background: rgba(255,255,255,0.05) !important; border-radius: 8px !important; border: none !important; height: 40px !important; width: 40px !important; display: flex !important; align-items: center !important; justify-content: center !important; padding: 0 !important; margin: 0 auto !important; font-size: 1.2rem !important; transition: all 0.2s !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button:hover { background: rgba(255,255,255,0.15) !important; transform: scale(1.05) !important; }
@keyframes rollDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
div[data-testid="stForm"]:has(.edit-rollout) { animation: rollDown 0.3s ease forwards !important; background: rgba(0,0,0,0.2) !important; border-left: 3px solid #00ff9d !important; border-radius: 0 0 12px 12px !important; border-top: none !important; border-right: none !important; border-bottom: none !important; padding: 16px !important; margin-top: -24px !important; margin-bottom: 20px !important; position: relative; z-index: 1; box-shadow: inset 0 4px 10px rgba(0,0,0,0.15) !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) { border-color: rgba(255, 77, 77, 0.3) !important; background: rgba(15, 23, 42, 0.95) !important; border-radius: 12px !important; padding: 16px !important; text-align: center !important; margin-bottom: 12px !important; box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) .stButton > button { border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s !important; width: 100% !important; margin-top: 8px !important; padding: 6px 12px !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(1) .stButton > button { background: rgba(255, 77, 77, 0.1) !important; color: #ff4d4d !important; border: 1px solid rgba(255, 77, 77, 0.3) !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(1) .stButton > button:hover { background: #ff4d4d !important; color: white !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(2) .stButton > button { background: rgba(255, 255, 255, 0.05) !important; color: #cbd5e1 !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.del-warn) div[data-testid="column"]:nth-child(2) .stButton > button:hover { background: rgba(255, 255, 255, 0.15) !important; color: white !important; }

/* Expanded Chart CSS Jailbreak */
.stApp.chart-expanded-mode div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"] {
    overflow: visible !important;
    scroll-snap-type: none !important;
}
.stApp.chart-expanded-mode div[data-testid="stMainBlockContainer"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    overflow: visible !important;
    transform: none !important;
}

@media (max-width: 768px) {
    .glossy-header { min-height: 90px; font-size: 22px; padding: 20px 16px; margin-bottom: 24px; margin-top: 20px; }
    .stats-layer-inner { gap: 6px !important; }
    .dash-value { font-size: clamp(11px, 3.5vw, 15px) !important; top: 24px !important; } 
    .dash-label { font-size: clamp(8px, 2.5vw, 10px) !important; bottom: 8px !important; white-space: nowrap !important; letter-spacing: 0.5px !important; }
    .usdc-banner { padding: 8px 14px; width: 92%; margin-bottom: 24px !important; }
    .usdc-banner-amount { font-size: 1.1rem; }
    
    div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 12px !important; }
    div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(4)) > div[data-testid="column"] { min-width: calc(50% - 12px) !important; width: calc(50% - 12px) !important; flex: 1 1 calc(50% - 12px) !important; }
    div[data-testid="stForm"]:has(.add-tx-card) input { padding: 6px !important; font-size: 0.95rem !important; }
    div[data-testid="stForm"]:has(.add-tx-card) div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(2):last-child) > div[data-testid="column"] { min-width: calc(50% - 12px) !important; width: calc(50% - 12px) !important; flex: 1 1 calc(50% - 12px) !important; }
    div[data-testid="stForm"]:has(.add-tx-card) div[role="radiogroup"] { min-width: 0 !important; width: 100% !important; }
    div[data-testid="stForm"]:has(.add-tx-card) .stButton { display: flex !important; justify-content: flex-end !important; width: 100% !important; }
    div[data-testid="stForm"]:has(.add-tx-card) .stButton > button { width: 100% !important; max-width: 120px !important; padding: 0 16px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; overflow: hidden !important; gap: 2px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="column"] { min-width: 0 !important; padding: 0 !important; width: auto !important; flex-shrink: 1 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) { flex: 0 0 35px !important; width: 35px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) { flex: 1 1 auto !important; overflow: hidden !important; text-align: left; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) { flex: 1.5 1 auto !important; overflow: hidden !important; text-align: center; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(4) { flex: 0 0 36px !important; width: 36px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) > div > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(5) { flex: 0 0 36px !important; width: 36px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.tx-row) div[data-testid="stButton"] button { width: 30px !important; height: 30px !important; font-size: 0.9rem !important; margin: 0 auto !important; }
    .mobile-logo { width: 32px !important; height: 32px !important; margin-top: 0 !important; }
    .mobile-tx-ticker { font-size: 0.95rem !important; margin-left: 2px !important;}
    .mobile-tx-amount { font-size: 0.95rem !important; white-space: nowrap !important; }
    .mobile-tx-sub { font-size: 0.7rem !important; white-space: nowrap !important; margin-left: 2px !important;}
}
</style>
""", unsafe_allow_html=True)

# ====================== DATA PREPARATION ENGINE ======================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
CRYPTO_JSON = DATA_DIR / "crypto_transactions.json"
FIAT_JSON = DATA_DIR / "fiat_transactions.json"

def format_datum(datum_val):
    if pd.isna(datum_val) or datum_val == "": return ""
    try: return (datetime(1899, 12, 30) + timedelta(days=int(float(datum_val)))).strftime("%d.%m.%Y")
    except: return str(datum_val)

def date_to_excel_serial(selected_date: date) -> int: return (selected_date - datetime(1899, 12, 30).date()).days
def parse_excel_date(x):
    try: return (datetime(1899, 12, 30) + timedelta(days=int(float(x)))).date()
    except: return datetime.now().date()

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
    ])

def get_initial_fiat_df():
    return pd.DataFrame([
        {"Datum": 46098, "CZK": 1010.16, "EUR": 40.0, "Fee": 1.0, "CZK/EUR": 25.254, "USDC": 44.67, "NI": "CZK", "GG": "", "ER": "8972.72"},
        {"Datum": 46098, "CZK": 3156.76, "EUR": 125.0, "Fee": 1.0, "CZK/EUR": 25.25408, "USDC": 142.03, "NI": "USDC", "GG": "", "ER": "402.308"},
        {"Datum": 46098, "CZK": 4174.67, "EUR": 165.0, "Fee": 1.0, "CZK/EUR": 25.3010303, "USDC": 188.188, "NI": "EUR", "GG": "", "ER": "355"},
        {"Datum": 46099, "CZK": 631.13, "EUR": 25.0, "Fee": 1.0, "CZK/EUR": 25.2452, "USDC": 27.42, "NI": "FEEs", "GG": "4", "ER": "101.0543103"},
    ])

def load_or_init_crypto():
    if CRYPTO_JSON.exists(): return pd.read_json(CRYPTO_JSON)
    df = get_initial_crypto_df(); save_crypto(df); return df

def load_or_init_fiat():
    if FIAT_JSON.exists(): return pd.read_json(FIAT_JSON)
    df = get_initial_fiat_df(); save_fiat(df); return df

def save_crypto(df): df.to_json(CRYPTO_JSON, orient="records", indent=2)
def save_fiat(df): df.to_json(FIAT_JSON, orient="records", indent=2)

if st.session_state.crypto_df.empty: st.session_state.crypto_df = load_or_init_crypto()
if st.session_state.fiat_df.empty: st.session_state.fiat_df = load_or_init_fiat()

CRYPTOCOMPARE_SYMBOL_MAP = {'BTC': 'BTC', 'ETH': 'ETH', 'SOL': 'SOL', 'HBAR': 'HBAR', 'XRP': 'XRP', 'BNB': 'BNB', 'TRX': 'TRX', 'LINK': 'LINK', 'SUI': 'SUI', 'USDC': 'USDC'}

def get_with_retry(url: str, headers: dict, timeout: int = 12, retries: int = 4) -> dict | None:
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and data.get('Response') == 'Error':
                if 'rate limit' in data.get('Message', '').lower(): time.sleep(1.5 ** attempt); continue
                return None 
            return data
        except:
            if attempt == retries - 1: return None
            time.sleep(1.0 ** attempt)
    return None

def get_all_cryptocompare_prices(tickers: tuple, refresh_key=0):
    prices = {"USDC": 1.0}
    symbols = [CRYPTOCOMPARE_SYMBOL_MAP.get(t.upper()) for t in tickers if t.upper() != "USDC"]
    symbols = [s for s in symbols if s]
    if not symbols: return prices
    try:
        url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={','.join(symbols)}&tsyms=USD"
        data = get_with_retry(url, {"User-Agent": "Mozilla/5.0"})
        if data:
            for sym, price_data in data.items():
                if isinstance(price_data, dict) and "USD" in price_data:
                    ticker = next((k for k, v in CRYPTOCOMPARE_SYMBOL_MAP.items() if v == sym), None)
                    if ticker: prices[ticker] = float(price_data["USD"])
    except: pass
    return prices

def fetch_all_historical_data(coins_tuple: tuple, limit: int, refresh_key: int):
    prices_dict = {}
    def fetch_coin(coin):
        if coin.upper() == "USDC": return coin, {}
        sym = CRYPTOCOMPARE_SYMBOL_MAP.get(coin.upper(), coin.upper())
        data = get_with_retry(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={sym}&tsym=USD&limit={limit}", {"User-Agent": "Mozilla/5.0"})
        if data and 'Data' in data and 'Data' in data['Data']:
            return coin, {datetime.fromtimestamp(d['time']).date(): float(d['close']) for d in data['Data']['Data']}
        return coin, {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        for coin, hist in executor.map(fetch_coin, coins_tuple):
            if hist: prices_dict[coin] = hist
    return prices_dict

def get_base_prices(prices_dict, coins):
    base_prices = {}
    ytd_days = (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    for coin in coins:
        hist = prices_dict.get(coin, {})
        if not hist: continue
        prices = [hist[d] for d in sorted(hist.keys())]
        if not prices: continue
        def get_p(days_back): return prices[-(days_back + 1)] if len(prices) > days_back else prices[0]
        base_prices[coin] = {'7d': get_p(7), '30d': get_p(30), '90d': get_p(90), 'ytd': get_p(ytd_days)}
    return base_prices

def build_portfolio_history(crypto_df, fiat_df, last_prices, hist_dict):
    if crypto_df.empty and fiat_df.empty: return [], "", pd.DataFrame()
    fiat = fiat_df.copy()
    daily_fiat_usdc = fiat.groupby(fiat['Datum'].apply(parse_excel_date))['USDC'].sum() if not fiat.empty else pd.Series(dtype=float)
    crypto = crypto_df.copy()
    daily_crypto_spent = crypto[crypto['Ticker'].str.upper() != 'USDC'].groupby(crypto['Datum'].apply(parse_excel_date))['USDC'].sum() if not crypto.empty else pd.Series(dtype=float)

    all_dates = sorted(set(daily_fiat_usdc.index) | set(crypto['Datum'].apply(parse_excel_date).dropna() if not crypto.empty else []))
    if not all_dates: return [], "", pd.DataFrame()
    
    min_date = min(all_dates)
    today = datetime.now().date()
    if min_date > today: min_date = today
    date_range = pd.date_range(start=min_date, end=today).date

    cum_fiat_usdc = daily_fiat_usdc.reindex(date_range, fill_value=0).cumsum()
    cum_crypto_spent = daily_crypto_spent.reindex(date_range, fill_value=0).cumsum()
    cum_unused_usdc = cum_fiat_usdc - cum_crypto_spent

    if not crypto.empty:
        crypto_assets = crypto[crypto['Ticker'].str.upper() != 'USDC']
        if not crypto_assets.empty:
            crypto_assets['Date'] = crypto_assets['Datum'].apply(parse_excel_date)
            cum_holdings = crypto_assets.groupby(['Date', 'Ticker'])['Amount'].sum().unstack(fill_value=0).reindex(date_range, fill_value=0).fillna(0).cumsum()
            coins = crypto_assets['Ticker'].unique()
        else: cum_holdings, coins = pd.DataFrame(index=date_range), []
    else: cum_holdings, coins = pd.DataFrame(index=date_range), []

    prices_df = pd.DataFrame(hist_dict).reindex(date_range).ffill().bfill().fillna(0) if hist_dict else pd.DataFrame(index=date_range)
    for coin in tuple(sorted(set(coins) | {'BTC'})):
        live_p = last_prices.get(coin, 0.0)
        if live_p == 0.0 and coin == 'BTC': live_p = 65000.0 
        if coin not in prices_df.columns: prices_df[coin] = live_p
        prices_df.loc[date_range[-1], coin] = live_p
    
    pnl_df = pd.DataFrame()
    common_cols = cum_holdings.columns.intersection(prices_df.columns)
    
    if not crypto.empty and not crypto_assets.empty:
        invested_daily = crypto_assets.groupby(['Date', 'Ticker'])['USDC'].sum().unstack(fill_value=0).reindex(date_range, fill_value=0).fillna(0).cumsum()
        pnl_df = (cum_holdings[common_cols] * prices_df[common_cols]) - invested_daily[common_cols]

    daily_crypto_value = (cum_holdings[common_cols] * prices_df[common_cols]).sum(axis=1) if not common_cols.empty else pd.Series(0.0, index=date_range)
    total_portfolio_value = daily_crypto_value + cum_unused_usdc

    if 'BTC' in prices_df.columns and not prices_df['BTC'].empty and prices_df['BTC'].sum() > 0:
        btc_prices = prices_df['BTC'].replace(0, 1) 
        btc_benchmark_value = (daily_fiat_usdc / btc_prices).cumsum() * btc_prices
    else: btc_benchmark_value = pd.Series(0.0, index=date_range)

    history_data = []
    for d in date_range:
        history_data.append({'time': int(datetime.combine(d, datetime.min.time()).timestamp()) * 1000, 'value': float(total_portfolio_value.loc[d]), 'invested': float(cum_fiat_usdc.loc[d]), 'btc': float(btc_benchmark_value.loc[d])})
        
    allocation_series_js_list = []
    if not common_cols.empty:
        coin_values_last_day = {c: (cum_holdings[c].loc[date_range[-1]] * prices_df[c].loc[date_range[-1]]) for c in common_cols}
        for coin in sorted(coin_values_last_day.keys(), key=lambda c: coin_values_last_day[c], reverse=True):
            data_points = [f"[{int(datetime.combine(d, datetime.min.time()).timestamp()) * 1000}, {float((cum_holdings[coin] * prices_df[coin]).loc[d])}]" for d in date_range]
            allocation_series_js_list.append(f"{{ name: '{coin}', data: [{','.join(data_points)}], color: '{get_ticker_color(coin)}', marker: {{ enabled: false }} }}")

    return history_data, ",\n".join(allocation_series_js_list), pnl_df

def calculate_portfolio(crypto_df, fiat_df, live_prices, base_prices):
    if crypto_df.empty: return pd.DataFrame(columns=['Ticker','Holdings','USDC','AVG','Live','PnL','PnL %','Value','Price7d','Price30d','Price90d','PriceYTD']), 0, 0, 0
    crypto_df = crypto_df.copy()
    crypto_df['Ticker'] = crypto_df['Ticker'].astype(str).str.upper()
    usdc_holdings = pd.to_numeric(fiat_df['USDC'], errors='coerce').fillna(0).sum() - pd.to_numeric(crypto_df['USDC'], errors='coerce').fillna(0).sum()
        
    portfolio = []
    for ticker in [t for t in crypto_df['Ticker'].unique() if t != 'USDC']:
        sub = crypto_df[crypto_df['Ticker'] == ticker]
        total_holdings, total_invested = sub['Amount'].sum(), sub['USDC'].sum()
        live_price = live_prices.get(ticker, 0.0)
        pnl = (total_holdings * live_price) - total_invested
        bp = base_prices.get(ticker, {'7d': live_price, '30d': live_price, '90d': live_price, 'ytd': live_price})
        portfolio.append({'Ticker':ticker,'Holdings':total_holdings,'USDC':total_invested,'AVG':total_invested/total_holdings if total_holdings > 0 else 0,'Live':live_price,'PnL':pnl,'PnL %':(pnl/total_invested*100) if total_invested > 0 else 0,'Value':total_holdings*live_price, 'Price7d':bp['7d'], 'Price30d':bp['30d'], 'Price90d':bp['90d'], 'PriceYTD':bp['ytd']})
    
    portfolio.append({'Ticker':'USDC','Holdings':usdc_holdings,'USDC':usdc_holdings,'AVG':1.0,'Live':1.0,'PnL':0,'PnL %':0,'Value':usdc_holdings, 'Price7d':1.0, 'Price30d':1.0, 'Price90d':1.0, 'PriceYTD':1.0})
    df_port = pd.DataFrame(portfolio).sort_values(by='USDC', ascending=False).reset_index(drop=True)
    total_value, total_pnl = df_port['Value'].sum(), df_port['PnL'].sum()
    return df_port, total_value, total_pnl, (total_pnl / (total_value - total_pnl) * 100) if (total_value - total_pnl) != 0 else 0

def get_ticker_logo(t: str) -> str:
    known = {'USDC': 'https://assets.coingecko.com/coins/images/6319/small/USD_Coin_icon.png', 'BTC': 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png', 'ETH': 'https://assets.coingecko.com/coins/images/279/small/ethereum.png', 'SOL': 'https://assets.coingecko.com/coins/images/4128/small/Solana.png', 'HBAR': 'https://assets.coingecko.com/coins/images/3688/small/hbar.png', 'XRP': 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png', 'SUI': 'https://logo.svgcdn.com/token-branded/sui.svg', 'LINK': 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png', 'BNB': 'https://assets.coingecko.com/coins/images/825/small/binance-coin-logo.png', 'TRX': 'https://assets.coingecko.com/coins/images/1094/small/tron-logo.png'}
    return known.get(t.upper(), f"https://cryptologos.cc/logos/{t.lower()}-logo.png")

def get_ticker_color(t: str) -> str:
    known = {'USDC': '#2775ca', 'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9b59b6', 'HBAR': '#ffffff', 'XRP': '#ffffff', 'SUI': '#60a5fa', 'LINK': '#1e3a8a', 'BNB': '#f4c430', 'TRX': '#ff2d55'}
    c = known.get(t.upper(), f"#{hashlib.md5(t.encode()).hexdigest()[:6]}")
    return '#ffffff' if c == '#000000' else c

def get_chart_color(t: str) -> str:
    return {'BTC': '#f7931a', 'ETH': '#627eea', 'SOL': '#9b59b6', 'HBAR': '#00b4d8', 'XRP': '#1e3a8a', 'BNB': '#f4c430', 'TRX': '#ff2d55', 'LINK': '#2ecc71', 'SUI': '#60a5fa'}.get(t.upper(), '#00ff9d')

def format_money(val): return f"${float(val):,.2f}" if float(val) >= 0 else f"-${-float(val):,.2f}" if not pd.isna(val) else ""
def format_holdings(val, ticker=None): return f"{float(val):,.6f}".replace(',', '.') if ticker == "BTC" else f"{float(val):,.4f}".replace(',', '.') if not pd.isna(val) else ""
def format_percent(val): return f"{float(val):.2f}%" if not pd.isna(val) else ""
def format_price(val): return f"{float(val):.4f}" if abs(float(val)) < 1 else f"{float(val):,.2f}" if not pd.isna(val) else ""

# ================== ZERO-LATENCY CACHE ARCHITECTURE ==================
current_hash = f"{st.session_state.crypto_table_version}_{st.session_state.fiat_table_version}_{st.session_state.refresh_key}"

if st.session_state.portfolio_cache.get('hash') != current_hash:
    fetch_tickers = tuple(sorted(set([t.upper() for t in st.session_state.crypto_df['Ticker'] if t.upper() != 'USDC']) | {'BTC'}))
    live_prices = get_all_cryptocompare_prices(fetch_tickers, st.session_state.refresh_key)
    for t, p in live_prices.items():
        if p > 0: st.session_state.last_known_prices[t] = p
    for t in fetch_tickers:
        if t not in live_prices or live_prices[t] == 0: live_prices[t] = st.session_state.last_known_prices.get(t, 0)
            
    hist_dict = fetch_all_historical_data(fetch_tickers, 2000, st.session_state.refresh_key)
    base_prices = get_base_prices(hist_dict, fetch_tickers)

    df_port, total_value, total_pnl, total_pnl_pct = calculate_portfolio(st.session_state.crypto_df, st.session_state.fiat_df, live_prices, base_prices)
    history_data_raw, allocation_series_js, pnl_df = build_portfolio_history(st.session_state.crypto_df, st.session_state.fiat_df, live_prices, hist_dict)

    st.session_state.portfolio_cache = {
        'hash': current_hash, 'df_port': df_port, 'total_value': total_value, 'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct, 'history_data_raw': history_data_raw, 'allocation_series_js': allocation_series_js,
        'pnl_df': pnl_df, 'live_prices': live_prices, 'base_prices': base_prices
    }

vault = st.session_state.portfolio_cache
df_port, total_value, total_pnl, total_pnl_pct = vault['df_port'], vault['total_value'], vault['total_pnl'], vault['total_pnl_pct']
history_data_raw, allocation_series_js, pnl_df = vault['history_data_raw'], vault['allocation_series_js'], vault['pnl_df']

usdc_row = df_port[df_port['Ticker'] == 'USDC'].iloc[0] if not df_port[df_port['Ticker'] == 'USDC'].empty else None
usdc_holdings = usdc_row['Holdings'] if usdc_row is not None else 0

# ================== BOTTOM NAV & SCROLL ENGINE ==================
st.markdown(f"""
<div class="bottom-nav-pill">
    <div class="nav-item" id="nav-btn-0" onclick="window.parent.scrollToPage(0)">
        {DASHBOARD_ICON}<span>Overview</span>
    </div>
    <div class="nav-item" id="nav-btn-1" onclick="window.parent.scrollToPage(1)">
        {CRYPTO_ICON}<span>Crypto</span>
    </div>
    <div class="nav-item" id="nav-btn-2" onclick="window.parent.scrollToPage(2)">
        {FIAT_ICON}<span>Fiat</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Bulletproof pure JS injection using a hidden img onerror to completely bypass Streamlit markdown stripping
js_scroll_sync = """
<img src="dummy" style="display:none;" onerror="
if (!window.scrollEngineLoaded) {
    window.scrollEngineLoaded = true;
    const win = window.parent || window;
    const doc = win.document;

    let attachInt = setInterval(function() {
        const master = doc.querySelector('div[data-testid=&quot;stMainBlockContainer&quot;] > div > div[data-testid=&quot;stVerticalBlock&quot;]');
        if (master) {
            clearInterval(attachInt);

            const saved = win.localStorage.getItem('appScrollPos');
            if (saved) master.scrollLeft = parseInt(saved);

            master.addEventListener('scroll', function() {
                clearTimeout(win.scrollTimeout);
                win.scrollTimeout = setTimeout(function() {
                    win.localStorage.setItem('appScrollPos', master.scrollLeft);
                    const width = win.innerWidth;
                    const idx = Math.round(master.scrollLeft / width);
                    const items = doc.querySelectorAll('.nav-item');
                    items.forEach(function(el, i) {
                        if(i === idx) el.classList.add('active');
                        else el.classList.remove('active');
                    });
                }, 50);
            });

            win.scrollToPage = function(idx) {
                const width = win.innerWidth;
                master.scrollTo({ left: width * idx, behavior: 'smooth' });
            };
            
            const initWidth = win.innerWidth;
            const initIdx = Math.round((saved ? parseInt(saved) : 0) / initWidth);
            const items = doc.querySelectorAll('.nav-item');
            items.forEach(function(el, i) {
                if(i === initIdx) el.classList.add('active');
                else el.classList.remove('active');
            });
        }
    }, 100);
}
">
"""
st.markdown(js_scroll_sync, unsafe_allow_html=True)

# ================== PAGE 1: HOME ==================
with st.container():
    value_box_html = f"""
    <input type="checkbox" id="dash-toggle" class="dashboard-toggle" style="display:none;">
    <div class="dashboard-wrapper">
    <label for="dash-toggle" class="glossy-header-label">
    <div class="glossy-header home-header">
    {DASHBOARD_ICON}<span style="margin-left:12px;">Overview</span>
    <div class="pull-indicator">{EYE_CLOSED}{EYE_OPEN}</div>
    </div>
    </label>
    <div class="stats-layer"><div class="stats-layer-inner">
    <div class="glossy-box swapped"><div class="dash-value"><span id="dash-total-value">{format_money(total_value)}</span></div><div class="dash-label">Total Value</div></div>
    <div class="glossy-box swapped"><div class="dash-value"><span id="dash-pnl" style="color:{'#00ff9d' if total_pnl>=0 else '#ff4d4d'}">{"▲" if total_pnl>0 else "▼" if total_pnl<0 else ""} {format_money(abs(total_pnl))}</span></div><div class="dash-label">PnL</div></div>
    <div class="glossy-box swapped"><div class="dash-value"><span id="dash-pnl-pct" style="color:{'#00ff9d' if total_pnl_pct>=0 else '#ff4d4d'}">{"▲" if total_pnl_pct>0 else "▼" if total_pnl_pct<0 else ""} {abs(total_pnl_pct):.2f}%</span></div><div class="dash-label">PnL %</div></div>
    </div></div></div>
    """
    st.markdown(value_box_html, unsafe_allow_html=True)

    hist_val_js_list, hist_inv_js_list, hist_btc_js_list = [], [], []
    if history_data_raw:
        today_ts = int(datetime.combine(datetime.now().date(), datetime.min.time()).timestamp()) * 1000
        fiat_usdc_total = pd.to_numeric(st.session_state.fiat_df['USDC'], errors='coerce').fillna(0).sum()
        for idx, d in enumerate(history_data_raw):
            ts, val, inv, btc = d['time'], d['value'], d['invested'], d['btc']
            if idx == len(history_data_raw) - 1 and ts == today_ts: val, inv = float(total_value), float(fiat_usdc_total)
            hist_val_js_list.append(f"[{ts}, {val}]"); hist_inv_js_list.append(f"[{ts}, {inv}]"); hist_btc_js_list.append(f"[{ts}, {btc}]")
        hist_val_js = ",\n".join(hist_val_js_list); hist_inv_js = ",\n".join(hist_inv_js_list); hist_btc_js = ",\n".join(hist_btc_js_list)
    else: hist_val_js, hist_inv_js, hist_btc_js = "", "", ""

    pie_data_js = ",\n".join([f"{{ name: '{r['Ticker']}', y: {r['Value']}, color: '{get_ticker_color(r['Ticker'])}' }}" for _, r in df_port.iterrows() if r['Ticker'] != 'USDC' and pd.notna(r['Value']) and r['Value'] > 0])

    pnl_data_js_dict = {'all': '', '1y': '', '30d': '', '7d': '', '1d': ''}
    if not pnl_df.empty:
        pnl_df_active = pnl_df[[c for c in [t for t in df_port['Ticker'] if t != 'USDC'] if c in pnl_df.columns]] if [c for c in [t for t in df_port['Ticker'] if t != 'USDC'] if c in pnl_df.columns] else pnl_df
        def format_pnl_js(series): return ",\n".join([f"{{ name: '{t}', y: {v}, color: '{get_ticker_color(t)}99' }}" for t, v in series.dropna().sort_values(ascending=True).items()])
        pnl_all = pnl_df_active.iloc[-1]
        pnl_data_js_dict['all'] = format_pnl_js(pnl_all)
        pnl_data_js_dict['1d'] = format_pnl_js(pnl_all - pnl_df_active.iloc[-2 if len(pnl_df_active) >= 2 else 0])
        pnl_data_js_dict['7d'] = format_pnl_js(pnl_all - pnl_df_active.iloc[-8 if len(pnl_df_active) >= 8 else 0])
        pnl_data_js_dict['30d'] = format_pnl_js(pnl_all - pnl_df_active.iloc[-31 if len(pnl_df_active) >= 31 else 0])
        pnl_data_js_dict['1y'] = format_pnl_js(pnl_all - pnl_df_active.iloc[-365 if len(pnl_df_active) >= 365 else 0])

    df_iv = df_port[df_port['Ticker'] != 'USDC'].sort_values(by='Value', ascending=False)
    inv_val_categories_js = json.dumps([str(r['Ticker']) for _, r in df_iv.iterrows()])
    val_data_js = ",\n".join([f"{{ name: '{r['Ticker']}', y: {r['Value'] if pd.notna(r['Value']) else 0}, color: '{get_ticker_color(r['Ticker'])}99' }}" for _, r in df_iv.iterrows()])
    inv_data_js = ",\n".join([f"{{ name: '{r['Ticker']}', y: {float(r['USDC']) if pd.notna(r['USDC']) else 0.0}, color: '#64748b99' }}" for _, r in df_iv.iterrows()])
    roi_data_js = ",\n".join([f"{{ name: '{r['Ticker']}', y: {r['PnL %']}, color: '{get_ticker_color(r['Ticker'])}99' }}" for _, r in df_port[df_port['Ticker'] != 'USDC'].sort_values(by='PnL %', ascending=False).iterrows() if pd.notna(r['PnL %'])])
    daily_data_js = ",\n".join([f"{{ name: '{r['Ticker']}', y: 0, color: '#64748b99' }}" for _, r in df_port[df_port['Ticker'] != 'USDC'].iterrows()])

    # Perfectly un-minified HTML with rock-solid Python injection points
    charts_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script>
            window.pnlDataMap = {{
                'all': [{pnl_data_js_dict['all']}],
                '1y': [{pnl_data_js_dict['1y']}],
                '30d': [{pnl_data_js_dict['30d']}],
                '7d': [{pnl_data_js_dict['7d']}],
                '1d': [{pnl_data_js_dict['1d']}]
            }};
        </script>
        <script src="https://code.highcharts.com/stock/highstock.js"></script>
        <script src="https://code.highcharts.com/stock/highcharts-3d.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: system-ui, sans-serif; }}
            .charts-scroll-wrapper {{ width: 100%; overflow-y: hidden; overflow-x: auto; padding: 6px 0px 6px 0px; margin-bottom: 0px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scrollbar-width: none; -ms-overflow-style: none; }}
            .charts-scroll-wrapper::-webkit-scrollbar {{ display: none; }}
            .charts-flex {{ display: flex; flex-direction: row; flex-wrap: nowrap; gap: 24px; width: max-content; padding: 0 24px; }}
            .chart-placeholder {{ scroll-snap-align: center; }}
            .chart-placeholder[data-type="pie"] {{ width: 350px; flex: 0 0 350px; height: 340px; }}
            .chart-placeholder[data-type="history"] {{ width: 600px; flex: 0 0 600px; height: 340px; }}
            .chart-placeholder[data-type="pnl"] {{ width: 400px; flex: 0 0 400px; height: 340px; }}
            .chart-placeholder[data-type="roi"] {{ width: 400px; flex: 0 0 400px; height: 340px; }}
            .chart-placeholder[data-type="allocation"] {{ width: 600px; flex: 0 0 600px; height: 340px; }}
            .chart-placeholder[data-type="inv-val"] {{ width: 500px; flex: 0 0 500px; height: 340px; }}
            .chart-placeholder[data-type="daily"] {{ width: 400px; flex: 0 0 400px; height: 340px; }}
            .chart-box {{ width: 100%; height: 100%; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); touch-action: pan-x pan-y; will-change: transform; position: relative; display: flex; flex-direction: column; }}
            .chart-header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 16px 0 16px; width: 100%; box-sizing: border-box; }}
            .chart-title {{ color: #e2e8f0; font-size: 13px; font-weight: bold; white-space: nowrap; }}
            .chart-controls {{ display: flex; gap: 4px; }}
            .chart-controls button {{ background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8; border-radius: 4px; padding: 3px 8px; font-size: 10px; cursor: pointer; font-weight: bold; transition: all 0.2s; }}
            .chart-controls button.active {{ background: rgba(0, 255, 157, 0.15); color: #00ff9d; border-color: #00ff9d; }}
            .chart-body {{ flex: 1; width: 100%; position: relative; }}
            #chart-overlay {{ visibility: hidden; opacity: 0; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(10, 15, 28, 0.85); z-index: 1000; backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px); transition: opacity 0.4s ease, visibility 0.4s ease; }}
            #chart-overlay.active {{ visibility: visible; opacity: 1; }}
            .expanded-chart {{ background: rgba(15, 23, 42, 0.98) !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; box-shadow: 0 15px 50px rgba(0,0,0,0.9) !important; border-radius: 20px !important; }}
            @media (max-width: 768px) {{ .chart-placeholder {{ height: 320px !important; width: 90vw !important; flex: 0 0 90vw !important; }} .charts-flex {{ padding: 0 5vw; gap: 16px; }} .chart-controls button {{ padding: 3px 6px; font-size: 9px; }} }}
        </style>
    </head>
    <body>
        <div id="chart-overlay"></div>
        <div class="charts-scroll-wrapper" id="chartsScrollContainer">
            <div class="charts-flex">
                <div class="chart-placeholder" data-type="pie"><div id="pie-container" class="chart-box"></div></div>
                <div class="chart-placeholder" data-type="history"><div id="history-wrapper" class="chart-box"><div class="chart-header"><div class="chart-title">Historical Performance</div><div class="chart-controls hist-controls"><button class="active" data-range="all">All</button><button data-range="1w">1W</button><button data-range="1m">1M</button><button data-range="1y">1Y</button><button data-range="ytd">YTD</button></div></div><div id="history-container" class="chart-body"></div></div></div>
                <div class="chart-placeholder" data-type="pnl"><div id="pnl-wrapper" class="chart-box"><div class="chart-header"><div class="chart-title">Winners & Losers ($)</div><div class="chart-controls pnl-controls"><button class="active" data-range="all">All</button><button data-range="1d">Today</button><button data-range="7d">1W</button><button data-range="30d">1M</button><button data-range="1y">1Y</button></div></div><div id="pnl-container" class="chart-body"></div></div></div>
                <div class="chart-placeholder" data-type="roi"><div id="roi-wrapper" class="chart-box"><div class="chart-header"><div class="chart-title">ROI (%) by Asset</div></div><div id="roi-container" class="chart-body"></div></div></div>
                <div class="chart-placeholder" data-type="daily"><div id="daily-wrapper" class="chart-box"><div class="chart-header"><div class="chart-title">24h Market Movers (%)</div></div><div id="daily-container" class="chart-body"></div></div></div>
                <div class="chart-placeholder" data-type="allocation"><div id="allocation-container" class="chart-box"></div></div>
                <div class="chart-placeholder" data-type="inv-val"><div id="inv-val-container" class="chart-box"></div></div>
            </div>
        </div>
        <script>
            Highcharts.setOptions({{ global: {{ useUTC: false }} }});
            function formatMoneyStr(val) {{ return val < 0 ? '-$' + Highcharts.numberFormat(Math.abs(val), 2) : '$' + Highcharts.numberFormat(val, 2); }}
            function formatAxisMoneyStr(val) {{ return val < 0 ? '-$' + Highcharts.numberFormat(Math.abs(val), 0) : '$' + Highcharts.numberFormat(val, 0); }}
            
            try {{
                Highcharts.chart('pie-container', {{
                    chart: {{ type: 'pie', options3d: {{ enabled: true, alpha: 55, beta: 0 }}, backgroundColor: 'transparent', margin: [0, 0, 0, 0] }},
                    title: {{ text: 'Current Holdings', style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }}, align: 'left', x: 16, y: 24 }},
                    tooltip: {{ formatter: function() {{ const isPrivacy = document.body.classList.contains('privacy-mode'); if (isPrivacy) return '<b>' + this.point.name + '</b><br/>' + this.point.percentage.toFixed(1) + '%'; return '<b>' + this.point.name + '</b><br/>' + formatMoneyStr(this.point.y) + '<br/>' + this.point.percentage.toFixed(1) + '%'; }}, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderWidth: 1, borderColor: 'rgba(255,255,255,0.15)' }},
                    plotOptions: {{ pie: {{ allowPointSelect: true, cursor: 'pointer', depth: 40, innerSize: '40%', size: '65%', dataLabels: {{ enabled: true, format: '<b>{{point.name}}</b><br>{{point.percentage:.1f}}%', style: {{ color: '#e2e8f0', textOutline: 'none', fontSize: '10px', fontWeight: '600' }}, connectorColor: 'rgba(255,255,255,0.2)', distance: 10, padding: 0 }}, borderWidth: 0 }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'Holdings', data: [{pie_data_js}] }}]
                }});
            }} catch(e) {{ console.error('Pie fail:', e); }}
            
            try {{
                Highcharts.stockChart('history-container', {{
                    chart: {{ type: 'areaspline', backgroundColor: 'transparent', marginTop: 25, marginBottom: 35 }}, 
                    rangeSelector: {{ enabled: false }}, navigator: {{ enabled: false }}, scrollbar: {{ enabled: false }},
                    title: {{ text: null }},
                    legend: {{ enabled: true, itemStyle: {{ color: '#94a3b8', fontSize: '11px', fontWeight: 'normal' }}, itemHoverStyle: {{ color: '#ffffff' }}, verticalAlign: 'top', align: 'center', y: -10 }},
                    xAxis: {{ gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, minorGridLineWidth: 0 }},
                    yAxis: {{ opposite: false, title: {{ text: null }}, labels: {{ style: {{ color: '#94a3b8', fontSize: '10px' }}, align: 'right', formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : formatAxisMoneyStr(this.value); }} }}, gridLineColor: 'rgba(255,255,255,0.05)' }},
                    tooltip: {{ shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ let s = '<b style="font-size: 11px; color:#cbd5e1;">' + Highcharts.dateFormat('%b %e, %Y', this.x) + '</b>'; const isPrivacy = document.body.classList.contains('privacy-mode'); this.points.forEach(function(point) {{ let val = isPrivacy ? '***' : formatMoneyStr(point.y); s += '<br/>' + '<span style="color:'+point.series.color+'">\u25CF</span> ' + point.series.name + ': <b style="font-size: 13px;">' + val + '</b>'; }}); return s; }} }},
                    plotOptions: {{ areaspline: {{ fillOpacity: 0.3, lineWidth: 2 }} }},
                    credits: {{ enabled: false }},
                    series: [
                        {{ name: 'Portfolio Value', data: [{hist_val_js}], color: '#00ff9d', fillColor: {{ linearGradient: {{ x1: 0, y1: 0, x2: 0, y2: 1 }}, stops: [ [0, 'rgba(0, 255, 157, 0.5)'], [1, 'rgba(0, 255, 157, 0.0)'] ] }}, zIndex: 3 }}, 
                        {{ name: 'BTC Benchmark', type: 'line', data: [{hist_btc_js}], color: '#f7931a', lineWidth: 2, zIndex: 2 }}, 
                        {{ name: 'Net Invested', type: 'line', data: [{hist_inv_js}], color: '#64748b', dashStyle: 'Dash', lineWidth: 2, zIndex: 1 }}
                    ]
                }});
            }} catch(e) {{ console.error('History fail:', e); }}
            
            document.querySelectorAll('.hist-controls button').forEach(btn => {{
                btn.addEventListener('click', (e) => {{
                    e.stopPropagation(); document.querySelectorAll('.hist-controls button').forEach(b => b.classList.remove('active')); btn.classList.add('active');
                    const range = btn.getAttribute('data-range'); const chart = Highcharts.charts.find(c => c && c.renderTo.id === 'history-container');
                    if (chart) {{
                        const max = chart.xAxis[0].dataMax; const min = chart.xAxis[0].dataMin; const day = 24 * 3600 * 1000; let newMin = min;
                        if (range === 'all') {{ chart.xAxis[0].setExtremes(null, null, true, true); }}
                        else {{
                            if (range === '1w') newMin = max - 7 * day; else if (range === '1m') newMin = max - 30 * day; else if (range === '1y') newMin = max - 365 * day;
                            else if (range === 'ytd') {{ const d = new Date(max); newMin = new Date(d.getFullYear(), 0, 1).getTime(); }}
                            chart.xAxis[0].setExtremes(Math.max(min, newMin), max, true, true);
                        }}
                    }}
                }});
            }});

            try {{
                Highcharts.chart('pnl-container', {{
                    chart: {{ type: 'bar', backgroundColor: 'transparent', marginTop: 15, marginBottom: 25 }},
                    title: {{ text: null }},
                    xAxis: {{ type: 'category', labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, lineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ enabled: false }}, gridLineColor: 'rgba(255,255,255,0.05)', minPadding: 0.25, maxPadding: 0.25 }},
                    legend: {{ enabled: false }},
                    tooltip: {{ backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ const isPrivacy = document.body.classList.contains('privacy-mode'); const val = isPrivacy ? '***' : formatMoneyStr(this.y); return `<b>${{this.point.name}}</b><br/>PnL: <b style="color:${{this.point.color}}">${{val}}</b>`; }} }},
                    plotOptions: {{ bar: {{ borderRadius: 4, borderWidth: 0, pointPadding: 0.1, groupPadding: 0.1, maxPointWidth: 35, shadow: {{ color: 'rgba(0,0,0,0.3)', offsetX: 1, offsetY: 2, width: 4 }}, dataLabels: {{ enabled: true, inside: false, crop: false, overflow: 'allow', style: {{ color: '#fff', textOutline: '2px #0f172a', fontWeight: 'bold', fontSize: '11px' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : formatMoneyStr(this.y); }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'PnL', data: window.pnlDataMap['all'] }}]
                }});
            }} catch(e) {{ console.error('PnL fail:', e); }}
            
            document.querySelectorAll('.pnl-controls button').forEach(btn => {{
                btn.addEventListener('click', (e) => {{
                    e.stopPropagation(); document.querySelectorAll('.pnl-controls button').forEach(b => b.classList.remove('active')); btn.classList.add('active');
                    const range = btn.getAttribute('data-range'); const chart = Highcharts.charts.find(c => c && c.renderTo.id === 'pnl-container');
                    if (chart && window.pnlDataMap[range]) {{ chart.series[0].setData(window.pnlDataMap[range], true, {{ duration: 500 }}, true); }}
                }});
            }});
            
            try {{
                Highcharts.chart('roi-container', {{
                    chart: {{ type: 'bar', backgroundColor: 'transparent', marginTop: 15, marginBottom: 25 }},
                    title: {{ text: null }},
                    xAxis: {{ type: 'category', labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, lineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ enabled: false }}, gridLineColor: 'rgba(255,255,255,0.05)', minPadding: 0.25, maxPadding: 0.25 }},
                    legend: {{ enabled: false }},
                    tooltip: {{ backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ const val = Highcharts.numberFormat(this.y, 2) + '%'; return `<b>${{this.point.name}}</b><br/>ROI: <b style="color:${{this.point.color}}">${{val}}</b>`; }} }},
                    plotOptions: {{ bar: {{ borderRadius: 4, borderWidth: 0, pointPadding: 0.1, groupPadding: 0.1, maxPointWidth: 35, shadow: {{ color: 'rgba(0,0,0,0.3)', offsetX: 1, offsetY: 2, width: 4 }}, dataLabels: {{ enabled: true, inside: false, crop: false, overflow: 'allow', style: {{ color: '#fff', textOutline: '2px #0f172a', fontWeight: 'bold', fontSize: '11px' }}, formatter: function() {{ return Highcharts.numberFormat(this.y, 2) + '%'; }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: 'ROI %', data: [ {roi_data_js} ] }}]
                }});
            }} catch(e) {{ console.error('ROI fail:', e); }}
            
            try {{
                Highcharts.chart('daily-container', {{
                    chart: {{ type: 'bar', backgroundColor: 'transparent', marginTop: 15, marginBottom: 25 }},
                    title: {{ text: null }},
                    xAxis: {{ type: 'category', labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, lineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ enabled: false }}, gridLineColor: 'rgba(255,255,255,0.05)', minPadding: 0.25, maxPadding: 0.25 }},
                    legend: {{ enabled: false }},
                    tooltip: {{ backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ const val = Highcharts.numberFormat(Math.abs(this.y), 2) + '%'; const sign = this.y >= 0 ? '▲ ' : '▼ '; return `<b>${{this.point.name}}</b><br/>24h Change: <b style="color:${{this.point.color}}">${{sign}}${{val}}</b>`; }} }},
                    plotOptions: {{ bar: {{ borderRadius: 4, borderWidth: 0, pointPadding: 0.1, groupPadding: 0.1, maxPointWidth: 35, shadow: {{ color: 'rgba(0,0,0,0.3)', offsetX: 1, offsetY: 2, width: 4 }}, dataLabels: {{ enabled: true, inside: false, crop: false, overflow: 'allow', style: {{ color: '#fff', textOutline: '2px #0f172a', fontWeight: 'bold', fontSize: '11px' }}, formatter: function() {{ return (this.y >= 0 ? '+' : '') + Highcharts.numberFormat(this.y, 2) + '%'; }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{{ name: '24h Change', data: [ {daily_data_js} ] }}]
                }});
            }} catch(e) {{ console.error('Daily fail:', e); }}
            
            try {{
                Highcharts.chart('allocation-container', {{
                    chart: {{ type: 'areaspline', backgroundColor: 'transparent', marginTop: 45, marginBottom: 35 }},
                    title: {{ text: 'Asset Allocation', align: 'left', x: 8, y: 24, style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }} }},
                    xAxis: {{ type: 'datetime', labels: {{ style: {{ color: '#94a3b8', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0, minorGridLineWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ formatter: function() {{ return this.value + '%'; }}, style: {{ color: '#94a3b8', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', max: 100 }},
                    legend: {{ enabled: false }},
                    tooltip: {{ shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ let s = '<b style="font-size: 11px; color:#cbd5e1;">' + Highcharts.dateFormat('%b %e, %Y', this.x) + '</b>'; this.points.forEach(function(point) {{ s += '<br/>' + '<span style="color:'+point.series.color+'">\u25CF</span> ' + point.series.name + ': <b>' + Highcharts.numberFormat(point.percentage, 1) + '%</b>'; }}); return s; }} }},
                    plotOptions: {{ areaspline: {{ stacking: 'percent', fillOpacity: 0.25, lineWidth: 2, marker: {{ enabled: false, symbol: 'circle', radius: 2, states: {{ hover: {{ enabled: true }} }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [{allocation_series_js}]
                }});
            }} catch(e) {{ console.error('Alloc fail:', e); }}

            try {{
                Highcharts.chart('inv-val-container', {{
                    chart: {{ type: 'column', backgroundColor: 'transparent', marginTop: 45, marginBottom: 35 }},
                    title: {{ text: 'Invested vs Current Value', align: 'left', x: 8, y: 24, style: {{ color: '#e2e8f0', fontSize: '13px', fontWeight: 'bold' }} }},
                    xAxis: {{ type: 'category', categories: {inv_val_categories_js}, labels: {{ style: {{ color: '#94a3b8', fontWeight: 'bold', fontSize: '10px' }} }}, gridLineColor: 'rgba(255,255,255,0.05)', tickWidth: 0 }},
                    yAxis: {{ title: {{ text: null }}, labels: {{ style: {{ color: '#94a3b8', fontSize: '10px' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : formatAxisMoneyStr(this.value); }} }}, gridLineColor: 'rgba(255,255,255,0.05)', minPadding: 0.15, maxPadding: 0.15 }},
                    legend: {{ enabled: false }},
                    tooltip: {{ shared: true, backgroundColor: 'rgba(15, 23, 42, 0.95)', style: {{ color: '#fff' }}, borderColor: 'rgba(255,255,255,0.15)', formatter: function() {{ let s = '<b style="font-size: 13px;">' + this.points[0].key + '</b>'; const isPrivacy = document.body.classList.contains('privacy-mode'); this.points.forEach(function(point) {{ let val = isPrivacy ? '***' : formatMoneyStr(point.y); s += '<br/>' + '<span style="color:'+ point.color +'">\u25CF</span> ' + point.series.name + ': <b>' + val + '</b>'; }}); return s; }} }},
                    plotOptions: {{ column: {{ borderRadius: 4, borderWidth: 0, maxPointWidth: 40, dataLabels: {{ enabled: true, inside: false, crop: false, overflow: 'allow', style: {{ color: '#fff', textOutline: '2px #0f172a', fontWeight: 'bold', fontSize: '11px' }}, formatter: function() {{ return document.body.classList.contains('privacy-mode') ? '***' : formatMoneyStr(this.y); }} }} }} }},
                    credits: {{ enabled: false }},
                    series: [
                        {{ name: 'Invested', data: [{inv_data_js}] }},
                        {{ name: 'Current Value', data: [{val_data_js}] }}
                    ]
                }});
            }} catch(e) {{ console.error('InvVal fail:', e); }}
            
            // The ultimate pure javascript jailbreak to expand charts perfectly across Streamlit's bounds
            function toggleExpandChart(wrapperId) {{
                if (window.innerWidth > 768) return; 
                const el = document.getElementById(wrapperId);
                const overlay = document.getElementById('chart-overlay');
                
                let parentIframe = null;
                try {{
                    const iframes = window.parent.document.querySelectorAll('iframe');
                    for (let ifr of iframes) {{ if (ifr.contentWindow === window) parentIframe = ifr; }}
                }} catch(e) {{}}

                if (el.classList.contains('expanded-chart')) {{
                    // CLOSE MECHANIC
                    overlay.classList.remove('active');
                    el.classList.remove('expanded-chart');
                    el.style.cssText = ''; 
                    
                    document.querySelectorAll('.chart-box').forEach(c => c.style.opacity = '1');
                    
                    if (parentIframe) {{
                        parentIframe.style.position = '';
                        parentIframe.style.top = '';
                        parentIframe.style.left = '';
                        parentIframe.style.width = '';
                        parentIframe.style.height = '';
                        parentIframe.style.zIndex = '';
                        parentIframe.style.background = '';
                        window.parent.document.querySelector('.stApp').classList.remove('chart-expanded-mode');
                    }}
                }} else {{
                    // OPEN MECHANIC
                    document.querySelectorAll('.chart-box').forEach(c => {{
                        if (c.id !== wrapperId) c.style.opacity = '0';
                    }});
                    
                    overlay.classList.add('active'); 
                    el.classList.add('expanded-chart');
                    
                    el.style.position = 'fixed';
                    el.style.top = '10vh';
                    el.style.left = '5vw';
                    el.style.width = '90vw';
                    el.style.height = '75vh';
                    el.style.zIndex = '9999999';
                    el.style.transform = 'none';
                    el.style.transition = 'all 0.3s ease';
                    
                    if (parentIframe) {{
                        parentIframe.style.position = 'fixed';
                        parentIframe.style.top = '0';
                        parentIframe.style.left = '0';
                        parentIframe.style.width = '100vw';
                        parentIframe.style.height = '100vh';
                        parentIframe.style.zIndex = '999999';
                        parentIframe.style.background = 'rgba(10,15,28,0.98)';
                        window.parent.document.querySelector('.stApp').classList.add('chart-expanded-mode');
                    }}
                    
                    setTimeout(() => {{
                        const hc = Highcharts.charts.find(c => c && c.renderTo.id === el.id.replace('-wrapper', '-container'));
                        if (hc) hc.reflow();
                    }}, 350);
                }}
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
                        e.preventDefault(); e.stopPropagation();
                    }}
                    lastTap = currentTime;
                }});
            }}

            setupDoubleTap('pie-container'); setupDoubleTap('history-wrapper'); setupDoubleTap('pnl-wrapper'); 
            setupDoubleTap('roi-wrapper'); setupDoubleTap('daily-wrapper'); setupDoubleTap('allocation-container'); setupDoubleTap('inv-val-container');
            
            document.getElementById('chart-overlay').addEventListener('click', () => {{
                document.querySelectorAll('.expanded-chart').forEach(el => {{
                    if (el.classList.contains('expanded-chart')) toggleExpandChart(el.id);
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

            setInterval(() => {{
                try {{
                    const saved = localStorage.getItem('dashboardOpen');
                    const isPrivacy = (saved === 'false');
                    const currentlyPrivacy = document.body.classList.contains('privacy-mode');
                    if (isPrivacy !== currentlyPrivacy) {{
                        if (isPrivacy) document.body.classList.add('privacy-mode');
                        else document.body.classList.remove('privacy-mode');
                        ['history-container', 'pnl-container', 'roi-container', 'daily-container', 'inv-val-container'].forEach(id => {{
                            const hc = Highcharts.charts.find(c => c && c.renderTo.id === id);
                            if (hc && hc.yAxis && hc.yAxis[0]) {{ hc.yAxis[0].isDirty = true; hc.redraw(true); }}
                        }});
                    }}
                }} catch(e) {{}}
            }}, 200);
            
            // Constantly ensure charts auto-resize perfectly when you swipe back to the Home tab
            setInterval(() => {{
                Highcharts.charts.forEach(c => {{
                    if (c && c.renderTo && c.renderTo.clientWidth > 0) {{ c.reflow(); }}
                }});
            }}, 500);
        </script>
    </body>
    </html>
    """
    components.html(charts_html, height=355, scrolling=False)

    st.markdown("<br><br>", unsafe_allow_html=True) # spacing
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.refresh_key = random.randint(100000, 999999)
            st.rerun()
    with c2:
        data = {"crypto": json.loads(st.session_state.crypto_df.to_json(orient="records")), "fiat": json.loads(st.session_state.fiat_df.to_json(orient="records"))}
        st.download_button("💾 Backup JSON", json.dumps(data, indent=2), "portfolio_backup.json", "application/json", use_container_width=True)


# ================== PAGE 2: CRYPTO ==================
with st.container():
    glossy_header("Crypto Transactions", CRYPTO_ICON)
    
    with st.form("add_crypto", border=False):
        st.markdown("<div class='add-tx-card'></div><h3 style='text-align: center; color: white; margin-top: 0px; margin-bottom: 10px;'>New Transaction</h3>", unsafe_allow_html=True)
        
        r1c1, r1c2, r1c3, r1c4 = st.columns(4)
        with r1c1: selected_date = st.date_input("Date", value=date(2026, 3, 25))
        with r1c2: ticker = st.text_input("Ticker", value="BTC").upper().strip()
        with r1c3: usdc = st.number_input("USDC Amount", value=15.0, step=0.01)
        with r1c4: amount = st.number_input("Coin Amount", value=0.1, step=0.000001, format="%.8f")
        
        action_col1, action_col2 = st.columns(2)
        with action_col1: tx_type = st.radio("Type", ["Buy", "Sell"], horizontal=True, label_visibility="collapsed")
        with action_col2: submitted = st.form_submit_button("+ Add")
        
        if submitted and ticker:
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

    df_display = st.session_state.crypto_df.copy()
    df_display['orig_idx'] = df_display.index
    df_display = df_display.dropna(how='all').sort_values(by='Datum', ascending=False)

    st.markdown("<h4 style='color: white; margin-top: 20px; margin-bottom: 15px;'>Transaction History</h4>", unsafe_allow_html=True)
    
    with st.container(height=550, border=False):
        for i, r in df_display.iterrows():
            orig_idx = r['orig_idx']
            logo_url = get_ticker_logo(r['Ticker'])
            amount, usdc = r['Amount'], r['USDC']
            is_buy = amount >= 0
            abs_amount, abs_usdc = abs(amount), abs(usdc)
            price = abs_usdc / abs_amount if abs_amount > 0 else 0
            
            sign, color = ("+", "#00ff9d") if is_buy else ("-", "#ff4d4d")
            action_text = "Spent" if is_buy else "Received"
            invested_formatted, amount_formatted, price_formatted = format_money(abs_usdc), format_holdings(abs_amount, r['Ticker']), format_price(price)
            date_str = format_datum(r['Datum'])

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
                with st.container(border=True):
                    st.markdown("<div class='tx-row'></div>", unsafe_allow_html=True)
                    col_logo, col_ticker, col_vals, col_edit, col_del = st.columns([0.5, 2, 2.5, 0.5, 0.5])
                    with col_logo: st.markdown(f"<img src='{logo_url}' class='mobile-logo' style='width:42px;height:42px;border-radius:50%;object-fit:contain;margin-top:6px;' onerror=\"this.src='https://via.placeholder.com/42/1e2a44/ffffff?text={r['Ticker'][0]}';\">", unsafe_allow_html=True)
                    with col_ticker: st.markdown(f"""<div style="line-height: 1.2; margin-top: 6px; overflow: hidden; text-overflow: ellipsis;"><div class="mobile-tx-ticker" style="font-weight: 700; font-size: 1.15rem; color: #ffffff; white-space: nowrap;">{r['Ticker']}</div><div class="mobile-tx-sub" style="font-size: 0.85rem; color: #94a3b8; white-space: nowrap;">{date_str}</div></div>""", unsafe_allow_html=True)
                    with col_vals: st.markdown(f"""<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; margin-top: 6px;"><div class="mobile-tx-amount" style="font-weight: 700; font-size: 1.15rem; color: {color}; white-space: nowrap;">{sign}{amount_formatted}</div><div class="mobile-tx-sub" style="font-size: 0.85rem; color: #cbd5e1; white-space: nowrap;">{action_text}: {invested_formatted} @ ${price_formatted}</div></div>""", unsafe_allow_html=True)
                    with col_edit:
                        if st.button("✏️", key=f"edit_btn_{orig_idx}"):
                            st.session_state['edit_crypto_row'] = None if st.session_state.get('edit_crypto_row') == orig_idx else orig_idx
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_btn_{orig_idx}"):
                            st.session_state['confirm_delete_crypto'] = orig_idx
                            st.rerun()

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

# ================== PAGE 3: FIAT ==================
with st.container():
    total_czk = pd.to_numeric(st.session_state.fiat_df['CZK'], errors='coerce').fillna(0).sum()
    total_eur = pd.to_numeric(st.session_state.fiat_df['EUR'], errors='coerce').fillna(0).sum()
    total_usdc = pd.to_numeric(st.session_state.fiat_df['USDC'], errors='coerce').fillna(0).sum()
    fees_eur = pd.to_numeric(st.session_state.fiat_df['Fee'], errors='coerce').fillna(0).sum()
    fees_czk = (pd.to_numeric(st.session_state.fiat_df['Fee'], errors='coerce').fillna(0) * pd.to_numeric(st.session_state.fiat_df['CZK/EUR'], errors='coerce').fillna(0)).sum()

    glossy_header("Fiat Transactions", FIAT_ICON)

    summary_html = f"""
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;margin-bottom:30px;">
    <div class="glossy-box swapped"><div class="dash-value">{total_czk:,.2f}</div><div class="dash-label">Total CZK</div></div>
    <div class="glossy-box swapped"><div class="dash-value">{total_eur:,.2f}</div><div class="dash-label">Total EUR</div></div>
    <div class="glossy-box swapped"><div class="dash-value">{format_money(total_usdc)}</div><div class="dash-label">Total USDC</div></div>
    <div class="glossy-box swapped"><div class="dash-value" style="font-size:13px !important; white-space:normal;">{fees_eur:,.2f} EUR / {fees_czk:,.2f} CZK</div><div class="dash-label">Fees</div></div>
    </div>
    """
    st.markdown(summary_html, unsafe_allow_html=True)

    df_clean = st.session_state.fiat_df.dropna(how='all').reset_index(drop=True)
    with st.container(height=520, border=True):
        h = st.columns([1.0, 0.9, 0.9, 0.6, 0.9, 1.0, 0.4, 0.4])
        h[0].markdown("**Date**"); h[1].markdown("**CZK**"); h[2].markdown("**EUR**"); h[3].markdown("**Fee**"); h[4].markdown("**CZK/EUR**"); h[5].markdown("**USDC**"); h[6].markdown("**Del**"); h[7].markdown("**Edit**")
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
            with col_b: new_czk = st.number_input("CZK", value=float(row['CZK']), step=0.01)
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
        with col2: czk = st.number_input("CZK", value=1000.0, step=0.01)
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
