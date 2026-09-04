import streamlit as st
import sqlite3
from datetime import datetime
import os
import pandas as pd
import plotly.express as px

# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Student Certificate Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(135deg, #312e81, #4f46e5);
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.10);
}

.hero h1 {
    font-size: 32px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 16px;
    opacity: 0.9;
}

.login-card {
    padding: 30px;
    border-radius: 18px;
    background: white;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    border: 1px solid #e5e7eb;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #312e81;
    margin-bottom: 15px;
}

.student-folder {
    padding: 18px;
    border-radius: 14px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
}

.footer {
    text-align: center;
    color: #6b7280;
    padding: 25px;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(
    "certificate.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    register_no TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    register_no TEXT NOT NULL,
    certificate_name TEXT NOT NULL,
    status TEXT NOT NULL,
    deadline TEXT NOT NULL
)
""")

conn.commit()

# ==================================================
# SESSION STATE
# ==================================================

if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "student_register" not in st.session_state:
    st.session_state.student_register = ""

# ==================================================
# HERO HEADER
# ==================================================

st.markdown("""
<div class="hero">
<h1>🎓 Student Certificate Management System</h1>
<p>Certificate Tracking • Deadline Management • Student Progress</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/3135/3135755.png",
        width=80
    )

    st.title("Certificate System")

    st.markdown("---")

    login_type = st.radio(
        "🔐 Login Type",
        [
            "Student Login",
            "Admin Login"
        ]
    )

    st.markdown("---")

    st.info(
        "🎓 AI & DS College Certificate Tracking System"
    )

# ==================================================
# STUDENT LOGIN
# ==================================================

