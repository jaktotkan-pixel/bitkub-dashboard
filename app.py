import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. SETUP PAGE & CYBERPUNK TRADING STYLE ---
st.set_page_config(page_title="Pro Candlestick Simulator", layout="wide")

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
        padding: 22px;
        margin-bottom: 20px;
    }
    
    /* กล่องข้อมูลจุดตัดสินใจฝั่งขาย */
    .decision-card-sell {
        background: rgba(255, 59, 48, 0.02);
        border: 1px solid rgba(255, 59, 48, 0.2);
        border-left: 6px solid #ff3b30;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
    }
    
    /* ซ่อนปุ่ม Deploy ที่ไม่ได้ใช้ */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 800; margin-top: 5px;'>📊 FULL CANDLESTICK PATTERN SIMULATOR</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>ระบบจำลองชุดกราฟเทรดเสมือนจริงทุกรูปแบบยอดฮิต เพื่อฝึกตัดสินใจออก Order ซื้อ (B) / ขาย (S)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 1px solid #1e293b; margin-bottom: 25px;'></div>", unsafe_allow_html=True)


# -----------------------------------------------------------------
# 🗂️ ฟังก์ชันสร้างข้อมูลกราฟจำลอง (เสมือนจริง 8 แท่งตามแต่ละ Pattern)
# -----------------------------------------------------------------
def generate_pattern_data(pattern_name):
    base_time = datetime.now() - timedelta(hours=10)
    times = [base_time + timedelta(hours=i) for i in range(8)]
    
    if pattern_name == "🔨 Hammer (ค้อนกลับตัวขึ้น)":
        opens  = [45.0, 43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0]
        highs  = [45.5, 44.0, 42.2, 41.5, 39.2, 41.0, 42.5, 44.2]
        lows   = [43.0, 41.5, 40.0, 38.0, 34.0, 38.8, 40.5, 42.0]
        closes = [43.5, 42.0, 41.2, 38.5, 39.0, 41.5, 43.0, 44.0]
        action_idx, action_type, text_label = 5, "B", "🎯 BUY Point (ไม้ 1)<br>หลังแท่งเขียวคอนเฟิร์ม"
        
    elif pattern_name == "📐 Inverted Hammer (ค้อนหงายหักศอก)":
        opens  = [50.0, 48.0, 46.5, 44.0, 41.0, 41.5, 44.5, 46.0]
        highs  = [50.5, 48.5, 47.0, 44.5, 45.0, 42.0, 45.5, 47.0]
        lows   = [47.5, 46.0, 43.5, 40.5, 40.8, 41.0, 43.0, 45.0]
        closes = [48.0, 46.5, 44.0, 41.0, 41.5, 44.5, 46.0, 47.5]
        action_idx, action_type, text_label = 5, "B", "🎯 BUY Point (ไม้ 1)<br>เมื่อแท่งคอนเฟิร์มปิดเขียว"
        
    elif pattern_name == "📈 Bullish Engulfing (เขียวใหญ่กลืนกิน)":
        opens  = [35.0, 33.5, 32.0, 30.5, 29.8, 28.0, 32.5, 34.5]
        highs  = [35.5, 34.0, 32.5, 31.0, 30.0, 33.0, 33.0, 35.0]
        lows   = [33.0, 31.5, 30.0, 29.5, 27.5, 27.8, 31.5, 33.0]
        closes = [33.5, 32.0, 30.5, 29.8, 28.0, 32.5, 34.5, 35.0]
        action_idx, action_type, text_label = 5, "B", "🎯 STRONG BUY (B+)<br>เข้าด่วนราคาปิดแท่งกลืนกิน"
        
    elif pattern_name == "🌅 Morning Star (สามสหายกลับตัวขึ้น)":
        # แท่ง 4 แดงใหญ่ -> แท่ง 5 เนื้อสั้นโดจิ -> แท่ง 6 เขียวยาวลากสวน
        opens  = [60.0, 58.5, 57.0, 55.5, 52.0, 49.8, 50.5, 54.0]
        highs  = [60.5, 59.0, 57.5, 56.0, 52.5, 50.5, 54.2, 55.5]
        lows   = [58.0, 56.5, 55.0, 51.5, 49.0, 49.5, 50.0, 53.0]
        closes = [58.5, 57.0, 55.5, 52.0, 49.8, 53.8, 54.0, 55.0]
        action_idx, action_type, text_label = 5, "B", "🎯 BUY Point (ไม้ 1)<br>จบชุดดาวรุ่งสามสหาย"

    elif pattern_name == "☄️ Shooting Star (ดาวตกยอดดอย)":
        opens  = [38.0, 40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5]
        highs  = [40.5, 42.5, 44.0, 45.5, 50.0, 45.2, 42.5, 40.0]
        lows   = [37.8, 40.0, 41.8, 43.5, 44.2, 41.5, 39.0, 37.0]
        closes = [40.2, 42.0, 43.8, 45.0, 44.8, 42.0, 39.5, 37.5]
        action_idx, action_type, text_label = 5, "S", "⚠️ SELL POINT (S)<br>กดขายล็อกกำไร/หนีตาย"
        
    elif pattern_name == "📉 Bearish Engulfing (แดงใหญ่กลืนกิน)":
        opens  = [20.0, 21.5, 23.0, 24.2, 25.0, 26.5, 22.0, 19.5]
        highs  = [21.8, 23.2, 24.5, 25.2, 26.8, 27.0, 22.5, 20.0]
        lows   = [19.8, 21.2, 22.8, 24.0, 24.8, 21.8, 19.0, 18.0]
        closes = [21.5, 23.0, 24.2, 25.0, 26.5, 22.0, 19.5, 18.5]
        action_idx, action_type, text_label = 5, "S", "⚠️ FORCE SELL (S+)<br>คัทลอสทันทีโดนกลืนกิน"
        
    else: # Evening Star (สามสหายกลับตัวลง)
        opens  = [70.0, 72.5, 75.0, 77.5, 80.0, 81.5, 81.0, 76.5]
        highs  = [72.8, 75.3, 77.8, 80.5, 82.0, 82.2, 81.5, 77.0]
        lows   = [69.5, 72.0, 74.5, 77.0, 79.5, 80.8, 76.0, 73.5]
        closes = [72.5, 75.0, 77.5, 80.0, 81.5, 76.5, 74.0, 74.0]
        action_idx, action_type, text_label = 5, "S", "⚠️ SELL POINT (S)<br>แนวโน้มพังถอนทุนด่วน"

    df = pd.DataFrame({'Time': times, 'Open': opens, 'High': highs, 'Low': lows, 'Close': closes})
    df['EMA12'] = df['Close'].ewm(span=3, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=5, adjust=False).mean()
    return df, action_idx, action_type, text_label


