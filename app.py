import streamlit as st
import pandas as pd
import math
import urllib.parse

SHEET_URL   = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5QV1mK8Tg8SGbnDBs005Re6LVTB_f4ZYjo9Vd8AmFkeh0pNZf4dKOzV9adzDn6SRIRwlNwyPlBFL/pub?output=csv"  # גיליון Alcohol
MIXERS_URL  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5QV1mK8Tg8SGbnDBs005Re6LVTB_f4ZYjo9Vd8AmFkeh0pNZf4dKOzV9adzDn6SRIRwlNwyPlBFL/pub?gid=1444549454&single=true&output=csv"
# Analytics sheet — עדכן לURL של גיליון Analytics לאחר פרסום
ANALYTICS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5QV1mK8Tg8SGbnDBs005Re6LVTB_f4ZYjo9Vd8AmFkeh0pNZf4dKOzV9adzDn6SRIRwlNwyPlBFL/pub?output=csv"
ANALYTICS_WRITE_URL = "https://script.google.com/macros/s/AKfycbxz57lULFP6ClP-Gabdn71dlwVvI-YIF6LCx81guHLzM4efv8c8q_0yualR33bHxR1x8g/exec"

st.set_page_config(page_title="יועץ אלכוהול לחתונה", page_icon="🥂", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Heebo:wght@300;400;600;700;900&family=Dancing+Script:wght@600;700&display=swap');

:root {
  /* Wedding palette — ivory, champagne, rose gold, sage */
  --gold: #d4a96a;
  --gold2: #b8883e;
  --rose: #c9838a;
  --sage: #8aab8a;
  --blush: rgba(210,170,170,0.18);
  --bg: #0e0b0b;
  --bg2: rgba(255,248,245,0.04);
  --bg3: rgba(255,248,245,0.07);
  --glass: rgba(22,15,15,0.88);
  --border: rgba(212,169,106,0.25);
  --border-dim: rgba(255,240,230,0.08);
  --text: #f5ede3;
  --text-mid: #a8957e;
  --text-dim: #5c4e42;
  --green: #7ec8a0;
  --red: #e08080;
  --blue: #90c8d8;
  --purple: #c8a0c8;
  --r: 18px;
  --r-sm: 12px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: 'Heebo', sans-serif;
  direction: rtl;
  background: var(--bg);
  color: var(--text);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Background particles ── */
.bg-wrap {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 0; overflow: hidden;
}
.particle {
  position: absolute;
  border-radius: 50%;
  background: var(--gold);
  opacity: 0;
  animation: float linear infinite;
}
@keyframes float {
  0%   { transform: translateY(100vh) scale(0); opacity: 0; }
  10%  { opacity: 0.15; }
  90%  { opacity: 0.05; }
  100% { transform: translateY(-10vh) scale(1); opacity: 0; }
}

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 3rem 1rem 2rem;
  position: relative;
}
.hero-glow {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 350px;
  background: radial-gradient(ellipse, rgba(232,201,126,0.08) 0%, transparent 65%);
  pointer-events: none;
}
.hero-badge {
  display: inline-block;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: .3rem .9rem;
  font-size: .72rem;
  color: var(--gold);
  letter-spacing: .05em;
  text-transform: uppercase;
  margin-bottom: .8rem;
}
.hero-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2rem, 6vw, 2.8rem);
  font-weight: 900;
  color: var(--gold);
  line-height: 1.1;
  margin-bottom: .4rem;
}
.hero-sub {
  font-size: .88rem;
  color: var(--text-dim);
}

/* ── Glass card ── */
.glass {
  background: var(--glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-dim);
  border-radius: var(--r);
  padding: 1.5rem 1.6rem;
  margin-bottom: 1rem;
}
.glass-gold {
  background: var(--glass);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.5rem 1.6rem;
  margin-bottom: 1rem;
  box-shadow: 0 0 40px rgba(232,201,126,0.06);
}

/* ── Section title ── */
.sec-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem; font-weight: 700;
  color: var(--gold);
  margin-bottom: 1rem;
  display: flex; align-items: center; gap: .4rem;
}

/* ── Style pills ── */
.style-pills { display: flex; gap: .5rem; }
.style-pill {
  flex: 1; padding: .6rem .3rem;
  background: var(--bg2);
  border: 1.5px solid var(--border-dim);
  border-radius: var(--r-sm);
  color: var(--text-mid);
  font-family: 'Heebo', sans-serif;
  font-size: .8rem; font-weight: 700;
  cursor: pointer; text-align: center;
  transition: all .2s; line-height: 1.3;
}
.style-pill.active {
  background: rgba(232,201,126,0.1);
  border-color: var(--gold);
  color: var(--gold);
}

