import streamlit as st
import re

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="ZTE OLT & PC Command Center", layout="wide")

# ปรับดีไซน์เป็นธีมขาว คลีน สบายตา + Highlight CSS
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
    
    /* สไตล์ Highlight สีเหลืองเข้ม */
    mark.highlight {
        background-color: #ffeb3b;
        color: #000000;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        box-shadow: 0 0 2px rgba(0,0,0,0.2);
    }

    /* ปรับแต่ง Sidebar */
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e1e4e8; }
    
    /* ซ่อนปุ่มที่ไม่จำเป็น */
    .stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)


# ฟังก์ชันทำ Highlight แถบสีเหลือง
def highlight_text(text, keyword):
    if not keyword:
        return text
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(lambda m: f'<mark class="highlight">{m.group(0)}</mark>', str(text))


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
        ["ล้างข้อมูล FDB ในพอร์ตที่ระบุ", "cler fdb ports ..."]
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
        ["ดู Category (cat)", "suscp:snb=xxxx ;"],
        ["ดูสถานะภาพรวมชุมสาย", "ststp:emg=xxxx ; emts=all ;"]
    ],
    "🔒 คำสั่งบล็อค & ปลดบล็อค (Block/Unblock)": [
        ["สั่งบล็อคพอร์ตอุปกรณ์", "blodi:dev=li3-xxxx;"],
        ["สั่งปลดบล็อคพอร์ตอุปกรณ์", "blode:dev=li3-xxxx;"],
        ["สั่งบล็อคที่ระดับชุมสาย", "remei:emg=xxxx,pcb=emrp-a-meu,mag=em-xx;"],
        ["สั่งปลดบล็อคที่ระดับ MAC", "blece:emg=xxxx,em=xx;"],
        ["สั่งปลดบล็อคทั้งหมด", "recei:emg=xxxx,emrp=o-a;"]
    ]
}

sg300_commands = {
    "⚙️ คำสั่งพื้นฐาน & จัดการ VLAN (Cisco SG300)": [
        ["เช็คการตั้งค่า Switch", "show running-config"],
        ["เข้าสู่โหมด Configuration", "config terminal"],
        ["สร้าง/เพิ่ม VLAN ใน Switch", "vlan ..."],
        ["เข้าจัดการพอร์ตที่ต้องการ", "interface gigabitethernet ..."],
        ["เพิ่ม VLAN แบบ Trunk ใส่พอร์ต", "switchport trunk allowed vlan add ..."],
        ["ปิดระบบป้องกัน VLAN หลุด (Smartport)", "no macro auto smartport"]
    ],
    "🌐 การตั้งค่า IP Address & Gateway": [
        ["ตั้งค่า Gateway ของ Switch", "ip default-gateway ...,...,...,..."],
        ["ลบค่า Gateway", "no ip default-gateway ...,...,...,..."],
        ["เข้าอินเตอร์เฟส VLAN เพื่อเปลี่ยน IP", "interface vlan 166"],
        ["กำหนดหมายเลข IP Address & Subnet", "ip address 10.223.128.33 255.255.255.0"]
    ]
}

huawei_commands = {
    "⚙️ คำสั่งตั้งค่า Switch (Huawei)": [
        ["เช็คการตั้งค่า Switch", "show running-config"],
        ["เข้าสู่โหมด Configuration", "config terminal"],
        ["สร้าง/เพิ่ม VLAN ใน Switch", "vlan ..."],
        ["เข้าจัดการพอร์ตที่ต้องการ", "interface gigabitethernet ..."],
        ["เพิ่ม VLAN แบบ Trunk ใส่พอร์ต", "switchport trunk allowed vlan add ..."],
        ["ตั้งค่า Gateway ของ Switch", "ip default-gateway ...,...,...,..."],
        ["ลบค่า Gateway", "no ip default-gateway ...,...,...,..."],
        ["เข้าอินเตอร์เฟส VLAN เพื่อเปลี่ยน IP", "interface vlan 166"],
        ["กำหนดหมายเลข IP Address & Subnet", "ip address 10.223.128.33 255.255.255.0"],
        ["ปิดระบบป้องกัน VLAN หลุด (Smartport)", "no macro auto smartport"]
    ]
}

dslam_commands = {
    "📟 ข้อมูลการเชื่อมต่อ DSLAM Forth": [
        ["Forth โหนด 577 (10.227.11.253)", 
"""IP: 10.227.11.253
User: krimsan
Pass: 577kri"""],
        ["Forth โหนด 222 (10.227.0.246)", 
"""IP: 10.227.0.246
User: kri01, kri02, kri03, kri04, kri05
Pass: admin1"""]
    ]
}

