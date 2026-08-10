import streamlit as st
import re
import json
import copy
from pathlib import Path
import base64
import streamlit.components.v1 as components

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="ZTE OLT & PC Command Center", layout="wide")

# --- ฟังก์ชันตรวจสอบรหัสผ่าน ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "jakntkan":  # <-- เปลี่ยนรหัสผ่านตรงนี้
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # ไม่เก็บบันทึกรหัสผ่านไว้ใน memory
        else:
            st.session_state["password_correct"] = False

    # หากผ่านการตรวจสอบแล้ว ให้คืนค่า True เพื่อให้แสดงผลหน้าเว็บปกติ
    if st.session_state.get("password_correct", False):
        return True

    # หากยังไม่กรอกรหัส หรือกรอกผิด ให้แสดงหน้าต่างให้กรอกรหัสผ่าน
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;600;700&family=JetBrains+Mono:wght@600&display=swap');
        .stApp {
            background-color: #030503;
            background-image: repeating-linear-gradient(180deg, rgba(51,255,119,0.018) 0px, rgba(51,255,119,0.018) 1px, transparent 1px, transparent 3px);
        }
        .lock-title {
            text-align: center; margin-top: 12vh;
            font-family: 'JetBrains Mono', monospace;
            color: #7bffa0; font-weight: 700; font-size: 20px;
            text-shadow: 0 0 10px rgba(51,255,119,0.35);
        }
        .lock-sub {
            text-align: center; color: #35603f; font-family: 'JetBrains Mono', monospace;
            font-size: 12.5px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 24px;
        }
    </style>
    <div class="lock-title">&gt; AUTH REQUIRED — กรุณาใส่รหัสผ่านเพื่อเข้าใช้งานระบบ</div>
    <div class="lock-sub">root@kri-noc :: zte olt &amp; pc command center</div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1.2, 1])
    with col_b:
        st.text_input(
            "รหัสผ่าน", type="password", on_change=password_entered, key="password"
        )

        if "password_correct" in st.session_state:
            st.error("😕 รหัสผ่านไม่ถูกต้อง ลองใหม่อีกครั้งครับ")

    return False


# ครอบโค้ดหลักทั้งหมดด้วยฟังก์ชันเช็ครหัสผ่าน
if not check_password():
    st.stop()  # หยุดการทำงานของหน้าเว็บไว้ตรงนี้หากยังไม่ใส่รหัสผ่านที่ถูกต้อง 


