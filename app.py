import streamlit as st
import pandas as pd
import math
import urllib.parse
import json
import threading
import urllib.request
import datetime
import random
try:
    import qrcode
    from qrcode.image.pil import PilImage
    import io
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

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
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;900&family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400;1,600&family=Dancing+Script:wght@600;700&display=swap');

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
  font-family:'Cormorant Garamond',serif;
  font-size:clamp(2.2rem,7vw,3rem);font-weight:700;font-style:italic;
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
.ec-title{font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-weight:700;color:var(--gold);}
.ec-desc{font-size:.78rem;color:var(--text-dim);margin-top:.1rem;}
.ec-arrow{margin-right:auto;color:var(--text-dim);font-size:1rem;}

/* ── Input Panel ── */
.input-panel{
  background:var(--bg2);border:1px solid var(--border-dim);
  border-radius:var(--r);padding:1.4rem 1.5rem;margin-bottom:1rem;
}
.panel-title{
  font-family:'Cormorant Garamond',serif;
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
  background:var(--bg2);border:1px solid var(--border-dim);
  border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.8rem;
  transition:border-color .2s;
  animation:fadeUp .4s ease both;
}
.r-card:hover{border-color:var(--border);}
.r-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.7rem;}
.r-left{flex:1;}
.r-cat{font-family:'Cormorant Garamond',serif;font-size:1.05rem;font-weight:700;color:var(--gold);}
.r-brand{font-size:.78rem;color:var(--text-mid);margin-top:.1rem;}
.r-right{text-align:center;min-width:56px;}
.r-num{font-family:'Cormorant Garamond',serif;font-size:2.2rem;font-weight:900;color:#fff;line-height:1;animation:popIn .4s ease both;}
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
.sheet-title{font-family:'Cormorant Garamond',serif;font-size:1rem;color:var(--gold);text-align:center;margin-bottom:.8rem;}
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
.total-main{font-family:'Cormorant Garamond',serif;font-size:2.4rem;font-weight:900;color:var(--gold);line-height:1;}
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
.sec{font-family:'Cormorant Garamond',serif;font-size:1.1rem;color:var(--gold);margin:.9rem 0 .5rem;}

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
if not st.session_state.event_type:
    st.markdown("""
    <div class="welcome">
      <div class="welcome-glow"></div>
      <div class="welcome-badge">✦ ברוכים הבאים ✦</div>
      <div class="welcome-title">יועץ האלכוהול</div>
      <div class="welcome-en">Bar Advisor</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="event-list">', unsafe_allow_html=True)
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

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem">
      <div style="font-family:'Dancing Script',cursive;font-size:1rem;color:var(--rose);opacity:.5">
        נוצר בלב ❤ על ידי בר אנקרי
      </div>
    </div>""", unsafe_allow_html=True)
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
  <div style="font-family:'Cormorant Garamond',serif;font-style:italic;
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
      <div style="font-family:'Cormorant Garamond',serif;font-style:italic;
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

        st.markdown(f"""
        <div class="r-card">
          <div class="r-head">
            <div class="r-left">
              <div class="r-cat">{CAT_HE[cat]}</div>
              <div class="r-brand">{item['brand_he']} &nbsp;{badge_html}</div>
            </div>
            <div class="r-right">
              <div class="r-num">{item['n']}</div>
              <div class="r-num-lbl">בקבוקים</div>
            </div>
          </div>
          <div class="r-row"><span>נפח</span><span>{item['vol']} מ"ל</span></div>
          <div class="r-row"><span>שותים ({item['pct']}%)</span><span>{item['drinkers']} אנשים</span></div>
          <div class="r-row"><span>מחיר לבקבוק</span><span>₪{item['ppb']:.0f}</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{item['total']:.0f}</span></div>
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
            st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:Cormorant Garamond,serif;font-size:.95rem;color:var(--gold);margin-bottom:.8rem;text-align:center">⚙️ עריכת {CAT_HE[cat]}</div>', unsafe_allow_html=True)

            # מותג
            st.markdown('<div style="font-size:.78rem;color:var(--text-dim);margin-bottom:.3rem">✏️ מותג</div>', unsafe_allow_html=True)
            bdf  = get_brands(df, cat)
            opts = bdf['brand'].tolist()
            cur  = opts.index(info["brand"]) if info["brand"] in opts else 0
            chosen = st.selectbox(
                "מותג",
                options=opts,
                index=cur,
                format_func=lambda x, d=bdf: f"{brand_display(d[d['brand']==x].iloc[0])}  [{d[d['brand']==x].iloc[0]['level']}]  ₪{d[d['brand']==x].iloc[0]['price']:.0f}",
                key=f"sel_{cat}",
                label_visibility="collapsed"
            )

            # %
            st.markdown('<div style="font-size:.78rem;color:var(--text-dim);margin:.6rem 0 .3rem">📊 % שותים</div>', unsafe_allow_html=True)
            cur_pct = info["pct"]
            new_pct = st.number_input("אחוז שותים", 5, 80, cur_pct, 5,
                                       key=f"pct_inp_{cat}", label_visibility="collapsed")
            new_d = math.ceil(nd(guests) * new_pct / 100)
            st.markdown(f'<div class="nbox" style="margin:.2rem 0 .6rem">{new_d} אנשים ישתו {CAT_HE[cat]}</div>', unsafe_allow_html=True)

            # כפתורי פעולה — ורטיקלי
            if st.button("✅ שמור שינויים", key=f"ok_{cat}", use_container_width=True):
                st.session_state.rec[cat]["brand"] = chosen
                st.session_state.rec[cat]["pct"]   = int(new_pct)
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

    # ── Extras ──
    EXTRA_LBL = {"Vodka":"וודקה בטעמים 🍹","Whiskey":"וויסקי נוסף 🥃","Tequila":"טקילה נוספת 🌵","Anis":"ארק נוסף 🌿"}
    for idx, ve in enumerate(st.session_state.extras):
        cat_e = ve.get("cat","Vodka")
        it    = calc_item(df, cat_e, ve["brand"], ve["pct"], guests, st.session_state.get("hours",4))
        total_alc += it["total"]
        share_lines.append(f"➕ {it['brand_he']}: {it['n']} בקבוקים (₪{it['total']:.0f})")
        st.markdown(f"""
        <div class="r-card" style="border-color:rgba(192,132,252,.2)">
          <div class="r-head">
            <div class="r-left"><div class="r-cat">{EXTRA_LBL.get(cat_e,cat_e)}</div>
            <div class="r-brand">{it['brand_he']}</div></div>
            <div class="r-right"><div class="r-num">{it['n']}</div><div class="r-num-lbl">בקבוקים</div></div>
          </div>
          <div class="r-row"><span>שותים ({ve['pct']}%)</span><span>{it['drinkers']} אנשים</span></div>
          <div class="r-row"><span>סה"כ</span><span class="r-val">₪{it['total']:.0f}</span></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑️ הסר", key=f"del_ex_{idx}"): st.session_state.extras.pop(idx); st.rerun()
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

    # ── Add buttons ──
    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-add">', unsafe_allow_html=True)
    if st.button("🍹 הוסף וודקה בטעמים", key="af", use_container_width=True):
        st.session_state.show_flav = not st.session_state.show_flav
        st.session_state.show_sp   = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-add">', unsafe_allow_html=True)
    if st.button("🥃 הוסף מותג וויסקי נוסף", key="aw", use_container_width=True):
        w_df  = get_brands(df,"Whiskey")
        exist = [r["brand"] for r in st.session_state.extras if r.get("cat")=="Whiskey"]
        exist.append(rec.get("Whiskey",{}).get("brand",""))
        nw = w_df[~w_df['brand'].isin(exist)]
        if not nw.empty:
            st.session_state.extras.append({"brand":nw.iloc[0]['brand'],"cat":"Whiskey","pct":10})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-sp">', unsafe_allow_html=True)
    if st.button("👑 הוסף בקבוק יוקרה", key="asp", use_container_width=True):
        st.session_state.show_sp   = not st.session_state.show_sp
        st.session_state.show_flav = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.show_flav:
        st.markdown('<div class="edit-pnl">', unsafe_allow_html=True)
        fd = get_brands(df,"Vodka",flavor="flavored")
        if not fd.empty:
            fo = fd['brand'].tolist()
            fi = st.selectbox("בחר טעם:",range(len(fo)),format_func=lambda x,d=fd:fmt_b(d.iloc[x]),key="fi")
            fp = st.number_input("% מהשותים שישתו וודקה בטעמים",5,40,15,5,key="fp")
            if st.button("✅ הוסף",key="fi_ok"):
                st.session_state.extras.append({"brand":fo[fi],"cat":"Vodka","pct":int(fp)})
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
    <div style="font-family:'Cormorant Garamond',serif;font-size:1rem;
         color:var(--gold);text-align:center;margin-bottom:.6rem">
      📲 רשימת קניות — QR Code
    </div>
    <div style="font-size:.78rem;color:var(--text-dim);text-align:center;margin-bottom:.8rem">
      סרוק עם הפלאפון בחנות
    </div>
    """, unsafe_allow_html=True)

    if QR_AVAILABLE:
        # בנה QR מהרשימה
        qr_text = chr(10).join(share_lines)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=3,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        # מרכז את ה-QR
        qc1, qc2, qc3 = st.columns([1,2,1])
        with qc2:
            st.image(buf, use_container_width=True)

        couple  = st.session_state.get("couple_name","").strip()
        meta    = f"{guests} אורחים · {st.session_state.get('style','מאוזן')}"
        if couple: meta = f"{couple} · " + meta
        st.markdown(
            f'<div style="text-align:center;font-size:.75rem;color:var(--text-dim);margin-top:.3rem">{meta} · ₪{total_cost:,.0f}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="nbox">להפעלת QR Code הרץ: <code>pip install qrcode[pil]</code></div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("🔄 התחל מחדש", key="rst"):
        for k in ["rec","generated","extras","specials","edit_open","show_flav","show_sp","venue_map"]:
            st.session_state[k] = {} if k in ["rec","venue_map"] else ([] if k in ["extras","specials"] else (False if "show" in k or k=="generated" else None))
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# ABOUT + FOOTER
# ══════════════════════════════════════
st.markdown('<div class="div"></div>', unsafe_allow_html=True)
with st.expander("👋 אודות היועץ"):
    st.markdown("""
    <div style="direction:rtl;padding:.3rem 0">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:700;color:var(--gold);margin-bottom:.7rem">
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
