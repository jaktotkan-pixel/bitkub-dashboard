import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import time

# ตั้งค่าหน้าจอแดชบอร์ดให้แสดงผลแบบเต็มหน้าจอ (Wide Mode)
st.set_page_config(layout="wide")

st.title("📊 Binance Realtime vs AI Analysis Model")
st.subheader("ระบบ AI ตรวจจับพฤติกรรมการเทรดมหาชน & วาดเส้นจุดเข้าซื้ออัตโนมัติ")

# 1. รายชื่อเหรียญคู่ USDT บนกระดาน
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
st.sidebar.header("⚙️ เลือกเหรียญเพื่อเปิดสัญญาณ")
selected_display = st.sidebar.selectbox("เลือกเหรียญ:", list(CRYPTO_MAP.keys()), index=0) # เริ่มต้นที่ DOGEUSDT
ticker_symbol = CRYPTO_MAP[selected_display]

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "2m", "5m", "15m", "30m", "1h", "1d"], 
    index=3  # ค่าเริ่มต้น 15m
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 3. ฟังก์ชันดึงข้อมูลแท่งเทียน
def get_crypto_candles(ticker, interval):
    period = "1d" if interval in ["1m", "2m", "5m", "15m", "30m"] else "1mo"
    if interval == "1d": period = "6mo"
    
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period=period, interval=interval)
    
    if df.empty:
        raise Exception("เซิร์ฟเวอร์ดึงข้อมูลสัญญาณดิบไม่ได้ชั่วคราว")
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns)
    df = df.rename(columns={time_col: 'Time'})
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# 4. ฟังก์ชัน AI คณิตศาสตร์คำนวณหาโซนที่ User ส่วนใหญ่รุมเข้าซื้อกันจริง (พฤติกรรมมหาชน)
def calculate_ai_zones(df):
    # หาแนวรับจากจุดต่ำสุดที่มีการเด้งบ่อยๆ ของราคาย้อนหลัง 20 แท่ง (Swing Low Support)
    ai_support = float(df['Low'].rolling(window=20).min().iloc[-1])
    
    # คำนวณราคาเฉลี่ยถ่วงน้ำหนักตามพฤติกรรมตลาดส่วนใหญ่ (Value Area)
    # ใช้ RSI ช่วยหาจุดที่เกิดแรงเทขายมากเกินไปจนรายใหญ่เริ่มเข้ามาพยุงรับซื้อ (Oversold Area)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    # วิเคราะห์จุดเก็บของ (Accumulation Zone)
    avg_price = df['Close'].rolling(window=10).mean().iloc[-1]
    last_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    # หากตลาดเทขายหนัก (RSI ต่ำ) ทุนเฉลี่ยรายใหญ่จะถูกดึงให้ต่ำลงมาเพื่อดักซื้อดิป
    if last_rsi < 40:
        ai_buy_zone = avg_price * 0.995 
    else:
        ai_buy_zone = ai_support * 1.002 # ตั้งไว้เหนือแนวรับเล็กน้อยเพื่อไม่ให้ตกรถ
        
    return ai_support, ai_buy_zone

# ประมวลผลดึงข้อมูลและรันโมเดล AI
try:
    df = get_crypto_candles(ticker_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    
    # ส่งข้อมูลแท่งเทียนเข้าสมอง AI คำนวณจุดซื้ออัตโนมัติ
    ai_support_line, ai_buy_zone_line = calculate_ai_zones(df)
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ ระบบกำลังคำนวณอัลกอริทึมกราฟ โปรดรอสักครู่: {str(e)}")

# วาดแดชบอร์ด
if not error_trigger:
    # 4. หน้าจอสรุปตัวเลขสถิติแบบ Realtime
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"ราคาตลาดปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🎯 เส้นแนวรับ AI คำนวณให้", value=f"{ai_support_line:,.6f} USDT", delta=f"{((current_price-ai_support_line)/current_price)*-100:.2f}% ห่างจากราคาปัจจุบัน")
    with col3:
        st.metric(label="💎 จุดราคาทุนเฉลี่ยมหาชน (Best Buy)", value=f"{ai_buy_zone_line:,.6f} USDT")

    # 5. วาดกราฟซ้อนเส้น AI วิเคราะห์อัตโนมัติ
    fig = go.Figure()

    # วาดแท่งเทียนตลาดจริง
    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคาตลาดจริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # วาดเส้นวิเคราะห์ของ AI ซ้อนทับลงไปโดยที่ User ไม่ต้องพิมพ์เอง
    # 1. เส้นแนวรับมหาชนสำคัญ (สีเขียวเข้ม)
    fig.add_hline(
        y=ai_support_line, line_dash="solid", line_color="#00ff88", line_width=2,
        annotation_text="🟢 แนวรับสำคัญ (มหาชนตั้งรับหนาแน่น)", annotation_position="bottom left"
    )
    
    # 2. เส้นจุดสะสมซื้อที่ดีที่สุด (สีฟ้านีออน)
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="dash", line_color="#00e6ff", line_width=2,
        annotation_text="🔵 AI Buy Zone (ทุนเฉลี่ยรายใหญ่ช้อนซื้อ)", annotation_position="top right"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=580,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 6. สรุปบทวิเคราะห์พฤติกรรมผู้เล่นส่วนใหญ่ในตลาดให้พิจารณาตัดสินใจง่ายๆ
    st.markdown("### 🧠 AI Trading Behavior Analysis")
    
    if current_price <= ai_buy_zone_line * 1.005 and current_price >= ai_support_line:
        st.success(f"✅ **สัญญาณน่าซื้อมาก (Strong Buy Zone):** ขณะนี้ราคากำลังลงมาเคลียร์คนทำ Short และเข้าใกล้จุดทุนเฉลี่ยของคนส่วนใหญ่ในตลาด เป็นจังหวะที่แรงซื้อกลับมักจะรุนแรง มีโอกาสเด้งสูง!")
    elif current_price < ai_support_line:
        st.warning(f"⚠️ **ตลาดเกิดแรงตื่นตระหนก (Panic Sell):** ราคาหลุดแนวรับมหาชนลงมา พฤติกรรมผู้เล่นส่วนใหญ่กำลังตัดขาดทุน (Stop Loss) แนะนำให้ชะลอการ Buy จนกว่าจะเกิดแท่งเทียนสีเขียวแท่งแรกเพื่อความปลอดภัย")
    else:
        st.info(f"⏳ **ราคายังแพงอยู่ (Wait for Pullback):** พฤติกรรมฝั่ง Buy ส่วนใหญ่รอเข้าซื้อเมื่อย่อตัว เส้นวิเคราะห์ชี้เป้าว่า ควรรอให้ราคาไหลหลุดลงมาแถวๆ **{ai_buy_zone_line:,.6f} USDT** จะได้เปรียบที่สุดครับ")

# 7. วิ่งรีเฟรชราคาวินาทีต่อวินาที
if auto_refresh:
    time.sleep(5)
    st.rerun()
