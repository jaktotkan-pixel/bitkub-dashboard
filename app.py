import streamlit as st

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="ZTE OLT & PC Command Center", layout="wide")

# ปรับดีไซน์เป็นธีมขาว คลีน สบายตา
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
    
    /* ปรับแต่ง Sidebar */
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e1e4e8; }
    
    /* ซ่อนปุ่มที่ไม่จำเป็น */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)


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
        ["เช็คประวัติ Log ย้อนหลังเพื่อดูพฤติกรรมสายลูกค้า", "show pon onu information gpon-onu_{slot}"]
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
        ["เช็คสถานะทางกายภาพและระดับความเร็ว (Speed) พอร์ต Uplink", "show interface port-status xgei_1/"],
        ["เช็คข้อมูลโมดูลแสงและระดับแสงของพอร์ต Uplink ล่าสุด (วิธีที่ 1)", "show interface optical-module-info xgei_1/"],
        ["เช็คระดับความแรงแสงโมดูลพอร์ต Uplink (วิธีที่ 2)", "show optical-module-info xgei-1/4"]
    ],
    "❌ คำสั่งลบค่า / เคลียร์ระบบ": [
        ["ล้างตารางเคลียร์ตารางค้าง MAC Address บน VLAN", "mac delete vlan {circuit}"],
        ["เข้าโหมดคอนฟิกเพื่อสั่งลบ MAC vlan ขยะ (เคลียร์ Session ค้าง)", "configure terminal\nmac delete vlan {circuit}"],
        ["สั่งเคลียร์ค่าตัวนับข้อผิดพลาดสายแลน (แก้ไขปัญหา CRC Error)", "Clear counter ethernet"]
    ],
    "🔍 การค้นหาข้อมูลภาพรวมตู้": [
        ["ค้นหาจุดเริ่มต้น Config บนตู้ตามเลขวงจรลูกค้า", "show run | begin {circuit}"],
        ["โชว์รายชื่อ ONU ป้ายแดงที่พึ่งเสียบสายเข้ามา (หาเลข S/N ลอย)", "show gpon onu uncfg"]
    ]
}

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


# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 📌 เมนูหลัก")

# 1. แถบเมนู Config
selected_menu = None
with st.sidebar.expander("⚙️ Config", expanded=True):
    config_options = [
        "🍏 ZTE C300 Series",
        "⚡ ZTE C600 Series",
        "📡 Uplink & Initial Config",
        "💻 Windows CMD Shortcuts",
        "🤖 Javis Line Bot"
    ]
    selected_menu = st.radio("เลือกหมวดหมู่การใช้งาน:", config_options, label_visibility="collapsed")

# 2. แถบเมนู Web (รวมลิงก์ทั้งหมด 11 เว็บ)
with st.sidebar.expander("🌐 Web", expanded=True):
    st.markdown("🔗 [Data Kan](https://sites.google.com/view/datakan)")
    st.markdown("🔗 [182.52.113.237](http://182.52.113.237/)")
    st.markdown("🔗 [TSP Login](https://tsp.totbb.net/index.php?r=tbl-users%2Flogin)")
    st.markdown("🔗 [SCOMS NT](https://scoms.intra.ntplc.co.th/Default.aspx)")
    st.markdown("🔗 [Umbo System](http://10.228.59.45/umbo/login.php?uri=%2Fumbo%2F)")
    st.markdown("🔗 [NT 1888 Request](https://nt1888.ntplc.co.th/request)")
    st.markdown("🔗 [TOP NT Central](https://top.ntcentral.net/login)")
    st.markdown("🔗 [NEX Intra NT](https://nex.intra.ntplc.co.th/ip/nex/)")
    st.markdown("🔗 [Ruijie Cloud](https://cloud-as.ruijienetworks.com/sso/login)")
    st.markdown("🔗 [IP Server (10.0.105.85)](http://10.0.105.85/)")
    st.markdown("🔗 [System Login (203.113.70.137)](http://203.113.70.137/login)")


# --- 3. MAIN CONTENT DISPLAY ---

st.markdown("<h1 style='color: #1a7f37; margin-top: -10px; font-weight: 800;'>💻 ZTE OLT & PC COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("---")

def render_command_section(title, command_dict, lang="routeros"):
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    search_term = st.text_input(f"🔍 ค้นหาคำสั่งในหมวดนี้:", "", key=f"search_{title}").lower()
    
    for sub_cat, items in command_dict.items():
        filtered = [
            i for i in items 
            if search_term in i[0].lower() or search_term in i[1].lower()
        ]
        
        if filtered:
            st.markdown(f"### {sub_cat}")
            for desc, code in filtered:
                if len(code) > 500:
                    st.markdown(f"📌 **{desc}**")
                    st.code(code, language=lang)
                else:
                    c1, c2 = st.columns([1.1, 1.9])
                    with c1: st.markdown(f"📌 **{desc}**")
                    with c2: st.code(code, language=lang)

# แสดงผลตามหน้าใน Config
if selected_menu == "🍏 ZTE C300 Series":
    render_command_section("🍏 หมวดคำสั่งสำหรับตู้ซีรีส์ ZTE C300", c300_commands)

elif selected_menu == "⚡ ZTE C600 Series":
    render_command_section("⚡ หมวดคำสั่งสำหรับตู้ซีรีส์ใหม่ ZTE C600", c600_commands)

elif selected_menu == "📡 Uplink & Initial Config":
    render_command_section("📡 หมวดคำสั่งระบบ Uplink และการตั้งค่าตู้ OLT เริ่มต้น", system_commands)

elif selected_menu == "💻 Windows CMD Shortcuts":
    render_command_section("💻 หมวดคำสั่ง CMD บนคอมพิวเตอร์ (Windows)", pc_cmd_commands, lang="batch")

elif selected_menu == "🤖 Javis Line Bot":
    st.info("ℹ️ คำแจ้งเตือน: Javis เป็น LINE Bot ช่วยจัดการ Configuration ของ ZTE รูปแบบการพิมพ์ต้องใช้เครื่องหมายคอมม่า ( , ) เป็นตัวแยกชุดคำสั่งเสมอ")
    render_command_section("🤖 Javis Line Bot Help Center", javis_bot_commands, lang="text")


# --- 4. FOOTER EXTRA ---
st.markdown("---")
with st.expander("📝 ตัวอย่างหน้าโปรไฟล์จัดพอร์ต ONU"):
    st.code("""service internet gemport 1 vlan 10
 interface eth eth_0/2 state lock
 interface eth eth_0/3 state lock
 interface eth eth_0/4 state lock
 vlan port eth_0/1 mode tag vlan 10
 dhcp-ip ethuni eth_0/1 forbidden""", language="routeros")