olt_ip_commands = {
    "📍 รายชื่อ IP OLT ในพื้นที่ & โครงข่าย": [
        ["รายการ IP OLT ทั้งหมดในระบบ (รวมชุดเดิมและชุดใหม่ล่าสุด)", 
"""• OLT-วังปลาหมู729 : 10.223.194.3
• OLT-ท่าอ้อ : 10.223.194.4
• OLT-บ้านดอนขลุบ737 : 10.223.194.8
• OLT-หนองสองห้อง812 : 10.223.194.10
• OLT-ทุ่งสมอ730 : 10.223.194.6
• OLT-ด่านมะขามเตี้ย : 10.223.194.14
• OLT-บ้านไทรทอง : 10.223.194.13
• OLT-หนองไผ่ม.6 : 10.223.194.15
• OLT-บ้านยางเกาะ : 10.223.194.16
• OLT-กลอนโดม.2vlan 736 : 10.223.194.17
• OLT-ตะเคียนงาม : 10.223.194.19
• OLT-รางสาลี่739 : 10.223.194.23
• OLT-หนองหญ้า : 10.223.194.29
• OLT-วังเย็น ม.3 : 10.223.194.30
• OLT-ดอนคราม743 : 10.223.194.27
• OLT-สำรอง740 : 10.223.194.24
• OLT-บ้านใหม่ : 10.223.194.25
• OLT-ห้วยไร่ : 10.223.194.28
• OLT-หนองเสือ742 : 10.223.194.26
• OLT-ดอนเจดีย์ : 10.223.194.22
• OLT-ดอนตาเพชร ม.6 : 10.223.194.55
• OLT-เบญจพาส : 10.223.194.54
• OLT_ห้วยสะพาน : 10.223.194.50
• OLT-พังตรุใน : 10.223.194.47
• OLT-หนองโรงม.4 750 : 10.223.194.49
• OLT-หนองตาขำ752 : 10.223.194.51
• OLT-เขากรวด : 10.223.194.52
• OLT-พังตรุ : 10.223.194.48
• OLT-หนองสาหร่าย : 10.223.194.57
• OLT-หนองลาน ม.4 : 10.223.194.56
• OLT_อุโลกสี่หมื่น ม.5 : 10.223.194.58
• OLT-ดอนแสลบ ม.8 : 10.223.194.53
• OLT_บ้านเก่า ม.1 : 10.223.194.66
• OLT- ท่ากระดาน ม.1 : 10.223.194.78
• OLT-สามยอด770 : 10.223.194.45
• OLT- พุพรม : 10.223.194.70
• OLT-บ่อพลอย : 10.223.194.71
• OLT- วังไผ่ ม.7 : 10.223.194.73
• OLT- หนองย่างช้าง : 10.223.194.44
• OLT-ช่องด่าน : 10.223.194.74
• OLT- บ้านยางสูง : 10.223.194.75
• OLT- สมเด็จเจริญ ม.5 : 10.223.194.76
• OLT- ห้วยกระเจา ม.3 : 10.223.194.69
• OLT- ด่านแม่แฉลบ ม.4 : 10.223.194.77
• OLT- ท่ากระดาน ม.4 : 10.223.194.79
• OLT- หนองปลาไหล : 10.223.194.83
• OLT- หนองกร่าง ม.2 : 10.223.194.81
• OLT- หนองขอนเทพพนม : 10.223.194.85
• OLT- หนองสาหร่าย : 10.223.194.84
• OLT-หนองปลิง ม.8 : 10.223.194.94
• OLT- โป่งช้าง : 10.223.194.82
• OLT- หนองกร่าง ม.9 : 10.223.194.89
• OLT- บ้านเขาวงพระจันทร์ ม.3 : 10.223.194.91
• OLT- บ้านทุ่งกระบ่ำ ม.8 : 10.223.194.86
• OLT- วัดหนองใหญ่เจริญพร : 10.223.194.88
• OLT- หนองปลิง ม.1 : 10.223.194.93
• OLT- หนองประดู่ : 10.223.194.95
• OLT-พุบอน : 10.223.194.92
• OLT-บ้านแก่งระเบิด : 10.223.194.103
• OLT-ต้นมะม่วง : 10.223.194.104
• OLT-วังกระแจะ : 10.223.194.102
• OLT-ช่องสะเดา : 10.223.194.98
• OLT-ลุ่มผึ้ง713 : 10.223.194.101
• OLT-สามัคคีธรรม : 10.223.194.99
• OLT-ท่าเสา : 10.223.194.115
• OLT-สะพานลาว : 10.223.194.110
• OLT-สิง ม.4 : 10.223.194.116
• OLT-ปากนาสวน : 10.223.194.108
• OLT-จะเลาะ : 10.223.194.109
• OLT-ห้วยเขย่ง ม.4 : 10.223.194.111
• OLT-หนองตากยาประชารัฐ : 10.223.194.114
• OLT-บ้านบึง : 10.223.194.118
• OLT-ทุ่งกระบ่ำ ม.6 : 10.223.194.122
• OLT-แยกบ่อยาง : 10.223.194.124
• OLT-หนองโสน : 10.223.194.125
• OLT-บ้านห้วยยาง : 10.223.194.126
• OLT-บ้านเขาหินตั้ง : 10.223.194.129
• OLT-พนมทวน : 10.223.194.128
• OLT-แก่งประลอม : 10.223.194.127
• OLT-หนองมะสังข์ : 10.223.194.123
• OLT-บ้านปากบาง : 10.223.194.119
• OLT บ้านท่าโป่ง(Bigrock) : 10.223.194.121
• OLT-บ้านภูเตย : 10.223.194.130
• olt-บ้านบ้องตี้ : 10.223.194.120
• OLT-บ้านโคกตะบอง : 10.223.194.117
• OLT- ห้วยกระเจา ม.8 : 10.223.194.46
• OLT-อีต่อง : 10.223.194.107
• OLT-บ้านเก่า ม.9 : 10.223.194.67
• OLT-หนองกุ่ม ม.7 : 10.223.194.59
• OLT-คีรีวงศ์ : 10.223.194.60
• OLT-หนองสามพราน : 10.223.194.61
• OLT-หนองกุ่ม ม.5 : 10.223.194.62
• OLT-อบต. แก่งเสี้ยน : 10.223.194.63
• OLT- หนองหญ้าปล้อง : 10.223.194.64
• OLT-จรเข้เผือก : 10.223.194.65
• OLT-หนองบ้านเก่า : 10.223.194.68
• OLT-วังใหญ่ : 10.223.194.72
• OLT- บ้านลำอีซู : 10.223.194.80
• OLT- วัดหนองขอน : 10.223.194.87
• OLT- บ้านหนองไม้เอื้อย : 10.223.194.90
• OLT-ศรีมงคล : 10.223.194.100
• OLT-พุเตย : 10.223.194.106
• บ่อพลอย(FTTx) : 10.233.17.249
• หลุมรัง (FTTx) : 10.233.17.208
• พนมทวน(FTTX) : 10.233.17.206
• สำนักคร้อ(FTTx) : 10.233.17.183
• ด่านมะขามเตี้ย(FTTx) : 10.233.17.212
• ท่าขนุน ม.5(FTTX) : 10.233.17.207
• หินดาด : 10.233.17.204
• เลาขวัญ(FTTx) : 10.233.17.226
• หนองตากยา(FTTX) : 10.233.17.252
• ดอนขมิ้น (FTTx) : 10.233.17.211
• ไทรโยค(FTTx) : 10.233.17.210
• สขาภิบาลลาดหญ้า(FTTX) : 10.233.17.242
• ศรีสวัสดิ์(FTTX) : 10.233.17.228
• ท่ามะกาZTE(ศูนย์บริการฯ) : 10.233.17.203
• สถานีโทรคมเขาป่าห้าม(FTTx) : 10.233.17.219
• OLT บ้านดอนแสลบ : 10.233.17.41
• หนองปรือ(FTTX) : 10.233.17.240
• แยกพุถ่อง(FTTX) : 10.233.17.202
• หนองฝ้าย (FTTx) : 10.233.17.209
• ท่ากระดาน ม.1 Fttx : 10.233.17.220
• ท่าม่วง (FTTx) : 10.233.17.243
• ยางม่วง(FTTX) : 10.233.17.234
• ท่ามะกา(FTTX) : 10.233.17.244
• ห้วยปากคอก(FTTX) : 10.233.17.10
• วังกระแจะ FTTx : 10.233.17.214
• ชะแล(FTTX) : 10.233.17.215
• พระแท่น (FTTx) : 10.233.17.225
• เขาตอง(FTTx) : 10.233.17.251
• ท่ามะขาม(FTTX) : 10.233.17.62
• หนองหญ้า(FTTx) : 10.233.17.218
• หนองสองตอน(FTTX) : 10.233.17.83
• ดอนชะเอม(FTTX) : 10.233.17.49
• ทุ่งทอง 2 (FTTx) : 10.233.17.43
• ทองผาภูมิ (FTTx) : 10.233.17.245
• หวายเหนียว(FTTx) : 10.233.17.122
• สังขละบุรี (FTTx) : 10.233.17.246
• พุน้ำร้อน(FTTx) : 10.233.17.248
• ด่านเจดีย์สามองค์(FTTx) : 10.233.17.216
• ท่าล้อ(FTTX) : 10.233.17.6
• เขาสามสิบหาบFttx : 10.233.17.51
• โคกตะบอง(FTTX) : 10.233.17.75
• OLT จองอั่ว : 10.233.17.99
• OLT หนองบัว ม.7 : 10.233.17.79
• Huawei_ตลุงเหนือ : 10.233.17.17
• Huawei_พาวิลเลี่ยน : 10.233.17.130
• ZTE_NongRee : 10.233.17.196
• OLT_ช่องกลิ้ง : 10.233.17.134
• OLT_ZTE_แก่งเรียง : 10.233.17.31
• Huawei_เขาน้อย : 10.233.17.131
• OLT ทุ่งทอง หมู่ 1 : 10.233.17.86
• โป่งนก : 10.233.17.29
• บ้านน้ำมุด(Bigrock) : 10.223.194.131
• huawei_หนองพังตรุ : 10.233.17.137
• kri_c600_01 : 10.233.17.138
• TMG-C600 : 10.233.17.241
• SCT_C600 : 10.233.17.238
• OLT ดอนตาเพชร ม.1 : 10.233.17.144
• ลิ่นถิ่น2 : 10.233.17.236
• Huawei_สระลงเรือ : 10.233.17.135
• พฤกษากาญจน์(FTTx) : 10.233.17.250
• ม่วงชุม(FTTX) : 10.233.17.18
• NT1_ท่ากระทุ่ม_10.158.5.158 : 10.158.5.158
• หนองลู ม.6 (DE) : 10.223.194.113
• ปรังเผล(FTTx) : 10.233.17.30
• ไทรโยค ม.2 : 10.233.17.121
• ZTE_แสนตอ : 10.233.17.221
• OLT-เขาปูน : 10.233.17.20
• วังศาลา(FTTX) : 10.233.17.227
• ราชภัฎ (FTTx) : 10.233.17.229
• ศูนย์ราชการ(FTTx) : 10.233.17.217
• OLT-ท่าไม้-ม.3 : 10.233.17.154
• หนองขาว_FiberHome_2 : 10.233.17.247
• บึงชะโค(FTTx) : 10.233.17.213
• OLT_หนองบัว : 10.233.17.28
• บ้านห้วยเขย่ง_ม.5 : 10.233.17.184
• NT1_หนองไผ่_10.158.90.7 : 10.158.90.7
• NT1_ตลาดสำรอง_10.158.95.3 : 10.158.95.3
• NT1_สมเด็จเจริญ_10.158.5.137 : 10.158.5.137
• อู่ล่อง : 10.233.17.149
• บ่อพลอย_c620 : 10.233.17.109
• NT1_ท่าพุ_10.158.90.3 : 10.158.90.3
• สระกลอย_FTTx : 10.233.17.132
• วังกระแจะ FIBERHOME : 10.233.17.231
• หม่องกะลา(Fttx) : 10.233.17.224
• Zte_หนองอำเภอจีน : 10.233.17.133
• OLT_หนองเข้ : 10.233.17.150"""]
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
        ["16. configด้าน pon (ตั้งค่าโปรไฟล์ฝั่งเครือข่าย PON)", "ponconfig,3451j0000"],
        ["17. config autoroute (คำสั่งสร้างเส้นทางแบบระบุรายละเอียดโหนดคริ)", "autoroute,kri,ZTEGC1E1E1EE,3001,3451j0000"],
        ["18. setdhcpfromnet (สั่งกำหนดดึง IP รับแจกผ่านระบบเครือข่าย)", "dhcpfromnet,3459j5063"]
    ]
}

