

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Performance Analytics Dashboard")
st.caption("Python + MySQL | Student Academic Insights")

# ---------------- DATABASE PASSWORD ----------------
password = st.text_input(
    "Enter MySQL password",
    type="password"
)

if password:
    engine = None

    try:
        # ---------------- DATABASE CONNECTION ----------------
        connection_url = URL.create(
            drivername="mysql+pymysql",
            username="root",
            password=password,
            host="localhost",
            port=3306,
            database="student_analysis"
        )

        engine = create_engine(connection_url)

        with engine.connect():
            st.success("MySQL connected successfully!")

        # ---------------- SQL QUERIES ----------------
        marks_query = """
            SELECT
                s.student_id,
                s.name,
                s.semester,
                ROUND(AVG(m.marks), 2) AS average_marks
            FROM students s
            JOIN marks m ON s.student_id = m.student_id
            GROUP BY s.student_id, s.name, s.semester
            ORDER BY average_marks DESC
        """

        attendance_query = """
            SELECT
                s.student_id,
                s.name,
                s.semester,
                a.attended,
                a.total,
                ROUND(a.attended * 100.0 / a.total, 2)
                    AS attendance_percentage
            FROM students s
            JOIN attendance a ON s.student_id = a.student_id
        """

        subject_query = """
            SELECT
                s.student_id,
                s.name,
                s.semester,
                m.subject,
                m.marks
            FROM students s
            JOIN marks m ON s.student_id = m.student_id
        """

        marks_df = pd.read_sql(marks_query, engine)
        attendance_df = pd.read_sql(attendance_query, engine)
        subject_df = pd.read_sql(subject_query, engine)

        # ---------------- SEARCH AND FILTERS ----------------
        st.subheader("🔎 Find Students")

        search_name = st.text_input(
            "Search by student name",
            placeholder="Enter a name, e.g. Aarav"
        )

        semesters = sorted(
            marks_df["semester"].dropna().unique().tolist()
        )

        selected_semesters = st.multiselect(
            "Filter by semester",
            options=semesters,
            default=semesters
        )

        filtered_marks = marks_df[
            marks_df["semester"].isin(selected_semesters)
            & marks_df["name"].str.contains(
                search_name,
                case=False,
                na=False,
                regex=False
            )
        ].copy()

        filtered_ids = filtered_marks["student_id"]

        filtered_attendance = attendance_df[
            attendance_df["student_id"].isin(filtered_ids)
        ].copy()

        filtered_subjects = subject_df[
            subject_df["student_id"].isin(filtered_ids)
        ].copy()

        # ---------------- KEY METRICS ----------------
        st.divider()
        st.subheader("📌 Key Performance Indicators")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Students Found",
            len(filtered_marks)
        )

        overall_average = (
            filtered_marks["average_marks"].mean()
            if not filtered_marks.empty else 0
        )

        col2.metric(
            "Average Marks",
            f"{overall_average:.2f}"
        )

        average_attendance = (
            filtered_attendance["attendance_percentage"].mean()
            if not filtered_attendance.empty else 0
        )

        col3.metric(
            "Average Attendance",
            f"{average_attendance:.2f}%"
        )

        # ---------------- PERFORMANCE AND ATTENDANCE ----------------
        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("🎓 Student Performance")

            if not filtered_marks.empty:
                performance_chart = filtered_marks.set_index("name")[
                    "average_marks"
                ]
                st.bar_chart(performance_chart)
                st.dataframe(filtered_marks, hide_index=True)
            else:
                st.info("No students match your filters.")

        with right:
            st.subheader("📅 Attendance Analysis")

            if not filtered_attendance.empty:
                attendance_chart = filtered_attendance.set_index("name")[
                    "attendance_percentage"
                ]
                st.bar_chart(attendance_chart)
                st.dataframe(filtered_attendance, hide_index=True)
            else:
                st.info("No attendance records for these students.")

        # ---------------- SUBJECT ANALYSIS ----------------
        st.divider()
        st.subheader("📚 Subject-wise Average Marks")

        if not filtered_subjects.empty:
            subject_averages = (
                filtered_subjects.groupby("subject")["marks"]
                .mean()
                .round(2)
                .sort_values(ascending=False)
            )

            st.bar_chart(subject_averages)

            subject_table = (
                filtered_subjects.groupby("subject")
                .agg(
                    average_marks=("marks", "mean"),
                    highest_marks=("marks", "max"),
                    lowest_marks=("marks", "min")
                )
                .round(2)
                .reset_index()
            )

            st.dataframe(subject_table, hide_index=True)
        else:
            st.info("No subject marks available for this selection.")

        # ---------------- LOW ATTENDANCE WARNING ----------------
        st.divider()
        st.subheader("⚠️ Low Attendance Warning")

        low_attendance = filtered_attendance[
            filtered_attendance["attendance_percentage"] < 75
        ]

        if low_attendance.empty:
            st.success(
                "No students below 75% attendance in this selection."
            )
        else:
            st.warning("Students with attendance below 75%")

            st.dataframe(
                low_attendance[
                    ["name", "semester", "attendance_percentage"]
                ],
                hide_index=True
            )

        # ---------------- CSV DOWNLOADS ----------------
        st.divider()
        st.subheader("📥 Download Reports")

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            st.download_button(
                label="Download Performance CSV",
                data=filtered_marks.to_csv(index=False).encode("utf-8"),
                file_name="student_performance.csv",
                mime="text/csv"
            )

        with download_col2:
            st.download_button(
                label="Download Attendance CSV",
                data=filtered_attendance.to_csv(index=False).encode("utf-8"),
                file_name="student_attendance.csv",
                mime="text/csv"
            )

    except Exception as error:
        st.error(
            "Something went wrong. Check your database connection and tables."
        )
        st.code(str(error))

    finally:
        if engine is not None:
            engine.dispose()

else:
    st.info("Enter your MySQL password above to load the dashboard.")
