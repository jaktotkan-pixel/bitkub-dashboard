import streamlit as st

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="ZTE OLT & PC Command Center", layout="wide")

# ปรับดีไซน์เป็นธีมขาว คลีน สว่าง สบายตา สแกนหัวข้อง่ายมาก
st.markdown("""
<style>
    /* พื้นหลังสีขาวสะอาดตา */
    .stApp { background-color: #ffffff; color: #1f2328; font-family: sans-serif; }
    
    /* กล่องข้อความ Code Block สีเทาอ่อน ขอบมน ชัดเจน */
    .stCodeBlock { background-color: #f6f8fa !important; border: 1px solid #d0d7de !important; }
    .stCodeBlock code { color: #000000 !important; }
    
    /* หัวข้อหลักสีน้ำเงินเข้ม มองเห็นเด่นชัด */
    h2 { color: #0969da !important; font-weight: 700; margin-top: 15px; margin-bottom: 5px; }
    h3 { color: #24292f !important; font-weight: 600; font-size: 17px; border-bottom: 2px solid #d0d7de; padding-bottom: 6px; margin-top: 15px; }
    
    /* สไตล์ข้อความธรรมดาให้หนาและชัดขึ้น */
    p, span, li { color: #24292f; font-weight: 500; }
    
    /* ซ่อนปุ่มที่ไม่จำเป็น */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color: #1a7f37; margin-top: -10px; font-weight: 800;'>💻 ZTE OLT & PC COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #57606a; font-size: 15px;'>ศูนย์รวมคำสั่งด่วน ZTE OLT C300/C600 และคำสั่ง CMD สำหรับวิเคราะห์ระบบหน้างาน (ธีมขาว คลีน สบายตา)</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 2. SIDEBAR : LIVE INJECTION ---
st.sidebar.markdown("### 🔍 ตัวแปรหน้างาน")
input_slot = st.sidebar.text_input("พิกัดพอร์ต (Slot/Port:ID)", "1/5/1:1")
input_circuit = st.sidebar.text_input("เลขวงจร / VLAN", "34")

# แปลงค่าพอร์ตย่อยสำหรับคำสั่งคุมพอร์ต PON ภาพรวม (ตัดเครื่องหมาย : ออกถ้ามี)
clean_slot = input_slot.split(':')[0] if ':' in input_slot else input_slot


# =================================================================
# ⚙️ Dictionary คลังคำสั่ง
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
    "🚀 ทางลัดเปิดโปรแกรมระบบ & หน้าต่างด่วน (Shortcut)": [
        ["javis (คำสั่งด่วนเรียกเปิดระบบช่วยเหลือ หรือเปิดลิงก์ Javis ผ่านบราวเซอร์หลัก)", "start https://javis.nt.co.th"],
        ["ncpa.cpl (คีย์ลัดเปิดหน้าต่าง Network Connections เพื่อไปจัดการการ์ดแลน / Fix IP)", "ncpa.cpl"],
        ["notepad (เปิดโปรแกรมจดบันทึก Notepad ขึ้นมาทดสคริปต์ด่วน)", "notepad"],
        ["compmgmt.msc (เปิดหน้า Computer Management จัดการระบบฮาร์ดแวร์/เช็คไดรเวอร์คอม)", "compmgmt.msc"]
    ],
    "💻 คำสั่งวิเคราะห์เน็ตหน้างานผ่านคอมพิวเตอร์": [
        ["ipconfig (เช็คหมายเลข IP Address เบื้องต้นในการ์ดแลนคอมพิวเตอร์)", "ipconfig"],
        ["ipconfig /all (เช็คไอพี, แมคแอดเดรส และข้อมูล DNS การ์ดแลนทั้งหมดในคอม)", "ipconfig /all"],
        ["arp -a (ตรวจสอบหมายเลขไอพีและแมคของอุปกรณ์อื่นๆ ในวง LAN เดียวกัน)", "arp -a"],
        ["nslookup (ใช้ตรวจสอบการทำงานและแปลชื่อโดเมน/DNS)", "nslookup google.com"],
        ["tracert (ทดสอบวิ่งหาเส้นทาง Network ยิงเช็คว่าเน็ตไปติดคอขวดที่ฮอปไหน)", "tracert 8.8.8.8"]
    ]
}

# 5. หมวดหมู่คำสั่งสำหรับ Line Bot Javis
javis_bot_commands = {
    "🔍 คำสั่งค้นหารายชื่อ Node และเช็คสถานะทางกายภาพ": [
        ["nodelist,hw. (ดูชื่อ node ต่างๆ ทั้งหมดในระบบ)", "nodelist,hw."],
        ["showoptical,hw[ชื่อ node] (สั่งดูค่าแสงของโหนดนั้นๆ เช่น ตลุงเหนือ)", "showoptical,hwตลุงเหนือ"]
    ],
    "⚡ คำสั่งตรวจสอบสถานะทั่วไป (Check Status)": [
        ["1. ดูซีรี ลอย (เช็ค Serial Number ที่ยังไม่ได้ลงทะเบียน)", "sn,กาญ"],
        ["2. ดูจำนวน ONU ใน PON (เช็คปริมาณอุปกรณ์ในพอร์ตของการ์ดนั้นๆ)", "state,กาญ"],
        ["3. ดู run config (ส่องโปรไฟล์การตั้งค่าปัจจุบันของ ONU)", "run,3451j0000"],
        ["4. ดู Port Lan (เช็คสถานะการเชื่อมต่อพอร์ตแลนหลัง ONU)", "lanstate,3451j0000"],
        ["13. ดู แสง / เช็คแสง (ตรวจสอบระดับสัญญาณ Optical ด่วน)", "!!,3451j0000"],
        ["14. ดู mac (ตรวจสอบตาราง MAC Address ที่ผ่านตัวอุปกรณ์)", "mac,3451j0000"]
    ],
    "🛠️ คำสั่งควบคุมระบบและแก้ไขพอร์ต (Control & Block)": [
        ["5. Block แสง (สั่งปิดสัญญาณแสงไปที่ ONU ชั่วคราว)", "block,3451j0000"],
        ["6. DeBlock แสง (สั่งเปิดสัญญาณแสงกลับคืนให้ ONU)", "deblock,3451j0000"],
        ["19. reboot onu (สั่งรีสตาร์ทตัว ONU ลูกค้าจากระยะไกล)", "reboot,3451j5000"]
    ],
    "➕❌ คำสั่งเพิ่ม / ลบ / เปลี่ยนแปลงอุปกรณ์ (Provisioning)": [
        ["7. ลบ ONU (ลบข้อมูล ONU ออกจากระบบโหนด [โหนด,พิกัด,วงจร])", "delonu,กาญ,1/2/2,100"],
        ["8. เปลี่ยน ONU (สลับเปลี่ยนเครื่องใหม่โดยใช้ค่า Config เดิม)", "replace,3451j0000,ZTEGC9999999"]
    ],
    "⚙️ คำสั่งตั้งค่าโปรไฟล์สลับโหมด (Configuration & Mode)": [
        ["9. config route (สั่งตั้งค่าเป็นโหมด Route โหมดเริ่มต้น)", "autoroute,กาญ,ZTEGC9999999,3003,3451j8888"],
        ["10. config bridge (สั่งตั้งค่าเป็นโหมด Bridge ต่อพ่วงเลเยอร์ 2)", "bridge,กาญ,ZTEGC9999999,3003,3451j8888"],
        ["11. เปลี่ยน route to bridge (สลับโหมดจาก Route ไปเป็น Bridge)", "rtob,3451j0000"],
        ["12. เปลี่ยน bridge to route (สลับโหมดจาก Bridge กลับมาเป็น Route)", "btor,3451j0000"],
        ["15. config ด้าน interface (จัดการระบบเชื่อมต่อพอร์ตโครงสร้าง)", "interface,3451j0000"],
        ["16. config ด้าน pon (ตั้งค่าโปรไฟล์ฝั่งเครือข่าย PON)", "ponconfig,3451j0000"],
        ["17. config autoroute (คำสั่งสร้างเส้นทางแบบระบุรายละเอียดโหนดคริ)", "autoroute,kri,ZTEGC1E1E1EE,3001,3451j0000"],
        ["18. setdhcpfromnet (สั่งกำหนดดึง IP รับแจกผ่านระบบเครือข่าย)", "dhcpfromnet,3459j5063"]
    ]
}


# --- 3. DISPLAY ENGINE (สลับแท็บแยกชัดเจน) ---

tab_c300, tab_c600, tab_sys, tab_pc, tab_javis_bot = st.tabs([
    "🍏 1. ตู้ซีรีส์เดิม ZTE C300", 
    "⚡ 2. ตู้ซีรีส์ใหม่ ZTE C600", 
    "📡 3. คำสั่ง Uplink / ชุดตั้งตู้ OLT ใหม่",
    "💻 4. คำสั่ง CMD บนคอมพิวเตอร์ (Windows)",
    "🤖 5. Javis Line Bot (ZTE Config)"
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

# แสดงผลพาร์ท System / Uplink / Initial Config
with tab_sys:
    st.markdown("<h2>📡 หมวดคำสั่งระบบ Uplink และการตั้งค่าตู้ OLT เริ่มต้น</h2>", unsafe_allow_html=True)
    search_sys = st.text_input("🔍 ค้นหาคำสั่งระบบ:", "", key="search_sys_key").lower()
    
    for sub_category, items in system_commands.items():
        filtered_items = [i for i in items if search_sys in i[0].lower() or search_sys in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                if len(cli_command) > 500:
                    st.markdown(f"📌 **{description}**")
                    st.code(cli_command, language="routeros")
                else:
                    col_desc, col_code = st.columns([1.1, 1.9])
                    with col_desc: st.markdown(f"📌 **{description}**")
                    with col_code: st.code(cli_command, language="routeros")

# แสดงผลพาร์ท PC CMD
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

# แสดงผลพาร์ท Javis Line Bot (พื้นหลังขาว-คลีน)
with tab_javis_bot:
    st.markdown("<h2>🤖 Javis Line Bot Help Center (สำหรับส่งคำสั่งควบคุม OLT/ONU ผ่านไลน์)</h2>", unsafe_allow_html=True)
    st.info("ℹ️ คำแจ้งเตือน: Javis เป็น LINE Bot ช่วยจัดการ Configuration ของ ZTE กรุณาใช้งานอย่างระมัดระวัง! รูปแบบการพิมพ์ต้องใช้เครื่องหมายคอมม่า ( , ) เป็นตัวแยกชุดคำสั่งเสมอ")
    search_javis = st.text_input("🔍 ค้นหาคำสั่ง Line Bot Javis:", "", key="search_javis_key").lower()
    
    for sub_category, items in javis_bot_commands.items():
        filtered_items = [i for i in items if search_javis in i[0].lower() or search_javis in i[1].lower()]
        if filtered_items:
            st.markdown(f"### {sub_category}")
            for description, cli_command in filtered_items:
                col_desc, col_code = st.columns([1.2, 1.8])
                with col_desc: st.markdown(f"📌 **{description}**")
                with col_code: st.code(cli_command, language="text")

# --- 5. FOOTER TEMPLATE PROFILE EXTRA ---
st.markdown("---")
with st.expander("📝 ส่องดูรูปแบบตัวอย่างหน้าโปรไฟล์จัดพอร์ต ONU"):
    st.code("""service internet gemport 1 vlan 10
 interface eth eth_0/2 state lock
 interface eth eth_0/3 state lock
 interface eth eth_0/4 state lock
 vlan port eth_0/1 mode tag vlan 10
 dhcp-ip ethuni eth_0/1 forbidden""", language="routeros")
