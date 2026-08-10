import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. APP CONFIGURATION & THEME ---
st.set_page_config(page_title="BorderLoad AI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
    <style>
        p, .stMarkdown p, .stText, label, .stAlert p { font-size: 17px !important; }
        .stButton>button { font-size: 17px !important; }
        .stApp { background-color: #F8F9FA; color: #212529; }
        [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E9ECEF; }
        [data-testid="stMetricValue"] { color: #0056B3; font-weight: 700; font-size: 2.2rem !important; }
        [data-testid="stMetricLabel"] { color: #495057; font-size: 1.1rem !important; font-weight: 500; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E9ECEF; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        h1, h2, h3, h4 { color: #212529; font-weight: 600; }
        .stAlert { background-color: #E3F2FD; color: #0D47A1; border-left: 5px solid #1976D2; }
        .stButton>button[kind="primary"] { background-color: #28A745; color: white; border: none; font-weight: 600; }
        .stButton>button[kind="primary"]:hover { background-color: #218838; }
        button[data-baseweb="tab"] { font-size: 18px !important; font-weight: 600 !important; }
    </style>
''', unsafe_allow_html=True)

# --- 2. SESSION STATE (ระบบความจำ) ---
# บันทึกข้อมูลรถและคนขับให้แก้ได้ (Human Override)
if 'trip_assignments' not in st.session_state:
    st.session_state.trip_assignments = {
        't1_truck': 'TH-001 (Capacity 5T)', 't1_driver': 'Somchai', 't1_orders': 0,
        't2_truck': 'TH-002 (Capacity 8T)', 't2_driver': 'Wichai', 't2_orders': 0,
        'other_orders': 0
    }
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if 'orders_df' not in st.session_state:
    st.session_state.orders_df = pd.DataFrame({
        'Order_ID': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
        'Origin': ['Thailand (Lamphun)'] * 5,
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
        'sidebar_title': '⚙️ Configuration', 'lang_select': 'Language / ภาษา',
        'scenario': 'Active Scenario', 'scenarios': ['Normal Operating', 'Disruption: Border Wait (6 hrs)', 'Disruption: Driver Unavailable', 'Incomplete Data'],
        'priority': 'Optimization Priority', 'priorities': ['Minimum Cost', 'Maximum On-Time Delivery'],
        'new_order': '➕ Add New Order', 'origin': 'Origin', 'dest': 'Destination', 'weight': 'Weight (kg)', 'vol': 'Volume (cbm)', 'cargo': 'Cargo Type',
        'add_btn': 'Add Order', 'tab_dash': '📊 AI Dashboard', 'tab_table': '📋 All Orders',
        'kpi_title': 'Key Performance Indicators', 'utilization': 'Truck Utilization', 'cost': 'Cost per Ton-km', 'ontime': 'On-Time Probability', 'empty': 'Empty Return %',
        'ai_plan': '🧠 AI Dispatch Recommendation', 'truck': 'Truck', 'driver': 'Driver', 'eta': 'Predicted ETA',
        'action': '🧑‍💻 Human Override', 'accept': '✅ Approve Plan', 'reject': '❌ Reject & Recalculate', 'modify': '✏️ Modify Manual',
        'reasoning': '💡 AI Reasoning & Assumptions',
        'trip1_dest': 'Vientiane', 'trip1_cargo': 'Consolidated Orders (Electronics, Food)',
        'trip2_dest': 'Kuala Lumpur', 'trip2_cargo': 'Consolidated Orders (*Chemicals isolated*)',
        'edit_title': '🛠️ Modify AI Plan', 'save_btn': '💾 Save Changes', 'cancel_btn': 'Cancel'
    },
    'TH': {
        'title': '🚚 BorderLoad AI: ระบบวางแผนและจัดกลุ่มขนส่งข้ามแดน',
        'sidebar_title': '⚙️ ตั้งค่าระบบ', 'lang_select': 'Language / ภาษา',
        'scenario': 'จำลองสถานการณ์', 'scenarios': ['สถานการณ์ปกติ (Normal)', 'เหตุขัดข้อง: ด่านตรวจล่าช้า (6 ชม.)', 'เหตุขัดข้อง: คนขับไม่พร้อม', 'ข้อมูลไม่สมบูรณ์'],
        'priority': 'เป้าหมายหลัก (Optimization)', 'priorities': ['เน้นต้นทุนต่ำสุด', 'เน้นส่งตรงเวลาที่สุด'],
        'new_order': '➕ เพิ่มออเดอร์ใหม่', 'origin': 'ต้นทาง', 'dest': 'ปลายทาง', 'weight': 'น้ำหนัก (กก.)', 'vol': 'ปริมาตร (ลบ.ม.)', 'cargo': 'ประเภทสินค้า',
        'add_btn': 'เพิ่มข้อมูล', 'tab_dash': '📊 แดชบอร์ด AI', 'tab_table': '📋 รายการออเดอร์ทั้งหมด',
        'kpi_title': 'ตัวชี้วัดประสิทธิภาพ (KPIs)', 'utilization': 'อัตราใช้พื้นที่รถ', 'cost': 'ต้นทุนต่อตัน-กม.', 'ontime': 'โอกาสส่งตรงเวลา', 'empty': 'สัดส่วนวิ่งรถเปล่า',
        'ai_plan': '🧠 แผนจัดส่งแนะนำโดย AI', 'truck': 'รถบรรทุก', 'driver': 'คนขับ', 'eta': 'เวลาถึงที่หมาย (ETA)',
        'action': '🧑‍💻 การตัดสินใจ (Human Override)', 'accept': '✅ อนุมัติแผนนี้', 'reject': '❌ ปฏิเสธและคำนวณใหม่', 'modify': '✏️ แก้ไขด้วยตนเอง',
        'reasoning': '💡 เหตุผลของ AI และสมมติฐาน',
        'trip1_dest': 'เวียงจันทน์', 'trip1_cargo': 'ออเดอร์จัดกลุ่ม (อิเล็กทรอนิกส์, อาหาร)',
        'trip2_dest': 'กัวลาลัมเปอร์', 'trip2_cargo': 'ออเดอร์จัดกลุ่ม (*แยกสินค้าเคมีออกจากกลุ่ม*)',
        'edit_title': '🛠️ ปรับแก้แผนของ AI', 'save_btn': '💾 บันทึกการเปลี่ยนแปลง', 'cancel_btn': 'ยกเลิก'
    }
}

# --- 4. AI LOGIC & CALCULATIONS ---
def generate_ai_results(scenario, priority, extra_orders):
    base_util = 85 + (extra_orders * 1.5) 
    base_cost = 1.85 - (extra_orders * 0.01) 
    base_ontime = 95
    base_empty = 15
    if "Disruption" in scenario or "เหตุขัดข้อง" in scenario:
        base_ontime -= 18
        base_cost += 0.4
    if priority == 'Maximum On-Time Delivery' or priority == 'เน้นส่งตรงเวลาที่สุด':
        base_ontime += 10
        base_cost += 0.2
        base_util -= 7
    return {'util': min(100, max(0, base_util)), 'cost': max(1.0, base_cost), 'ontime': min(100, max(0, base_ontime)), 'empty': max(0, base_empty)}

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
        o_dest = st.selectbox(l['dest'], ["Laos (Vientiane)", "Malaysia (Kuala Lumpur)", "Vietnam (Hanoi)", "China (Kunming)"])
        o_weight = st.number_input(l['weight'], min_value=100, max_value=5000, value=1000)
        o_vol = st.number_input(l['vol'], min_value=1.0, max_value=20.0, value=5.0)
        o_cargo = st.selectbox(l['cargo'], ["Electronics", "Textiles", "Food", "Chemicals"])
        submitted = st.form_submit_button(l['add_btn'], use_container_width=True)
        
        if submitted:
            # AI แยกแยะออเดอร์ตามปลายทางอย่างสมเหตุสมผล
            if 'Vientiane' in o_dest or 'เวียงจันทน์' in o_dest:
                st.session_state.trip_assignments['t1_orders'] += 1
                assigned_trip = "Pending AI Assignment (Trip 1)"
            elif 'Kuala Lumpur' in o_dest or 'กัวลาลัมเปอร์' in o_dest:
                st.session_state.trip_assignments['t2_orders'] += 1
                assigned_trip = "Pending AI Assignment (Trip 2)"
            else:
                st.session_state.trip_assignments['other_orders'] += 1
                assigned_trip = "Pending AI Assignment (New Trip)"

            new_id = f"ORD-NEW-{st.session_state.trip_assignments['t1_orders'] + st.session_state.trip_assignments['t2_orders'] + st.session_state.trip_assignments['other_orders']}"
            new_row = pd.DataFrame([{'Order_ID': new_id, 'Origin': o_origin, 'Destination': o_dest, 'Weight_kg': o_weight, 'Cargo_Type': o_cargo, 'Status': assigned_trip, 'ETA': 'TBD'}])
            st.session_state.orders_df = pd.concat([new_row, st.session_state.orders_df], ignore_index=True)
            st.success("Order Added & Routed by Destination!" if lang_choice == 'English' else "เพิ่มออเดอร์และจัดเส้นทางสำเร็จ!")

# --- 6. MAIN LAYOUT (TABS) ---
st.title(l['title'])
tab1, tab2 = st.tabs([l['tab_dash'], l['tab_table']])

total_new_orders = st.session_state.trip_assignments['t1_orders'] + st.session_state.trip_assignments['t2_orders'] + st.session_state.trip_assignments['other_orders']

with tab1:
    ai_metrics = generate_ai_results(selected_scenario, selected_priority, total_new_orders)

    st.subheader(l['kpi_title'])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(l['utilization'], f"{ai_metrics['util']:.1f}%", f"+{total_new_orders*1.5}%" if total_new_orders > 0 else "0%")
    col2.metric(l['cost'], f"฿{ai_metrics['cost']:.2f}")
    col3.metric(l['ontime'], f"{ai_metrics['ontime']}%")
    col4.metric(l['empty'], f"{ai_metrics['empty']}%")
    st.divider()

    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader(l['ai_plan'])
        
        with st.container(border=True):
            st.markdown(f"#### 📦 Trip 1: Lamphun ➡️ {l['trip1_dest']}")
            st.write(f"**{l['truck']}:** {st.session_state.trip_assignments['t1_truck']} &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** {st.session_state.trip_assignments['t1_driver']}")
            st.write(f"**Cargo:** {3 + st.session_state.trip_assignments['t1_orders']} {l['trip1_cargo']}")
            st.write(f"**{l['eta']}:** 2026-08-14 09:30 AM")
        
        with st.container(border=True):
            st.markdown(f"#### 📦 Trip 2: Lamphun ➡️ {l['trip2_dest']}")
            st.write(f"**{l['truck']}:** {st.session_state.trip_assignments['t2_truck']} &nbsp;&nbsp;|&nbsp;&nbsp; **{l['driver']}:** {st.session_state.trip_assignments['t2_driver']}")
            st.write(f"**Cargo:** {5 + st.session_state.trip_assignments['t2_orders']} {l['trip2_cargo']}")
            st.write(f"**{l['eta']}:** 2026-08-16 14:00 PM")
            
        status_data = pd.DataFrame({'Status': ['On-Time', 'Delayed', 'Critical'], 'Count': [ai_metrics['ontime'] + total_new_orders, 100 - ai_metrics['ontime'] - 2, 2]})
        fig = px.bar(status_data, x='Status', y='Count', color='Status', color_discrete_map={'On-Time':'#28A745', 'Delayed':'#FFC107', 'Critical':'#DC3545'})
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_title=None, yaxis_title="Orders")
        st.plotly_chart(fig, use_container_width=True)

    with col_side:
        st.subheader(l['action'])
        
        # ปุ่มอนุมัติแผน
        if st.button(l['accept'], use_container_width=True, type="primary"):
            st.session_state.orders_df.loc[st.session_state.orders_df['Status'].str.contains('Pending'), 'Status'] = 'Assigned (Approved)'
            st.session_state.edit_mode = False
            st.rerun()
            
        # ปุ่มแก้ไข (Human Override - Dropdown Menu)
        if st.button(l['modify'], use_container_width=True):
            st.session_state.edit_mode = not st.session_state.edit_mode
            
        if st.session_state.edit_mode:
            with st.expander(l['edit_title'], expanded=True):
                with st.form("override_form"):
                    st.markdown("**Trip 1 Override**")
                    new_t1_truck = st.selectbox("Select Truck (Trip 1)", ["TH-001 (Capacity 5T)", "TH-003 (Capacity 6T)", "TH-009 (Capacity 10T)"], index=0)
                    new_t1_driver = st.selectbox("Select Driver (Trip 1)", ["Somchai", "Somsak", "Mana", "Niran"], index=0)
                    
                    st.markdown("**Trip 2 Override**")
                    new_t2_truck = st.selectbox("Select Truck (Trip 2)", ["TH-002 (Capacity 8T)", "TH-004 (Capacity 8T)", "TH-007 (Capacity 12T)"], index=0)
                    new_t2_driver = st.selectbox("Select Driver (Trip 2)", ["Wichai", "Preecha", "Kittipong", "Supachai"], index=0)
                    
                    save_override = st.form_submit_button(l['save_btn'], type="primary")
                    if save_override:
                        st.session_state.trip_assignments['t1_truck'] = new_t1_truck
                        st.session_state.trip_assignments['t1_driver'] = new_t1_driver
                        st.session_state.trip_assignments['t2_truck'] = new_t2_truck
                        st.session_state.trip_assignments['t2_driver'] = new_t2_driver
                        st.session_state.edit_mode = False
                        st.rerun()

        # ปุ่มปฏิเสธ
        if st.button(l['reject'], use_container_width=True):
            st.session_state.trip_assignments['t1_orders'] = 0
            st.session_state.trip_assignments['t2_orders'] = 0
            st.session_state.trip_assignments['other_orders'] = 0
            st.session_state.orders_df = st.session_state.orders_df[~st.session_state.orders_df['Order_ID'].str.contains("ORD-NEW")]
            st.session_state.edit_mode = False
            st.rerun()
        
        st.divider()
        st.subheader(l['reasoning'])
        st.info(f"💡 AI matched destinations: {st.session_state.trip_assignments['t1_orders']} orders added to Trip 1 (VTE) and {st.session_state.trip_assignments['t2_orders']} to Trip 2 (KUL).")

with tab2:
    st.subheader(l['tab_table'])
    display_df = st.session_state.orders_df.copy()
    if lang_choice == 'ภาษาไทย':
        display_df.columns = ['รหัสออเดอร์', 'ต้นทาง', 'ปลายทาง', 'น้ำหนัก (กก.)', 'ประเภทสินค้า', 'สถานะจัดรถ', 'เวลาถึง (ETA)']
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
