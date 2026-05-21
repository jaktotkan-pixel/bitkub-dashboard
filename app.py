import streamlit as st
import pandas as pd

# --- 1. SETTING & CYBERPUNK CSS STYLE ---
st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* กล่อง Metrics Card ปรับขนาดให้ยืดหยุ่นเต็มพื้นที่ ไม่หดตกขอบ */
    .neon-card {
        background: linear-gradient(135deg, #0d1224 0%, #151c33 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e2942;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        text-align: center;
        transition: all 0.3s ease;
        width: 100%;
    }
    .neon-card:hover {
        border-color: #00FFCC;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.35);
    }
    .neon-lbl { font-size: 12px; color: #64748b; margin-bottom: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .neon-val { font-size: 22px; font-weight: bold; color: #ffffff; }
    
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

# ฟังก์ชันจัดปลอกทศนิยมส่วนแสดงผล ลบเลข 0 ลากหางออก 100% แต่ถ้าเป็นเลขยาวๆ โชว์ครบปกติ
def format_smart_clean(value):
    if value == 0 or value is None:
        return "0.00"
    
    # แปลงเป็นทศนิยมความละเอียดสูงสุด 8 ตำแหน่งรองรับสเปก 8F
    formatted = f"{value:,.8f}"
    
    if '.' in formatted:
        formatted = formatted.rstrip('0').rstrip('.')
        if '.' in formatted:
            parts = formatted.split('.')
            if len(parts[1]) == 1:
                formatted = f"{parts[0]}.{parts[1]}0"
            elif len(parts[1]) == 0:
                formatted = f"{parts[0]}.00"
        else:
            formatted = f"{formatted}.00"
            
    return formatted

# ฟังก์ชันช่วยแปลงข้อความจากช่องกรอกให้เป็น Float ปลอดภัย ไร้ Error
def parse_float_input(val_str):
    if not val_str or val_str.strip() == "":
        return None
    try:
        return float(val_str.replace(",", "").strip())
    except ValueError:
        return 0.0

FEE_RATE = 0.0025

# --- LAYOUT DIVISION (โครงสร้างหลักแยกฝั่งซ้าย-ขวาอย่างสมดุล) ---
col_result, col_input = st.columns([1.2, 1])

# ----------------------------------------------------
# 🔴 ฝั่งขวา [INPUT]: บันทึกรายการเข้าซื้อ (ใช้ช่อง Text คลีนๆ พิมพ์ง่าย ไม่มีศูนย์งอก)
# ----------------------------------------------------
with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📥 [INPUT] บันทึกรายการเข้าซื้อ</h3>", unsafe_allow_html=True)
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", key="c1_str", placeholder="เช่น 1000")
        price_1_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", key="p1_str", placeholder="เช่น 45.77 หรือ 0.0001924")
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", key="c2_str", placeholder="กรอกเงินทุน...")
        price_2_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", key="p2_str", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", key="c3_str", placeholder="กรอกเงินทุน...")
        price_3_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", key="p3_str", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", key="c4_str", placeholder="กรอกเงินทุน...")
        price_4_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", key="p4_str", placeholder="กรอกราคาเหรียญ...")
        
    with st.expander("🪵 รายละเอียด ไม้ที่
