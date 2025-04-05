import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime
from auth_utils import login_user, register_user
from email_utils import send_mail

st.markdown('<style>' + open('styles.css').read() + '</style>', unsafe_allow_html=True)


# MySQL Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rajkumar@2004",
        database="resource_optimization"
    )

# Initialize session states
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

# Database fetch functions
def fetch_resources():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM resources", conn)
    conn.close()
    return df

# ---------- Login/Register ----------
def login_register():
    st.title("🌾 AI-Powered Crop Yield Prediction & Resource Optimization")
    option = st.radio("Choose option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            if login_user(email, password):
                st.session_state.page = "home"
                st.success("✅ Logged in successfully!")
            else:
                st.error("❌ Invalid credentials.")

    elif option == "Register":
        if st.button("Register"):
            if register_user(email, password):
                st.success("✅ Registered! Now log in.")
            else:
                st.warning("⚠️ Email already exists.")

# ---------- Home ----------
def home():
    st.title("🏡 Home - AI Resource System")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌾 Crop Yield Prediction"):
            st.info("🔧 To be implemented")
        if st.button("🧪 Crop Recommendation"):
            st.info("🔧 To be implemented")
    with col2:
        if st.button("🔄 Update Resource"):
            st.session_state.page = "update"
        if st.button("📦 Request Resource"):
            st.session_state.page = "request"
        if st.button("🤖 Ask Bot"):
            st.info("🔧 To be implemented")

# ---------- Update Resource ----------
def update_resource():
    st.title("🔄 Update Resource")
    df = fetch_resources()
    st.dataframe(df)

    new_data = {}
    with st.form("update_form"):
        for _, row in df.iterrows():
            qty = st.number_input(f"{row['resource']}", min_value=0, value=int(row['quantity']))
            new_data[row['resource']] = qty
        submitted = st.form_submit_button("Update")

    if submitted:
        conn = get_connection()
        cursor = conn.cursor()
        for res, new_qty in new_data.items():
            cursor.execute("SELECT quantity FROM resources WHERE resource = %s", (res,))
            old_qty = cursor.fetchone()[0]
            if old_qty != new_qty:
                cursor.execute("UPDATE resources SET quantity = %s WHERE resource = %s", (new_qty, res))
                cursor.execute("INSERT INTO resource_updates (resource, old_quantity, new_quantity) VALUES (%s, %s, %s)",
                               (res, old_qty, new_qty))
        conn.commit()
        conn.close()
        st.success("✅ Resources updated successfully!")

    if st.button("📜 Show Recent Updates"):
        conn = get_connection()
        updates = pd.read_sql("SELECT * FROM resource_updates ORDER BY updated_at DESC LIMIT 10", conn)
        conn.close()
        st.dataframe(updates)

    if st.button("🏠 Home"):
        st.session_state.page = "home"

# ---------- Request Resource ----------
def request_resource():
    st.title("📦 Request Resources")
    df = fetch_resources()
    st.dataframe(df)

    st.subheader("🧾 Personal Info")
    name = st.text_input("Name")
    contact = st.text_input("Contact No.")
    street = st.text_input("Street")

    st.subheader("📧 Manager Emails")
    fert_email = st.text_input("Fertilizer, Pesticide, Seeds Manager Email")
    mach_email = st.text_input("Machinery & Labour Manager Email")

    required = {}
    with st.form("request_form"):
        for _, row in df.iterrows():
            req = st.number_input(f"Required {row['resource']}", min_value=0, key=row['resource'])
            required[row['resource']] = req
        submit = st.form_submit_button("Submit Request")

    if submit:
        conn = get_connection()
        cursor = conn.cursor()
        shortages_fert = {}
        shortages_mach = {}
        all_ok = True

        for res, qty in required.items():
            cursor.execute("SELECT quantity FROM resources WHERE resource = %s", (res,))
            available = cursor.fetchone()[0]
            if available < qty:
                all_ok = False
                if res in ["Fertilizer (kg)", "Pesticides (liters)", "Seeds (kg)"]:
                    shortages_fert[res] = qty - available
                else:
                    shortages_mach[res] = qty - available

        contact_info = f"\n\nContact Info:\nName: {name}\n📞 {contact}\n🏡 {street}"
        if shortages_fert and fert_email:
            body = "Dear Manager,\nShortage in the following resources:\n" + \
                   "\n".join([f"{k}: Need {v} more" for k, v in shortages_fert.items()]) + contact_info
            subject = "🚨 Shortage Alert - F/P/S"
            result = send_mail(subject, body, fert_email)
            st.info(result)
            st.session_state.email_history.append(f"{datetime.now()} - Sent to {fert_email}: {subject}")

        if shortages_mach and mach_email:
            body = "Dear Manager,\nShortage in the following resources:\n" + \
                   "\n".join([f"{k}: Need {v} more" for k, v in shortages_mach.items()]) + contact_info
            subject = "🚨 Shortage Alert - M/L"
            result = send_mail(subject, body, mach_email)
            st.info(result)
            st.session_state.email_history.append(f"{datetime.now()} - Sent to {mach_email}: {subject}")

        if all_ok:
            for res, qty in required.items():
                cursor.execute("UPDATE resources SET quantity = quantity - %s WHERE resource = %s", (qty, res))
            st.success("✅ All resources allocated!")
            conn.commit()

        # Save request log
        cursor.execute("INSERT INTO resource_requests (requested_data) VALUES (%s)", (str(required),))
        conn.commit()
        conn.close()

    if st.button("📈 Show Visualization"):
        visualize_bar_chart(df, required)

    if st.button("📜 Previous Requests"):
        conn = get_connection()
        logs = pd.read_sql("SELECT * FROM resource_requests ORDER BY timestamp DESC LIMIT 10", conn)
        conn.close()
        st.dataframe(logs)

    if st.session_state.email_history:
        st.subheader("📨 Sent Emails")
        for mail in st.session_state.email_history:
            st.write(mail)

    if st.button("🏠 Home"):
        st.session_state.page = "home"

# ---------- Visualization ----------
def visualize_bar_chart(available_df, requested):
    st.subheader("📊 Resource Comparison")
    resources = available_df['resource'].tolist()
    available_qty = available_df['quantity'].tolist()
    requested_qty = [requested[res] for res in resources]

    fig, ax = plt.subplots(figsize=(10, 4))
    index = range(len(resources))
    bar_width = 0.35

    ax.bar(index, available_qty, bar_width, label='Available', color='green')
    ax.bar([i + bar_width for i in index], requested_qty, bar_width, label='Requested', color='red')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(resources, rotation=45)
    ax.set_ylabel("Quantity")
    ax.set_title("Available vs Requested")
    ax.legend()
    st.pyplot(fig)

# ---------- Main Navigation ----------
if st.session_state.page == "login":
    login_register()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "update":
    update_resource()
elif st.session_state.page == "request":
    request_resource()
