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
        background-color: #151c33 !important;
        color: #00FFCC !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักสไตล์ Trader Space Station
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ CYBERPUNK NEON TRADER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>MULTI-TIER PORTFOLIO SIMULATOR • 5 ไม้ละเอียด (FEE 0.25%)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 30px; box-shadow: 0 1px 5px rgba(0,255,204,0.1);'></div>", unsafe_allow_html=True)

# ฟังก์ชันจัดการทศนิยมแบบสะอาด ไร้เลข 0 ลากหางรกสายตา
def format_smart_clean(value):
    if value == 0:
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

# --- LAYOUT DIVISION ---
# ฝั่งซ้าย (ผลลัพธ์และ Simulator กราฟ) และ ฝั่งขวา (กล่องกรอกข้อมูลรายไม้)
col_result, col_input = st.columns([1.3, 1])

# ----------------------------------------------------
# 🔴 ฝั่งขวา [INPUT]: บันทึกข้อมูลเข้าซื้อรายไม้ (ใช้ตัวเลขสะอาด พิมพ์ง่าย)
# ----------------------------------------------------
with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📥 1. บันทึกรายการเข้าซื้อ รายไม้</h3>", unsafe_allow_html=True)
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", min_value=0.0, value=2600.0, step=100.0, key="c1_num")
        price_1 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", min_value=0.0, value=47.55, format="%.8f", step=0.0001, key="p1_num")
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c2_num")
        price_2 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", min_value=0.0, value=0.0, format="%.8f", step=0.0001, key="p2_num")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c3_num")
        price_3 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", min_value=0.0, value=0.0, format="%.8f", step=0.0001, key="p3_num")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c4_num")
        price_4 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", min_value=0.0, value=0.0, format="%.8f", step=0.0001, key="p4_num")
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c5_num")
        price_5 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 5 (บาท):", min_value=0.0, value=0.0, format="%.8f", step=0.0001, key="p5_num")

# --- ประมวลผลข้อมูลหลังบ้าน ---
raw_data = [
    {"ไม้ที่": 1, "cash": cash_1, "price": price_1},
    {"ไม้ที่": 2, "cash": cash_2, "price": price_2},
    {"ไม้ที่": 3, "cash": cash_3, "price": price_3},
    {"ไม้ที่": 4, "cash": cash_4, "price": price_4},
    {"ไม้ที่": 5, "cash": cash_5, "price": price_5}
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
# 🟨 ฝั่งซ้าย [OUTPUT]: แผงควบคุมและกราฟจำลองขึ้นลงอัจฉริยะ
# ----------------------------------------------------
with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📊 2. ประมวลผลพอร์ตฝั่งซื้อ</h3>", unsafe_allow_html=True)
    
    if len(rows) > 0:
        # แสดงตารางผลลัพธ์ฝั่งซื้อ
        df = pd.DataFrame(rows)
        st.table(df)
        
        # จัดระเบียบโซนกรอกราคาเป้าหมาย และกราฟจำลองให้อยู่คู่กัน
        sub_col_target, sub_col_chart = st.columns([1.1, 0.9])
        
        with sub_col_target:
            st.markdown("<h4 style='color: #ffffff; font-size: 13px; font-weight: 600; margin-bottom: 8px;'>🎯 4. จำลองเป้าหมายราคาตั้งขาย (พิมพ์ตัวเลขหรือกดบวก/ลบ)</h4>", unsafe_allow_html=True)
            
            # ช่องกรอกราคาเป้าหมายแบบสะอาด สามารถพิมพ์เลข หรือกดปุ่ม + / - เพื่อดึงจำลองราคาขึ้นลงได้ทันที
            target_sell_price = st.number_input(
                "ปรับราคาเหรียญที่ต้องการทดสอบตั้งขาย (บาท):",
                min_value=0.0,
                value=float(avg_cost_per_coin),
                format="%.8f",
                step=0.0001 if avg_cost_per_coin > 1 else 0.000001,
                key="target_sell_num"
            )
            
            gross_sell_revenue = total_coins * target_sell_price
            sell_fee = gross_sell_revenue * FEE_RATE
            net_sell_revenue = gross_sell_revenue - sell_fee 
            
            pnl_baht = net_sell_revenue - total_invest_cash
            pnl_percent = (pnl_baht / total_invest_cash) * 100
            
            status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
            status_bg = "rgba(0, 255, 102, 0.02)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.02)"
            status_sign = "+" if pnl_baht >= 0 else ""
            
            st.markdown(f"""
            <div style='background-color:{status_bg}; padding:18px; border-radius:12px; border: 1px solid #1e2942; border-left:5px solid {status_color}; box-shadow: 0 8px 16px rgba(0,0,0,0.4);'>
                <h4 style='color:white; margin-top:0px; font-size:13px; font-weight:700; margin-bottom:10px;'>📍 TARGET ANALYSIS: ราคา {format_smart_clean(target_sell_price)} บาท</h4>
                <table style='width:100%; color:white; font-size:13px; border-collapse: collapse;'>
                    <tr style='border-bottom: 1px solid #1e2942;'>
                        <td style='padding:6px 0; color:#64748b;'>💵 ยอดขายรวม (ก่อนหักค่าฟี):</td>
                        <td style='text-align:right; font-weight:600;'>{gross_sell_revenue:,.2f} บาท</td>
                    </tr>
                    <tr style='border-bottom: 1px solid #1e2942;'>
                        <td style='padding:6px 0; color:#64748b;'>📉 หักค่าธรรมเนียมฝั่งขาย (0.25%):</td>
                        <td style='text-align:right; color:#FF3366;'>- {sell_fee:,.2f} บาท</td>
                    </tr>
                    <tr style='border-bottom: 2px solid #1e2942;'>
                        <td style='padding:8px 0; color:#00E5FF; font-weight:bold;'>💰 ยอดเงินสุทธิที่จะได้รับจริง (หักฟีแล้ว):</td>
                        <td style='text-align:right; color:#00E5FF; font-size:15px; font-weight:bold;'>{net_sell_revenue:,.2f} บาท</td>
                    </tr>
                    <tr>
                        <td style='padding:10px 0 0 0; color:{status_color}; font-weight:bold;'>📈 สรุปกำไร / ขาดทุนสุทธิ:</td>
                        <td style='text-align:right; color:{status_color}; font-size:18px; font-weight:900; padding-top:6px;'>
                            {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        with sub_col_chart:
            st.markdown("<h4 style='color: #ffffff; font-size: 13px; font-weight: 600; margin