# -----------------------------------------------------------------
# 🎛️ แผงแบ่งกลุ่มเมนูใหญ่ (ฝั่งซื้อ VS ฝั่งขาย)
# -----------------------------------------------------------------
main_tab1, main_tab2 = st.tabs(["🟢 หมวดสัญญาณเข้าซื้อ (Buy Signals)", "🔴 หมวดสัญญาณเข้าขาย (Sell Signals)"])

# =================================================================
# 🟢 MAIN TAB 1: สัญญาณเข้าซื้อ (BUY)
# =================================================================
with main_tab1:
    pattern_buy = st.radio(
        "🎯 เลือกรูปแบบแท่งเทียนฝั่งขาขึ้น (Bullish) ที่ต้องการฝึกดูหน้างาน:",
        [
            "🔨 Hammer (ค้อนกลับตัวขึ้น)", 
            "📐 Inverted Hammer (ค้อนหงายหักศอก)", 
            "📈 Bullish Engulfing (เขียวใหญ่กลืนกิน)",
            "🌅 Morning Star (สามสหายกลับตัวขึ้น)"
        ],
        horizontal=True
    )
    
    df, act_idx, act_type, lbl_text = generate_pattern_data(pattern_buy)
    
    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        st.markdown(f"#### 📊 กราฟจำลองตลาดจริง: {pattern_buy}")
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30', name="ราคา"
        )])
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=2)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=2)))
        
        # ปักหมุดลูกศรชี้จุดซื้อ B
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[act_idx], y=df['Low'].iloc[act_idx] - 1.2,
            text=lbl_text, showarrow=True, arrowhead=2, arrowcolor="#00ff66",
            bgcolor="#00ff66", font=dict(color="black", size=12, family="Anuphan"),
            bordercolor="#00ff66", borderwidth=1, borderpad=5, ay=-45
        )
        fig.update_layout(plot_bgcolor='#05070a', paper_bgcolor='#05070a', xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'), margin=dict(l=10, r=10, t=10, b=10), height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 💡 กลยุทธ์ประเมินหน้าเทรดเพื่อกดออเดอร์")
        
        if "Hammer" in pattern_buy:
            st.markdown("""
            <div class="decision-card-buy">
                <h4 style="color:#00ff66; margin-top:0;">🔨 เจาะลึกรูปค้อน (Hammer):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> กราฟไหลลงมาแรงๆ แท่งที่ 5 เปิดมาปุ๊บโดนทุบลากลงลึกทันทีเพื่อบังคับให้รายย่อยยอมคัทลอสล้างพอร์ต แต่สุดท้ายแรงช้อนของวาฬดันสวนขึ้นมาปิดยอดบนสุด ทิ้งไส้ล่างยาวเฟี้ยว</p>
                <p>• <b>เงื่อนไขคอนเฟิร์ม:</b> รอดูดังแท่งที่ 6 ถ้าปิดเป็นแท่งเขียวหนุนชัดเจน แสดงว่าแรงซื้อกลับมาคุมตลาดสมบูรณ์</p>
                <p style="color:#00ff66; font-weight:bold; margin-bottom:0;">🎯 การออก Order (B): กดเข้าซื้อไม้ที่ 1 ที่ราคาปิดของแท่งคอนเฟิร์มสีเขียว (แท่งที่ 6) ได้เลยครับ!</p>
            </div>
            """, unsafe_allow_html=True)
        elif "Inverted Hammer" in pattern_buy:
            st.markdown("""
            <div class="decision-card-buy">
                <h4 style="color:#00ff66; margin-top:0;">📐 เจาะลึกค้อนหงาย (Inverted Hammer):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> เกิดช่วงปลายเทรนด์ขาลง แท่งที่ 5 มีการดันราคาพุ่งขึ้นไปยาวมาก (ไส้บนยาว) เพื่อทดสอบแรงขายด้านบน แม้จะโดนกดลงมาปิดต่ำ แต่เนื้อเทียนยกตัวเปลี่ยนเป็นสีเขียว บ่งบอกว่าฝั่งซื้อเริ่มลองดีส่งสัญญาณยึดพื้นที่</p>
                <p>• <b>เงื่อนไขคอนเฟิร์ม:</b> รอแท่งถัดไปปิดเขียวยกฐานข้ามเส้น EMA 12</p>
                <p style="color:#00ff66; font-weight:bold; margin-bottom:0;">🎯 การออก Order (B): เปิดออเดอร์ซื้อตามน้ำไม้ที่ 1 เมื่อจบบทพิสูจน์แท่งเขียวคอนเฟิร์มครับ</p>
            </div>
            """, unsafe_allow_html=True)
        elif "Engulfing" in pattern_buy:
            st.markdown("""
            <div class="decision-card-buy">
                <h4 style="color:#00ff66; margin-top:0;">📈 เจาะลึกเขียวกลืนกิน (Bullish Engulfing):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> กราฟกำลังซึมลงอยู่ดีๆ แท่งที่ 6 ก็มีแรงซื้อถล่มเข้ามามหาศาล ลากราคาเป็นแท่งเขียวยาวใหญ่ ร่างกายสูงใหญ่อ้วนท้วนกลืนกินเนื้อเทียนสีแดงของแท่งที่ 5 จนมิดจมหายไป</p>
                <p>• <b>เงื่อนไขคอนเฟิร์ม:</b> ไม่ต้องรอแท่งอื่น คอนเฟิร์มจบในตัวเองทันทีเพราะแรงซื้อชนะฝั่งขายแบบเด็ดขาด 100%</p>
                <p style="color:#00ff66; font-weight:bold; margin-bottom:0;">🎯 การออก Order (B): จังหวะนี้สัญญาณแรงจัด (B+) กดเปิดออเดอร์ซื้อ Market Order ทันทีที่ราคาปิดแท่งเขียวยักษ์นี้ครับพี่!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="decision-card-buy">
                <h4 style="color:#00ff66; margin-top:0;">🌅 เจาะลึกดาวรุ่งสามสหาย (Morning Star):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> ประกอบด้วย 3 แท่งเทียนในตำนาน (แดงใหญ่เทลงมา -> เกิดแท่งเล็กๆ โดจิหมดแรงวิ่ง -> เกิดแท่งเขียวยาวดีดสวนข้ามกึ่งกลางแท่งแดงแรก) สัญญาณนี้แสดงถึงการเปลี่ยนขั้วอำนาจตลาดจากลงเป็นขึ้นถาวร</p>
                <p>• <b>เงื่อนไขคอนเฟิร์ม:</b> สมบูรณ์แบบเมื่อแท่งสีเขียวที่สามปิดตัวอย่างทรงพลัง</p>
                <p style="color:#00ff66; font-weight:bold; margin-bottom:0;">🎯 การออก Order (B): ออกออเดอร์ซื้อไม้ 1 หรืออัดเพิ่มไม้ 2 ได้ทันทีหลังจากเห็นสัญญาณสามสหายนี้ฟอร์มตัวเสร็จครับ</p>
            </div>
            """, unsafe_allow_html=True)

# =================================================================
# 🔴 MAIN TAB 2: สัญญาณเข้าขาย (SELL)
# =================================================================
with main_tab2:
    pattern_sell = st.radio(
        "⚠️ เลือกรูปแบบแท่งเทียนฝั่งขาลง (Bearish) ที่ต้องการฝึกดูหน้างาน:",
        [
            "☄️ Shooting Star (ดาวตกยอดดอย)", 
            "📉 Bearish Engulfing (แดงใหญ่กลืนกิน)", 
            "🌌 Evening Star (สามสหายกลับตัวลง)"
        ],
        horizontal=True
    )
    
    df, act_idx, act_type, lbl_text = generate_pattern_data(pattern_sell)
    
    col1, col2 = st.columns([1.8, 1.2])
    with col1:
        st.markdown(f"#### 📊 กราฟจำลองตลาดจริง: {pattern_sell}")
        fig = go.Figure(data=[go.Candlestick(
            x=df['Time'].dt.strftime('%H:%M'),
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00ff66', decreasing_line_color='#ff3b30', name="ราคา"
        )])
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA12'], mode='lines', name='EMA 12 (เขียว)', line=dict(color='#00ff66', width=2)))
        fig.add_trace(go.Scatter(x=df['Time'].dt.strftime('%H:%M'), y=df['EMA26'], mode='lines', name='EMA 26 (ส้ม)', line=dict(color='#ff9f0a', width=2)))
        
        # ปักหมุดลูกศรชี้จุดขาย S
        fig.add_annotation(
            x=df['Time'].dt.strftime('%H:%M').iloc[act_idx], y=df['High'].iloc[act_idx] + 1.2,
            text=lbl_text, showarrow=True, arrowhead=2, arrowcolor="#ff3b30",
            bgcolor="#ff3b30", font=dict(color="white", size=12, family="Anuphan"),
            bordercolor="#ff3b30", borderwidth=1, borderpad=5, ay=45
        )
        fig.update_layout(plot_bgcolor='#05070a', paper_bgcolor='#05070a', xaxis_rangeslider_visible=False, font=dict(color='#cbd5e1'), margin=dict(l=10, r=10, t=10, b=10), height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 💡 กลยุทธ์ประเมินหน้าเทรดเพื่อกดออเดอร์")
        
        if "Shooting Star" in pattern_sell:
            st.markdown("""
            <div class="decision-card-sell">
                <h4 style="color:#ff3b30; margin-top:0;">☄️ เจาะลึกดาวตก (Shooting Star):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> ราคาพุ่งขึ้นร้อนแรงติดต่อกันหลายชั่วโมง ล่อให้รายย่อยกระโดดโฟโมตาม แท่งที่ 5 เปิดมาราคาพุ่งปรี๊ดขึ้นฟ้า ก่อนจะโดนวาฬใหญ่ตั้งป้อมทุบสวนแจกของโครมเดียวร่วงมาปิดข้างล่าง ทิ้งไส้บนยาวดั่งเสาอากาศ</p>
                <p>• <b>เงื่อนไขตัดสินใจ:</b> เกิดบริเวณแนวต้านยอดยอดดอย หรือราคาฉีกห่างเส้น EMA 26 มากเกินไป</p>
                <p style="color:#ff3b30; font-weight:bold; margin-bottom:0;">🎯 การออก Order (S): จังหวะนี้อันตรายสุดขีด ให้ "กดขายล็อกกำไร (Sell Order)" ออกมาถือเงินสดทันทีเพื่อความปลอดภัยครับพี่!</p>
            </div>
            """, unsafe_allow_html=True)
        elif "Engulfing" in pattern_sell:
            st.markdown("""
            <div class="decision-card-sell">
                <h4 style="color:#ff3b30; margin-top:0;">📉 เจาะลึกแดงกลืนกิน (Bearish Engulfing):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> ราคาลอยอยู่ด้านบนจู่ๆ เกิดแท่งแดงยักษ์เทกระจาดลากดิ่งลงมายาวมาก ตัวเนื้อเทียนหนาใหญ่กลืนกินแท่งเขียวก่อนหน้าจมมิดหายไปอย่างไร้ร่องรอย บ่งบอกว่าเจ้ามือล้างพอร์ตหนีตายกันหมดแล้ว</p>
                <p>• <b>เงื่อนไขตัดสินใจ:</b> แรงขายคุมตลาดเบ็ดเสร็จ กราฟพังแนวรับทันที</p>
                <p style="color:#ff3b30; font-weight:bold; margin-bottom:0;">🎯 การออก Order (S): สัญญาณนี้หนีตายด่วน (S+) มีออเดอร์ฝั่งซื้อค้างอยู่ให้กดสั่งขายล้างพอร์ตคัทลอสทิ้งทุกราคา ห้ามฝืนถัวเด็ดขาด!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="decision-card-sell">
                <h4 style="color:#ff3b30; margin-top:0;">🌌 เจาะลึกดาวดับสามสหาย (Evening Star):</h4>
                <p>• <b>พฤติกรรมเจ้ามือ:</b> รูปแบบแดนสนธยาตรงข้ามกับ Morning Star (แท่งเขียวยาวขึ้นมา -> แท่งโดจิเล็กๆ หมดแรงวิ่งที่ยอดดอย -> แท่งแดงยาวทุบดิ่งสวนลงมา) เป็นการจบรอบขาขึ้นอย่างเป็นทางการ</p>
                <p>• <b>เงื่อนไขตัดสินใจ:</b> เมื่อแท่งแดงที่สามลากกินลึกเกินกึ่งกลางของแท่งเขียวแรก</p>
                <p style="color:#ff3b30; font-weight:bold; margin-bottom:0;">🎯 การออก Order (S): ยืนยันจังหวะเปลี่ยนเป็นเทรนด์ขาลง ให้กดเปิดออเดอร์ขายถอนทุนและล็อกกำไรออกมาก่อนกราฟจะไหลลึกครับ</p>
            </div>
            """, unsafe_allow_html=True)
