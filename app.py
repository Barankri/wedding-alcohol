import streamlit as st
import pandas as pd
import math
import urllib.parse
import json
import threading
import urllib.request
import datetime
import random
# QR נוצר דרך API חינמי — ללא ספרייה חיצונית
QR_AVAILABLE = True

# ══════════════════════════════════════
# URLs
# ══════════════════════════════════════
SHEET_URL            = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5QV1mK8Tg8SGbnDBs005Re6LVTB_f4ZYjo9Vd8AmFkeh0pNZf4dKOzV9adzDn6SRIRwlNwyPlBFL/pub?output=csv"
MIXERS_URL           = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTy5QV1mK8Tg8SGbnDBs005Re6LVTB_f4ZYjo9Vd8AmFkeh0pNZf4dKOzV9adzDn6SRIRwlNwyPlBFL/pub?gid=1444549454&single=true&output=csv"
ANALYTICS_WRITE_URL  = "https://script.google.com/macros/s/AKfycbxz57lULFP6ClP-Gabdn71dlwVvI-YIF6LCx81guHLzM4efv8c8q_0yualR33bHxR1x8g/exec"

st.set_page_config(page_title="יועץ האלכוהול", page_icon="🥂", layout="centered")

# ══════════════════════════════════════
# CSS — Mobile App Native
# ══════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;900&family=Frank+Ruhl+Libre:wght@400;500;700;900&family=Dancing+Script:wght@600;700&display=swap');

:root {
  --gold:#e8c97e; --gold2:#b89a50;
  --rose:#c9838a; --sage:#8aab8a;
  --bg:#09090f; --bg2:#111119; --bg3:#17171f; --bg4:#1c1c28;
  --glass:rgba(18,15,25,0.92);
  --border:rgba(232,201,126,0.2); --border-dim:rgba(255,255,255,0.07);
  --text:#ede5d5; --text-mid:#a09070; --text-dim:#5a5248;
  --green:#4ade80; --red:#f87171; --blue:#60c8f5;
  --r:20px; --r-sm:14px; --r-xs:10px;
}
/* event themes */
body.theme-henna {
  --bg:#0a0812; --bg2:#150f20; --bg3:#1c1530;
  --gold:#e67e22; --rose:#9b59b6;
  --border:rgba(230,126,34,0.2);
}
body.theme-barmitzvah {
  --bg:#07090f; --bg2:#0f1520; --bg3:#141e30;
  --gold:#e8c97e; --rose:#1a6bb5;
  --border:rgba(96,165,250,0.2);
}
*{box-sizing:border-box;}
html,body,[class*="css"]{
  font-family:'Heebo',sans-serif;
  direction:rtl; background:var(--bg); color:var(--text);
  -webkit-tap-highlight-color:transparent;
}

/* ── Welcome ── */
.welcome{text-align:center;padding:3rem 1rem 2rem;position:relative;}
.welcome-glow{
  position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:500px;height:400px;
  background:radial-gradient(ellipse,rgba(232,201,126,0.07) 0%,rgba(201,131,138,0.04) 40%,transparent 70%);
  pointer-events:none;
}
.welcome-badge{
  display:inline-block;background:rgba(232,201,126,0.08);
  border:1px solid var(--border);border-radius:30px;
  padding:.3rem 1rem;font-size:.7rem;color:var(--gold);
  letter-spacing:.12em;text-transform:uppercase;margin-bottom:.8rem;
  animation:fadeDown .6s ease both;
}
.welcome-title{
  font-family:Frank Ruhl Libre,serif;
  font-size:clamp(2.2rem,7vw,3rem);font-weight:700;
  color:var(--gold);line-height:1.05;margin-bottom:.3rem;
  animation:fadeDown .6s .05s ease both;
}
.welcome-en{
  font-family:'Dancing Script',cursive;
  font-size:1.1rem;color:var(--rose);opacity:.7;margin-bottom:2rem;
  animation:fadeDown .6s .1s ease both;
}

/* ── Event cards ── */
.event-list{display:flex;flex-direction:column;gap:.8rem;animation:fadeUp .6s .15s ease both;}
.event-card{
  background:var(--glass);backdrop-filter:blur(12px);
  border:1px solid var(--border-dim);border-radius:var(--r);
  padding:1.1rem 1.3rem;display:flex;align-items:center;gap:1rem;
  transition:all .2s;position:relative;overflow:hidden;
  cursor:pointer;
}
.event-card::after{
  content:'';position:absolute;inset:0;opacity:0;transition:opacity .2s;
}
.event-card:hover{border-color:var(--border);transform:translateY(-1px);}
.event-card:hover::after{opacity:1;}
.ec-wedding::after{background:linear-gradient(135deg,rgba(232,201,126,.06),transparent);}
.ec-henna::after{background:linear-gradient(135deg,rgba(230,126,34,.08),transparent);}
.ec-bar::after{background:linear-gradient(135deg,rgba(26,107,181,.08),transparent);}
.ec-icon{font-size:2rem;min-width:48px;text-align:center;}
.ec-title{font-family:Frank Ruhl Libre,serif;font-size:1.2rem;font-weight:700;color:var(--gold);}
.ec-desc{font-size:.78rem;color:var(--text-dim);margin-top:.1rem;}
.ec-arrow{margin-right:auto;color:var(--text-dim);font-size:1rem;}

/* ── Input Panel ── */
.input-panel{
  background:var(--bg2);border:1px solid var(--border-dim);
  border-radius:var(--r);padding:1.4rem 1.5rem;margin-bottom:1rem;
}
.panel-title{
  font-family:Frank Ruhl Libre,serif;
  font-size:1.05rem;font-weight:700;color:var(--gold);
  margin-bottom:1rem;display:flex;align-items:center;gap:.4rem;
}

/* ── Style pills ── */
.style-pills{display:flex;gap:.5rem;width:100%;}
.style-pill{
  flex:1;padding:.55rem .3rem;background:var(--bg3);
  border:1.5px solid var(--border-dim);border-radius:var(--r-sm);
  color:var(--text-dim);font-size:.78rem;font-weight:700;
  cursor:pointer;text-align:center;transition:all .2s;line-height:1.3;
  font-family:'Heebo',sans-serif;
}
.style-pill.active{background:rgba(232,201,126,.1);border-color:var(--gold);color:var(--gold);}

