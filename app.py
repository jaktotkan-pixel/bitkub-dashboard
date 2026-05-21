import streamlit as st
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, PointDrawTool, HoverTool
from bokeh.layouts import layout

# --- 1. ตั้งค่าโครงสร้างหน้าจอและ CSS สไตล์ Cyberpunk Neon Pro ---
st.set_page_config(page_title="Coin Average Cost Calculator", layout="wide")

st.markdown("""
<style>
    /* ปรับแต่งพื้นหลังและโทนสีมืดสนิทสไตล์ Cyberpunk */
    .stApp {
        background-color: #060913;
        color: #e2e8f0;
    }
    
    /* custom กล่องสรุปผล Metrics Card ให้เรืองแสง Neon Cyan */
    .neon-card {
        background: linear-gradient(135deg, #0d1224 0%, #151c33 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid #1e2942;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .neon-card:hover {
        border-color: #00FFCC;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.35);
    }
    .neon-lbl { font-size: 13px; color: #64748b; margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
    .neon-val { font-size: 26px; font-weight: bold; color: #ffffff; }
    
    /* custom กล่องอินพุตฝั่งขวา (Expander) ให้ดุดันเข้าธีม */
    .stExpander {
        background-color: #0d1224 !important;
        border: 1px solid #1e2942 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .stExpander summary {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
    .stExpander summary:hover {
        color: #00FFCC !important;
    }
    
    /* custom ตารางแสดงผลฝั่งซื้อ */
    .stTable {
        background-color: #0d1224;
        border: 1px solid #1e2942;
        border-radius: 10px;
        overflow: hidden;
    }
    .stTable th {
        background-color: #151c33 !important;
        color: #00FFCC !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ส่วนหัวข้อหลักเรืองแสงสไตล์ Cyberpunk Pro
st.markdown("<h1 style='text-align: center; color: #00FFCC; font-weight: 900; letter-spacing: 2px; text-shadow: 0 0 12px rgba(0,255,204,0.4); margin-bottom: 5px;'>⚡ CYBERPUNK NEON TRADER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; font-weight: 500; letter-spacing: 0.5px;'>เครื่องคำนวณต้นทุนเฉลี่ย และจำลองกำไรสุทธิ 5 ไม้ละเอียด ( custom 0 สะอาด)</p>", unsafe_allow_html=True)
st.markdown("<div style='border-bottom: 2px solid #1e2942; margin-bottom: 30px; box-shadow: 0 1px 5px rgba(0,255,204,0.1);'></div>", unsafe_allow_html=True)

# 💡 custom Python function สำหรับจัดการเลข 0 ในช่องกรอกตัวเลขแบบ bersih
# (ถ้าไม่มีเศษหรือค่าเป็น 0 โชว์ 2 ตำแหน่ง / ค่าน้อยกว่า 1 โชว์ 8 ตำแหน่งโดยไม่มี 0 ต่อท้าย)
def format_ bersih_ float(value):
    if value == 0:
        return "0.00"
    elif abs(value) < 1.0:
        return f"{value:,.8f}".rstrip('0').rstrip('.') if '.' in f"{value:,.8f}" else f"{value:,.2f}"
    else:
        # ตัดเลข 0 ส่วนเกินฝั่งขวาออกให้เหลือสวยๆ สูงสุดไม่เกิน 8 หรือตามจริง
        formatted = f"{value:,.8f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
            # บังคับให้มีทศนิยมอย่างน้อย 2 ตำแหน่งเพื่อความสวยงามทางบัญชี เช่น 47.55
            if '.' in formatted:
                parts = formatted.split('.')
                if len(parts[1]) < 2:
                    formatted = f"{parts[0]}.{parts[1].ljust(2, '0')}"
            else:
                formatted = f"{formatted}.00"
        return formatted

def safe_float(val_str, default=0.0):
    try:
        return float(val_str.replace(',', '').strip())
    except ValueError:
        return default

# กำหนดอัตราค่าธรรมเนียม Bitkub (0.25%)
FEE_RATE = 0.0025

# สร้าง Layout แยกฝั่งซ้าย (ผลลัพธ์+กราฟวงกลม) และ ฝั่งขวา (INPUT กล่องกรอกข้อมูล bersih)
col_result, col_input = st.columns([1.25, 1])

with col_input:
    st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 15px; letter-spacing: 0.5px;'>📥 1. บันทึกรายการเข้าซื้อ รายไม้</h3>", unsafe_allow_html=True)
    
    # ไม้ที่ 1
    with st.expander("🪵 รายละเอียด ไม้ที่ 1", expanded=True):
        cash_1 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 1 (บาท):", min_value=0.0, value=2600.0, step=100.0, key="c1")
        price_1_raw = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 1 (บาท):", min_value=0.00000001, value=47.55000000, format="%.8f", step=0.00000001, key="p1")
        price_1 = safe_float(format_ bersih_ float(price_1_raw), 47.55) # เคลียร์ 0 สะอาด
    
    # ไม้ที่ 2
    with st.expander("🪵 รายละเอียด ไม้ที่ 2", expanded=False):
        cash_2 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 2 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c2")
        price_2_raw = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 2 (บาท):", min_value=0.00000001, value=45.00000000, format="%.8f", step=0.00000001, key="p2")
        price_2 = safe_float(format_ bersih_ float(price_2_raw), 45.0) # เคลียร์ 0 สะอาด
        
    # ไม้ที่ 3
    with st.expander("🪵 รายละเอียด ไม้ที่ 3", expanded=False):
        cash_3 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 3 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c3")
        price_3_raw = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 3 (บาท):", min_value=0.00000001, value=43.00000000, format="%.8f", step=0.00000001, key="p3")
        price_3 = safe_float(format_ bersih_ float(price_3_raw), 43.0) # เคลียร์ 0 สะอาด
        
    # ไม้ที่ 4
    with st.expander("🪵 รายละเอียด ไม้ที่ 4", expanded=False):
        cash_4 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 4 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c4")
        price_4_raw = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 4 (บาท):", min_value=0.00000001, value=41.00000000, format="%.8f", step=0.00000001, key="p4")
        price_4 = safe_float(format_ bersih_ float(price_4_raw), 41.0) # เคลียร์ 0 สะอาด
        
    # ไม้ที่ 5
    with st.expander("🪵 รายละเอียด ไม้ที่ 5", expanded=False):
        cash_5 = st.number_input("เงินทุนที่ใช้ซื้อ ไม้ 5 (บาท):", min_value=0.0, value=0.0, step=100.0, key="c5")
        price_5_raw = st.number_input("ราคาเหรียญตอนซื้อ ไม้ 5 (บาท):", min_value=0.00000001, value=39.00000000, format="%.8f", step=0.00000001, key="p5")
        price_5 = safe_float(format_ bersih_ float(price_5_raw), 39.0) # เคลียร์ 0 สะอาด

# รวบรวมข้อมูลและคำนวณรายละเอียดแต่ละไม้
raw_data = [
    {"ไม้ที่": 1, "input_cash": cash_1, "buy_price": price_1},
    {"ไม้ที่": 2, "input_cash": cash_2, "buy_price": price_2},
    {"ไม้ที่": 3, "input_cash": cash_3, "buy_price": price_3},
    {"ไม้ที่": 4, "input_cash": cash_4, "buy_price": price_4},
    {"ไม้ที่": 5, "input_cash": cash_5, "buy_price": price_5}
]

rows = []
chart_labels = []
chart_values = []
total_invest_cash = 0.0
total_coins = 0.0
total_buy_fee = 0.0

for item in raw_data:
    if item["input_cash"] > 0:
        fee = item["input_cash"] * FEE_RATE
        net_buy = item["input_cash"] - fee
        coins_received = net_buy / item["buy_price"]
        
        total_invest_cash += item["input_cash"]
        total_buy_fee += fee
        total_coins += coins_received
        
        rows.append({
            "ไม้ที่": f"ไม้ {item['ไม้ที่']}",
            "เงินทุนซื้อ (บาท)": f"{item['input_cash']:,.2f}",
            "ราคาตอนซื้อ": format_ bersih_ float(item['buy_price']), # เคลียร์ 0 สะอาด
            "ค่าธรรมเนียมซื้อ (0.25%)": f"{fee:,.2f}",
            "เหรียญที่ได้รับ": f"{coins_received:,.4f}"
        })
        chart_labels.append(f"ไม้ {item['ไม้ที่']}")
        chart_values.append(item["input_cash"])

with col_result:
    st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 15px; letter-spacing: 0.5px;'>📊 2. ประมวลผลพอร์ตฝั่งซื้อ</h3>", unsafe_allow_html=True)
    if len(rows) > 0:
        df = pd.DataFrame(rows)
        st.table(df)
        
        # คำนวณราคาเฉลี่ยสุทธิ
        avg_cost_per_coin = total_invest_cash / total_coins if total_coins > 0 else 0.0
        
        st.markdown("<h4 style='color: #ffffff; font-size: 15px; font-weight: 600; margin-top: 20px; margin-bottom: 10px; letter-spacing: 0.5px;'>🎯 3. สรุปแดชบอร์ดต้นทุนเฉลี่ยสุทธิ</h4>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>💰 เงินทุนรวมทั้งหมด</div>
                <div class='neon-val'>{total_invest_cash:,.2f} <span style='font-size:13px; color:#64748b;'>THB</span></div>
                <div style='color:#475569; font-size:11px; margin-top:5px; font-weight:500;'>ฟีซื้อรวม {total_buy_fee:,.2f} บ.</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='neon-card'>
                <div class='neon-lbl'>🪙 จำนวนเหรียญในมือ</div>
                <div class='neon-val' style='color:#00E5FF;'>{total_coins:,.4f}</div>
                <div style='color:#475569; font-size:11px; margin-top:5px; font-weight:500;'>เหรียญสุทธิหักฟีแล้ว</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='neon-card' style='border: 1px solid #00FFCC; box-shadow: 0 0 10px rgba(0,255,204,0.15);'>
                <div class='neon-lbl' style='color:#00FFCC; font-weight:bold;'>🏷️ ทุนเฉลี่ย / เหรียญ</div>
                <div class='neon-val' style='color:#00FFCC;'>{format_ bersih_ float(avg_cost_per_coin)} <span style='font-size:13px; color:#00FFCC;'>บ.</span></div>
                <div style='color:#00FFCC; font-size:11px; margin-top:5px; font-weight:600;'>*BREAK-EVEN PRICE</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='border-bottom: 1px solid #1e2942; margin: 20px 0;'></div>", unsafe_allow_html=True)
        
        # 🎯 โซนตั้งเป้าหมายราคาขายเพื่อดูผลกำไร - custom กลับมาเป็น number_input สะอาด
        st.markdown("<h3 style='color: #00FFCC; font-size: 17px; font-weight: 700; margin-bottom: 10px; letter-spacing: 0.5px;'>🎯 4. จำลองเป้าหมายราคาขาย ( custom กลับเป็นพิมพ์ได้ ดึงกราฟได้)</h3>", unsafe_allow_html=True)
        
        target_sell_price_raw = st.number_input(
            "พิมพ์กรอกราคาเหรียญที่ต้องการตั้งขายจริงในกระดาน (บาท):",
            min_value=0.00000001,
            value=float(avg_cost_per_coin),
            format="%.8f",
            step=0.00000001,
            key="target_sell"
        )
        target_sell_price = safe_float(format_ bersih_ float(target_sell_price_raw), avg_cost_per_coin) # เคลียร์ 0 สะอาด

        # ----------------------------------------------------
        # 📈 เครื่องจำลอง (Simulator) กราฟดึงขึ้นลงด้วย Bokeh
        # ----------------------------------------------------
        # 1. เตรียมข้อมูล COLUMN DATA SOURCE
        current_data = {
            'x': ['ราคาปัจจุบัน'],
            'y': [target_sell_price],
            'color': ['#33FF66'] # สีปัจจุบัน
        }
        break_even_data = {
            'x': ['ราคาต้นทุน'],
            'y': [avg_cost_per_coin],
            'color': ['#00FFCC'] # สีต้นทุน
        }

        s1 = ColumnDataSource(data=current_data)
        s2 = ColumnDataSource(data=break_even_data)

        # 2. สร้างโครงสร้าง Bokeh Figure
        p = figure(x_range=['ราคาปัจจุบัน', 'ราคาต้นทุน'], height=350, title=f"เครื่องจำลองเป้าหมายราคาขาย (จุดคุ้มทุนคือ {format_ bersih_ float(avg_cost_per_coin)} บาท)",
                  background_fill_color="#0d1224", border_fill_color="#060913", outline_line_color="#1e2942",
                  x_axis_label="", y_axis_label="ราคาเหรียญ (บาท)", sizing_mode="stretch_width")

        p.axis.axis_line_color = "#334155"
        p.axis.major_label_text_color = "#94a3b8"
        p.grid.grid_line_color = "#1e2942"
        p.title.text_color = "#00FFCC"
        p.title.font_style = "bold"

        # 3. วาดจุด simulator แนวตั้ง (Scatter Plot with point draw)
        render_p1 = p.scatter(x='x', y='y', size=30, source=s1, color='color', line_color='#ffffff', line_width=2)
        render_p2 = p.scatter(x='x', y='y', size=30, source=s2, color='color', line_color='#ffffff', line_width=2)

        # custom hover tool
        p.add_tools(HoverTool(renderers=[render_p1], tooltips=[("ราคาจำลอง", "@y{0.00000000} บ.")]),
                    HoverTool(renderers=[render_p2], tooltips=[("ต้นทุนเฉลี่ย", "@y{0.00000000} บ.")]))

        # custom PointDrawTool: เพื่อให้สามารถ "ดึงจุดขึ้นลงได้" ด้วยเมาส์
        draw_tool = PointDrawTool(renderers=[render_p1], add=False, drag=True) # add=False ห้ามสร้างจุดใหม่, drag=True ให้ดึงจุดได้
        p.add_tools(draw_tool)
        p.toolbar.active_drag = draw_tool # ทำให้ PointDrawTool เป็น default tool

        # 4. วาดเส้นแนวนอน Break-even เพื่อใช้อ้างอิง
        p.line(x_range=['ราคาปัจจุบัน', 'ราคาต้นทุน'], y=[avg_cost_per_coin, avg_cost_per_coin], line_color='#ff3366', line_dash="dashed", line_width=2, legend_label="เส้น break-even")

        st.bokeh_chart(layout([[p]]), use_container_width=True)

        # คำนวณฝั่งขาย
        gross_sell_revenue = total_coins * target_sell_price
        sell_fee = gross_sell_revenue * FEE_RATE
        net_sell_revenue = gross_sell_revenue - sell_fee 
        
        # คำนวณกำไร / ขาดทุน
        pnl_baht = net_sell_revenue - total_invest_cash
        pnl_percent = (pnl_baht / total_invest_cash) * 100
        
        # ปรับสีตามสถานะ กำไรเขียว / ขาดทุนแดง
        status_color = "#00FF66" if pnl_baht >= 0 else "#FF3366"
        status_bg = "rgba(0, 255, 102, 0.03)" if pnl_baht >= 0 else "rgba(255, 51, 102, 0.03)"
        status_sign = "+" if pnl_baht >= 0 else ""
        
        st.markdown(f"""
        <div style='background-color:{status_bg}; padding:22px; border-radius:12px; border: 1px solid #1e2942; border-left:6px solid {status_color}; margin-top:15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);'>
            <h4 style='color:white; margin-top:0px; font-size:16px; margin-bottom:15px;'>📍 สรุปผลลัพธ์ที่ราคาจำลอง {format_ bersih_ float(target_sell_price)} บาท</h4>
            <table style='width:100%; color:white; font-size:15px; border-collapse: collapse;'>
                <tr style='border-bottom: 1px solid #1e2942;'>
                    <td style='padding:8px 0; color:#94a3b8;'>💵 ยอดขายรวม (ก่อนหักค่าฟี):</td>
                    <td style='text-align:right; font-weight:500;'>{gross_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 1px solid #1e2942;'>
                    <td style='padding:8px 0; color:#94a3b8;'>📉 หักค่าธรรมเนียมฝั่งขาย (0.25%):</td>
                    <td style='text-align:right; color:#FF3366;'>- {sell_fee:,.2f} บาท</td>
                </tr>
                <tr style='border-bottom: 2px solid #334155;'>
                    <td style='padding:12px 0; color:#00E5FF; font-weight:bold;'>💰 ยอดเงินสุทธิที่จะได้รับจริง (หักฟีแล้ว):</td>
                    <td style='text-align:right; color:#00E5FF; font-size:19px; font-weight:bold;'>{net_sell_revenue:,.2f} บาท</td>
                </tr>
                <tr>
                    <td style='padding:15px 0 5px 0; color:{status_color}; font-weight:bold; font-size:17px;'>📈 สรุปกำไร / ขาดทุนสุทธิ:</td>
                    <td style='text-align:right; color:{status_color}; font-size:22px; font-weight:bold; padding-top:10px;'>
                        {status_sign}{pnl_percent:,.2f}% ({status_sign}{pnl_baht:,.2f} บาท)
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.info("💡 ระบบพร้อมทำงาน! กรุณากรอกจำนวนเงินทุนใน 'ไม้ที่ 1' ฝั่งซ้ายเพื่อเริ่มคำนวณครับ")
