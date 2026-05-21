import streamlit as st
import pandas as pd

st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

# ตั้งค่าหัวข้อแอป
st.markdown("<h1 style='text-align: center; color: #00FFCC;'>🧮 เครื่องคำนวณต้นทุนเฉลี่ย และจำลองกำไร (5 ไม้ละเอียด)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>คำนวณละเอียดรายไม้ หักลบค่าธรรมเนียมขาซื้อ-ขาขาย 0.25% แม่นยำตามจริง</p>", unsafe_allow_html=True)
st.write("---")

# กำหนดอัตราค่าธรรมเนียม Bitkub (0.25%)
FEE_RATE = 0.0025

# สร้าง Layout แยกฝั่งซ้าย (กรอกข้อมูลซื้อ) และ ฝั่งขวา (สรุปผลและจำลองราคาขาย)
col_input, col_result = st.columns([1, 1.2])

with col_input:
    st.subheader("📥 1. บันทึกรายการเข้าซื้อ (สูงสุด 5 ไม้)")
    st.caption("ไม้ไหนยังไม่ได้ซื้อ ให้ใส่จำนวนเงินทุนเป็น 0 บาท")
    
    # ไม้ที่ 1
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", min_value=0.0, value=2600.0, step=100.0, key="c1")
        # 🎯 ปรับราคาตอนซื้อให้กรอกและแสดงผลเป็น 8 ตำแหน่ง
        price_1 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", min_value=0.00000001, value=47.55000000, format="%.8f", step=0.00000001, key="p1")
    
    # ไม้ที่ 2
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c2")
        # 🎯 ปรับราคาตอนซื้อให้กรอกและแสดงผลเป็น 8 ตำแหน่ง
        price_2 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", min_value=0.00000001, value=45.00000000, format="%.8f", step=0.00000001, key="p2")
        
    # ไม้ที่ 3
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c3")
        # 🎯 ปรับราคาตอนซื้อให้กรอกและแสดงผลเป็น 8 ตำแหน่ง
        price_3 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", min_value=0.00000001, value=43.00000000, format="%.8f", step=0.00000001, key="p3")
        
    # ไม้ที่ 4
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c4")
        # 🎯 ปรับราคาตอนซื้อให้กรอกและแสดงผลเป็น 8 ตำแหน่ง
        price_4 = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", min_value=0.00000001, value=41.00000000, format="%.8f", step=0.00000001, key="p4")
        
    # ไม้ที่ 5
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c5")
        # 🎯 ปรับราคาตอนซื้อให้กรอกและแสดงผลเป็น 8 ตำแหน่ง
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
        
        # สะสมค่ารวมทั้งหมด
        total_invest_cash += item["input_cash"]
        total_buy_fee += fee
        total_coins += coins_received
        
        # 🎯 ปรับการแสดงผลราคาในตารางสรุปเป็น 8 ตำแหน่ง และคงจำนวนเหรียญที่ได้ไว้ 4 ตำแหน่ง
        rows.append({
            "ไม้ที่": f"ไม้ {item['ไม้ที่']}",
            "เงินทุนซื้อ (บาท)": f"{item['input_cash']:,.2f}",
            "ราคาตอนซื้อ": f"{item['buy_price']:,.8f}",
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{fee:,.2f}",
            "เหรียญที่ได้รับ": f"{coins_received:,.4f}"
        })