/* ── Result card — compact mobile ── */
.r-card{
  border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.8rem;
  transition:border-color .2s;
  animation:fadeUp .4s ease both;
}
.r-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.7rem;}
.r-left{flex:1;}
.r-cat{font-family:Frank Ruhl Libre,serif;font-size:1.05rem;font-weight:700;color:var(--gold);}
.r-brand{font-size:.78rem;color:var(--text-mid);margin-top:.1rem;}
.r-right{text-align:center;min-width:56px;}
.r-num{font-family:Frank Ruhl Libre,serif;font-size:2.2rem;font-weight:900;color:#fff;line-height:1;animation:popIn .4s ease both;}
.r-num-lbl{font-size:.62rem;color:var(--text-dim);}
.r-row{display:flex;justify-content:space-between;padding:.28rem 0;border-bottom:1px solid var(--border-dim);font-size:.82rem;color:var(--text);}
.r-row:last-child{border-bottom:none;}
.r-val{color:var(--gold);font-weight:700;}
.badge{display:inline-block;padding:.12rem .5rem;border-radius:20px;font-size:.65rem;font-weight:700;}
.badge-basic{background:rgba(74,222,128,.1);color:#4ade80;border:1px solid rgba(74,222,128,.2);}
.badge-premium{background:rgba(232,201,126,.1);color:var(--gold);border:1px solid var(--border);}
.badge-special{background:rgba(192,132,252,.1);color:#c084fc;border:1px solid rgba(192,132,252,.2);}

/* ── Edit panel ── */
.edit-pnl{background:var(--bg3);border:1px solid var(--border);border-radius:var(--r-sm);padding:.9rem 1rem;margin-bottom:.8rem;}

/* ── Bottom sheet simulation ── */
.sheet-overlay{
  background:rgba(0,0,0,0.5);border-radius:var(--r);
  padding:.8rem;margin-bottom:.8rem;
  animation:fadeIn .2s ease both;
}
.sheet-inner{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:var(--r);padding:1rem 1.1rem;
}
.sheet-handle{width:36px;height:3px;background:var(--border-dim);border-radius:2px;margin:0 auto .8rem;}
.sheet-title{font-family:Frank Ruhl Libre,serif;font-size:1rem;color:var(--gold);text-align:center;margin-bottom:.8rem;}
.brand-option{
  display:flex;justify-content:space-between;align-items:center;
  padding:.6rem .8rem;border-radius:var(--r-xs);margin-bottom:.4rem;
  background:var(--bg3);border:1px solid var(--border-dim);
  transition:all .15s;cursor:pointer;
}
.brand-option.sel{background:rgba(232,201,126,.08);border-color:var(--gold);}
.brand-opt-name{font-size:.85rem;color:var(--text);}
.brand-opt-name.sel{color:var(--gold);font-weight:700;}
.brand-opt-price{font-size:.75rem;color:var(--text-dim);}

/* ── Special card ── */
.sp-card{
  background:linear-gradient(135deg,rgba(192,132,252,.08),rgba(192,132,252,.02));
  border:1px solid rgba(192,132,252,.25);border-radius:var(--r);
  padding:1.1rem 1.3rem;margin-bottom:.8rem;
}

/* ── Mixer card ── */
.mix-card{
  background:linear-gradient(135deg,rgba(96,200,245,.04),transparent);
  border:1px solid rgba(96,200,245,.15);border-radius:var(--r);
  padding:1.1rem 1.3rem;margin-bottom:.8rem;
}
.mix-hdr{font-size:.9rem;font-weight:700;color:var(--blue);margin-bottom:.7rem;}
.mix-row{display:flex;justify-content:space-between;align-items:center;padding:.35rem 0;border-bottom:1px solid var(--border-dim);font-size:.82rem;}
.mix-row:last-child{border-bottom:none;}

/* ── Sticky total ── */
.total-strip{
  background:linear-gradient(135deg,rgba(232,201,126,.1),rgba(232,201,126,.03));
  border:1.5px solid var(--border);border-radius:var(--r);
  padding:1.2rem 1.4rem;display:flex;justify-content:space-between;
  align-items:center;margin:1rem 0;
  box-shadow:0 0 40px rgba(232,201,126,.06);
}
.total-main{font-family:Frank Ruhl Libre,serif;font-size:2.4rem;font-weight:900;color:var(--gold);line-height:1;}
.total-meta{font-size:.75rem;color:var(--text-dim);margin-top:.2rem;}
.budget-bar{height:4px;background:var(--border-dim);border-radius:2px;margin-top:.5rem;overflow:hidden;width:120px;}
.budget-fill{height:100%;border-radius:2px;transition:width .6s ease;}

/* ── Add buttons row ── */
.add-row{display:flex;gap:.5rem;margin:.5rem 0 1rem;}

/* ── Info boxes ── */
.ibox{background:rgba(74,222,128,.05);border:1px solid rgba(74,222,128,.15);border-radius:var(--r-xs);padding:.5rem .8rem;color:#a8efc0;font-size:.8rem;margin:.35rem 0;}
.wbox{background:rgba(248,113,113,.06);border:1px solid rgba(248,113,113,.15);border-radius:var(--r-xs);padding:.5rem .8rem;color:#fca5a5;font-size:.8rem;margin:.35rem 0;}
.nbox{background:rgba(232,201,126,.06);border:1px solid rgba(232,201,126,.15);border-radius:var(--r-xs);padding:.5rem .8rem;color:var(--gold);font-size:.8rem;margin:.35rem 0;text-align:center;}

/* ── Divider ── */
.div{height:1px;background:linear-gradient(to right,transparent,var(--border),transparent);margin:1rem 0;}
.sec{font-family:Frank Ruhl Libre,serif;font-size:1.1rem;color:var(--gold);margin:.9rem 0 .5rem;}

/* ── Share ── */
.wa-btn{display:flex;align-items:center;justify-content:center;gap:.5rem;background:#25D366;color:#fff;border:none;border-radius:var(--r);padding:.75rem;font-family:'Heebo',sans-serif;font-weight:800;font-size:.9rem;text-decoration:none;width:100%;}

/* ── Confetti ── */
.confetti-wrap{position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;overflow:hidden;}
.cp{position:absolute;top:-10px;border-radius:2px;animation:cfall linear forwards;}
@keyframes cfall{0%{transform:translateY(0) rotate(0deg) scale(1);opacity:1;}80%{opacity:1;}100%{transform:translateY(100vh) rotate(720deg) scale(.4);opacity:0;}}

/* ── Animations ── */
@keyframes fadeDown{from{opacity:0;transform:translateY(-12px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes popIn{0%{transform:scale(0);opacity:0}100%{transform:scale(1);opacity:1}}
@keyframes pulse{0%,100%{opacity:.6}50%{opacity:1}}

/* ── Buttons ── */
.stButton>button{
  background:linear-gradient(135deg,var(--gold2),var(--gold)) !important;
  color:#09090f !important;font-family:'Heebo',sans-serif !important;
  font-weight:800 !important;border:none !important;
  border-radius:var(--r) !important;padding:.75rem 1.5rem !important;
  width:100% !important;transition:all .2s !important;
  box-shadow:0 3px 18px rgba(232,201,126,.15) !important;
  font-size:.92rem !important;min-height:50px !important;
}
.stButton>button:hover{transform:translateY(-1px) !important;box-shadow:0 5px 24px rgba(232,201,126,.25) !important;}
.btn-ghost>button{background:var(--bg3) !important;color:var(--text-mid) !important;border:1px solid var(--border-dim) !important;box-shadow:none !important;font-size:.82rem !important;min-height:44px !important;}
.btn-danger>button{background:rgba(248,113,113,.08) !important;color:#f87171 !important;border:1px solid rgba(248,113,113,.2) !important;box-shadow:none !important;font-size:.82rem !important;min-height:44px !important;}
.btn-add>button{background:rgba(74,222,128,.07) !important;color:var(--green) !important;border:1px solid rgba(74,222,128,.2) !important;box-shadow:none !important;font-size:.82rem !important;min-height:44px !important;}
.btn-sp>button{background:rgba(192,132,252,.07) !important;color:#c084fc !important;border:1px solid rgba(192,132,252,.2) !important;box-shadow:none !important;font-size:.82rem !important;min-height:44px !important;}

/* ── Mobile ── */
@media(max-width:600px){
  .main .block-container{padding-left:.5rem !important;padding-right:.5rem !important;max-width:100% !important;}
  .welcome-title{font-size:1.9rem !important;}
  .r-num{font-size:1.8rem !important;}
  .total-main{font-size:1.9rem !important;}
  .r-card,.input-panel,.mix-card,.sp-card{padding:.85rem .9rem !important;border-radius:16px !important;}
  .stButton>button{min-height:50px !important;font-size:.8rem !important;}
  input[type="number"]{font-size:1rem !important;}
  /* Radio options bigger touch targets */
  [data-testid="stRadio"] label{
    min-height:44px !important;
    display:flex !important;align-items:center !important;
    padding:.5rem .4rem !important;
    font-size:.85rem !important;
  }
  /* Columns fix */
  [data-testid="column"]{padding:.05rem .08rem !important;}
  /* Number input arrows bigger */
  input[type="number"]::-webkit-inner-spin-button{height:2em !important;opacity:1 !important;}
}
html,body{overflow-x:hidden !important;}
.main .block-container{max-width:640px !important;overflow-x:hidden !important;}
[data-testid="column"]{padding:.1rem .1rem !important;min-width:0 !important;}
[data-testid="stHorizontalBlock"]{gap:.4rem !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# DATA
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
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('₪','').str.replace(',','').str.strip(),errors='coerce')
        if 'flavor_type' in df.columns:
            df['flavor_type'] = df['flavor_type'].str.lower().str.strip()
        else:
            df['flavor_type'] = 'regular'
            kw = ['Watermelon','Pineapple','Asai','Melon','Van Gogh','Cavalli']
            mask = df['brand'].str.contains('|'.join(kw),case=False,na=False)
            df.loc[mask & (df['category']=='Vodka'),'flavor_type'] = 'flavored'
        df['level']    = df['level'].str.strip()
        df['category'] = df['category'].str.strip()
        if 'brand_he' not in df.columns: df['brand_he'] = df['brand']
        return df, None
    except Exception as e: return None, str(e)

@st.cache_data(ttl=300)
def load_mixers():
    try:
        mx = pd.read_csv(MIXERS_URL)
        mx.columns = mx.columns.str.strip()
        for col in mx.select_dtypes(include='object').columns:
            mx[col] = mx[col].str.strip()
        for col in ['price_per_unit','unit_ml','price_per_crate','crate_size']:
            if col in mx.columns:
                mx[col] = pd.to_numeric(mx[col].astype(str).str.strip(),errors='coerce').fillna(0)
        return mx, None
    except Exception as e: return None, str(e)

# ══════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════
SAFETY  = 1.10
ML_CUP  = {"Vodka":50,"Whiskey":50,"Tequila":35,"Anis":50}
MIX_ML  = 150
CAT_HE  = {"Vodka":"וודקה 🍸","Whiskey":"וויסקי 🥃","Tequila":"טקילה 🌵","Anis":"ארק 🌿"}
CAT_COLOR = {
    "Vodka":   {"gold":"#60c8f5","bg":"#0d1520","border":"rgba(96,200,245,0.3)","dim":"rgba(96,200,245,0.08)","text":"#304858","mid":"#507090"},
    "Whiskey": {"gold":"#d4934a","bg":"#1a1208","border":"rgba(212,147,74,0.3)", "dim":"rgba(212,147,74,0.08)", "text":"#584830","mid":"#907050"},
    "Tequila": {"gold":"#7ab648","bg":"#0d1a0d","border":"rgba(122,182,72,0.3)", "dim":"rgba(122,182,72,0.08)", "text":"#385030","mid":"#507040"},
    "Anis":    {"gold":"#9b72cf","bg":"#120d1a","border":"rgba(155,114,207,0.3)","dim":"rgba(155,114,207,0.08)","text":"#403058","mid":"#706090"},
}
CAT_EMJ = {"Vodka":"🍸","Whiskey":"🥃","Tequila":"🌵","Anis":"🌿"}
MIXER_EMJ = {"energy":"⚡","cranberry":"🫐","russian":"🫧","lemonade":"🍋"}
MIXER_HE  = {"energy":"אנרגי","cranberry":"חמוציות","russian":"ראשן","lemonade":"לימונדה"}

BADGE_MAP = {
    "basic":   '<span class="badge badge-basic">Basic</span>',
    "premium": '<span class="badge badge-premium">Premium</span>',
    "special": '<span class="badge badge-special">Special ✦</span>',
}

EVENT_CFG = {
    "wedding": {
        "name":"חתונה","emoji":"💍","en":"Wedding Night",
        "dist":{
            "מאוזן":  {"Vodka":40,"Whiskey":30,"Tequila":20,"Anis":10},
            "חסכוני": {"Vodka":50,"Whiskey":25,"Tequila":15,"Anis":10},
            "פרמיום": {"Vodka":35,"Whiskey":35,"Tequila":20,"Anis":10},
        },
        "dr_by_size":{200:0.80,300:0.75,9999:0.70},
        "cups":3.0,
        "loading":["🥂 מכין את הבר המושלם לערב הגדול...",
                   "💍 בוחר את המותגים הטובים ביותר...",
                   "✨ מאזן את הבר שלכם...",
                   "🌹 כמעט מוכן..."],
        "blessing":"שיהיה לכם ערב בלתי נשכח 🥂",
        "confetti":["#e8c97e","#c9838a","#8aab8a","#f5e6c8","#ffffff","#d4a96a"],
        "gold":"#e8c97e","accent":"#c9838a",
        "bg_main":"#0e0b08","bg2":"#1a1510","bg3":"#221e14",
        "glow":"rgba(232,201,126,0.07)",
    },
    "henna": {
        "name":"חינה","emoji":"🌙","en":"Henna Night",
        "dist":{
            "מאוזן":  {"Vodka":30,"Whiskey":25,"Tequila":10,"Anis":35},
            "חסכוני": {"Vodka":35,"Whiskey":20,"Tequila":5,"Anis":40},
            "פרמיום": {"Vodka":25,"Whiskey":30,"Tequila":10,"Anis":35},
        },
        "dr_by_size":{200:0.80,300:0.75,9999:0.70},
        "cups":3.0,
        "loading":["🌙 אהלן וסהלן! מכין לכם לילה מושלם...",
                   "✦ בוחר את הארק הכי טוב...",
                   "🕌 מכין את הלילה שלכם...",
                   "🌟 כמעט מוכן..."],
        "blessing":"בשעה טובה! שתהיה חינה מהממת 🌙",
        "confetti":["#9b59b6","#e67e22","#f39c12","#d4a96a","#ffffff","#8e44ad"],
        "gold":"#e67e22","accent":"#9b59b6",
        "bg_main":"#0a0812","bg2":"#150f20","bg3":"#1c1530",
        "glow":"rgba(155,89,182,0.07)",
    },
    "barmitzvah": {
        "name":"בר/בת מצווה","emoji":"🎉","en":"Bar Mitzvah",
        "dist":{
            "מאוזן":  {"Vodka":30,"Whiskey":50,"Tequila":10,"Anis":10},
            "חסכוני": {"Vodka":35,"Whiskey":45,"Tequila":10,"Anis":10},
            "פרמיום": {"Vodka":25,"Whiskey":60,"Tequila":10,"Anis":5},
        },
        "dr_by_size":{200:0.60,9999:0.55},
        "cups":2.5,
        "loading":["🎉 מכין את החגיגה...",
                   "✡️ בוחר את הוויסקי הכי טוב...",
                   "🎊 כמעט מוכן...",
                   "💙 מאזן את הבר..."],
        "blessing":"מזל טוב! שיהיה אירוע מושלם 🎉",
        "confetti":["#1a6bb5","#ffffff","#e8c97e","#4ade80","#60a5fa","#93c5fd"],
        "gold":"#e8c97e","accent":"#1a6bb5",
        "bg_main":"#07090f","bg2":"#0f1520","bg3":"#141e30",
        "glow":"rgba(26,107,181,0.07)",
    },
}

STYLE_CFG = {
    "חסכוני": {"levels":["Basic"]},
    "מאוזן":  {"levels":["Basic","Premium"]},
    "פרמיום": {"levels":["Premium"]},
}

# ══════════════════════════════════════
# HELPERS
# ══════════════════════════════════════
def get_dr_rate(event_key, guests):
    cfg = EVENT_CFG.get(event_key, EVENT_CFG["wedding"])
    for threshold, rate in sorted(cfg["dr_by_size"].items()):
        if guests <= threshold: return rate
    return 0.70

def nd(g, event_key=None):
    if event_key is None:
        event_key = st.session_state.get("event_type","wedding") or "wedding"
    return math.ceil(g * get_dr_rate(event_key, g))

def get_cups(event_key=None):
    if event_key is None:
        event_key = st.session_state.get("event_type","wedding") or "wedding"
    return EVENT_CFG.get(event_key, EVENT_CFG["wedding"])["cups"]

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
    event_key    = st.session_state.get("event_type","wedding") or "wedding"
    d            = math.ceil(nd(guests, event_key) * pct / 100)
    hours_factor = 1.0 + max(0, hours - 4) * 0.15
    cups_val     = get_cups(event_key)
    ml           = d * cups_val * ML_CUP[cat] * SAFETY * hours_factor
    p            = get_prod(df, cat, brand)
    n            = max(1, math.ceil(ml / int(p['volume_ml'])))
    return {"cat":cat,"brand":brand,"brand_he":brand_display(p),"level":p.get('level',''),
            "vol":int(p['volume_ml']),"n":n,"ppb":p['price'],"total":p['price']*n,
            "drinkers":d,"pct":pct}

def auto_rec(df, guests, style, active_cats):
    cfg        = STYLE_CFG[style]
    event_key  = st.session_state.get("event_type","wedding") or "wedding"
    event_dist = EVENT_CFG[event_key]["dist"].get(style, EVENT_CFG[event_key]["dist"]["מאוזן"])
    rec = {}
    for cat in active_cats:
        b = best_brand(df, cat, cfg["levels"])
        if b is not None:
            rec[cat] = {"brand":b['brand'],"pct":event_dist.get(cat,20)}
    return rec

def mixer_calc(cups_per_mixer, mx_df, venue_map, energy_choice="XL"):
    results = []
    if mx_df is None or mx_df.empty: return results
    CRATE_SIZE = {"energy":24,"cranberry":12,"russian":12,"lemonade":12}
    for _, row in mx_df.iterrows():
        key  = str(row.get('mixer_key','')).strip().lower()
        name = str(row.get('name_he', key)).strip()
        if key == "energy" and name != energy_choice: continue
        if key not in cups_per_mixer: continue
        cups       = cups_per_mixer[key]
        tot_ml     = cups * MIX_ML
        unit_ml    = int(row.get('unit_ml', 250))
        units      = math.ceil(tot_ml / unit_ml)
        crate_size = CRATE_SIZE.get(key, 12)
        crates     = math.ceil(units / crate_size)
        ppc        = float(row.get('price_per_crate', 0))
        ppu        = float(row.get('price_per_unit', 0))
        cost       = crates * ppc if ppc > 0 else units * ppu
        by_venue   = venue_map.get(key, False)
        results.append({"key":key,"name":name,"units":units,"unit_ml":unit_ml,
                        "crate_size":crate_size,"crates":crates,"ppu":ppu,"ppc":ppc,
                        "cost":cost,"by_venue":by_venue})
    return results

def send_analytics(style_v, guests_v):
    try:
        ts  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        evt = st.session_state.get("event_type","wedding") or "wedding"
        url = (ANALYTICS_WRITE_URL +
               f"?ts={urllib.parse.quote(ts)}&event=generate"
               f"&style={urllib.parse.quote(style_v)}&guests={guests_v}"
               f"&event_type={urllib.parse.quote(evt)}")
        def _send(u):
            try: urllib.request.urlopen(u, timeout=4)
            except: pass
        threading.Thread(target=_send, args=(url,), daemon=True).start()
    except: pass

# ══════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════
def ss_init():
    defs = {
        "event_type":None,
        "tool_type":None,
        "guests":150,"budget":None,"use_b":False,
        "style":"מאוזן",
        "active_cats":["Vodka","Whiskey","Tequila","Anis"],
        "rec":{},"generated":False,
        "extras":[],"specials":[],
        "edit_open":None,
        "show_flav":False,"show_sp":False,
        "venue_map":{},"energy_choice":"XL",
        "hours":4,"couple_name":"",
        "_counted":False,
    }
    for k,v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

ss_init()
df, err     = load_alcohol()
mx_df, _    = load_mixers()

if err or df is None:
    st.error(f"❌ שגיאה בטעינת נתונים: {err}")
    st.stop()

# ══════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════
if not st.session_state.event_type and not st.session_state.tool_type:
    st.markdown("""
    <div class="welcome">
      <div class="welcome-glow"></div>
      <div class="welcome-badge">✦ ברוכים הבאים ✦</div>
      <div class="welcome-title">יועץ האלכוהול</div>
      <div class="welcome-en">Bar Advisor</div>
    </div>
    """, unsafe_allow_html=True)

    # ── אירועים ──
    st.markdown('''<div style="font-size:.78rem;color:var(--text-dim);margin-bottom:.5rem">
        האירוע שלכם</div>''', unsafe_allow_html=True)

    st.markdown("""
    <div class="event-card ec-wedding">
      <div class="ec-icon">💍</div>
      <div><div class="ec-title">חתונה</div>
      <div class="ec-desc">וודקה · וויסקי · טקילה · ארק</div></div>
      <div class="ec-arrow">›</div>
    </div>""", unsafe_allow_html=True)
    if st.button("💍  חתונה", key="ev_w", use_container_width=True):
        st.session_state.event_type = "wedding"; st.rerun()

    st.markdown("""
    <div class="event-card ec-henna" style="border-color:rgba(230,126,34,0.2)">
      <div class="ec-icon">🌙</div>
      <div><div class="ec-title" style="color:#e67e22">חינה</div>
      <div class="ec-desc">ארק · וויסקי · וודקה · וייב מזרחי</div></div>
      <div class="ec-arrow">›</div>
    </div>""", unsafe_allow_html=True)
    if st.button("🌙  חינה", key="ev_h", use_container_width=True):
        st.session_state.event_type = "henna"; st.rerun()

    st.markdown("""
    <div class="event-card ec-bar" style="border-color:rgba(26,107,181,0.2)">
      <div class="ec-icon">🎉</div>
      <div><div class="ec-title" style="color:#60a5fa">בר / בת מצווה</div>
      <div class="ec-desc">וויסקי · וודקה · קהל מעורב</div></div>
      <div class="ec-arrow">›</div>
    </div>""", unsafe_allow_html=True)
    if st.button("🎉  בר / בת מצווה", key="ev_b", use_container_width=True):
        st.session_state.event_type = "barmitzvah"; st.rerun()

    # ── מפריד ──
    st.markdown('''
    <div style="display:flex;align-items:center;gap:8px;margin:1.2rem 0 .8rem">
      <div style="flex:1;height:1px;background:rgba(255,255,255,0.05)"></div>
      <div style="font-size:.72rem;color:var(--text-dim);white-space:nowrap">כלים נוספים</div>
      <div style="flex:1;height:1px;background:rgba(255,255,255,0.05)"></div>
    </div>
    ''', unsafe_allow_html=True)

    # ── כלים ──
    st.markdown('''
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin-bottom:.5rem">
      <div style="background:var(--bg2);border:1px solid var(--border-dim);border-radius:14px;
           padding:.9rem .8rem;text-align:center">
        <div style="font-size:1.4rem;margin-bottom:.3rem">🔄</div>
        <div style="font-size:.82rem;font-weight:700;color:var(--text-mid);margin-bottom:.2rem">כמה אורחים?</div>
        <div style="font-size:.7rem;color:var(--text-dim);line-height:1.4">יש לי X בקבוקים — לכמה אורחים זה מספיק?</div>
      </div>
      <div style="background:var(--bg2);border:1px solid var(--border-dim);border-radius:14px;
           padding:.9rem .8rem;text-align:center">
        <div style="font-size:1.4rem;margin-bottom:.3rem">📊</div>
        <div style="font-size:.82rem;font-weight:700;color:var(--text-mid);margin-bottom:.2rem">מה נשאר?</div>
        <div style="font-size:.7rem;color:var(--text-dim);line-height:1.4">אחרי האירוע — נתח מה שתו בפועל</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("🔄 כמה אורחים?", key="tool_rev", use_container_width=True):
            st.session_state.tool_type = "reverse"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with tc2:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("📊 מה נשאר?", key="tool_left", use_container_width=True):
            st.session_state.tool_type = "leftover"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 .5rem">
      <div style="font-family:'Dancing Script',cursive;font-size:1rem;color:var(--rose);opacity:.5">
        נוצר בלב ❤ על ידי בר אנקרי
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════
# כלי 6 — מחשבון הפוך
# ══════════════════════════════════════
if st.session_state.tool_type == "reverse":
    ecfg_t = EVENT_CFG["wedding"]
    st.markdown(f"""
    <div style="text-align:center;padding:1.2rem 1rem .8rem">
      <div style="font-family:'Dancing Script',cursive;font-size:.9rem;color:var(--rose);opacity:.7;margin-bottom:.3rem">✦ כלי נוסף ✦</div>
      <div style="font-family:Frank Ruhl Libre,serif;font-size:2rem;font-weight:700;color:var(--gold)">🔄 כמה אורחים?</div>
      <div style="font-size:.82rem;color:var(--text-dim);margin-top:.3rem">הזן כמה בקבוקים יש לך — נחשב לכמה אורחים זה מספיק</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("← חזור למסך הפתיחה", key="back_rev", use_container_width=True):
        st.session_state.tool_type = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)

    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🍾 מה יש לך במלאי?</div>', unsafe_allow_html=True)
    st.markdown('<div class="nbox" style="margin-bottom:.8rem">הזן 0 אם אין לך מאותו סוג</div>', unsafe_allow_html=True)

    rev_vodka   = st.number_input("🍸 בקבוקי וודקה (ליטר)", 0, 200, 0, 1, key="rv_v")
    rev_whiskey = st.number_input("🥃 בקבוקי וויסקי (ליטר)", 0, 200, 0, 1, key="rv_w")
    rev_tequila = st.number_input("🌵 בקבוקי טקילה (ליטר)", 0, 200, 0, 1, key="rv_t")
    rev_anis    = st.number_input("🌿 בקבוקי ארק (700 מ\"ל)", 0, 200, 0, 1, key="rv_a")

    rev_hours   = st.number_input("⏱️ שעות האירוע", 3, 10, 4, 1, key="rv_h")
    st.markdown('</div>', unsafe_allow_html=True)

    # חישוב
    total_ml = {
        "Vodka":   rev_vodka   * 1000,
        "Whiskey": rev_whiskey * 1000,
        "Tequila": rev_tequila * 1000,
        "Anis":    rev_anis    * 700,
    }
    hours_factor = 1.0 + max(0, rev_hours - 4) * 0.15
    CUPS_REV = {"Vodka":3.0,"Whiskey":3.0,"Tequila":3.0,"Anis":3.0}
    DIST_REV = {"Vodka":0.40,"Whiskey":0.30,"Tequila":0.20,"Anis":0.10}

    results_rev = {}
    for cat, ml in total_ml.items():
        if ml > 0:
            ml_per_drinker = CUPS_REV[cat] * ML_CUP[cat] * SAFETY * hours_factor
            drinkers = ml / ml_per_drinker
            guests_from_cat = drinkers / DIST_REV[cat]
            results_rev[cat] = {"ml": ml, "drinkers": math.floor(drinkers), "guests": math.floor(guests_from_cat)}

    if any(v > 0 for v in [rev_vodka,rev_whiskey,rev_tequila,rev_anis]):
        min_guests = min(r["guests"] for r in results_rev.values()) if results_rev else 0

        verdict = "⚠️ מלאי קטן" if min_guests < 80 else "✅ מלאי טוב!"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(232,201,126,0.1),rgba(232,201,126,0.03));
             border:1.5px solid var(--border);border-radius:var(--r);
             padding:1.8rem 1.4rem;text-align:center;margin-top:.8rem">
          <div style="font-size:.82rem;color:var(--text-dim);margin-bottom:.3rem">המלאי שלך מספיק ל</div>
          <div style="font-family:Frank Ruhl Libre,serif;font-size:3.5rem;font-weight:900;
               color:var(--gold);line-height:1">~{min_guests}</div>
          <div style="font-size:.9rem;color:var(--text-mid);margin-top:.4rem">
            אורחים · {rev_hours} שעות · {verdict}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="nbox" style="margin-top:.8rem">הזן כמויות כדי לראות את התוצאה</div>', unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════
# כלי 7 — מה נשאר?
# ══════════════════════════════════════
if st.session_state.tool_type == "leftover":
    st.markdown(f"""
    <div style="text-align:center;padding:1.2rem 1rem .8rem">
      <div style="font-family:'Dancing Script',cursive;font-size:.9rem;color:var(--rose);opacity:.7;margin-bottom:.3rem">✦ כלי נוסף ✦</div>
      <div style="font-family:Frank Ruhl Libre,serif;font-size:2rem;font-weight:700;color:var(--gold)">📊 מה נשאר?</div>
      <div style="font-size:.82rem;color:var(--text-dim);margin-top:.3rem">הזן מה קנית ומה נשאר — נחשב כמה שתו בפועל</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("← חזור למסך הפתיחה", key="back_left", use_container_width=True):
        st.session_state.tool_type = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)

    # קלט — מה קנית
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🛒 מה קנית?</div>', unsafe_allow_html=True)
    lf_guests = st.number_input("👥 כמה אורחים היו?", 10, 3000, 150, 10, key="lf_g")
    lf_bought_v = st.number_input("🍸 בקבוקי וודקה שקנית", 0, 200, 12, 1, key="lf_bv")
    lf_bought_w = st.number_input("🥃 בקבוקי וויסקי שקנית", 0, 200, 8, 1, key="lf_bw")
    lf_bought_t = st.number_input("🌵 בקבוקי טקילה שקנית", 0, 200, 5, 1, key="lf_bt")
    lf_bought_a = st.number_input("🌿 בקבוקי ארק שקנית (700מ\"ל)", 0, 200, 6, 1, key="lf_ba")
    st.markdown('</div>', unsafe_allow_html=True)

    # קלט — מה נשאר
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📦 מה נשאר?</div>', unsafe_allow_html=True)
    lf_left_v = st.number_input("🍸 בקבוקי וודקה שנשארו", 0, lf_bought_v or 1, 0, 1, key="lf_lv")
    lf_left_w = st.number_input("🥃 בקבוקי וויסקי שנשארו", 0, lf_bought_w or 1, 0, 1, key="lf_lw")
    lf_left_t = st.number_input("🌵 בקבוקי טקילה שנשארו", 0, lf_bought_t or 1, 0, 1, key="lf_lt")
    lf_left_a = st.number_input("🌿 בקבוקי ארק שנשארו", 0, lf_bought_a or 1, 0, 1, key="lf_la")
    st.markdown('</div>', unsafe_allow_html=True)

    bought = {"Vodka":lf_bought_v,"Whiskey":lf_bought_w,"Tequila":lf_bought_t,"Anis":lf_bought_a}
    left   = {"Vodka":lf_left_v,  "Whiskey":lf_left_w,  "Tequila":lf_left_t,  "Anis":lf_left_a}
    used   = {cat: bought[cat] - left[cat] for cat in bought}
    total_bought = sum(bought.values())
    total_used   = sum(used.values())
    total_pct    = (total_used / total_bought * 100) if total_bought > 0 else 0

    if total_bought > 0:
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec">📈 ניתוח הערב</div>', unsafe_allow_html=True)

        # כרטיס סיכום
        pct_color = "#4ade80" if total_pct >= 75 else ("#f5d78e" if total_pct >= 50 else "#f87171")
        verdict   = "מעולה! 🎉" if total_pct >= 80 else ("טוב 👍" if total_pct >= 60 else "נשאר הרבה 🤔")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(232,201,126,0.08),rgba(232,201,126,0.02));
             border:1.5px solid var(--border);border-radius:var(--r);padding:1.2rem 1.4rem;
             text-align:center;margin-bottom:.8rem">
          <div style="font-size:.78rem;color:var(--text-dim)">ניצולת כוללת</div>
          <div style="font-family:Frank Ruhl Libre,serif;font-size:2.8rem;font-weight:900;
               color:{pct_color};line-height:1">{total_pct:.0f}%</div>
          <div style="font-size:.82rem;color:var(--text-mid)">{total_used} מתוך {total_bought} בקבוקים · {verdict}</div>
          <div style="height:5px;background:var(--border-dim);border-radius:3px;overflow:hidden;margin:.6rem 0 0">
            <div style="width:{min(total_pct,100):.0f}%;height:100%;background:{pct_color};border-radius:3px"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        # פירוט לפי קטגוריה
        for cat in ["Vodka","Whiskey","Tequila","Anis"]:
            if bought[cat] == 0: continue
            pct_cat = (used[cat] / bought[cat] * 100) if bought[cat] > 0 else 0
            c_bar   = "#4ade80" if pct_cat >= 75 else ("#f5d78e" if pct_cat >= 50 else "#f87171")
            tip = ""
            if pct_cat == 100:
                tip = '<div class="wbox" style="margin:.4rem 0 0;font-size:.75rem">⚠️ אזל לגמרי — בפעם הבאה הוסף 1-2 בקבוקים</div>'
            elif pct_cat < 50:
                tip = f'<div class="wbox" style="margin:.4rem 0 0;font-size:.75rem">💡 נשאר הרבה — בפעם הבאה הפחת ב-{100-int(pct_cat):.0f}%</div>'
            st.markdown(f"""
            <div class="r-card" style="margin-bottom:.6rem">
              <div class="r-head">
                <div class="r-left">
                  <div class="r-cat">{CAT_HE[cat]}</div>
                  <div class="r-brand">שתו {used[cat]} מתוך {bought[cat]} בקבוקים</div>
                </div>
                <div class="r-right">
                  <div class="r-num" style="color:{c_bar}">{pct_cat:.0f}%</div>
                  <div class="r-num-lbl">ניצולת</div>
                </div>
              </div>
              <div style="height:5px;background:var(--border-dim);border-radius:3px;overflow:hidden;margin:.3rem 0">
                <div style="width:{min(pct_cat,100):.0f}%;height:100%;background:{c_bar};border-radius:3px"></div>
              </div>
              {tip}
            </div>""", unsafe_allow_html=True)

        # המלצה לפעם הבאה
        st.markdown('<div class="div"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec">💡 להפעם הבאה</div>', unsafe_allow_html=True)
        lf_next_guests = st.number_input("👥 כמה אורחים יהיו בפעם הבאה?", 10, 3000, lf_guests, 10, key="lf_ng")
        if st.button("✨ חשב המלצה לפעם הבאה", key="lf_next", use_container_width=True):
            st.session_state.event_type = "wedding"
            st.session_state.guests     = lf_next_guests
            st.session_state.tool_type  = None
            st.session_state.generated  = False
            st.rerun()
    else:
        st.markdown('<div class="nbox" style="margin-top:.8rem">הזן כמויות כדי לראות ניתוח</div>', unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════
# MAIN APP (after event chosen)
# ══════════════════════════════════════
evt     = st.session_state.event_type
ecfg    = EVENT_CFG.get(evt, EVENT_CFG["wedding"])
e_gold  = ecfg["gold"]
e_acc   = ecfg["accent"]

# Hero
st.markdown(f"""
<div style="text-align:center;padding:1.5rem 1rem 1rem;position:relative">
  <div style="position:absolute;top:0;left:50%;transform:translateX(-50%);
    width:400px;height:250px;
    background:radial-gradient(ellipse,rgba(232,201,126,0.07) 0%,transparent 65%);
    pointer-events:none"></div>
  <div style="font-family:'Dancing Script',cursive;font-size:.9rem;color:{e_acc};opacity:.7;margin-bottom:.3rem">
    ✦ {ecfg['en']} ✦
  </div>
  <div style="font-family:Frank Ruhl Libre,serif;
    font-size:clamp(1.8rem,5vw,2.4rem);font-weight:700;color:{e_gold};line-height:1.1">
    {ecfg['emoji']} יועץ האלכוהול
  </div>
  <div style="font-size:.82rem;color:var(--text-dim);margin-top:.3rem">
    {ecfg['name']} · המלצה מיידית · ניתן לעריכה
  </div>
</div>
""", unsafe_allow_html=True)

# Change event button
st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
if st.button("← שנה סוג אירוע", key="chg_evt"):
    st.session_state.event_type = None
    st.session_state.generated  = False
    st.session_state.rec        = {}
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="div"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# INPUT
# ══════════════════════════════════════
st.markdown('<div class="input-panel">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">📋 פרטי האירוע</div>', unsafe_allow_html=True)

g = st.number_input("👥 מספר אורחים", 10, 3000, st.session_state.guests, 10, key="g_in")
st.session_state.guests = g
ub = st.checkbox("💰 הגדר תקציב", value=st.session_state.use_b, key="ub")
st.session_state.use_b = ub
if ub:
    bv = st.number_input("תקציב (₪)", 500, 300000, st.session_state.budget or 5000, 500, key="bv")
    st.session_state.budget = bv
else:
    st.session_state.budget = None

n_d  = nd(g)
bpd  = (st.session_state.budget / n_d) if (st.session_state.budget and n_d>0) else None
itxt = f"👥 כ-<b>{n_d}</b> מתוך <b>{g}</b> שותים"
if bpd: itxt += f" · 💰 ₪<b>{bpd:.0f}</b> לשותה"
st.markdown(f'<div class="ibox" style="margin:.4rem 0">{itxt}</div>', unsafe_allow_html=True)

# Couple name
couple_input = st.text_input("💍 שם הזוג (אופציונלי)", value=st.session_state.couple_name,
                              placeholder="לדוגמה: דנה ועמית", key="couple_inp")
st.session_state.couple_name = couple_input

# Style
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="panel-title" style="margin-bottom:.4rem">🎨 סגנון</div>', unsafe_allow_html=True)
for sk,lbl,desc in [
    ("חסכוני","💚 חסכוני","Basic — הכי משתלם"),
    ("מאוזן","⚖️ מאוזן","Basic + Premium"),
    ("פרמיום","✨ פרמיום","Premium — מובחר"),
]:
    is_a   = st.session_state.style == sk
    border = "var(--gold)" if is_a else "var(--border-dim)"
    bg     = "rgba(232,201,126,0.08)" if is_a else "var(--bg3)"
    clr    = "var(--gold)" if is_a else "var(--text-dim)"
    tick   = "✓" if is_a else ""
    st.markdown(
        f'<div style="background:{bg};border:1.5px solid {border};border-radius:14px;' +
        f'padding:.7rem 1rem;margin-bottom:.4rem;display:flex;justify-content:space-between;' +
        f'align-items:center"><div style="font-size:.88rem;font-weight:700;color:{clr}">{lbl}</div>' +
        f'<div style="display:flex;align-items:center;gap:.5rem">' +
        f'<span style="font-size:.72rem;color:var(--text-dim)">{desc}</span>' +
        f'<span style="color:var(--gold)">{tick}</span></div></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button(lbl, key=f"sty_{sk}", use_container_width=True):
        st.session_state.style = sk; st.session_state.generated = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Categories
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="panel-title" style="margin-bottom:.4rem">🍾 סוגי אלכוהול</div>', unsafe_allow_html=True)
for cat in ["Vodka","Whiskey","Tequila","Anis"]:
    val = st.toggle(CAT_HE[cat], value=(cat in st.session_state.active_cats), key=f"tog_{cat}")
    if val and cat not in st.session_state.active_cats:
        st.session_state.active_cats.append(cat); st.session_state.generated = False
    elif not val and cat in st.session_state.active_cats:
        st.session_state.active_cats.remove(cat)
        st.session_state.rec.pop(cat, None); st.session_state.generated = False

# Hours
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="panel-title" style="margin-bottom:.3rem">⏱️ שעות האירוע</div>', unsafe_allow_html=True)
h_val = st.session_state.get("hours", 4)
h_note = "בסיס" if h_val == 4 else f"+{(h_val-4)*15}% כמות"
st.markdown(f'''<div style="display:flex;align-items:center;gap:.8rem;
    background:var(--bg3);border:1px solid var(--border-dim);
    border-radius:14px;padding:.7rem 1rem">
  <div style="flex:1;text-align:right;font-size:.9rem;color:var(--gold);font-weight:700">{h_val} שעות</div>
  <div style="font-size:.78rem;color:var(--text-dim)">{h_note}</div>
</div>''', unsafe_allow_html=True)
st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
if st.button("➕ הוסף שעה", key="hp", use_container_width=True) and h_val < 10:
    st.session_state.hours = h_val + 1; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
if st.button("➖ הפחת שעה", key="hm", use_container_width=True) and h_val > 3:
    st.session_state.hours = h_val - 1; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Generate button ──
if not st.session_state.generated:
    # Empty state SVG
    if evt == "wedding":
        st.markdown("""<div style="text-align:center;padding:1rem 0;opacity:.7">
          <svg viewBox="0 0 260 120" xmlns="http://www.w3.org/2000/svg" style="max-width:240px;width:90%">
            <rect x="20" y="95" width="220" height="7" rx="3" fill="#c9838a" opacity=".4"/>
            <rect x="65" y="55" width="16" height="40" rx="4" fill="#d4a96a" opacity=".6"/>
            <rect x="69" y="47" width="8" height="12" rx="3" fill="#d4a96a" opacity=".6"/>
            <rect x="95" y="60" width="20" height="35" rx="4" fill="#8aab8a" opacity=".6"/>
            <rect x="101" y="50" width="8" height="14" rx="3" fill="#8aab8a" opacity=".5"/>
            <path d="M135 95 L131 75 Q129 62 140 60 Q151 62 149 75 L145 95Z" fill="#c9838a" opacity=".5"/>
            <path d="M165 95 L162 78 Q160 65 170 63 Q180 65 177 78 L174 95Z" fill="#d4a96a" opacity=".5"/>
            <circle cx="210" cy="82" r="9" fill="none" stroke="#d4a96a" stroke-width="2" opacity=".5"/>
            <circle cx="210" cy="82" r="4" fill="#d4a96a" opacity=".25"/>
            <text x="130" y="18" text-anchor="middle" font-family="serif" font-size="11" fill="#d4a96a" opacity=".6" font-style="italic">הזן פרטים וקבל המלצה מיידית</text>
          </svg></div>""", unsafe_allow_html=True)
    elif evt == "henna":
        st.markdown("""<div style="text-align:center;padding:1rem 0;opacity:.7">
          <svg viewBox="0 0 260 120" xmlns="http://www.w3.org/2000/svg" style="max-width:240px;width:90%">
            <circle cx="30" cy="20" r="2" fill="#e67e22" opacity=".5"/>
            <circle cx="230" cy="15" r="1.5" fill="#9b59b6" opacity=".6"/>
            <circle cx="130" cy="10" r="2" fill="#e67e22" opacity=".4"/>
            <polygon points="130,18 143,42 148,72 130,80 112,72 117,42" fill="#9b59b6" opacity=".3" stroke="#9b59b6" stroke-width="1"/>
            <rect x="122" y="35" width="9" height="12" rx="2" fill="#f39c12" opacity=".45"/>
            <rect x="134" y="35" width="9" height="12" rx="2" fill="#f39c12" opacity=".45"/>
            <rect x="122" y="52" width="9" height="12" rx="2" fill="#f39c12" opacity=".45"/>
            <rect x="134" y="52" width="9" height="12" rx="2" fill="#f39c12" opacity=".45"/>
            <line x1="130" y1="8" x2="130" y2="18" stroke="#e67e22" stroke-width="1.5" opacity=".5"/>
            <circle cx="55" cy="88" r="8" fill="#9b59b6" opacity=".25"/>
            <circle cx="47" cy="83" r="5" fill="#e67e22" opacity=".3"/>
            <circle cx="63" cy="83" r="5" fill="#e67e22" opacity=".3"/>
            <circle cx="205" cy="35" r="16" fill="#e67e22" opacity=".1"/>
            <circle cx="212" cy="30" r="12" fill="#0a0812" opacity=".7"/>
            <text x="130" y="108" text-anchor="middle" font-family="serif" font-size="11" fill="#e67e22" opacity=".6" font-style="italic">אהלן וסהלן! הזן פרטים לחינה מושלמת</text>
          </svg></div>""", unsafe_allow_html=True)
    elif evt == "barmitzvah":
        st.markdown("""<div style="text-align:center;padding:1rem 0;opacity:.7">
          <svg viewBox="0 0 260 120" xmlns="http://www.w3.org/2000/svg" style="max-width:240px;width:90%">
            <polygon points="130,12 145,38 115,38" fill="none" stroke="#1a6bb5" stroke-width="2" opacity=".6"/>
            <polygon points="130,50 115,24 145,24" fill="none" stroke="#1a6bb5" stroke-width="2" opacity=".6"/>
            <rect x="45" y="58" width="26" height="40" rx="13" fill="#1a6bb5" opacity=".35"/>
            <rect x="51" y="55" width="5" height="46" rx="2" fill="#e8c97e" opacity=".5"/>
            <rect x="65" y="55" width="5" height="46" rx="2" fill="#e8c97e" opacity=".5"/>
            <rect x="189" y="58" width="26" height="40" rx="13" fill="#1a6bb5" opacity=".35"/>
            <rect x="195" y="55" width="5" height="46" rx="2" fill="#e8c97e" opacity=".5"/>
            <rect x="209" y="55" width="5" height="46" rx="2" fill="#e8c97e" opacity=".5"/>
            <circle cx="28" cy="40" r="11" fill="#1a6bb5" opacity=".25"/>
            <circle cx="232" cy="40" r="11" fill="#e8c97e" opacity=".25"/>
            <text x="130" y="110" text-anchor="middle" font-family="serif" font-size="11" fill="#e8c97e" opacity=".6" font-style="italic">מזל טוב! הזן פרטים לחגיגה מושלמת</text>
          </svg></div>""", unsafe_allow_html=True)

if st.button("✨ הפק המלצה מיידית", key="gen"):
    if not st.session_state.active_cats:
        st.error("בחר לפחות סוג אחד")
    else:
        # Confetti
        colors = ecfg["confetti"]
        pieces = ""
        for i in range(70):
            c   = random.choice(colors)
            lft = random.randint(3,97)
            dur = random.uniform(1.2,2.5)
            dly = random.uniform(0,0.5)
            sz  = random.choice(["6px","8px","5px","10px"])
            pieces += f'<div class="cp" style="left:{lft}%;background:{c};width:{sz};height:{sz};animation-duration:{dur:.1f}s;animation-delay:{dly:.1f}s"></div>'
        st.markdown(f'<div class="confetti-wrap">{pieces}</div>', unsafe_allow_html=True)

        with st.spinner(random.choice(ecfg["loading"])):
            import time; time.sleep(0.5)

        st.session_state.rec       = auto_rec(df, g, st.session_state.style, st.session_state.active_cats)
        st.session_state.extras    = []
        st.session_state.specials  = []
        st.session_state.edit_open = None
        st.session_state.generated = True
        st.session_state._counted  = False
        st.rerun()

# ══════════════════════════════════════
# RESULTS
# ══════════════════════════════════════
if st.session_state.generated and st.session_state.rec:
    rec     = st.session_state.rec
    guests  = st.session_state.guests
    budget  = st.session_state.budget
    couple  = st.session_state.couple_name.strip()

    total_alc  = 0.0
    total_mix  = 0.0
    mixer_cups = {}

    # Counter
    if not st.session_state.get("_counted", False):
        send_analytics(st.session_state.style, guests)
        st.session_state._counted = True

    # Blessing
    blessing = ecfg["blessing"]
    name_part = f"מזל טוב {couple}! " if couple else "מזל טוב! "
    st.markdown(f"""
    <div style="text-align:center;padding:1rem .5rem .5rem">
      <div style="font-family:'Dancing Script',cursive;font-size:1.5rem;
           color:{e_gold};animation:fadeDown .5s ease both">{name_part}</div>
      <div style="font-family:Frank Ruhl Libre,serif;
           font-size:.95rem;color:var(--text-mid);margin-top:.2rem">{blessing}</div>
    </div>
    <div style="text-align:center;color:{e_acc};opacity:.4;font-size:.9rem;
         letter-spacing:.4em;margin-bottom:.5rem">✦ &nbsp; ✦ &nbsp; ✦</div>
    """, unsafe_allow_html=True)

    _title = f"🥂 *רשימת האלכוהול של {couple}*" if couple else "🥂 *רשימת אלכוהול*"
    share_lines = [_title, f"👥 {guests} אורחים | {nd(guests)} שותים", ""]

    st.markdown(f'<div class="sec">{ecfg["emoji"]} ההמלצה שלך</div>', unsafe_allow_html=True)

    # ── Main alcohol cards ──
    for cat in list(rec.keys()):
        info = rec[cat]
        item = calc_item(df, cat, info["brand"], info["pct"], guests, st.session_state.get("hours",4))
        total_alc += item["total"]
        if not has_split:
            share_lines.append(f"{CAT_EMJ[cat]} {item['brand_he']}: {item['n']} בקבוקים (₪{item['total']:.0f})")

        lvl_key    = item["level"].lower() if item["level"] else "basic"
        badge_html = BADGE_MAP.get(lvl_key, "")

        if cat=="Vodka":
            cups_m = math.ceil(item["drinkers"] * get_cups() * SAFETY)
            for m in ["energy","cranberry","russian"]:
                mixer_cups[m] = mixer_cups.get(m,0) + cups_m
        if cat=="Anis":
            cups_m = math.ceil(item["drinkers"] * get_cups() * SAFETY)
            mixer_cups["lemonade"] = mixer_cups.get("lemonade",0) + cups_m

        cc = CAT_COLOR.get(cat, {"gold":"var(--gold)","bg":"var(--bg2)","border":"var(--border)","dim":"var(--border-dim)","text":"var(--text-dim)","mid":"var(--text-mid)"})

        # בדוק אם יש מותגים נוספים לקטגוריה זו
        sub_brands = [(i,e) for i,e in enumerate(st.session_state.extras)
                      if e.get("cat")==cat]
        has_split  = len(sub_brands) > 0

        if has_split:
            # חשב כל מותג
            total_extra_split = sum(e.get("split_pct",20) for _,e in sub_brands)
            main_split_pct    = max(10, 100 - total_extra_split)
            all_brands_card   = [(info["brand"], main_split_pct, item, False)] +                                 [(e["brand"], e.get("split_pct",20),
                                  calc_item(df, cat, e["brand"],
                                            round(item["pct"] * e.get("split_pct",20) / 100) or 5,
                                            guests, st.session_state.get("hours",4)),
                                  e.get("flavor_type","regular")=="flavored")
                                 for _,e in sub_brands]
            total_n_all   = sum(b[2]["n"] for b in all_brands_card)
            total_cost_all= sum(b[2]["total"] for b in all_brands_card)
            total_alc    += total_cost_all - item["total"]  # כבר הוסיף item["total"] למעלה

            # split bar
            colors_card = [cc["gold"],"#a07040","#9b72cf","#7ab648"]
            bar_html    = "".join(f'<div style="width:{b[1]}%;background:{colors_card[i%4]};height:100%;opacity:{0.9-i*0.1}"></div>' for i,b in enumerate(all_brands_card))
            lbl_html    = "".join(f'<span style="font-size:.68rem;color:{cc["mid"]}">{brand_display(get_prod(df,cat,b[0]))} {b[1]}%</span>' for b in all_brands_card)

            st.markdown(f"""
            <div style="background:{cc['bg']};border:1.5px solid {cc['border']};
                 border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.5rem;
                 animation:fadeUp .4s ease both">
              <div class="r-head" style="margin-bottom:.4rem">
                <div class="r-left">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:1.05rem;font-weight:700;color:{cc['gold']}">{CAT_HE[cat]}</div>
                  <div style="font-size:.75rem;color:{cc['text']};margin-top:.1rem">{len(all_brands_card)} מותגים · {item['pct']}% שותים · {item['drinkers']} אנשים</div>
                </div>
                <div class="r-right">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:2.2rem;font-weight:900;color:{cc['gold']};line-height:1">{total_n_all}</div>
                  <div class="r-num-lbl" style="color:{cc['text']}">בקבוקים</div>
                </div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:.25rem">{lbl_html}</div>
              <div style="height:7px;border-radius:4px;overflow:hidden;display:flex;margin-bottom:.6rem">{bar_html}</div>""", unsafe_allow_html=True)

            for i_b, (br, sp_pct, it_b, is_flav) in enumerate(all_brands_card):
                c_b  = colors_card[i_b % 4]
                he_b = brand_display(get_prod(df, cat, br))
                flav_tag = ' 🍹' if is_flav else ''
                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.15);border:1px solid {cc['dim']};
                     border-radius:10px;padding:.5rem .8rem;margin-bottom:.3rem;
                     display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-size:.83rem;font-weight:700;color:{c_b}">{he_b}{flav_tag}</div>
                    <div style="font-size:.7rem;color:{cc['text']};margin-top:.05rem">{sp_pct}% · ₪{it_b['ppb']:.0f}/בקבוק</div>
                  </div>
                  <div style="text-align:left">
                    <div style="font-family:Frank Ruhl Libre,serif;font-size:1.3rem;font-weight:700;color:{c_b}">{it_b['n']}</div>
                    <div style="font-size:.65rem;color:{cc['text']}">₪{it_b['total']:.0f}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
              <div style="display:flex;justify-content:space-between;padding-top:.5rem;
                   border-top:1px solid {cc['dim']};font-size:.82rem;color:{cc['mid']}">
                <span>סה"כ</span>
                <span style="color:{cc['gold']};font-weight:700">₪{total_cost_all:.0f}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            share_lines.append(f"{CAT_EMJ[cat]} {CAT_HE[cat].split()[0]}: {total_n_all} בקבוקים (₪{total_cost_all:.0f})")

        else:
            # כרטיס רגיל — מותג אחד
            st.markdown(f"""
            <div style="background:{cc['bg']};border:1px solid {cc['border']};
                 border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.8rem;
                 transition:border-color .2s;animation:fadeUp .4s ease both">
              <div class="r-head">
                <div class="r-left">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:1.05rem;font-weight:700;color:{cc['gold']}">{CAT_HE[cat]}</div>
                  <div style="font-size:.78rem;color:{cc['text']};margin-top:.1rem">{item['brand_he']} &nbsp;{badge_html}</div>
                </div>
                <div class="r-right">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:2.2rem;font-weight:900;color:{cc['gold']};line-height:1;animation:popIn .4s ease both">{item['n']}</div>
                  <div class="r-num-lbl" style="color:{cc['text']}">בקבוקים</div>
                </div>
              </div>
              <div style="display:flex;justify-content:space-between;padding:.28rem 0;border-bottom:1px solid {cc['dim']};font-size:.82rem;color:{cc['mid']}"><span>נפח</span><span>{item['vol']} מ"ל</span></div>
              <div style="display:flex;justify-content:space-between;padding:.28rem 0;border-bottom:1px solid {cc['dim']};font-size:.82rem;color:{cc['mid']}"><span>שותים ({item['pct']}%)</span><span>{item['drinkers']} אנשים</span></div>
              <div style="display:flex;justify-content:space-between;padding:.28rem 0;border-bottom:1px solid {cc['dim']};font-size:.82rem;color:{cc['mid']}"><span>מחיר לבקבוק</span><span>₪{item['ppb']:.0f}</span></div>
              <div style="display:flex;justify-content:space-between;padding:.28rem 0;font-size:.82rem;color:{cc['mid']}"><span>סה"כ</span><span style="color:{cc['gold']};font-weight:700">₪{item['total']:.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)

        # ── כפתור ⚙️ אחד — פותח פאנל עריכה ──
        is_open = st.session_state.edit_open == f"edit_{cat}"
        btn_lbl = f"✕ סגור" if is_open else f"⚙️ ערוך"
        btn_cls = "btn-ghost" if not is_open else "btn-ghost"
        st.markdown(f'<div class="{btn_cls}">', unsafe_allow_html=True)
        if st.button(btn_lbl, key=f"gear_{cat}", use_container_width=True):
            st.session_state.edit_open = f"edit_{cat}" if not is_open else None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # ── פאנל עריכה מאוחד ──
        if st.session_state.edit_open == f"edit_{cat}":
            cc_p = CAT_COLOR.get(cat, {"gold":"var(--gold)","dim":"var(--border-dim)","text":"var(--text-dim)","mid":"var(--text-mid)","bg":"var(--bg2)","border":"var(--border)"})
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:Frank Ruhl Libre,serif;font-size:.95rem;color:{cc_p["gold"]};margin-bottom:.8rem;text-align:center">⚙️ עריכת {CAT_HE[cat]}</div>', unsafe_allow_html=True)

            # ── מותג ראשי ──
            st.markdown('<div style="font-size:.78rem;color:var(--text-dim);margin-bottom:.3rem">✏️ מותג ראשי</div>', unsafe_allow_html=True)
            bdf  = get_brands(df, cat, flavor="regular")
            opts = bdf['brand'].tolist()
            cur  = opts.index(info["brand"]) if info["brand"] in opts else 0
            chosen = st.selectbox("מותג", options=opts, index=cur,
                format_func=lambda x, d=bdf: f"{brand_display(d[d['brand']==x].iloc[0])}  [{d[d['brand']==x].iloc[0]['level']}]  ₪{d[d['brand']==x].iloc[0]['price']:.0f}",
                key=f"sel_{cat}", label_visibility="collapsed")

            # ── % כולל ──
            st.markdown('<div style="font-size:.78rem;color:var(--text-dim);margin:.6rem 0 .3rem">📊 % שותים (סה"כ קטגוריה)</div>', unsafe_allow_html=True)
            cur_pct = info["pct"]
            new_pct = st.number_input("אחוז שותים", 5, 80, cur_pct, 5,
                                       key=f"pct_inp_{cat}", label_visibility="collapsed")
            new_d = math.ceil(nd(guests) * new_pct / 100)
            st.markdown(f'<div class="nbox" style="margin:.2rem 0 .5rem">{new_d} אנשים ישתו {CAT_HE[cat]}</div>', unsafe_allow_html=True)

            # ── מותגים נוספים קיימים ──
            extras_this_cat = [(i,e) for i,e in enumerate(st.session_state.extras)
                               if e.get("cat")==cat and e.get("flavor_type","regular")=="regular"]
            flav_extras     = [(i,e) for i,e in enumerate(st.session_state.extras)
                               if e.get("cat")=="Vodka" and e.get("flavor_type","regular")=="flavored"] if cat=="Vodka" else []

            if extras_this_cat or flav_extras:
                st.markdown('<div style="height:.3rem"></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:.75rem;color:var(--text-dim);margin-bottom:.4rem">🔀 מותגים נוספים</div>', unsafe_allow_html=True)

            for i_e, e_item in extras_this_cat:
                he_e = brand_display(get_prod(df, cat, e_item["brand"]))
                sp_  = e_item.get("split_pct", 20)
                # selectbox לבחירת מותג
                ex_bdf  = get_brands(df, cat, flavor="regular")
                ex_opts = ex_bdf['brand'].tolist()
                ex_cur  = ex_opts.index(e_item["brand"]) if e_item["brand"] in ex_opts else 0
                st.markdown(f'<div style="font-size:.72rem;color:{cc_p["gold"]};margin-bottom:.2rem">מותג {i_e+2}</div>', unsafe_allow_html=True)
                ex_chosen = st.selectbox(f"מותג {i_e+2}", ex_opts, index=ex_cur,
                    format_func=lambda x, d=ex_bdf: f"{brand_display(d[d['brand']==x].iloc[0])}  [{d[d['brand']==x].iloc[0]['level']}]  ₪{d[d['brand']==x].iloc[0]['price']:.0f}",
                    key=f"ex_sel2_{i_e}", label_visibility="collapsed")
                new_sp = st.number_input(f"% חלוקה למותג {i_e+2}", 5, 80, sp_, 5,
                                         key=f"sp_pct2_{i_e}", label_visibility="visible")
                if ex_chosen != e_item["brand"]:
                    st.session_state.extras[i_e]["brand"] = ex_chosen; st.rerun()
                if new_sp != sp_:
                    st.session_state.extras[i_e]["split_pct"] = int(new_sp); st.rerun()
                st.markdown('<div class="btn-danger" style="margin-bottom:.4rem">', unsafe_allow_html=True)
                if st.button(f"🗑️ הסר {he_e}", key=f"rm_ex2_{i_e}", use_container_width=True):
                    st.session_state.extras.pop(i_e); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # וודקה בטעמים
            for i_f, e_f in flav_extras:
                fd      = get_brands(df,"Vodka",flavor="flavored")
                fo_opts = fd['brand'].tolist()
                fo_cur  = fo_opts.index(e_f["brand"]) if e_f["brand"] in fo_opts else 0
                st.markdown(f'<div style="font-size:.72rem;color:#9b72cf;margin-bottom:.2rem">🍹 וודקה בטעמים</div>', unsafe_allow_html=True)
                f_chosen = st.selectbox("טעם", fo_opts, index=fo_cur,
                    format_func=lambda x, d=fd: f"{brand_display(d[d['brand']==x].iloc[0])}  ₪{d[d['brand']==x].iloc[0]['price']:.0f}",
                    key=f"flav_sel2_{i_f}", label_visibility="collapsed")
                f_sp = st.number_input("% טעמים", 5, 40, e_f.get("split_pct",15), 5,
                                        key=f"flav_sp2_{i_f}", label_visibility="visible")
                if f_chosen != e_f["brand"]: st.session_state.extras[i_f]["brand"] = f_chosen; st.rerun()
                if f_sp != e_f.get("split_pct",15): st.session_state.extras[i_f]["split_pct"] = int(f_sp); st.rerun()
                st.markdown('<div class="btn-danger" style="margin-bottom:.4rem">', unsafe_allow_html=True)
                if st.button("🗑️ הסר וודקה בטעמים", key=f"rm_flav2_{i_f}", use_container_width=True):
                    st.session_state.extras.pop(i_f); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # ── כפתורי הוספה ──
            st.markdown('<div style="height:.3rem"></div>', unsafe_allow_html=True)
            exist_brands = [info["brand"]] + [e["brand"] for _,e in extras_this_cat]
            add_bdf = get_brands(df, cat, flavor="regular")
            add_bdf = add_bdf[~add_bdf['brand'].isin(exist_brands)]
            if not add_bdf.empty:
                # Toggle להוספת מותג נוסף
                show_add_key = f"show_add_{cat}"
                if st.session_state.get(show_add_key, False):
                    add_opts = add_bdf['brand'].tolist()
                    st.markdown(f'<div style="font-size:.72rem;color:{cc_p["gold"]};margin-bottom:.2rem">➕ בחר מותג נוסף</div>', unsafe_allow_html=True)
                    new_brand_idx = st.selectbox("בחר מותג להוספה", range(len(add_opts)),
                        format_func=lambda x, d=add_bdf: f"{brand_display(d[d['brand']==add_opts[x]].iloc[0])}  [{d[d['brand']==add_opts[x]].iloc[0]['level']}]  ₪{d[d['brand']==add_opts[x]].iloc[0]['price']:.0f}",
                        key=f"new_brand_sel_{cat}", label_visibility="collapsed")
                    c_add1, c_add2 = st.columns(2)
                    with c_add1:
                        if st.button("✅ הוסף", key=f"confirm_add_{cat}", use_container_width=True):
                            st.session_state.extras.append({
                                "brand": add_opts[new_brand_idx], "cat": cat,
                                "pct": 0, "split_pct": 20, "flavor_type": "regular"
                            })
                            st.session_state[show_add_key] = False; st.rerun()
                    with c_add2:
                        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                        if st.button("✕ ביטול", key=f"cancel_add_{cat}", use_container_width=True):
                            st.session_state[show_add_key] = False; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="btn-add">', unsafe_allow_html=True)
                    cat_name = CAT_HE[cat].split()[0]
                    if st.button(f"➕ הוסף מותג {cat_name} נוסף", key=f"add_extra_{cat}", use_container_width=True):
                        st.session_state[show_add_key] = True; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # וודקה בטעמים כפתור
            if cat == "Vodka" and not flav_extras:
                fd = get_brands(df,"Vodka",flavor="flavored")
                if not fd.empty:
                    show_flav_key = "show_add_flav"
                    if st.session_state.get(show_flav_key, False):
                        fo_add = fd['brand'].tolist()
                        st.markdown('<div style="font-size:.72rem;color:#9b72cf;margin-bottom:.2rem">🍹 בחר וודקה בטעמים</div>', unsafe_allow_html=True)
                        flav_idx = st.selectbox("בחר טעם", range(len(fo_add)),
                            format_func=lambda x, d=fd: f"{brand_display(d[d['brand']==fo_add[x]].iloc[0])}  ₪{d[d['brand']==fo_add[x]].iloc[0]['price']:.0f}",
                            key="new_flav_sel", label_visibility="collapsed")
                        cf1, cf2 = st.columns(2)
                        with cf1:
                            if st.button("✅ הוסף", key="confirm_flav", use_container_width=True):
                                st.session_state.extras.append({
                                    "brand": fo_add[flav_idx], "cat": "Vodka",
                                    "pct": 0, "split_pct": 15, "flavor_type": "flavored"
                                })
                                st.session_state[show_flav_key] = False; st.rerun()
                        with cf2:
                            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                            if st.button("✕ ביטול", key="cancel_flav", use_container_width=True):
                                st.session_state[show_flav_key] = False; st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="btn-add">', unsafe_allow_html=True)
                        if st.button("🍹 הוסף וודקה בטעמים", key="add_flav_btn", use_container_width=True):
                            st.session_state[show_flav_key] = True; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)

            # ── שמור / ביטול / הסר ──
            if st.button("✅ שמור שינויים", key=f"ok_{cat}", use_container_width=True):
                st.session_state.rec[cat]["brand"] = chosen
                st.session_state.rec[cat]["pct"]   = int(new_pct)
                # נקה toggle states
                st.session_state.pop(f"show_add_{cat}", None)
                st.session_state.pop("show_add_flav", None)
                st.session_state.edit_open = None; st.rerun()
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("✕ ביטול", key=f"cancel_{cat}", use_container_width=True):
                st.session_state.edit_open = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
            if st.button("🗑️ הסר קטגוריה זו", key=f"del_{cat}", use_container_width=True):
                del st.session_state.rec[cat]
                if cat in st.session_state.active_cats: st.session_state.active_cats.remove(cat)
                st.session_state.edit_open = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Extras — grouped by cat with split bar ──
    extras_by_cat = {}
    for idx, ve in enumerate(st.session_state.extras):
        cat_e = ve.get("cat","Vodka")
        if cat_e not in extras_by_cat:
            extras_by_cat[cat_e] = []
        extras_by_cat[cat_e].append((idx, ve))

    for cat_e, items_e in extras_by_cat.items():
        cc_e = CAT_COLOR.get(cat_e, {"gold":"var(--gold)","bg":"var(--bg2)","border":"var(--border)","dim":"var(--border-dim)","text":"var(--text-dim)","mid":"var(--text-mid)"})
        main_brand = rec.get(cat_e,{}).get("brand","")
        main_pct   = rec.get(cat_e,{}).get("pct",0)
        main_it    = calc_item(df, cat_e, main_brand, main_pct, guests, st.session_state.get("hours",4)) if main_brand else None

        # חשב כל extra
        extra_items = []
        for idx_e, ve in items_e:
            it_e = calc_item(df, cat_e, ve["brand"], ve["pct"], guests, st.session_state.get("hours",4))
            total_alc += it_e["total"]
            share_lines.append(f"➕ {it_e['brand_he']}: {it_e['n']} בקבוקים (₪{it_e['total']:.0f})")
            extra_items.append((idx_e, ve, it_e))

        # כרטיס מאוחד אם יש גם main
        if main_it and cat_e in rec:
            total_n   = main_it["n"] + sum(i[2]["n"] for i in extra_items)
            total_cat = main_it["total"] + sum(i[2]["total"] for i in extra_items)
            total_pct_all = main_pct + sum(i[1]["pct"] for i in extra_items)

            # בנה split bar
            split_bars = ""
            split_labels = ""
            colors_split = ["#d4934a","#a07040","#7a5030","#5a3820"]
            all_brands_split = [(main_brand, main_pct, main_it["n"], brand_display(get_prod(df, cat_e, main_brand)))] +                                [(i[1]["brand"], i[1]["pct"], i[2]["n"], i[2]["brand_he"]) for i in extra_items]
            total_pct_sum = sum(b[1] for b in all_brands_split)

            for bi, (br, pct_b, n_b, he_b) in enumerate(all_brands_split):
                w = round(pct_b / total_pct_sum * 100) if total_pct_sum > 0 else 0
                c = colors_split[bi % len(colors_split)]
                split_bars += f'<div style="width:{w}%;background:{c};height:100%;opacity:{0.9 - bi*0.15}"></div>'
                split_labels += f'<span style="font-size:.68rem;color:{cc_e["mid"]}">{he_b} {w}%</span>'

            st.markdown(f"""
            <div style="background:{cc_e['bg']};border:1.5px solid {cc_e['border']};
                 border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.5rem;
                 animation:fadeUp .4s ease both">
              <div class="r-head" style="margin-bottom:.5rem">
                <div class="r-left">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:1.05rem;font-weight:700;color:{cc_e['gold']}">{CAT_HE[cat_e]}</div>
                  <div style="font-size:.75rem;color:{cc_e['text']};margin-top:.1rem">{len(all_brands_split)} מותגים · {total_pct_all}% שותים</div>
                </div>
                <div class="r-right">
                  <div style="font-family:Frank Ruhl Libre,serif;font-size:2.2rem;font-weight:900;color:{cc_e['gold']};line-height:1">{total_n}</div>
                  <div class="r-num-lbl" style="color:{cc_e['text']}">בקבוקים</div>
                </div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:.3rem">
                {split_labels}
              </div>
              <div style="height:8px;border-radius:4px;overflow:hidden;display:flex;margin-bottom:.7rem">
                {split_bars}
              </div>""", unsafe_allow_html=True)

            # תת-כרטיסים
            for bi, (br, pct_b, n_b, he_b) in enumerate(all_brands_split):
                c = colors_split[bi % len(colors_split)]
                ppb = get_prod(df, cat_e, br)["price"]
                t   = n_b * ppb
                st.markdown(f"""
                <div style="background:{cc_e['bg']};border:1px solid rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.25);
                     border-radius:10px;padding:.6rem .8rem;margin-bottom:.35rem;
                     display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-size:.83rem;font-weight:700;color:{c}">{he_b}</div>
                    <div style="font-size:.7rem;color:{cc_e['text']};margin-top:.1rem">{pct_b}% · ₪{ppb:.0f} לבקבוק</div>
                  </div>
                  <div style="text-align:left">
                    <div style="font-family:Frank Ruhl Libre,serif;font-size:1.4rem;font-weight:700;color:{c}">{n_b}</div>
                    <div style="font-size:.65rem;color:{cc_e['text']}">₪{t:.0f}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
              <div style="display:flex;justify-content:space-between;align-items:center;
                   padding-top:.5rem;border-top:1px solid {cc_e['dim']}">
                <div style="font-size:.82rem;color:{cc_e['mid']}">סה"כ <span style="color:{cc_e['gold']};font-weight:700">₪{total_cat:.0f}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)

            # כפתורי עריכה extras
            for idx_e, ve, it_e in extra_items:
                ex_open = st.session_state.edit_open == f"ex_{idx_e}"
                st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                if st.button(f"✕ סגור" if ex_open else f"⚙️ ערוך {it_e['brand_he']}", key=f"ex_gear_{idx_e}", use_container_width=True):
                    st.session_state.edit_open = f"ex_{idx_e}" if not ex_open else None; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                if ex_open:
                    st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
                    ex_bdf  = get_brands(df, cat_e)
                    ex_opts = ex_bdf['brand'].tolist()
                    ex_cur  = ex_opts.index(ve["brand"]) if ve["brand"] in ex_opts else 0
                    ex_chosen = st.selectbox("מותג", ex_opts, index=ex_cur,
                        format_func=lambda x, d=ex_bdf: f"{brand_display(d[d['brand']==x].iloc[0])}  [{d[d['brand']==x].iloc[0]['level']}]  ₪{d[d['brand']==x].iloc[0]['price']:.0f}",
                        key=f"ex_sel_{idx_e}", label_visibility="collapsed")
                    ex_pct = st.number_input("% שותים", 5, 40, ve["pct"], 5, key=f"ex_pct_{idx_e}", label_visibility="collapsed")
                    if st.button("✅ שמור", key=f"ex_ok_{idx_e}", use_container_width=True):
                        st.session_state.extras[idx_e]["brand"] = ex_chosen
                        st.session_state.extras[idx_e]["pct"]   = int(ex_pct)
                        st.session_state.edit_open = None; st.rerun()
                    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                    if st.button("🗑️ הסר", key=f"del_ex_{idx_e}"): st.session_state.extras.pop(idx_e); st.rerun()
                    st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            # extra בלי main — הצג כרטיס רגיל
            for idx_e, ve, it_e in extra_items:
                total_alc += 0  # already counted above
                st.markdown(f"""
                <div style="background:{cc_e['bg']};border:1px solid {cc_e['border']};
                     border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.8rem">
                  <div class="r-head">
                    <div class="r-left">
                      <div style="font-size:1.05rem;font-weight:700;color:{cc_e['gold']}">{CAT_HE[cat_e]}</div>
                      <div style="font-size:.78rem;color:{cc_e['text']}">{it_e['brand_he']}</div>
                    </div>
                    <div class="r-right">
                      <div style="font-size:2.2rem;font-weight:900;color:{cc_e['gold']};line-height:1">{it_e['n']}</div>
                      <div style="font-size:.65rem;color:{cc_e['text']}">בקבוקים</div>
                    </div>
                  </div>
                  <div style="display:flex;justify-content:space-between;font-size:.82rem;color:{cc_e['mid']}">
                    <span>שותים ({ve['pct']}%)</span><span>{it_e['drinkers']} אנשים</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;font-size:.82rem;color:{cc_e['mid']};margin-top:.2rem">
                    <span>סה"כ</span><span style="color:{cc_e['gold']};font-weight:700">₪{it_e['total']:.0f}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
                if st.button("🗑️ הסר", key=f"del_ex_{idx_e}"): st.session_state.extras.pop(idx_e); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Specials ──
    for idx, sp in enumerate(st.session_state.specials):
        it = calc_item(df, sp["category"], sp["brand"], sp["pct"], guests, st.session_state.get("hours",4))
        total_alc += it["total"]
        share_lines.append(f"👑 {it['brand_he']}: {it['n']} בקבוקים (₪{it['total']:.0f})")
        st.markdown(f"""
        <div class="sp-card">
          <div class="r-head">
            <div class="r-left"><div class="r-cat">👑 יוקרה</div>
            <div class="r-brand">{it['brand_he']} {BADGE_MAP.get('special','')}</div></div>
            <div class="r-right"><div class="r-num">{it['n']}</div><div class="r-num-lbl">בקבוקים</div></div>
          </div>
          <div class="r-row"><span>שותים ({sp['pct']}%)</span><span>{it['drinkers']} אנשים</span></div>
          <div class="r-row"><span>מחיר לבקבוק</span><span>₪{it['ppb']:.0f}</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{it['total']:.0f}</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑️ הסר", key=f"del_sp_{idx}"): st.session_state.specials.pop(idx); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Add buttons — רק יוקרה נשאר כפתור נפרד ──
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-sp">', unsafe_allow_html=True)
    if st.button("👑 הוסף בקבוק יוקרה", key="asp", use_container_width=True):
        st.session_state.show_sp   = not st.session_state.show_sp
        st.session_state.show_flav = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_sp:
        sp_raw = df[df['level'].str.lower()=='special'].copy()
        if not sp_raw.empty:
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            p_sp  = sp_raw[sp_raw['volume_ml']==1000]
            if p_sp.empty: p_sp = sp_raw[sp_raw['volume_ml']==700]
            sp_cl = p_sp.drop_duplicates('brand').reset_index(drop=True)
            si = st.selectbox("בחר מוצר:",range(len(sp_cl)),format_func=lambda x,d=sp_cl:fmt_b(d.iloc[x]),key="si")
            sp_ = st.number_input("% מהשותים שיקבלו בקבוק זה",2,20,5,1,key="sip")
            if st.button("✅ הוסף",key="si_ok"):
                st.session_state.specials.append({"brand":sp_cl.iloc[si]['brand'],"category":sp_cl.iloc[si]['category'],"pct":int(sp_)})
                st.session_state.show_sp = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="nbox">עדכן level=Special לבקבוקי יוקרה בגיליון</div>', unsafe_allow_html=True)

    # ── Mixers ──
    if mixer_cups and mx_df is not None and not mx_df.empty:
        st.markdown('<div class="sec">🧃 מיקסרים</div>', unsafe_allow_html=True)

        cur_e = st.session_state.get("energy_choice","XL")
        new_e = st.radio("⚡ סוג משקה אנרגי:", ["XL","Blue"],
                         index=["XL","Blue"].index(cur_e),
                         horizontal=True, key="energy_r")
        if new_e != cur_e:
            st.session_state.energy_choice = new_e; st.rerun()

        mix_results = mixer_calc(mixer_cups, mx_df, st.session_state.venue_map,
                                 st.session_state.get("energy_choice","XL"))

        share_lines.append(""); share_lines.append("🧃 *מיקסרים:*")
        st.markdown('<div class="mix-card"><div class="mix-hdr">אומדן מיקסרים</div>', unsafe_allow_html=True)
        for mr in mix_results:
            by_v  = mr["by_venue"]
            if not by_v: total_mix += mr["cost"]
            venue_tag = '<span style="background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.2);border-radius:20px;padding:.1rem .45rem;font-size:.65rem;color:#4ade80">✓ האולם מביא</span>' if by_v else ""
            qty_txt   = f'<s style="color:var(--text-dim)">~{mr["crates"]} ארגזים</s>' if by_v else f'<b>~{mr["crates"]} ארגזים</b>'
            cost_txt  = "₪0" if by_v else (f'₪{mr["cost"]:.0f} <span style="font-size:.7rem;color:var(--text-dim)">(₪{mr["ppc"]:.0f}/ארגז)</span>' if mr["ppc"]>0 else f'₪{mr["cost"]:.0f}')
            share_lines.append(f"{'✅' if by_v else '•'} {mr['name']}: ~{mr['crates']} ארגזים")
            st.markdown(f"""
            <div class="mix-row">
              <div style="display:flex;align-items:center;gap:.4rem">
                <span style="font-size:16px">{MIXER_EMJ.get(mr['key'],'🍶')}</span>
                <div><div style="font-size:.83rem;color:var(--text)">{mr['name']} {venue_tag}</div>
                <div style="font-size:.72rem;color:var(--text-dim)">~{mr['units']} יח' · {mr['crate_size']} יח' לארגז</div></div>
              </div>
              <div style="text-align:left"><div style="font-size:.9rem;font-weight:700;color:var(--gold)">{qty_txt}</div>
              <div style="font-size:.72rem;color:var(--text-dim)">{cost_txt}</div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Venue toggles
        st.markdown('<div class="edit-pnl" style="margin-top:.4rem">', unsafe_allow_html=True)
        st.markdown("**🏛️ מה האולם מביא?**")
        seen = set()
        for mr in mix_results:
            vk = mr["key"]
            if vk in seen: continue
            seen.add(vk)
            cur_v  = st.session_state.venue_map.get(vk, False)
            new_v  = st.checkbox(f'{MIXER_EMJ.get(vk,"🍶")} {mr["name"]}', value=cur_v, key=f"ven_{vk}")
            if new_v != cur_v:
                st.session_state.venue_map[vk] = new_v; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Total ──
    total_cost = total_alc + total_mix
    share_lines.append(f"\n💰 *אלכוהול: ₪{total_alc:,.0f}*")
    if total_mix > 0: share_lines.append(f"🧃 *מיקסרים: ₪{total_mix:,.0f}*")
    share_lines.append(f"✨ *סה\"כ: ₪{total_cost:,.0f}*")

    if budget:
        pct_u  = min(total_cost/budget, 1.0)
        b_clr  = "#4ade80" if pct_u < 0.85 else ("#f5d78e" if pct_u < 1.0 else "#f87171")
        in_b   = total_cost <= budget
        status = f"✅ חוסך ₪{budget-total_cost:,.0f}" if in_b else f"❌ חורג ב-₪{total_cost-budget:,.0f}"
        c_main = "var(--green)" if in_b else "var(--red)"
        st.markdown(f"""
        <div class="total-strip">
          <div>
            <div style="font-size:.75rem;color:var(--text-dim)">סה"כ עלות</div>
            <div class="total-main" style="color:{c_main}">₪{total_cost:,.0f}</div>
            <div style="font-size:.72rem;color:var(--text-dim);margin-top:.2rem">{status}</div>
          </div>
          <div style="text-align:left">
            <div style="font-size:.72rem;color:var(--text-dim)">מתוך ₪{budget:,.0f}</div>
            <div class="budget-bar"><div class="budget-fill" style="width:{pct_u*100:.0f}%;background:{b_clr}"></div></div>
            <div style="font-size:.72rem;color:var(--text-dim);margin-top:.3rem">{nd(guests)} שותים</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        sub_txt = f"{nd(guests)} שותים"
        if total_mix > 0: sub_txt += f" · אלכוהול ₪{total_alc:,.0f} + מיקסרים ₪{total_mix:,.0f}"
        st.markdown(f"""
        <div class="total-strip">
          <div>
            <div style="font-size:.75rem;color:var(--text-dim)">סה"כ עלות</div>
            <div class="total-main">₪{total_cost:,.0f}</div>
          </div>
          <div style="text-align:left;font-size:.72rem;color:var(--text-dim)">{sub_txt}</div>
        </div>""", unsafe_allow_html=True)

    # Auto-save
    _state = {}
    for _k in ["guests","budget","use_b","style","active_cats","rec","extras","specials","venue_map","generated","couple_name","hours","event_type"]:
        try:
            _v = st.session_state.get(_k)
            json.dumps(_v); _state[_k] = _v
        except: pass
    _sj = json.dumps(_state, ensure_ascii=False)
    st.components.v1.html(f"<script>try{{localStorage.setItem('weddingApp',{repr(_sj)})}}catch(e){{}}</script>", height=0)

    # ── FAQ ──
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    with st.expander("❓ שאל את הבר — שאלות נפוצות"):
        faqs = [
            ("כמה וודקה לחתונה עם 200 אורחים?",
             "עם 200 אורחים כ-160 שותים. אם 40% שותים וודקה (~64 איש) לאירוע של 4 שעות — כ-10-11 בקבוקי ליטר. הפעל את החישוב עם 200 אורחים לתוצאה מדויקת."),
            ('האם עדיף לקנות בקבוקי ליטר או 700 מ"ל?',
             'בקבוקי ליטר כמעט תמיד משתלמים יותר מבחינת מחיר למ"ל. ה-700 שימושי לוודקות בטעמים או לשולחנות ספציפיים.'),
            ("כמה מרווח ביטחון להוסיף?",
             "האפליקציה כוללת 10% מרווח אוטומטי. לחתונות מעל 300 אורחים מומלץ להוסיף עוד 5% ידנית."),
            ("מה ההבדל בין Basic לPremium?",
             "Basic = מותגים כמו פינלנדיה, ג'וני ווקר רד — איכות טובה במחיר נגיש. Premium = בלוגה, גריי גוס, בלאק לייבל — מותגים יוקרתיים."),
            ("האם לחשב מיקסרים כחלק מהתקציב?",
             "כן! מיקסרים יכולים להוסיף 15-25% לעלות. האפליקציה מחשבת זאת אוטומטית. אם האולם מספק — סמן 'האולם מביא'."),
            ("מתי הזמן הנכון לקנות?",
             "אלכוהול: 1-2 חודשים לפני — מחירים יציבים. מיקסרים: שבוע לפני — פחית טרייה. קרח בדרך כלל מסופק על ידי האולם — כדאי לוודא מראש."),
            ("כמה כוסות שותה אדם ממוצע בחתונה?",
             "3 כוסות בממוצע לאירוע של 4 שעות. לאירוע ארוך יותר — הגדל את מספר השעות."),
        ]
        for q, a in faqs:
            st.markdown(f"**🔹 {q}**")
            st.markdown(f"<div style='color:var(--text-mid);font-size:.83rem;margin-bottom:.8rem;padding-right:.4rem'>{a}</div>", unsafe_allow_html=True)

    # ── Share ──
    wa = f"https://wa.me/?text={urllib.parse.quote(chr(10).join(share_lines))}"
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown("**📤 שתף את הרשימה:**")
    st.markdown(f'<a href="{wa}" target="_blank" class="wa-btn">📱 שלח לוואצאפ</a>', unsafe_allow_html=True)

    # ── QR Code ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:Frank Ruhl Libre,serif;font-size:1rem;
         color:var(--gold);text-align:center;margin-bottom:.6rem">
      📲 רשימת קניות — QR Code
    </div>
    <div style="font-size:.78rem;color:var(--text-dim);text-align:center;margin-bottom:.8rem">
      סרוק עם הפלאפון בחנות
    </div>
    """, unsafe_allow_html=True)

    if QR_AVAILABLE:
        # QR מצביע על וואצאפ עם הרשימה
        couple_m = st.session_state.get("couple_name","").strip()
        meta_txt = f"{guests} אורחים · {st.session_state.get('style','מאוזן')}"
        if couple_m: meta_txt = f"{couple_m} · " + meta_txt
        # ה-QR פותח וואצאפ עם הרשימה ישירות
        wa_text    = urllib.parse.quote(chr(10).join(share_lines))
        wa_link    = f"https://wa.me/?text={wa_text}"
        qr_data    = urllib.parse.quote(wa_link)
        qr_img_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={qr_data}&color=000000&bgcolor=ffffff&margin=10&ecc=M"
        st.markdown(f"""
        <div style="text-align:center;padding:.5rem 0">
          <div style="font-size:.78rem;color:var(--text-mid);margin-bottom:.5rem">
            סרוק → נפתח וואצאפ עם הרשימה 📱
          </div>
          <img src="{qr_img_url}" width="200" height="200"
               style="border-radius:14px;border:3px solid rgba(232,201,126,0.3);
                      background:white;padding:8px;display:block;margin:0 auto"
               alt="QR Code"/>
          <div style="font-size:.7rem;color:var(--text-dim);margin-top:.4rem">{meta_txt} · ₪{total_cost:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("🔄 התחל מחדש", key="rst"):
        for k in ["rec","generated","extras","specials","edit_open","show_flav","show_sp","venue_map"]:
            st.session_state[k] = {} if k in ["rec","venue_map"] else ([] if k in ["extras","specials"] else (False if "show" in k or k=="generated" else None))
        st.session_state.event_type = None
        st.session_state.tool_type  = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# ABOUT + FOOTER
# ══════════════════════════════════════
st.markdown('<div class="div"></div>', unsafe_allow_html=True)
with st.expander("👋 אודות היועץ"):
    st.markdown("""
    <div style="direction:rtl;padding:.3rem 0">
      <div style="font-family:Frank Ruhl Libre,serif;font-size:1.3rem;font-weight:700;color:var(--gold);margin-bottom:.7rem">
        היי, אני בר אנקרי 👋
      </div>
      <div style="color:var(--text-mid);font-size:.86rem;line-height:1.8">
        <p>דאטה אנליסט שאוהב לפתור בעיות אמיתיות עם נתונים.</p>
        <p>בניתי את היועץ הזה מתוך צורך אמיתי — כשראיתי כמה זוגות מתבלבלים עם שאלת האלכוהול לחתונה. כמה לקנות? מה לקנות? כמה זה עולה?</p>
        <p>הכלי חינמי לחלוטין ונועד לעזור לכם להיכנס לאירוע רגועים — לפחות בצד האלכוהול 🥂</p>
        <p style="color:var(--gold);font-style:italic">מזל טוב מראש! 💍</p>
      </div>
      <div style="margin-top:.9rem">
        <a href="https://www.linkedin.com/in/bar-ankri-a92672383" target="_blank"
           style="display:inline-flex;align-items:center;gap:.4rem;
                  background:rgba(10,102,194,0.12);border:1px solid rgba(10,102,194,0.35);
                  color:#5a9fd4;border-radius:8px;padding:.4rem .85rem;
                  font-size:.82rem;font-weight:700;text-decoration:none">
          🔗 LinkedIn — בר אנקרי
        </a>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:.8rem 0 1.5rem">
  <div style="font-family:'Dancing Script',cursive;font-size:1rem;color:var(--rose);opacity:.55;margin-bottom:.3rem">
    נוצר בלב ❤ על ידי בר אנקרי
  </div>
  <div style="color:var(--text-dim);font-size:.68rem;letter-spacing:.03em">
    60% שותים · 3 כוסות לאדם · 10% מרווח ביטחון
  </div>
</div>
""", unsafe_allow_html=True)
