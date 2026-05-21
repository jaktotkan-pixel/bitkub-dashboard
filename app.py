import streamlit as st
import requests
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

# --- 1. ตั้งค่าโครงสร้างหน้าจอและ CSS ---
st.set_page_config(page_title="Bitkub Smart Multi-Tier Analyzer", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1a1e2e; color: white; }
.metric-container {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #334155;
    text-align: center;
}
.metric-lbl { font-size: 13px; color: #94a3b8; margin-bottom: 5px; }
.metric-val { font-size: 22px; font-weight: bold; color: white; }
</style>
""", unsafe_allow_html=True)

# อัตราค่าธรรมเนียมมาตรฐาน Bitkub (0.25%)
FEE_RATE = 0.0025

# ฟังก์ชันดึงราคาสดจริงจาก API Bitkub
def get_bitkub_price(coin_ticker):
    url = "https://api.bitkub.com/api/market/ticker"
    pair = f"THB_{coin_ticker}"
    try:
        response = requests.get(url).json()
        if pair in response:
            return response[pair]['last']
    except:
        pass
    return 0.0

# ฟังก์ชันจำลองเส้นกราฟ 24 ชม. ให้สอดคล้องกับฐานราคาปัจจุบัน
def generate_current_24h_data(base_price):
    history = []
    now = datetime.now()
    current = base_price if base_price > 0 else 18.50
    for i in range(24):
        change = current * random.uniform(-0.012, 0.012)
        current = current + change
        t_stamp = now - timedelta(hours=(24 - i))
        history.append({"timestamp": t_stamp, "price": current})
    return history

# --- 2. ระบบ Auto-Refresh หน้าเว็บทุกๆ 5 วินาที ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()

# --- 3. แถบเมนูด้านซ้าย (Sidebar) สำหรับเลือกเหรียญและกรอกข้อมูล 5 ไม้ ---
st.sidebar.header("🪙 เลือกสินทรัพย์")
# 🎯 ปรับเอา XRP ขึ้นมาเป็นอันดับ 1 เพื่อเป็นค่าเริ่มต้นตอนเปิดแอป
supported_coins = ["XRP", "ZEREBRO", "KUB", "BTC", "ETH", "USDT", "SOL", "ADA"]

if "current_coin" not in st.session_state:
    st.session_state.current_coin = supported_coins[0]

try:
    current_idx = supported_coins.index(st.session_state.current_coin)
except ValueError:
    current_idx = 0

selected_coin = st.sidebar.selectbox("เหรียญที่ต้องการตรวจสอบ (Ticker):", supported_coins, index=current_idx)

# บล็อกล้างข้อมูลข้ามเหรียญ
if st.session_state.current_coin != selected_coin:
    st.session_state.current_coin = selected_coin
    if "raw_history" in st.session_state:
        del st.session_state["raw_history"]
    st.rerun()

# ดึงราคาตลาดอัปเดตสดใหม่หน้าเว็บทุก 5 วินาที
current_price = get_bitkub_price(selected_coin)

# แสดงผลราคาวิ่งล่าสุดด้านซ้ายเป็น 8 ตำแหน่งรองรับทุกเหรียญ
st.sidebar.markdown(f"""
<div style='background-color:#0f172a; padding:10px; border-radius:6px; border: 1px solid #00FFCC; text-align:center; margin-top:5px; margin-bottom:15px;'>
    <span style='color:#cbd5e1; font-size:13px;'>⚡ ราคา {selected_coin} วิ่งล่าสุดบนเว็บ</span><br>
    <b style='color:#00FFCC; font-size:20px;'>{current_price:,.8f} <span style='font-size:12px; color:#cbd5e1;'>THB</span></b>
</div>
""", unsafe_allow_html=True)

# กล่องกรอกข้อมูล 5 ไม้ฝั่งซ้ายละเอียด
st.sidebar.subheader("🔢 บันทึกรายการเข้าซื้อละเอียด [1-5]")
st.sidebar.caption("ไม้ไหนยังไม่ได้ซื้อ ให้คงมูลค่าเงินทุนไว้ที่ 0 บาท")

def render_tier_input(tier_num, default_cash, default_buy_price):
    with st.sidebar.expander(f"🪵 รายละเอียด ไม้ที่ {tier_num}", expanded=(tier_num == 1)):
        cash = st.number_input(f"เงินทุนที่ใช้ซื้อ ไม้ {tier_num} (บาท)", value=default_cash, step=100.0, key=f"c_{tier_num}")
        buy_price = st.number_input(f"ราคาเหรียญตอนกดซื้อ ไม้ {tier_num}", value=float(default_buy_price), format="%.8f", step=0.00000001, key=f"p_{tier_num}")
    return cash, buy_price

default_init_p = current_price if current_price > 0 else 18.50
c1, p1 = render_tier_input(1, 2600.0, default_init_p)
c2, p2 = render_tier_input(2, 0.0, default_init_p * 0.95)
c3, p3 = render_tier_input(3, 0.0, default_init_p * 0.90)
c4, p4 = render_tier_input(4, 0.0, default_init_p * 0.85)
c5, p5 = render_tier_input(5, 0.0, default_init_p * 0.80)

# ประมวลผลและคำนวณหักค่าธรรมเนียมฝั่งขาซื้อรายไม้
tier_inputs = [
    {"num": 1, "cash": c1, "price": p1},
    {"num": 2, "cash": c2, "price": p2},
    {"num": 3, "cash": c3, "price": p3},
    {"num": 4, "cash": c4, "price": p4},
    {"num": 5, "cash": c5, "price": p5},
]

rows_summary = []
total_invested_cash = 0.0
total_coins_held = 0.0
total_buy_fee_paid = 0.0

for t in tier_inputs:
    if t["cash"] > 0 and t["price"] > 0:
        buy_fee = t["cash"] * FEE_RATE
        net_buy_cash = t["cash"] - buy_fee
        coins_received = net_buy_cash / t["price"]
        
        total_invested_cash += t["cash"]
        total_buy_fee_paid += buy_fee
        total_coins_held += coins_received
        
        rows_summary.append({
            "ไม้": f"ไม้ {t['num']}",
            "เงินทุนรวมภาษีฟี (บาท)": f"{t['cash']:,.2f}",
            "ราคาตอนซื้อ": f"{t['price']:,.8f}",
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{buy_fee:,.2f}",
            "เหรียญที่ได้รับสุทธิ": f"{coins_received:,.4f}"
        })

# คำนวณราคาเฉลี่ยกลางหลังหักฟีซื้อ
avg_cost_per_coin = total_invested_cash / total_coins_held if total_coins_held > 0 else 0.0

# --- 4. การจัดการข้อมูลกราฟ ---
if "raw_history" not in st.session_state or not st.session_state.raw_history:
    st.session_state.raw_history = generate_current_24h_data(current_price)

now_dt = datetime.now()
st.session_state.raw_history = [item for item in st.session_state.raw_history if item["timestamp"] >= (now_dt - timedelta(hours=24))]

if len(st.session_state.raw_history) > 0:
    last_stored_time = st.session_state.raw_history[-1]["timestamp"]
    if now_dt - last_stored_time >= timedelta(hours=1):
        st.session_state.raw_history.append({"timestamp": now_dt, "price": current_price})
    else:
        st.session_state.raw_history[-1]["price"] = current_price
        st.session_state.raw_history[-1]["timestamp"] = now_dt

time_labels = [item["timestamp"].strftime("%H:%M") for item in st.session_state.raw_history]
prices_list = [item["price"] for item in st.session_state.raw_history]

# เว้นช่องแกนขวาสำหรับอนาคต 1 ชั่วโมง
future_dt = now_dt + timedelta(hours=1)
time_labels.append(future_dt.strftime("%H:%M"))
prices_list.append(None)

# --- 5. ส่วนแสดงผลหลักตรงกลาง ---
st.markdown(f"<h2 style='color: white;'>📊 แดชบอร์ดสรุปวิเคราะห์ต้นทุนเฉลี่ยและกำไร {selected_coin}</h2>", unsafe_allow_html=True)

if total_invested_cash > 0:
    # คำนวณสถานะพอร์ตกับราคาปัจจุบันบนเว็บ
    net_val_now = total_coins_held * current_price
    pnl_now_baht = net_val_now - total_invested_cash
    pnl_now_pct = (pnl_now_baht / total_invested_cash) * 100
    
    now_color = "#FF3366" if pnl_now_baht < 0 else "#00FF66"
    now_text = f"📉 ขณะนี้พอร์ตคุณดอยอยู่: {pnl_now_pct:,.2f}% ({pnl_now_baht:,.2f} บาท)" if pnl_now_baht < 0 else f"🔥 ขณะนี้พอร์ตคุณกำไรอยู่: +{pnl_now_pct:,.2f}% (+{pnl_now_baht:,.2f} บาท)"
    
    st.markdown(f"""
    <div style='background-color:#1e293b; padding:12px 20px; border-radius:8px; border-left: 6px solid {now_color}; margin-bottom:20px;'>
        <b style='color:{now_color}; font-size:16px;'>{now_text} (อิงจากราคาล่าสุดบนกระดานเทรด)</b>
    </div>
    """, unsafe_allow_html=True)
    
    # แสดงตารางแจกแจงรายไม้
    st.markdown("### 📋 ตารางแจกแจงบัญชีฝั่งซื้อแยกรายไม้")
    st.table(pd.DataFrame(rows_summary))
    
    # การคำนวณราคาสุดท้ายทั้งหมด
    st.markdown("### 🏷️ สรุปต้นทุนราคาสุดท้ายสุทธิ")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>💵 เงินทุนรวมที่จ่ายไปทั้งหมด</div><div class='metric-val'>{total_invested_cash:,.2f} <span style='font-size:12px; color:#94a3b8;'>บ.</span></div><div style='color:#64748b; font-size:11px;'>รวมค่าธรรมเนียมซื้อ {total_buy_fee_paid:,.2f} บ. แล้ว</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-container'><div class='metric-lbl'>🪙 จำนวนเหรียญในมือก้อนสุดท้าย</div><div class='metric-val' style='color:#00E5FF;'>{total_coins_held:,.4f}</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-container' style='border: 1px solid #00FFCC;'><div class='metric-lbl' style='color:#00FFCC; font-weight:bold;'>🎯 ราคาต้นทุนเฉลี่ยสุทธิ / เหรียญ</div><div class='metric-val' style='color:#00FFCC;'>{avg_cost_per_coin:,.8f} <span style='font-size:12px; color:#00FFCC;'>บ.</span></div></div>", unsafe_allow_html=True)
        
    st.write("---")
    
    # 🎯 กล่องจำลองราคาตั้งขายเพื่อหากำไรสุทธิหักค่าธรรมเนียมแล้ว
    st.markdown("### 🎯 ช่องจำลองเป้าหมายราคาขายสุทธิ (หักลบค่าธรรมเนียมขาขายออกแล้ว)")
    sell_target_price = st.slider("เลื่อนปรับระดับราคาเหรียญที่พี่ต้องการจะตั้งขายจริงในตลาด (บาท):", 
                                  min_value=float(avg_cost_per_coin * 0.4), max_value=float(avg_cost_per_coin * 2.0), value=float(avg_cost_per_coin), format="%.8f", step=0.00000001)
    
    # สูตรคำนวณหักฟีฝั่งขาขายออก 0.25%
    gross_sell_amount = total_coins_held * sell_target_price
    sell_fee_deduct = gross_sell_amount * FEE_RATE
    net_sell_cash_received = gross_sell_amount - sell_fee_deduct
    
    sim_pnl_baht = net_sell_cash_received - total_invested_cash
    sim_pnl_pct = (sim_pnl_baht / total_invested_cash) * 100
    
    sim_color = "#00FF66" if sim_pnl_baht >= 0 else "#FF3366"
    sim_sign = "+" if sim_pnl_baht >= 0 else ""
    
    st.markdown(f"""
    <div style='background-color:#161b22; padding:20px; border-radius:10px; border-left:6px solid {sim_color};'>
        <h4 style='color:white; margin-top:0px;'>📍 สรุปตัวเลขผลลัพธ์สุทธิจากการขายที่เป้าหมาย {sell_target_price:,.8f} บาท</h4>
        <table style='width:100%; color:white; font-size:15px;'>
            <tr>
                <td style='padding:5px 0;'>💵 ยอดเงินรวมก่อนหักค่าธรรมเนียม:</td>
                <td style='text-align:right;'>{gross_sell_amount:,.2f} บาท</td>
            </tr>
            <tr>
                <td style='padding:5px 0; color:#94a3b8;'>📉 หักค่าธรรมเนียมขาขายออก (0.25%):</td>
                <td style='text-align:right; color:#FF3366;'>- {sell_fee_deduct:,.2f} บาท</td>
            </tr>
            <tr style='font-weight:bold; border-top:1px solid #334155;'>
                <td style='padding:10px 0; color:#00E5FF;'>💰 ยอดเงินบาทสุดท้ายสุทธิที่จะได้รับรวม (เข้าธนาคาร):</td>
                <td style='text-align:right; color:#00E5FF; font-size:18px;'>{net_sell_cash_received:,.2f} บาท</td>
            </tr>
            <tr style='font-weight:bold; font-size:18px;'>
                <td style='padding:5px 0; color:{sim_color};'>📈 คิดเป็นกำไร / ขาดทุนสุทธิ:</td>
                <td style='text-align:right; color:{sim_color};'>
                    {sim_sign}{sim_pnl_pct:,.2f}% ({sim_sign}{sim_pnl_baht:,.2f} บาท)
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # --- 6. ส่วนวิเคราะห์กราฟ Timeline 24h ---
    st.markdown("<br>### 📈 กราฟความเคลื่อนไหวราคา Timeline (ย้อนหลัง 24 ชม.)", unsafe_allow_html=True)
    selected_tf = st.select_slider("เลื่อนปรับกรอบกรอบเส้นแนวต้าน/แนวรับความผันผวน (Timeframe):", options=["1m", "5m", "15m", "1h", "4h", "1D"], value="1h")
    tf_mods = {
        "1m": {"up": 1.004, "down": 0.996}, "5m": {"up": 1.012, "down": 0.988},
        "15m": {"up": 1.025, "down": 0.975}, "1h": {"up": 1.050, "down": 0.950},
        "4h": {"up": 1.090, "down": 0.910}, "1D": {"up": 1.180, "down": 0.820}
    }
    mods = tf_mods[selected_tf]
    upper_lines = [(p * mods["up"]) if p is not None else None for p in prices_list]
    lower_lines = [(p * mods["down"]) if p is not None else None for p in prices_list]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_labels, y=upper_lines, mode='lines', name='🛑 แนวต้าน ขา S (เส้นประ)', line=dict(color='#FF3366', width=2, dash='dash'), connectgaps=False))
    fig.add_trace(go.Scatter(x=time_labels, y=prices_list, mode='lines+markers', name=f'⚡ ราคาปัจจุบัน {selected_coin}', line=dict(color='#00FFCC', width=2.5, dash='dot'), marker=dict(size=4, color='#00FFCC'), connectgaps=False))
    fig.add_trace(go.Scatter(x=time_labels, y=lower_lines, mode='lines', name='🟢 แนวรับ ขา B (เส้นประ)', line=dict(color='#00FF66', width=2, dash='dash'), connectgaps=False))

    fig.update_layout(
        template="plotly_dark", paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
        margin=dict(l=10, r=10, t=10, b=30), height=300, hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#21262d', zeroline=False, nticks=12),
        yaxis=dict(showgrid=True, gridcolor='#21262d', zeroline=False)
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("💡 รันหน้าแดชบอร์ดสำเร็จ! เริ่มต้นใช้งานโดยกรอกจำนวนเงินและราคาต้นทุนในแถบ 'ไม้ที่ 1' ฝั่งซ้ายมือได้เลยครับ")

time.sleep(0.1)