# --- ฝั่งขวา: แสดงผลการคำนวณสุทธิ ---
with col_result:
    st.subheader("📊 2. ตารางสรุปรายละเอียดฝั่งซื้อ")
    if len(rows) > 0:
        df = pd.DataFrame(rows)
        st.table(df)
        
        # คำนวณราคาเฉลี่ยสุทธิ
        avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0
        
        st.markdown("### 🎯 3. สรุปราคาสุดท้ายและต้นทุนเฉลี่ย")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div style='background-color:#1e293b; padding:15px; border-radius:8px; border:1px solid #334155; text-align:center;'>
                <div style='color:#94a3b8; font-size:13px;'>💰 เงินทุนรวมทั้งหมด</div>
                <div style='color:#ffffff; font-size:20px; font-weight:bold;'>{total_invest_cash:,.2f} บ.</div>
                <div style='color:#64748b; font-size:11px;'>รวมค่าฟีซื้อ {total_buy_fee:,.2f} บ.แล้ว</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div style='background-color:#1e293b; padding:15px; border-radius:8px; border:1px solid #334155; text-align:center;'>
                <div style='color:#94a3b8; font-size:13px;'>🪙 จำนวนเหรียญในมือ</div>
                <div style='color:#00E5FF; font-size:20px; font-weight:bold;'>{total_coins:,.4f}</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            # 🎯 ปรับกล่องสรุปต้นทุนเฉลี่ยสุดท้ายตรงกลางให้โชว์ 8 ตำแหน่ง
            st.markdown(f"""
            <div style='background-color:#0f172a; padding:15px; border-radius:8px; border:1px solid #00FFCC; text-align:center;'>
                <div style='color:#00FFCC; font-size:13px; font-weight:bold;'>🏷️ ต้นทุนเฉลี่ย/เหรียญ</div>
                <div style='color:#00FFCC; font-size:20px; font-weight:bold;'>{avg_cost_per_coin:,.8f} บ.</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        
        # โซนตั้งเป้าหมายราคาขายเพื่อดูผลกำไร
        st.subheader("🎯 4. จำลองเป้าหมายราคาตั้งขายเพื่อดูไรสุทธิ")
        
        # ให้ Slider เริ่มต้นที่ราคาเฉลี่ยปัจจุบัน เพื่อให้เลื่อนดูง่าย
        # 🎯 ปรับตัวเลื่อน (Slider) ให้ขยับทีละสเต็ปเล็กๆ และแสดงผลเป็น 8 ตำแหน่ง
        target_sell_price = st.slider(
            "เลื่อนปรับราคาเหรียญที่คุณตั้งใจจะกดขายจริง (บาท):",
            min_value=float(avg_cost_per_coin * 0.7),
            max_value=float(avg_cost_per_coin * 1.5),
            value=float(avg_cost_per_coin),
            format="%.8f",
            step=0.00000001
        )
        
        # คำนวณฝั่งขาย
        gross_sell_revenue = total_coins * target_sell_price
        sell_fee = gross_sell_revenue * FEE_RATE
        net_sell_revenue = gross_sell_revenue - sell_fee # เงินบาทสุดท้ายที่จะเข้าบัญชีจริง
        
        # คำนวณกำไร / ขาดทุน
        pnl_baht = net_sell_revenue - total_invest_cash
        pnl_percent = (pnl_baht / total_invest_cash) * 100
        
        # ปรับสีตามสถานะ กำไรเขียว / ขาดทุนแดง
        status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
        status_sign = "+" if pnl_baht >= 0 else ""
        
        # 🎯 ปรับหัวข้อสรุปการจำลองราคาตั้งขายให้แสดงเป็น 8 ตำแหน่ง
        st.markdown(f"""
        <div style='background-color:#161b22; padding:20px; border-radius:10px; border-left:6px solid {status_color}; margin-top:15px;'>
            <h4 style='color:white; margin-top:0px;'>📍 ผลลัพธ์จากการตั้งขายที่ราคา {target_sell_price:,.8f} บาท</h4>
            <table style='width:100%; color:white; font-size:15px;'>
                <tr>
                    <td style='padding:5px 0;'>💵 ยอดขายก่อนหักค่าฟี:</td>
                    <td style='text-align:right;'>{gross_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr>
                    <td style='padding:5px 0; color:#94a3b8;'>📉 หักค่าธรรมเนียมฝั่งขาย (0.25%):</td>
                    <td style='text-align:right; color:#FF3366;'>- {sell_fee:,.2f} บาท</td>
                </tr>
                <tr style='font-weight:bold; border-top:1px solid #334155;'>
                    <td style='padding:10px 0; color:#00E5FF;'>💰 เงินสุทธิที่จะได้รับรวม (หักฟีแล้ว):</td>
                    <td style='text-align:right; color:#00E5FF; font-size:18px;'>{net_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr style='font-weight:bold; font-size:18px;'>
                    <td style='padding:5px 0; color:{status_color};'>📈 สรุปกำไร/ขาดทุนสุทธิ:</td>
                    <td style='text-align:right; color:{status_color};'>
                        {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("💡 กรุณากรอกจำนวนเงินทุนใน 'ไม้ที่ 1' ฝั่งซ้ายมือ เพื่อเริ่มคำนวณครับ")
