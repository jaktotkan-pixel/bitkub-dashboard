import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

# 1. ตั้งค่าหน้าจอแดชบอร์ด
st.set_page_config(
    page_title="Binance Realtime AI Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Binance Realtime Market & AI Analysis")
st.subheader("ดึงข้อมูลตรงจาก Binance API แบบ Real-time (ไม่ผ่าน yfinance)")

# 2. รายชื่อเหรียญยอดนิยมคู่ USDT บน Binance (ใช้ Symbol ตรงของ Binance)
CRYPTO_LIST = [
    "DOGEUSDT",
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "SHIBUSDT",
    "DOTUSDT",
    "LINKUSDT"
]

# 3. แถบควบคุมด้านซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ ตัวเลือกสัญญาณ")
selected_symbol = st.sidebar.selectbox("เลือกเหรียญ (Binance Pair):", CRYPTO_LIST, index=0)

# Binance API รองรับ timeframe เหล่านี้โดยตรง: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=4  # ล็อกไว้ที่ 4h เป็นค่าเริ่มต้น
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 4. ฟังก์ชันดึงข้อมูลแท่งเทียนจาก Binance API โดยตรง (Public REST API)
@st.cache_data(ttl=3) # Cache ข้อมูลไว้ 3 วินาที ป้องกันการยิง API ซ้ำซ้อน
def get_binance_klines(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    response = requests.get(url, params=params, timeout=5)
    
    if response.status_code != 200:
        raise Exception(f"Binance API Error: {response.status_code} - {response.text}")
        
    data = response.json()
    
    # Binance klines Format:
    # [ Open time, Open, High, Low, Close, Volume, Close time, ... ]
    df = pd.DataFrame(data, columns=[
        'Open_Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_Time', 'Quote_Asset_Volume', 'Number_of_Trades',
        'Taker_Buy_Base_Asset_Volume', 'Taker_Buy_Quote_Asset_Volume', 'Ignore'
    ])
    
    # แปลงชนิดข้อมูลตัวเลขและเวลา
    df['Time'] = pd.to_datetime(df['Open_Time'], unit='ms')
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = df[col].astype(float)
        
    return df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

# 5. ฟังก์ชันคำนวณ AI Indicator Signals
def calculate_ai_signals(df):
    ai_max_high = float(df['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df['Low'].rolling(window=20).min().iloc[-1])
    
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    current_ema = df['EMA_50'].iloc[-1]
    
    # คำนวณ RSI แบบมาตรฐาน (Wilder's Exponential Moving Average)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    avg_price = df['Close'].rolling(window=10).mean().iloc[-1]
    if last_rsi < 40:
        ai_buy_zone = avg_price * 0.995
    else:
        ai_buy_zone = ai_support * 1.002
        
    return ai_support, ai_buy_zone, ai_max_high, current_ema

# ประมวลผลรันระบบ
try:
    df = get_binance_klines(selected_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    ai_support_line, ai_buy_zone_line, ai_max_high_line, main_trend_ema = calculate_ai_signals(df)
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อกับ Binance API: {str(e)}")

if not error_trigger:
    # 📌 ไม้บรรทัดสไลเดอร์
    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 ไม้บรรทัดลากเส้นวิเคราะห์เอง")
    
    min_chart_price = float(df['Low'].min())
    max_chart_price = float(df['High'].max())
    
    # ใช้ session_state เพื่อจำค่าตำแหน่งเส้นที่คุณลากไว้ ไม่ให้โดนรีเซ็ตเมื่อหน้ารีเฟรช
    if "user_price" not in st.session_state:
        st.session_state.user_price = float(current_price)

    user_custom_price = st.sidebar.slider(
        "เลื่อนเพื่อลากเส้นปรับระดับราคา:",
        min_value=min_chart_price,
        max_value=max_chart_price,
        value=st.session_state.user_price,
        step=(max_chart_price - min_chart_price) / 500,
        format="%.6f"
    )
    st.session_state.user_price = user_custom_price

    # 6. กล่องสรุปสถิติราคา Real-time ด้านบน
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"ราคาปัจจุบัน ({selected_symbol})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🔵 AI Best Buy Zone", value=f"{ai_buy_zone_line:,.6f} USDT")
    with col3:
        st.metric(label="🔴 AI Max High Target", value=f"{ai_max_high_line:,.6f} USDT")
    with col4:
        user_dist = ((user_custom_price - current_price) / current_price) * 100
        st.metric(label="✏️ เส้นวิเคราะห์ส่วนตัว", value=f"{user_custom_price:,.6f} USDT", delta=f"{user_dist:.2f}%")

    # 7. สร้างกราฟ Plotly แสดงแท่งเทียน Real-time
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคา Binance จริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # เส้น Max High Target
    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right",
        annotation_font=dict(size=11, color="white"),
        annotation_bgcolor="#ff4500"
    )
    
    # เส้น AI Buy Zone
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"🔵 AI BUY ZONE: {ai_buy_zone_line:,.6f} USDT", 
        annotation_position="bottom left",
        annotation_font=dict(size=11, color="black"),
        annotation_bgcolor="#00e6ff"
    )

    # เส้นวิเคราะห์ลากเอง
    fig.add_hline(
        y=user_custom_price, line_dash="dashdot", line_color="#ffff00", line_width=3,
        annotation_text=f"🟡 เส้นวิเคราะห์ของคุณ: {user_custom_price:,.6f} USDT", 
        annotation_position="top left",
        annotation_font=dict(size=12, color="black"),
        annotation_bgcolor="#ffff00"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=620, 
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 8. บทวิเคราะห์ AI
    st.markdown("---")
    st.markdown("### 🧠 AI Trading Direction & Market Psychology Analysis")
    
    if current_price > main_trend_ema:
        st.info(f"📈 **แนวโน้มทิศทางกรอบเวลา {tf_choice} : เป็นขาขึ้นเชิงบวก (Bullish Bias)**\n\nโครงสร้างราคาฝั่ง Buy กำลังได้เปรียบ แนะนำเน้นดักช้อนซื้อเมื่อราคาเกิดการย่อตัวลงมาหาป้ายราคาเส้นสีฟ้า")
    else:
        st.warning(f"📉 **แนวโน้มทิศทางกรอบเวลา {tf_choice} : เป็นขาลงคุมตลาด (Bearish Bias)**\n\nระวังแรงเทขายสะสมตามโครงสร้างใหญ่ที่มีแรงกดดัน แนะนำเล่นด้วยความระมัดระวังและตั้งจุดรับไว้ที่ป้ายปลอดภัย")

    st.markdown("**📌 แผนการเข้าเทรดรายวัน:**")
    if current_price <= ai_buy_zone_line * 1.005 and current_price >= ai_support_line:
        st.success(f"✅ **จังหวะซื้อได้เปรียบสูง (Strong Buy Alert):** ปัจจุบันราคาไหลลงมาสถิตอยู่ในโซนปลอดภัย **{ai_buy_zone_line:,.6f} USDT** มีโอกาสเกิดการเด้งกลับสูง!")
    elif current_price < ai_support_line:
        st.error(f"🚨 **จุดอันตราย (Panic Breakout):** ราคาหลุดทะลุป้ายแนวรับด้านล่างลงมาแล้ว ตลาดกำลังตื่นตระหนก แนะนำให้ชะลอการเข้าซื้อ")
    else:
        st.markdown(f"⏳ **รอการย่อตัว (Wait for Pullback):** ราคายังลอยอยู่ห่างจากจุดซื้อที่ปลอดภัย แนะนำให้ใจเย็นๆ รอกราฟย่อตัวลงมาหาป้ายราคา **{ai_buy_zone_line:,.6f} USDT**")

# 9. ลูปอัปเดตอัตโนมัติ Realtime
if auto_refresh:
    time.sleep(5)
    st.rerun()