ofc_distances = [
    ("หนองปรือ - เขาโจด", "19.2 km", "Core 17, 16 | Bead core 7 (1.7km จากเขาโจด)"),
    ("เขาโจด - สมเด็จเจริญ", "19.0 km", "Core 14, 18"),
    ("RTหนองปลิง ม.1 - RTหนองปลิง ม.8", "10.7 km", "-"),
    ("เลาขวัญ - หนองปลิง ม.8", "21.5 km", "-"),
    ("ดอนแสลบ - สยามฟอร์เรดทรี", "11.2 km", "-"),
    ("บ่อพลอย - หนองปรือ VDR", "39.0 km", "-"),
    ("ลาดหญ้า - ไมด้า รีสอร์ท", "22.2 km", "-"),
    ("กาญ - หนองบัว ม.6", "16.3 km", "-"),
    ("พนมทวน - ดอนตาเพชร ม.1", "7.1 km", "-"),
    ("กาญ - ด่านมะขามเตี้ย", "32.7 km", "-"),
    ("กาญ - เขาปูน", "4.1 km", "-"),
    ("เขาน้อย - รางสาลี่", "11.6 km", "-"),
    ("ชะแล - สังขละบุรี", "51.0 km", "-"),
    ("Exดอนแสลบ - Exเลาขวัญ", "39.0 km", "-"),
    ("พนมทวน - แยกรางหวาย", "13.5 km", "-"),
    ("กาญ - เขาป่าห้าม", "49.8 km", "-"),
    ("เลาขวัญ - หนองปรือ", "41.5 km", "-"),
    ("พนมทวน - หนองสาหร่าย ม.4", "14.6 km", "-"),
    ("ลาดหญ้า - ช่องสะเดา", "27.9 km", "-"),
    ("ช่องสะเดา - ท่าเสา", "18.4 km", "-"),
    ("ท่าเสา - ป่าห้าม", "8.3 km", "-"),
    ("ดอนตาเพชร ม.6 - ดอนแสลบ ม.8", "13.5 km", "-"),
    ("กาญ - หนองบัว ม.7", "28.0 km", "-"),
    ("วังมะสัง - เขื่อนศรี", "11.3 km", "-"),
    ("วังมะสัง - ท่ากระดานม.1", "13.3 km", "-"),
    ("RTด่านมะขามเตี้ย - RTหนองไผ่", "10.2 km", "-"),
    ("พนมทวน - ตลาดเขต", "28.8 km", "-"),
    ("ตลาดเขต - ดอนแสลบ ม.2", "16.9 km", "-"),
    ("ท่ามะกา - RTพงตึก", "7.3 km", "-"),
    ("ดอนแสลบ ม.2 - RTหนองประดู่ ม.4", "19.0 km", "-"),
    ("ท่ากระดาน ม.4 - ช่องสะเดา ม.3", "18.4 km", "-"),
    ("ท่ากระดาน ม.4 - เขาวังมะสัง", "13.5 km", "-"),
    ("กาญ - พนมทวน", "24.0 km", "-"),
    ("บ่อพลอย - หลุมรัง ม.1", "27.5 km", "-"),
    ("กาญ - บ้านเก่า ม.9", "44.0 km", "-"),
    ("กาญ - ลิ้นช้าง", "1.4 km", "-"),
    ("กาญ - พุน้ำร้อน", "74.0 km", "-"),
    ("ทองผาภูมิ - ห้วยเขย่ง ม.8", "20.9 km", "-"),
    ("ห้วยเขย่ง ม.8 - ห้วยเขย่ง ม.2", "7.9 km", "-"),
    ("กาญ - อิตาเลี่ยน", "76.0 km", "-"),
    ("บ้านเก่า ม.9 - พุน้ำร้อน", "30.0 km", "-"),
    ("พุน้ำร้อน - อิตาเลี่ยน", "2.0 km", "-"),
    ("ท่าเรือ - อุโลกสี่หมื่น", "9.1 km", "-"),
    ("ศรีมงคล - บ้องตี้", "35.7 km", "-"),
    ("ทองผาภูมิ - ชะแล", "30.1 km", "-"),
    ("ทองผาภูมิ - สะพานข้ามสุด", "19.2 km", "-"),
    ("สะพานข้ามสุด - ชะแล", "15.0 km", "-"),
    ("ทองผาภูมิ - ท่าขนุน", "18.2 km", "-"),
    ("ดอนแสลบ - เลาขวัญ", "39.2 km", "-"),
    ("พงตึก - โคกบอง", "4.6 km", "-"),
    ("กาญ - กลอนโด ม.2 - วังเย็น", "36.4 km", "-"),
    ("ไทรโยค ม.7 - วังเขมร", "14.0 km", "-"),
    ("สามสิบหาบ - ท่าไม้ ม.4", "11.6 km", "-"),
    ("สามสิบหาบ - หนองตากยา", "31.1 km", "-"),
    ("RTอุโลกสี่หมื่น - หนองลาน ม.4", "12.4 km", "-"),
    ("กาญ - ลาดหญ้า ม.3", "23.3 km", "-"),
    ("กาญ - หนองหญ้า", "14.7 km", "-"),
    ("ค่ายสุรศรี - ลาดหญ้า", "8.8 km", "-"),
    ("แยกม่วงชุม - บ้านถ้ำ", "5.0 km", "-"),
    ("ท่าม่วง - เขาน้อย", "10.9 km", "-"),
    ("กาญ - ยางเกาะ", "25.0 km", "-"),
    ("หนองกุ่ม ม.7 - หนองกุ่ม ม.1", "11.1 km", "-"),
    ("หนองกุ่ม ม.7 - ลาดหญ้า ม.3", "7.6 km", "-"),
    ("กาญ - บ่อพลอย", "51.0 km", "-"),
    ("กาญ - แสงชูโต", "30.0+ km", "-"),
    ("ชะแล - สังขละ", "52.0 km", "-"),
    ("พิพิธภัณฑ์บ้านเก่า - สิงห์ ม.1", "9.3 km", "-"),
    ("ท่าม่วง - รางสาลี่", "22.9 km", "-"),
    ("วังเขมร - ทองผาภูมิ", "65.9 km", "-"),
    ("เลาขวัญ - ห้วยยาง", "33.3 km", "-"),
    ("ลาดหญ้า - พาวิเลียม", "9.7 km", "-"),
    ("พนมทวน - ชุมสายพังตรุ", "11.1 km", "-"),
    ("ลาดหญ้า - เขื่อน", "55.7 km", "-"),
    ("ท่าโป่ง - ป่าห้าม", "15.5 km", "-"),
    ("ดอนแสลย - หนองประดู่ ม.4", "19.2 km", "-"),
    ("ท่าม่วง - ดอนคราม", "8.1 km", "-"),
    ("กาญ - ม่วงชุม", "18.0 km", "-"),
    ("ป่าห้าม - สิงห์ ม.4", "24.1 km", "-"),
    ("RTป่าห้าม - ศรีมงคล - บ้องตี้", "56.0 km", "-"),
    ("ป่าห้าม - ศรีมงคล", "20.6 km", "-"),
    ("Oltป่าห้าม - บ้องตี้", "25.6 km", "-"),
    ("ป่าห้าม - สามัคคีธรรม", "39.9 km", "-"),
    ("ช่องด่าน - oltยางสูง", "14.0 km", "-"),
    ("บ้านเก่า ม.9 - ลำทหาร", "7.4 km", "-"),
    ("วังกระแจะ - oltต้นมะม่วง", "14.1 km", "-"),
    ("ท่าม่วง - winetหนองรี", "11.2 km", "-"),
    ("เขื่อนศรี - oltน้ำมุด", "34.0 km", "-"),
    ("ดอนแสลบ - winetสระลงเรือ", "7.2 km", "-"),
    ("หนองฝ้าย - sg300หนองปลิง ม.8", "6.0 km", "-"),
    ("หนองปรือ - oltลำอีซู", "17.6 km", "-"),
    ("ห้วยกระเจา ม.3 - oltวังไผ่ ม.7", "9.7 km", "-"),
    ("วังเขมร - ไทรโยค ม.2", "17.7 km", "-"),
    ("ไทรโยค ม.2 - ลิ้นถิ่น", "11.1 km", "-"),
    ("พฤษากาญ - oltแก่งเสี้ยน", "12.9 km", "-"),
    ("พฤษากาญ - สถานพินิจ", "14.7 km", "-"),
    ("สถานพินิจ - oltแก่งเสี้ยน", "1.8 km", "-"),
    ("ป่าห้าม - เลคเฮฟเว่น", "8.6 km", "-"),
    ("ป่าห้าม - dslam ลุ่มผึ้ง", "5.4 km", "-"),
    ("LPE-พุเลียบ - LPE-ป่าห้าม", "32.7 km", "-"),
    ("ป่าห้าม - วังโพธิ์", "3.6 km", "-"),
    ("บ้านเก่าม.1 - สิงห์ม.1", "10.2 km", "-"),
    ("ดอนแสลบ - ตลาดเขต", "11.4 km", "-"),
    ("SG300 บ้องตี้ - ร.รทุ่งมะเซอย่อ", "12.6 km", "-"),
    ("Lpeด่านมะขามเตี้ย - oltพระธาตุโป่งนก", "4.8 km", "-"),
    ("ป่าห้าม - base หนองสามพราน", "23.4 km", "-"),
    ("Rt หนองโรง - ชุมสายพนมทวน", "11.9 km", "-"),
    ("หนองประดู่ม.4 - ฟาร์มโปร่งไหม", "1.8688 km", "-"),
    ("ท่าม่วง - แสงชูโต", "15.2 km", "-"),
    ("แสงชูโต - ท่ามะกา", "9.1 km", "-"),
    ("บ่อพลอย - sw24 kช่องด่าน", "8.9 km", "-"),
    ("ลาดหญ้า - olt พุพรม", "37.2 km", "-"),
    ("กาญ - ราชภัฏ", "18.8 km", "-"),
    ("ลาดหญ้า - บ่อพลอย", "33.0 km", "-"),
    ("กาญ - olt หนองสองตอน", "14.0 km", "-"),
    ("olt เขาปูน - APE2 เมือง", "11.2 km", "-"),
    ("บ้านเก่าม.9 - olt ตะเคียนงาม", "26.5 km", "-"),
    ("กาญ - สุราทิพย์พระราช", "29.7 km", "-"),
    ("ชุมสายลาดหญ้า - ลาดหญ้าม.3", "13.7 km", "-"),
    ("กาญ - บิ๊กc", "5.5 km", "-")
]

