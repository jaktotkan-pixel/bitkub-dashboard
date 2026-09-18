import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. ตั้งค่าหน้าจอ Streamlit Dashboard
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Crypto Daily AI Model",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Multi-Crypto Daily AI Model (Bypass Connection Block)")
st.subheader("ระบบสรุปจุดซื้อ AI Buy Zone (ดึงข้อมูลผ่าน Public Crypto Data Bridge)")

# -----------------------------------------------------------------------------
# 2. รายชื่อเหรียญและ ID การดึงข้อมูล
# -----------------------------------------------------------------------------
CRYPTO_MAP = {
    "BTCUSDT": {"id": "bitcoin", "symbol": "BTC"},
    "ETHUSDT": {"id": "ethereum", "symbol": "ETH"},
    "SOLUSDT": {"id": "solana", "symbol": "SOL"},
    "BNBUSDT": {"id": "binancecoin", "symbol": "BNB"},
    "DOGEUSDT": {"id": "dogecoin", "symbol": "DOGE"},
    "XRPUSDT": {"id": "ripple", "symbol": "XRP"},
    "ADAUSDT": {"id": "cardano", "symbol": "ADA"},
    "SHIBUSDT": {"id": "shiba-inu", "symbol": "SHIB"},
    "DOTUSDT": {"id": "polkadot", "symbol": "DOT"},
    "LINKUSDT": {"id": "chainlink", "symbol": "LINK"}
}

# -----------------------------------------------------------------------------
# 3. แถบควบคุมด้านซ้ายมือ (Sidebar)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ ตัวเลือกสัญญาณ")
selected_display = st.sidebar.selectbox("เลือกเหรียญเจาะลึกบนกราฟ:", list(CRYPTO_MAP.keys()), index=4)

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe กราฟเจาะลึก:", 
    ["1h", "4h", "1d"], 
    index=1
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 15 วินาที)", value=True)

# -----------------------------------------------------------------------------
# 4. ฟังก์ชันดึงข้อมูลราคาย้อนหลัง (Bypass Connection Error)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=10)
def get_crypto_klines_safe(symbol_key, days=30):
    coin_id = CRYPTO_MAP[symbol_key]["id"]
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    res = requests.get(url, params=params, headers=headers, timeout=5)
    
    if res.status_code != 200:
        raise Exception(f"ไม่สามารถเชื่อมต่อ Data API ได้ Code: {res.status_code}")
        
    data = res.json()
    prices = data['prices']
    
    df = pd.DataFrame(prices, columns=['Timestamp', 'Close'])
    df['Time'] = pd.to_datetime(df['Timestamp'], unit='ms')
    
    # จำลองแท่งเทียน Open, High, Low จาก Price Action เพื่อใช้คำนวณ Indicator
    df['Open'] = df['Close'].shift(1).fillna(df['Close'])
    df['High'] = df[['Open', 'Close']].max(axis=1) * 1.002
    df['Low'] = df[['Open', 'Close']].min(axis=1) * 0.998
    
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# -----------------------------------------------------------------------------
# 5. ฟังก์ชันคำนวณสัญญาณ AI รายวัน (Fixed Daily Zone)
# -----------------------------------------------------------------------------
def calculate_daily_fixed_signals(symbol_key):
    df_daily = get_crypto_klines_safe(symbol_key, days=30)
    
    ai_max_high = float(df_daily['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df_daily['Low'].rolling(window=20).min().iloc[-1])
    current_price = float(df_daily['Close'].iloc[-1])
    
    # คำนวณ RSI
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
# 6. ฟังก์ชันสร้างตารางสรุป 10 เหรียญ
# -----------------------------------------------------------------------------
def get_all_crypto_summary(symbol_list):
    summary_data = []
    for sym in symbol_list:
        try:
            sup, buy_zone, max_high, price = calculate_daily_fixed_signals(sym)
            dist_pct = ((price - buy_zone) / buy_zone) * 100
            
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
# 7. แสดงผลตารางสรุป
# -----------------------------------------------------------------------------
st.markdown("### 📋 ตารางสรุปจุดซื้อ AI Buy Zone ของทุกเหรียญ (ประจำวัน)")

with st.spinner("กำลังดึงราคาแบบ Real-time..."):
    df_summary = get_all_crypto_summary(list(CRYPTO_MAP.keys()))
    
st.dataframe(df_summary, use_container_width=True, hide_index=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# 8. กราฟเจาะลึกรายเหรียญ
# -----------------------------------------------------------------------------
st.markdown(f"### 📈 เจาะลึกกราฟ & สัญญาณเทรด: **{selected_display}**")

try:
    df_chart = get_crypto_klines_safe(selected_display, days=7)
    current_price = df_chart['Close'].iloc[-1]
    
    df_chart['EMA_50'] = df_chart['Close'].ewm(span=50, adjust=False).mean()
    main_trend_ema = df_chart['EMA_50'].iloc[-1]
    
    ai_support_line, ai_buy_zone_line, ai_max_high_line, _ = calculate_daily_fixed_signals(selected_display)
    
    # Sidebar Slider
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
        st.metric(label=f"ราคาปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🔵 AI Best Buy Zone", value=f"{ai_buy_zone_line:,.6f} USDT")
    with col3:
        st.metric(label="🔴 AI Max High Target", value=f"{ai_max_high_line:,.6f} USDT")
    with col4:
        user_dist = ((user_custom_price - current_price) / current_price) * 100
        st.metric(label="✏️ เส้นวิเคราะห์ส่วนตัว", value=f"{user_custom_price:,.6f} USDT", delta=f"{user_dist:.2f}%")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_chart['Time'], open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'],
        name='ราคา Realtime', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right", annotation_font=dict(size=11, color="white"), annotation_bgcolor="#ff4500"
    )
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"🔵 BUY ZONE: {ai_buy_zone_line:,.6f} USDT", 
        annotation_position="bottom left", annotation_font=dict(size=11, color="black"), annotation_bgcolor="#00e6ff"
    )
    fig.add_hline(
        y=user_custom_price, line_dash="dashdot", line_color="#ffff00", line_width=3,
        annotation_text=f"🟡 เส้นของคุณ: {user_custom_price:,.6f} USDT", 
        annotation_position="top left", annotation_font=dict(size=12, color="black"), annotation_bgcolor="#ffff00"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False, template="plotly_dark", height=500, margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดกราฟ: {str(e)}")

# -----------------------------------------------------------------------------
# 9. Auto Refresh (15s)
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(15)
    st.rerun()
