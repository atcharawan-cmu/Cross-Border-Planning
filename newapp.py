import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. APP CONFIGURATION & THEME ---
st.set_page_config(page_title="BorderLoad AI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
    <style>
        p, .stMarkdown p, .stText, label, .stAlert p { font-size: 18px !important; }
        .stButton>button { font-size: 18px !important; }
        .stApp { background-color: #F8F9FA; color: #212529; }
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E9ECEF; }
        [data-testid="stMetricValue"] { color: #0056B3; font-weight: 700; font-size: 2.2rem !important; }
        [data-testid="stMetricLabel"] { color: #495057; font-size: 1.2rem !important; font-weight: 500; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E9ECEF; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        h1, h2, h3, h4 { color: #212529; font-weight: 600; }
        .stAlert { background-color: #E3F2FD; color: #0D47A1; border-left: 5px solid #1976D2; }
        .stButton>button[kind="primary"] { background-color: #28A745; color: white; border: none; font-weight: 600; }
        .stButton>button[kind="primary"]:hover { background-color: #218838; }
        /* ขยายขนาดตัวหนังสือใน Tab */
        button[data-baseweb="tab"] { font-size: 20px !important; font-weight: 600 !important; }
    </style>
''', unsafe_allow_html=True)

# --- 2. SESSION STATE (ระบบความจำของตารางและ Dashboard) ---
if 'new_orders' not in st.session_state:
    st.session_state.new_orders = 0

if 'orders_df' not in st.session_state:
    # สร้างข้อมูลจำลองเริ่มต้น 5 รายการ
    st.session_state.orders_df = pd.DataFrame({
        'Order_ID': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
        'Origin': ['Thailand (Lamphun)', 'Thailand (Lamphun)', 'Thailand (Lamphun)', 'Thailand (Lamphun)', 'Thailand (Lamphun)'],
        'Destination': ['Laos (Vientiane)', 'Malaysia (Kuala Lumpur)', 'Laos (Vientiane)', 'Malaysia (Kuala Lumpur)', 'Vietnam (Hanoi)'],
        'Weight_kg': [1200, 850, 2100, 500, 1800],
        'Cargo_Type': ['Electronics', 'Chemicals', 'Food', 'Textiles', 'Electronics'],
        'Status': ['Assigned (Trip 1)', 'Assigned (Trip 2)', 'Assigned (Trip 1)', 'Assigned (Trip 2)', 'Assigned (Trip 3)'],
        'ETA': ['2026-08-14 09:30', '2026-08-16 14:00', '2026-08-14 09:30', '2026-08-16 14:00', '2026-08-15 12:00']
    })

# --- 3. LANGUAGE DICTIONARY ---
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
        'origin': 'Origin', 'dest': 'Destination', 'weight': 'Weight (kg)', 'vol': 'Volume (cbm)', 'cargo': 'Cargo Type',
        'add_btn': 'Add Order',
        'tab_dash': '📊 AI Dashboard', 'tab_table': '📋 All Orders',
        'kpi_title': 'Key Performance Indicators',
        'utilization': 'Truck Utilization', 'cost': 'Cost per Ton-km', 'ontime': 'On-Time Probability', 'empty': 'Empty Return %',
        'ai_plan': '🧠 AI Dispatch Recommendation',
        'truck': 'Truck', 'driver': 'Driver', 'eta': 'Predicted ETA',
        'action': '🧑‍💻 Human Override',
        'accept': '✅ Approve Plan', 'reject': '❌ Reject & Recalculate', 'modify': '✏️ Modify Manual',
        'reasoning': '💡 AI Reasoning & Assumptions',
        'reason_text_normal': "AI optimized for cost. Cargo compatibility checked (Chemicals isolated).",
        'reason_text_disruption': "ALERT: 6-hour delay. AI prioritized urgent shipments and re-routed.",
        'reason_text_priority': "Priority shifted to On-Time Delivery. AI deployed additional trucks.",
        'warning': '⚠️ Alerts',
        'warn_msg': 'Urgent orders detected. Priority adjustment recommended.',
        'chart_title': 'Estimated Delivery Status',
        'trip1_dest': 'Vientiane', 'trip1_cargo': 'Consolidated Orders (Electronics, Food)',
        'trip2_dest': 'Kuala Lumpur', 'trip2_cargo': 'Consolidated Orders (*Chemicals isolated*)'
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
        'origin': 'ต้นทาง', 'dest': 'ปลายทาง', 'weight': 'น้ำหนัก (กก.)', 'vol': 'ปริมาตร (ลบ.ม.)', 'cargo': 'ประเภทสินค้า',
        'add_btn': 'เพิ่มข้อมูล',
        'tab_dash': '📊 แดชบอร์ด AI', 'tab_table': '📋 รายการออเดอร์ทั้งหมด',
        'kpi_title': 'ตัวชี้วัดประสิทธิภาพ (KPIs)',
        'utilization': 'อัตราใช้พื้นที่รถ', 'cost': 'ต้นทุนต่อตัน-กม.', 'ontime': 'โอกาสส่งตรงเวลา', 'empty': 'สัดส่วนวิ่งรถเปล่า',
        'ai_plan': '🧠 แผนจัดส่งแนะนำโดย AI',
        'truck': 'รถบรรทุก', 'driver': 'คนขับ', 'eta': 'เวลาถึงที่หมาย (ETA)',
        'action': '🧑‍💻 การตัดสินใจ (Human Override)',
        'accept': '✅ อนุมัติแผนนี้', 'reject': '❌ ปฏิเสธและคำนวณใหม่', 'modify': '✏️ แก้ไขด้วยตนเอง',
        'reasoning': '💡 เหตุผลของ AI และสมมติฐาน',
        'reason_text_normal': "AI เน้นลดต้นทุนเป็นหลัก จัดกลุ่มตามปลายทาง ตรวจสอบประเภทสินค้าเรียบร้อย (แยกสินค้าเคมีออกจากอาหาร)",
        'reason_text_disruption': "แจ้งเตือน: พบความล่าช้าหน้าด่าน 6 ชม. AI ปรับเส้นทางเพื่อเลี่ยงรถติดและรักษาเวลา",
        'reason_text_priority': "เปลี่ยนเป้าหมายเป็น 'เน้นส่งตรงเวลา' AI เพิ่มจำนวนรถเพื่อให้ส่งได้เร็วขึ้น",
        'warning': '⚠️ การแจ้งเตือน',
        'warn_msg': 'พบออเดอร์เร่งด่วน แนะนำให้ปรับเป้าหมายเป็นเน้นส่งตรงเวลา',
        'chart_title': 'สถานะการส่งมอบโดยประมาณ',
        'trip1_dest': 'เวียงจันทน์', 'trip1_cargo': 'ออเดอร์จัดกลุ่ม (อิเล็กทรอนิกส์, อาหาร)',
        'trip2_dest': 'กัวลาลัมเปอร์', 'trip2_cargo': 'ออเดอร์จัดกลุ่ม (*แยกสินค้าเคมีออกจากกลุ่ม*)'
    }
}

# --- 4. AI LOGIC & CALCULATIONS ---
def generate_ai_results(scenario, priority, extra_orders):
    base_util = 85 + (extra_orders * 2) 
    base_cost = 1.85 - (extra_orders * 0.02) 
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
        'util': min(100, max(0, base_util)), 'cost': max(1.0, base_cost),
        'ontime': min(100, max(0, base_ontime)), 'empty': max(0, base_empty)
    }

# --- 5. SIDEBAR & FORM ---
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
            st.session_state.new_orders += 1
            new_id = f"ORD-NEW-{st.session_state.new_orders}"
            # เพิ่มข้อมูลลง DataFrame
            new_row = pd.DataFrame([{
                'Order_ID': new_id, 'Origin': o_origin, 'Destination': o_dest,
                'Weight_kg': o_weight, 'Cargo_Type': o_cargo, 
                'Status': 'Pending AI Assignment', 'ETA': 'TBD'
            }])
            st.session_state.orders_df = pd.concat([new_row, st.session_state.orders_df], ignore_index=True)
            st.success("Order Added successfully!" if lang_choice == 'English' else "เพิ่มออเดอร์สำเร็จ!")

# --- 6. MAIN LAYOUT (TABS) ---
st.title(l['title'])

# สร้าง Tabs
tab1, tab2 = st.tabs([l['tab_dash'], l['tab_table']])

# ----------------- TAB 1: DASHBOARD -----------------
with tab1:
    ai_metrics = generate_ai_results(selected_scenario, selected_priority, st.session_state.new_orders)

    if "Disruption" in selected_scenario or "ด่วน" in l['warn_msg'] or "เหตุขัดข้อง" in selected_scenario:
        st.warning(f"**{l['warning']}:** {l['warn_msg']}")

    st.subheader(l['kpi_title'])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(l['utilization'], f"{ai_metrics['util']}%", f"+{st.session_state.new_orders*2}%" if st.session_state.new_orders > 0 else "0%")
    col2.metric(l['cost'], f"฿{ai_metrics['cost']:.2f}")
    col3.metric(l['ontime'], f"{ai_metrics['ontime']}%")
    col4.metric(l['empty'], f"{ai_metrics['empty']}%")

    st.divider()

    col_main, col_side = st.columns([2, 1])
    with col_main:
        st.subheader(l['ai_plan'])
        base_orders_trip1 = 3 + st.session_state.new_orders
        base_orders_trip2 = 5
        
        with st.container(border=True):
            st.markdown(f"#### 📦 Trip 1: Lamphun ➡️ {l['trip1_dest']}")
            st.write(f"**{l['truck']}:** TH-001 (Capacity 5T) &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** Somchai")
            st.write(f"**Cargo:** {base_orders_trip1} {l['trip1_cargo']}")
            st.write(f"**{l['eta']}:** 2026-08-14 09:30 AM")
        
        with st.container(border=True):
            st.markdown(f"#### 📦 Trip 2: Lamphun ➡️ {l['trip2_dest']}")
            st.write(f"**{l['truck']}:** TH-002 (Capacity 8T) &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** Wichai")
            st.write(f"**Cargo:** {base_orders_trip2} {l['trip2_cargo']}")
            st.write(f"**{l['eta']}:** 2026-08-16 14:00 PM")
        
        st.subheader(l['chart_title'])
        status_data = pd.DataFrame({'Status': ['On-Time', 'Delayed', 'Critical'], 'Count': [ai_metrics['ontime'] + st.session_state.new_orders, 100 - ai_metrics['ontime'] - 2, 2]})
        fig = px.bar(status_data, x='Status', y='Count', color='Status', color_discrete_map={'On-Time':'#28A745', 'Delayed':'#FFC107', 'Critical':'#DC3545'})
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title=None, yaxis_title="Orders")
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader(l['action'])
        if st.button(l['accept'], use_container_width=True, type="primary"):
            # เปลี่ยนสถานะออเดอร์ใหม่เป็น Assigned เมื่อกดยอมรับ
            st.session_state.orders_df.loc[st.session_state.orders_df['Status'] == 'Pending AI Assignment', 'Status'] = 'Assigned (Trip 1)'
            st.session_state.orders_df.loc[st.session_state.orders_df['ETA'] == 'TBD', 'ETA'] = '2026-08-14 09:30'
            st.rerun()
            
        st.button(l['modify'], use_container_width=True)
        if st.button(l['reject'], use_container_width=True):
            st.session_state.new_orders = 0
            # ลบออเดอร์ที่เพิ่งเพิ่มเข้ามา (ลบแถวที่มีคำว่า ORD-NEW)
            st.session_state.orders_df = st.session_state.orders_df[~st.session_state.orders_df['Order_ID'].str.contains("ORD-NEW")]
            st.rerun()
        
        st.divider()
        st.subheader(l['reasoning'])
        if "Disruption" in selected_scenario or "เหตุขัดข้อง" in selected_scenario:
            st.info(l['reason_text_disruption'], icon="💡")
        elif selected_priority == l['priorities'][1]:
            st.info(l['reason_text_priority'], icon="💡")
        else:
            st.info(l['reason_text_normal'] + (f" (AI just assigned {st.session_state.new_orders} new orders to Trip 1)" if st.session_state.new_orders > 0 else ""), icon="💡")

# ----------------- TAB 2: DATA TABLE -----------------
with tab2:
    st.subheader(l['tab_table'])
    
    # แปลงชื่อคอลัมน์ตารางตามภาษา
    display_df = st.session_state.orders_df.copy()
    if lang_choice == 'ภาษาไทย':
        display_df.columns = ['รหัสออเดอร์', 'ต้นทาง', 'ปลายทาง', 'น้ำหนัก (กก.)', 'ประเภทสินค้า', 'สถานะจัดรถ', 'เวลาถึง (ETA)']
    
    # แสดงตารางแบบ Interactive (ผู้ใช้สามารถกดหัวตารางเพื่อเรียงลำดับได้)
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
