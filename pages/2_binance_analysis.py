import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. ตั้งค่าหน้าจอ Streamlit Dashboard (Wide Mode)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Binance Multi-Crypto AI Buy Zone Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Binance Realtime & Multi-Crypto Daily AI Model")
st.subheader("แดชบอร์ดสรุปจุดซื้อ AI Buy Zone ของเหรียญยอดนิยม + กราฟวิเคราะห์เจาะลึก")

# -----------------------------------------------------------------------------
# 2. รายชื่อเหรียญยอดนิยมคู่ USDT บน Binance (10 เหรียญ)
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
selected_symbol = st.sidebar.selectbox("เลือกเหรียญเจาะลึกบนกราฟ:", CRYPTO_LIST, index=0)

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe กราฟเจาะลึก:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=4
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# -----------------------------------------------------------------------------
# 4. ฟังก์ชันดึงข้อมูลแท่งเทียนจาก Binance API
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3)
def get_binance_klines(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params, timeout=5)
    
    if response.status_code != 200:
        raise Exception(f"Binance API Error [{symbol}]: {response.status_code}")
        
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
# 5. ฟังก์ชันคำนวณสัญญาณ AI รายวัน (Fixed Daily Zone)
# -----------------------------------------------------------------------------
def calculate_daily_fixed_signals(symbol):
    df_daily = get_binance_klines(symbol, "1d", limit=30)
    
    ai_max_high = float(df_daily['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df_daily['Low'].rolling(window=20).min().iloc[-1])
    current_price = float(df_daily['Close'].iloc[-1])
    
    # คำนวณ RSI รายวัน
    delta = df_daily['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_daily_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    avg_daily_price = df_daily['Close'].rolling(window=10).mean().iloc[-1]
    
    if last_daily_rsi < 40:
        ai_buy_zone = avg_daily_price * 0.995 
    else:
        ai_buy_zone = ai_support * 1.002
        
    return ai_support, ai_buy_zone, ai_max_high, current_price

# -----------------------------------------------------------------------------
# 6. ฟังก์ชันสร้างตารางสรุป 10 เหรียญแบบ Batch Processing
# -----------------------------------------------------------------------------
def get_all_crypto_summary(symbol_list):
    summary_data = []
    for sym in symbol_list:
        try:
            sup, buy_zone, max_high, price = calculate_daily_fixed_signals(sym)
            dist_pct = ((price - buy_zone) / buy_zone) * 100
            
            # กำหนดสถานะสัญญาณ
            if price <= buy_zone * 1.005 and price >= sup:
                status = "✅ Strong Buy Zone"
            elif price < sup:
                status = "🚨 Panic Breakout"
            elif dist_pct <= 3.0:
                status = "👀 Near Buy Zone"
            else:
                status = "⏳ Waiting"
                
            summary_data.append({
                "เหรียญ": sym,
                "ราคาปัจจุบัน (USDT)": f"{price:,.6f}",
                "AI Buy Zone (USDT)": f"{buy_zone:,.6f}",
                "Max High Target (USDT)": f"{max_high:,.6f}",
                "ห่างจากจุดซื้อ (%)": f"{dist_pct:+.2f}%",
                "สถานะสัญญาณ": status
            })
        except Exception:
            summary_data.append({
                "เหรียญ": sym,
                "ราคาปัจจุบัน (USDT)": "Error",
                "AI Buy Zone (USDT)": "-",
                "Max High Target (USDT)": "-",
                "ห่างจากจุดซื้อ (%)": "-",
                "สถานะสัญญาณ": "⚠️ Connection Fail"
            })
    return pd.DataFrame(summary_data)

# -----------------------------------------------------------------------------
# 7. ส่วนแสดงผลตารางสรุป 10 เหรียญด้านบนสุด
# -----------------------------------------------------------------------------
st.markdown("### 📋 ตารางสรุปจุดซื้อ AI Buy Zone ของทุกเหรียญ (ประจำวัน)")

with st.spinner("กำลังอัปเดตข้อมูลราคาทุกเหรียญแบบ Real-time..."):
    df_summary = get_all_crypto_summary(CRYPTO_LIST)
    
st.dataframe(
    df_summary,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. ส่วนแสดงผลกราฟและเจาะลึกรายเหรียญ (Selected Symbol)
# -----------------------------------------------------------------------------
st.markdown(f"### 📈 เจาะลึกกราฟ & สัญญาณเทรด: **{selected_symbol}**")

try:
    df_chart = get_binance_klines(selected_symbol, tf_choice)
    current_price = df_chart['Close'].iloc[-1]
    
    df_chart['EMA_50'] = df_chart['Close'].ewm(span=50, adjust=False).mean()
    main_trend_ema = df_chart['EMA_50'].iloc[-1]
    
    ai_support_line, ai_buy_zone_line, ai_max_high_line, _ = calculate_daily_fixed_signals(selected_symbol)
    
    # ไม้บรรทัดลากเส้นส่วนตัว Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 ไม้บรรทัดลากเส้นวิเคราะห์เอง")
    min_chart_price = float(df_chart['Low'].min())
    max_chart_price = float(df_chart['High'].max())
    
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

    # Metric Cards
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

    # Plotly Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_chart['Time'], open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'],
        name='ราคา Binance', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 DAILY MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right", annotation_font=dict(size=11, color="white"), annotation_bgcolor="#ff4500"
    )
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"🔵 DAILY BUY ZONE: {ai_buy_zone_line:,.6f} USDT", 
        annotation_position="bottom left", annotation_font=dict(size=11, color="black"), annotation_bgcolor="#00e6ff"
    )
    fig.add_hline(
        y=user_custom_price, line_dash="dashdot", line_color="#ffff00", line_width=3,
        annotation_text=f"🟡 เส้นของคุณ: {user_custom_price:,.6f} USDT", 
        annotation_position="top left", annotation_font=dict(size=12, color="black"), annotation_bgcolor="#ffff00"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False, template="plotly_dark", height=550, margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # AI Analysis Text
    st.markdown("### 🧠 AI Direction & Market Psychology")
    if current_price > main_trend_ema:
        st.info(f"📈 **แนวโน้มระยะสั้น ({tf_choice}) : ขาขึ้น (Bullish Bias)** — ได้เปรียบฝั่ง Buy แนะนำรอย่อเข้าซื้อที่จุดสีฟ้า")
    else:
        st.warning(f"📉 **แนวโน้มระยะสั้น ({tf_choice}) : ขาลง (Bearish Bias)** — ระวังแรงเทขายสะสม เล่นด้วยความระมัดระวัง")

except Exception as e:
    st.error(f"⚠️ ไม่สามารถโหลดข้อมูลเจาะลึกของ {selected_symbol} ได้: {str(e)}")

# -----------------------------------------------------------------------------
# 9. ลูป Auto Refresh
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(5)
    st.rerun()
