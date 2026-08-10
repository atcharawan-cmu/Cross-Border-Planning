import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. APP CONFIGURATION & THEME ---
st.set_page_config(
    page_title="BorderLoad AI Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Light Theme & Cleaner Look
st.markdown('''
    <style>
        .stApp { background-color: #F8F9FA; color: #212529; }
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E9ECEF; }
        [data-testid="stMetricValue"] { color: #0056B3; font-weight: 700; }
        [data-testid="stMetricLabel"] { color: #495057; font-size: 1.1rem; font-weight: 500; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E9ECEF; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        h1, h2, h3, h4 { color: #212529; font-weight: 600; }
        .stAlert { background-color: #E3F2FD; color: #0D47A1; border-left: 5px solid #1976D2; }
        .stButton>button[kind="primary"] { background-color: #28A745; color: white; border: none; font-weight: 600; }
        .stButton>button[kind="primary"]:hover { background-color: #218838; }
    </style>
''', unsafe_allow_html=True)


# --- 2. LANGUAGE DICTIONARY ---
LANG = {
    'EN': {
        'title': '🚚 BorderLoad AI: Cross-Border Consolidation Planner',
        'sidebar_title': '⚙️ Configuration',
        'lang_select': 'Language / ภาษา',
        'scenario': 'Active Scenario',
        'scenarios': ['Normal Operating', 'Disruption: Border Wait (6 hrs)', 'Disruption: Driver Unavailable', 'Incomplete Data'],
        'priority': 'Optimization Priority',
        'priorities': ['Minimum Cost', 'Maximum On-Time Delivery'],
        'new_order': '➕ Add New Order',
        'origin': 'Origin',
        'dest': 'Destination',
        'weight': 'Weight (kg)',
        'vol': 'Volume (cbm)',
        'cargo': 'Cargo Type',
        'add_btn': 'Add Order',
        'kpi_title': '📊 Key Performance Indicators',
        'utilization': 'Truck Utilization',
        'cost': 'Cost per Ton-km',
        'ontime': 'On-Time Probability',
        'empty': 'Empty Return %',
        'ai_plan': '🧠 AI Dispatch Recommendation',
        'truck': 'Truck',
        'driver': 'Driver',
        'route': 'Route',
        'eta': 'Predicted ETA',
        'action': '🧑‍💻 Human Override',
        'accept': '✅ Approve Plan',
        'reject': '❌ Reject & Recalculate',
        'modify': '✏️ Modify Manual',
        'reasoning': '💡 AI Reasoning & Assumptions',
        'reason_text_normal': "AI optimized for cost. Orders grouped by destination. Cargo compatibility checked (Chemicals isolated).",
        'reason_text_disruption': "ALERT: 6-hour border delay detected. AI prioritized urgent shipments and re-routed to avoid congestion, increasing cost slightly to maintain 92% on-time delivery.",
        'reason_text_priority': "Priority shifted to On-Time Delivery. AI deployed additional trucks to ensure faster transit, reducing truck utilization to 85%.",
        'warning': '⚠️ Alerts',
        'warn_msg': 'Urgent orders detected. Priority adjustment recommended.',
        'chart_title': 'Estimated Delivery Status',
        'trip1_dest': 'Vientiane',
        'trip1_cargo': '3 Consolidated Orders (Electronics, Food)',
        'trip2_dest': 'Kuala Lumpur',
        'trip2_cargo': '5 Consolidated Orders (*Chemicals isolated*)'
    },
    'TH': {
        'title': '🚚 BorderLoad AI: ระบบวางแผนและจัดกลุ่มขนส่งข้ามแดน',
        'sidebar_title': '⚙️ ตั้งค่าระบบ',
        'lang_select': 'Language / ภาษา',
        'scenario': 'จำลองสถานการณ์',
        'scenarios': ['สถานการณ์ปกติ (Normal)', 'เหตุขัดข้อง: ด่านตรวจล่าช้า (6 ชม.)', 'เหตุขัดข้อง: คนขับไม่พร้อม', 'ข้อมูลไม่สมบูรณ์'],
        'priority': 'เป้าหมายหลัก (Optimization)',
        'priorities': ['เน้นต้นทุนต่ำสุด', 'เน้นส่งตรงเวลาที่สุด'],
        'new_order': '➕ เพิ่มออเดอร์ใหม่',
        'origin': 'ต้นทาง',
        'dest': 'ปลายทาง',
        'weight': 'น้ำหนัก (กก.)',
        'vol': 'ปริมาตร (ลบ.ม.)',
        'cargo': 'ประเภทสินค้า',
        'add_btn': 'เพิ่มข้อมูล',
        'kpi_title': '📊 ตัวชี้วัดประสิทธิภาพ (KPIs)',
        'utilization': 'อัตราใช้พื้นที่รถ',
        'cost': 'ต้นทุนต่อตัน-กม.',
        'ontime': 'โอกาสส่งตรงเวลา',
        'empty': 'สัดส่วนวิ่งรถเปล่า',
        'ai_plan': '🧠 แผนจัดส่งแนะนำโดย AI',
        'truck': 'รถบรรทุก',
        'driver': 'คนขับ',
        'route': 'เส้นทาง',
        'eta': 'เวลาถึงที่หมาย (ETA)',
        'action': '🧑‍💻 การตัดสินใจ (Human Override)',
        'accept': '✅ อนุมัติแผนนี้',
        'reject': '❌ ปฏิเสธและคำนวณใหม่',
        'modify': '✏️ แก้ไขด้วยตนเอง',
        'reasoning': '💡 เหตุผลของ AI และสมมติฐาน',
        'reason_text_normal': "AI เน้นลดต้นทุนเป็นหลัก จัดกลุ่มตามปลายทาง ตรวจสอบประเภทสินค้าเรียบร้อย (แยกสินค้าเคมีออกจากอาหาร)",
        'reason_text_disruption': "แจ้งเตือน: พบความล่าช้าหน้าด่าน 6 ชม. AI ปรับให้ส่งสินค้าด่วนก่อนและเปลี่ยนเส้นทางเพื่อเลี่ยงรถติด ทำให้ต้นทุนเพิ่มขึ้นเล็กน้อยเพื่อรักษาการส่งตรงเวลาที่ 92%",
        'reason_text_priority': "เปลี่ยนเป้าหมายเป็น 'เน้นส่งตรงเวลา' AI เพิ่มจำนวนรถเพื่อให้ส่งได้เร็วขึ้น ทำให้อัตราการบรรทุกลดลงเหลือ 85%",
        'warning': '⚠️ การแจ้งเตือน',
        'warn_msg': 'พบออเดอร์เร่งด่วน แนะนำให้ปรับเป้าหมายเป็นเน้นส่งตรงเวลา',
        'chart_title': 'สถานะการส่งมอบโดยประมาณ',
        'trip1_dest': 'เวียงจันทน์',
        'trip1_cargo': 'รวม 3 ออเดอร์ (อิเล็กทรอนิกส์, อาหาร)',
        'trip2_dest': 'กัวลาลัมเปอร์',
        'trip2_cargo': 'รวม 5 ออเดอร์ (*แยกสินค้าเคมีออกจากกลุ่ม*)'
    }
}


# --- 3. MOCK DATA GENERATION (Simulated AI Output) ---
def generate_ai_results(scenario, priority):
    base_util = 92
    base_cost = 1.85
    base_ontime = 95
    base_empty = 15
    
    if "Disruption" in scenario or "เหตุขัดข้อง" in scenario:
        base_ontime -= 18
        base_cost += 0.4
    if priority == 'Maximum On-Time Delivery' or priority == 'เน้นส่งตรงเวลาที่สุด':
        base_ontime += 10
        base_cost += 0.2
        base_util -= 7
        
    return {
        'util': min(100, max(0, base_util + np.random.randint(-3, 4))),
        'cost': max(1.0, base_cost + np.random.uniform(-0.1, 0.2)),
        'ontime': min(100, max(0, base_ontime + np.random.randint(-2, 3))),
        'empty': max(0, base_empty + np.random.randint(-5, 5))
    }

# --- 4. MAIN LAYOUT ---

# Sidebar
with st.sidebar:
    lang_choice = st.radio("Language / ภาษา", ['English', 'ภาษาไทย'], horizontal=True)
    l = LANG['EN'] if lang_choice == 'English' else LANG['TH']
    
    st.divider()
    
    st.header(l['sidebar_title'])
    
    selected_scenario = st.selectbox(l['scenario'], l['scenarios'])
    selected_priority = st.select_slider(l['priority'], options=l['priorities'])
    
    st.divider()
    st.subheader(l['new_order'])
    with st.form("new_order_form"):
        o_origin = st.selectbox(l['origin'], ["Thailand (Lamphun)", "Thailand (Bangkok)"])
        o_dest = st.selectbox(l['dest'], ["Malaysia (Kuala Lumpur)", "Laos (Vientiane)", "Vietnam (Hanoi)", "China (Kunming)"])
        o_weight = st.number_input(l['weight'], min_value=100, max_value=5000, value=1000)
        o_vol = st.number_input(l['vol'], min_value=1.0, max_value=20.0, value=5.0)
        o_cargo = st.selectbox(l['cargo'], ["Electronics", "Textiles", "Food", "Chemicals"])
        submitted = st.form_submit_button(l['add_btn'], use_container_width=True)
        if submitted:
            st.success("Order Added (Simulation)")

# Title
st.title(l['title'])

# Simulate AI processing
ai_metrics = generate_ai_results(selected_scenario, selected_priority)

# Warning Section
if "Disruption" in selected_scenario or "ด่วน" in l['warn_msg'] or "เหตุขัดข้อง" in selected_scenario:
    st.warning(f"**{l['warning']}:** {l['warn_msg']}")

# KPIs
st.subheader(l['kpi_title'])
col1, col2, col3, col4 = st.columns(4)
col1.metric(l['utilization'], f"{ai_metrics['util']}%", f"{np.random.randint(-2,3)}%")
col2.metric(l['cost'], f"฿{ai_metrics['cost']:.2f}", f"{np.random.uniform(-0.1,0.1):.2f}")
col3.metric(l['ontime'], f"{ai_metrics['ontime']}%", f"{np.random.randint(-5,5)}%")
col4.metric(l['empty'], f"{ai_metrics['empty']}%", f"{np.random.randint(-2,2)}%", delta_color="inverse")

st.divider()

# Main Dashboard Area
col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader(l['ai_plan'])
    
    with st.container(border=True):
        st.markdown(f"#### 📦 Trip 1: Lamphun ➡️ {l['trip1_dest']}")
        st.write(f"**{l['truck']}:** TH-001 (Capacity 5T) &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** Somchai")
        st.write(f"**Cargo:** {l['trip1_cargo']}")
        st.write(f"**{l['eta']}:** 2026-08-14 09:30 AM")
    
    with st.container(border=True):
        st.markdown(f"#### 📦 Trip 2: Lamphun ➡️ {l['trip2_dest']}")
        st.write(f"**{l['truck']}:** TH-002 (Capacity 8T) &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** Wichai")
        st.write(f"**Cargo:** {l['trip2_cargo']}")
        st.write(f"**{l['eta']}:** 2026-08-16 14:00 PM")
    
    st.subheader(l['chart_title'])
    status_data = pd.DataFrame({
        'Status': ['On-Time', 'Delayed', 'Critical'],
        'Count': [ai_metrics['ontime'], 100 - ai_metrics['ontime'] - 2, 2]
    })
    
    # Chart
    fig = px.bar(status_data, x='Status', y='Count', color='Status', 
                 color_discrete_map={'On-Time':'#28A745', 'Delayed':'#FFC107', 'Critical':'#DC3545'})
    fig.update_layout(
        height=300, 
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title=None,
        yaxis_title="Orders"
    )
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.subheader(l['action'])
    st.button(l['accept'], use_container_width=True, type="primary")
    st.button(l['modify'], use_container_width=True)
    st.button(l['reject'], use_container_width=True)
    
    st.divider()
    st.subheader(l['reasoning'])
    
    if "Disruption" in selected_scenario or "เหตุขัดข้อง" in selected_scenario:
        st.info(l['reason_text_disruption'], icon="💡")
    elif selected_priority == l['priorities'][1]:
        st.info(l['reason_text_priority'], icon="💡")
    else:
        st.info(l['reason_text_normal'], icon="💡")
