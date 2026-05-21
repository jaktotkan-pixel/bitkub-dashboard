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

FEE_RATE = 0.0025

# --- LAYOUT DIVISION (โครงสร้างหลักแยกฝั่งซ้าย-ขวาอย่างสมดุล) ---
col_result, col_input = st.columns([1.2, 1])

# ----------------------------------------------------
# 🔴 ฝั่งขวา [INPUT]: บันทึกรายการเข้าซื้อ 
# ----------------------------------------------------
with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📥 [INPUT] บันทึกรายการเข้าซื้อ</h3>", unsafe_allow_html=True)
    
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
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

# --- จัดเตรียมข้อมูลชุดพื้นฐานเพื่อคำนวณสัดส่วน ---
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
            "เหรียญที่ได้รับ": format_smart_clean(coins_received)
        })

avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0

# ----------------------------------------------------
# 🟨 ฝั่งซ้าย [OUTPUT]: ประมวลผลพอร์ตและความคุ้มทุน
# ----------------------------------------------------
with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 16px; font-weight: 700; margin-bottom: 15px;'>📊 [OUTPUT] ประมวลผลพอร์ตและความคุ้มทุน</h3>", unsafe_allow_html=True)
    
    # 🌟 ส่วนที่ 1: จำลองเป้าหมายราคาตั้งขาย
    st.markdown("<h4 style='color: #ffffff; font-size: 13px; font-weight: 600; margin-bottom: 4px;'>🎯 1. จำลองเป้าหมายราคาตั้งขาย</h4>", unsafe_allow_html=True)
    
    target_sell_price_raw = st.number_input(
        "พิมพ์กรอกราคาเหรียญที่ต้องการตั้งขายจริงในกระดาน (บาท):",
        min_value=0.0,
        value=None,
        format="%.8f",
        step=0.0001,
        key="target_sell_num",
        placeholder="กรอกราคาตั้งขายเพื่อจำลองกำไร..."
    )
    
    target_sell_price = target_sell_price_raw if target_sell_price_raw is not None else 0.0
    
    # ประมวลผลรายรับฝั่งตั้งขาย
    gross_sell_revenue = total_coins * target_sell_price
    sell_fee = gross_sell_revenue * FEE_RATE
    net_sell_revenue = gross_sell_revenue - sell_fee 
    
    if total_invest_cash > 0:
        pnl_baht = net_sell_revenue - total_invest_cash
        pnl_percent = (pnl_baht / total_invest_cash) * 100
    else:
        pnl_baht = 0.0
        pnl_percent = 0.0
        
    status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
    status_bg = "rgba(0, 255, 102, 0.02)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.02)"
    status_sign = "+" if pnl_baht >= 0 else ""
    
    st.markdown(f"""
    <div style='background-color:{status_bg}; padding:18px; border-radius:12px; border: 1px solid #1e2942; border-left:5px solid {status_color}; box-shadow: 0 8px 16px rgba(0,0,0,0.4); margin-bottom: 25px;'>
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
                <td style='padding:8px 0; color:#00E5FF; font-weight:bold;'>💰 ยอดเงินเข้าบัญชีสุทธิ (หักฟีแล้ว):</td>
                <td style='text-align:right; color:#00E5FF; font-size:15px; font-weight:bold;'>{net_sell_revenue:,.2f} บาท</td>
            </tr>
            <tr>
                <td style='padding:10px 0 0 0; color:{status_color}; font-weight:bold;'>📈 NET PROFIT / LOSS:</td>
                <td style='text-align:right; color:{status_color}; font-size:18px; font-weight:900; padding-top:6px;'>
                    {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    # 🌟 ส่วนที่ 2: สรุปแดชบอร์ดต้นทุนเฉลี่ยสุทธิ (แสดงผลครบถ้วน 3 ใบเรียงหน้ากระดานสวยงาม ไม่ตกขอบ)
    st.markdown("<h4 style='color: #ffffff; font-size: 13px; font-weight: 600; margin-bottom: 10px;'>🎯 2. สรุปแดชบอร์ดต้นทุนเฉลี่ยสุทธิ</h4>", unsafe_allow_html=True)
    
    if len(rows) > 0:
        st.markdown(f"""
        <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; width: 100%;">
            <div class='neon-card' style='flex: 1; min-width: 140px;'>
                <div class='neon-lbl'>💰 เงินทุนรวมทั้งหมด</div>
                <div class='neon-val'>{total_invest_cash:,.2f} <span style='font-size:11px; color:#64748b;'>THB</span></div>
                <div style='color:#475569; font-size:11px; margin-top:3px;'>ฟีซื้อรวม {total_buy_fee:,.2f} บ.</div>
            </div>
            <div class='neon-card' style='flex: 1; min-width: 140px;'>
                <div class='neon-lbl'>🪙 จำนวนเหรียญในมือ</div>
                <div class='neon-val' style='color:#00E5FF;'>{format_smart_clean(total_coins)}</div>
                <div style='color:#475569; font-size:11px; margin-top:3px;'>เหรียญสุทธิหักฟีแล้ว</div>
            </div>
            <div class='neon-card' style='flex: 1; min-width: 140px; border-color: #00FFCC;'>
                <div class='neon-lbl' style='color:#00FFCC; font-weight:bold;'>🏷️ ต้นทุนเฉลี่ย / เหรียญ</div>
                <div class='neon-val' style='color:#00FFCC;'>{format_smart_clean(avg_cost_per_coin)} <span style='font-size:11px;'>บ.</span></div>
                <div style='color:#00FFCC; font-size:10px; margin-top:3px; font-weight:600;'>*BREAK-EVEN PRICE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
        # ตารางผลลัพธ์ข้อมูลรายไม้ สดสะอาด ไม่มีอะไรมาบดบังด้านล่าง
        df = pd.DataFrame(rows)
        st.table(df)
        
    else:
        st.info("💡 SYSTEMS READY: กรุณากรอกจำนวนเงินทุนและราคาเหรียญในฝั่งขวา เพื่อเปิดระบบประมวลผลพอร์ตครับ")