circuit_list = [
    ("3452J1796", "พี่ปุ๋ย"),
    ("3452J1425, 3452J3606", "หวานเย็น"),
    ("3452J1426", "น้าแดง"),
    ("3451J9174", "พี่นก"),
    ("3451J2660", "นุ่น"),
    ("3452J8002", "ตาคิด"),
    ("3451J5651", "อ.เดชา"),
    ("3452J2060", "บ้านอ้อน"),
    ("3451J4720", "บ้านเป้")
]

all_categories = {
    "🍏 ZTE C300 Series": c300_commands,
    "⚡ ZTE C600 Series": c600_commands,
    "🟢 SW ZTE ประชารัฐ": zte_pracharath_commands,
    "🟣 Extreme Switch": extreme_commands,
    "🔵 Cisco SG300": sg300_commands,
    "🔴 Huawei Switch": huawei_commands,
    "📞 ชุมสาย Fixline": fixline_commands,
    "📟 DSLAM Forth": dslam_commands,
    "📍 IP OLT ในพื้นที่": olt_ip_commands,
    "📡 Uplink & Initial Config": system_commands,
    "💻 Windows CMD Shortcuts": pc_cmd_commands,
    "🤖 Javis Line Bot": javis_bot_commands
}


# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.markdown("## 📌 เมนูหลัก")

