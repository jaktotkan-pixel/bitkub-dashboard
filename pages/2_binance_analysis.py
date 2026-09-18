import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. ตั้งค่าหน้าจอ Streamlit Dashboard (Wide Mode)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Binance Realtime vs Daily AI Model",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Binance Realtime & Fixed Daily AI Model")
st.subheader("ระบบ AI ล็อกแนวรับ-จุดซื้อรายวัน (Daily Fixed Zone) + ไม้บรรทัดลากเส้นวิเคราะห์เอง")

# -----------------------------------------------------------------------------
# 2. รายชื่อเหรียญยอดนิยมคู่ USDT บน Binance
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 3. แถบควบคุมด้านซ้ายมือ (Sidebar)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ ตัวเลือกสัญญาณ")
selected_symbol = st.sidebar.selectbox("เลือกเหรียญ (Binance Pair):", CRYPTO_LIST, index=0)

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe แสดงกราฟ:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=4  # ค่าเริ่มต้น 4h
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# -----------------------------------------------------------------------------
# 4. ฟังก์ชันดึงข้อมูลแท่งเทียนจาก Binance API โดยตรง
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3)  # Cache ข้อมูลไว้ 3 วินาที เพื่อป้องกันการยิง API ถี่เกินไป
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
    
    df = pd.DataFrame(data, columns=[
        'Open_Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_Time', 'Quote_Asset_Volume', 'Number_of_Trades',
        'Taker_Buy_Base_Asset_Volume', 'Taker_Buy_Quote_Asset_Volume', 'Ignore'
    ])
    
    df['Time'] = pd.to_datetime(df['Open_Time'], unit='ms')
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        df[col] = df[col].astype(float)
        
    return df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

