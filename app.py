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
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ CYBERPUNK NEON TRADER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>MULTI-TIER COST CALCULATOR • 5 ไม้ละเอียด (FEE 0.25%)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 30px; box-shadow: 0 1px 5px rgba(0,255,204,0.1);'></div>", unsafe_allow_html=True)

# ฟังก์ชันจัดปลอกทศนิยมอัจฉริยะ ป้องกันเลข 0 ลากหางยาว
def format_smart(value):
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

# ฟังก์ชันเซฟสำหรับแปลงข้อความกลับเป็นตัวเลข float
def safe_float(val_str, default=0.0):
    try:
        return float(val_str.replace(',', '').strip())
    except ValueError:
        return default

# กำหนดอัตราค่าธรรมเนียม Bitkub (0.25%)
FEE_RATE = 0.0025

# สร้างสัดส่วนหน้าจอ ฝั่งซ้าย (Input ข้อมูล) และ ฝั่งขวา (สรุปผลและจำลองเป้าหมาย)
col_input, col_result = st.columns([1, 1.25])

with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 15px; letter-spacing: 0.5px;'>📥 [INPUT] บันทึกรายการเข้าซื้อ</h3>", unsafe_allow_html=True)
    
    # 💡 เคลียร์ค่าเริ่มต้นของราคาตอนซื้อตรงไม้ต่างๆ ให้เป็น "0.00" คลีนๆ ทั้งหมดแล้วครับ
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", value="2600.00", key="c1")
        price_1_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", value="47.55", key="p1")
        cash_1, price_1 = safe_float(cash_1_raw, 2600.0), safe_float(price_1_raw, 47.55)
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", value="0.00", key="c2")
        price_2_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", value="0.00", key="p2")
        cash_2, price_2 = safe_float(cash_2_raw, 0.0), safe_float(price_2_raw, 0.0)
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", value="0.00", key="c3")
        price_3_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", value="0.00", key="p3")
        cash_3, price_3 = safe_float(cash_3_raw, 0.0), safe_float(price_3_raw, 0.0)
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", value="0.00", key="c4")
        price_4_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", value="0.00", key="p4")
        cash_4, price_4 = safe_float(cash_4_raw, 0.0), safe_float(price_4_raw, 0.0)
        
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5_raw = st.text_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", value="0.00", key="c5")
        price_5_raw = st.text_input("ราคาเหรียญตอนซื้อ ไม้ 5 (บาท):", value="0.00", key="p5")
        cash_5, price_5 = safe_float(cash_5_raw, 0.0), safe_float(price_5_raw, 0.0)

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
    if item["input_cash"] > 0 and item["buy_price"] > 0:
        fee = item["input_cash"] * FEE_RATE
        net_buy = item["input_cash"] - fee
        coins_received = net_buy / item["buy_price"]
        
        total_invest_cash += item["input_cash"]
        total_buy_fee += fee
        total_coins += coins_received
        
        rows.append({
            "ไม้ที่": f"ไม้ {item['ไม้ที่']}",
            "เงินทุนซื้อ (บาท)": f"{item['input_cash']:,.2f}",
            "ราคาตอนซื้อ": format_smart(item['buy_price']),
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{fee:,.2f}",
            "เหรียญที่ได้รับ": f"{coins_received:,.4f}"
        })

