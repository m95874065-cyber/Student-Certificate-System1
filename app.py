import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from supabase import create_client
import hashlib
import secrets


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Certificate Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

STORAGE_BUCKET = "certificates"


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_password):

    try:

        salt, stored_hash = stored_password.split("$")

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

        return secrets.compare_digest(
            password_hash,
            stored_hash
        )

    except ValueError:

        return False


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_students():

    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data or []


def get_student(register_no):

    response = (
        supabase
        .table("students")
        .select("*")
        .eq(
            "register_no",
            register_no
        )
        .execute()
    )

    if response.data:

        return response.data[0]

    return None


def get_certificates(register_no=None):

    query = (
        supabase
        .table("certificates")
        .select("*")
    )

    if register_no:

        query = query.eq(
            "register_no",
            register_no
        )

    response = query.execute()

    return response.data or []


# ============================================================
# REGISTER NUMBER SORTING
# ============================================================

def get_numeric_register_number(register_no):

    try:

        if "BAI" in register_no:

            number_part = (
                register_no
                .split("BAI")[-1]
            )

            return int(number_part)

        return 999999999

    except:

        return 999999999


# ============================================================
# STORAGE FILE PATH
# ============================================================

def storage_file_path(
    register_no,
    certificate_name,
    original_name
):

    safe_name = (
        certificate_name
        .replace(" ", "_")
    )

    return (
        register_no
        + "_"
        + safe_name
        + "_"
        + original_name
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .login-card {
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #dddddd;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .info-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        font-size: 14px;
    }

    .college-name {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .college-name h2 {
        margin-bottom: 3px;
        font-size: 28px;
        font-weight: 700;
    }

    .college-name p {
        margin-top: 0;
        font-size: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🎓 Student Certificate Management System
    </div>

    <div class="sub-title">
        Certificate Tracking & Deadline Management
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "user_type" not in st.session_state:

    st.session_state.user_type = None


if "register_no" not in st.session_state:

    st.session_state.register_no = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/3135/3135755.png",
        width=100
    )

    st.markdown(
        "## 🎓 Certificate System"
    )

    st.markdown("---")

    if not st.session_state.logged_in:

        login_type = st.radio(
            "Login Type",
            [
                "Student Login",
                "Admin Login"
            ]
        )

    else:

        login_type = st.session_state.user_type

        if login_type == "Student":

            st.success(
                "👨‍🎓 Student Logged In"
            )

        else:

            st.success(
                "👨‍💼 Admin Logged In"
            )

        st.markdown("---")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.register_no = None

            st.rerun()

    st.markdown("---")

    st.info(
        """
        📌 Students can check their certificates,
        deadlines and upload completed certificates.

        📌 Admin can manage students,
        certificates and view analytics.
        """
    )


# ============================================================
# LOGIN SECTION
# ============================================================

if not st.session_state.logged_in:

    # ========================================================
    # COLLEGE NAME
    # ========================================================

    st.markdown(
        """
        <div class="college-name">
            <h2>RATHINAM GLOBAL TO BE DEEMED UNIVERSITY</h2>
            
        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # STUDENT LOGIN
    # ========================================================

    if login_type == "Student Login":

        st.markdown(
            '<div class="login-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            "## 👨‍🎓 Student Login"
        )

        register_no = st.text_input(
            "Register Number",
            placeholder="Enter your register number"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        login_button = st.button(
            "🔐 Login",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if login_button:

            if not register_no or not password:

                st.warning(
                    "⚠️ Please enter register number and password."
                )

            else:

                student = get_student(
                    register_no.strip()
                )

                if student:

                    stored_password = student["password"]

                    if verify_password(
                        password,
                        stored_password
                    ):

                        st.session_state.logged_in = True
                        st.session_state.user_type = "Student"
                        st.session_state.register_no = (
                            register_no.strip()
                        )

                        st.rerun()

                    elif stored_password == password:

                        new_hashed_password = (
                            hash_password(password)
                        )

                        (
                            supabase
                            .table("students")
                            .update(
                                {
                                    "password":
                                    new_hashed_password
                                }
                            )
                            .eq(
                                "register_no",
                                register_no.strip()
                            )
                            .execute()
                        )

                        st.session_state.logged_in = True
                        st.session_state.user_type = "Student"
                        st.session_state.register_no = (
                            register_no.strip()
                        )

                        st.rerun()

                    else:

                        st.error(
                            "❌ Invalid password."
                        )

                else:

                    st.error(
                        "❌ Student not found."
                    )


    # ========================================================
    # ADMIN LOGIN
    # ========================================================

    else:

        st.markdown(
            '<div class="login-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            "## 👨‍💼 Admin Login"
        )

        admin_username = st.text_input(
            "Username"
        )

        admin_password = st.text_input(
            "Password",
            type="password"
        )

        admin_login_button = st.button(
            "🔐 Admin Login",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if admin_login_button:

            if (
                admin_username == "admin"
                and admin_password == "admin123"
            ):

                st.session_state.logged_in = True
                st.session_state.user_type = "Admin"

                st.rerun()

            else:

                st.error(
                    "❌ Invalid admin credentials."
                )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

if (
    st.session_state.logged_in
    and st.session_state.user_type == "Student"
):

    register_no = st.session_state.register_no

    student = get_student(
        register_no
    )

    certificates = get_certificates(
        register_no
    )

    st.markdown(
        '<div class="section-title">👨‍🎓 Student Dashboard</div>',
        unsafe_allow_html=True
    )

    if student:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.info(
                f"""
                **👤 Name**

                {student["name"]}
                """
            )

        with col2:

            st.info(
                f"""
                **🆔 Register Number**

                {student["register_no"]}
                """
            )

        with col3:

            st.info(
                f"""
                **🏫 Department**

                {student["department"]}
                """
            )

        total_certificates = len(
            certificates
        )

        completed_certificates = sum(
            1
            for c in certificates
            if c["status"] == "Completed"
        )

        pending_certificates = sum(
            1
            for c in certificates
            if c["status"] == "Pending"
        )

        not_updated_certificates = sum(
            1
            for c in certificates
            if c["status"] == "Status"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "📜 Total",
                total_certificates
            )

        with col2:

            st.metric(
                "✅ Completed",
                completed_certificates
            )

        with col3:

            st.metric(
                "⏳ Pending",
                pending_certificates
            )

        with col4:

            st.metric(
                "❓ Not Updated",
                not_updated_certificates
            )

        if total_certificates > 0:

            progress = (
                completed_certificates
                / total_certificates
            )

        else:

            progress = 0

        st.markdown(
            "### 📈 Certificate Progress"
        )

        st.progress(
            progress
        )

        st.write(
            f"**{completed_certificates} / "
            f"{total_certificates} certificates completed "
            f"({progress * 100:.0f}%)**"
        )

        if total_certificates > 0:

            chart_data = pd.DataFrame(
                {
                    "Status": [
                        "Completed",
                        "Pending",
                        "Not Updated"
                    ],
                    "Count": [
                        completed_certificates,
                        pending_certificates,
                        not_updated_certificates
                    ]
                }
            )

            chart_data = chart_data[
                chart_data["Count"] > 0
            ]

            if not chart_data.empty:

                st.markdown(
                    "### 🥧 Certificate Status"
                )

                fig = px.pie(
                    chart_data,
                    names="Status",
                    values="Count",
                    title="My Certificate Status"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        st.markdown(
            "### 📋 Certificate Details"
        )

        if certificates:

            for certificate in certificates:

                certificate_name = (
                    certificate["certificate_name"]
                )

                status = certificate["status"]

                deadline = certificate["deadline"]

                if status == "Completed":

                    st.success(
                        f"📜 {certificate_name} | "
                        f"Status: ✅ Completed | "
                        f"Deadline: {deadline}"
                    )

                elif status == "Pending":

                    st.warning(
                        f"📜 {certificate_name} | "
                        f"Status: ⏳ Pending | "
                        f"Deadline: {deadline}"
                    )

                else:

                    st.info(
                        f"📜 {certificate_name} | "
                        f"Status: ❓ Not Updated | "
                        f"Deadline: {deadline}"
                    )

                if status == "Completed":

                    answer = st.radio(
                        "Did you complete this certificate?",
                        ["Yes", "No"],
                        index=0,
                        key=f"answer_{certificate['id']}"
                    )

                elif status == "Pending":

                    answer = st.radio(
                        "Did you complete this certificate?",
                        ["Yes", "No"],
                        index=1,
                        key=f"answer_{certificate['id']}"
                    )

                else:

                    answer = st.radio(
                        "Did you complete this certificate?",
                        ["Yes", "No"],
                        index=None,
                        key=f"answer_{certificate['id']}"
                    )

                if answer:

                    new_status = (
                        "Completed"
                        if answer == "Yes"
                        else "Pending"
                    )

                    if new_status != status:

                        (
                            supabase
                            .table("certificates")
                            .update(
                                {
                                    "status":
                                    new_status
                                }
                            )
                            .eq(
                                "id",
                                certificate["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Certificate status updated."
                        )

                        st.rerun()

                try:

                    deadline_date = datetime.strptime(
                        deadline,
                        "%Y-%m-%d"
                    ).date()

                    today = datetime.today().date()

                    days_left = (
                        deadline_date - today
                    ).days

                    if status != "Completed":

                        if days_left < 0:

                            st.error(
                                "🚨 Deadline expired!"
                            )

                        elif days_left <= 3:

                            st.error(
                                f"⚠️ Only {days_left} "
                                f"day(s) left!"
                            )

                        elif days_left <= 7:

                            st.warning(
                                f"⏰ {days_left} "
                                f"day(s) remaining."
                            )

                except:

                    pass

                if status == "Completed":

                    st.markdown(
                        "**📤 Upload Completed Certificate**"
                    )

                    uploaded_file = st.file_uploader(
                        "Choose certificate file",
                        type=[
                            "pdf",
                            "png",
                            "jpg",
                            "jpeg"
                        ],
                        key=f"upload_{certificate['id']}"
                    )

                    if uploaded_file:

                        if st.button(
                            "📤 Upload Certificate",
                            key=f"upload_btn_{certificate['id']}"
                        ):

                            file_path = storage_file_path(
                                register_no,
                                certificate_name,
                                uploaded_file.name
                            )

                            file_bytes = (
                                uploaded_file.getvalue()
                            )

                            content_type = (
                                uploaded_file.type
                                or "application/octet-stream"
                            )

                            try:

                                (
                                    supabase
                                    .storage
                                    .from_(STORAGE_BUCKET)
                                    .upload(
                                        file_path,
                                        file_bytes,
                                        {
                                            "content-type":
                                            content_type,
                                            "upsert": True
                                        }
                                    )
                                )

                                st.success(
                                    "✅ Certificate uploaded successfully."
                                )

                            except Exception as e:

                                st.error(
                                    f"❌ Upload failed: {e}"
                                )

        else:

            st.info(
                "📭 No certificates assigned yet."
            )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

if (
    st.session_state.logged_in
    and st.session_state.user_type == "Admin"
):

    st.markdown(
        '<div class="section-title">👨‍💼 Admin Dashboard</div>',
        unsafe_allow_html=True
    )

    all_students = get_students()

    all_certificates = get_certificates()

    all_students = sorted(
        all_students,
        key=lambda x:
        get_numeric_register_number(
            x["register_no"]
        )
    )

    all_certificates = sorted(
        all_certificates,
        key=lambda x:
        get_numeric_register_number(
            x["register_no"]
        )
    )

    total_students = len(
        all_students
    )

    total_completed = sum(
        1
        for c in all_certificates
        if c["status"] == "Completed"
    )

    total_pending = sum(
        1
        for c in all_certificates
        if c["status"] == "Pending"
    )

    total_not_updated = sum(
        1
        for c in all_certificates
        if c["status"] == "Status"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👨‍🎓 Total Students",
            total_students
        )

    with col2:

        st.metric(
            "✅ Completed",
            total_completed
        )

    with col3:

        st.metric(
            "⏳ Pending",
            total_pending
        )

    with col4:

        st.metric(
            "❓ Not Updated",
            total_not_updated
        )

    st.markdown("---")

    admin_menu = st.selectbox(
        "Admin Menu",
        [
            "Add New Student",
            "Remove Student",
            "Add Certificate",
            "Remove Certificate",
            "Student List",
            "Certificate Overview",
            "Certificate Analytics",
            "Update Certificate",
            "Uploaded Certificates"
        ]
    )


    # ========================================================
    # ADD NEW STUDENT
    # ========================================================

    if admin_menu == "Add New Student":

        st.subheader(
            "➕ Add New Student"
        )

        new_register_no = st.text_input(
            "Register Number"
        )

        new_name = st.text_input(
            "Student Name"
        )

        new_department = st.text_input(
            "Department"
        )

        new_password = st.text_input(
            "Student Password",
            type="password"
        )

        if st.button(
            "➕ Add Student"
        ):

            if (
                new_register_no
                and new_name
                and new_department
                and new_password
            ):

                existing_student = get_student(
                    new_register_no.strip()
                )

                if existing_student:

                    st.error(
                        "❌ Student already exists."
                    )

                else:

                    hashed_password = hash_password(
                        new_password
                    )

                    try:

                        (
                            supabase
                            .table("students")
                            .insert(
                                {
                                    "register_no":
                                    new_register_no.strip(),

                                    "name":
                                    new_name.strip(),

                                    "department":
                                    new_department.strip(),

                                    "password":
                                    hashed_password
                                }
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Student added successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )

            else:

                st.warning(
                    "⚠️ Please fill all fields."
                )


    # ========================================================
    # REMOVE STUDENT
    # ========================================================

    elif admin_menu == "Remove Student":

        st.subheader(
            "🗑️ Remove Student"
        )

        if all_students:

            student_options = [
                f'{s["register_no"]} - {s["name"]}'
                for s in all_students
            ]

            selected_student = st.selectbox(
                "Select Student",
                student_options
            )

            selected_register = (
                selected_student
                .split(" - ")[0]
            )

            if st.button(
                "🗑️ Remove Student"
            ):

                try:

                    (
                        supabase
                        .table("certificates")
                        .delete()
                        .eq(
                            "register_no",
                            selected_register
                        )
                        .execute()
                    )

                    (
                        supabase
                        .table("students")
                        .delete()
                        .eq(
                            "register_no",
                            selected_register
                        )
                        .execute()
                    )

                    st.success(
                        "✅ Student removed successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Error: {e}"
                    )

        else:

            st.info(
                "📭 No students available."
            )


    # ========================================================
    # ADD CERTIFICATE
    # ========================================================

    elif admin_menu == "Add Certificate":

        st.subheader(
            "📜 Add Certificate"
        )

        if all_students:

            student_options = [
                f'{s["register_no"]} - {s["name"]}'
                for s in all_students
            ]

            selected_student = st.selectbox(
                "Select Student",
                student_options
            )

            selected_register = (
                selected_student
                .split(" - ")[0]
            )

            certificate_name = st.text_input(
                "Certificate Name"
            )

            certificate_status = st.selectbox(
                "Initial Status",
                [
                    "Status",
                    "Pending",
                    "Completed"
                ]
            )

            certificate_deadline = st.date_input(
                "Deadline"
            )

            if st.button(
                "➕ Add Certificate"
            ):

                if certificate_name:

                    try:

                        (
                            supabase
                            .table("certificates")
                            .insert(
                                {
                                    "register_no":
                                    selected_register,

                                    "certificate_name":
                                    certificate_name.strip(),

                                    "status":
                                    certificate_status,

                                    "deadline":
                                    certificate_deadline
                                    .strftime(
                                        "%Y-%m-%d"
                                    )
                                }
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Certificate added successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )

                else:

                    st.warning(
                        "⚠️ Enter certificate name."
                    )

        else:

            st.info(
                "📭 Add students first."
            )


    # ========================================================
    # REMOVE CERTIFICATE
    # ========================================================

    elif admin_menu == "Remove Certificate":

        st.subheader(
            "🗑️ Remove Certificate"
        )

        if all_certificates:

            certificate_options = [
                f'{c["id"]} - '
                f'{c["register_no"]} - '
                f'{c["certificate_name"]}'
                for c in all_certificates
            ]

            selected_certificate = st.selectbox(
                "Select Certificate",
                certificate_options
            )

            selected_id = int(
                selected_certificate
                .split(" - ")[0]
            )

            if st.button(
                "🗑️ Remove Certificate"
            ):

                try:

                    (
                        supabase
                        .table("certificates")
                        .delete()
                        .eq(
                            "id",
                            selected_id
                        )
                        .execute()
                    )

                    st.success(
                        "✅ Certificate removed successfully."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Error: {e}"
                    )

        else:

            st.info(
                "📭 No certificates available."
            )


    # ========================================================
    # STUDENT LIST
    # ========================================================

    elif admin_menu == "Student List":

        st.subheader(
            "👨‍🎓 Student List"
        )

        if all_students:

            student_rows = []

            for student in all_students:

                student_rows.append(
                    {
                        "Register Number":
                        student["register_no"],

                        "Name":
                        student["name"],

                        "Department":
                        student["department"]
                    }
                )

            student_df = pd.DataFrame(
                student_rows
            )

            st.dataframe(
                student_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "📭 No students available."
            )


    # ========================================================
    # CERTIFICATE OVERVIEW
    # ========================================================

    elif admin_menu == "Certificate Overview":

        st.subheader(
            "📂 Certificate Overview"
        )

        if all_students:

            for student in all_students:

                student_register = (
                    student["register_no"]
                )

                student_name = (
                    student["name"]
                )

                student_certificates = [
                    c
                    for c in all_certificates
                    if c["register_no"]
                    == student_register
                ]

                st.markdown(
                    f"""
                    ### 📁 {student_name}
                    **🆔 {student_register}**
                    | 📜 {len(student_certificates)}
                    Certificate(s)
                    """
                )

                with st.expander(
                    "Open Student Folder"
                ):

                    st.write(
                        f"**👤 Name:** {student_name}"
                    )

                    st.write(
                        f"**🆔 Register Number:** "
                        f"{student_register}"
                    )

                    st.write(
                        f"**🏫 Department:** "
                        f"{student['department']}"
                    )

                    st.markdown("---")

                    if student_certificates:

                        for certificate in student_certificates:

                            if certificate["status"] == "Completed":

                                st.success(
                                    f"""
                                    📜 **{
                                        certificate[
                                            "certificate_name"
                                        ]
                                    }**

                                    Status: ✅ Completed

                                    Deadline: {
                                        certificate[
                                            "deadline"
                                        ]
                                    }
                                    """
                                )

                            elif certificate["status"] == "Pending":

                                st.warning(
                                    f"""
                                    📜 **{
                                        certificate[
                                            "certificate_name"
                                        ]
                                    }**

                                    Status: ⏳ Pending

                                    Deadline: {
                                        certificate[
                                            "deadline"
                                        ]
                                    }
                                    """
                                )

                            else:

                                st.info(
                                    f"""
                                    📜 **{
                                        certificate[
                                            "certificate_name"
                                        ]
                                    }**

                                    Status: ❓ Not Updated

                                    Deadline: {
                                        certificate[
                                            "deadline"
                                        ]
                                    }
                                    """
                                )

                    else:

                        st.info(
                            "📭 No certificates assigned."
                        )

        else:

            st.info(
                "📭 No students available."
            )


    # ========================================================
    # CERTIFICATE ANALYTICS
    # ========================================================

    elif admin_menu == "Certificate Analytics":

        st.subheader(
            "📊 Certificate Analytics"
        )

        st.write(
            "View certificate-wise completion status "
            "with student names and register numbers."
        )

        if all_certificates:

            student_lookup = {}

            for student in all_students:

                student_lookup[
                    student["register_no"]
                ] = student

            analytics_rows = []

            for certificate in all_certificates:

                certificate_name = (
                    certificate[
                        "certificate_name"
                    ]
                    .strip()
                )

                register_no = (
                    certificate[
                        "register_no"
                    ]
                )

                student = student_lookup.get(
                    register_no
                )

                if student:

                    student_name = (
                        student["name"]
                    )

                else:

                    student_name = "Unknown Student"

                status = certificate[
                    "status"
                ]

                if status == "Completed":

                    status_name = "Completed"

                elif status == "Pending":

                    status_name = "Pending"

                else:

                    status_name = "Not Updated"

                analytics_rows.append(
                    {
                        "Certificate":
                        certificate_name,

                        "Register Number":
                        register_no,

                        "Student Name":
                        student_name,

                        "Status":
                        status_name
                    }
                )

            analytics_df = pd.DataFrame(
                analytics_rows
            )

            summary_df = (
                analytics_df
                .groupby(
                    [
                        "Certificate",
                        "Status"
                    ]
                )
                .size()
                .unstack(
                    fill_value=0
                )
                .reset_index()
            )

            for column in [
                "Completed",
                "Pending",
                "Not Updated"
            ]:

                if column not in summary_df.columns:

                    summary_df[column] = 0

            summary_df["Total"] = (
                summary_df["Completed"]
                + summary_df["Pending"]
                + summary_df["Not Updated"]
            )

            summary_df = summary_df[
                [
                    "Certificate",
                    "Completed",
                    "Pending",
                    "Not Updated",
                    "Total"
                ]
            ]

            st.markdown(
                "### 📋 Certificate-wise Status"
            )

            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True
            )

            analytics_completed = int(
                summary_df[
                    "Completed"
                ].sum()
            )

            analytics_pending = int(
                summary_df[
                    "Pending"
                ].sum()
            )

            analytics_not_updated = int(
                summary_df[
                    "Not Updated"
                ].sum()
            )

            analytics_total = int(
                summary_df[
                    "Total"
                ].sum()
            )

            st.markdown(
                "### 📈 Overall Certificate Statistics"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "📜 Total",
                    analytics_total
                )

            with col2:

                st.metric(
                    "✅ Completed",
                    analytics_completed
                )

            with col3:

                st.metric(
                    "⏳ Pending",
                    analytics_pending
                )

            with col4:

                st.metric(
                    "❓ Not Updated",
                    analytics_not_updated
                )

            st.markdown(
                "### 📊 Certificate-wise Comparison"
            )

            chart_df = summary_df.melt(
                id_vars=[
                    "Certificate"
                ],
                value_vars=[
                    "Completed",
                    "Pending",
                    "Not Updated"
                ],
                var_name="Status",
                value_name="Students"
            )

            fig = px.bar(
                chart_df,
                x="Certificate",
                y="Students",
                color="Status",
                barmode="group",
                title="Certificate Completion Status"
            )

            fig.update_layout(
                height=500,
                xaxis_title="Certificate",
                yaxis_title="Number of Students",
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=80
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # STUDENT-WISE DETAILS
            # =================================================

            st.markdown(
                "### 👨‍🎓 Student Details by Certificate"
            )

            certificate_names = sorted(
                analytics_df[
                    "Certificate"
                ].unique()
            )

            for certificate_name in certificate_names:

                certificate_data = analytics_df[
                    analytics_df[
                        "Certificate"
                    ]
                    == certificate_name
                ]

                completed_students = (
                    certificate_data[
                        certificate_data[
                            "Status"
                        ] == "Completed"
                    ]
                )

                pending_students = (
                    certificate_data[
                        certificate_data[
                            "Status"
                        ] == "Pending"
                    ]
                )

                not_updated_students = (
                    certificate_data[
                        certificate_data[
                            "Status"
                        ] == "Not Updated"
                    ]
                )

                with st.expander(
                    f"📁 {certificate_name}"
                ):

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "📜 Total",
                            len(certificate_data)
                        )

                    with col2:

                        st.metric(
                            "✅ Completed",
                            len(completed_students)
                        )

                    with col3:

                        st.metric(
                            "⏳ Pending",
                            len(pending_students)
                        )

                    with col4:

                        st.metric(
                            "❓ Not Updated",
                            len(not_updated_students)
                        )

                    st.markdown("---")

                    st.markdown(
                        "#### ✅ Completed Students"
                    )

                    if not completed_students.empty:

                        completed_display = (
                            completed_students[
                                [
                                    "Register Number",
                                    "Student Name"
                                ]
                            ]
                            .reset_index(
                                drop=True
                            )
                        )

                        completed_display.index = (
                            completed_display.index + 1
                        )

                        completed_display.index.name = (
                            "S.No"
                        )

                        st.dataframe(
                            completed_display,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No students have completed this certificate."
                        )

                    st.markdown(
                        "#### ⏳ Pending Students"
                    )

                    if not pending_students.empty:

                        pending_display = (
                            pending_students[
                                [
                                    "Register Number",
                                    "Student Name"
                                ]
                            ]
                            .reset_index(
                                drop=True
                            )
                        )

                        pending_display.index = (
                            pending_display.index + 1
                        )

                        pending_display.index.name = (
                            "S.No"
                        )

                        st.dataframe(
                            pending_display,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No pending students."
                        )

                    st.markdown(
                        "#### ❓ Not Updated Students"
                    )

                    if not not_updated_students.empty:

                        not_updated_display = (
                            not_updated_students[
                                [
                                    "Register Number",
                                    "Student Name"
                                ]
                            ]
                            .reset_index(
                                drop=True
                            )
                        )

                        not_updated_display.index = (
                            not_updated_display.index + 1
                        )

                        not_updated_display.index.name = (
                            "S.No"
                        )

                        st.dataframe(
                            not_updated_display,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No students with Not Updated status."
                        )

        else:

            st.info(
                "📭 No certificates available for analytics."
            )


    # ========================================================
    # UPDATE CERTIFICATE
    # ========================================================

    elif admin_menu == "Update Certificate":

        st.subheader(
            "✏️ Update Certificate"
        )

        if all_certificates:

            certificate_options = [
                f'{c["id"]} - '
                f'{c["register_no"]} - '
                f'{c["certificate_name"]}'
                for c in all_certificates
            ]

            selected_certificate = st.selectbox(
                "Select Certificate",
                certificate_options
            )

            selected_id = int(
                selected_certificate
                .split(" - ")[0]
            )

            selected_certificate_data = next(
                (
                    c
                    for c in all_certificates
                    if c["id"] == selected_id
                ),
                None
            )

            if selected_certificate_data:

                current_status = (
                    selected_certificate_data[
                        "status"
                    ]
                )

                current_deadline = datetime.strptime(
                    selected_certificate_data[
                        "deadline"
                    ],
                    "%Y-%m-%d"
                ).date()

                new_status = st.selectbox(
                    "Status",
                    [
                        "Status",
                        "Pending",
                        "Completed"
                    ],
                    index=[
                        "Status",
                        "Pending",
                        "Completed"
                    ].index(
                        current_status
                    )
                    if current_status
                    in [
                        "Status",
                        "Pending",
                        "Completed"
                    ]
                    else 0
                )

                new_deadline = st.date_input(
                    "Deadline",
                    value=current_deadline
                )

                if st.button(
                    "💾 Update Certificate"
                ):

                    try:

                        (
                            supabase
                            .table("certificates")
                            .update(
                                {
                                    "status":
                                    new_status,

                                    "deadline":
                                    new_deadline
                                    .strftime(
                                        "%Y-%m-%d"
                                    )
                                }
                            )
                            .eq(
                                "id",
                                selected_id
                            )
                            .execute()
                        )

                        st.success(
                            "✅ Certificate updated successfully."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )

        else:

            st.info(
                "📭 No certificates available."
            )


    # ========================================================
    # UPLOADED CERTIFICATES
    # ========================================================

    elif admin_menu == "Uploaded Certificates":

        st.subheader(
            "📤 Uploaded Certificates"
        )

        try:

            storage_files = (
                supabase
                .storage
                .from_(STORAGE_BUCKET)
                .list()
            )

            if storage_files:

                for file_info in storage_files:

                    file_name = file_info.get(
                        "name"
                    )

                    if not file_name:

                        continue

                    st.markdown(
                        f"### 📄 {file_name}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        if st.button(
                            "👁️ View / Download",
                            key=f"view_{file_name}"
                        ):

                            try:

                                file_bytes = (
                                    supabase
                                    .storage
                                    .from_(
                                        STORAGE_BUCKET
                                    )
                                    .download(
                                        file_name
                                    )
                                )

                                st.download_button(
                                    "⬇️ Download File",
                                    data=file_bytes,
                                    file_name=file_name,
                                    key=f"download_{file_name}"
                                )

                            except Exception as e:

                                st.error(
                                    f"❌ Download failed: {e}"
                                )

                    with col2:

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{file_name}"
                        ):

                            try:

                                (
                                    supabase
                                    .storage
                                    .from_(
                                        STORAGE_BUCKET
                                    )
                                    .remove(
                                        [file_name]
                                    )
                                )

                                st.success(
                                    "✅ File deleted."
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    f"❌ Delete failed: {e}"
                                )

                    st.markdown("---")

            else:

                st.info(
                    "📭 No uploaded certificates found."
                )

        except Exception as e:

            st.error(
                f"❌ Unable to access storage: {e}"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🎓 Student Certificate Management System
        <br>
        Built with Python, Streamlit & Supabase
    </div>
    """,
    unsafe_allow_html=True
)
