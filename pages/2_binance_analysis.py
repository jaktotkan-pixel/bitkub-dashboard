import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import time

# -----------------------------------------------------------------------------
# 1. ตั้งค่าหน้าจอ Streamlit Dashboard
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Crypto AI Dynamic & Predictive Model",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Multi-Crypto AI Dynamic & Predictive Model")
st.subheader("ระบบสรุปจุดซื้อ Dynamic AI พร้อมคาดการณ์แรงซื้อ/แรงขายบนแท่งเทียน (Predictive Momentum)")

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

status_filter = st.sidebar.multiselect(
    "🎯 กรองสถานะสัญญาณในตาราง:",
    options=["🔥 Active Buy Zone", "✅ Safe Buy Zone", "👀 Near Buy Zone", "⏳ Waiting", "🚨 Panic Breakout"],
    default=["🔥 Active Buy Zone", "✅ Safe Buy Zone", "👀 Near Buy Zone", "⏳ Waiting", "🚨 Panic Breakout"]
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
    data = yf.download(tickers=tickers, period="60d", interval="1d", group_by="ticker", progress=False)
    return data

@st.cache_data(ttl=25)
def get_single_crypto_detail(symbol_key, tf):
    ticker = CRYPTO_MAP[symbol_key]
    interval = "1h" if tf == "4h" else tf
    period = "1mo" if tf in ["1h", "4h"] else "1y"
    
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df.empty:
        raise Exception("ไม่พบข้อมูลกราฟจากเซิร์ฟเวอร์หลัก")
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns[0])
    df = df.rename(columns={time_col: 'Time'})
    
    if tf == "4h":
        df.set_index('Time', inplace=True)
        df = df.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna().reset_index()
        
    return df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]