with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 15px; letter-spacing: 0.5px;'>📊 [OUTPUT] ประมวลผลพอร์ตฝั่งซื้อ</h3>", unsafe_allow_html=True)
    if len(rows) > 0:
        df = pd.DataFrame(rows)
        st.table(df)
        
        avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0
        
        st.markdown("<h4 style='color: #ffffff; font-size: 14px; font-weight: 600; margin-top: 25px; margin-bottom: 12px; letter-spacing: 0.5px;'>🎯 3. สรุปแดชบอร์ดต้นทุนเฉลี่ยสุทธิ</h4>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>💰 เงินทุนรวมทั้งหมด</div>
                <div class='neon-val'>{total_invest_cash:,.2f} <span style='font-size:12px; color:#64748b;'>THB</span></div>
                <div style='color:#475569; font-size:11px; margin-top:5px; font-weight:500;'>ฟีซื้อรวม {total_buy_fee:,.2f} บ.</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>🪙 จำนวนเหรียญในมือ</div>
                <div class='neon-val' style='color:#00E5FF;'>{total_coins:,.4f}</div>
                <div style='color:#475569; font-size:11px; margin-top:5px; font-weight:500;'>เหรียญสุทธิหักฟีแล้ว</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='neon-card' style='border-color: #00FFCC; box-shadow: 0 0 12px rgba(0,255,204,0.15);'>
                <div class='neon-lbl' style='color:#00FFCC; font-weight:bold;'>🏷️ ต้นทุนเฉลี่ย / เหรียญ</div>
                <div class='neon-val' style='color:#00FFCC;'>{format_smart(avg_cost_per_coin)} <span style='font-size:12px; color:#00FFCC;'>บ.</span></div>
                <div style='color:#00FFCC; font-size:10px; margin-top:5px; font-weight:600;'>*BREAK-EVEN PRICE</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='border-bottom: 1px solid #1e2942; margin: 25px 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 12px; letter-spacing: 0.5px;'>🎯 4. จำลองเป้าหมายราคาตั้งขาย</h3>", unsafe_allow_html=True)
        
        # 💡 ตรงเป้าหมาย: ดึงราคาเฉลี่ยที่ล้างเลข 0 ส่วนเกินออกแล้วมาตั้งต้นให้ในช่อง พิมพ์แก้ได้อิสระและคลีนแน่นอนครับ
        default_sell_str = format_smart(avg_cost_per_coin).replace(',', '')
        target_sell_raw = st.text_input(
            "พิมพ์กรอกราคาเหรียญที่ต้องการตั้งขายจริงในกระดาน (บาท):",
            value=default_sell_str,
            key="target_sell"
        )
        target_sell_price = safe_float(target_sell_raw, avg_cost_per_coin)
        
        gross_sell_revenue = total_coins * target_sell_price
        sell_fee = gross_sell_revenue * FEE_RATE
        net_sell_revenue = gross_sell_revenue - sell_fee 
        
        pnl_baht = net_sell_revenue - total_invest_cash
        pnl_percent = (pnl_baht / total_invest_cash) * 100
        
        status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
        status_bg = "rgba(0, 255, 102, 0.03)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.03)"
        status_sign = "+" if pnl_baht >= 0 else ""
        
        st.markdown(f"""
        <div style='background-color:{status_bg}; padding:22px; border-radius:12px; border: 1px solid #1e2942; border-left:6px solid {status_color}; margin-top:15px; box-shadow: 0 10px 20px rgba(0,0,0,0.4);'>
            <h4 style='color:white; margin-top:0px; font-size:15px; font-weight:700; margin-bottom:15px; letter-spacing: 0.5px;'>📍 TARGET ANALYSIS: ราคา {format_smart(target_sell_price)} บาท</h4>
            <table style='width:100%; color:white; font-size:14px; border-collapse: collapse;'>
                <tr style='border-bottom: 1px solid #1e2942;'>
                    <td style='padding:10px 0; color:#64748b; font-weight:500;'>💵 ยอดขายรวม (ก่อนหักฟี):</td>
                    <td style='text-align:right; font-weight:600; font-size:15px;'>{gross_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 1px solid #1e2942;'>
                    <td style='padding:10px 0; color:#64748b; font-weight:500;'>📉 ค่าธรรมเนียมฝั่งขาย (0.25%):</td>
                    <td style='text-align:right; color:#FF3366; font-weight:600;'>- {sell_fee:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 2px solid #1e2942;'>
                    <td style='padding:14px 0; color:#00E5FF; font-weight:bold;'>💰 ยอดเงินเข้าบัญชีสุทธิ (หักฟีแล้ว):</td>
                    <td style='text-align:right; color:#00E5FF; font-size:20px; font-weight:bold;'>{net_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr>
                    <td style='padding:16px 0 5px 0; color:{status_color}; font-weight:bold; font-size:16px; text-transform:uppercase; letter-spacing:0.5px;'>📈 Net Profit / Loss:</td>
                    <td style='text-align:right; color:{status_color}; font-size:24px; font-weight:black; padding-top:10px;'>
                        {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("💡 SYSTEMS READY: กรุณากรอกจำนวนเงินทุนใน 'ไม้ที่ 1' ฝั่งซ้ายมือ เพื่อเริ่มต้นระบบคำนวณครับ")