if login_type == "Student Login":

    if not st.session_state.student_logged_in:

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            st.markdown(
                '<div class="login-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-title">👨‍🎓 Student Login</div>',
                unsafe_allow_html=True
            )

            st.write(
                "Login using your college register number."
            )

            register_no = st.text_input(
                "College Register Number",
                placeholder="Enter register number"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
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

                cursor.execute(
                    """
                    SELECT *
                    FROM students
                    WHERE register_no = ?
                    AND password = ?
                    """,
                    (
                        register_no,
                        password
                    )
                )

                student = cursor.fetchone()

                if student:

                    st.session_state.student_logged_in = True
                    st.session_state.student_register = register_no

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid Register Number or Password"
                    )

    # ==================================================
    # STUDENT DASHBOARD
    # ==================================================

    if st.session_state.student_logged_in:

        register_no = st.session_state.student_register

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE register_no = ?
            """,
            (register_no,)
        )

        student = cursor.fetchone()

        if student:

            st.success(
                f"👋 Welcome, {student[1]}!"
            )

            st.write(
                "Track your certificates, deadlines and progress here."
            )

            # ==================================================
            # STUDENT PROFILE
            # ==================================================

            st.markdown(
                '<div class="section-title">👤 Student Profile</div>',
                unsafe_allow_html=True
            )

            profile1, profile2, profile3 = st.columns(3)

            with profile1:
                st.info(
                    f"👤 Student Name\n\n**{student[1]}**"
                )

            with profile2:
                st.info(
                    f"🆔 Register Number\n\n**{student[0]}**"
                )

            with profile3:
                st.info(
                    f"🏫 Department\n\n**{student[2]}**"
                )

            # ==================================================
            # GET CERTIFICATES
            # ==================================================

            cursor.execute(
                """
                SELECT id,
                       certificate_name,
                       status,
                       deadline
                FROM certificates
                WHERE register_no = ?
                ORDER BY id
                """,
                (register_no,)
            )

            certificates = cursor.fetchall()

            total = len(certificates)

            completed = sum(
                1
                for certificate in certificates
                if certificate[2] == "Completed"
            )

            pending = sum(
                1
                for certificate in certificates
                if certificate[2] == "Pending"
            )

            not_updated = sum(
                1
                for certificate in certificates
                if certificate[2] == "Status"
            )

            progress = (
                completed / total
                if total > 0
                else 0
            )

            # ==================================================
            # CERTIFICATE SUMMARY
            # ==================================================

            st.markdown(
                '<div class="section-title">📊 Certificate Summary</div>',
                unsafe_allow_html=True
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "📜 Total Certificates",
                    total
                )

            with col2:
                st.metric(
                    "✅ Completed",
                    completed
                )

            with col3:
                st.metric(
                    "⏳ Pending",
                    pending
                )

            with col4:
                st.metric(
                    "📈 Progress",
                    f"{int(progress * 100)}%"
                )

            if not_updated > 0:
                st.info(
                    f"ℹ️ {not_updated} certificate(s) waiting for student response."
                )

            # ==================================================
            # PROGRESS
            # ==================================================

            progress_col1, progress_col2 = st.columns([2, 1])

            with progress_col1:

                st.markdown(
                    "### 📈 Overall Certificate Progress"
                )

                st.progress(progress)

                st.write(
                    f"**{completed} out of {total} certificates completed**"
                )

                if total == 0:
                    st.info(
                        "ℹ️ No certificates assigned yet."
                    )

                elif progress == 1:
                    st.success(
                        "🎉 Excellent! All certificates are completed."
                    )

                elif progress >= 0.5:
                    st.info(
                        "👍 Good progress! Keep completing your certificates."
                    )

                else:
                    st.warning(
                        "⚠️ You have several certificates pending."
                    )

            with progress_col2:

                st.markdown(
                    "### 🎯 Completion"
                )

                st.metric(
                    "Completion Rate",
                    f"{int(progress * 100)}%"
                )

            # ==================================================
            # PIE CHART
            # ==================================================

            if total > 0:

                st.markdown(
                    "### 🥧 Certificate Status"
                )

                chart_data = pd.DataFrame(
                    {
                        "Status": [
                            "Completed",
                            "Pending",
                            "Not Updated"
                        ],
                        "Count": [
                            completed,
                            pending,
                            not_updated
                        ]
                    }
                )

                chart_data = chart_data[
                    chart_data["Count"] > 0
                ]

                fig = px.pie(
                    chart_data,
                    names="Status",
                    values="Count",
                    hole=0.45,
                    title="Certificate Completion Status"
                )

                fig.update_layout(
                    height=400,
                    margin=dict(
                        l=20,
                        r=20,
                        t=60,
                        b=20
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.divider()

            # ==================================================
            # DEADLINE ALERTS
            # ==================================================

            st.markdown(
                "### 🔔 Deadline Alerts"
            )

            deadline_found = False

            for certificate in certificates:

                name = certificate[1]
                status = certificate[2]
                deadline = certificate[3]

                try:

                    deadline_date = None

                    try:
                        deadline_date = datetime.strptime(
                            deadline,
                            "%d %b %Y"
                        )

                    except ValueError:
                        pass

                    if deadline_date is None:

                        try:
                            deadline_date = datetime.strptime(
                                deadline,
                                "%A %d/%m/%Y"
                            )

                        except ValueError:
                            pass

                    if deadline_date is not None:

                        today = datetime.now()

                        days_left = (
                            deadline_date.date()
                            - today.date()
                        ).days

                        if status != "Completed":

                            if days_left < 0:

                                st.error(
                                    f"🔴 **{name}** — Deadline expired "
                                    f"({abs(days_left)} days ago)"
                                )

                                deadline_found = True

                            elif days_left == 0:

                                st.error(
                                    f"🚨 **{name}** — Deadline is TODAY!"
                                )

                                deadline_found = True

                            elif days_left <= 7:

                                st.warning(
                                    f"🟡 **{name}** — Due in "
                                    f"{days_left} days "
                                    f"({deadline})"
                                )

                                deadline_found = True

                except Exception:
                    pass

            if not deadline_found:

                st.success(
                    "✅ No urgent certificate deadlines."
                )

            st.divider()

            # ==================================================
            # MY CERTIFICATES
            # ==================================================

            st.markdown(
                "### 📜 My Certificates"
            )

            if not certificates:

                st.info(
                    "No certificates assigned yet."
                )

            else:

                for index, certificate in enumerate(certificates):

                    certificate_id = certificate[0]
                    name = certificate[1]
                    status = certificate[2]
                    deadline = certificate[3]

                    st.markdown(
                        f"#### 📜 {name}"
                    )

                    st.write(
                        f"**Deadline:** {deadline}"
                    )

                    st.markdown(
                        "##### ❓ Did you complete this certificate?"
                    )

                    if status == "Completed":

                        student_answer = st.radio(
                            f"Select answer for {name}",
                            ["Yes", "No"],
                            index=0,
                            key=f"answer_{certificate_id}"
                        )

                    elif status == "Pending":

                        student_answer = st.radio(
                            f"Select answer for {name}",
                            ["Yes", "No"],
                            index=1,
                            key=f"answer_{certificate_id}"
                        )

                    else:

                        student_answer = st.radio(
                            f"Select answer for {name}",
                            ["Yes", "No"],
                            index=None,
                            key=f"answer_{certificate_id}"
                        )

                    if student_answer is not None:

                        new_status = (
                            "Completed"
                            if student_answer == "Yes"
                            else "Pending"
                        )

                        if new_status != status:

                            cursor.execute(
                                """
                                UPDATE certificates
                                SET status = ?
                                WHERE id = ?
                                """,
                                (
                                    new_status,
                                    certificate_id
                                )
                            )

                            conn.commit()

                            st.rerun()

                    if student_answer == "Yes":

                        st.success(
                            "✅ Completed"
                        )

                        st.caption(
                            "🎉 You have completed this certificate."
                        )

                        uploaded_file = st.file_uploader(
                            f"📤 Upload {name} Certificate",
                            type=[
                                "pdf",
                                "png",
                                "jpg",
                                "jpeg"
                            ],
                            key="upload_" + str(certificate_id)
                        )

                        if uploaded_file is not None:

                            upload_folder = "certificates"

                            if not os.path.exists(upload_folder):
                                os.makedirs(upload_folder)

                            safe_name = name.replace(
                                " ",
                                "_"
                            )

                            file_path = os.path.join(
                                upload_folder,
                                register_no +
                                "_" +
                                safe_name +
                                "_" +
                                uploaded_file.name
                            )

                            with open(
                                file_path,
                                "wb"
                            ) as f:

                                f.write(
                                    uploaded_file.getbuffer()
                                )

                            st.success(
                                f"✅ {name} certificate uploaded successfully!"
                            )

                    elif student_answer == "No":

                        st.warning(
                            "⏳ Pending"
                        )

                        st.caption(
                            "📌 Please complete this certificate before the deadline."
                        )

                    else:

                        st.info(
                            "ℹ️ Please select Yes or No."
                        )

                    st.divider()

            # ==================================================
            # STUDENT LOGOUT
            # ==================================================

            logout_col1, logout_col2, logout_col3 = st.columns(
                [1, 1, 1]
            )

            with logout_col2:

                if st.button(
                    "🚪 Student Logout",
                    use_container_width=True
                ):

                    st.session_state.student_logged_in = False
                    st.session_state.student_register = ""

                    st.rerun()

# ==================================================
# ADMIN LOGIN
# ==================================================

else:

    if not st.session_state.admin_logged_in:

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            st.markdown(
                '<div class="login-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-title">👨‍🏫 Admin Login</div>',
                unsafe_allow_html=True
            )

            username = st.text_input(
                "Admin Username",
                key="admin_username",
                placeholder="admin"
            )

            admin_password = st.text_input(
                "Admin Password",
                type="password",
                key="admin_password",
                placeholder="Enter password"
            )

            if st.button(
                "🔐 Admin Login",
                use_container_width=True
            ):

                if (
                    username == "admin"
                    and admin_password == "admin123"
                ):

                    st.session_state.admin_logged_in = True

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid Admin Username or Password"
                    )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

    # ==================================================
    # ADMIN DASHBOARD
    # ==================================================

    if st.session_state.admin_logged_in:

        st.success(
            "Admin Login Successful! 🎉"
        )

        st.markdown(
            '<div class="section-title">📊 Admin Dashboard</div>',
            unsafe_allow_html=True
        )

        # ==================================================
        # STATISTICS
        # ==================================================

        cursor.execute(
            "SELECT COUNT(*) FROM students"
        )

        total_students = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM certificates
            WHERE status = 'Completed'
            """
        )

        total_completed = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM certificates
            WHERE status = 'Pending'
            """
        )

        total_pending = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM certificates
            WHERE status = 'Status'
            """
        )

        total_not_updated = cursor.fetchone()[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "👥 Total Students",
                total_students
            )

        with col2:
            st.metric(
                "✅ Completed Certificates",
                total_completed
            )

        with col3:
            st.metric(
                "⏳ Pending Certificates",
                total_pending
            )

        with col4:
            st.metric(
                "❓ Not Updated",
                total_not_updated
            )

        # ==================================================
        # ADMIN MENU
        # ==================================================

        st.divider()

        admin_menu = st.selectbox(
            "🛠️ Admin Menu",
            [
                "Add New Student",
                "Remove Student",
                "Add Certificate",
                "Remove Certificate",
                "Student List",
                "Certificate Overview",
                "Update Certificate",
                "Uploaded Certificates"
            ]
        )

        # ==================================================
        # ADD STUDENT
        # ==================================================

        if admin_menu == "Add New Student":

            st.subheader(
                "➕ Add New Student"
            )

            new_register = st.text_input(
                "Register Number",
                key="new_register"
            )

            new_name = st.text_input(
                "Student Name",
                key="new_name"
            )

            new_department = st.text_input(
                "Department",
                key="new_department"
            )

            new_password = st.text_input(
                "Student Password",
                type="password",
                key="new_password"
            )

            if st.button(
                "➕ Add Student"
            ):

                if (
                    new_register
                    and new_name
                    and new_department
                    and new_password
                ):

                    cursor.execute(
                        """
                        SELECT register_no
                        FROM students
                        WHERE register_no = ?
                        """,
                        (new_register,)
                    )

                    existing_student = cursor.fetchone()

                    if existing_student:

                        st.error(
                            "❌ Register Number already exists!"
                        )

                    else:

                        cursor.execute(
                            """
                            INSERT INTO students
                            (
                                register_no,
                                name,
                                department,
                                password
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                new_register,
                                new_name,
                                new_department,
                                new_password
                            )
                        )

                        conn.commit()

                        st.success(
                            "✅ Student added successfully!"
                        )

                else:

                    st.warning(
                        "⚠️ Please fill all fields"
                    )

        # ==================================================
        # REMOVE STUDENT
        # ==================================================

        elif admin_menu == "Remove Student":

            st.subheader(
                "🗑️ Remove Student"
            )

            cursor.execute(
                """
                SELECT register_no, name, department
                FROM students
                ORDER BY CAST(
                    substr(
                        register_no,
                        instr(register_no, 'BAI') + 3
                    ) AS INTEGER
                )
                """
            )

            students_for_delete = cursor.fetchall()

            if students_for_delete:

                student_options = {
                    f"{student[1]} - {student[0]}": student[0]
                    for student in students_for_delete
                }

                selected_student = st.selectbox(
                    "Select Student to Remove",
                    list(student_options.keys()),
                    key="delete_student_select"
                )

                selected_register = student_options[
                    selected_student
                ]

                st.warning(
                    "⚠️ Deleting this student will also delete all certificates assigned to this student."
                )

                if st.button(
                    "🗑️ Delete Student",
                    type="primary"
                ):

                    cursor.execute(
                        """
                        DELETE FROM certificates
                        WHERE register_no = ?
                        """,
                        (selected_register,)
                    )

                    cursor.execute(
                        """
                        DELETE FROM students
                        WHERE register_no = ?
                        """,
                        (selected_register,)
                    )

                    conn.commit()

                    st.success(
                        "✅ Student and their certificates deleted successfully!"
                    )

                    st.rerun()

            else:

                st.info(
                    "No students available to remove."
                )

        # ==================================================
        # ADD CERTIFICATE
        # ==================================================

        elif admin_menu == "Add Certificate":

            st.subheader(
                "📜 Add Certificate"
            )

            certificate_register = st.text_input(
                "Student Register Number",
                key="certificate_register"
            )

            certificate_name = st.text_input(
                "Certificate Name",
                key="certificate_name"
            )

            certificate_status = st.selectbox(
                "Initial Certificate Status",
                [
                    "Status",
                    "Pending",
                    "Completed"
                ],
                key="certificate_status"
            )

            st.caption(
                "ℹ️ If 'Status' is selected, the student will choose Yes or No."
            )

            certificate_deadline = st.text_input(
                "Deadline",
                key="certificate_deadline",
                placeholder="Example: 15 Sep 2026"
            )

            if st.button(
                "➕ Add Certificate"
            ):

                if (
                    certificate_register
                    and certificate_name
                    and certificate_deadline
                ):

                    cursor.execute(
                        """
                        SELECT register_no
                        FROM students
                        WHERE register_no = ?
                        """,
                        (certificate_register,)
                    )

                    student_exists = cursor.fetchone()

                    if student_exists:

                        cursor.execute(
                            """
                            SELECT id
                            FROM certificates
                            WHERE register_no = ?
                            AND certificate_name = ?
                            """,
                            (
                                certificate_register,
                                certificate_name
                            )
                        )

                        certificate_exists = cursor.fetchone()

                        if certificate_exists:

                            st.error(
                                "❌ This certificate already exists for this student!"
                            )

                        else:

                            cursor.execute(
                                """
                                INSERT INTO certificates
                                (
                                    register_no,
                                    certificate_name,
                                    status,
                                    deadline
                                )
                                VALUES (?, ?, ?, ?)
                                """,
                                (
                                    certificate_register,
                                    certificate_name,
                                    certificate_status,
                                    certificate_deadline
                                )
                            )

                            conn.commit()

                            st.success(
                                "✅ Certificate added successfully!"
                            )

                    else:

                        st.error(
                            "❌ Student Register Number not found!"
                        )

                else:

                    st.warning(
                        "⚠️ Please fill all fields"
                    )

        # ==================================================
        # REMOVE CERTIFICATE
        # ==================================================

        elif admin_menu == "Remove Certificate":

            st.subheader(
                "🗑️ Remove Certificate"
            )

            cursor.execute(
                """
                SELECT id,
                       register_no,
                       certificate_name,
                       status,
                       deadline
                FROM certificates
                ORDER BY
                    CAST(
                        substr(
                            register_no,
                            instr(register_no, 'BAI') + 3
                        ) AS INTEGER
                    ),
                    certificate_name
                """
            )

            certificates_for_delete = cursor.fetchall()

            if certificates_for_delete:

                certificate_options = {}

                for certificate in certificates_for_delete:

                    certificate_id = certificate[0]
                    register = certificate[1]
                    name = certificate[2]
                    status = certificate[3]

                    display_name = (
                        f"{register} - {name} ({status})"
                    )

                    certificate_options[
                        display_name
                    ] = certificate_id

                selected_certificate = st.selectbox(
                    "Select Certificate to Remove",
                    list(certificate_options.keys()),
                    key="delete_certificate_select"
                )

                selected_certificate_id = certificate_options[
                    selected_certificate
                ]

                st.warning(
                    "⚠️ This certificate record will be permanently deleted."
                )

                if st.button(
                    "🗑️ Delete Certificate",
                    type="primary"
                ):

                    cursor.execute(
                        """
                        DELETE FROM certificates
                        WHERE id = ?
                        """,
                        (selected_certificate_id,)
                    )

                    conn.commit()

                    st.success(
                        "✅ Certificate deleted successfully!"
                    )

                    st.rerun()

            else:

                st.info(
                    "No certificates available to remove."
                )

        # ==================================================
        # STUDENT LIST
        # ==================================================

        elif admin_menu == "Student List":

            st.subheader(
                "👥 Student List"
            )

            cursor.execute(
                """
                SELECT register_no,
                       name,
                       department
                FROM students
                ORDER BY CAST(
                    substr(
                        register_no,
                        instr(register_no, 'BAI') + 3
                    ) AS INTEGER
                )
                """
            )

            students = cursor.fetchall()

            if students:

                student_df = pd.DataFrame(
                    students,
                    columns=[
                        "Register Number",
                        "Name",
                        "Department"
                    ]
                )

                st.dataframe(
                    student_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No students found."
                )

        # ==================================================
        # CERTIFICATE OVERVIEW - FOLDER STYLE
        # ==================================================

        elif admin_menu == "Certificate Overview":

            st.subheader(
                "📜 Certificate Overview"
            )

            st.write(
                "📁 Select a student to view all their certificates."
            )

            # --------------------------------------------------
            # GET ALL STUDENTS - NUMERIC REGISTER ORDER
            # --------------------------------------------------

            cursor.execute(
                """
                SELECT register_no,
                       name,
                       department
                FROM students
                ORDER BY CAST(
                    substr(
                        register_no,
                        instr(register_no, 'BAI') + 3
                    ) AS INTEGER
                )
                """
            )

            all_students = cursor.fetchall()

            if all_students:

                # --------------------------------------------------
                # STUDENT FOLDER LIST
                # --------------------------------------------------

                for student_index, student_data in enumerate(all_students):

                    student_register = student_data[0]
                    student_name = student_data[1]
                    student_department = student_data[2]

                    # Get certificate count
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM certificates
                        WHERE register_no = ?
                        """,
                        (student_register,)
                    )

                    certificate_count = cursor.fetchone()[0]

                    # --------------------------------------------------
                    # FOLDER
                    # --------------------------------------------------

                    with st.expander(
                        f"📁 {student_name}  |  🆔 {student_register}  |  📜 {certificate_count} Certificate(s)",
                        expanded=False
                    ):

                        st.markdown(
                            f"### 👤 {student_name}"
                        )

                        profile_col1, profile_col2, profile_col3 = st.columns(3)

                        with profile_col1:

                            st.info(
                                f"🆔 Register Number\n\n**{student_register}**"
                            )

                        with profile_col2:

                            st.info(
                                f"👤 Student Name\n\n**{student_name}**"
                            )

                        with profile_col3:

                            st.info(
                                f"🏫 Department\n\n**{student_department}**"
                            )

                        st.divider()

                        # --------------------------------------------------
                        # GET THIS STUDENT'S CERTIFICATES
                        # --------------------------------------------------

                        cursor.execute(
                            """
                            SELECT id,
                                   certificate_name,
                                   status,
                                   deadline
                            FROM certificates
                            WHERE register_no = ?
                            ORDER BY id
                            """,
                            (student_register,)
                        )

                        student_certificates = cursor.fetchall()

                        if student_certificates:

                            st.markdown(
                                "### 📜 All Certificates"
                            )

                            for cert_index, certificate in enumerate(
                                student_certificates
                            ):

                                certificate_id = certificate[0]
                                certificate_name = certificate[1]
                                certificate_status = certificate[2]
                                certificate_deadline = certificate[3]

                                cert_col1, cert_col2, cert_col3 = st.columns(
                                    [2, 1, 1]
                                )

                                with cert_col1:

                                    st.markdown(
                                        f"**📜 {certificate_name}**"
                                    )

                                with cert_col2:

                                    if certificate_status == "Completed":

                                        st.success(
                                            "✅ Completed"
                                        )

                                    elif certificate_status == "Pending":

                                        st.warning(
                                            "⏳ Pending"
                                        )

                                    else:

                                        st.info(
                                            "❓ Not Updated"
                                        )

                                with cert_col3:

                                    st.write(
                                        f"📅 **{certificate_deadline}**"
                                    )

                                st.divider()

                        else:

                            st.info(
                                "📭 No certificates assigned to this student."
                            )

            else:

                st.info(
                    "No students found."
                )

        # ==================================================
        # UPDATE CERTIFICATE
        # ==================================================

        elif admin_menu == "Update Certificate":

            st.subheader(
                "✏️ Update Certificate"
            )

            update_register = st.text_input(
                "Student Register Number",
                key="update_register"
            )

            update_certificate = st.text_input(
                "Certificate Name",
                key="update_certificate"
            )

            update_status = st.selectbox(
                "New Status",
                [
                    "Status",
                    "Pending",
                    "Completed"
                ],
                key="update_status"
            )

            update_deadline = st.text_input(
                "New Deadline",
                key="update_deadline"
            )

            if st.button(
                "💾 Update Certificate"
            ):

                if (
                    update_register
                    and update_certificate
                    and update_deadline
                ):

                    cursor.execute(
                        """
                        SELECT id
                        FROM certificates
                        WHERE register_no = ?
                        AND certificate_name = ?
                        """,
                        (
                            update_register,
                            update_certificate
                        )
                    )

                    certificate_exists = cursor.fetchone()

                    if certificate_exists:

                        cursor.execute(
                            """
                            UPDATE certificates
                            SET status = ?,
                                deadline = ?
                            WHERE register_no = ?
                            AND certificate_name = ?
                            """,
                            (
                                update_status,
                                update_deadline,
                                update_register,
                                update_certificate
                            )
                        )

                        conn.commit()

                        st.success(
                            "✅ Certificate updated successfully!"
                        )

                    else:

                        st.error(
                            "❌ Certificate not found!"
                        )

                else:

                    st.warning(
                        "⚠️ Please fill all fields"
                    )

        # ==================================================
        # UPLOADED CERTIFICATES
        # ==================================================

        elif admin_menu == "Uploaded Certificates":

            st.subheader(
                "📂 Uploaded Certificates"
            )

            upload_folder = "certificates"

            if os.path.exists(upload_folder):

                uploaded_files = os.listdir(
                    upload_folder
                )

                if uploaded_files:

                    for file_name in uploaded_files:

                        file_path = os.path.join(
                            upload_folder,
                            file_name
                        )

                        st.markdown(
                            f"📄 **{file_name}**"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            with open(
                                file_path,
                                "rb"
                            ) as file:

                                st.download_button(
                                    "⬇️ Download",
                                    file,
                                    file_name=file_name,
                                    key="download_" + file_name
                                )

                        with col2:

                            if st.button(
                                "🗑️ Delete",
                                key="delete_upload_" + file_name,
                                type="primary"
                            ):

                                try:

                                    os.remove(
                                        file_path
                                    )

                                    st.success(
                                        f"✅ {file_name} deleted successfully!"
                                    )

                                    st.rerun()

                                except Exception as e:

                                    st.error(
                                        f"❌ Unable to delete file: {e}"
                                    )

                        st.divider()

                else:

                    st.info(
                        "No certificates uploaded yet."
                    )

            else:

                st.info(
                    "No certificates uploaded yet."
                )

        # ==================================================
        # ADMIN LOGOUT
        # ==================================================

        st.markdown("---")

        if st.button(
            "🚪 Admin Logout"
        ):

            st.session_state.admin_logged_in = False

            st.rerun()

# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <div class="footer">
        🎓 Student Certificate Management System<br>
        Certificate Tracking & Deadline Management
    </div>
    """,
    unsafe_allow_html=True
)
