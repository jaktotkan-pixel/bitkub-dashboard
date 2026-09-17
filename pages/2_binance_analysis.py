import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

# หัวข้อหน้าแดชบอร์ด
st.title("📊 Binance Realtime vs My Analysis")
st.subheader("ระบบวิเคราะห์ราคาเรียลไทม์ ซ้อนทับจุดเข้าซื้อ (Buy Zone)")

# 1. ฟังก์ชันดึงรายชื่อเหรียญเวอร์ชันแก้ไข (ครอบคลุม DOGE และทุกคู่เทรด USDT)
@st.cache_data(ttl=3600)
def get_binance_symbols():
    try:
url = "https://binance.us"
        response = requests.get(url).json()
        # ปรับเงื่อนไขให้กรองเฉพาะเหรียญที่จับคู่กับ USDT และพร้อมให้เทรดจริงทั้งหมด
        symbols = [s['symbol'] for s in response['symbols'] if s['symbol'].endswith('USDT') and 'TRADING' in s.get('status', s.get('tradingStatus', ''))]
        
        # ลบรายการที่ซ้ำและจัดเรียงตัวอักษร
        symbols = sorted(list(set(symbols)))
        
        # เพิ่ม Guard เผื่อไว้ถ้าชื่อ DOGEUSDT หลุดไป ให้ใส่แทรกเข้าไปดื้อๆ เลย
        if "DOGEUSDT" not in symbols:
            symbols.append("DOGEUSDT")
            symbols = sorted(symbols)
            
        return symbols
    except Exception as e:
        # หาก API สัญญาณขาดหาย ให้คืนค่าเหรียญหลักๆ มารองรับทันที
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT"]

all_symbols = get_binance_symbols()

# 2. แถบควบคุมด้านซ้ายมือ (Sidebar)
st.sidebar.header("⚙️ ตั้งค่าข้อมูล")
selected_symbol = st.sidebar.selectbox(
    "เลือกเหรียญใน Binance:", 
    all_symbols, 
    index=all_symbols.index("BTCUSDT") if "BTCUSDT" in all_symbols else 0
)

timeframe = st.sidebar.selectbox(
    "เลือก Timeframe:", 
    ["1m", "5m", "15m", "1h", "4h", "1d"], 
    index=2  # ค่าเริ่มต้น 15m
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 จุดวิเคราะห์เข้า BUY")
my_target_price = st.sidebar.number_input("ราคาแนวรับที่คาดว่าจะลงมาถึง:", value=0.0, format="%.6f")
buy_zone_buffer = st.sidebar.number_input("ขอบเขต Buy Zone (+/- จากเป้าหมาย):", value=0.0, format="%.6f")

# ระบบเปิด-ปิด Auto Refresh เพื่อดึงราคาระดับวินาที
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("เปิดระบบดึงราคา Realtime (อัปเดตทุก 5 วินาที)", value=True)

# 3. ฟังก์ชันดึงข้อมูลแท่งเทียนย้อนหลัง
def get_klines(symbol, interval):
    url = f"https://binance.us{symbol}&interval={interval}&limit=80"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', '_', '_', '_', '_', '_', '_'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = df[col].astype(float)
    return df

# โหลดข้อมูล
df = get_klines(selected_symbol, timeframe)
current_price = df['Close'].iloc[-1]

# 4. แสดงผลราคาปัจจุบันตัวใหญ่ๆ
col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"ราคาตลาดปัจจุบัน ({selected_symbol})", value=f"{current_price:,.4f} USDT")
with col2:
    if my_target_price > 0:
        dist_percent = ((current_price - my_target_price) / current_price) * 100
        st.metric(label="ระยะห่างจากจุดเข้าซื้อของคุณ", value=f"{dist_percent:.2f} %")

# 5. สร้างกราฟซ้อนกันระหว่างแท่งเทียนจริง กับ เส้นวิเคราะห์ของคุณ
fig = go.Figure()

# วาดกราฟแท่งเทียนราคาจริง
fig.add_trace(go.Candlestick(
    x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='ราคาตลาดจริง',
    increasing_line_color='#0ecb81', decreasing_line_color='#f6465d'
))

# วาดเส้นจุดวิเคราะห์ซ้อนทับลงไป
if my_target_price > 0:
    # เส้นราคาเป้าหมาย
    fig.add_hline(
        y=my_target_price, line_dash="dash", line_color="#00e6ff", line_width=2, 
        annotation_text="🎯 จุดวิเคราะห์ของคุณ", annotation_position="top right"
    )
    
    # พื้นที่เงาสีเขียว (Buy Zone)
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

# 6. ส่วนแจ้งเตือนสถานะการเข้าซื้อ
st.markdown("### 🔔 สถานะการวิเคราะห์")
if my_target_price > 0:
    if current_price <= my_target_price + buy_zone_buffer and current_price >= my_target_price - buy_zone_buffer:
        st.success("✅ ราคาไหลลงมาอยู่ใน Buy Zone ที่คุณวิเคราะห์ไว้แล้ว! พิจารณาเข้าซื้อ")
    elif current_price > my_target_price:
        st.info("⏳ ราคายังอยู่สูงกว่าแผนการเทรดของคุณ กำลังรอให้ย่อตัวลงมา")
    else:
        st.warning("⚠️ ราคาหลุดทะลุแนวรับแนววิเคราะห์ลงไปแล้ว (โปรดระวังการกลับตัว)")
else:
    st.info("💡 กรุณากรอก 'ราคาแนวรับที่คาดว่าจะลงมาถึง' ที่แถบเมนูด้านซ้ายเพื่อเริ่มต้นเปรียบเทียบกราฟซ้อน")

# 7. ระบบสั่งรีเฟรชหน้าจออัตโนมัติเพื่อให้กราฟขยับ
if auto_refresh:
    time.sleep(5)
    st.rerun()

