import streamlit as st
import pandas as pd
import yfinance as yf
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

st.title("⚡ Multi-Crypto Daily AI Model")
st.subheader("ระบบสรุปจุดซื้อ AI Buy Zone พร้อมระบบกรองสถานะสัญญาณ")

# -----------------------------------------------------------------------------
# 2. รายชื่อเหรียญและ Ticker บน Yahoo Finance
# -----------------------------------------------------------------------------
CRYPTO_MAP = {
    "BTCUSDT": "BTC-USD",
    "ETHUSDT": "ETH-USD",
    "SOLUSDT": "SOL-USD",
    "BNBUSDT": "BNB-USD",
    "DOGEUSDT": "DOGE-USD",
    "XRPUSDT": "XRP-USD",
    "ADAUSDT": "ADA-USD",
    "SHIBUSDT": "SHIB-USD",
    "DOTUSDT": "DOT-USD",
    "LINKUSDT": "LINK-USD"
}

# -----------------------------------------------------------------------------
# 3. แถบควบคุมด้านซ้ายมือ (Sidebar)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ ตัวเลือกสัญญาณ")

# ตัวกรองสถานะสัญญาณในตาราง
status_filter = st.sidebar.multiselect(
    "🎯 กรองสถานะสัญญาณในตาราง:",
    options=["✅ Strong Buy Zone", "👀 Near Buy Zone", "⏳ Waiting", "🚨 Panic Breakout"],
    default=["✅ Strong Buy Zone", "👀 Near Buy Zone", "⏳ Waiting", "🚨 Panic Breakout"]
)

selected_display = st.sidebar.selectbox("เลือกเหรียญเจาะลึกบนกราฟ:", list(CRYPTO_MAP.keys()), index=4)

tf_choice = st.sidebar.selectbox(
    "เลือก Timeframe กราฟเจาะลึก:", 
    ["1h", "4h", "1d"], 
    index=1
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 30 วินาที)", value=True)

# -----------------------------------------------------------------------------
# 4. ฟังก์ชันดึงข้อมูลแบบ Batch (ยิงทีเดียว 10 เหรียญ กัน Rate Limit)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=25)
def get_all_crypto_daily_data():
    tickers = list(CRYPTO_MAP.values())
    data = yf.download(tickers=tickers, period="30d", interval="1d", group_by="ticker", progress=False)
    return data

@st.cache_data(ttl=25)
def get_single_crypto_detail(symbol_key, tf):
    ticker = CRYPTO_MAP[symbol_key]
    interval = "1h" if tf == "4h" else tf
    period = "1mo" if tf in ["1h", "4h"] else "1y"
    
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df.empty:
        raise Exception("ไม่สามารถดึงข้อมูลกราฟเจาะลึกได้")
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns[0])
    df = df.rename(columns={time_col: 'Time'})
    
    if tf == "4h":
        df.set_index('Time', inplace=True)
        df = df.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna().reset_index()
        
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# -----------------------------------------------------------------------------
# 5. ฟังก์ชันคำนวณสัญญาณ AI รายวัน
# -----------------------------------------------------------------------------
def process_daily_ai_signals(df_symbol):
    df_symbol = df_symbol.dropna(subset=['Close'])
    ai_max_high = float(df_symbol['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df_symbol['Low'].rolling(window=20).min().iloc[-1])
    current_price = float(df_symbol['Close'].iloc[-1])
    
    delta = df_symbol['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_daily_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    avg_daily_price = df_symbol['Close'].rolling(window=10).mean().iloc[-1]
    
    if last_daily_rsi < 40:
        ai_buy_zone = avg_daily_price * 0.995 
    else:
        ai_buy_zone = ai_support * 1.002
        
    return ai_support, ai_buy_zone, ai_max_high, current_price

# -----------------------------------------------------------------------------
# 6. แสดงผลตารางสรุป + ระบบกรองสถานะสัญญาณ
# -----------------------------------------------------------------------------
st.markdown("### 📋 ตารางสรุปจุดซื้อ AI Buy Zone ของทุกเหรียญ (ประจำวัน)")

try:
    with st.spinner("กำลังอัปเดตราคาจากเซิร์ฟเวอร์หลัก..."):
        all_data = get_all_crypto_daily_data()
        summary_list = []
        
        for display_name, ticker in CRYPTO_MAP.items():
            try:
                df_sym = all_data[ticker].copy()
                sup, buy_zone, max_high, price = process_daily_ai_signals(df_sym)
                dist_pct = ((price - buy_zone) / buy_zone) * 100
                
                # จำแนกสถานะสัญญาณ
                if price <= buy_zone * 1.005 and price >= sup:
                    status = "✅ Strong Buy Zone"
                elif price < sup:
                    status = "🚨 Panic Breakout"
                elif dist_pct <= 3.0:
                    status = "👀 Near Buy Zone"
                else:
                    status = "⏳ Waiting"
                    
                summary_list.append({
                    "เหรียญ": display_name,
                    "ราคาปัจจุบัน (USDT)": f"{price:,.6f}",
                    "AI Buy Zone (USDT)": f"{buy_zone:,.6f}",
                    "Max High Target (USDT)": f"{max_high:,.6f}",
                    "ห่างจากจุดซื้อ (%)": f"{dist_pct:+.2f}%",
                    "สถานะสัญญาณ": status
                })
            except Exception:
                summary_list.append({
                    "เหรียญ": display_name,
                    "ราคาปัจจุบัน (USDT)": "Error",
                    "AI Buy Zone (USDT)": "-",
                    "Max High Target (USDT)": "-",
                    "ห่างจากจุดซื้อ (%)": "-",
                    "สถานะสัญญาณ": "⚠️ Data Error"
                })
                
        df_full_summary = pd.DataFrame(summary_list)
        
        # กรองข้อมูลตามที่ผู้ใช้เลือกใน Sidebar
        if status_filter:
            df_filtered = df_full_summary[df_full_summary['สถานะสัญญาณ'].isin(status_filter)]
        else:
            df_filtered = df_full_summary

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดตารางสรุป: {str(e)}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. แสดงผลกราฟเจาะลึกรายเหรียญ
# -----------------------------------------------------------------------------
st.markdown(f"### 📈 เจาะลึกกราฟ & สัญญาณเทรด: **{selected_display}**")

try:
    df_chart = get_single_crypto_detail(selected_display, tf_choice)
    current_price = df_chart['Close'].iloc[-1]
    
    df_chart['EMA_50'] = df_chart['Close'].ewm(span=50, adjust=False).mean()
    main_trend_ema = df_chart['EMA_50'].iloc[-1]
    
    df_daily_single = all_data[CRYPTO_MAP[selected_display]].copy()
    ai_support_line, ai_buy_zone_line, ai_max_high_line, _ = process_daily_ai_signals(df_daily_single)
    
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

    # Card Metrics
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
        name='ราคาตลาดจริง', increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
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
# 8. Auto Refresh (30s)
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(30)
    st.rerun()