selected_menu = None
with st.sidebar.expander("⚙️ Config", expanded=True):
    selected_menu = st.radio("เลือกหมวดหมู่การใช้งาน:", list(all_categories.keys()), label_visibility="collapsed")

with st.sidebar.expander("🌐 Web", expanded=False):
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

with st.sidebar.expander("📏 ระยะสาย Optic", expanded=False):
    st.markdown("#### 🛠️ ข้อมูลระยะสาย OFC หน้างาน")
    search_ofc = st.text_input("🔍 ค้นหาเส้นทางสาย OFC:", "", key="search_ofc_sidebar").strip().lower()
    
    filtered_ofc = [
        row for row in ofc_distances 
        if search_ofc in row[0].lower() or search_ofc in row[1].lower() or search_ofc in row[2].lower()
    ]
    
    if filtered_ofc:
        for route, dist, note in filtered_ofc:
            if note != "-":
                st.markdown(f"• **{route}** : `{dist}`\n  *(หมายเหตุ: {note})*")
            else:
                st.markdown(f"• **{route}** : `{dist}`")
    else:
        st.write("ไม่พบข้อมูลเส้นทางที่ค้นหา")

with st.sidebar.expander("🆔 เลขวงจรลูกค้า", expanded=False):
    for code, owner in circuit_list:
        st.markdown(f"• `{code}` : {owner}")

