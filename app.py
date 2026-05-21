import streamlit as st

# --- 1. SETTING & CYBERPUNK CSS STYLE ---
st.set_page_config(page_title="Bitkub Multi-Coin Dashboard", layout="wide")

# ปรับแต่งธีมภาพรวมด้วยสไตล์มืด Cyberpunk Neon
st.logo("https://www.bitkub.com/static/images/logo-bitkub.e25b16f3.svg", icon_image="https://www.bitkub.com/static/images/logo-bitkub.e25b16f3.svg") if hasattr(st, "logo") else None

st.markdown("""
<style>
    /* พื้นหลังมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* ปรับแต่งช่อง Input ให้คลีน มินิมอล */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #060913 !important;
        color: #ffffff !important;
        border: 1px solid #1e2942 !important;
    }
    
    /* ซ่อนปุ่มหรือแถบที่ไม่จำเป็น */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักสไตล์ Trader Space Station
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ BITKUB MULTI-COIN MONITOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>ระบบคำนวณแยกอิสระ 5 บล็อกสี่เหลี่ยมเดี่ยว • แก้ไขบั๊กการแสดงผล HTML เรียบร้อย</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 35px;'></div>", unsafe_allow_html=True)

# รายชื่อเหรียญใน Bitkub สำหรับให้เลือกใน Dropdown
BITKUB_COINS = [
    "เลือกเหรียญ...", "ZEREBRO", "BTC", "ETH", "KUB", "XRP", "ADA", "SOL", "DOGE", "BNB", 
    "DOT", "GALA", "NEAR", "OP", "ARB", "AVAX", "LINK", "LTC", "IOST", "USDT"
]

# ฟังก์ชันจัดปลอกทศนิยมส่วนแสดงผล ลบเลข 0 ลากหางออก 100% แต่ถ้าเป็นเลขยาวๆ โชว์ครบปกติ
def format_smart_clean(value):
    if value == 0 or value is None:
        return "0.00"
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

# ฟังก์ชันแปลงข้อความจากช่องกรอกให้เป็น Float ปลอดภัย ไร้ Error
def parse_float_input(val_str):
    if not val_str or val_str.strip() == "":
        return None
    try:
        return float(val_str.replace(",", "").strip())
    except ValueError:
        return 0.0

FEE_RATE = 0.0025

# --- ลูปสร้างกล่องสี่เหลี่ยมเดียวรวมศูนย์ 5 ชุดแยกอิสระ ---
for i in range(1, 6):
    
    # ใช้ st.container ครอบเพื่อสร้างขอบเขตกล่องสี่เหลี่ยมเดียวกันอย่างสมบูรณ์แบบ
    with st.container(border=True):
        st.markdown(f"""
        <div style="font-size: 15px; font-weight: 800; color: #00E5FF; margin-bottom: 12px; letter-spacing: 0.5px;">
            📦 ชุดที่ {i} : บล็อกประมวลผลเหรียญรายไม้ (รวมศูนย์ในกรอบเดียว)
        </div>
        """, unsafe_allow_html=True)
        
        # เจาะ Grid ด้านในกล่องสี่เหลี่ยม: แยกซ้าย (กรอกข้อมูล) ขวา (แดชบอร์ดสรุปผล)
        inner_col_in, inner_col_out = st.columns([1, 1.2])
        
        with inner_col_in:
            coin_name = st.selectbox(f"🪙 เลือกเหรียญ (ชุด {i}):", BITKUB_COINS, key=f"coin_{i}")
            cash_raw = st.text_input(f"💵 เงินทุนที่ใช้ซื้อ (บาท):", key=f"cash_{i}", placeholder="เช่น 1000")
            buy_price_raw = st.text_input(f"🏷️ ราคาเหรียญตอนซื้อ (บาท):", key=f"bp_{i}", placeholder="เช่น 1.0334")
            sell_price_raw = st.text_input(f"🎯 ราคาที่ต้องการตั้งขาย (บาท):", key=f"sp_{i}", placeholder="เช่น 1.20")
            
        with inner_col_out:
            # ดึงค่ามาคำนวณหลังบ้าน
            cash = parse_float_input(cash_raw) if parse_float_input(cash_raw) is not None else 0.0
            buy_price = parse_float_input(buy_price_raw) if parse_float_input(buy_price_raw) is not None else 0.0
            sell_price = parse_float_input(sell_price_raw) if parse_float_input(sell_price_raw) is not None else 0.0
            
            if coin_name != "เลือกเหรียญ..." and cash > 0 and buy_price > 0:
                # 1. คำนวณฝั่งซื้อ
                buy_fee = cash * FEE_RATE
                net_buy = cash - buy_fee
                coins_received = net_buy / buy_price
                
                # 2. คำนวณฝั่งขาย
                gross_sell = coins_received * sell_price
                sell_fee = gross_sell * FEE_RATE
                net_sell = gross_sell - sell_fee
                
                # 3. กำไร/ขาดทุนสุทธิ
                pnl_baht = net_sell - cash
                pnl_percent = (pnl_baht / cash) * 100 if cash > 0 else 0.0
                
                status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
                status_bg = "rgba(0, 255, 102, 0.02)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.02)"
                status_sign = "+" if pnl_baht >= 0 else ""
                
                # ใช้ st.html สำหรับพ่นกราฟิกการ์ด เพื่อไม่ให้โค้ดหลุดรั่วออกมาหน้าจออีก
                st.html(f"""
                <div style='background: {status_bg}; padding: 15px; border-radius: 10px; border: 1px solid #1e2942; border-left: 5px solid {status_color}; margin-top: 5px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                        <span style='font-size: 14px; font-weight: bold; color: #ffffff;'>📊 NET SUMMARY ({coin_name})</span>
                        <span style='font-size: 16px; font-weight: 900; color: {status_color};'>
                            {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บ.)
                        </span>
                    </div>
                    
                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1;">
                            <div style="font-size: 10px; color: #64748b; font-weight: 600;">🪙 ได้รับเหรียญสุทธิ</div>
                            <div style="font-size: 14px; font-weight: bold; color: #00E5FF; margin-top: 3px;">{format_smart_clean(coins_received)}</div>
                        </div>
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1;">
                            <div style="font-size: 10px; color: #64748b; font-weight: 600;">📈 เงินเข้าบัญชีสุทธิ</div>
                            <div style="font-size: 14px; font-weight: bold; color: #ffffff; margin-top: 3px;">{net_sell:,.2f} บ.</div>
                        </div>
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1; border-color: {status_color};">
                            <div style="font-size: 10px; color: {status_color}; font-weight: 600;">NET PROFIT / LOSS</div>
                            <div style="font-size: 14px; font-weight: bold; color: {status_color}; margin-top: 3px;">{status_sign}{pnl_baht:,.2f} บ.</div>
                        </div>
                    </div>
                    
                    <table style='width:100%; color:#64748b; font-size:11px; border-collapse: collapse; margin-top: 5px;'>
                        <tr style='border-bottom: 1px solid rgba(30, 41, 66, 0.4);'>
                            <td style='padding: 3px 0;'>💵 ทุนซื้อ: {cash:,.2f} บ. (หักฟีซื้อ: {buy_fee:,.2f} บ.)</td>
                            <td style='text-align: right; color:#ffffff;'>ราคาเข้า: {format_smart_clean(buy_price)} บ.</td>
                        </tr>
                        <tr>
                            <td style='padding: 3px 0;'>🎯 ยอดขายรวม: {gross_sell:,.2f} บ. (หักฟีขาย: {sell_fee:,.2f} บ.)</td>
                            <td style='text-align: right; color:#ffffff;'>ราคาขาย: {format_smart_clean(sell_price)} บ.</td>
                        </tr>
                    </table>
                </div>
                """)
            else:
                # หน้าตาสแตนด์บายรอข้อมูลในกรอบขวาอย่างสุภาพ ไม่มีโค้ดหลุดร่วง
                st.html(f"""
                <div style='text-align: center; padding: 52px 15px; color: #475569; border: 1px dashed #1e2942; border-radius: 10px; font-size: 13px; background: rgba(6, 9, 19, 0.3); margin-top: 5px;'>
                    ⏳ [STANDBY] กรุณาเลือกเหรียญ และระบุเงินทุน + ราคาซื้อ เพื่อเปิดระบบแสดงแดชบอร์ดสรุปผลครับ
                </div>
                """)
                
    # เว้นช่องไฟระหว่างบล็อกสี่เหลี่ยมให้ดูง่ายสบายตา
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
