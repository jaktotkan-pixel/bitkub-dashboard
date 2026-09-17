import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

st.title("📊 Binance Realtime vs My Analysis")
st.subheader("ระบบวิเคราะห์ราคาเรียลไทม์ ซ้อนทับจุดเข้าซื้อ (Global Open API Version)")

# 1. รายชื่อเหรียญยอดนิยมบนตลาด Binance จับคู่ USDT (ป้องกันปัญหา API บล็อก)
# คุณสามารถพิมพ์เพิ่มชื่อเหรียญตัวพิมพ์ใหญ่ลงใน List นี้ได้ตามใจชอบเลยครับ
POPULAR_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", 
    "XRPUSDT", "ADAUSDT", "SHIBUSDT", "DOTUSDT", "LINKUSDT",
    "AVAXUSDT", "MATICUSDT", "TRXUSDT", "LTCUSDT", "NEARUSDT"
]

# 2. แถบควบคุมด้านซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ ตั้งค่าข้อมูล")
selected_symbol = st.sidebar.selectbox("เลือกเหรียญ:", POPULAR_SYMBOLS, index=POPULAR_SYMBOLS.index("DOGEUSDT"))

timeframe = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=2  # ค่าเริ่มต้น 15m
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 จุดวิเคราะห์เข้า BUY")
my_target_price = st.sidebar.number_input("ราคาแนวรับที่คาดว่าจะลงมาถึง:", value=0.0, format="%.6f")
buy_zone_buffer = st.sidebar.number_input("ขอบเขต Buy Zone (+/- จากเป้าหมาย):", value=0.0, format="%.6f")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 3. ฟังก์ชันดึงข้อมูลแท่งเทียนอัจฉริยะ (ยิงผ่าน Open API ไม่โดนบล็อก IP)
def get_klines_backup(symbol, interval):
    # แกะชื่อเหรียญ เช่น DOGEUSDT -> coin='DOGE', market='USDT'
    coin = symbol.replace("USDT", "")
    
    # แปลงหน่วยเวลาให้เข้ากับ Open API
    limit = 80
    if interval == "1m": url_part = f"histominute?fsym={coin}&tsym=USDT&limit={limit}&aggregate=1"
    elif interval == "5m": url_part = f"histominute?fsym={coin}&tsym=USDT&limit={limit}&aggregate=5"
    elif interval == "15m": url_part = f"histominute?fsym={coin}&tsym=USDT&limit={limit}&aggregate=15"
    elif interval == "1h": url_part = f"histohour?fsym={coin}&tsym=USDT&limit={limit}&aggregate=1"
    elif interval == "4h": url_part = f"histohour?fsym={coin}&tsym=USDT&limit={limit}&aggregate=4"
    else: url_part = f"histoday?fsym={coin}&tsym=USDT&limit={limit}"
    
    url = f"https://cryptocompare.com{url_part}"
    
    res = requests.get(url).json()
    raw_data = res['Data']['Data']
    
    df = pd.DataFrame(raw_data)
    # แปลงหัวตารางให้ตรงกับระบบแท่งเทียนปกติ
    df['Time'] = pd.to_datetime(df['time'], unit='s')
    df['Open'] = df['open'].astype(float)
    df['High'] = df['high'].astype(float)
    df['Low'] = df['low'].astype(float)
    df['Close'] = df['close'].astype(float)
    return df[['Time', 'Open', 'High', 'Low', 'Close']]

# ดึงข้อมูลมาประมวลผล
try:
    df = get_klines_backup(selected_symbol, timeframe)
    current_price = df['Close'].iloc[-1]
    error_trigger = False
except Exception as e:
    error_trigger = True
    st.error(f"❌ เกิดข้อผิดพลาดในการโหลดข้อมูลชั่วคราว: {str(e)}")

# ถ้าข้อมูลโหลดสำเร็จ ให้วาดกราฟทันที
if not error_trigger:
    # 4. แสดงผลราคาปัจจุบันตัวใหญ่ๆ
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"ราคาตลาดปัจจุบัน ({selected_symbol})", value=f"{current_price:,.6f} USDT")
    with col2:
        if my_target_price > 0:
            dist_percent = ((current_price - my_target_price) / current_price) * 100
            st.metric(label="ระยะห่างจากจุดเข้าซื้อของคุณ", value=f"{dist_percent:.2f} %")

    # 5. สร้างกราฟแท่งเทียนซ้อนเส้นแผนเทรด
    fig = go.Figure()

    # วาดแท่งเทียนจริง
    fig.add_trace(go.Candlestick(
        x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='ราคาตลาดจริง',
        increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
    ))

    # วาดเส้นแนวรับที่คุณวิเคราะห์ซ้อนทับลงไป
    if my_target_price > 0:
        fig.add_hline(
            y=my_target_price, line_dash="dash", line_color="#00e6ff", line_width=2, 
            annotation_text="🎯 จุดวิเคราะห์ของคุณ", annotation_position="top right"
        )
        
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

    # 6. ส่วนแจ้งเตือนสถานะ
    st.markdown("### 🔔 Status")
    if my_target_price > 0:
        if current_price <= my_target_price + buy_zone_buffer and current_price >= my_target_price - buy_zone_buffer:
            st.success("✅ ราคาไหลลงมาอยู่ใน Buy Zone ที่คุณวิเคราะห์ไว้แล้ว! พิจารณาเข้าซื้อ")
        elif current_price > my_target_price:
            st.info("⏳ ราคยังอยู่สูงกว่าแผนการเทรดของคุณ กำลังรอให้ย่อตัวลงมา")
        else:
            st.warning("⚠️ ราคาหลุดทะลุแนวรับแนววิเคราะห์ลงไปแล้ว (โปรดระวังการกลับตัว)")
    else:
        st.info("💡 กรุณากรอก 'ราคาแนวรับที่คาดว่าจะลงมาถึง' ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นเปรียบเทียบกราฟซ้อน")

# 7. ระบบสั่งรีเฟรชหน้าจออัตโนมัติ (ขยับทุกๆ 5 วินาที)
if auto_refresh:
    time.sleep(5)
    st.rerun()
