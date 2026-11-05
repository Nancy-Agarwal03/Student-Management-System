
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

password = input("Enter your MySQL password: ")

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="******",
    host="localhost",
    port=3306,
    database="student_analysis"
)

engine = create_engine(connection_url)

try:
    with engine.connect():
        print("MySQL connected successfully!")

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
    print(df)

except Exception as error:
    print("Error:", error)

finally:
    engine.dispose()
