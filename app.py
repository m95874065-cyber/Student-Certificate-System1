    # ========================================================
    # LINKEDIN UPDATES
    # ========================================================

    elif admin_menu == "LinkedIn Updates":

        st.subheader(
            "🔗 LinkedIn Updates"
        )

        # ----------------------------------------------------
        # COMPLETED CERTIFICATES
        # ----------------------------------------------------

        completed_certificates = [
            c
            for c in all_certificates
            if c["status"] == "Completed"
        ]

        total_completed_linkedin = len(
            completed_certificates
        )

        verified_count = sum(
            1
            for c in completed_certificates
            if get_linkedin_status(c)
            == "Verified"
        )

        submitted_count = sum(
            1
            for c in completed_certificates
            if get_linkedin_status(c)
            == "Submitted"
        )

        not_updated_count = (
            total_completed_linkedin
            - verified_count
            - submitted_count
        )

        # ----------------------------------------------------
        # TOP STATISTICS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "📜 Completed Certificates",
                total_completed_linkedin
            )

        with col2:

            st.metric(
                "✅ Verified",
                verified_count
            )

        with col3:

            st.metric(
                "🔗 Posted / Submitted",
                submitted_count
            )

        with col4:

            st.metric(
                "❌ Not Updated",
                not_updated_count
            )

        # ----------------------------------------------------
        # LINKEDIN PROGRESS
        # ----------------------------------------------------

        if total_completed_linkedin > 0:

            linkedin_progress = (
                verified_count
                + submitted_count
            ) / total_completed_linkedin

        else:

            linkedin_progress = 0

        st.progress(
            linkedin_progress
        )

        st.write(
            f"**{verified_count + submitted_count} / "
            f"{total_completed_linkedin} completed certificates "
            f"are marked as LinkedIn updated "
            f"({linkedin_progress * 100:.0f}%)**"
        )

        st.markdown("---")

        # ====================================================
        # ALL STUDENTS
        # ====================================================

        linkedin_rows = []

        for student_item in all_students:

            student_register = (
                student_item["register_no"]
            )

            # Get completed certificates
            student_completed = [
                c
                for c in completed_certificates
                if c["register_no"]
                == student_register
            ]

            # Count LinkedIn updated certificates
            updated_for_student = sum(
                1
                for c in student_completed
                if get_linkedin_status(c)
                in [
                    "Submitted",
                    "Verified"
                ]
            )

            # Pending LinkedIn updates
            pending_for_student = (
                len(student_completed)
                - updated_for_student
            )

            linkedin_rows.append(
                {
                    "Register Number":
                    student_register,

                    "Student Name":
                    student_item["name"],

                    "Department":
                    student_item["department"],

                    "LinkedIn Profile":
                    get_linkedin_profile_url(
                        student_item
                    )
                    or "Not Added",

                    "Completed Certificates":
                    len(student_completed),

                    "LinkedIn Updated":
                    updated_for_student,

                    "Pending":
                    pending_for_student
                }
            )

        # ====================================================
        # STUDENT-WISE LINKEDIN TRACKING
        # ====================================================

        if linkedin_rows:

            st.markdown(
                "### 👨‍🎓 Student-wise LinkedIn Tracking"
            )

            linkedin_df = pd.DataFrame(
                linkedin_rows
            )

            st.dataframe(
                linkedin_df,
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # TOTAL STUDENT COUNT
            # ------------------------------------------------

            st.info(
                f"👨‍🎓 Total Students: "
                f"{len(all_students)}"
            )

            # =================================================
            # STUDENT DETAILS
            # =================================================

            st.markdown(
                "### 📋 Student Details"
            )

            for student_item in all_students:

                student_register = (
                    student_item["register_no"]
                )

                student_completed = [
                    c
                    for c in completed_certificates
                    if c["register_no"]
                    == student_register
                ]

                student_updated = sum(
                    1
                    for c in student_completed
                    if get_linkedin_status(c)
                    in [
                        "Submitted",
                        "Verified"
                    ]
                )

                student_pending = (
                    len(student_completed)
                    - student_updated
                )

                profile_url = (
                    get_linkedin_profile_url(
                        student_item
                    )
                )

                # --------------------------------------------
                # EXPANDER
                # --------------------------------------------

                with st.expander(
                    f"👨‍🎓 {student_item['name']} | "
                    f"🆔 {student_register} | "
                    f"🔗 {student_updated}/"
                    f"{len(student_completed)} Updated"
                ):

                    # Student information

                    detail_col1, detail_col2, detail_col3 = (
                        st.columns(3)
                    )

                    with detail_col1:

                        st.write(
                            f"**👤 Name:** "
                            f"{student_item['name']}"
                        )

                    with detail_col2:

                        st.write(
                            f"**🆔 Register Number:** "
                            f"{student_register}"
                        )

                    with detail_col3:

                        st.write(
                            f"**🏫 Department:** "
                            f"{student_item['department']}"
                        )

                    st.markdown("---")

                    # ----------------------------------------
                    # LINKEDIN PROFILE
                    # ----------------------------------------

                    if profile_url:

                        st.markdown(
                            f"🔗 [Open LinkedIn Profile]"
                            f"({profile_url})"
                        )

                    else:

                        st.warning(
                            "⚠️ LinkedIn profile not added "
                            "by this student."
                        )

                    # ----------------------------------------
                    # STUDENT LINKEDIN SUMMARY
                    # ----------------------------------------

                    summary_col1, summary_col2, summary_col3 = (
                        st.columns(3)
                    )

                    with summary_col1:

                        st.metric(
                            "📜 Completed",
                            len(student_completed)
                        )

                    with summary_col2:

                        st.metric(
                            "🔗 LinkedIn Updated",
                            student_updated
                        )

                    with summary_col3:

                        st.metric(
                            "⏳ Pending",
                            student_pending
                        )

                    st.markdown("---")

                    # ----------------------------------------
                    # CERTIFICATE DETAILS
                    # ----------------------------------------

                    if student_completed:

                        for certificate in student_completed:

                            linkedin_status = (
                                get_linkedin_status(
                                    certificate
                                )
                            )

                            c1, c2 = st.columns(
                                [4, 2]
                            )

                            with c1:

                                st.write(
                                    f"📜 **"
                                    f"{certificate['certificate_name']}"
                                    f"**"
                                )

                                if linkedin_status == "Verified":

                                    st.success(
                                        "Status: ✅ Verified"
                                    )

                                elif linkedin_status == "Submitted":

                                    st.info(
                                        "Status: 🔗 Posted / Submitted"
                                    )

                                else:

                                    st.warning(
                                        "Status: ❌ Not Updated"
                                    )

                            with c2:

                                # VERIFY

                                if linkedin_status == "Submitted":

                                    if st.button(
                                        "✅ Verify",
                                        key=(
                                            f"verify_linkedin_"
                                            f"{certificate['id']}"
                                        )
                                    ):

                                        try:

                                            update_linkedin_status(
                                                certificate["id"],
                                                "Verified"
                                            )

                                            st.rerun()

                                        except Exception as e:

                                            st.error(
                                                f"❌ Error: {e}"
                                            )

                                # MARK NOT UPDATED

                                if linkedin_status in [
                                    "Submitted",
                                    "Verified"
                                ]:

                                    if st.button(
                                        "❌ Mark Not Updated",
                                        key=(
                                            f"not_updated_linkedin_"
                                            f"{certificate['id']}"
                                        )
                                    ):

                                        try:

                                            update_linkedin_status(
                                                certificate["id"],
                                                "Not Updated"
                                            )

                                            st.rerun()

                                        except Exception as e:

                                            st.error(
                                                f"❌ Error: {e}"
                                            )

                            st.markdown("---")

                    else:

                        st.info(
                            "📭 This student has no completed "
                            "certificates yet."
                        )

        else:

            st.info(
                "📭 No students available."
            )