# =================================================================
# 🎨 ธีม "Trading Terminal" — พื้นหลังเข้ม ตัวหนังสือคมชัด อ่านง่าย
# =================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-0: #030503;
        --bg-1: #070a07;
        --bg-2: #0c110c;
        --bg-3: #121a12;
        --line: #1c3320;
        --line-soft: #142616;
        --text-hi: #7bffa0;
        --text-body: #4fa868;
        --text-lo: #35603f;
        --up: #33ff77;
        --up-dim: rgba(51, 255, 119, 0.10);
        --down: #ff5c5c;
        --down-dim: rgba(255, 92, 92, 0.12);
        --amber: #ffcc33;
        --blue: #66e0ff;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans Thai', 'JetBrains Mono', monospace; }

    /* พื้นหลังดำสนิทแบบจอเทอร์มินัล + สแกนไลน์บางๆ ให้ฟีล CRT */
    .stApp {
        background-color: var(--bg-0);
        color: var(--text-body);
        background-image:
            repeating-linear-gradient(180deg, rgba(51,255,119,0.018) 0px, rgba(51,255,119,0.018) 1px, transparent 1px, transparent 3px),
            radial-gradient(ellipse 100% 60% at 50% -10%, rgba(51,255,119,0.05) 0%, transparent 60%);
    }
    .block-container { padding-top: 1.6rem; max-width: 1200px; }

    /* ตัวหนังสือทั่วไปโทนเขียวฟอสฟอร์ ระดับกลาง อ่านสบายตา ไม่จ้าเกินไป */
    p, span, label, li, div { color: var(--text-body); }
    h1, h2, h3, h4, strong, b { color: var(--text-hi) !important; }
    .stCaption, [data-testid="stCaptionContainer"] { color: var(--text-lo) !important; }
    [data-testid="stMarkdownContainer"] p { color: var(--text-body); }

    /* Inline code (ตัวอักษรที่ครอบด้วย backtick ในข้อความ markdown เช่นค่าระยะทาง, IP ฯลฯ) */
    [data-testid="stMarkdownContainer"] code {
        background-color: #050a06 !important;
        color: var(--up) !important;
        border: 1px solid var(--line) !important;
        border-radius: 4px !important;
        padding: 1px 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.92em !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] code {
        background-color: #050a06 !important;
        color: var(--up) !important;
    }

    h1 {
        font-family: 'JetBrains Mono', monospace; letter-spacing: -0.5px;
        text-shadow: 0 0 10px rgba(51,255,119,0.35);
    }
    h2 {
        color: var(--text-hi) !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 20px;
        margin-top: 6px; margin-bottom: 4px;
        padding-left: 4px;
    }
    h2::before { content: "$ "; color: var(--text-lo); }
    h3 {
        color: var(--text-hi) !important;
        font-weight: 600; font-size: 14.5px;
        text-transform: uppercase; letter-spacing: 0.6px;
        border-bottom: 1px dashed var(--line);
        padding-bottom: 8px; margin-top: 22px;
        font-family: 'JetBrains Mono', monospace;
    }
    h3::before { content: "> "; color: var(--up); }

    /* กล่องข้อความ Code Block แบบคอนโซลดำสนิท ตัวหนังสือเขียวสว่าง */
    .stCodeBlock,
    div[data-testid="stCodeBlock"],
    div[data-testid="stCode"],
    div[data-testid="stCodeBlock"] > div,
    div[data-testid="stCode"] > div,
    .stCodeBlock pre,
    div[data-testid="stCodeBlock"] pre,
    div[data-testid="stCode"] pre {
        background-color: #050a06 !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
        box-shadow: inset 0 0 12px rgba(51,255,119,0.04);
    }
    .stCodeBlock code,
    div[data-testid="stCodeBlock"] code,
    div[data-testid="stCode"] code,
    .stCodeBlock pre code,
    div[data-testid="stCodeBlock"] pre code,
    div[data-testid="stCode"] pre code,
    .stCodeBlock span,
    div[data-testid="stCodeBlock"] span,
    div[data-testid="stCode"] span {
        background-color: transparent !important;
        color: var(--up) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13.5px !important;
    }
    /* ปุ่ม Copy มุมขวาบนของ Code Block ให้กลืนกับพื้นหลังดำ */
    .stCodeBlock button,
    div[data-testid="stCodeBlock"] button,
    div[data-testid="stCode"] button {
        background-color: #050a06 !important;
        color: var(--up) !important;
    }

    /* Highlight คำค้นหา แบบสีอำพันเรืองแสงบนพื้นดำ */
    mark.highlight {
        background-color: var(--amber);
        color: #1a1300;
        padding: 1px 6px;
        border-radius: 2px;
        font-weight: 700;
    }

    /* ===== SIDEBAR: กระดานฝั่งซ้ายดำสนิทกว่าเนื้อหา ===== */
    [data-testid="stSidebar"] {
        background-color: var(--bg-1);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { color: var(--text-body); }
    [data-testid="stSidebar"] strong, [data-testid="stSidebar"] b { color: var(--text-hi); }
    [data-testid="stSidebar"] h2 {
        font-size: 12.5px; letter-spacing: 1.5px; text-transform: uppercase;
        color: var(--text-lo) !important; padding-left: 0;
    }
    [data-testid="stSidebar"] h2::before { content: ""; }
    [data-testid="stSidebar"] a { color: var(--blue) !important; text-decoration: none; }
    [data-testid="stSidebar"] a:hover { text-decoration: underline; }

    /* Expander ใน Sidebar ให้ดูเป็นการ์ดโมดูลคอนโซล */
    [data-testid="stSidebar"] details {
        background-color: var(--bg-2);
        border: 1px solid var(--line-soft);
        border-radius: 6px;
        margin-bottom: 8px;
        overflow: hidden;
    }
    [data-testid="stSidebar"] summary {
        font-weight: 600; font-size: 13.5px;
        font-family: 'JetBrains Mono', monospace;
        padding: 2px 0;
    }

    /* ปุ่มตัวเลือกหมวดหมู่ (radio) ให้ดูเหมือนเมนูคำสั่งคอนโซล */
    [data-testid="stSidebar"] .stRadio > div { gap: 2px; }
    [data-testid="stSidebar"] .stRadio label {
        border: 1px solid transparent;
        border-radius: 4px;
        padding: 7px 8px !important;
        width: 100%;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        transition: background-color 0.12s ease, border-color 0.12s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: var(--up-dim);
        border-color: var(--line);
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio input:checked + div {
        color: var(--up) !important;
        text-shadow: 0 0 6px rgba(51,255,119,0.4);
    }

    /* Text input ทั่วทั้งแอป */
    .stTextInput input, [data-testid="stSidebar"] .stTextInput input {
        background-color: #050a06 !important;
        color: var(--up) !important;
        caret-color: var(--up) !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace;
    }
    .stTextInput input:focus { border-color: var(--up) !important; box-shadow: 0 0 0 1px var(--up) !important; }
    .stTextInput input::placeholder { color: var(--text-lo) !important; }

    /* ===== Selectbox (เลือกไฟล์ PDF ฯลฯ) ===== */
    div[data-baseweb="select"] > div {
        background-color: #050a06 !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
        color: var(--up) !important;
    }
    div[data-baseweb="select"] * { color: var(--up) !important; fill: var(--up) !important; }
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: var(--bg-2) !important;
        border: 1px solid var(--line) !important;
    }
    li[role="option"] { background-color: var(--bg-2) !important; color: var(--text-body) !important; }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: var(--up-dim) !important; color: var(--up) !important;
    }

    /* ===== File uploader (เพิ่ม PDF เข้าคลัง) ===== */
    [data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section {
        background-color: var(--bg-2) !important;
        border: 1px dashed var(--line) !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploader"] section * {
        color: var(--text-body) !important;
    }
    [data-testid="stFileUploaderDropzone"] button, [data-testid="stFileUploader"] section button {
        background-color: var(--bg-3) !important;
        color: var(--text-hi) !important;
        border: 1px solid var(--line) !important;
    }

    /* ===== Checkbox label ===== */
    [data-testid="stCheckbox"] label p, [data-testid="stCheckbox"] span {
        color: var(--text-body) !important;
    }

    /* ปุ่มหลัก */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stButton"] button,
    [data-testid="baseButton-secondary"],
    [data-testid="stBaseButton-secondary"] {
        background-color: var(--bg-2) !important;
        color: var(--text-hi) !important;
        border: 1px solid var(--line) !important;
        border-radius: 6px !important;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .stButton > button[kind="primary"],
    [data-testid="baseButton-primary"],
    [data-testid="stBaseButton-primary"] {
        background-color: var(--up) !important;
        color: #041006 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover { background-color: #58ff93 !important; }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--up); color: var(--up);
    }

    /* ===== ปุ่มลบ (🗑️) ทุกหัวข้อ — พื้นดำเดียวกับ Dashboard ขอบ/ไอคอนสีแดงเพื่อสื่อว่าเป็นการลบ ===== */
    [class*="st-key-del_"] button {
        background-color: var(--bg-0) !important;
        border: 1px solid #ff5c5c !important;
        color: #ff5c5c !important;
        border-radius: 6px !important;
    }
    [class*="st-key-del_"] button:hover {
        background-color: rgba(255, 92, 92, 0.12) !important;
        border-color: #ff7a7a !important;
        color: #ff7a7a !important;
    }
    [class*="st-key-del_"] button p {
        color: inherit !important;
    }

    /* Alert boxes (success / warning / error / info) โทนดำ */
    div[data-testid="stAlert"] { border-radius: 6px; border: 1px solid var(--line); }

    /* เส้นแบ่ง */
    hr { border-color: var(--line) !important; }

    /* Expander บนหน้าหลัก (คลังเอกสาร PDF) */
    div[data-testid="stExpander"] {
        background-color: var(--bg-1);
        border: 1px solid var(--line);
        border-radius: 8px;
    }

    /* ===== Ticker แถบสรุปสถานะด้านบน สไตล์ terminal readout ===== */
    .ticker-wrap {
        display: flex; flex-wrap: wrap; gap: 0;
        background-color: var(--bg-1);
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
        margin: 14px 0 20px 0;
    }
    .ticker-item {
        flex: 1 1 150px;
        padding: 12px 18px;
        border-right: 1px dashed var(--line);
        min-width: 140px;
    }
    .ticker-item:last-child { border-right: none; }
    .ticker-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px; letter-spacing: 1.2px; text-transform: uppercase;
        color: var(--text-lo); margin-bottom: 4px;
    }
    .ticker-label::before { content: "// "; }
    .ticker-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px; font-weight: 700; color: var(--text-hi);
        display: flex; align-items: baseline; gap: 6px;
    }
    .ticker-value.up { color: var(--up); text-shadow: 0 0 8px rgba(51,255,119,0.45); }
    .ticker-unit { font-size: 11px; color: var(--text-lo); font-weight: 500; }
    .live-dot {
        display: inline-block; width: 7px; height: 7px; border-radius: 50%;
        background-color: var(--up); margin-right: 6px;
        box-shadow: 0 0 0 0 rgba(51,255,119, 0.6);
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(51,255,119, 0.5); }
        70%  { box-shadow: 0 0 0 6px rgba(51,255,119, 0); }
        100% { box-shadow: 0 0 0 0 rgba(51,255,119, 0); }
    }

    /* เคอร์เซอร์กระพริบท้ายหัวข้อหลัก — จุดเด่นของธีมนี้ */
    .blink-cursor {
        display: inline-block; width: 10px; height: 1.05em;
        background-color: var(--up); margin-left: 4px; vertical-align: text-bottom;
        animation: blink 1s steps(1) infinite;
        box-shadow: 0 0 8px rgba(51,255,119,0.6);
    }
    @keyframes blink { 50% { opacity: 0; } }

    /* ป้ายชื่อคำสั่ง */
    .cmd-label {
        font-size: 13.5px; font-weight: 600; color: var(--text-hi);
        font-family: 'JetBrains Mono', monospace;
        padding-left: 4px;
        margin: 14px 0 4px 0;
    }
    .cmd-label::before { content: "λ "; color: var(--up); }

    /* ซ่อนปุ่มที่ไม่จำเป็น */
    .stDeployButton { display:none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ===== แถบ Header ด้านบนสุดของ Streamlit (Share / ดาว / ดินสอ / GitHub) ===== */
    [data-testid="stHeader"] {
        background-color: var(--bg-0) !important;
        border-bottom: 1px solid var(--line);
    }
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stStatusWidget"],
    [data-testid="stDecoration"] {
        background-color: transparent !important;
    }
    [data-testid="stHeader"] *,
    [data-testid="stToolbarActions"] * {
        color: var(--text-hi) !important;
        fill: var(--text-hi) !important;
    }
    [data-testid="stToolbarActions"] button:hover,
    [data-testid="stHeader"] button:hover {
        background-color: var(--up-dim) !important;
    }
    [data-testid="stHeader"] a {
        color: var(--text-hi) !important;
    }
</style>
""", unsafe_allow_html=True)


# ฟังก์ชันทำ Highlight แถบสีเหลือง
def highlight_text(text, keyword):
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f'<mark class="highlight">{m.group(0)}</mark>', str(text))


# =================================================================
# 🗃️ ระบบจัดการข้อมูลแบบแก้ไขได้ (เพิ่ม/ลบ) สำหรับหัวข้อต่างๆ ใน Sidebar
#    เช่น Web, ระยะสาย Optic, เลขวงจร, ที่อยู่, IP Phone, SecureCRT
# =================================================================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def load_section_data(filename, seed):
    """โหลดข้อมูลของหัวข้อจากไฟล์ JSON ถ้ายังไม่มีไฟล์จะสร้างจากข้อมูลตั้งต้น (seed)"""
    path = DATA_DIR / filename
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    seed_copy = copy.deepcopy(seed)
    save_section_data(filename, seed_copy)
    return seed_copy


def save_section_data(filename, data):
    """บันทึกข้อมูลของหัวข้อลงไฟล์ JSON"""
    (DATA_DIR / filename).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def render_delete_button(filename, data, idx, key):
    """ปุ่มลบรายการที่ idx แล้วบันทึกและรีเฟรชหน้า"""
    if st.button("🗑️", key=key, help="ลบรายการนี้"):
        data.pop(idx)
        save_section_data(filename, data)
        st.rerun()


def render_web_section(filename, seed):
    """หัวข้อ 🌐 Web: เพิ่ม/ลบลิงก์เว็บได้"""
    data = load_section_data(filename, seed)

    with st.form("add_web_form", clear_on_submit=True):
        name = st.text_input("ชื่อเว็บ", key="web_name_input")
        url = st.text_input("URL", key="web_url_input", placeholder="https://...")
        submitted = st.form_submit_button("➕ เพิ่มลิงก์", use_container_width=True)
        if submitted:
            if not name.strip() or not url.strip():
                st.warning("กรุณากรอกทั้งชื่อเว็บและ URL")
            else:
                clean_url = url.strip()
                if not clean_url.startswith(("http://", "https://")):
                    clean_url = "https://" + clean_url
                data.append({"name": name.strip(), "url": clean_url})
                save_section_data(filename, data)
                st.rerun()

    st.markdown("---")
    if not data:
        st.caption("ยังไม่มีลิงก์เว็บ")
    for idx, item in enumerate(data):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.markdown(f"🔗 [{item['name']}]({item['url']})")
        with col_b:
            render_delete_button(filename, data, idx, key=f"del_web_{idx}")
    return data


def render_ofc_section(filename, seed):
    """หัวข้อ 📏 ระยะสาย Optic: เพิ่ม/ลบ/ค้นหาเส้นทางได้"""
    data = load_section_data(filename, seed)

    with st.form("add_ofc_form", clear_on_submit=True):
        route = st.text_input("เส้นทาง (เช่น จุด A - จุด B)", key="ofc_route_input")
        distance = st.text_input("ระยะทาง (เช่น 12.3 km)", key="ofc_distance_input")
        note = st.text_input("หมายเหตุ (ถ้ามี)", key="ofc_note_input")
        submitted = st.form_submit_button("➕ เพิ่มเส้นทาง", use_container_width=True)
        if submitted:
            if not route.strip() or not distance.strip():
                st.warning("กรุณากรอกเส้นทางและระยะทาง")
            else:
                data.append({
                    "route": route.strip(),
                    "distance": distance.strip(),
                    "note": note.strip() or "-",
                })
                save_section_data(filename, data)
                st.rerun()

    st.markdown("---")
    st.markdown("#### 🛠️ ข้อมูลระยะสาย OFC หน้างาน")
    search_ofc = st.text_input("🔍 ค้นหาเส้นทางสาย OFC:", "", key="search_ofc_sidebar").strip().lower()

    filtered = [
        (idx, item) for idx, item in enumerate(data)
        if search_ofc in item["route"].lower()
        or search_ofc in item["distance"].lower()
        or search_ofc in item.get("note", "").lower()
    ]

    if not filtered:
        st.write("ไม่พบข้อมูลเส้นทางที่ค้นหา")

    for idx, item in filtered:
        col_a, col_b = st.columns([5, 1])
        with col_a:
            if item.get("note", "-") != "-":
                st.markdown(f"• **{item['route']}** : `{item['distance']}`\n  *(หมายเหตุ: {item['note']})*")
            else:
                st.markdown(f"• **{item['route']}** : `{item['distance']}`")
        with col_b:
            render_delete_button(filename, data, idx, key=f"del_ofc_{idx}")
    return data


def render_circuit_section(filename, seed):
    """หัวข้อ 🆔 เลขวงจรลูกค้า: เพิ่ม/ลบได้"""
    data = load_section_data(filename, seed)

    with st.form("add_circuit_form", clear_on_submit=True):
        code = st.text_input("เลขวงจร", key="circuit_code_input")
        owner = st.text_input("ชื่อเจ้าของ/หมายเหตุ", key="circuit_owner_input")
        submitted = st.form_submit_button("➕ เพิ่มวงจร", use_container_width=True)
        if submitted:
            if not code.strip():
                st.warning("กรุณากรอกเลขวงจร")
            else:
                data.append({"code": code.strip(), "owner": owner.strip()})
                save_section_data(filename, data)
                st.rerun()

    st.markdown("---")
    if not data:
        st.caption("ยังไม่มีข้อมูล")
    for idx, item in enumerate(data):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.markdown(f"• `{item['code']}` : {item['owner']}")
        with col_b:
            render_delete_button(filename, data, idx, key=f"del_circuit_{idx}")
    return data


def render_address_section(filename, seed):
    """หัวข้อ 📍 ที่อยู่ NT: เพิ่ม/ลบได้"""
    data = load_section_data(filename, seed)

    with st.form("add_address_form", clear_on_submit=True):
        title = st.text_input("ชื่อสถานที่", key="addr_title_input")
        detail = st.text_area("รายละเอียดที่อยู่", key="addr_detail_input", height=80)
        submitted = st.form_submit_button("➕ เพิ่มที่อยู่", use_container_width=True)
        if submitted:
            if not title.strip() or not detail.strip():
                st.warning("กรุณากรอกชื่อสถานที่และรายละเอียด")
            else:
                data.append({"title": title.strip(), "detail": detail.strip()})
                save_section_data(filename, data)
                st.rerun()

    st.markdown("---")
    if not data:
        st.caption("ยังไม่มีข้อมูล")
    for idx, item in enumerate(data):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.markdown(f"**{item['title']}:**\n{item['detail']}")
        with col_b:
            render_delete_button(filename, data, idx, key=f"del_addr_{idx}")
        st.markdown("---")
    return data


def render_simple_value_section(filename, seed, value_label, form_prefix):
    """หัวข้อแบบค่า + หมายเหตุ (ใช้กับ IP Phone และ SecureCRT): เพิ่ม/ลบได้"""
    data = load_section_data(filename, seed)

    with st.form(f"add_{form_prefix}_form", clear_on_submit=True):
        value = st.text_input(value_label, key=f"{form_prefix}_value_input")
        note = st.text_input("หมายเหตุ (ถ้ามี)", key=f"{form_prefix}_note_input")
        submitted = st.form_submit_button("➕ เพิ่ม", use_container_width=True)
        if submitted:
            if not value.strip():
                st.warning("กรุณากรอกข้อมูล")
            else:
                data.append({"value": value.strip(), "note": note.strip()})
                save_section_data(filename, data)
                st.rerun()

    st.markdown("---")
    if not data:
        st.caption("ยังไม่มีข้อมูล")
    for idx, item in enumerate(data):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            note_txt = f" ({item['note']})" if item.get("note") else ""
            st.markdown(f"• `{item['value']}`{note_txt}")
        with col_b:
            render_delete_button(filename, data, idx, key=f"del_{form_prefix}_{idx}")
    return data


# =================================================================
# 📚 คลังเอกสาร PDF บน Dashboard
# =================================================================
PDF_LIBRARY_DIR = Path("pdf_library")
PDF_LIBRARY_DIR.mkdir(exist_ok=True)


def get_pdf_files():
    """คืนรายการ PDF ที่บันทึกไว้ในคลัง"""
    return sorted(PDF_LIBRARY_DIR.glob("*.pdf"), key=lambda file: file.name.lower())


def show_pdf_library():
    """แสดงส่วนเพิ่มไฟล์ เปิดดู และดาวน์โหลดเอกสาร PDF"""
    with st.expander("📚 คลังเอกสาร PDF", expanded=False):
        st.caption("เพิ่มคู่มือหรือเอกสารที่ต้องใช้ร่วมกันบน Dashboard")

        uploaded_pdf = st.file_uploader(
            "เลือกไฟล์ PDF เพื่อเพิ่มเข้าคลัง",
            type=["pdf"],
            key="pdf_library_uploader"
        )

        if uploaded_pdf is not None:
            safe_name = Path(uploaded_pdf.name).name
            save_path = PDF_LIBRARY_DIR / safe_name

            if save_path.exists():
                st.warning(f"มีไฟล์ชื่อ {safe_name} อยู่แล้ว การบันทึกจะเขียนทับไฟล์เดิม")

            if st.button("💾 บันทึกไฟล์ PDF", type="primary", key="save_pdf_library"):
                save_path.write_bytes(uploaded_pdf.getvalue())
                st.success(f"บันทึกไฟล์ “{safe_name}” เรียบร้อยแล้ว")
                st.rerun()

        pdf_files = get_pdf_files()
        if not pdf_files:
            st.info("ยังไม่มีเอกสาร PDF ในคลัง")
            return

        selected_pdf = st.selectbox(
            "เลือกเอกสาร",
            pdf_files,
            format_func=lambda file: file.name,
            key="pdf_library_selected"
        )
        pdf_data = selected_pdf.read_bytes()

        st.download_button(
            "📥 ดาวน์โหลดเอกสาร",
            data=pdf_data,
            file_name=selected_pdf.name,
            mime="application/pdf",
            use_container_width=True
        )

        confirm_delete = st.checkbox(
            f"ยืนยันการลบไฟล์: {selected_pdf.name}",
            key=f"confirm_delete_{selected_pdf.name}"
        )
        if st.button(
            "🗑️ ลบไฟล์ PDF ที่เลือก",
            type="secondary",
            use_container_width=True,
            disabled=not confirm_delete,
            key=f"delete_pdf_{selected_pdf.name}"
        ):
            selected_pdf.unlink()
            st.success(f"ลบไฟล์ “{selected_pdf.name}” เรียบร้อยแล้ว")
            st.rerun()

        if st.checkbox("👁️ เปิดดูเอกสารใน Dashboard", key="pdf_library_preview"):
            # ฝัง PDF ใน component โดยตรง จึงไม่ต้องติดตั้ง streamlit[pdf]
            pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")
            components.html(
                f'''<object data="data:application/pdf;base64,{pdf_base64}"
                    type="application/pdf" width="100%" height="650px">
                    ไม่สามารถแสดงตัวอย่าง PDF ได้ กรุณาใช้ปุ่มดาวน์โหลดเอกสาร
                </object>''',
                height=660,
                scrolling=False
            )


# =================================================================
# ⚙️ Dictionary คลังคำสั่ง
# =================================================================

c300_commands = {
    "🔦 เช็คระดับแสง (Optical Monitoring)": [
        ["เช็คระดับแสงทั้ง OLT และ ONU พร้อมค่า Attenuation", "show pon power attenuation gpon-onu_{slot}"],
        ["เช็คแสงผ่านพอร์ตย่อยอินเตอร์เฟส PON", "show gpon remote-onu interface pon gpon-onu_{slot}"]
    ],
    "📝 ตรวจสอบ Configuration & วงจร": [
        ["ดู Config รวมอินเตอร์เฟส (เข้าตำแหน่งเบอร์)", "show running-config interface gpon-onu_{slot}"],
        ["ดูเนื้อหา Config หลัง ONU (Profile / VLAN Port)", "show running-config | begin pon-onu-mng gpon-onu_{slot}"],
        ["ส่องดูเฉพาะฝั่ง PON Profile ของลูกค้า", "show onu running-config gpon-onu_{slot}"],
        ["ค้นหาเลขวงจรลูกค้าที่ผูกอยู่ข้างในพอร์ต PON", "show running-config | begin gpon-onu_{slot}"]
    ],
    "🌐 ตรวจสอบสถานะอุปกรณ์ (MAC / IP / LAN Ports)": [
        ["ส่องดูหมายเลข MAC Address ที่เรียนรู้ผ่านตัว ONU ล่าสุด", "show mac gpon onu gpon-onu_{slot}"],
        ["ดู MAC Address ทั้งหมดในพอร์ต PON ย่อย (ตาม Slot/Port)", "show mac gpon onu gpon-onu_{clean_slot}/"],
        ["ตรวจสอบหมายเลข IP Address ฝั่ง WAN/Host ของตัว ONU", "show gpon remote-onu ip-host gpon-onu_{slot}"],
        ["ตรวจสอบสถานะพอร์ตแลน (Ethernet) แต่ละช่องที่ตัว ONU ในบ้าน", "show gpon remote-onu interface eth gpon-onu_{slot}"]
    ],
    "📊 ตรวจสอบข้อมูลประวัติ & Log ย้อนหลัง": [
        ["เช็คประวัติอย่างละเอียดของการ Up/Down และสาเหตุสายหลุด", "show gpon onu detail-info gpon-onu_{slot}"],
        ["เช็คสถานะภาพรวม ONU ออนไลน์/ออฟไลน์ ทั้งหมดในการ์ด PON", "show gpon onu state gpon-olt_{clean_slot}"],
        ["เช็คประวัติ Log ย้อนหลังเพื่อดูพฤติกรรมสายลูกค้า", "show pon information gpon-onu_{slot}"]
    ]
}

c600_commands = {
    "🔦 เช็คระดับแสง (Optical Monitoring)": [
        ["เช็คระดับแสงขาเข้าที่ตัว ONU (C600)", "show pon power onu-rx gpon_onu-{slot}"],
        ["เช็คระดับแสงขาเข้าที่การ์ดตู้ OLT (C600)", "show pon power olt-rx gpon_onu-{slot}"]
    ],
    "📝 ตรวจสอบ Configuration & วงจร": [
        ["เช็ค Running Config บนพอร์ต ONU ล่าสุด (C600)", "show running-config-interface gpon_onu-{slot}"],
        ["เช็คโครงสร้างพอร์ตแลนและพอร์ตแมป VLAN (vport C600)", "show running-config-interface vport-1/{slot}"]
    ],
    "📊 ตรวจสอบข้อมูลประวัติ & Log ย้อนหลัง": [
        ["เช็คประวัติอย่างละเอียดและสาเหตุการ Up/Down ล่าสุด (C600)", "show gpon onu detail-info gpon_onu-{slot}"]
    ]
}

zte_pracharath_commands = {
    "🔑 รหัสผ่านเข้าใช้งาน (Account & Credentials)": [
        ["ข้อมูลการเข้าใช้งาน SW ZTE ประชารัฐ", 
"""User: nex
Pass: N3x@autoconfig 
Login enable Pass: zxr10"""]
    ],
    "🔍 คำสั่งตรวจสอบและเช็คแสง (Switch ZTE)": [
        ["แสดงสถานะ Port Up / Down", "show interface description"],
        ["เช็คสถานะ Port โดยรวมทั้งหมด", "show running-config"],
        ["เช็คแสงออกจาก SFP (TX Power)", "show optical-inform details tx-power interface xgei_0/"],
        ["เช็คแสงกลับมาจาก SFP (RX Power)", "show optical-inform details rx-power interface xgei_0/"],
        ["คำสั่งสำหรับ Sw 24k (เปิด/ปิด ระบบเช็คแสง)", "# optical-inform monitor enable"]
    ]
}

extreme_commands = {
    "🔍 คำสั่งตรวจสอบสถานะ & MAC Address": [
        ["ดู Status (แสดงแบบ No-Refresh ไม่ใช่ Real-time)", "show port no-refresh"],
        ["ดู MAC Address ภายใน VLAN ที่กำหนด", "show fdb vlan v..."],
        ["ดูว่าพอร์ตที่ระบุ มี VLAN อะไรผ่านบ้าง", "show fdb port ..."],
        ["ล้างข้อมูล FDB ในพอร์ตที่ระบุ", "clear fdb ports ..."]
    ],
    "⚙️ คำสั่งจัดการ VLAN & Configuration": [
        ["เพิ่ม VLAN แบบ Tagged ใส่พอร์ต", "config vlan v... add port ... tagged"],
        ["ลบ VLAN ออกจากพอร์ต", "config vlan v... delete port ..."],
        ["ตรวจสอบว่า VLAN ถูกใส่ไปที่พอร์ตไหนบ้าง", "show vlan v..."],
        ["สร้าง VLAN ใหม่พร้อมกำหนด Tag", "create vlan v... tag ..."],
        ["แสดงการตั้งค่าเฉพาะพอร์ต", "configure ports 17 display"]
    ],
    "🔦 คำสั่งตรวจสอบค่าแสง SFP (Transceiver)": [
        ["เช็คระดับแสงภาพรวมทุกพอร์ต", "show ports transceiver information detail"],
        ["เช็คระดับแสงแยกเฉพาะพอร์ต (ตัวอย่างพอร์ต 11)", "show ports 11 transceiver information detail"]
    ]
}

fixline_commands = {
    "🔍 คำสั่งตรวจสอบสถานะ & ตำแหน่ง": [
        ["ดูสถานะเลขหมาย", "stsup:sub=xxxx ;"],
        ["ดูตำแหน่งวงจร/พอร์ต", "exdrp:dev=li3-xxxx ;"],
        ["ดู Category (cat)", "suscp:snb=xxxx ;"]
    ]
}

# --- 2. SIDEBAR NAVIGATION & DATA SECTIONS ---
st.sidebar.title("⚡ COMMAND CENTER")

# ตัวเลือกเมนูหมวดหมู่
category = st.sidebar.radio(
    "เลือกโหมดใช้งาน",
    [
        "ZTE C300",
        "ZTE C600",
        "ZTE ประชารัฐ",
        "Extreme Switch",
        "Fixline",
        "ข้อมูลอ้างอิง & บันทึก"
    ]
)

st.sidebar.markdown("---")

# ส่วนแสดงข้อมูลเพิ่มเติมใน Sidebar (โหลดแบบ Dynamic มีการบันทึก/แก้ไข)
with st.sidebar.expander("🌐 ลิงก์เว็บใช้งานบ่อย", expanded=False):
    render_web_section("web_links.json", [
        {"name": "Google", "url": "https://www.google.com"},
        {"name": "Streamlit Docs", "url": "https://docs.streamlit.io"}
    ])

with st.sidebar.expander("📏 ระยะสาย Optic", expanded=False):
    render_ofc_section("ofc_routes.json", [
        {"route": "Node A - Node B", "distance": "5.2 km", "note": "Main route"}
    ])

with st.sidebar.expander("🆔 เลขวงจรสำคัญ", expanded=False):
    render_circuit_section("circuits.json", [
        {"code": "CIR-100203", "owner": "NOC Center"}
    ])

with st.sidebar.expander("📍 ที่อยู่ NT / Node", expanded=False):
    render_address_section("nt_addresses.json", [
        {"title": "ศูนย์ NT กาญจนบุรี", "detail": "123 ถ.แสงชูโต ต.บ้านเหนือ อ.เมือง จ.กาญจนบุรี"}
    ])

with st.sidebar.expander("📞 เบอร์ IP Phone", expanded=False):
    render_simple_value_section("ip_phones.json", [{"value": "1001", "note": "ห้องปฏิบัติการ NOC"}], "เบอร์ IP Phone", "ip_phone")

with st.sidebar.expander("💻 SecureCRT Session", expanded=False):
    render_simple_value_section("securecrt.json", [{"value": "OLT-C300-SiteA", "note": "10.0.0.1"}], "ชื่อ Session / Host", "securecrt")


# --- 3. MAIN CONTENT DISPLAY ---

# Ticker Readout
st.markdown("""
<div class="ticker-wrap">
    <div class="ticker-item">
        <div class="ticker-label"><span class="live-dot"></span>SYSTEM STATUS</div>
        <div class="ticker-value up">ONLINE <span class="ticker-unit">100%</span></div>
    </div>
    <div class="ticker-item">
        <div class="ticker-label">ACTIVE MODE</div>
        <div class="ticker-value">''' + category + '''</div>
    </div>
    <div class="ticker-item">
        <div class="ticker-label">HOST LOGGED</div>
        <div class="ticker-value">root@kri-noc</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<h2>{category}<span class='blink-cursor'></span></h2>", unsafe_allow_html=True)

# ช่องค้นหาคำสั่งหลัก
search_query = st.text_input("🔎 ค้นหาคำสั่ง (Search Command / Keyword):", "").strip()

# แสดงคลังเอกสาร PDF
show_pdf_library()

st.markdown("---")

# ฟังก์ชันแสดงผลกลุ่มคำสั่ง
def display_command_group(cmd_dict, slot_val="", clean_slot_val=""):
    found_any = False
    for group_name, cmds in cmd_dict.items():
        # กรองรายการตามคำค้นหา
        matching_cmds = []
        for item in cmds:
            desc = item[0]
            cmd_template = item[1]
            
            # แทนค่าพารามิเตอร์ slot ในคำสั่ง (ถ้ามี)
            formatted_cmd = cmd_template.format(slot=slot_val, clean_slot=clean_slot_val) if slot_val else cmd_template
            
            if not search_query or search_query.lower() in desc.lower() or search_query.lower() in formatted_cmd.lower():
                matching_cmds.append((desc, formatted_cmd))

        if matching_cmds:
            found_any = True
            st.markdown(f"### {group_name}")
            for desc, final_cmd in matching_cmds:
                highlighted_desc = highlight_text(desc, search_query)
                st.markdown(f'<div class="cmd-label">{highlighted_desc}</div>', unsafe_allow_html=True)
                st.code(final_cmd, language="bash")

    if not found_any:
        st.info("❌ ไม่พบคำสั่งที่ตรงกับคำค้นหา")


# การประมวลผลแยกตามหมวดหมู่ที่เลือก
if category in ["ZTE C300", "ZTE C600"]:
    st.caption("ระบุตำแหน่ง Slot/Port/ONU เพื่อเจนเนอเรตคำสั่งอัตโนมัติ")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        slot_input = st.text_input("ระบุตำแหน่ง (เช่น 1/2/3:4 หรือ 1/1/1):", "1/1/1:1").strip()
    
    # คำนวณ clean_slot (ตัดส่วน ONU หลังเครื่องหมาย : หรือ / ออกเพื่อใช้กับระดับ Port)
    clean_slot_input = re.split(r'[:/]', slot_input)[0] if slot_input else ""
    if slot_input and ":" in slot_input:
        clean_slot_input = slot_input.split(":")[0]

    st.markdown("---")
    
    if category == "ZTE C300":
        display_command_group(c300_commands, slot_val=slot_input, clean_slot_val=clean_slot_input)
    else:
        display_command_group(c600_commands, slot_val=slot_input, clean_slot_val=clean_slot_input)

elif category == "ZTE ประชารัฐ":
    display_command_group(zte_pracharath_commands)

elif category == "Extreme Switch":
    display_command_group(extreme_commands)

elif category == "Fixline":
    display_command_group(fixline_commands)

elif category == "ข้อมูลอ้างอิง & บันทึก":
    st.markdown("### 📌 สรุปข้อมูลบันทึกระบบหน้างาน")
    
    tab1, tab2, tab3 = st.tabs(["📏 เส้นทาง OFC", "🆔 เลขวงจร", "📍 สถานที่ NT"])
    
    with tab1:
        ofc_data = load_section_data("ofc_routes.json", [])
        if ofc_data:
            for item in ofc_data:
                st.markdown(f"• **{item['route']}** — `{item['distance']}` (หมายเหตุ: {item.get('note', '-')})")
        else:
            st.caption("ไม่มีข้อมูลเส้นทาง OFC")
            
    with tab2:
        circuit_data = load_section_data("circuits.json", [])
        if circuit_data:
            for item in circuit_data:
                st.markdown(f"• `{item['code']}` — {item['owner']}")
        else:
            st.caption("ไม่มีข้อมูลเลขวงจร")
            
    with tab3:
        addr_data = load_section_data("nt_addresses.json", [])
        if addr_data:
            for item in addr_data:
                st.markdown(f"**{item['title']}**\n{item['detail']}\n---")
        else:
            st.caption("ไม่มีข้อมูลสถานที่")
