import streamlit as st
import requests
import random
import time
import urllib3
import concurrent.futures
import plotly.graph_objects as go
from pdf_exporter import create_meal_plan_pdf

from data import food_items_breakfast, food_items_lunch, food_items_dinner
from prompts import (
    pre_prompt_b, pre_prompt_l, pre_prompt_d,
    pre_breakfast, pre_lunch, pre_dinner, negative_prompt
)
from recipe_generator import (
    generate_breakfast_recipe, generate_lunch_recipe, generate_dinner_recipe
)

# ─── Constants ────────────────────────────────────────────────────────────────
UNITS_LB_TO_KG = 1 / 2.20462
UNITS_IN_TO_CM = 1 / 0.393701
GROQ_API_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL     = "llama-3.3-70b-versatile"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Meal Planner", page_icon="🥗", layout="wide", initial_sidebar_state="collapsed")

# ─── Session State ────────────────────────────────────────────────────────────
for k, v in {"dark_mode": True, "generated_data": None, "last_name": ""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

dm = st.session_state.dark_mode

# ════════════════════════════════════════════════════════════════════════════
# THEME TOKENS
# ════════════════════════════════════════════════════════════════════════════
if dm:
    BG         = "#050514"
    SURFACE    = "rgba(15, 23, 42, 0.45)"
    BORDER     = "rgba(255, 255, 255, 0.08)"
    TEXT_MAIN  = "#F8FAFC"
    TEXT_MUTED = "#94A3B8"
    INPUT_BG   = "rgba(0, 0, 0, 0.2)" # Fixed opaque issue
    RADIALS    = """
      radial-gradient(circle at 15% 15%, rgba(139,92,246,0.1) 0%, transparent 40%),
      radial-gradient(circle at 85% 20%, rgba(6,182,212,0.1) 0%, transparent 40%),
      radial-gradient(circle at 50% 80%, rgba(236,72,153,0.1) 0%, transparent 40%)
    """
    BTN_TEXT   = "☀️  Light Mode"
else:
    BG         = "#E6EBF5"
    SURFACE    = "rgba(255, 255, 255, 0.6)"
    BORDER     = "rgba(109, 40, 217, 0.22)"
    TEXT_MAIN  = "#1A0D3D"
    TEXT_MUTED = "#3B2D7A"
    INPUT_BG   = "rgba(255, 255, 255, 0.85)"
    RADIALS    = "radial-gradient(circle at 50% 0%, rgba(255,255,255,0.8) 0%, transparent 100%)"
    BTN_TEXT   = "🌙  Dark Mode"

PURPLE = "#8B5CF6"
CYAN   = "#06B6D4"
PINK   = "#EC4899"

# ════════════════════════════════════════════════════════════════════════════
# CORE UI CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

*,*::before,*::after{{box-sizing:border-box;}}
html,body,.stApp{{
  background-color:{BG}!important;
  background-image:{RADIALS}!important;
  font-family:'Space Grotesk',sans-serif!important;
  color:{TEXT_MAIN}!important;
}}

#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"],[data-testid="stDecoration"]{{
  display:none!important;visibility:hidden!important;
}}

.main .block-container{{ padding:2rem 3rem 6rem!important; max-width:1440px!important; margin:0 auto; }}

/* Universal Inputs */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div > div {{
  background:{INPUT_BG}!important; border:1px solid {BORDER}!important;
  border-radius:12px!important; color:{TEXT_MAIN}!important; font-weight:500!important;
}}

/* Fix text colors */
p, span, div, label {{ color: {TEXT_MAIN}; }}
label[data-testid="stWidgetLabel"] p, div[data-testid="stRadio"] label p {{ color:{TEXT_MUTED}!important; font-weight:600!important; }}

