import streamlit as st

# --- 1. SETTING & CYBERPUNK CSS STYLE ---
st.set_page_config(page_title="Candlestick B/S Signals Dashboard", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #0b0e14;
        color: #cbd5e1;
        font-family: 'Anuphan', sans-serif;
    }
    
    /* กล่องสัญญาณซื้อ (Buy) */
    .signal-box-buy {
        background: rgba(0, 255, 102, 0.03);
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #1e293b;
        border-left: 6px solid #00ff66;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 255, 102, 0.05);
    }
    
    /* กล่องสัญญาณขาย (Sell) */
    .signal-box-sell {
        background: rgba(255, 59, 48, 0.03);
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #1e293b;
        border-left: 6px solid #ff3b30;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(255, 59, 48, 0.05);
    }
    
    /* หัวข้อ Badge */
    .badge-buy {
        background: rgba(0, 255, 102, 0.15);
        color: #00ff66;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #00ff66;
    }
    .badge-sell {
        background: rgba(255, 59, 48, 0.15);
        color: #ff3b30;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        border: 1px solid #ff3b30;
    }
    
    /* --- แผงกล่องดำขนาดใหญ่สำหรับแสดงกราฟต่อเนื่อง --- */
    .chart-sequence-card {
        background-color: #05070a;
        border: 2px solid #1e293b;
        border-radius: 12px;
        padding: 30px 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 280px;
        height: 100%;
    }

    /* ตารางโครงสร้างกราฟแท่งเทียน */
    .candle-table {
        border: none !important;
        margin: 0 auto;
        width: auto;
        border-collapse: collapse;
    }
    .candle-table td {
        border: none !important;
        padding: 0 !important;
        text-align: center !important;
    }
    
    /* ตัวครอบจัดตารางเรียงแนวตั้งแยกส่วนไส้-เนื้อ */
    .wick { width: 3px; background-color: #ffffff; margin: 0 auto; }
    .wick-highlight { width: 3px; background-color: #00ff66; margin: 0 auto; box-shadow: 0 0 8px #00ff66; }
    .wick-danger { width: 3px; background-color: #ff3b30; margin: 0 auto; box-shadow: 0 0 8px #ff3b30; }

    /* ซ่อนปุ่มที่ไม่ได้ใช้งาน */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #ffffff; font-weight: 800; margin-top: 10px;'>📊 CANDLESTICK SIGNALS DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 16px;'>จำลองชุดแนวโน้มราคาต่อเนื่อง 6 แท่งเทียนเพื่อวิเคราะห์พฤติกรรมราคา</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 1px solid #1e293b; margin-bottom: 30px;'></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🟢 วิเคราะห์ชุดสัญญาณซื้อ (Buy)", "🔴 วิเคราะห์ชุดสัญญาณขาย (Sell)"])

# -----------------------------------------------------------------
# 🟢 TAB 1: สัญญาณซื้อ (BUY SIGNALS - 6 CANDLES SEQUENCE)
# -----------------------------------------------------------------
with tab1:
    st.markdown("<h3 style='color: #00ff66; margin-bottom: 20px;'>1. ชุดแท่งเทียนการเกิด Hammer (กลับตัวจากขาลงเป็นขาขึ้น)</h3>", unsafe_allow_html=True)
    
    col1_text, col1_img = st.columns([1.3, 1.7])
    with col1_text:
        st.markdown(f"""
        <div class="signal-box-buy" style="height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="color: #ffffff; margin: 0; font-size: 20px;">🔨 พฤติกรรมกราฟแบบ 6 แท่ง</h4>
                <span class="badge-buy">SIGNAL B</span>
            </div>
            <p style="font-size:15px;"><strong>• แท่ง 1-3 (เทขาย):</strong> ราคาร่วงดิ่งลงต่อเนื่อง เกิดแท่งแดงเรียงตัวกันลงมา</p>
            <p style="font-size:15px;"><strong>• แท่งที่ 4 (Hammer):</strong> ราคาเปิดปุ๊บโดนทุบลงไปลึกมาก แต่ท้ายชั่วโมงมีแรงซื้อวาฬดันสวนกลับขึ้นมาปิดด้านบน ทิ้งไส้ล่างยาวเฟี้ยว</p>
            <p style="font-size:15px;"><strong>• แท่งที่ 5-6 (กลับตัวขึ้น):</strong> แรงซื้อไหลเข้าต่อเนื่อง ดันราคาปิดเป็นแท่งเขียวยาวสวนแนวโน้มเดิมขึ้นไป</p>
            <p style="color: #00ff66; font-size:15px; margin-top:10px;"><strong>🎯 จุด Action (B):</strong> เข้าซื้อไม้ที่ 1 เมื่อจบแท่งที่ 5 คอนเฟิร์มเขียวครับ!</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col1_img:
        # สังเกตตรงนี้ครับ เพิ่ม unsafe_allow_html=True เข้าไปแล้วเพื่อให้ฝั่งขวาเรนเดอร์แท่งเทียนสำเร็จ
        st.markdown("""
        <div class="chart-sequence-card">
            <div style="display: flex; gap: 18px; align-items: flex-start; justify-content: center; width: 100%;">
                
                <div style="text-align:center; margin-top: 20px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:30px; height:50px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">1.ลง</div>
                </div>

                <div style="text-align:center; margin-top: 50px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:30px; height:55px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">2.ลงต่อ</div>
                </div>

                <div style="text-align:center; margin-top: 90px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:30px; height:45px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">3.ทุบสุด</div>
                </div>

                <div style="text-align:center; margin-top: 105px;">
                    <table class="candle-table">
                        <tr><td><div style="background-color:#00ff66; width:32px; height:25px; border-radius:3px; box-shadow:0 0 15px rgba(0,255,102,0.8);"></div></td></tr>
                        <tr><td><div class="wick-highlight" style="height:90px;"></div></td></tr>
                    </table>
                    <div style="font-size:13px; color:#00ff66; font-weight:bold; margin-top:8px;">4.ค้อน!</div>
                </div>

                <div style="text-align:center; margin-top: 55px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                        <tr><td><div style="background-color:#00ff66; width:30px; height:65px; border-radius:2px; box-shadow: 0 0 10px rgba(0,255,102,0.2);"></div></td></tr>
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                    </table>
                    <div style="font-size:13px; color:#00ff66; font-weight:bold; margin-top:8px;">5.ซื้อ (B)</div>
                </div>

                <div style="text-align:center; margin-top: 15px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                        <tr><td><div style="background-color:#00ff66; width:30px; height:75px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">6.พุ่งยาว</div>
                </div>

            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------
# 🔴 TAB 2: สัญญาณขาย (SELL SIGNALS - 6 CANDLES SEQUENCE)
# -----------------------------------------------------------------
with tab2:
    st.markdown("<h3 style='color: #ff3b30; margin-bottom: 20px;'>2. ชุดแท่งเทียนการเกิด Shooting Star (กลับตัวจากขาขึ้นเป็นดิ่งลง)</h3>", unsafe_allow_html=True)
    
    col2_text, col2_img = st.columns([1.3, 1.7])
    with col2_text:
        st.markdown(f"""
        <div class="signal-box-sell" style="height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="color: #ffffff; margin: 0; font-size: 20px;">☄️ พฤติกรรมกราฟแบบ 6 แท่ง</h4>
                <span class="badge-sell">SIGNAL S</span>
            </div>
            <p style="font-size:15px;"><strong>• แท่ง 1-3 (ขาขึ้นล่อซื้อ):</strong> ราคาพุ่งทะยานขึ้นต่อเนื่องเป็นแท่งเขียว ดึงดูดรายย่อยให้ไล่ราคาเข้าซื้อ</p>
            <p style="font-size:15px;"><strong>• แท่งที่ 4 (Shooting Star):</strong> ราคาทำท่าพุ่งแรงต่อแต่โดนแรงขายเจ้ามือทุบสวนคว่ำ ดึงราคาลงมาปิดข้างล่าง ทิ้งไส้บนยาวเตือนภัย</p>
            <p style="font-size:15px;"><strong>• แท่งที่ 5-6 (เทกระจาด):</strong> แรงขายชนะขาดเกิดแท่งแดงใหญ่ลากดิ่งเหวทำลายรอบขาขึ้น</p>
            <p style="color: #ff3b30; font-size:15px; margin-top:10px;"><strong>🎯 จุด Action (S):</strong> เจอแท่ง 5 ปิดแดงกินทุนลงมา ต้องตัดสินใจขายออกทันทีครับ!</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2_img:
        st.markdown("""
        <div class="chart-sequence-card">
            <div style="display: flex; gap: 18px; align-items: flex-start; justify-content: center; width: 100%;">
                
                <div style="text-align:center; margin-top: 110px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#00ff66; width:30px; height:45px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">1.ขึ้น</div>
                </div>

                <div style="text-align:center; margin-top: 65px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                        <tr><td><div style="background-color:#00ff66; width:30px; height:55px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">2.ขึ้นต่อ</div>
                </div>

                <div style="text-align:center; margin-top: 35px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#00ff66; width:30px; height:50px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">3.ล่อซื้อ</div>
                </div>

                <div style="text-align:center; margin-top: 10px;">
                    <table class="candle-table">
                        <tr><td><div class="wick-danger" style="height:90px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:32px; height:25px; border-radius:3px; box-shadow:0 0 15px rgba(255,59,48,0.8);"></div></td></tr>
                    </table>
                    <div style="font-size:13px; color:#ff3b30; font-weight:bold; margin-top:8px;">4.ดาวตก!</div>
                </div>

                <div style="text-align:center; margin-top: 45px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:30px; height:65px; border-radius:2px; box-shadow: 0 0 10px rgba(255,59,48,0.2);"></div></td></tr>
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                    </table>
                    <div style="font-size:13px; color:#ff3b30; font-weight:bold; margin-top:8px;">5.ขาย (S)</div>
                </div>

                <div style="text-align:center; margin-top: 95px;">
                    <table class="candle-table">
                        <tr><td><div class="wick" style="height:10px;"></div></td></tr>
                        <tr><td><div style="background-color:#ff3b30; width:30px; height:75px; border-radius:2px;"></div></td></tr>
                        <tr><td><div class="wick" style="height:15px;"></div></td></tr>
                    </table>
                    <div style="font-size:12px; color:#64748b; margin-top:8px;">6.ลงยาว</div>
                </div>

            </div>
        </div>
        """, unsafe_allow_html=True)
