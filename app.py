import streamlit as st

# --- 1. SETTING & CYBERPUNK CSS STYLE ---
st.set_page_config(page_title="Bitkub Multi-Currency Dashboard", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* กล่องสรุปผลรวมยักษ์บนสุด */
    .total-portfolio-box {
        background: linear-gradient(135deg, #151324 0%, #0d1b2a 100%);
        padding: 25px;
        border-radius: 16px;
        border: 2px solid #00FFCC;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.25);
        margin-bottom: 35px;
        text-align: center;
    }
    
    /* ปรับแต่งช่อง Input ให้คลีน มินิมอล */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #060913 !important;
        color: #ffffff !important;
        border: 1px solid #1e2942 !important;
    }
    
    /* ซ่อนปุ่มที่ไม่จำเป็น */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักสไตล์ Trader Space Station
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ BITKUB MULTI-COIN MONITOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>ระบบคำนวณแยกอิสระ 5 บล็อกสี่เหลี่ยมเดี่ยว • พร้อมปุ่มสลับสกุลเงินหลักพอร์ต</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🎛️ [CURRENCY SELECTOR] ปุ่มสลับ THB / USDT ด้านบนสุดของแอป
# -----------------------------------------------------------------
currency_mode = st.radio(
    "💱 เลือกสกุลเงินหลักที่ใช้เทรดในพอร์ตนี้:",
    ["THB (บาทไทย)", "USDT (ดอลลาร์สหรัฐ)"],
    index=0,
    horizontal=True
)
currency_label = "THB" if "THB" in currency_mode else "USDT"

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# รายชื่อเหรียญใน Bitkub
BITKUB_COINS = [
    "เลือกเหรียญ...", "ZEREBRO", "STO", "BTC", "ETH", "KUB", "XRP", "ADA", "SOL", "DOGE", "BNB", 
    "DOT", "GALA", "NEAR", "OP", "ARB", "AVAX", "LINK", "LTC", "IOST", "USDT"
]

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

def parse_float_input(val_str):
    if not val_str or val_str.strip() == "":
        return None
    try:
        return float(val_str.replace(",", "").strip())
    except ValueError:
        return 0.0

FEE_RATE = 0.0025

# --- [PRE-CALCULATION] วิ่งเก็บค่าล่วงหน้าเพื่อทำสรุปยอดรวม ---
grand_total_cash = 0.0
grand_total_net_sell = 0.0
grand_total_pnl_baht = 0.0
active_blocks_count = 0

for idx in range(1, 6):
    c_name = st.session_state.get(f"coin_{idx}", "เลือกเหรียญ...")
    c_raw = st.session_state.get(f"cash_{idx}", "")
    bp_raw = st.session_state.get(f"bp_{idx}", "")
    sp_raw = st.session_state.get(f"sp_{idx}", "")
    
    cash_val = parse_float_input(c_raw) if parse_float_input(c_raw) is not None else 0.0
    bp_val = parse_float_input(bp_raw) if parse_float_input(bp_raw) is not None else 0.0
    sp_val = parse_float_input(sp_raw) if parse_float_input(sp_raw) is not None else 0.0
    
    if c_name != "เลือกเหรียญ..." and cash_val > 0 and bp_val > 0:
        active_blocks_count += 1
        b_fee = cash_val * FEE_RATE
        n_buy = cash_val - b_fee
        coins = n_buy / bp_val
        
        g_sell = coins * sp_val
        s_fee = g_sell * FEE_RATE
        n_sell = g_sell - s_fee
        
        pnl_b = n_sell - cash_val
        
        grand_total_cash += cash_val
        grand_total_net_sell += n_sell
        grand_total_pnl_baht += pnl_b

# -----------------------------------------------------------------
# 🌟 [TOP RENDER] กล่องแดชบอร์ดสรุปเงินรวมทุกไม้ (TOTAL PORTFOLIO SUMMARY)
# -----------------------------------------------------------------
if active_blocks_count > 0:
    grand_pnl_percent = (grand_total_pnl_baht / grand_total_cash) * 100 if grand_total_cash > 0 else 0.0
    g_status_color = "#00FF66" if grand_total_pnl_baht >= 0 else "#FF3366"
    g_status_sign = "+" if grand_total_pnl_baht >= 0 else ""
    
    st.html(f"""
    <div class="total-portfolio-box">
        <div style="font-size: 13px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">
            📊 TOTAL PORTFOLIO SUMMARY (สรุปผลรวมพอร์ตทั้งหมด {active_blocks_count} ไม้)
        </div>
        <div style="font-size: 38px; font-weight: 900; color: {g_status_color}; text-shadow: 0 0 15px {g_status_color}40; margin-bottom: 15px;">
            {g_status_sign}{grand_total_pnl_baht:,.2f} <span style="font-size: 18px; font-weight: 700;">{currency_label} ({g_status_sign}{grand_pnl_percent:,.2f}%)</span>
        </div>
        
        <div style="display: flex; gap: 15px; justify-content: center; max-width: 800px; margin: 0 auto;">
            <div style="background: rgba(6, 9, 19, 0.6); padding: 12px 25px; border-radius: 8px; border: 1px solid #1e2942; flex: 1;">
                <div style="font-size: 11px; color: #64748b; font-weight: 600;">💵 เงินทุนรวมทุกไม้ ({currency_label})</div>
                <div style="font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;">{grand_total_cash:,.2f} {currency_label}</div>
            </div>
            <div style="background: rgba(6, 9, 19, 0.6); padding: 12px 25px; border-radius: 8px; border: 1px solid #1e2942; flex: 1;">
                <div style="font-size: 11px; color: #00E5FF; font-weight: 600;">💰 เงินเข้าบัญชีสุทธิรวมทั้งหมด ({currency_label})</div>
                <div style="font-size: 20px; font-weight: bold; color: #00E5FF; margin-top: 2px;">{grand_total_net_sell:,.2f} {currency_label}</div>
            </div>
        </div>
    </div>
    """)
else:
    st.info(f"💡 SYSTEMS READY: กรุณากรอกข้อมูลเหรียญในบล็อกด้านล่าง ระบบจะคำนวณรวมยอดเป็นหน่วย {currency_label} ให้ทันทีครับพี่จักรกฤช")


# -----------------------------------------------------------------
# 📦 [BODY RENDER] ลูปสร้างบล็อกสี่เหลี่ยมเดี่ยวรายเหรียญ 5 ชุด
# -----------------------------------------------------------------
for i in range(1, 6):
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="font-size: 15px; font-weight: 800; color: #00E5FF; margin-bottom: 12px; letter-spacing: 0.5px;">
            📦 ชุดที่ {i} : บล็อกประมวลผลเหรียญรายไม้ ({currency_label})
        </div>
        """, unsafe_allow_html=True)
        
        inner_col_in, inner_col_out = st.columns([1, 1.2])
        
        with inner_col_in:
            coin_name = st.selectbox(f"🪙 เลือกเหรียญ (ชุด {i}):", BITKUB_COINS, key=f"coin_{i}")
            cash_raw = st.text_input(f"💵 เงินทุนที่ใช้ซื้อ ({currency_label}):", key=f"cash_{i}", placeholder=f"ระบุยอดเงิน {currency_label}")
            buy_price_raw = st.text_input(f"🏷️ ราคาเหรียญตอนซื้อ ({currency_label}):", key=f"bp_{i}", placeholder="ราคาเข้าซื้อ")
            sell_price_raw = st.text_input(f"🎯 ราคาที่ต้องการตั้งขาย ({currency_label}):", key=f"sp_{i}", placeholder="เป้าหมายขาย")
            
        with inner_col_out:
            cash = parse_float_input(cash_raw) if parse_float_input(cash_raw) is not None else 0.0
            buy_price = parse_float_input(buy_price_raw) if parse_float_input(buy_price_raw) is not None else 0.0
            sell_price = parse_float_input(sell_price_raw) if parse_float_input(sell_price_raw) is not None else 0.0
            
            if coin_name != "เลือกเหรียญ..." and cash > 0 and buy_price > 0:
                buy_fee = cash * FEE_RATE
                net_buy = cash - buy_fee
                coins_received = net_buy / buy_price
                
                gross_sell = coins_received * sell_price
                sell_fee = gross_sell * FEE_RATE
                net_sell = gross_sell - sell_fee
                
                pnl_baht = net_sell - cash
                pnl_percent = (pnl_baht / cash) * 100 if cash > 0 else 0.0
                
                status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
                status_bg = "rgba(0, 255, 102, 0.02)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.02)"
                status_sign = "+" if pnl_baht >= 0 else ""
                
                st.html(f"""
                <div style='background: {status_bg}; padding: 15px; border-radius: 10px; border: 1px solid #1e2942; border-left: 5px solid {status_color}; margin-top: 5px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                        <span style='font-size: 14px; font-weight: bold; color: #ffffff;'>📊 NET SUMMARY ({coin_name})</span>
                        <span style='font-size: 16px; font-weight: 900; color: {status_color};'>
                            {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} {currency_label})
                        </span>
                    </div>
                    
                    <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1;">
                            <div style="font-size: 10px; color: #64748b; font-weight: 600;">🪙 ได้รับเหรียญสุทธิ</div>
                            <div style="font-size: 14px; font-weight: bold; color: #00E5FF; margin-top: 3px;">{format_smart_clean(coins_received)}</div>
                        </div>
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1;">
                            <div style="font-size: 10px; color: #64748b; font-weight: 600;">📈 เงินเข้าบัญชีสุทธิ</div>
                            <div style="font-size: 14px; font-weight: bold; color: #ffffff; margin-top: 3px;">{net_sell:,.2f} {currency_label}</div>
                        </div>
                        <div style="background: rgba(6, 9, 19, 0.7); padding: 10px; border-radius: 6px; border: 1px solid #1e2942; text-align: center; flex: 1; border-color: {status_color};">
                            <div style="font-size: 10px; color: {status_color}; font-weight: 600;">NET PROFIT / LOSS</div>
                            <div style="font-size: 14px; font-weight: bold; color: {status_color}; margin-top: 3px;">{status_sign}{pnl_baht:,.2f} {currency_label}</div>
                        </div>
                    </div>
                    
                    <table style='width:100%; color:#64748b; font-size:11px; border-collapse: collapse; margin-top: 5px;'>
                        <tr style='border-bottom: 1px solid rgba(30, 41, 66, 0.4);'>
                            <td style='padding: 3px 0;'>💵 ทุนซื้อ: {cash:,.2f} {currency_label} (หักฟีซื้อ: {buy_fee:,.2f} {currency_label})</td>
                            <td style='text-align: right; color:#ffffff;'>ราคาเข้า: {format_smart_clean(buy_price)} {currency_label}</td>
                        </tr>
                        <tr>
                            <td style='padding: 3px 0;'>🎯 ยอดขายรวม: {gross_sell:,.2f} {currency_label} (หักฟีขาย: {sell_fee:,.2f} {currency_label})</td>
                            <td style='text-align: right; color:#ffffff;'>ราคาขาย: {format_smart_clean(sell_price)} {currency_label}</td>
                        </tr>
                    </table>
                </div>
                """)
            else:
                st.html(f"""
                <div style='text-align: center; padding: 52px 15px; color: #475569; border: 1px dashed #1e2942; border-radius: 10px; font-size: 13px; background: rgba(6, 9, 19, 0.3); margin-top: 5px;'>
                    ⏳ [STANDBY] กรุณาเลือกเหรียญ และระบุเงินทุน + ราคาซื้อ เพื่อประมวลผลคำนวณเงินในระบบหน่วย {currency_label} ครับ
                </div>
                """)
                
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