with st.sidebar.expander("📍 ที่อยู่ NT", expanded=False):
    st.markdown("**ตึกเก่า:**\n111/2 ถ.อู่ทอง ต.บ้านเหนือ อ.เมือง จ.กาญจนบุรี 71000")
    st.markdown("---")
    st.markdown("**ตึกเขาตอง:**\n1/11 ม.9 ต.ปากแพรก อ.เมือง จ.กาญจนบุรี 71000")

with st.sidebar.expander("📞 IP Phone", expanded=False):
    st.markdown("• `sipp11.totbb.net`")
    st.markdown("• `sipp12.totbb.net`")
    st.markdown("• `sipp13.totbb.net`")
    st.markdown("• `172.31.83.4` (อยุธยา)")
    st.markdown("• `172.31.92.4` (เพชร)")
    st.markdown("• `172.30.202.4`")

with st.sidebar.expander("🔐 SecureCRT", expanded=False):
    st.markdown("• `10.227.102.190` *(ใช้อยู่)*")
    st.markdown("• `10.224.55.121`")
    st.markdown("• `10.224.55.125`")
    st.markdown("• `10.224.55.129`")


# --- 3. MAIN CONTENT DISPLAY & DASHBOARD SEARCH ---

st.markdown("<h1 style='color: #1a7f37; margin-top: -10px; font-weight: 800;'>💻 ZTE OLT & PC COMMAND CENTER</h1>", unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])