# -----------------------------------------------------------------------------
# 5. ฟังก์ชันคำนวณสัญญาณ AI รายวัน + Dynamic Active Buy Zone
# -----------------------------------------------------------------------------
def process_dynamic_ai_signals(df_symbol):
    df_symbol = df_symbol.dropna(subset=['Close']).copy()
    current_price = float(df_symbol['Close'].iloc[-1])
    
    ai_max_high = float(df_symbol['High'].rolling(window=20).max().iloc[-1])
    ai_support = float(df_symbol['Low'].rolling(window=20).min().iloc[-1])
    
    delta = df_symbol['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else 50

    safe_buy_zone = ai_support * 1.002

    ema20 = df_symbol['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
    std20 = df_symbol['Close'].rolling(window=20).std().iloc[-1]
    bollinger_lower = ema20 - (2 * std20) if pd.notnull(std20) else ema20 * 0.95
    
    if last_rsi >= 50:
        active_buy_zone = max(ema20 * 0.98, bollinger_lower)
    else:
        active_buy_zone = (ema20 + safe_buy_zone) / 2

    return safe_buy_zone, active_buy_zone, ai_max_high, current_price

# -----------------------------------------------------------------------------
# 6. ฟังก์ชันวิเคราะห์และกำหนดสถานะโมเมนตัมแท่งเทียน
# -----------------------------------------------------------------------------
def apply_ai_predictive_candle_colors(df):
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Vol_SMA'] = df['Volume'].rolling(window=10).mean().fillna(df['Volume'])

    colors = []
    predict_status = []

    for i in range(len(df)):
        close = df['Close'].iloc[i]
        open_p = df['Open'].iloc[i]
        ema9 = df['EMA_9'].iloc[i]
        ema21 = df['EMA_21'].iloc[i]
        rsi = df['RSI'].iloc[i] if pd.notnull(df['RSI'].iloc[i]) else 50
        vol = df['Volume'].iloc[i]
        vol_avg = df['Vol_SMA'].iloc[i]

        if close > ema9 and ema9 > ema21 and rsi >= 55:
            colors.append('#00FF7F')  # เขียวสว่าง
            predict_status.append("🟢 แรงซื้อหนาแน่น (Bullish Momentum)")
        elif close < ema9 and ema9 < ema21 and rsi <= 45:
            colors.append('#FF1493')  # แดงสว่าง
            predict_status.append("🔴 แรงขายกดดัน (Bearish Momentum)")
        elif rsi < 45 and vol > vol_avg * 1.1 and close > open_p:
            colors.append('#FFD700')  # เหลือง
            predict_status.append("🟡 เริ่มสะสมแรงซื้อ (Pre-Buy Signal)")
        elif rsi > 60 and vol > vol_avg * 1.1 and close < open_p:
            colors.append('#FF8C00')  # ส้ม
            predict_status.append("🟠 เริ่มมีแรงขายชะลอตัว (Pre-Sell Signal)")
        else:
            colors.append('#808080')  # เทา
            predict_status.append("⚪ ตลาดเลือกทาง (Sideway)")

    df['Candle_Color'] = colors
    df['AI_Predict_Status'] = predict_status
    return df

# -----------------------------------------------------------------------------
# 7. แสดงผลตารางสรุป
# -----------------------------------------------------------------------------
st.markdown("### 📋 ตารางสรุปจุดซื้อ Dynamic AI Buy Zone")

try:
    with st.spinner("กำลังคำนวณจุดซื้อ Dynamic และวิเคราะห์โมเมนตัม..."):
        all_data = get_all_crypto_daily_data()
        summary_list = []
        
        for display_name, ticker in CRYPTO_MAP.items():
            try:
                df_sym = all_data[ticker].copy()
                safe_buy, active_buy, max_high, price = process_dynamic_ai_signals(df_sym)
                dist_active_pct = ((price - active_buy) / active_buy) * 100
                
                if price <= active_buy and price >= safe_buy:
                    status = "🔥 Active Buy Zone"
                elif price <= safe_buy:
                    status = "✅ Safe Buy Zone"
                elif price < safe_buy * 0.95:
                    status = "🚨 Panic Breakout"
                elif dist_active_pct <= 2.5:
                    status = "👀 Near Buy Zone"
                else:
                    status = "⏳ Waiting"
                    
                summary_list.append({
                    "เหรียญ": display_name,
                    "ราคาปัจจุบัน (USDT)": f"{price:,.6f}",
                    "Dynamic Buy Zone (USDT)": f"{active_buy:,.6f}",
                    "Safe Buy Zone (USDT)": f"{safe_buy:,.6f}",
                    "Max High Target (USDT)": f"{max_high:,.6f}",
                    "ห่างจุดซื้อ Dynamic (%)": f"{dist_active_pct:+.2f}%",
                    "สถานะสัญญาณ": status
                })
            except Exception:
                summary_list.append({
                    "เหรียญ": display_name,
                    "ราคาปัจจุบัน (USDT)": "Error",
                    "Dynamic Buy Zone (USDT)": "-",
                    "Safe Buy Zone (USDT)": "-",
                    "Max High Target (USDT)": "-",
                    "ห่างจุดซื้อ Dynamic (%)": "-",
                    "สถานะสัญญาณ": "⚠️ Data Error"
                })
                
        df_full_summary = pd.DataFrame(summary_list)
        
        if status_filter:
            df_filtered = df_full_summary[df_full_summary['สถานะสัญญาณ'].isin(status_filter)]
        else:
            df_filtered = df_full_summary

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดตารางสรุป: {str(e)}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 8. แสดงผลกราฟเจาะลึก (แก้ปัญหาวาดกราฟ Plotly)
# -----------------------------------------------------------------------------
st.markdown(f"### 📈 เจาะลึกกราฟ & AI Predictive Momentum: **{selected_display}**")

try:
    df_chart = get_single_crypto_detail(selected_display, tf_choice)
    df_chart = apply_ai_predictive_candle_colors(df_chart)
    
    current_price = df_chart['Close'].iloc[-1]
    latest_predict = df_chart['AI_Predict_Status'].iloc[-1]
    
    df_daily_single = all_data[CRYPTO_MAP[selected_display]].copy()
    safe_buy_line, active_buy_line, ai_max_high_line, _ = process_dynamic_ai_signals(df_daily_single)
    
    # Card Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label=f"ราคาปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🔮 AI Momentum คาดการณ์แท่งปัจจุบัน", value=latest_predict)
    with col3:
        diff_act = ((current_price - active_buy_line) / active_buy_line) * 100
        st.metric(label="⚡ Dynamic Buy Zone", value=f"{active_buy_line:,.6f} USDT", delta=f"{diff_act:.2f}%")
    with col4:
        st.metric(label="🔴 AI Max High Target", value=f"{ai_max_high_line:,.6f} USDT")

    st.caption("🎨 **สัญลักษณ์สีแท่งเทียน AI:** 🟢 เขียว = แรงซื้อหนาแน่น | 🔴 แดง = แรงขายกดดัน | 🟡 เหลือง = เริ่มสะสมแรงซื้อ | 🟠 ส้ม = เริ่มมีแรงขายชะลอ | ⚪ เทา = Sideway")

    # 📌 วาดกราฟ Candlestick แบบรองรับ Custom Color แน่นอน
    fig = go.Figure()

    # สร้างแท่งเทียน Candlestick มาตรฐาน
    fig.add_trace(go.Candlestick(
        x=df_chart['Time'],
        open=df_chart['Open'],
        high=df_chart['High'],
        low=df_chart['Low'],
        close=df_chart['Close'],
        name='ราคาจริง',
        increasing_line_color='#0ecb81',
        decreasing_line_color='#f6465d'
    ))

    # วาดไฮไลต์จุดคาดการณ์ AI ด้วย Marker บนแท่งเทียนแบบเสถียร
    fig.add_trace(go.Scatter(
        x=df_chart['Time'],
        y=df_chart['High'] * 1.002,
        mode='markers',
        marker=dict(
            size=6,
            color=df_chart['Candle_Color'],
            symbol='circle'
        ),
        name='AI Predictive Momentum',
        hoverinfo='text',
        hovertext=df_chart['AI_Predict_Status']
    ))

    # เส้น AI Max High
    fig.add_hline(
        y=ai_max_high_line, line_dash="dash", line_color="#ff4500", line_width=2,
        annotation_text=f"🔴 MAX HIGH: {ai_max_high_line:,.6f} USDT", 
        annotation_position="top right", annotation_font=dict(size=11, color="white"), annotation_bgcolor="#ff4500"
    )
    # เส้น Dynamic Buy Zone
    fig.add_hline(
        y=active_buy_line, line_dash="solid", line_color="#00e6ff", line_width=2.5,
        annotation_text=f"⚡ DYNAMIC BUY ZONE: {active_buy_line:,.6f} USDT", 
        annotation_position="bottom left", annotation_font=dict(size=11, color="black"), annotation_bgcolor="#00e6ff"
    )
    # เส้น Safe Buy Zone
    fig.add_hline(
        y=safe_buy_line, line_dash="dot", line_color="#00ff7f", line_width=2,
        annotation_text=f"🛡️ SAFE BUY ZONE: {safe_buy_line:,.6f} USDT", 
        annotation_position="bottom right", annotation_font=dict(size=10, color="black"), annotation_bgcolor="#00ff7f"
    )

    # ตั้งค่า layout
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=520,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified"
    )
    
    fig.update_xaxes(showspikes=True, spikecolor="gray", spikethickness=1, spikedash="dot", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="gray", spikethickness=1, spikedash="dot", spikemode="across")

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดกราฟ: {str(e)}")

# -----------------------------------------------------------------------------
# 9. Auto Refresh (30s)
# -----------------------------------------------------------------------------
if auto_refresh:
    time.sleep(30)
    st.rerun()
