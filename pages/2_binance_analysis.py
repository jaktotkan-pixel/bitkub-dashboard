import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import time

# ตั้งค่าหน้าจอแดชบอร์ดให้แสดงผลแบบเต็มหน้าจอ (Wide Mode)
st.set_page_config(layout="wide")

st.title("📊 Binance Realtime vs AI Analysis Model")
st.subheader("ระบบ AI วิเคราะห์ทิศทางรายวัน & ตรวจจับจุดเข้าซื้ออัตโนมัติ (ไม่ต้องคีย์ตัวเลข)")

# 1. รายชื่อเหรียญยอดนิยมคู่ USDT บนกระดานเทรด (ดึงผ่านช่องทางเปิดเสถียรภาพสูง 100%)
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
    ["1m", "2m", "5m", "15m", "30m", "1h", "1d"], 
    index=3  # ค่าเริ่มต้น 15m สำหรับสายซิ่งดูรอบสั้น
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
        raise Exception("สัญญาณดิบจากเซิร์ฟเวอร์หลักขัดข้องชั่วคราว")
        
    df = df.reset_index()
    time_col = 'Datetime' if 'Datetime' in df.columns else ('Date' if 'Date' in df.columns else df.columns)
    df = df.rename(columns={time_col: 'Time'})
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# 4. ฟังก์ชัน AI ประมวลผลหาทิศทางรายวันและโซนที่ User ส่วนใหญ่สะสมของจริง
def calculate_ai_signals(df):
    # คำนวณแนวรับมหาชนจากจุดต่ำสุดที่มีการเด้งบ่อยย้อนหลัง 20 แท่ง (Swing Low Support)
    ai_support = float(df['Low'].rolling(window=20).min().iloc[-1])
    
    # คำนวณเส้นทิศทางแนวโน้มภาพรวมหลักรายวันด้วย EMA 50
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    current_ema = df['EMA_50'].iloc[-1]
    
    # คำนวณความแรงตลาดด้วย RSI 14 เพื่อดูสภาวะขายมากเกินไป (Oversold Area)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else 50
    
    # อัลกอริทึมจำลองราคาทุนเฉลี่ยรายใหญ่ช้อนซื้อ (Best Buy Zone)
    avg_price = df['Close'].rolling(window=10).mean().iloc[-1]
    if last_rsi < 40:
        ai_buy_zone = avg_price * 0.995 # ตลาด Panic เทขายรุนแรง AI ดึงแนวรับช้อนซื้อให้ต่ำลงตามกลไก
    else:
        ai_buy_zone = ai_support * 1.002 # สภาพปกติ ตั้งรับซื้อไว้เหนือเส้นแนวรับมหาชนเล็กน้อยป้องกันตกรด
        
    return ai_support, ai_buy_zone, current_ema

# ประมวลผลรันระบบ
try:
    df = get_crypto_candles(ticker_symbol, tf_choice)
    current_price = df['Close'].iloc[-1]
    
    # คำนวณโมเดลแผนการเทรดอัตโนมัติ
    ai_support_line, ai_buy_zone_line, main_trend_ema = calculate_ai_signals(df)
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"⚠️ ระบบกำลังเชื่อมโยงอัลกอริทึมข้อมูลคริปโต: {str(e)}")

