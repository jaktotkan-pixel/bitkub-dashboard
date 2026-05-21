import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETTING & CYBERPUNK CSS STYLE ---
st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* กล่อง Metrics Card เรืองแสง Neon Cyan */
    .neon-card {
        background: linear-gradient(135deg, #0d1224 0%, #151c33 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e2942;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .neon-card:hover {
        border-color: #00FFCC;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.35);
    }
    .neon-lbl { font-size: 12px; color: #64748b; margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .neon-val { font-size: 24px; font-weight: bold; color: #ffffff; }
    
    /* กล่อง Expander ฝั่งขวา (Input) */
    .stExpander {
        background-color: #0d1224 !important;
        border: 1px solid #1e2942 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
    }
    .stExpander summary { font-weight: 600 !important; color: #e2e8f0 !important; }
    .stExpander summary:hover { color: #00FFCC !important; }
    
    /* ปรับแต่งสไตล์ตารางประมวลผล */
    .stTable {
        background-color: #0d1224;
        border: 1px solid #1e2942;
        border-radius: 10px;
        overflow: hidden;
    }
    .stTable th {
        background-color: #151324 !important;
        color: #00FFCC !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักสไตล์ Trader Space Station
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ CYBERPUNK NEON TRADER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>MULTI-TIER PORTFOLIO OVERVIEW • 5 ไม้ละเอียด (FEE 0.25%)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 30px; box-shadow: 0 1px 5px rgba(0,255,204,0.1);'></div>", unsafe_allow_html=True)

# ฟังก์ชันจัดการทศนิยมแบบสะอาด ไร้เลข 0 ลากหางรกสายตา
def format_smart_clean(value):
    if value == 0 or value is None:
        return "0.00"
    elif abs(value) < 1.0:
        return f"{value:,.8f}".rstrip('0').rstrip('.') if '.' in f"{value:,.8f}" else f"{value:,.2f}"
    else:
        formatted = f"{value:,.8f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
            if '.' in formatted:
                parts = formatted.split('.')
                if len(parts[1]) < 2:
                    formatted = f"{parts[0]}.{parts[1].ljust(2, '0')}"
            else:
                formatted = f"{formatted}.00"
        return formatted

FEE_RATE = 0.0025

# --- LAYOUT DIVISION (โครงสร้างเดิม: ผลลัพธ์อยู่ซ้าย, กล่องกรอกอยู่ขวา) ---
col_result, col_input = st.columns([1.3, 1])

# ----------------------------------------------------
# 🔴 ฝั่งขวา [INPUT]: บันทึกรายการเข้าซื้อ (ปรับค่าเริ่มต้นเป็น None เพื่อให้เป็นช่องว่าง)
# ----------------------------------------------------
with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📥 [INPUT] บันทึกรายการเข้าซื้อ</h3>", unsafe_allow_html=True)
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        # 🌟 ปรับเป็นช่องว่าง (None) ทั้งหมด พิมพ์เติมตัวเลขได้เลยทันที
        cash_1 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", min_value=0.0, value=None, step=100.0, key="c1_num", placeholder="กรอกเงินทุน...")
        price_1 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", min_value=0.0, value=None, format="%.8f", step=0.0001, key="p1_num", placeholder="กรอกราคาเหรียญ...")
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", min_value=0.0, value=None, step=100.0, key="c2_num", placeholder="กรอกเงินทุน...")
        price_2 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", min_value=0.0, value=None, format="%.8f", step=0.0001, key="p2_num", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", min_value=0.0, value=None, step=100.0, key="c3_num", placeholder="กรอกเงินทุน...")
        price_3 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", min_value=0.0, value=None, format="%.8f", step=0.0001, key="p3_num", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", min_value=0.0, value=None, step=100.0, key="c4_num", placeholder="กรอกเงินทุน...")
        price_4 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", min_value=0.0, value=None, format="%.8f", step=0.0001, key="p4_num", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", min_value=0.0, value=None, step=100.0, key="c5_num", placeholder="กรอกเงินทุน...")
        price_5 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 5 (บาท):", min_value=0.0, value=None, format="%.8f", step=0.0001, key="p5_num", placeholder="กรอกราคาเหรียญ...")

# --- เซฟโซนป้องกัน Error กรณีช่องว่างเปลี่ยนเป็น 0 หลังบ้าน ---
c1 = cash_1 if cash_1 is not None else 0.0
p1 = price_1 if price_1 is not None else 0.0
c2 = cash_2 if cash_2 is not None else 0.0
p2 = price_2 if price_2 is not None else 0.0
c3 = cash_3 if cash_3 is not None else 0.0
p3 = price_3 if price_3 is not None else 0.0
c4 = cash_4 if cash_4 is not None else 0.0
p4 = price_4 if price_4 is not None else 0.0
c5 = cash_5 if cash_5 is not None else 0.0
p5 = price_5 if price_5 is not None else 0.0

raw_data = [
    {"ไม้ที่": 1, "cash": c1, "price": p1},
    {"ไม้ที่": 2, "cash": c2, "price": p2},
    {"ไม้ที่": 3, "cash": c3, "price": p3},
    {"ไม้ที่": 4, "cash": c4, "price": p4},
    {"ไม้ที่": 5, "cash": c5, "price": p5}
]

rows = []
chart_labels = []
chart_values = []
total_invest_cash = 0.0
total_coins = 0.0
total_buy_fee = 0.0

for item in raw_data:
    if item["cash"] > 0 and item["price"] > 0:
        fee = item["cash"] * FEE_RATE
        net_buy = item["cash"] - fee
        coins_received = net_buy / item["price"]
        
        total_invest_cash += item["cash"]
        total_buy_fee += fee
        total_coins += coins_received
        
        rows.append({
            "ไม้ที่": f"ไม้ {item['ไม้ที่']}",
            "เงินทุนซื้อ (บาท)": f"{item['cash']:,.2f}",
            "ราคาตอนซื้อ": format_smart_clean(item['price']),
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{fee:,.2f}",
            "เหรียญที่ได้รับ": f"{coins_received:,.4f}"
        })
        
        chart_labels.append(f"ไม้ {item['ไม้ที่']}")
        chart_values.append(item["cash"])

avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0

# ----------------------------------------------------
# 🟨 ฝั่งซ้าย [OUTPUT]: ประมวลผลพอร์ตและความคุ้มทุน (โครงสร้างเดิม)
# ----------------------------------------------------
with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📊 [OUTPUT] ประมวลผลพอร์ตและความ
