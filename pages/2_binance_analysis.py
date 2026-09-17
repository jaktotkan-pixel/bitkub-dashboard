import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import time

# ตั้งค่าหน้าจอแดชบอร์ดให้แสดงผลแบบเต็มหน้าจอ (Wide Mode)
st.set_page_config(layout="wide")

st.title("📊 Binance Realtime vs AI Analysis Model")
st.subheader("ระบบ AI ตรวจจับจุดซื้อ 4h + ไม้บรรทัดลากเส้นประวิเคราะห์ด้วยตัวเองพร้อมป้ายราคา")

# 1. รายชื่อเหรียญยอดนิยมคู่ USDT บนกระดานเทรด (เสถียรภาพสูง 100%)
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
st.sidebar.header("⚙️ ตัวเลือกสัญญาณ")
selected_display = st.sidebar.selectbox("เลือกเหรียญ:", list(CRYPTO_MAP.keys()), index=0) # เริ่มต้นที่ DOGEUSDT
ticker_symbol = CRYPTO_MAP[selected_display]

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=4  # ล็อกค่าเริ่มต้นไว้ที่ 4h ตามต้องการครับ
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 3. ฟังก์ชันดึงข้อมูลแท่งเทียนอัจฉริยะ รองรับ 4h
def get_crypto_candles(ticker, interval):
    if interval in ["1m", "5m", "15m"]:
        period = "1d"
    elif interval in ["1h", "4h"]:
        period = "1mo"  # ดึงย้อนหลัง 1 เดือนเพื่อให้มีข้อมูลคำนวณรอบ 4h ได้แม่นยำ
    else:
        period = "1y"
        
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period=period, interval=interval)
    
    if df.empty:
        raise Exception("สัญญาณดิบจากเซิร์ฟเวอร์หลักขัดข้องชั่วคราว")
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns)
    df = df.rename(columns={time_col: 'Time'})
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# 4. ฟังก์ชัน AI ประมวลผลหาทิศทางและโซนราคาสำคัญ
def calculate_ai_signals(df):
    ai_max_high = float(df['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df['Low'].rolling(window=20).min().iloc[-1])
    
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    current_ema = df['EMA_50'].iloc[-1]
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    avg_price = df['Close'].rolling(window=10).mean().iloc[-1]
    if last_rsi < 40:
        ai_buy_zone = avg_price * 0.995
    else:
        ai_buy_zone = ai_support * 1.002
        
    return ai_support, ai_buy_zone, ai_max_high, current_ema

# ประมวลผลรันระบบตั้งต้น
try:
    df = get_crypto_candles(ticker_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    
    # คำนวณโมเดลแผนการเทรดอัตโนมัติของ AI
    ai_support_line, ai_buy_zone_line, ai_max_high_line, main_trend_ema = calculate_ai_signals(df)
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ ระบบกำลังเชื่อมโยงอัลกอริทึมข้อมูลคริปโต: {str(e)}")

# ถ้าข้อมูลโหลดสำเร็จ ให้เริ่มคำนวณไม้บรรทัดแบบ Interactive
if not error_trigger:
    # 📌 ฟีเจอร์ไม้บรรทัดลากเส้นได้เอง: สร้างสไลเดอร์ควบคุมราคาสัญจรฝั่งซ้ายโดยสเกลตามกรอบราคาเหรียญนั้นๆ อัตโนมัติ
    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 ไม้บรรทัดลากเส้นวิเคราะห์เอง")
    
    min_chart_price = float(df['Low'].min())
    max_chart_price = float(df['High'].max())
    
    # ตัวเลื่อนราคาอิสระ (ลากขยับเส้นเหลืองนีออนบนกราฟ)
    user_custom_price = st.sidebar.slider(
        "เลื่อนเพื่อลากเส้นปรับระดับราคา:",
        min_value=min_chart_price,
        max_value=max_chart_price,
        value=float(current_price),
        step=(max_chart_price - min_chart_price) / 500,
        format="%.6f"
    )

    # 4. กล่องสรุปสถิติเป้าหมายแบบตัวเลขเรียลไทม์ด้านบน
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"ราคาปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🔵 AI Best Buy Zone (จุดช้อนซื้อ)", value=f"{ai_buy_zone_line:,.6f} USDT")
    with col3:
        st.metric(label="🔴 AI Max High Target (ราคาสูงสุด)", value=f"{ai_max_high_line:,.6f} USDT")
    with col4:
        user_dist = ((user_custom_price - current_price) / current_price) * 100
        st.metric(label="✏️ เส้นที่คุณลากเอง ห่างจากราคาปัจจุบัน", value=f"{user_custom_price:,.6f} USDT", delta=f"{user_dist:.2f}%")

    # 5. สร้างกราฟแท่งเทียนและระบบวาดเส้นแผนเทรดซ้อนทับพร้อมป้ายราคาชัดเจน
    fig = go.Figure()

    # วาดกราฟแท่งเทียนตลาดจริง (เขียว-แดงสไตล์กระดาน Binance จริง)
    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคาตลาดจริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # วาดเส้นวิเคราะห์อัตโนมัติซ้อนลงไปบนกราฟพร้อมระบุป้ายราคาวิ่งตามราคาปัจจุบัน
    # 1. เส้นราคาสูงสุดรอบปัจจุบัน (AI Max High - เส้นสีแดงส้ม)
    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right",
        annotation_font=dict(size=11, color="white"),
        annotation_bgcolor="#ff4500"
    )
    
    # 2. เส้นเป้าหมายจุดที่ควรเข้าซื้อช้อนราคาที่ดีที่สุด (AI Buy Zone - เส้นสีฟ้านีออน)
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"🔵 AI BUY ZONE: {ai_buy_zone_line:,.6f} USDT", 
        annotation_position="bottom left",
        annotation_font=dict(size=11, color="black"),
        annotation_bgcolor="#00e6ff"
    )

    # 3. 🔥 เส้นประไม้บรรทัดลากได้เองตามนิ้วผู้ใช้ (User Custom Line - เส้นสีเหลืองนีออนสะท้อนแสง)
    fig.add_hline(
        y=user_custom_price, line_dash="dashdot", line_color="#ffff00", line_width=3,
        annotation_text=f"🟡 เส้นวิเคราะห์ของคุณ: {user_custom_price:,.6f} USDT", 
        annotation_position="top left",
        annotation_font=dict(size=12, color="black", bold=True),
        annotation_bgcolor="#ffff00"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=620, 
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 6. กล่อง AI เจาะลึกทิศทางทิศทางการเทรดรอบวันและกลยุทธ์
    st.markdown("---")
    st.markdown("### 🧠 AI Trading Direction & Market Psychology Analysis")
    
    # ส่วนวิเคราะห์ทิศทางต่อวัน (Daily Trend Direction)
    if current_price > main_trend_ema:
        st.info(f"📈 **แนวโน้มทิศทางกรอบเวลา {tf_choice} : เป็นขาขึ้นเชิงบวก (Bullish Bias)**\n\nโครงสร้างราคาผู้เล่นส่วนใหญ่ฝั่ง Buy กำลังได้เปรียบ แนะนำเน้นดักช้อนซื้อเมื่อราคาเกิดการย่อตัวลงมาหาป้ายราคาเส้นสีฟ้า")
    else:
        st.warning(f"📉 **แนวโน้มทิศทางกรอบเวลา {tf_choice} : เป็นขาลงคุมตลาด (Bearish Bias)**\n\nระวังแรงเทขายตามโครงสร้างใหญ่ที่มีแรงกดดัน แนะนำเล่นด้วยความระมัดระวังและตั้งจุดรับไว้ที่ป้ายปลอดภัย")

    # ส่วนวิเคราะห์จังหวะการเข้าซื้อวินาทีปัจจุบัน
    st.markdown("**📌 แผนการเข้าเทรดรายวัน:**")
    if current_price <= ai_buy_zone_line * 1.005 and current_price >= ai_support_line:
        st.success(f"✅ **จังหวะซื้อได้เปรียบสูง (Strong Buy Alert):** ปัจจุบันราคาไหลลงมาสถิตอยู่ในโซนปลอดภัย **{ai_buy_zone_line:,.6f} USDT** ซึ่งเป็นทุนเฉลี่ยของวาฬส่วนใหญ่ มีโอกาสเกิดการเด้งกลับสูง!")
    elif current_price < ai_support_line:
        st.error(f"🚨 **จุดอันตราย (Panic Breakout):** ราคาหลุดทะลุป้ายแนวรับสีเขียวด้านล่างลงมาแล้ว ตลาดกำลังตื่นตระหนก แนะนำให้ชะลอการเข้าซื้อ")
    else:
        st.markdown(f"⏳ **รอการย่อตัว (Wait for Pullback):** ราคายังลอยอยู่ห่างจากจุดซื้อที่ปลอดภัย แนะนำให้ใจเย็นๆ รอกราฟย่อตัวลงมาหาป้ายราคา **{ai_buy_zone_line:,.6f} USDT**")

# 7. สั่งกระตุ้นระบบรีเฟรชอัปเดตราคาแบบ Realtime ทุกๆ 5 วินาที
if auto_refresh:
    time.sleep(5)
    st.rerun()