/* Primary Generated Button */
.stButton>button {{
  width:100%; padding:1rem!important; border-radius:12px!important;
  font-family:'Space Grotesk',sans-serif!important; font-size:1.1rem!important; font-weight:700!important;
  background:linear-gradient(135deg, {PURPLE}, {CYAN})!important; color:#FFFFFF!important; border:none!important;
}}
.stButton>button:hover {{ box-shadow:0 8px 30px rgba(139,92,246,0.4)!important; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# LOGIC & HELPERS
# ════════════════════════════════════════════════════════════════════════════
def dash_title(title, subtitle):
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:3rem">
      <div style="display:inline-flex;align-items:center;padding:6px 16px;border-radius:100px;
        background:{SURFACE};border:1px solid {BORDER};font-size:0.8rem;font-weight:700;
        letter-spacing:1px;color:{TEXT_MAIN};margin-bottom:1rem">
        <span style="color:{PURPLE};margin-right:8px">●</span> AI-POWERED • GROQ LLAMA 3.3
      </div>
      <h1 style="font-size:clamp(2.5rem, 5vw, 4rem);font-weight:800;line-height:1.1;margin:0 0 1rem 0;color:{TEXT_MAIN}">{title}</h1>
      <p style="font-size:1.1rem;color:{TEXT_MUTED};max-width:600px;margin:0 auto;line-height:1.5">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def calc_bmi(w,h): return round(w/(h/100)**2,1) if h>0 else 0.0
def calc_bmr(w,h,a,g): b=9.99*w+6.25*h-4.92*a; return b+5 if g=="Male" else b-161
def bmi_cat(b):
    if b<18.5: return "Underweight", "#3B82F6"
    if b<25.0: return "Normal Weight", "#10B981"
    if b<30.0: return "Overweight", "#F59E0B"
    return "Obese", "#EF4444"

DIET_MAP={"Vegan":["vegan"],"Vegetarian":["vegan","vegetarian"],"Non-Vegetarian":["vegan","vegetarian","non-vegetarian"]}
def filter_diet(fd,al): return {g:{i:info for i,info in fs.items() if info.get("type","non-vegetarian") in al} for g,fs in fd.items()}
def flatten(fg): return {g:{i:info["calories"] for i,info in fs.items()} for g,fs in fg.items()}
def knapsack(target,groups):
    items=[(c,i) for g in groups.values() for i,c in g.items()]
    n=len(items)
    if n==0: return [],0
    dp=[[0]*(target+1) for _ in range(n+1)]
    for i in range(1,n+1):
        for j in range(target+1):
            c,_=items[i-1]
            dp[i][j]=dp[i-1][j] if c>j else max(dp[i-1][j],dp[i-1][j-c]+c)
    sel,j=[],target
    for i in range(n,0,-1):
        if dp[i][j]!=dp[i-1][j]:
            c,itm=items[i-1];sel.append(itm);j-=c
    return sel,dp[n][target]

def call_llm(content):
    try:
        h={"Authorization":f"Bearer {st.secrets['GROQ_API_KEY']}","Content-Type":"application/json"}
        r=requests.post(GROQ_API_URL,headers=h,
            json={"model":GROQ_MODEL,"messages":[{"role":"user","content":content}],"max_tokens":250},
            verify=False,timeout=20)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"AI Unavailable: {e}"

def gen_desc(items,pp,pm): return call_llm(pp+str(items)+pm+negative_prompt)

def draw_bmi_gauge(bmi):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=bmi, number={'suffix': " kg/m²", 'font': {'size': 40, 'color': TEXT_MAIN, 'family': 'Space Grotesk'}},
        gauge={
            'axis': {'range': [10, 40], 'tickwidth': 1, 'tickcolor': TEXT_MUTED},
            'bar': {'color': TEXT_MAIN, 'thickness': 0.15},
            'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 0,
            'steps': [
                {'range': [10, 18.5], 'color': 'rgba(59, 130, 246, 0.4)'},
                {'range': [18.5, 25], 'color': '#10B981'},
                {'range': [25, 30], 'color': 'rgba(245, 158, 11, 0.4)'},
                {'range': [30, 40], 'color': 'rgba(239, 68, 68, 0.4)'}
            ]
        }))
    fig.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color': TEXT_MAIN})
    return fig

