import streamlit as st
import pandas as pd

# --- 1. ตั้งค่าโครงสร้างหน้าจอและ CSS ตกแต่งความสวยงามทันสมัย ---
st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

# ใส่ CSS Custom ตกแต่งสไตล์ Cyberpunk Neon Dark Mode
st.markdown("""
<style>
    /* ปรับพื้นหลังและฟอนต์โดยรวม */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    /* ตกแต่งกล่องสรุปผลข้อมูล (Metrics Card) ให้เรืองแสงสวยงาม */
    .neon-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .neon-card:hover {
        border-color: #00FFCC;
        box-shadow: 0 0 12px rgba(0, 255, 204, 0.2);
    }
    .neon-lbl { font-size: 14px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
    .neon-val { font-size: 24px; font-weight: bold; color: #ffffff; }
    
    /* ตกแต่งหัวข้อ Expander ฝั่งซ้าย */
    .stExpander {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    
    /* ตกแต่งตารางผลลัพธ์ */
    .stTable {
        background-color: #111827;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อแอปดีไซน์โมเดิร์น
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px;'>🧮 Smart Multi-Tier Cost Calculator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 15px;'>เครื่องมือคำนวณต้นทุนเฉลี่ย และจำลองกำไรสุทธิ 5 ไม้ละเอียด (หักลบค่าฟี ซื้อ-ขาย 0.25% เรียบร้อย)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1f2937; margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# กำหนดอัตราค่าธรรมเนียม Bitkub (0.25%)
FEE_RATE = 0.0025

# สร้าง Layout แยกฝั่งซ้าย (กรอกข้อมูลซื้อ) และ ฝั่งขวา (สรุปผลและจำลองราคาขาย)
col_input, col_result = st.columns([1, 1.25])

with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 18px; margin-bottom: 15px;'>📥 1. บันทึกรายการเข้าซื้อ รายไม้</h3>", unsafe_allow_html=True)
    
    # ไม้ที่ 1
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", min_value=0.0, value=2600.0, step=100.0, key="c1")
        price_1 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", min_value=0.00000001, value=47.55000000, format="%.8f", step=0.00000001, key="p1")
    
    # ไม้ที่ 2
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c2")
        price_2 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", min_value=0.00000001, value=45.00000000, format="%.8f", step=0.00000001, key="p2")
        
    # ไม้ที่ 3
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c3")
        price_3 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", min_value=0.00000001, value=43.00000000, format="%.8f", step=0.00000001, key="p3")
        
    # ไม้ที่ 4
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c4")
        price_4 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", min_value=0.00000001, value=41.00000000, format="%.8f", step=0.00000001, key="p4")
        
    # ไม้ที่ 5
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c5")
        price_5 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 5 (บาท):", min_value=0.00000001, value=39.00000000, format="%.8f", step=0.00000001, key="p5")

# รวบรวมข้อมูลและคำนวณรายละเอียดแต่ละไม้
raw_data = [
    {"ไม้ที่": 1, "input_cash": cash_1, "buy_price": price_1},
    {"ไม้ที่": 2, "input_cash": cash_2, "buy_price": price_2},
    {"ไม้ที่": 3, "input_cash": cash_3, "buy_price": price_3},
    {"ไม้ที่": 4, "input_cash": cash_4, "buy_price": price_4},
    {"ไม้ที่": 5, "input_cash": cash_5, "buy_price": price_5}
]

rows = []
total_invest_cash = 0.0
total_coins = 0.0
total_buy_fee = 0.0

for item in raw_data:
    if item["input_cash"] > 0:
        fee = item["input_cash"] * FEE_RATE
        net_buy = item["input_cash"] - fee
        coins_received = net_buy / item["buy_price"]
        
        total_invest_cash += item["input_cash"]
        total_buy_fee += fee
        total_coins += coins_received
        
        rows.append({
            "ไม้ที่": f"ไม้ {item['ไม้ที่']}",
            "เงินทุนซื้อ (บาท)": f"{item['input_cash']:,.2f}",
            "ราคาตอนซื้อ": f"{item['buy_price']:,.8f}",
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{fee:,.2f}",
            "เหรียญที่ได้รับ": f"{coins_received:,.4f}"
        })

# --- ฝั่งขวา: แสดงผลการคำนวณสุทธิ ---
with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 18px; margin-bottom: 15px;'>📊 2. ประมวลผลพอร์ตฝั่งซื้อ</h3>", unsafe_allow_html=True)
    if len(rows) > 0:
        df = pd.DataFrame(rows)
        st.table(df)
        
        # คำนวณราคาเฉลี่ยสุทธิ
        avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0
        
        st.markdown("<h4 style='color: #ffffff; font-size: 15px; margin-top: 20px; margin-bottom: 10px;'>🎯 3. บอร์ดสรุปต้นทุนเฉลี่ยสุทธิ</h4>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>💰 เงินทุนรวมทั้งหมด</div>
                <div class='neon-val'>{total_invest_cash:,.2f} <span style='font-size:13px; color:#94a3b8;'>บ.</span></div>
                <div style='color:#64748b; font-size:11px; margin-top:4px;'>ฟีซื้อ {total_buy_fee:,.2f} บ.</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>🪙 จำนวนเหรียญในมือ</div>
                <div class='neon-val' style='color:#00E5FF;'>{total_coins:,.4f}</div>
                <div style='color:#64748b; font-size:11px; margin-top:4px;'>เหรียญสุทธิหลังหักฟี</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='neon-card' style='border: 1px solid #00FFCC; box-shadow: 0 0 10px rgba(0,255,204,0.1);'>
                <div class='neon-lbl' style='color:#00FFCC; font-weight:bold;'>🏷️ ทุนเฉลี่ย / เหรียญ</div>
                <div class='neon-val' style='color:#00FFCC;'>{avg_cost_per_coin:,.8f} <span style='font-size:13px; color:#00FFCC;'>บ.</span></div>
                <div style='color:#00FFCC; font-size:11px; margin-top:4px;'>*จุดคุ้มทุนซื้อ</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='border-bottom: 1px solid #1f2937; margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        # โซนตั้งเป้าหมายราคาขายเพื่อดูผลกำไร
        st.markdown("<h3 style='color: #00FFCC; font-size: 18px; margin-bottom: 10px;'>🎯 4. จำลองตั้งเป้าหมายราคาขาย</h3>", unsafe_allow_html=True)
        
        target_sell_price = st.number_input(
            "พิมพ์กรอกราคาเหรียญที่ต้องการตั้งขายจริงในกระดาน (บาท):",
            min_value=0.00000001,
            value=float(avg_cost_per_coin),
            format="%.8f",
            step=0.00000001,
            key="target_sell"
        )
        
        # คำนวณฝั่งขาย
        gross_sell_revenue = total_coins * target_sell_price
        sell_fee = gross_sell_revenue * FEE_RATE
        net_sell_revenue = gross_sell_revenue - sell_fee 
        
        # คำนวณกำไร / ขาดทุน
        pnl_baht = net_sell_revenue - total_invest_cash
        pnl_percent = (pnl_baht / total_invest_cash) * 100
        
        # ปรับสีตามสถานะ กำไรเขียว / ขาดทุนแดง
        status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
        status_sign = "+" if pnl_baht >= 0 else ""
        
        st.markdown(f"""
        <div style='background-color:#111827; padding:22px; border-radius:12px; border: 1px solid #1f2937; border-left:6px solid {status_color}; margin-top:15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);'>
            <h4 style='color:white; margin-top:0px; font-size:16px; margin-bottom:15px;'>📍 สรุปผลลัพธ์ที่เป้าหมายราคา {target_sell_price:,.8f} บาท</h4>
            <table style='width:100%; color:white; font-size:15px; border-collapse: collapse;'>
                <tr style='border-bottom: 1px solid #1f2937;'>
                    <td style='padding:8px 0; color:#94a3b8;'>💵 ยอดขายรวม (ก่อนหักค่าฟี):</td>
                    <td style='text-align:right; font-weight:500;'>{gross_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 1px solid #1f2937;'>
                    <td style='padding:8px 0; color:#94a3b8;'>📉 หักค่าธรรมเนียมฝั่งขาย (0.25%):</td>
                    <td style='text-align:right; color:#FF3366;'>- {sell_fee:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 2px solid #334155;'>
                    <td style='padding:12px 0; color:#00E5FF; font-weight:bold;'>💰 ยอดเงินสุทธิที่จะได้รับจริง (หักฟีแล้ว):</td>
                    <td style='text-align:right; color:#00E5FF; font-size:19px; font-weight:bold;'>{net_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr>
                    <td style='padding:15px 0 5px 0; color:{status_color}; font-weight:bold; font-size:17px;'>📈 สรุปกำไร / ขาดทุนสุทธิ:</td>
                    <td style='text-align:right; color:{status_color}; font-size:22px; font-weight:bold; padding-top:10px;'>
                        {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("💡 ระบบพร้อมทำงาน! กรุณากรอกจำนวนเงินทุนและราคาใน 'ไม้ที่ 1' ฝั่งซ้ายเพื่อเริ่มคำนวณความหล่อครับ")
