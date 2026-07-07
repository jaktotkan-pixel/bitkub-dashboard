import streamlit as st

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="ZTE OLT & PC Command Center", layout="wide")

# ปรับดีไซน์ให้จัดกลุ่มสีแยกโมเดลชัดเจน สแกนสายตาง่าย
st.markdown("""
<style>
    .stApp { background-color: #0b0f14; color: #c9d1d9; font-family: sans-serif; }
    .stCodeBlock { background-color: #161b22 !important; border: 1px solid #30363d; }
    h2 { color: #58a6ff !important; font-weight: 600; margin-top: 10px; }
    h3 { color: #58a6ff !important; font-weight: 500; font-size: 16px; border-bottom: 1px solid #21262d; padding-bottom: 5px; }
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #2ea043; margin-top: -10px;'>💻 ZTE OLT & PC COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8b949e;'>ศูนย์รวมคำสั่งด่วน ZTE OLT C300/C600 และคำสั่ง CMD สำหรับวิเคราะห์ระบบหน้างาน</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. SIDEBAR : LIVE INJECTION ---
st.sidebar.markdown("### 🔍 ตัวแปรหน้างาน")
input_slot = st.sidebar.text_input("พิกัดพอร์ต (Slot/Port:ID)", "1/5/1:1")
input_circuit = st.sidebar.text_input("เลขวงจร / VLAN", "34")

# แปลงค่าพอร์ตย่อยสำหรับคำสั่งคุมพอร์ต PON ภาพรวม (ตัดเครื่องหมาย : ออกถ้ามี)
clean_slot = input_slot.split(':')[0] if ':' in input_slot else input_slot


# =================================================================
# ⚙️ Dictionary คลังคำสั่งที่แยกเก็บอย่างเป็นระเบียบ (แก้ไข/เพิ่มตรงนี้ได้ตลอด)
# =================================================================

# 1. หมวดหมู่สำหรับตู้รุ่นเดิม (C300 ซีรีส์)
c300_commands = {
    "🔦 เช็คระดับแสง (Optical Monitoring)": [
        ["เช็คระดับแสงทั้ง OLT และ ONU พร้อมค่า Attenuation", f"show pon power attenuation gpon-onu_{input_slot}"],
        ["เช็คแสงผ่านพอร์ตย่อยอินเตอร์เฟส PON", f"show gpon remote-onu interface pon gpon-onu_{input_slot}"]
    ],
    "📝 ตรวจสอบ Configuration & วงจร": [
        ["ดู Config รวมอินเตอร์เฟส (เข้าตำแหน่งเบอร์)", f"show running-config interface gpon-onu_{input_slot}"],
        ["ดูเนื้อหา Config หลัง ONU (Profile / VLAN Port)", f"show running-config | begin pon-onu-mng gpon-onu_{input_slot}"],
        ["ส่องดูเฉพาะฝั่ง PON Profile ของลูกค้า", f"show onu running-config gpon-onu_{input_slot}"],
        ["ค้นหาเลขวงจรลูกค้าที่ผูกอยู่ข้างในพอร์ต PON", f"show running-config | begin gpon-onu_{input_slot}"]
    ],
    "🌐 ตรวจสอบสถานะอุปกรณ์ (MAC / IP / LAN Ports)": [
        ["ส่องดูหมายเลข MAC Address ที่เรียนรู้ผ่านตัว ONU ล่าสุด", f"show mac gpon onu gpon-onu_{input_slot}"],
        ["ดู MAC Address ทั้งหมดในพอร์ต PON ย่อย (ตาม Slot/Port)", f"show mac gpon onu gpon-onu_{clean_slot}/"],
        ["ตรวจสอบหมายเลข IP Address ฝั่ง WAN/Host ของตัว ONU", f"show gpon remote-onu ip-host gpon-onu_{input_slot}"],
        ["ตรวจสอบสถานะพอร์ตแลน (Ethernet) แต่ละช่องที่ตัว ONU ในบ้าน", f"show gpon remote-onu interface eth gpon-onu_{input_slot}"]
    ],
    "📊 ตรวจสอบข้อมูลประวัติ & Log ย้อนหลัง": [
        ["เช็คประวัติอย่างละเอียดของการ Up/Down และสาเหตุสายหลุด", f"show gpon onu detail-info gpon-onu_{input_slot}"],
        ["เช็คสถานะภาพรวม ONU ออนไลน์/ออฟไลน์ ทั้งหมดในการ์ด PON", f"show gpon onu state gpon-olt_{clean_slot}"],
        ["เช็คประวัติ Log ย้อนหลังเพื่อดูพฤติกรรมสายลูกค้า", f"show pon onu information gpon-onu_{input_slot}"]
    ]
}

# 2. หมวดหมู่สำหรับตู้รุ่นใหม่ (C600 ซีรีส์)
c600_commands = {
    "🔦 เช็คระดับแสง (Optical Monitoring)": [
        ["เช็คระดับแสงขาเข้าที่ตัว ONU (C600)", f"show pon power onu-rx gpon_onu-{input_slot}"],
        ["เช็คระดับแสงขาเข้าที่การ์ดตู้ OLT (C600)", f"show pon power olt-rx gpon_onu-{input_slot}"]
    ],
    "📝 ตรวจสอบ Configuration & วงจร": [
        ["เช็ค Running Config บนพอร์ต ONU ล่าสุด (C600)", f"show running-config-interface gpon_onu-{input_slot}"],
        ["เช็คโครงสร้างพอร์ตแลนและพอร์ตแมป VLAN (vport C600)", f"show running-config-interface vport-1/{input_slot}"]
    ],
    "📊 ตรวจสอบข้อมูลประวัติ & Log ย้อนหลัง": [
        ["เช็คประวัติอย่างละเอียดและสาเหตุการ Up/Down ล่าสุด (C600)", f"show gpon onu detail-info gpon_onu-{input_slot}"]
    ]
}

# 3. หมวดหมู่คำสั่งระบบและพอร์ตเชื่อมต่อหลัก (Uplink / System / Config OLT ล่าสุด)
system_commands = {
    "🏗️ ชุดคำสั่งเริ่มต้นตู้ใหม่ (Initial Config)": [
        ["คำสั่งรวดเดียว สำหรับจัดบอร์ดตั้งชื่อระบบ แฟน เทส และสร้างโพรไฟล์บนตู้ OLT ตัวใหม่", 
"""configure terminal 
hostname kri-sigm4-24kolt02
username nex password N3x@autoconfig privilege 15

vlan database
vlan 16 name nex-wifi24k
exit

interface vlan16
ip address 10.223.194.116 255.255.255.0
byname nex-wifi24k
exit
ip route 0.0.0.0 0.0.0.0 10.223.194.1

interface xgei_1/3/2
no shutdown
hybrid-attribute fiber
description link to kri_kph_lpe1,Ethernet0 
switchport mode trunk
switchport vlan 16 tag
exit

ntp server 10.223.194.1 priority 1
ntp enable
clock timezone Thailand 7 0
snmp-server community ntx_public view AllView rw
snmp-server host 1.179.233.29 version 2c ntx_public enable NOTIFICATIONS target-addr-name EMS_1.179.233.29 isnmsserver
auto-write enable
auto-write 02:00:00 everyday

no fan env-card-device
no fan env-uplink-device
no fan env-serial-baudrate
fan epm enable

pon
onu-type ZTEG-F600 gpon description 4ETH
onu-type-if ZTEG-F600 eth_0/1-4
exit

gpon
profile tcont MDES-10M-IN type 2 assured 13000
exit

traffic-profile MDES-30M-OUT ip cir 39000 cbs 128 pir 39000 pbs 256
exit
write"""]
    ],
    "📡 ตรวจสอบพอร์ตเชื่อมต่อหลัก (Uplink)": [
        ["เช็คสถานะทางกายภาพและระดับความเร็ว (Speed) พอร์ต Uplink", f"show interface port-status xgei_1/"],
        ["เช็คข้อมูลโมดูลแสงและระดับแสงของพอร์ต Uplink ล่าสุด (วิธีที่ 1)", f"show interface optical-module-info xgei_1/"],
        ["เช็คระดับความแรงแสงโมดูลพอร์ต Uplink (วิธีที่ 2)", f"show optical-module-info xgei-1/4"]
    ],
    "❌ คำสั่งลบค่า / เคลียร์ระบบ": [
        ["ล้างตารางเคลียร์ตารางค้าง MAC Address บน VLAN", f"mac delete vlan {input_circuit}"],
        ["เข้าโหมดคอนฟิกเพื่อสั่งลบ MAC vlan ขยะ (เคลียร์ Session ค้าง)", f"configure terminal\nmac delete vlan {input_circuit}"],
        ["สั่งเคลียร์ค่าตัวนับข้อผิดพลาดสายแลน (แก้ไขปัญหา CRC Error)", f"Clear counter ethernet"]
    ],
    "🔍 การค้นหาข้อมูลภาพรวมตู้": [
        ["ค้นหาจุดเริ่มต้น Config บนตู้ตามเลขวงจรลูกค้า", f"show run | begin {input_circuit}"],
        ["โชว์รายชื่อ ONU ป้ายแดงที่พึ่งเสียบสายเข้ามา (หาเลข S/N ลอย)", f"show gpon onu uncfg"]
    ]
}

# 4. หมวดหมู่คำสั่งรันบนคอมพิวเตอร์หน้างาน (Windows CMD)
pc_cmd_commands = {
    "💻 คำสั่งวิเคราะห์เน็ตหน้างานผ่านคอมพิวเตอร์": [
        ["ipconfig", "ipconfig"],
        ["ipconfig /all (เช็คไอพี, แมคแอดเดรส และการ์ดแลนทั้งหมดในคอม)", "ipconfig /all"],
        ["arp -a (ตรวจสอบหมายเลขไอพีและแมคของอุปกรณ์อื่นๆ ในวง LAN เดียวกัน)", "arp -a"],
        ["nslookup (ใช้ตรวจสอบการทำงานและแปลชื่อโดเมน/DNS)", "nslookup google.com"],
        ["tracert (ทดสอบวิ่งหาเส้นทาง Network ยิงเช็คว่าเน็ตไปติดคอขวดที่ฮอปไหน)", "tracert 8.8.8.8"]
    ]
}


# --- 3. DISPLAY ENGINE (สลับแท็บแบบใช้งานสะดวกรวดเร็ว) ---

tab_c300, tab_c600, tab_sys, tab_pc = st.tabs([
    "🍏 1. ตู้ซีรีส์เดิม ZTE C300", 
    "⚡ 2. ตู้ซีรีส์ใหม่ ZTE C600", 
    "📡 3. คำสั่ง Uplink / ชุดตั้งตู้ OLT ใหม่",
    "💻 4. คำสั่ง CMD บนคอมพิวเตอร์ (Windows)"
])

# แสดงผลพาร์ท C300
with tab_c300:
    st.markdown("<h2>🍏 หมวดคำสั่งสำหรับตู้ซีรีส์ ZTE C300</h2>", unsafe_allow_html=True)
    search_c300 = st.text_input("🔍 ค้นหาคำสั่งภายในตู้ C300:", "", key="search_c300_key").lower()
    
    for sub_category, items in c300_commands.items():
        filtered_items = [i for i in items if search_c300 in i[0].lower() or search_c300 in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                col_desc, col_code = st.columns([1.1, 1.9])
                with col_desc: st.markdown(f"📌 **{description}**")
                with col_code: st.code(cli_command, language="routeros")

# แสดงผลพาร์ท C600
with tab_c600:
    st.markdown("<h2>⚡ หมวดคำสั่งสำหรับตู้ซีรีส์ใหม่ ZTE C600</h2>", unsafe_allow_html=True)
    search_c600 = st.text_input("🔍 ค้นหาคำสั่งภายในตู้ C600:", "", key="search_c600_key").lower()
    
    for sub_category, items in c600_commands.items():
        filtered_items = [i for i in items if search_c600 in i[0].lower() or search_c600 in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                col_desc, col_code = st.columns([1.1, 1.9])
                with col_desc: st.markdown(f"📌 **{description}**")
                with col_code: st.code(cli_command, language="routeros")

# แสดงผลพาร์ท System / Uplink / Initial Config ตัวใหม่
with tab_sys:
    st.markdown("<h2>📡 หมวดคำสั่งระบบ Uplink และการตั้งค่าตู้ OLT เริ่มต้น</h2>", unsafe_allow_html=True)
    search_sys = st.text_input("🔍 ค้นหาคำสั่งระบบ:", "", key="search_sys_key").lower()
    
    for sub_category, items in system_commands.items():
        filtered_items = [i for i in items if search_sys in i[0].lower() or search_sys in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                # กรณีสคริปต์ยาวมาก (Initial Config) ให้กินพื้นที่เต็มยาวลงมาสวยๆ
                if len(cli_command) > 500:
                    st.markdown(f"📌 **{description}**")
                    st.code(cli_command, language="routeros")
                else:
                    col_desc, col_code = st.columns([1.1, 1.9])
                    with col_desc: st.markdown(f"📌 **{description}**")
                    with col_code: st.code(cli_command, language="routeros")

# แสดงผลพาร์ท PC CMD ยิงเช็คเน็ตฝั่งคอมลูกค้า
with tab_pc:
    st.markdown("<h2>💻 หมวดคำสั่ง CMD บนคอมพิวเตอร์ (Windows) สำหรับวิเคราะห์หน้างาน</h2>", unsafe_allow_html=True)
    search_pc = st.text_input("🔍 ค้นหาคำสั่งคอมพิวเตอร์:", "", key="search_pc_key").lower()
    
    for sub_category, items in pc_cmd_commands.items():
        filtered_items = [i for i in items if search_pc in i[0].lower() or search_pc in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                col_desc, col_code = st.columns([1.1, 1.9])
                with col_desc: st.markdown(f"📌 **{description}**")
                with col_code: st.code(cli_command, language="batch")

# --- 5. FOOTER TEMPLATE PROFILE EXTRA ---
st.markdown("---")
with st.expander("📝 ส่องดูรูปแบบตัวอย่างหน้าโปรไฟล์จัดพอร์ต ONU"):
    st.code("""service internet gemport 1 vlan 10
 interface eth eth_0/2 state lock
 interface eth eth_0/3 state lock
 interface eth eth_0/4 state lock
 vlan port eth_0/1 mode tag vlan 10
 dhcp-ip ethuni eth_0/1 forbidden""", language="routeros")
