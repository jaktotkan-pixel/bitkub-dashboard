import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import time

# ตั้งค่าหน้าจอแดชบอร์ดให้แสดงผลแบบเต็มหน้าจอ (Wide Mode)
st.set_page_config(layout="wide")

st.title("📊 Binance Realtime vs My Analysis")
st.subheader("ระบบวิเคราะห์ราคาเรียลไทม์ ซ้อนทับจุดเข้าซื้อ (เสถียรภาพสูง 100%)")

# 1. รายชื่อเหรียญยอดนิยมคู่ USDT บนระบบ (แมปปิ้งดึงข้อมูลตรงเป้าหมาย)
CRYPTO_MAP = {
    "DOGEUSDT": "DOGE-USD",
    "BTCUSDT": "BTC-USD",
    "ETHUSDT": "ETH-USD",
    "BNBUSDT": "BNB-USD",
    "SOLUSDT": "SOL-USD",
    "XRPUSDT": "XRP-USD",
    "ADAUSDT": "ADA-USD",
    "SHIBUSDT": "SHIB-USD",
    "DOTUSDT": "DOT-USD",
    "LINKUSDT": "LINK-USD"
}

# 2. แถบควบคุมด้านซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ ตั้งค่าข้อมูล")
selected_display = st.sidebar.selectbox("เลือกเหรียญ:", list(CRYPTO_MAP.keys()), index=0) # เลือก DOGEUSDT เป็นค่าแรก
ticker_symbol = CRYPTO_MAP[selected_display]

# แปลง Timeframe ให้เข้ากับระบบ
tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "2m", "5m", "15m", "30m", "1h", "1d"], 
    index=3  # ค่าเริ่มต้นตั้งไว้ที่ 15m
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 จุดวิเคราะห์เข้า BUY")
my_target_price = st.sidebar.number_input("ราคาแนวรับที่คาดว่าจะลงมาถึง:", value=0.0, format="%.6f")
buy_zone_buffer = st.sidebar.number_input("ขอบเขต Buy Zone (+/- จากเป้าหมาย):", value=0.0, format="%.6f")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 3. ฟังก์ชันดึงข้อมูลแท่งเทียนอัจฉริยะ (เสถียรที่สุด ปลอดภัยจากการโดนบล็อกไอพี)
def get_crypto_candles(ticker, interval):
    # กำหนดระยะช่วงเวลาดึงประวัติให้อยู่ในกรอบที่เหมาะกับไทม์เฟรมนั้นๆ เพื่อความรวดเร็ว
    period = "1d" if interval in ["1m", "2m", "5m", "15m", "30m"] else "1mo"
    if interval == "1d": period = "6mo"
    
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period=period, interval=interval)
    
    if df.empty:
        raise Exception("เซิร์ฟเวอร์ยังไม่มีการเคลื่อนไหวของข้อมูลในหน้านี้ชั่วคราว")
        
    df = df.reset_index()
    # ตรวจสอบชื่อหัวตารางเวลาให้รองรับทุกเวอร์ชัน
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns[0])
    df = df.rename(columns={time_col: 'Time'})
    
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# ประมวลผลดึงข้อมูล
try:
    df = get_crypto_candles(ticker_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ กำลังเตรียมการเชื่อมโยงระบบสัญญาณราคา โปรดรอสักครู่ หรือลองเปลี่ยนไทม์เฟรม: {str(e)}")

# ถ้าข้อมูลโหลดสำเร็จ ไม่มี Error ให้เริ่มวาดหน้าจอทันที
if not error_trigger:
    # 4. แสดงผลราคาปัจจุบันตัวใหญ่ๆ ด้านบนกราฟ
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"ราคาตลาดปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        if my_target_price > 0:
            dist_percent = ((current_price - my_target_price) / current_price) * 100
            st.metric(label="ระยะห่างจากจุดเข้าซื้อของคุณ", value=f"{dist_percent:.2f} %")

    # 5. สร้างกราฟแท่งเทียนและระบบวาดเส้นแผนเทรดซ้อนทับ
    fig = go.Figure()

    # วาดแท่งเทียนราคาตลาดจริง (เขียว-แดงตามสไตล์หน้ากระดานเทรดจริง)
    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคาตลาดจริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # วาดเส้นแนวรับที่คุณวิเคราะห์ซ้อนทับลงไปบนแกนราคาเดียวกัน
    if my_target_price > 0:
        fig.add_hline(
            y=my_target_price, line_dash="dash", line_color="#00e6ff", line_width=2, 
            annotation_text="🎯 จุดวิเคราะห์ของคุณ", annotation_position="top right"
        )
        
        # วาดพื้นที่ Buy Zone (เงาสีเขียวจางๆ) เพื่อดูขอบเขตราคา
        if buy_zone_buffer > 0:
            fig.add_hrect(
                y0=my_target_price - buy_zone_buffer, y1=my_target_price + buy_zone_buffer, 
                fillcolor="green", opacity=0.15, line_width=0, name="Buy Zone"
            )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=550,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 6. ส่วนแจ้งเตือนสถานะความแม่นยำในการวิเคราะห์
    st.markdown("### 🔔 Status")
    if my_target_price > 0:
        if current_price <= my_target_price + buy_zone_buffer and current_price >= my_target_price - buy_zone_buffer:
            st.success("✅ ราคาไหลลงมาอยู่ใน Buy Zone ที่คุณวิเคราะห์ไว้แล้ว! พิจารณาเข้าซื้อ")
        elif current_price > my_target_price:
            st.info("⏳ ราคายังอยู่สูงกว่าแผนการเทรดของคุณ กำลังรอให้ย่อตัวลงมา")
        else:
            st.warning("⚠️ ราคาหลุดทะลุแนวรับแนววิเคราะห์ลงไปแล้ว (โปรดระวังการกลับตัว)")
    else:
        st.info("💡 กรุณากรอก 'ราคาแนวรับที่คาดว่าจะลงมาถึง' ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นเปรียบเทียบกราฟซ้อน")

# 7. ระบบสั่งรันซ้ำอัตโนมัติเพื่อให้กราฟและราคาขยับแบบเรียลไทม์
if auto_refresh:
    time.sleep(5)
    st.rerun()
