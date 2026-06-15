import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as [g]o
from datetime import datetime, timedelta

# --- 1. SETUP PAGE & STYLE ---
st.set_page_config(page_title="Crypto Candlestick Simulator", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #0b0e14;
        color: #cbd5e1;
        font-family: 'Anuphan', sans-serif;
    }
    .decision-card-buy {
        background: rgba(0, 255, 102, 0.04);
        border: 1px solid #00ff66;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .decision-card-sell {
        background: rgba(255, 59, 48, 0.04);
        border: 1px solid #ff3b30;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 800;'>📈 CANDLESTICK PATTERN SIMULATOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>ระบบจำลองกราฟเทรดเสมือนจริงเพื่อฝึกการตัดสินใจเข้า Order ซื้อ (B) / ขาย (S)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 1px solid #1e293b; margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🗂️ฟังก์ชันสร้างข้อมูลกราฟจำลองเสมือนจริง (6-10 แท่งต่อเนื่อง)
# -----------------------------------------------------------------
def generate_mock_data(pattern_type="hammer"):
    base_time = datetime.now() - timedelta(hours=10)
    times = [base_time + timedelta(hours=i) for i in range(8)]
    
    if pattern_type == "hammer":
        # จำลองสถานการณ์ขาลง -> เกิดค้อน -> เด้งขึ้น
        opens  = [45.0, 43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0]
        highs  = [45.5, 44.0, 42.2, 41.5, 39.2, 41.0, 42.5, 44.2]
        lows   = [43.0, 41.5, 40.0, 38.0, 34.0, 38.8, 40.5, 42.0]
        closes = [43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0, 44.0]
    else:
        # จำลองสถานการณ์ขาขึ้น -> เกิดดาวตก -> ดิ่งลงเหว
        opens  = [38.0, 40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5]
        highs  = [40.5, 42.5, 44.0, 45.5, 50.0, 45.2, 42.5, 40.0]
        lows   = [37.8, 40.0, 41.8, 43.5, 44.2, 41.5, 39.0, 37.0]
        closes = [40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5, 37.5]
        
    df = pd.DataFrame({
        'Time': times, 'Open': opens, 'High': highs, 'Low': lows, 'Close': closes
    })
    # คำนวณเส้นอินดิเคเตอร์จำลองให้เห็นทิศทางแนวโน้ม
    df['EMA12'] = df['Close'].ewm(span=3, adjust=False).mean() # ปรับ span ให้สั้นลงเพื่อให้สอดคล้องกับแท่งเทียนจำลอง
    df['EMA26'] = df['Close'].ewm(span=5, adjust=False).mean()
    return df

# เลือกโหมดที่ต้องการศึกษาหรือจำลองสถานการณ์
mode = st.radio("⚡ เลือกสถานการณ์กราฟจำลองเพื่อฝึกตัดสินใจ:", ["🟢 จำลองจุดซื้อ (B) ด้วยรูปแบบ Hammer", "🔴 จำลองจุดขาย (S) ด้วยรูปแบบ Shooting Star"], horizontal=True)

# -----------------------------------------------------------------
# 🟢 MODE 1: HAMMER SIMULATION (จุดซื้อ B)
# -----------------------------------------------------------------
if mode == "🟢 จำลองจุดซื้อ (B) ด้วยรูปแบบ Hammer":
    df = generate_mock_data("hammer")
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.subheader("📊 กราฟจำลองสถานการณ์ตลาดเสมือนจริง")
        
        # วาดกราฟแท่งเทียนเสมือนจริงด้วย Plotly
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30',
            name="ราคาเหรียญ"
        )])
        
        # ใส่เส้น EMA 12 และ EMA 26 เข้าไปในกราฟ
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=1.5)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=1.5)))
        
        # ปักหมุดลูกศรชี้จุดซื้อ (B) บนแท่งที่คอนเฟิร์มสัญญาณ
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[5], y=df['Low'].iloc[5] - 1.5,
            text="🎯 BUY POINT (B)<br>เข้าซื้อไม้ที่ 1", showarrow=True,
            arrowhead=2, arrowcolor="#00ff66", bgcolor="#00ff66", font=dict(color="black", size=12),
            bordercolor="#00ff66", borderwidth=1, borderpad=4, ay=-40
        )
        
        fig.update_layout(
            plot_bgcolor='#05070a', paper_bgcolor='#05070a',
            xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💡 คู่มือวิเคราะห์เพื่อตัดสินใจออก Order")
        st.markdown("""
        <div class="decision-card_buy" style="border-left: 6px solid #00ff66; padding-left:15px; background:rgba(0,255,102,0.02);">
            <h4 style="color:#00ff66;">🔍 วิธีการมองหน้างานจริง:</h4>
            <p><b>1. สังเกตแนวโน้มหลักก่อนหน้า:</b> กราฟ 4 แท่งแรกไหลลงต่อเนื่อง เส้น EMA ม้วนหัวลง แสดงว่าฝั่งขายคุมตลาดอยู่</p>
            <p><b>2. จุดเกิดแท่งค้อน (แท่งที่ 5):</b> ราคาเปิดมาปุ๊บโดนลากลงไปลึกมาก (ทิ้งไส้ล่างยาวเรียว) ก่อนจะมี <b>'แรงซื้อปริศนา'</b> ดันราคากลับขึ้นมาปิดจุดบนสุด เกิดพฤติกรรมปฏิเสธราคาต่ำ</p>
            <p><b>3. แท่งคอนเฟิร์ม (แท่งที่ 6):</b> ดีดตัวขึ้นมาปิดเป็นแท่งเขียวเหนือหัวค้อนได้อย่างสวยงาม พร้อมเส้น EMA 12 เริ่มหักหัวกลับขึ้นมา</p>
            <h4 style="color:#ffffff; margin-top:15px;">🛠️ สรุปแผนเข้าออเดอร์ (Decision Making):</h4>
            <p style="color:#00ff66; font-size:16px; font-weight:bold;">👉 จังหวะนี้ สัญญาณคอนเฟิร์มครบถ้วน! สามารถกดเข้าเปิดออเดอร์ซื้อ (Buy Order) ไม้ที่ 1 ได้ทันทีที่ราคาปิดแท่งเขียวนี้ครับ</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🔴 MODE 2: SHOOTING STAR SIMULATION (จุดขาย S)
# -----------------------------------------------------------------
else:
    df = generate_mock_data("shooting")
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.subheader("📊 กราฟจำลองสถานการณ์ตลาดเสมือนจริง")
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30',
            name="ราคาเหรียญ"
        )])
        
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=1.5)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=1.5)))
        
        # ปักหมุดลูกศรชี้จุดขาย (S) บนแท่งที่หลุดแนวโน้ม
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[5], y=df['High'].iloc[5] + 1.5,
            text="⚠️ SELL POINT (S)<br>กดขายหนีตาย / ล็อกกำไร", showarrow=True,
            arrowhead=2, arrowcolor="#ff3b30", bgcolor="#ff3b30", font=dict(color="white", size=12),
            bordercolor="#ff3b30", borderwidth=1, borderpad=4, ay=40
        )
        
        fig.update_layout(
            plot_bgcolor='#05070a', paper_bgcolor='#05070a',
            xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'),
            margin=dict(l=20, r=20, t=20, b=20), height=450
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💡 คู่มือวิเคราะห์เพื่อตัดสินใจออก Order")
        st.markdown("""
        <div class="decision-card_sell" style="border-left: 6px solid #ff3b30; padding-left:15px; background:rgba(255,59,48,0.02);">
            <h4 style="color:#ff3b30;">🔍 วิธีการมองหน้างานจริง:</h4>
            <p><b>1. สังเกตแนวโน้มก่อนหน้า:</b> ราคาพุ่งขึ้นร้อนแรงมาก 4 แท่งแรกเป็นสีเขียวสดใส ยั่วยวนใจให้รายย่อยอยากกระโดดเกาะรถ (FOMO)</p>
            <p><b>2. จุดเกิดดาวตก (แท่งที่ 5):</b> ราคาดันซิ่งทะลักไปสูงมาก แต่สุดท้ายโดนแรงทุบมหาศาลไล่สับลงมาจนมาปิดตูดด้านล่าง ทิ้งไส้เทียนยาวเป็นเสาอากาศอยู่ข้างบน แปลว่าเจ้ามือรินขายของออกหมดแล้ว</p>
            <p><b>3. แท่งทุบย้ำตอกฝาโลง (แท่งที่ 6):</b> เกิดแท่งแดงใหญ่ลากดิ่งลงสวนทาง ทะลุเส้นแนวรับ EMA ขาลงก่อตัวสมบูรณ์</p>
            <h4 style="color:#ffffff; margin-top:15px;">🛠️ สรุปแผนเข้าออเดอร์ (Decision Making):</h4>
            <p style="color:#ff3b30; font-size:16px; font-weight:bold;">👉 จังหวะนี้ อันตรายสุดๆ! ห้ามกดเปิดออเดอร์ซื้อเด็ดขาด และถ้ามีของอยู่ในมือ ให้ทำตามแผนคือ "กดเปิดออเดอร์ขาย (Sell Order)" ออกมาถือเงินสดทันทีครับพี่!</p>
        </div>
        """, unsafe_allow_html=True)
