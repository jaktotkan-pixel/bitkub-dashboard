import streamlit as st
import pandas as pd

# --- 1. ตั้งค่าโครงสร้างหน้าจอและ CSS สไตล์ Cyberpunk Neon Pro ---
st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

st.markdown("""
<style>
    /* ปรับแต่งพื้นหลังและโทนสีมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* ตกแต่งกล่องสรุปผลข้อมูล (Metrics Card) ขอบเรืองแสง Neon Cyan */
    .neon-card {
        background: linear-gradient(135deg, #0d1224 0%, #151c33 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #1e2942;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    /* เอฟเฟกต์เรืองแสงเวลาเอาเมาส์ไปชี้ */
    .neon-card:hover {
        border-color: #00FFCC;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.35);
    }
    .neon-lbl { font-size: 13px; color: #64748b; margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
    .neon-val { font-size: 26px; font-weight: bold; color: #ffffff; }
    
    /* ตกแต่งกล่องอินพุตฝั่งซ้าย (Expander) ให้ดุดันเข้าธีม */
    .stExpander {
        background-color: #0d1224 !important;
        border: 1px solid #1e2942 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* สไตล์ปุ่มและหัวข้อ Expander */
    .stExpander summary {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
    .stExpander summary:hover {
        color: #00FFCC !important;
    }
    
    /* ตกแต่งตารางแสดงผลฝั่งซื้อ */
    .stTable {
        background-color: #0d1224;
        border: 1px solid #1e2942;
        border-radius: 10px;
        overflow: hidden;
    }
    .stTable th {
        background-color: #151c33 !important;
        color: #00FFCC !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักเรืองแสงสไตล์ Cyberpunk Pro
st.markdown("<h1 style='text-align