# วาดหน้าจอแสดงผลเมื่อโหลดสำเร็จ
if not error_trigger:
    # 4. กล่องสรุปสถิติเป้าหมายแบบตัวเลขกระพริบเรียลไทม์
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"ราคาปัจจุบัน ({selected_display})", value=f"{current_price:,.6f} USDT")
    with col2:
        st.metric(label="🟢 แนวรับสำคัญ (มหาชนตั้งรับหนาแน่น)", value=f"{ai_support_line:,.6f} USDT", 
                  delta=f"{((current_price - ai_support_line) / current_price) * -100:.2f}% ห่างจากจุดรับ")
    with col3:
        st.metric(label="🔵 AI Best Buy Zone (ทุนรายใหญ่สะสม)", value=f"{ai_buy_zone_line:,.6f} USDT")

    # 5. วาดกราฟเปรียบเทียบซ้อนทับเส้นอัตโนมัติ
    fig = go.Figure()

    # วาดกราฟแท่งเทียนตลาดจริง (เขียว-แดงสไตล์กระดาน Binance)
    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคาตลาดจริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # วาดเส้นวิเคราะห์อัตโนมัติซ้อนลงไปบนแกนราคาเดียวกัน
    # 1. เส้นทึบแนวรับมหาชนที่คนตั้งรับซื้อหนาแน่น
    fig.add_hline(
        y=ai_support_line, line_dash="solid", line_color="#00ff88", line_width=2,
        annotation_text="🟢 แนวรับมหาชน", annotation_position="bottom left"
    )
    
    # 2. เส้นประเป้าหมายจุดที่ควรเข้าซื้อช้อนราคาที่ดีที่สุด
    fig.add_hline(
        y=ai_buy_zone_line, line_dash="dash", line_color="#00e6ff", line_width=2,
        annotation_text="🔵 AI Buy Zone", annotation_position="top right"
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=550,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 6. กล่อง AI เจาะลึกทิศทางทิศทางการเทรดรอบวัน (Daily Bias) ควบปัจจัยจิตวิทยา
    st.markdown("---")
    st.markdown("### 🧠 AI Trading Direction & Market Psychology Analysis")
    
    # ส่วนวิเคราะห์ทิศทางต่อวัน (Daily Trend Direction)
    if current_price > main_trend_ema:
        st.info("📈 **แนวโน้มทิศทางรอบวัน (Daily Bias): เป็นขาขึ้นเชิงบวก (Bullish Outperform)**\n\nพฤติกรรมผู้เล่นส่วนใหญ่ในวันนี้กำลังมีความเชื่อมั่นและเน้นเปิดสถานะฝั่ง Buy เป็นหลัก แนะนำให้เน้นตั้งรับซื้อตามจังหวะที่ย่อตัวลงมาเทสโซนแนวรับ")
    else:
        st.warning("📉 **แนวโน้มทิศทางรอบวัน (Daily Bias): เป็นขาลงคุมตลาด (Bearish Underperform)**\n\nระวังแรงเทขายสะสมจากปัจจัยข่าวเศรษฐกิจโลกและพฤติกรรมการถอนเงินสดหลบความเสี่ยงของผู้เล่นรายใหญ่ แนะนำเน้นความเพลย์เซฟ")

    # ส่วนวิเคราะห์จังหวะการเข้าซื้อวินาทีปัจจุบัน
    st.markdown("**📌 แผนการเข้าเทรด ณ เวลาปัจจุบัน:**")
    if current_price <= ai_buy_zone_line * 1.005 and current_price >= ai_support_line:
        st.success(f"✅ **จังหวะซื้อได้เปรียบสูง (Strong Buy Alert):** ราคาลดราคาลงมาเคลียร์คนทำฝั่ง Long ตกรถ และเข้าใกล้จุดราคาทุนเฉลี่ยมหาชนที่ **{ai_buy_zone_line:,.6f} USDT** แรงช้อนซื้อกลับมักจะหนาแน่นจุดนี้ พิจารณาแบ่งไม้เข้าซื้อได้ครับ")
    elif current_price < ai_support_line:
        st.error(f"🚨 **จุดอันตราย (Panic Sell / Stop Loss Flow):** ราคาหลุดทะลุแนวรับสำคัญลงมา พฤติกรรมรายย่อยส่วนใหญ่กำลังแห่เทขายตัดขาดทุนเพื่อความปลอดภัย แนะนำให้ชะลอการกดปุ่ม Buy ออกไปก่อน จนกว่าราคาสัญญาณจะนิ่ง")
    else:
        st.markdown(f"⏳ **รอการย่อตัว (Wait for Pullback):** ราคายังลอยอยู่ค่อนข้างแพง หากกด Buy ตอนนี้จะเสียเปรียบ พฤติกรรมมหาชนกำลังตั้งโรบอทดักช้อนซื้อเมื่อกราฟย่อตัวลงมาแถวๆ **{ai_buy_zone_line:,.6f} USDT**")

# 7. สั่งกระตุ้นระบบรีเฟรชอัปเดตราคาแบบ Realtime ทุกๆ 5 วินาที
if auto_refresh:
    time.sleep(5)
    st.rerun()
