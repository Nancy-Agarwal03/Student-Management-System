
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

password = input("Enter your MySQL password: ")

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=password,
    host="localhost",
    port=3306,
    database="student_analysis"
)

engine = create_engine(connection_url)

try:
    query = """
    SELECT
        s.name,
        ROUND(AVG(m.marks), 2) AS average_marks
    FROM students s
    JOIN marks m
        ON s.student_id = m.student_id
    GROUP BY s.student_id, s.name
    ORDER BY average_marks DESC
    """

    df = pd.read_sql(query, engine)

    print("\nStudent Performance Report:")
    print(df)


    
    attendance_query = """
    SELECT
        s.name,
        a.attended,
        a.total,
        ROUND((a.attended * 100.0) / a.total, 2)
            AS attendance_percentage
    FROM students s
    JOIN attendance a
        ON s.student_id = a.student_id
    ORDER BY attendance_percentage DESC
    """

    attendance_df = pd.read_sql(attendance_query, engine)

    print("\nAttendance Analysis:")
    print(attendance_df)


    # Attendance graph
    plt.figure(figsize=(8, 5))
    plt.bar(
        attendance_df["name"],
        attendance_df["attendance_percentage"]
    )

    plt.title("Student Attendance Analysis")
    plt.xlabel("Student Name")
    plt.ylabel("Attendance Percentage (%)")
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig("student_graph.png")
    plt.close()

    # Low attendance warning
    print("\nLow Attendance Warning (below 75%):")

    low_attendance = attendance_df[
        attendance_df["attendance_percentage"] < 75
    ]

    if low_attendance.empty:
        print("All students have attendance of 75% or above.")
    else:
        print(low_attendance[["name", "attendance_percentage"]])


    plt.figure(figsize=(8, 5))
    plt.bar(df["name"], df["average_marks"])

    plt.title("Student Performance Analysis")
    plt.xlabel("Student Name")
    plt.ylabel("Average Marks")
    plt.ylim(0, 100)

    plt.tight_layout()
    plt.savefig("student_graph.png")
    plt.close()
except Exception as error:
    print("Error:", error)

finally:
    engine.dispose()