# -----------------------------------------------------------------------------
# 5. ฟังก์ชันคำนวณสัญญาณ AI แบบ "รายวัน" (Fixed Daily Zone)
# -----------------------------------------------------------------------------
def calculate_daily_fixed_signals(symbol):
    # ดึงข้อมูลกราฟ 1 วัน (1d) ย้อนหลัง 30 วันมาคำนวณเส้นหลัก
    df_daily = get_binance_klines(symbol, "1d", limit=30)
    
    # แนวต้านสูงสุด และแนวรับต่ำสุดในรอบ 20 วัน
    ai_max_high = float(df_daily['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df_daily['Low'].rolling(window=20).min().iloc[-1])
    
    # คำนวณ RSI รายวัน (Standard Wilder's Smoothing)
    delta = df_daily['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_daily_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    # ราคาเฉลี่ย 10 วันย้อนหลัง
    avg_daily_price = df_daily['Close'].rolling(window=10).mean().iloc[-1]
    
    # คำนวณจุดซื้อประจำวัน
    if last_daily_rsi < 40:
        ai_buy_zone = avg_daily_price * 0.995 
    else:
        ai_buy_zone = ai_support * 1.002
        
    return ai_support, ai_buy_zone, ai_max_high

# -----------------------------------------------------------------------------
# 6. บล็อกประมวลผลข้อมูล Real-time
# -----------------------------------------------------------------------------
try:
    # 6.1 ดึงข้อมูลตาม Timeframe ย่อยที่ผู้ใช้เลือกมาโชว์บนกราฟ
    df = get_binance_klines(selected_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    
    # 6.2 คำนวณเส้นเฉลี่ยระยะสั้น EMA50 สำหรับดูแนวโน้ม
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    main_trend_ema = df['EMA_50'].iloc[-1]
    
    # 6.3 ดึงค่าแนวรับ-แนวต้านรายวัน (Fixed Lines)
    ai_support_line, ai_buy_zone_line, ai_max_high_line = calculate_daily_fixed_signals(selected_symbol)
    
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ เกิดข้อผิดพลาดในการเชื่อมต่อข้อมูล: {str(e)}")

# -----------------------------------------------------------------------------
# 7. แสดงผลส่วนอินเทอร์เฟซ Dashboard
# -----------------------------------------------------------------------------
if not error_trigger:
    # 📐 ไม้บรรทัดลากเส้นปรับระดับราคาเองด้านซ้าย
    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 ไม้บรรทัดลากเส้นวิเคราะห์เอง")
    
    min_chart_price = float(df['Low'].min())
    max_chart_price = float(df['High'].max())
    
    # ล็อกค่าสไลเดอร์ไว้ใน session_state ไม่ให้เด้งกลับเมื่อหน้ารีเฟรช
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

    # 📊 การ์ดแสดงสถิติตัวเลขด้านบน
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"ราคาปัจจุบัน ({selected_symbol})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🔵 AI Best Buy Zone (รายวัน)", value=f"{ai_buy_zone_line:,.6f} USDT")
    with col3:
        st.metric(label="🔴 AI Max High Target (รายวัน)", value=f"{ai_max_high_line:,.6f} USDT")
    with col4:
        user_dist = ((user_custom_price - current_price) / current_price) * 100
        st.metric(label="✏️ เส้นวิเคราะห์ส่วนตัว", value=f"{user_custom_price:,.6f} USDT", delta=f"{user_dist:.2f}%")

    # 📈 สร้างกราฟแท่งเทียน Candlestick
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคา Binance จริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # 1. เส้น Max High รายวัน (สีแดงส้ม)
    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 DAILY MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right",
        annotation_font=dict(size=11, color="white"),
        annotation_bgcolor="#ff4500"
    )
    
    # 2. เส้นจุดช้อนซื้อรายวัน (สีฟ้านีออน - ล็อกค่านิ่งตลอดวัน)
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"🔵 DAILY BUY ZONE: {ai_buy_zone_line:,.6f} USDT", 
        annotation_position="bottom left",
        annotation_font=dict(size=11, color="black"),
        annotation_bgcolor="#00e6ff"
    )

    # 3. เส้นวิเคราะห์ลากเอง (สีเหลืองสะท้อนแสง)
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

    # 🧠 บทวิเคราะห์ AI
    st.markdown("---")
    st.markdown("### 🧠 AI Trading Direction & Market Psychology Analysis")
    
    if current_price > main_trend_ema:
        st.info(f"📈 **แนวโน้มทิศทางในระยะสั้น ({tf_choice}) : ขาขึ้น (Bullish Bias)**\n\nโครงสร้างราคาระยะสั้นได้เปรียบฝั่ง Buy แนะนำรอย่อตัวเข้าซื้อบริเวณจุดซื้อปลอดภัยรายวันเส้นสีฟ้า")
    else:
        st.warning(f"📉 **แนวโน้มทิศทางในระยะสั้น ({tf_choice}) : ขาลง (Bearish Bias)**\n\nระวังแรงเทขายสะสมตามโครงสร้างย่อย แนะนำเล่นด้วยความระมัดระวัง")

    st.markdown("**📌 แผนการเข้าเทรดประจำวัน:**")
    if current_price <= ai_buy_zone_line * 1.005 and current_price >= ai_support_line:
        st.success(f"✅ **จังหวะซื้อได้เปรียบสูง (Strong Buy Alert):** ปัจจุบันราคาลงมาถึงโซนซื้อปลอดภัยประจำวัน **{ai_buy_zone_line:,.6f} USDT** มีโอกาสเกิดการตั้งฐานเด้งกลับ!")
    elif current_price < ai_support_line:
        st.error(f"🚨 **จุดอันตราย (Panic Breakout):** ราคาหลุดแนวรับรายวันลงมาแล้ว ชะลอการเข้าซื้อและรอประเมินสถานการณ์")
    else:
        st.markdown(f"⏳ **รอการย่อตัว (Wait for Pullback):** ราคายังลอยอยู่สูง แนะนำให้ตั้งรับรอซื้อบริเวณ **{ai_buy_zone_line:,.6f} USDT**")

# -----------------------------------------------------------------------------
# 8. ลูปสั่งอัปเดตราคาแบบ Auto-Refresh
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