with col_input:
    dash_search = st.text_input(
        "ค้นหาข้ามระบบ", 
        placeholder="🔍 พิมพ์คำค้นหาด่วน เช่น โป่งช้าง, ท่าเสา, OLT, nodelist, IP...", 
        label_visibility="collapsed",
        key="dash_global_search"
    ).strip()

with col_btn:
    search_clicked = st.button("🔍 ค้นหา", use_container_width=True, type="primary")

st.markdown("---")

if dash_search:
    st.markdown(f"### 🎯 ผลการค้นหาสำหรับ: `<mark class='highlight'>{dash_search}</mark>`", unsafe_allow_html=True)
    found_global = False

    matched_ofc = [row for row in ofc_distances if dash_search.lower() in row[0].lower() or dash_search.lower() in row[1].lower() or dash_search.lower() in row[2].lower()]
    if matched_ofc:
        found_global = True
        st.markdown("#### 📏 พบใน: ระยะสาย Optic (OFC)")
        for route, dist, note in matched_ofc:
            h_route = highlight_text(route, dash_search)
            h_note = highlight_text(note, dash_search)
            st.markdown(f"• **{h_route}** : `{dist}` (หมายเหตุ: {h_note})", unsafe_allow_html=True)
        st.markdown("---")

    matched_circuits = [c for c in circuit_list if dash_search.lower() in c[0].lower() or dash_search.lower() in c[1].lower()]
    if matched_circuits:
        found_global = True
        st.markdown("#### 🆔 พบใน: เลขวงจรลูกค้า")
        for code, owner in matched_circuits:
            h_code = highlight_text(code, dash_search)
            h_owner = highlight_text(owner, dash_search)
            st.markdown(f"• **{h_code}** : {h_owner}", unsafe_allow_html=True)
        st.markdown("---")

    for cat_name, cat_dict in all_categories.items():
        cat_matches = []
        for sub_cat, items in cat_dict.items():
            for desc, code in items:
                if dash_search.lower() in desc.lower() or dash_search.lower() in code.lower():
                    cat_matches.append((sub_cat, desc, code))
        
        if cat_matches:
            found_global = True
            st.markdown(f"#### ⚙️ หมวด Config: {cat_name}")
            for sub_cat, desc, code in cat_matches:
                h_desc = highlight_text(desc, dash_search)
                st.markdown(f"📌 [{sub_cat}] **{h_desc}**", unsafe_allow_html=True)
                
                lang = "routeros"
                if cat_name in ["📞 ชุมสาย Fixline", "📟 DSLAM Forth", "📍 IP OLT ในพื้นที่", "🤖 Javis Line Bot"]:
                    lang = "text"
                elif cat_name == "💻 Windows CMD Shortcuts":
                    lang = "batch"
                    
                st.code(code, language=lang)
            st.markdown("---")

    if not found_global:
        st.warning(f"❌ ไม่พบข้อมูลใดๆ ที่ตรงกับคำว่า '{dash_search}'")