# ════════════════════════════════════════════════════════════════════════════
# HEADER & TOGGLE
# ════════════════════════════════════════════════════════════════════════════
col_logo, col_theme = st.columns([5,1])
with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
      <div style="background:linear-gradient(135deg,{PURPLE},{CYAN});border-radius:12px;padding:8px;font-size:1.5rem">🥗</div>
      <span style="font-size:1.4rem;font-weight:700;color:{TEXT_MAIN}">NutriAI</span>
    </div>
    """, unsafe_allow_html=True)
with col_theme:
    if st.button(BTN_TEXT):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# ALL-IN-ONE PAGE LAYOUT
# ════════════════════════════════════════════════════════════════════════════
dash_title("YOUR PERSONAL AI MEAL PLANNER", "One page. Zero waiting. Enter your details and generate everything instantly.")

# --- TOP SECTION: INPUTS & BMI GAUGE ---
col_form, col_gauge = st.columns([1,1], gap="large")

with col_form:
    st.markdown(f'<div style="font-size:1.2rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:1rem;border-bottom:1px solid {BORDER};padding-bottom:10px">👤 Personal Profile</div>', unsafe_allow_html=True)
    name   = st.text_input("Full Name", value=st.session_state.last_name, placeholder="e.g. Samarth Shekhar")
    age    = st.number_input("Age (years)", 10, 100, 25)
    
    c1, c2 = st.columns(2)
    with c1: gender = st.radio("Gender", ["Male", "Female"], horizontal=True)
    with c2: diet   = st.selectbox("Diet Type", ["Non-Vegetarian", "Vegetarian", "Vegan"])
    
    act_map = {
        "Sedentary (0 days/wk)": 1.2, 
        "Light (1-3 days/wk)": 1.375, 
        "Moderate (3-5 days/wk)": 1.55, 
        "Active (6-7 days/wk)": 1.725
    }
    act_lbl = st.selectbox("Activity Level", list(act_map.keys()), index=1)
    gl_map  = {"Maintain Weight":0, "Lose Weight":-500, "Gain Weight":+500}
    gl_lbl  = st.selectbox("Calorie Goal", list(gl_map.keys()))

    c3, c4 = st.columns(2)
    with c3: w = st.number_input("Weight (kg)", 20.0, 300.0, 70.0)
    with c4: h = st.number_input("Height (cm)", 100.0, 250.0, 170.0)

# Calculate live stats
bmi = calc_bmi(w, h)
cat, cat_col = bmi_cat(bmi)
bmr = calc_bmr(w, h, age, gender)
tdee= bmr * act_map[act_lbl]
tgt = max(1200, round(tdee + gl_map[gl_lbl]))

with col_gauge:
    st.markdown(f'<div style="font-size:1.2rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:1rem;border-bottom:1px solid {BORDER};padding-bottom:10px">📊 Live Body Analysis</div>', unsafe_allow_html=True)
    st.plotly_chart(draw_bmi_gauge(bmi), use_container_width=True, config={'displayModeBar':False})
    st.markdown(f'<div style="text-align:center;font-size:1.2rem;font-weight:700;color:{cat_col};margin-top:-20px">{"✅" if cat=="Normal Weight" else "⚠️"} {cat}</div>', unsafe_allow_html=True)
    
    # Quick Stats Row
    protein_tgt = round((tgt * 0.30) / 4)
    c1, c2, c3, c4, c5 = st.columns(5)
    
    labels = ["BMI", "BMR", "TDEE", "CALORIES", "PROTEIN"]
    values = [bmi, round(bmr), round(tdee), tgt, f"{protein_tgt}g"]
    colors = ["#10B981", "#A855F7", "#06B6D4", "#10B981", "#EC4899"]
    
    for col, lbl, val, colr in zip([c1,c2,c3,c4,c5], labels, values, colors):
        with col:
            st.markdown(f'<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;padding:10px 5px;text-align:center"><div style="font-size:1.3rem;font-weight:800;color:{colr};line-height:1">{val}</div><div style="font-size:0.65rem;font-weight:700;color:{TEXT_MUTED};letter-spacing:1px">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- MIDDLE SECTION: GENERATION ---
_, c_btn, _ = st.columns([1,2,1])
with c_btn:
    if st.button("🚀 Fast-Track Generation (Plan + AI Recipes)"):
        st.session_state.last_name = name.strip() or "User"
        
        # Knapsack
        cb,cl,cd = round(tgt*.35),round(tgt*.40),round(tgt*.25)
        al = DIET_MAP[diet]
        bi = filter_diet(food_items_breakfast,al)
        li = filter_diet(food_items_lunch,al)
        di = filter_diet(food_items_dinner,al)
        ib,cb_=knapsack(cb,flatten(bi)); il,cl_=knapsack(cl,flatten(li)); id_,cd_=knapsack(cd,flatten(di))
        
        # Parallel Execution for Extreme Speed
        with st.spinner("AI is crafting your recipes in parallel (usually <5 seconds)..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                ft_b_rec = executor.submit(generate_breakfast_recipe, bi)
                ft_l_rec = executor.submit(generate_lunch_recipe, li)
                ft_d_rec = executor.submit(generate_dinner_recipe, di)
                ft_b_des = executor.submit(gen_desc, ib, pre_prompt_b, pre_breakfast)
                ft_l_des = executor.submit(gen_desc, il, pre_prompt_l, pre_lunch)
                ft_d_des = executor.submit(gen_desc, id_, pre_prompt_d, pre_dinner)
                
                b_rec = ft_b_rec.result(); l_rec = ft_l_rec.result(); d_rec = ft_d_rec.result()
                db = ft_b_des.result(); dl = ft_l_des.result(); dd = ft_d_des.result()
                
        # Store for PDF and display
        meals_data=[
            {"title":"Breakfast","calories":cb_,"tgt":cb,"items":ib,"description":db,"recipe":b_rec,"color":PURPLE},
            {"title":"Lunch",    "calories":cl_,"tgt":cl,"items":il,"description":dl,"recipe":l_rec,"color":CYAN},
            {"title":"Dinner",   "calories":cd_,"tgt":cd,"items":id_,"description":dd,"recipe":d_rec,"color":PINK},
        ]
        user_info={"name":st.session_state.last_name,"age":age,"gender":gender,"diet":diet,"bmr":bmr,"bmi":bmi,"bmi_cat":cat,"tdee":tgt}
        
        st.session_state.generated_data = {"meals": meals_data, "user_info": user_info}
        st.rerun()

# --- BOTTOM SECTION: DISPLAY RESULTS ---
if st.session_state.generated_data:
    gdata = st.session_state.generated_data
    
    uname = st.session_state.last_name
    st.markdown(f'<div style="text-align:center;margin-bottom:2rem"><div style="font-size:1.2rem;color:{TEXT_MUTED};font-weight:600">Hey {uname}, here are your results!</div><h2 style="color:{TEXT_MAIN};margin:0;font-size:2.5rem;font-weight:800">🍱 Your Complete Plan</h2></div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3, gap="large")
    for col, m in zip([m1, m2, m3], gdata["meals"]):
        with col:
            st.markdown(f"""
            <div style="background:{SURFACE};border:1px solid {BORDER};border-radius:24px;padding:2rem;height:100%">
              <div style="font-size:1.5rem;font-weight:700;color:{TEXT_MAIN};margin-bottom:10px">{m['title']}</div>
              <div style="font-size:2.5rem;font-weight:800;color:{m['color']};line-height:1">{m['calories']} <span style="font-size:1rem;color:{TEXT_MUTED}">kcal</span></div>
              <div style="margin:15px 0;">{"".join([f'<span style="display:inline-block;background:rgba(255,255,255,0.05);border:1px solid {BORDER};padding:6px 12px;border-radius:100px;margin:3px;font-size:0.8rem;color:{TEXT_MAIN}">🍽️ {i.replace("_", " ").title()}</span>' for i in m['items']])}</div>
              <p style="font-size:0.9rem;color:{TEXT_MUTED};font-style:italic;margin-bottom:15px">"{m['description']}"</p>
              <div style="font-size:0.85rem;color:{TEXT_MAIN};background:rgba(0,0,0,0.1);padding:15px;border-radius:12px;white-space:pre-wrap;border-left:3px solid {m['color']}">{m['recipe']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, dl_c, _ = st.columns([1,2,1])
    with dl_c:
        create_meal_plan_pdf(gdata["meals"], gdata["user_info"], "meal_plan.pdf")
        with open("meal_plan.pdf", "rb") as f:
            st.download_button("📥 Download Master PDF", data=f, file_name=f"{st.session_state.last_name}_Diet.pdf", mime="application/pdf")