/* ── Level badge ── */
.badge {
  display: inline-block;
  padding: .15rem .55rem;
  border-radius: 20px;
  font-size: .68rem;
  font-weight: 700;
  letter-spacing: .03em;
}
.badge-basic   { background: rgba(74,222,128,.12);  color: #4ade80; border: 1px solid rgba(74,222,128,.25); }
.badge-premium { background: rgba(232,201,126,.12); color: var(--gold); border: 1px solid var(--border); }
.badge-special { background: rgba(192,132,252,.12); color: #c084fc; border: 1px solid rgba(192,132,252,.25); }

/* ── Result card ── */
.r-card {
  background: var(--glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-dim);
  border-radius: var(--r);
  padding: 1.3rem 1.4rem;
  margin-bottom: .9rem;
  transition: border-color .25s, box-shadow .25s;
  position: relative;
  overflow: hidden;
}
.r-card::before {
  content: '';
  position: absolute; top: 0; right: 0;
  width: 80px; height: 80px;
  background: radial-gradient(circle, rgba(232,201,126,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.r-card:hover { border-color: rgba(232,201,126,0.3); }

.r-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: .9rem; }
.r-left {}
.r-cat  { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; font-weight: 700; color: var(--gold); }
.r-brand{ font-size: .8rem; color: var(--text-mid); margin-top: .15rem; }
.r-right{ text-align: center; }
.r-num  {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem; font-weight: 900; color: #fff;
  line-height: 1;
}
.r-num-lbl { font-size: .62rem; color: var(--text-dim); }

.r-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .3rem 0; border-bottom: 1px solid var(--border-dim);
  font-size: .82rem; color: var(--text);
}
.r-row:last-child { border-bottom: none; }
.r-val { color: var(--gold); font-weight: 700; }

/* ── Edit panel ── */
.edit-pnl {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 1rem 1.1rem;
  margin-bottom: .8rem;
}

/* ── Mixer card ── */
.mix-wrap {
  background: var(--glass);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(96,200,245,.18);
  border-radius: var(--r);
  padding: 1.3rem 1.4rem;
  margin-bottom: .9rem;
}
.mix-hdr { font-size: .95rem; font-weight: 700; color: var(--blue); margin-bottom: .8rem; }
.mix-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: .5rem 0; border-bottom: 1px solid var(--border-dim);
  font-size: .83rem;
}
.mix-item:last-child { border-bottom: none; }
.mix-name { display: flex; align-items: center; gap: .4rem; }
.mix-qty  { color: var(--gold); font-weight: 700; font-size: .9rem; }
.mix-price{ color: var(--text-mid); font-size: .75rem; margin-top: .1rem; }
.venue-tag{
  display: inline-block;
  background: rgba(74,222,128,.1);
  border: 1px solid rgba(74,222,128,.2);
  border-radius: 20px;
  padding: .1rem .5rem;
  font-size: .68rem; color: #4ade80;
}

/* ── Special card ── */
.sp-card {
  background: linear-gradient(135deg, rgba(192,132,252,.08), rgba(192,132,252,.02));
  border: 1px solid rgba(192,132,252,.3);
  border-radius: var(--r);
  padding: 1.3rem 1.4rem;
  margin-bottom: .9rem;
}

/* ── Budget bar ── */
.budget-bar-wrap { margin: .5rem 0 .2rem; }
.budget-bar-bg {
  height: 6px; background: var(--bg3);
  border-radius: 3px; overflow: hidden;
}
.budget-bar-fill {
  height: 100%; border-radius: 3px;
  transition: width .6s ease;
}

/* ── Total box ── */
.total-wrap {
  background: linear-gradient(135deg, rgba(232,201,126,.09), rgba(196,124,58,.04));
  border: 2px solid var(--border);
  border-radius: var(--r);
  padding: 1.8rem 1.4rem;
  text-align: center;
  margin: 1.2rem 0;
  box-shadow: 0 0 60px rgba(232,201,126,.06);
  position: relative; overflow: hidden;
}
.total-wrap::after {
  content: '🥂';
  position: absolute; bottom: -10px; left: 50%;
  transform: translateX(-50%);
  font-size: 5rem; opacity: .04;
}
.total-main {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.4rem, 8vw, 3.2rem);
  font-weight: 900; color: var(--gold);
  line-height: 1;
}
.total-sub { color: var(--text-dim); font-size: .8rem; margin-top: .4rem; }

/* ── Info boxes ── */
.ibox { background: rgba(74,222,128,.06); border: 1px solid rgba(74,222,128,.15); border-radius: var(--r-sm); padding: .5rem .9rem; color: #a8efc0; font-size: .8rem; margin: .4rem 0; }
.wbox { background: rgba(248,113,113,.07); border: 1px solid rgba(248,113,113,.18); border-radius: var(--r-sm); padding: .5rem .9rem; color: #fca5a5; font-size: .8rem; margin: .4rem 0; }
.nbox { background: rgba(232,201,126,.07); border: 1px solid rgba(232,201,126,.18); border-radius: var(--r-sm); padding: .5rem .9rem; color: var(--gold); font-size: .8rem; margin: .4rem 0; text-align: center; }

/* ── Divider ── */
.div { height: 1px; background: linear-gradient(to right, transparent, var(--border), transparent); margin: 1.2rem 0; }
.sec { font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; color: var(--gold); margin: 1.3rem 0 .6rem; }

/* ── Share buttons ── */
.wa-btn  { display: flex; align-items: center; justify-content: center; gap: .5rem; background: #25D366; color: #fff; border: none; border-radius: var(--r); padding: .8rem; font-family: 'Heebo', sans-serif; font-weight: 800; font-size: .92rem; text-decoration: none; width: 100%; }
.mail-btn{ display: flex; align-items: center; justify-content: center; gap: .5rem; background: var(--bg2); color: var(--text); border: 1px solid var(--border-dim); border-radius: var(--r); padding: .8rem; font-family: 'Heebo', sans-serif; font-weight: 700; font-size: .88rem; text-decoration: none; width: 100%; }

/* ── Streamlit overrides ── */
.stButton > button {
  background: linear-gradient(135deg, var(--gold2), var(--gold)) !important;
  color: #07070d !important;
  font-family: 'Heebo', sans-serif !important;
  font-weight: 800 !important;
  border: none !important;
  border-radius: var(--r) !important;
  padding: .75rem 1.5rem !important;
  width: 100% !important;
  transition: all .2s !important;
  box-shadow: 0 4px 20px rgba(232,201,126,.15) !important;
  font-size: .95rem !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 26px rgba(232,201,126,.25) !important; }
.btn-ghost > button  { background: var(--bg3) !important; color: var(--text-mid) !important; border: 1px solid var(--border-dim) !important; box-shadow: none !important; font-size: .82rem !important; padding: .5rem !important; }
.btn-danger > button { background: rgba(248,113,113,.1) !important; color: #f87171 !important; border: 1px solid rgba(248,113,113,.22) !important; box-shadow: none !important; font-size: .82rem !important; padding: .5rem !important; }
.btn-add > button    { background: rgba(74,222,128,.09) !important; color: var(--green) !important; border: 1px solid rgba(74,222,128,.22) !important; box-shadow: none !important; font-size: .82rem !important; padding: .5rem !important; }
.btn-sp > button     { background: rgba(192,132,252,.09) !important; color: var(--purple) !important; border: 1px solid rgba(192,132,252,.22) !important; box-shadow: none !important; font-size: .82rem !important; padding: .5rem !important; }

/* Fix slider - prevent overflow */
[data-testid="stSlider"] {
  padding: 0 !important;
  overflow: hidden !important;
  max-width: 100% !important;
}
[data-testid="stSlider"] > div { max-width: 100% !important; }
[data-testid="column"] { padding: .1rem .15rem !important; }

/* Full overflow prevention */
html, body { overflow-x: hidden !important; }
section[data-testid="stMain"] > div { overflow-x: hidden !important; max-width: 100vw !important; }
.main .block-container {
  max-width: 640px !important;
  padding-left: .9rem !important;
  padding-right: .9rem !important;
  overflow-x: hidden !important;
  width: 100% !important;
}

/* ── Mobile first — 100% תאימות ── */
@media (max-width: 640px) {
  .main .block-container { padding-left: .6rem !important; padding-right: .6rem !important; }
  .hero-title  { font-size: 1.75rem !important; }
  .hero-sub    { font-size: .8rem !important; }
  .hero-badge  { font-size: .66rem !important; }
  .r-num       { font-size: 1.85rem !important; }
  .total-main  { font-size: 2rem !important; }
  .sec         { font-size: 1rem !important; }
  .glass, .glass-gold, .r-card, .mix-wrap, .sp-card, .edit-pnl {
    padding: .9rem .85rem !important;
    border-radius: 14px !important;
  }
  .r-row, .mix-item { font-size: .79rem !important; }
  .r-cat  { font-size: .98rem !important; }
  .r-brand{ font-size: .76rem !important; }
  .r-head { gap: .5rem !important; }
  /* Big tap targets */
  .stButton > button {
    min-height: 50px !important;
    font-size: .88rem !important;
    padding: .6rem .8rem !important;
  }
  .btn-ghost > button, .btn-danger > button,
  .btn-add > button, .btn-sp > button {
    min-height: 44px !important;
    font-size: .8rem !important;
  }
  /* number_input bigger */
  input[type="number"] { font-size: 1rem !important; padding: .5rem !important; }
  /* selectbox */
  .stSelectbox select { font-size: .9rem !important; }
  /* share buttons */
  .wa-btn, .mail-btn { font-size: .85rem !important; padding: .7rem !important; }
  /* columns on mobile */
  [data-testid="column"] { min-width: 0 !important; flex-shrink: 1 !important; }
  /* hide particles on mobile for perf */
  .bg-wrap { display: none !important; }
}

/* number_input arrows — bigger */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  opacity: 1 !important;
  height: 2.5em !important;
  cursor: pointer !important;
}

/* ── Wedding illustrations ── */
.wedding-bar-svg { text-align:center; padding: 1.5rem 0 .5rem; opacity:.85; }
.wedding-bar-svg svg { max-width: 280px; width: 90%; }

/* ── Confetti burst ── */
.confetti-wrap {
  position: fixed; top: 0; left: 0;
  width: 100vw; height: 100vh;
  pointer-events: none; z-index: 9999;
  overflow: hidden;
}
.confetti-piece {
  position: absolute; top: -10px;
  width: 8px; height: 8px;
  border-radius: 2px;
  animation: confettiFall linear forwards;
}
@keyframes confettiFall {
  0%   { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; }
  80%  { opacity: 1; }
  100% { transform: translateY(100vh) rotate(720deg) scale(.5); opacity: 0; }
}

/* ── Loading shimmer ── */
.loading-wrap {
  text-align: center; padding: 2rem 1rem;
}
.loading-msg {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.2rem; font-style: italic;
  color: var(--gold); opacity: .8;
  animation: pulse 1.5s ease-in-out infinite;
}
.loading-dots::after {
  content: '';
  animation: dots 1.5s steps(3, end) infinite;
}
@keyframes dots {
  0%   { content: ''; }
  33%  { content: '.'; }
  66%  { content: '..'; }
  100% { content: '...'; }
}
@keyframes pulse {
  0%,100% { opacity: .6; }
  50%      { opacity: 1; }
}

/* ── Bottom sheet ── */
.bottom-sheet-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  animation: fadeIn .2s ease;
}
.bottom-sheet {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: #1a1215;
  border-top: 1px solid var(--border);
  border-radius: 20px 20px 0 0;
  padding: 1.5rem 1.2rem 2rem;
  z-index: 1001;
  animation: slideUp .3s cubic-bezier(.34,1.56,.64,1);
  max-height: 80vh; overflow-y: auto;
}
.sheet-handle {
  width: 40px; height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin: 0 auto 1rem;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* ── Animated number ── */
.anim-num {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.4rem; font-weight: 900; color: #fff;
  line-height: 1; display: inline-block;
  animation: popIn .4s cubic-bezier(.34,1.56,.64,1) both;
}
@keyframes popIn {
  0%   { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>

<div class="bg-wrap">
  <!-- petals -->
  <div class="particle" style="width:3px;height:3px;left:10%;animation-duration:14s;animation-delay:0s;background:#d4a96a"></div>
  <div class="particle" style="width:2px;height:2px;left:28%;animation-duration:20s;animation-delay:2s;background:#c9838a"></div>
  <div class="particle" style="width:4px;height:4px;left:50%;animation-duration:16s;animation-delay:5s;background:#d4a96a"></div>
  <div class="particle" style="width:2px;height:2px;left:72%;animation-duration:22s;animation-delay:1s;background:#c9838a"></div>
  <div class="particle" style="width:3px;height:3px;left:88%;animation-duration:18s;animation-delay:8s;background:#8aab8a"></div>
  <div class="particle" style="width:2px;height:2px;left:40%;animation-duration:24s;animation-delay:12s;background:#d4a96a"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════
@st.cache_data(ttl=300)
def load_alcohol():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].str.strip()
        for col in ['price','volume_ml','popularity_score']:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace('₪','').str.replace(',','').str.strip(),
                    errors='coerce')
        if 'flavor_type' in df.columns:
            df['flavor_type'] = df['flavor_type'].str.lower().str.strip()
        else:
            df['flavor_type'] = 'regular'
            kw = ['Watermelon','Pineapple','Asai','Melon','Van Gogh','Cavalli']
            mask = df['brand'].str.contains('|'.join(kw),case=False,na=False)
            df.loc[mask & (df['category']=='Vodka'),'flavor_type'] = 'flavored'
        df['level']    = df['level'].str.strip()
        df['category'] = df['category'].str.strip()
        if 'brand_he' not in df.columns:
            df['brand_he'] = df['brand']
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=300)
def load_mixers():
    try:
        mx = pd.read_csv(MIXERS_URL)
        mx.columns = mx.columns.str.strip()
        for col in mx.select_dtypes(include='object').columns:
            mx[col] = mx[col].str.strip()
        for col in ['price_per_unit','unit_ml','price_per_crate','crate_size']:
            if col in mx.columns:
                mx[col] = pd.to_numeric(mx[col].astype(str).str.strip(), errors='coerce').fillna(0)
        return mx, None
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════
DR_RATE = 0.60
SAFETY  = 1.10
CUPS    = {"Vodka":2.5,"Whiskey":2.5,"Tequila":3.0,"Anis":2.5}
ML_CUP  = {"Vodka":50,"Whiskey":50,"Tequila":35,"Anis":50}
MIX_ML  = 150

CAT_HE  = {"Vodka":"וודקה 🍸","Whiskey":"וויסקי 🥃","Tequila":"טקילה 🌵","Anis":"ארק 🌿"}
CAT_EMJ = {"Vodka":"🍸","Whiskey":"🥃","Tequila":"🌵","Anis":"🌿"}

MIXER_EMJ = {"energy":"⚡","cranberry":"🫐","russian":"🫧","lemonade":"🍋"}

STYLE_CFG = {
    "חסכוני": {"levels":["Basic"],         "dist":{"Vodka":50,"Whiskey":25,"Tequila":15,"Anis":10}},
    "מאוזן":  {"levels":["Basic","Premium"],"dist":{"Vodka":40,"Whiskey":30,"Tequila":20,"Anis":10}},
    "פרמיום": {"levels":["Premium"],        "dist":{"Vodka":35,"Whiskey":35,"Tequila":20,"Anis":10}},
}

BADGE_MAP = {
    "basic":   '<span class="badge badge-basic">Basic</span>',
    "premium": '<span class="badge badge-premium">Premium</span>',
    "special": '<span class="badge badge-special">Special ✦</span>',
}

# ══════════════════════════════════════
# HELPERS
# ══════════════════════════════════════
def nd(g): return math.ceil(g * DR_RATE)

def best_brand(df, cat, levels, flavor="regular"):
    sub = df[(df['category']==cat)&(df['flavor_type']==flavor)&(df['level'].isin(levels))].copy()
    p = sub[sub['volume_ml']==1000]
    if p.empty: p = sub[sub['volume_ml']==700]
    if p.empty: p = sub
    if p.empty: return None
    return p.drop_duplicates('brand').sort_values('price').iloc[0]

def get_brands(df, cat, flavor=None, levels=None):
    sub = df[df['category']==cat].copy()
    if flavor:  sub = sub[sub['flavor_type']==flavor]
    if levels:  sub = sub[sub['level'].isin(levels)]
    if sub.empty: return pd.DataFrame()
    # לכל מותג — בחר נפח מועדף (1000 אם קיים, אחרת 700)
    # אבל כלול את כל המותגים הייחודיים
    result_rows = []
    for brand, grp in sub.groupby('brand'):
        pref = grp[grp['volume_ml']==1000]
        row  = pref.iloc[0] if not pref.empty else grp.iloc[0]
        result_rows.append(row)
    r = pd.DataFrame(result_rows).copy()
    ord_map = {'Basic':0,'Premium':1,'Special':2}
    r['_o'] = r['level'].map(ord_map).fillna(3)
    return r.sort_values(['_o','price']).drop(columns='_o').reset_index(drop=True)

def get_prod(df, cat, brand):
    sub = df[(df['category']==cat)&(df['brand']==brand)]
    p = sub[sub['volume_ml']==1000]
    return p.iloc[0] if not p.empty else sub.iloc[0]

def brand_display(row):
    he = row.get('brand_he', row['brand'])
    return he if he and str(he).strip() and str(he)!=str(row['brand']) else row['brand']

def fmt_b(row):
    he = row.get('brand_he', row['brand'])
    name = he if he and str(he).strip() else row['brand']
    return f"[{row['level']}] {name}  (₪{row['price']:.0f})"

def calc_item(df, cat, brand, pct, guests, hours=4):
    d  = math.ceil(nd(guests) * pct / 100)
    # כמות גדלה לפי שעות: 4 שעות = בסיס, כל שעה נוספת +15%
    hours_factor = 1.0 + max(0, hours - 4) * 0.15
    ml = d * CUPS[cat] * ML_CUP[cat] * SAFETY * hours_factor
    p  = get_prod(df, cat, brand)
    n  = max(1, math.ceil(ml / int(p['volume_ml'])))
    return {
        "cat":cat,"brand":brand,
        "brand_he": brand_display(p),
        "level": p.get('level',''),
        "vol":int(p['volume_ml']),"n":n,
        "ppb":p['price'],"total":p['price']*n,
        "drinkers":d,"pct":pct,"hours":hours
    }

def auto_rec(df, guests, style, active_cats):
    cfg = STYLE_CFG[style]
    rec = {}
    for cat in active_cats:
        b = best_brand(df, cat, cfg["levels"])
        if b is not None:
            rec[cat] = {"brand":b['brand'],"pct":cfg["dist"].get(cat,20)}
    return rec

def mixer_calc(cups_per_mixer, mx_df, venue_map, energy_choice="XL"):
    """
    cups_per_mixer: {mixer_key: num_cups}
    mx_df: mixers dataframe
    venue_map: {mixer_key: bool}
    energy_choice: "XL" or "Blue"
    Returns list of mixer result dicts
    """
    results = []
    if mx_df is None or mx_df.empty:
        return results
    for _, row in mx_df.iterrows():
        key  = str(row.get('mixer_key','')).strip().lower()
        name = str(row.get('name_he', key)).strip()
        # לאנרגי — רק הסוג שנבחר
        if key == "energy":
            if name != energy_choice:
                continue
        if key not in cups_per_mixer:
            continue
        cups       = cups_per_mixer[key]
        tot_ml     = cups * MIX_ML
        unit_ml    = int(row.get('unit_ml', 250))
        units      = math.ceil(tot_ml / unit_ml)
        crate_size = int(row.get('crate_size', 12)) or 12
        crates     = math.ceil(units / crate_size)
        ppc        = float(row.get('price_per_crate', 0))
        ppu        = float(row.get('price_per_unit', 0))
        # חשב עלות: אם יש מחיר לארגז — השתמש בו, אחרת חשב לפי יחידה
        if ppc > 0:
            cost = crates * ppc
        else:
            cost = units * ppu
        by_venue = venue_map.get(key, False)
        results.append({
            "key":        key,
            "name":       name,
            "units":      units,
            "unit_ml":    unit_ml,
            "crate_size": crate_size,
            "crates":     crates,
            "ppu":        ppu,
            "ppc":        ppc,
            "cost":       cost,
            "by_venue":   by_venue,
        })
    return results

# ══════════════════════════════════════
# SESSION
# ══════════════════════════════════════
def ss():
    defs = {
        "guests":150,"budget":None,"use_b":False,
        "style":"מאוזן",
        "active_cats":["Vodka","Whiskey","Tequila","Anis"],
        "rec":{},"generated":False,
        "extras":[],"specials":[],
        "edit_open":None,
        "show_flav":False,"show_sp":False,
        "venue_map":{},
    "energy_choice":"XL",
    "hours":4,
    "_counted":False,
    }
    for k,v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v
ss()

# ── שמירה/שחזור ב-query params ──
import json

SAVE_KEYS = ["guests","budget","use_b","style","active_cats","rec","extras","specials","venue_map","generated"]

def save_state():
    """שמור מצב ב-sessionStorage דרך JS component"""
    state = {}
    for k in SAVE_KEYS:
        val = st.session_state.get(k)
        try:
            json.dumps(val)
            state[k] = val
        except:
            pass
    state_json = json.dumps(state, ensure_ascii=False)
    # שמור ב-sessionStorage כדי לשרוד רענון
    st.components.v1.html(f"""
    <script>
    (function() {{
      try {{
        sessionStorage.setItem('weddingApp', JSON.stringify({state_json}));
      }} catch(e) {{}}
    }})();
    </script>
    """, height=0)

def try_restore_state():
    """שחזר מ-sessionStorage בטעינה ראשונה"""
    if st.session_state.get("_restored"):
        return
    st.session_state["_restored"] = True
    # קרא state שהוחזר מ-JS
    restore_val = st.session_state.get("_js_restore")
    if restore_val:
        try:
            saved = json.loads(restore_val)
            for k,v in saved.items():
                if k in SAVE_KEYS:
                    st.session_state[k] = v
        except:
            pass

try_restore_state()

df, err = load_alcohol()
mx_df, mx_err = load_mixers()

if err or df is None:
    st.error(f"❌ שגיאה בטעינת נתונים: {err}")
    st.stop()

# ══════════════════════════════════════
# HERO
# ══════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-glow"></div>
  <div class="hero-ornament">❧</div>
  <div class="hero-badge">✦ לחתונה מושלמת ✦</div>
  <div class="hero-title">יועץ האלכוהול לחתונה</div>
  <div class="hero-title-en">Wedding Bar Advisor</div>
  <div class="hero-sub">3 שאלות · המלצה מיידית · ניתן לעריכה מלאה</div>
  <div class="hero-divider"><span>🥂</span></div>
  <div style="margin-top:.3rem;opacity:.3;font-size:.8rem;letter-spacing:.4em;color:var(--rose)">
    ✿ &nbsp; ✿ &nbsp; ✿
  </div>
</div>
""", unsafe_allow_html=True)

# שחזור sessionStorage בטעינה ראשונה
if not st.session_state.get("_storage_read"):
    st.session_state["_storage_read"] = True
    restore_html = st.components.v1.html("""
    <script>
    (function() {
      try {
        var saved = sessionStorage.getItem('weddingApp');
        if (saved) {
          // Send to Streamlit via URL fragment trick
          var url = new URL(window.location.href);
          // Store in parent if available
          if (window.parent && window.parent.postMessage) {
            window.parent.postMessage({type:'weddingRestore', data: saved}, '*');
          }
        }
      } catch(e) {}
    })();
    </script>
    """, height=0)

# סטטוס נתונים מוסתר — רק לצורך דיבוג
if st.session_state.get("_dev_mode"):
    with st.expander("🔄 סטטוס נתונים", expanded=False):
        lvls = sorted(df['level'].unique())
        st.success(f"✅ {len(df)} מוצרים | רמות: {', '.join(lvls)}")
        has_he = 'brand_he' in df.columns and df['brand_he'].notna().any()
        has_mx = mx_df is not None and not mx_df.empty
        st.info(f"שמות עברית: {'✅' if has_he else '❌'} | מיקסרים: {'✅' if has_mx else '❌'}")
        if st.button("🔄 רענן נתונים", key="ref"):
            st.cache_data.clear(); st.rerun()

# ══════════════════════════════════════
# INPUT
# ══════════════════════════════════════
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="sec-title">📋 פרטי האירוע</div>', unsafe_allow_html=True)

c1,c2 = st.columns(2)
with c1:
    g = st.number_input("👥 מספר אורחים", 10, 3000, st.session_state.guests, 10, key="g_in")
    st.session_state.guests = g
with c2:
    ub = st.checkbox("💰 הגדר תקציב", value=st.session_state.use_b, key="ub")
    st.session_state.use_b = ub
    if ub:
        bv = st.number_input("תקציב ₪", 500, 300000, st.session_state.budget or 5000, 500, key="bv")
        st.session_state.budget = bv
    else:
        st.session_state.budget = None

n_d = nd(g)
bpd = (st.session_state.budget / n_d) if (st.session_state.budget and n_d>0) else None
info_txt = f"👥 כ-<b>{n_d}</b> מתוך <b>{g}</b> שותים"
if bpd: info_txt += f" &nbsp;·&nbsp; 💰 ₪<b>{bpd:.0f}</b> לשותה"
st.markdown(f'<div class="ibox" style="margin:.5rem 0">{info_txt}</div>', unsafe_allow_html=True)

# סגנון
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-title" style="margin-bottom:.5rem">🎨 סגנון האירוע</div>', unsafe_allow_html=True)
s1,s2,s3 = st.columns(3)
for col,(sk,lbl,desc) in zip([s1,s2,s3],[
    ("חסכוני","💚 חסכוני","הכי משתלם"),
    ("מאוזן","⚖️ מאוזן","Basic+Premium"),
    ("פרמיום","✨ פרמיום","מובחר"),
]):
    with col:
        is_a = st.session_state.style == sk
        st.markdown(f'<div class="style-pill {"active" if is_a else ""}">{lbl}<br><small style="font-weight:400;font-size:.69rem;opacity:.8">{desc}</small></div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button(lbl, key=f"sty_{sk}"):
            st.session_state.style = sk; st.session_state.generated = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# קטגוריות
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-title" style="margin-bottom:.5rem">🍾 סוגי אלכוהול</div>', unsafe_allow_html=True)
cc = st.columns(4)
for col, cat in zip(cc, ["Vodka","Whiskey","Tequila","Anis"]):
    with col:
        val = st.toggle(CAT_HE[cat], value=(cat in st.session_state.active_cats), key=f"tog_{cat}")
        if val and cat not in st.session_state.active_cats:
            st.session_state.active_cats.append(cat)
            st.session_state.generated = False
        elif not val and cat in st.session_state.active_cats:
            st.session_state.active_cats.remove(cat)
            st.session_state.rec.pop(cat, None)
            st.session_state.generated = False

# שעות אירוע
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-title" style="margin-bottom:.3rem">⏱️ כמה שעות האירוע?</div>', unsafe_allow_html=True)
h_val = st.session_state.get("hours", 4)
hc1,hc2,hc3 = st.columns([1,3,1])
with hc1:
    if st.button("➖", key="hm") and h_val > 3:
        st.session_state.hours = h_val - 1; st.rerun()
with hc2:
    h_pct = (h_val - 4) * 15
    h_note = "בסיס" if h_val == 4 else f"+{h_pct}% כמות"
    st.markdown(f'<div class="nbox" style="margin:0"><b>{h_val} שעות</b> · {h_note}</div>', unsafe_allow_html=True)
with hc3:
    if st.button("➕", key="hp") and h_val < 10:
        st.session_state.hours = h_val + 1; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── איור בר חתונה (empty state) ──
if not st.session_state.get("generated"):
    st.markdown("""
    <div class="wedding-bar-svg">
      <svg viewBox="0 0 300 160" xmlns="http://www.w3.org/2000/svg">
        <!-- טייבל -->
        <rect x="30" y="120" width="240" height="8" rx="4" fill="#c9838a" opacity=".5"/>
        <rect x="50" y="128" width="8" height="28" rx="3" fill="#c9838a" opacity=".3"/>
        <rect x="242" y="128" width="8" height="28" rx="3" fill="#c9838a" opacity=".3"/>
        <!-- בקבוק וודקה -->
        <rect x="80" y="75" width="18" height="45" rx="5" fill="#d4a96a" opacity=".7"/>
        <rect x="85" y="65" width="8" height="14" rx="3" fill="#d4a96a" opacity=".7"/>
        <rect x="84" y="62" width="10" height="5" rx="2" fill="#b8883e"/>
        <!-- בקבוק וויסקי -->
        <rect x="115" y="80" width="22" height="40" rx="4" fill="#8aab8a" opacity=".65"/>
        <rect x="121" y="68" width="10" height="16" rx="3" fill="#8aab8a" opacity=".65"/>
        <rect x="120" y="64" width="12" height="6" rx="2" fill="#6a8a6a"/>
        <!-- כוס יין -->
        <path d="M160 120 L155 95 Q152 80 165 78 Q178 80 175 95 L170 120 Z" fill="#c9838a" opacity=".5"/>
        <rect x="162" y="118" width="6" height="2" rx="1" fill="#c9838a" opacity=".4"/>
        <ellipse cx="165" cy="120" rx="10" ry="2" fill="#c9838a" opacity=".3"/>
        <!-- כוס שמפניה -->
        <path d="M195 120 L192 100 Q190 85 198 83 Q206 85 204 100 L201 120 Z" fill="#d4a96a" opacity=".5"/>
        <rect x="196" y="118" width="4" height="3" rx="1" fill="#d4a96a" opacity=".4"/>
        <!-- טבעת -->
        <circle cx="240" cy="108" r="10" fill="none" stroke="#d4a96a" stroke-width="2.5" opacity=".6"/>
        <circle cx="240" cy="108" r="5" fill="#d4a96a" opacity=".3"/>
        <!-- פרחים -->
        <circle cx="60" cy="95" r="6" fill="#c9838a" opacity=".4"/>
        <circle cx="52" cy="100" r="4" fill="#d4a96a" opacity=".35"/>
        <circle cx="68" cy="100" r="4" fill="#8aab8a" opacity=".35"/>
        <!-- כוכבי זהב -->
        <text x="25" y="55" font-size="12" fill="#d4a96a" opacity=".4">✦</text>
        <text x="265" y="65" font-size="10" fill="#c9838a" opacity=".4">✦</text>
        <text x="145" y="45" font-size="14" fill="#d4a96a" opacity=".5">🥂</text>
        <!-- כיתוב -->
        <text x="150" y="22" text-anchor="middle" font-family="Cormorant Garamond, serif"
              font-size="13" fill="#d4a96a" opacity=".7" font-style="italic">
          הזן פרטים וקבל המלצה מיידית
        </text>
      </svg>
    </div>
    """, unsafe_allow_html=True)

if st.button("✨ הפק המלצה מיידית", key="gen"):
    if not st.session_state.active_cats:
        st.error("בחר לפחות סוג אחד")
    else:
        # 🎉 Confetti burst
        import random as _rnd
        colors = ['#d4a96a','#c9838a','#8aab8a','#f5e6c8','#e8c97e','#ffffff']
        pieces = ""
        for i in range(60):
            c   = _rnd.choice(colors)
            lft = _rnd.randint(5,95)
            dur = _rnd.uniform(1.2, 2.4)
            dly = _rnd.uniform(0, 0.4)
            rot = _rnd.choice(['2px','8px'])
            pieces += f'<div class="confetti-piece" style="left:{lft}%;background:{c};width:{rot};height:{rot};animation-duration:{dur:.1f}s;animation-delay:{dly:.1f}s"></div>'
        st.markdown(f'<div class="confetti-wrap">{pieces}</div>', unsafe_allow_html=True)

        # ⏳ Loading message
        import random as _r2
        msgs = [
            "🥂 בודק מלאי...", "✨ בוחר את המותגים הטובים ביותר...",
            "🍸 מחשב כמויות...", "🥃 מאזן את הבר...",
            "🌹 מכין את ההמלצה שלך...", "💍 כמעט מוכן...",
        ]
        with st.spinner(_r2.choice(msgs)):
            import time; time.sleep(0.6)

        st.session_state.rec      = auto_rec(df, g, st.session_state.style, st.session_state.active_cats)
        st.session_state.extras   = []
        st.session_state.specials = []
        st.session_state.edit_open = None
        st.session_state.generated = True
        st.session_state._counted  = False
        st.rerun()

# ══════════════════════════════════════
# RESULTS
# ══════════════════════════════════════
if st.session_state.generated and st.session_state.rec:
    rec    = st.session_state.rec
    guests = st.session_state.guests
    budget = st.session_state.budget

    total_alc  = 0.0
    total_mix  = 0.0
    mixer_cups = {}
    share_lines = [f"🥂 *רשימת אלכוהול לחתונה*", f"👥 {guests} אורחים | {nd(guests)} שותים", ""]

    # ── Counter: רישום שקט ב-Google Sheets ──
    if not st.session_state.get("_counted", False):
        try:
            import datetime, threading, urllib.request as _ur
            ts      = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            style_v = st.session_state.get("style","מאוזן")
            guests_v= str(st.session_state.get("guests", 0))
            url     = (ANALYTICS_WRITE_URL +
                       f"?ts={urllib.parse.quote(ts)}"
                       f"&event=generate"
                       f"&style={urllib.parse.quote(style_v)}"
                       f"&guests={guests_v}")
            # שליחה ברקע — לא מאט את האפליקציה
            def _send(u):
                try: _ur.urlopen(u, timeout=4)
                except: pass
            threading.Thread(target=_send, args=(url,), daemon=True).start()
            st.session_state._counted = True
        except: pass

    st.markdown("""
    <div style="text-align:center;padding:.5rem 0;opacity:.5;font-size:1.1rem;letter-spacing:.3em;color:var(--rose)">
      ✦ &nbsp; ✦ &nbsp; ✦
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sec">🍾 ההמלצה שלך</div>', unsafe_allow_html=True)

    # ── אלכוהול עיקרי ──
    for cat in list(rec.keys()):
        info = rec[cat]
        item = calc_item(df, cat, info["brand"], info["pct"], guests, st.session_state.get("hours",4))
        total_alc += item["total"]
        share_lines.append(f"{CAT_EMJ[cat]} {item['brand_he']}: {item['n']} בקבוקים (₪{item['total']:.0f})")

        lvl_key = item["level"].lower() if item["level"] else "basic"
        badge_html = BADGE_MAP.get(lvl_key, "")

        st.markdown(f"""
        <div class="r-card">
          <div class="r-head">
            <div class="r-left">
              <div class="r-cat">{CAT_HE[cat]}</div>
              <div class="r-brand">{item['brand_he']} &nbsp;{badge_html}</div>
            </div>
            <div class="r-right">
              <div class="anim-num">{item['n']}</div>
              <div class="r-num-lbl">בקבוקים</div>
            </div>
          </div>
          <div class="r-row"><span>נפח לבקבוק</span><span>{item['vol']} מ"ל</span></div>
          <div class="r-row"><span>שותים ({item['pct']}%)</span><span>{item['drinkers']} אנשים</span></div>
          <div class="r-row"><span>מחיר לבקבוק</span><span>₪{item['ppb']:.0f}</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{item['total']:.0f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        ea,eb,ec = st.columns(3)
        with ea:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("✏️ מותג", key=f"eb_{cat}"):
                st.session_state.edit_open = f"brand_{cat}" if st.session_state.edit_open!=f"brand_{cat}" else None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with eb:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button(f"📊 {info['pct']}%", key=f"ep_{cat}"):
                st.session_state.edit_open = f"pct_{cat}" if st.session_state.edit_open!=f"pct_{cat}" else None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with ec:
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑️ הסר", key=f"ed_{cat}"):
                del st.session_state.rec[cat]
                if cat in st.session_state.active_cats: st.session_state.active_cats.remove(cat)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.edit_open == f"brand_{cat}":
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            bdf = get_brands(df, cat)
            opts = bdf['brand'].tolist()
            cur  = opts.index(info["brand"]) if info["brand"] in opts else 0
            ni   = st.selectbox("בחר מותג:", range(len(opts)),
                                format_func=lambda x,d=bdf: fmt_b(d.iloc[x]),
                                index=cur, key=f"sel_{cat}")
            if st.button("✅ אשר", key=f"ok_b_{cat}"):
                st.session_state.rec[cat]["brand"] = opts[ni]
                st.session_state.edit_open = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.edit_open == f"pct_{cat}":
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            cur_pct = info["pct"]
            new_d_preview = math.ceil(nd(guests) * cur_pct / 100)
            st.markdown(f'<div class="nbox" style="margin:0 0 .5rem">{CAT_HE[cat]} — כרגע <b>{cur_pct}%</b> · {new_d_preview} אנשים</div>', unsafe_allow_html=True)
            new_pct = st.number_input(
                "% מהשותים",
                min_value=5, max_value=80,
                value=cur_pct, step=5,
                key=f"pct_input_{cat}",
                label_visibility="collapsed"
            )
            if new_pct != cur_pct:
                st.session_state.rec[cat]["pct"] = int(new_pct)
                st.rerun()
            pc1, pc2 = st.columns(2)
            with pc1:
                st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                if st.button("✅ סגור", key=f"ok_p_{cat}"):
                    st.session_state.edit_open = None; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # חישוב מיקסרים
        if cat == "Vodka":
            cups = math.ceil(item["drinkers"] * CUPS["Vodka"] * SAFETY)
            for m in ["energy","cranberry","russian"]:
                mixer_cups[m] = mixer_cups.get(m,0) + cups
        if cat == "Anis":
            cups = math.ceil(item["drinkers"] * CUPS["Anis"] * SAFETY)
            mixer_cups["lemonade"] = mixer_cups.get("lemonade",0) + cups

    # ── extras ──
    EXTRA_LBL = {"Vodka":"וודקה בטעמים 🍹","Whiskey":"וויסקי נוסף 🥃","Tequila":"טקילה נוספת 🌵","Anis":"ארק נוסף 🌿"}
    for idx,ve in enumerate(st.session_state.extras):
        cat_e = ve.get("cat","Vodka")
        it    = calc_item(df, cat_e, ve["brand"], ve["pct"], guests, st.session_state.get("hours",4))
        total_alc += it["total"]
        share_lines.append(f"➕ {it['brand_he']}: {it['n']} בקבוקים (₪{it['total']:.0f})")
        lvl_key = it["level"].lower() if it["level"] else "basic"
        badge_html = BADGE_MAP.get(lvl_key,"")
        st.markdown(f"""
        <div class="r-card" style="border-color:rgba(192,132,252,.25)">
          <div class="r-head">
            <div><div class="r-cat">{EXTRA_LBL.get(cat_e,cat_e)}</div>
            <div class="r-brand">{it['brand_he']} &nbsp;{badge_html}</div></div>
            <div class="r-right"><div class="r-num">{it['n']}</div><div class="r-num-lbl">בקבוקים</div></div>
          </div>
          <div class="r-row"><span>שותים ({ve['pct']}%)</span><span>{it['drinkers']} אנשים</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{it['total']:.0f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑️ הסר", key=f"del_ex_{idx}"): st.session_state.extras.pop(idx); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── specials ──
    for idx,sp in enumerate(st.session_state.specials):
        it = calc_item(df, sp["category"], sp["brand"], sp["pct"], guests, st.session_state.get("hours",4))
        total_alc += it["total"]
        share_lines.append(f"👑 {it['brand_he']}: {it['n']} בקבוקים (₪{it['total']:.0f})")
        st.markdown(f"""
        <div class="sp-card">
          <div class="r-head">
            <div><div class="r-cat">👑 יוקרה</div><div class="r-brand">{it['brand_he']} {BADGE_MAP.get('special','')}</div></div>
            <div class="r-right"><div class="r-num">{it['n']}</div><div class="r-num-lbl">בקבוקים</div></div>
          </div>
          <div class="r-row"><span>שותים ({sp['pct']}%)</span><span>{it['drinkers']} אנשים</span></div>
          <div class="r-row"><span>מחיר לבקבוק</span><span>₪{it['ppb']:.0f}</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{it['total']:.0f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑️ הסר", key=f"del_sp_{idx}"): st.session_state.specials.pop(idx); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── כפתורי הוספה ──
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    ba,bb,bc = st.columns(3)
    with ba:
        st.markdown('<div class="btn-add">', unsafe_allow_html=True)
        if st.button("🍹 + וודקה בטעמים", key="af"):
            st.session_state.show_flav = not st.session_state.show_flav
            st.session_state.show_sp   = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with bb:
        st.markdown('<div class="btn-add">', unsafe_allow_html=True)
        if st.button("🥃 + וויסקי נוסף", key="aw"):
            w_df = get_brands(df,"Whiskey")
            exist = [r["brand"] for r in st.session_state.extras if r.get("cat")=="Whiskey"]
            exist.append(rec.get("Whiskey",{}).get("brand",""))
            nw = w_df[~w_df['brand'].isin(exist)]
            if not nw.empty:
                st.session_state.extras.append({"brand":nw.iloc[0]['brand'],"cat":"Whiskey","pct":10})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with bc:
        st.markdown('<div class="btn-sp">', unsafe_allow_html=True)
        if st.button("👑 + יוקרה", key="asp"):
            st.session_state.show_sp   = not st.session_state.show_sp
            st.session_state.show_flav = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_flav:
        st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
        fd = get_brands(df,"Vodka",flavor="flavored")
        if not fd.empty:
            fo = fd['brand'].tolist()
            fc1,fc2 = st.columns([3,1])
            with fc1: fi = st.selectbox("טעם:",range(len(fo)),format_func=lambda x,d=fd:fmt_b(d.iloc[x]),key="fi")
            with fc2: fp = st.number_input("% שותים",5,40,15,5,key="fp")
            if st.button("✅ הוסף",key="fi_ok"):
                st.session_state.extras.append({"brand":fo[fi],"cat":"Vodka","pct":int(fp)})
                st.session_state.show_flav = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_sp:
        sp_df_raw = df[df['level'].str.lower()=='special'].copy()
        if not sp_df_raw.empty:
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            p_sp = sp_df_raw[sp_df_raw['volume_ml']==1000]
            if p_sp.empty: p_sp = sp_df_raw[sp_df_raw['volume_ml']==700]
            sp_cl = p_sp.drop_duplicates('brand').reset_index(drop=True)
            sc1,sc2 = st.columns([3,1])
            with sc1: si = st.selectbox("בחר:",range(len(sp_cl)),format_func=lambda x,d=sp_cl:fmt_b(d.iloc[x]),key="si")
            with sc2: sp_ = st.number_input("% שותים",2,20,5,1,key="sip")
            if st.button("✅ הוסף",key="si_ok"):
                st.session_state.specials.append({"brand":sp_cl.iloc[si]['brand'],"category":sp_cl.iloc[si]['category'],"pct":int(sp_)})
                st.session_state.show_sp = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nbox">עדכן level=Special לבקבוקי יוקרה בגיליון</div>', unsafe_allow_html=True)

    # ══ מיקסרים ══
    if mixer_cups and mx_df is not None and not mx_df.empty:
        st.markdown('<div class="sec">🧃 מיקסרים</div>', unsafe_allow_html=True)

        # בחירת סוג אנרגי
        ec1, ec2 = st.columns([2,3])
        with ec1:
            st.markdown('<div style="color:var(--text-mid);font-size:.85rem;padding-top:.4rem">⚡ סוג אנרגי:</div>', unsafe_allow_html=True)
        with ec2:
            energy_opts = ["XL","Blue"]
            cur_e = st.session_state.get("energy_choice","XL")
            new_e = st.radio("סוג אנרגי", energy_opts, index=energy_opts.index(cur_e),
                             horizontal=True, key="energy_radio", label_visibility="collapsed")
            if new_e != cur_e:
                st.session_state.energy_choice = new_e; st.rerun()

        mix_results = mixer_calc(mixer_cups, mx_df, st.session_state.venue_map,
                                 energy_choice=st.session_state.get("energy_choice","XL"))
        CRATE_SIZE  = {"energy":24,"cranberry":12,"russian":12,"lemonade":12}

        st.markdown('<div class="mix-wrap"><div class="mix-hdr">🧃 אומדן מיקסרים</div>', unsafe_allow_html=True)
        share_lines.append(""); share_lines.append("🧃 *מיקסרים:*")

        for mr in mix_results:
            by_venue  = mr["by_venue"]
            crates    = math.ceil(mr["units"] / CRATE_SIZE.get(mr["key"], 12))
            if not by_venue: total_mix += mr["cost"]
            venue_html = '<span class="venue-tag">✓ האולם מביא</span>' if by_venue else ""
            crate_txt  = f'<s style="color:var(--text-dim)">~{crates} ארגזים</s>' if by_venue else f'<b>~{crates} ארגזים</b>'
            cost_html  = "₪0" if by_venue else f'₪{mr["cost"]:.0f}'
            share_lines.append(f"{'✅' if by_venue else '•'} {mr['name']}: ~{crates} ארגזים ({cost_html})")

            st.markdown(f"""
            <div class="mix-item">
              <div class="mix-name">
                <span>{MIXER_EMJ.get(mr['key'],'🍶')}</span>
                <div>
                  <div>{mr['name']} {venue_html}</div>
                  <div class="mix-price">~{mr['units']} יח' · {CRATE_SIZE.get(mr['key'],12)} יח' לארגז</div>
                </div>
              </div>
              <div style="text-align:center">
                <div class="mix-qty">{crate_txt}</div>
                <div class="mix-price">{cost_html}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # checkboxes האולם מביא - מחוץ ל-loop של display
        st.markdown('<div class="edit-pnl" style="margin-top:.5rem">', unsafe_allow_html=True)
        st.markdown("**🏛️ מה האולם מביא? (סמן ✓)**")
        seen_venue_keys = set()
        for mr in mix_results:
            vkey = mr["key"]
            if vkey in seen_venue_keys:
                continue
            seen_venue_keys.add(vkey)
            cur_val = st.session_state.venue_map.get(vkey, False)
            new_val = st.checkbox(f'{MIXER_EMJ.get(vkey,"🍶")} {mr["name"]}', value=cur_val, key=f"ven_cb_{vkey}")
            if new_val != cur_val:
                st.session_state.venue_map[vkey] = new_val; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # שמור מצב אוטומטית
    save_state()

    # ══ סה"כ ══
    total_cost = total_alc + total_mix
    share_lines.append(f"\n💰 *אלכוהול: ₪{total_alc:,.0f}*")
    if total_mix > 0: share_lines.append(f"🧃 *מיקסרים: ₪{total_mix:,.0f}*")
    share_lines.append(f"✨ *סה\"כ: ₪{total_cost:,.0f}*")

    if budget:
        pct_used = min(total_cost/budget, 1.0)
        bar_color = "#4ade80" if pct_used < 0.85 else ("#f5d78e" if pct_used < 1.0 else "#f87171")
        in_b      = total_cost <= budget
        status    = f"✅ חוסך ₪{budget-total_cost:,.0f}" if in_b else f"❌ חורג ב-₪{total_cost-budget:,.0f}"
        c_main    = "var(--green)" if in_b else "var(--red)"
        st.markdown(f"""
        <div class="total-wrap">
          <div class="total-sub">סה"כ עלות</div>
          <div class="total-main" style="color:{c_main}">₪{total_cost:,.0f}</div>
          <div class="budget-bar-wrap">
            <div class="budget-bar-bg">
              <div class="budget-bar-fill" style="width:{pct_used*100:.0f}%;background:{bar_color}"></div>
            </div>
          </div>
          <div class="total-sub">מתוך ₪{budget:,.0f} | {status}</div>
        </div>""", unsafe_allow_html=True)
    else:
        sub_parts = [f"{nd(guests)} שותים"]
        if total_mix>0: sub_parts.append(f"אלכוהול ₪{total_alc:,.0f} + מיקסרים ₪{total_mix:,.0f}")
        st.markdown(f"""
        <div class="total-wrap">
          <div class="total-sub">סה"כ עלות</div>
          <div class="total-main">₪{total_cost:,.0f}</div>
          <div class="total-sub">{' · '.join(sub_parts)}</div>
        </div>""", unsafe_allow_html=True)

    # ══ FAQ ══
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    with st.expander("❓ שאל את הבר — שאלות נפוצות"):
        faqs = [
            ("כמה וודקה לחתונה עם 200 אורחים?",
             "עם 200 אורחים כ-120 שותים. אם 40% שותים וודקה (~48 איש) לאירוע של 4 שעות — כ-7-8 בקבוקי ליטר. הפעל את החישוב עם 200 אורחים וסגנון מאוזן לתוצאה מדויקת."),
            ('האם עדיף לקנות בקבוקי ליטר או 700 מ"ל?',
             'בקבוקי ליטר כמעט תמיד משתלמים יותר מבחינת מחיר למ"ל. ה-700 מ"ל שימושי יותר לוודקות בטעמים או לשולחנות ספציפיים.'),
            ("כמה מרווח ביטחון להוסיף?",
             "האפליקציה כוללת 10% מרווח אוטומטי. לחתונות גדולות מעל 300 אורחים מומלץ להוסיף עוד 5-10% ידנית."),
            ("מה ההבדל בין Basic לPremium?",
             "Basic = מותגים כמו פינלנדיה, ג'וני ווקר רד — איכות טובה במחיר נגיש. Premium = בלוגה, גריי גוס, בלאק לייבל — מותגים יוקרתיים לאירועים מובחרים."),
            ("האם לחשב מיקסרים כחלק מהתקציב?",
             "כן! מיקסרים יכולים להוסיף 15-25% לעלות הכוללת. האפליקציה מחשבת זאת אוטומטית. אם האולם מספק חלק מהם — סמן 'האולם מביא' להפחתה."),
            ("מתי הזמן הנכון לקנות?",
             "אלכוהול: 1-2 חודשים לפני — מחירים יציבים ויש זמן לאחסן. מיקסרים: שבוע לפני — פחית טרייה יותר. קרח בדרך כלל מסופק על ידי האולם — כדאי לוודא מראש."),
            ("כמה כוסות שותה אדם ממוצע בחתונה?",
             "2.5-3 כוסות בממוצע לאירוע של 4 שעות. האפליקציה משתמשת בנתון זה. לאירוע ארוך יותר — הגדל את מספר השעות בהגדרות."),
        ]
        for q, a in faqs:
            st.markdown(f"**🔹 {q}**")
            st.markdown(f"<div style='color:var(--text-mid);font-size:.85rem;margin-bottom:.8rem;padding-right:.5rem'>{a}</div>", unsafe_allow_html=True)

    # ══ שיתוף ══
    import json as _json
    # שמירה אוטומטית ב-localStorage
    _save_keys = ["guests","budget","use_b","style","active_cats","rec","extras","specials","venue_map","generated"]
    _state = {}
    for _k in _save_keys:
        try:
            _v = st.session_state.get(_k)
            _json.dumps(_v)
            _state[_k] = _v
        except: pass
    _sj = _json.dumps(_state, ensure_ascii=False)
    st.components.v1.html(f"""
    <script>
    try {{
      localStorage.setItem('weddingAlcohol', {repr(_sj)});
    }} catch(e) {{}}
    </script>
    <div style="text-align:center;color:rgba(232,201,126,0.45);font-size:.7rem;
      font-family:'Heebo',sans-serif;padding:.2rem 0 .5rem;direction:rtl;">
      💾 ההתקדמות נשמרה אוטומטית — תוכל לחזור מאוחר יותר
    </div>
    """, height=30)

    wa  = f"https://wa.me/?text={urllib.parse.quote(chr(10).join(share_lines))}"
    ml  = f"mailto:?subject={urllib.parse.quote('רשימת אלכוהול לחתונה')}&body={urllib.parse.quote(chr(10).join(share_lines))}"
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown("**📤 שתף את הרשימה:**")
    sh1,sh2 = st.columns(2)
    with sh1: st.markdown(f'<a href="{wa}" target="_blank" class="wa-btn">📱 שלח לוואצאפ</a>', unsafe_allow_html=True)
    with sh2: st.markdown(f'<a href="{ml}" class="mail-btn">📧 שלח באימייל</a>', unsafe_allow_html=True)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("🔄 התחל מחדש", key="rst"):
        st.components.v1.html("<script>try{localStorage.removeItem('weddingAlcohol')}catch(e){}</script>", height=0)
        for k in ["rec","generated","extras","specials","edit_open","show_flav","show_sp","venue_map"]:
            st.session_state[k] = {} if k in ["rec","venue_map"] else ([] if k in ["extras","specials"] else (False if "show" in k or k=="generated" else None))
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)
st.markdown('''
<div style="text-align:center;padding:.5rem 0 1rem">
  <div style="font-family:'Dancing Script',cursive;font-size:1.1rem;color:var(--rose);opacity:.7;margin-bottom:.3rem">
    נוצר בלב ❤ על ידי בר אנקרי
  </div>
  <div style="color:var(--text-dim);font-size:.7rem;letter-spacing:.03em">
    מחירים מבוססים על מחירון קמעונאי · 60% שותים · 2.5 כוסות לאדם · 10% מרווח
  </div>
</div>
''', unsafe_allow_html=True)