else:
    def render_command_section(title, command_dict, lang="routeros"):
        st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
        
        sec_search = st.text_input(f"🔍 ค้นหาเฉพาะหมวดนี้:", "", key=f"search_{title}").strip().lower()
        
        found_any = False
        for sub_cat, items in command_dict.items():
            filtered = [
                i for i in items 
                if sec_search in i[0].lower() or sec_search in i[1].lower()
            ]
            
            if filtered:
                found_any = True
                st.markdown(f"### {sub_cat}")
                for desc, code in filtered:
                    h_desc = highlight_text(desc, sec_search) if sec_search else desc
                    if len(code) > 500 or "\n" in code:
                        st.markdown(f"📌 **{h_desc}**", unsafe_allow_html=True)
                        st.code(code, language=lang)
                    else:
                        c1, c2 = st.columns([1.1, 1.9])
                        with c1: st.markdown(f"📌 **{h_desc}**", unsafe_allow_html=True)
                        with c2: st.code(code, language=lang)
        
        if not found_any and sec_search:
            st.warning(f"ไม่พบข้อมูลคำสั่งที่ตรงกับ '{sec_search}' ในหมวดนี้")

    if selected_menu == "🍏 ZTE C300 Series":
        render_command_section("🍏 หมวดคำสั่งสำหรับตู้ซีรีส์ ZTE C300", c300_commands)

    elif selected_menu == "⚡ ZTE C600 Series":
        render_command_section("⚡ หมวดคำสั่งสำหรับตู้ซีรีส์ใหม่ ZTE C600", c600_commands)

    elif selected_menu == "🟢 SW ZTE ประชารัฐ":
        render_command_section("🟢 หมวดคำสั่งและรหัสผ่าน SW ZTE ประชารัฐ", zte_pracharath_commands)

    elif selected_menu == "🟣 Extreme Switch":
        render_command_section("🟣 หมวดคำสั่งสำหรับ Extreme Switch", extreme_commands)

    elif selected_menu == "🔵 Cisco SG300":
        render_command_section("🔵 หมวดคำสั่งสำหรับ Cisco SG300", sg300_commands)

    elif selected_menu == "🔴 Huawei Switch":
        render_command_section("🔴 หมวดคำสั่งสำหรับ Huawei Switch", huawei_commands)

    elif selected_menu == "📞 ชุมสาย Fixline":
        render_command_section("📞 หมวดคำสั่งระบบชุมสาย Fixline", fixline_commands, lang="text")

    elif selected_menu == "📟 DSLAM Forth":
        render_command_section("📟 ข้อมูลการเชื่อมต่อ DSLAM Forth", dslam_commands, lang="text")

    elif selected_menu == "📍 IP OLT ในพื้นที่":
        render_command_section("📍 ข้อมูลหมายเลข IP ของตู้ OLT ในพื้นที่", olt_ip_commands, lang="text")

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
