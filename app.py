import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SETUP PAGE & STYLE ---
st.set_page_config(page_title="Crypto Candlestick Simulator", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังมืดสไตล์ Cyberpunk Bitkub Room */
    .stApp {
        background-color: #0b0e14;
        color: #cbd5e1;
        font-family: 'Anuphan', sans-serif;
    }
    
    /* กล่องข้อมูลจุดตัดสินใจฝั่งซื้อ */
    .decision-card-buy {
        background: rgba(0, 255, 102, 0.02);
        border: 1px solid rgba(0, 255, 102, 0.2);
        border-left: 6px solid #00ff66;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* กล่องข้อมูลจุดตัดสินใจฝั่งขาย */
    .decision-card-sell {
        background: rgba(255, 59, 48, 0.02);
        border: 1px solid rgba(255, 59, 48, 0.2);
        border-left: 6px solid #ff3b30;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* ซ่อนปุ่ม Deploy ที่ไม่ได้ใช้ */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 800; margin-top: 10px;'>📈 CANDLESTICK PATTERN SIMULATOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>ระบบจำลองกราฟเทรดเสมือนจริงเพื่อฝึกการตัดสินใจเข้า Order ซื้อ (B) / ขาย (S)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 1px solid #1e293b; margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🗂️ ฟังก์ชันสร้างข้อมูลกราฟจำลองเสมือนจริง (6-8 แท่งต่อเนื่อง)
# -----------------------------------------------------------------
def generate_mock_data(pattern_type="hammer"):
    base_time = datetime.now() - timedelta(hours=10)
    times = [base_time + timedelta(hours=i) for i in range(8)]
    
    if pattern_type == "hammer":
        # จำลองเทรนด์ขาลง -> เกิดค้อน Hammer แท่งที่ 5 -> คอนเฟิร์มเขียวแท่งที่ 6 -> ดีดขึ้นต่อ
        opens  = [45.0, 43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0]
        highs  = [45.5, 44.0, 42.2, 41.5, 39.2, 41.0, 42.5, 44.2]
        lows   = [43.0, 41.5, 40.0, 38.0, 34.0, 38.8, 40.5, 42.0]
        closes = [43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0, 44.0]
    else:
        # จำลองเทรนด์ขาขึ้น -> เกิดดาวตก Shooting Star แท่งที่ 5 -> คอนเฟิร์มทุบแท่งที่ 6 -> ดิ่งลงเหว
        opens  = [38.0, 40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5]
        highs  = [40.5, 42.5, 44.0, 45.5, 50.0, 45.2, 42.5, 40.0]
        lows   = [37.8, 40.0, 41.8, 43.5, 44.2, 41.5, 39.0, 37.0]
        closes = [40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5, 37.5]
        
    df = pd.DataFrame({
        'Time': times, 'Open': opens, 'High': highs, 'Low': lows, 'Close': closes
    })
    
    # คำนวณเส้นอินดิเคเตอร์จำลองให้สอดคล้องกับพฤติกรรมกราฟ
    df['EMA12'] = df['Close'].ewm(span=3, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=5, adjust=False).mean()
    return df

# ส่วนเลือกโหมดสถานการณ์ในการเทรด
mode = st.radio("⚡ เลือกสถานการณ์กราฟจำลองเพื่อฝึกตัดสินใจหน้างาน:", ["🟢 ฝึกดูจุดซื้อ (B) ด้วยรูปแบบ Hammer", "🔴 ฝึกดูจุดขาย (S) ด้วยรูปแบบ Shooting Star"], horizontal=True)

# -----------------------------------------------------------------
# 🟢 MODE 1: HAMMER SIMULATION (ฝึกดูจุดเข้าซื้อ B)
# -----------------------------------------------------------------
if mode == "🟢 ฝึกดูจุดซื้อ (B) ด้วยรูปแบบ Hammer":
    df = generate_mock_data("hammer")
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.markdown("### 📊 กระดานกราฟจำลองเสมือนจริง (Interactive Chart)")
        
        # สร้างกราฟแท่งเทียนด้วย Plotly Object ที่ถูกต้อง
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30',
            name="ราคาปิด"
        )])
        
        # ใส่เส้น EMA 12 และ EMA 26 ลงไปบนหน้าจอ
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=2)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=2)))
        
        # สร้างลูกศรชี้เป้าจุด Action เข้าออเดอร์ซื้อ (B) หลังแท่งเขียวคอนเฟิร์มปิดตัว
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[5], y=df['Low'].iloc[5] - 1.2,
            text="🎯 BUY ORDER (B)<br>กดเข้าซื้อไม้ที่ 1 ตรงนี้!", showarrow=True,
            arrowhead=2, arrowcolor="#00ff66", bgcolor="#00ff66", font=dict(color="black", size=12, family="Anuphan"),
            bordercolor="#00ff66", borderwidth=1, borderpad=5, ay=-45
        )
        
        fig.update_layout(
            plot_bgcolor='#05070a', paper_bgcolor='#05070a',
            xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=10, t=10, b=10), height=460
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💡 คู่มือแกะรอยเจ้ามือเพื่อกดออเดอร์")
        st.markdown("""
        <div class="decision-card-buy">
            <h4 style="color:#00ff66; margin-top:0;">🔍 โครงสร้างพฤติกรรมราคาหน้าเทรด:</h4>
            <p><b>• แท่งที่ 1 - 4 (เทรนด์ลง):</b> ราคาไหลรูดลงมาเรื่อยๆ จนคนเริ่มถอดใจ ตลาดถูกฝั่งขายคุมเบ็ดเสร็จ</p>
            <p><b>• แท่งที่ 5 (เกิดรูปค้อน Hammer):</b> ราคาเปิดปุ๊บโดนทุบเปรี้ยงดิ่งลึกหลุดทุกแนวรับ แต่ก่อนปิดแท่งมีวอลลุ่มวาฬลึกลับดึงราคากลับขึ้นมาปิดบนสุดอย่างรวดเร็ว (ทิ้งไส้ล่างยาวเกิน 2 เท่าของเนื้อเทียน) แปลว่า <b>"เจ้ามือแอบกวาดของหนีคนคัทลอส"</b></p>
            <p><b>• แท่งที่ 6 (แท่งตัดสินคอนเฟิร์ม):</b> ราคาดีดปิดเป็นแท่งสีเขียวเต็มตัวอยู่เหนือหัวค้อน บ่งบอกว่าแรงซื้อชนะขาด</p>
            <h4 style="color:#ffffff; margin-top:15px;">🛠️ จังหวะตัดสินใจออก Order (Action):</h4>
            <p style="color:#00ff66; font-size:16px; font-weight:bold; margin-bottom:0;">👉 วินัยหน้างาน: เมื่อแท่งที่ 6 ปิดเขียวคอนเฟิร์มชัดเจน ให้ทำการ "กดเปิดออเดอร์ซื้อ (Buy ไม้ 1)" ที่ราคาปิดแท่งนี้ทันที พอร์ตจะปลอดภัยและได้เปรียบสุดๆ ครับพี่!</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🔴 MODE 2: SHOOTING STAR SIMULATION (ฝึกดูจุดเข้าขาย S)
# -----------------------------------------------------------------
else:
    df = generate_mock_data("shooting")
    
    col1, col2 = st.columns([1.8, 1.2])
    
    with col1:
        st.markdown("### 📊 กระดานกราฟจำลองเสมือนจริง (Interactive Chart)")
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30',
            name="ราคาปิด"
        )])
        
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=2)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=2)))
        
        # สร้างลูกศรชี้เป้าจุด Action ขายหนีตายหรือล็อกกำไร (S)
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[5], y=df['High'].iloc[5] + 1.2,
            text="⚠️ SELL ORDER (S)<br>กดขายล้างพอร์ตทันที!", showarrow=True,
            arrowhead=2, arrowcolor="#ff3b30", bgcolor="#ff3b30", font=dict(color="white", size=12, family="Anuphan"),
            bordercolor="#ff3b30", borderwidth=1, borderpad=5, ay=45
        )
        
        fig.update_layout(
            plot_bgcolor='#05070a', paper_bgcolor='#05070a',
            xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=10, t=10, b=10), height=460
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 💡 คู่มือแกะรอยเจ้ามือเพื่อกดออเดอร์")
        st.markdown("""
        <div class="decision-card-sell">
            <h4 style="color:#ff3b30; margin-top:0;">🔍 โครงสร้างพฤติกรรมราคาหน้าเทรด:</h4>
            <p><b>• แท่งที่ 1 - 4 (เทรนด์ขึ้น):</b> ราคาวิ่งฉลุยเขียวสลับเขียวเข้ม ล่อให้เม่ารายย่อยเกิดอาการกลัวตกรถ (FOMO) แล้วแห่แย่งกันซื้อตามที่ยอดดอย</p>
            <p><b>• แท่งที่ 5 (เกิดดาวตก Shooting Star):</b> ราคาเปิดมาทำท่าจะซิ่งต่อ ลากไปสูงลิ่ว แต่เจอแรงทุบกระหน่ำขายจากกระเป๋าวาฬ ทุบราคาร่วงจากฟากฟ้ากลับลงมาปิดกองอยู่ข้างล่าง ทิ้งไส้บนเป็นเข็มยาวเฟี้ยว สัญญาณนี้แปลว่า <b>"เจ้ามือล่อซื้อเสร็จแล้วเทของใส่หน้าทันที"</b></p>
            <p><b>• แท่งที่ 6 (แท่งทุบย้ำสัญญาณ):</b> แท่งแดงใหญ่หล่นโครมตัดเส้น EMA เทรนด์ขึ้นพังทลายลง</p>
            <h4 style="color:#ffffff; margin-top:15px;">🛠️ จังหวะตัดสินใจออก Order (Action):</h4>
            <p style="color:#ff3b30; font-size:16px; font-weight:bold; margin-bottom:0;">👉 วินัยหน้างาน: ห้ามกดเปิดออเดอร์ซื้อสวนเด็ดขาด! และถ้าพี่มีของสะสมมาตั้งแต่ข้างล่าง ให้ทำการ "กดเปิดออเดอร์ขาย (Sell Order)" ล็อกกำไรเงินสดออกมาก่อนทันที ก่อนราคาจะดิ่งลึกกว่าเดิมครับพี่!</p>
        </div>
        """, unsafe_allow_html=True)
