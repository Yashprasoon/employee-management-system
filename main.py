

import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Database Connection
def connect_to_database():
    mydb = mysql.connector.connect(host="localhost", user="root", password="admin", database="employee")
    return mydb

# Authentication
def login_user(userid, password):
    mydb = connect_to_database()
    c = mydb.cursor()
    c.execute("SELECT * FROM users WHERE user_id = %s AND password = %s", (userid, password))
    return c.fetchone()

# User Registration
def register_user(user_id, employee_id, username, password):
    mydb = connect_to_database()
    c = mydb.cursor()
    c.execute("INSERT INTO users (user_id, employee_id, username, password) VALUES (%s, %s, %s, %s)", (user_id, employee_id, username, password))
    mydb.commit()

# Attendance Tracking
def mark_attendance(employee_id):
    mydb = connect_to_database()
    c = mydb.cursor()

    if 'user' not in st.session_state or st.session_state['user'] != employee_id:
        # New user or different user logged in
        st.session_state['user'] = employee_id
        login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO Attendance (employee_id, attendance_date, clock_in_time) VALUES (%s, %s, %s)",
                  (employee_id, datetime.now().date(), login_time))
        mydb.commit()
        st.success(f"User {employee_id} logged in. Clock-in time recorded.")
    else:
        # Same user logged in again, consider this as logout
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE Attendance SET clock_out_time = %s WHERE employee_id = %s AND clock_out_time IS NULL",
                  (logout_time, employee_id))
        mydb.commit()
        st.success(f"User {employee_id} logged out. Clock-out time recorded.")

# Leave Management
def request_leave(employee_id, start_date, end_date, reason):
    mydb = connect_to_database()
    c = mydb.cursor()
    request_date = datetime.now().date()  # Get the current date for the leave request

    c.execute("INSERT INTO LeaveRequest (employee_id, request_date, start_date, end_date, leave_type, status) VALUES (%s, %s, %s, %s, %s, %s)",
              (employee_id, request_date, start_date, end_date, reason, 'pending'))
    mydb.commit()


# Data Visualization
def visualize_data():
    mydb = connect_to_database()
    c = mydb.cursor()
    c.execute("SELECT * FROM attendance")
    data = c.fetchall()

    df = pd.DataFrame(data, columns=['attendance_id', 'employee_id', 'attendance_date', 'clock_in_time', 'clock_out_time'])
    # Example: Bar chart for attendance status
    plt.bar(df['attendance_date'], df['employee_id'])
    st.pyplot(plt)

# Streamlit App
def main():
    st.title("EMPLOYEE MANAGEMENT SYSTEM")
    choice = st.sidebar.selectbox("My Menu", ("Home", "Login", "Register", "Attendance", "Leave Management", "Data Visualization"))

    if choice == "Home":
        st.image("./emp-payroll.png")
        st.header("WELCOME")
        st.write("THIS IS THE APPLICATION DEVELOPED BY YASH PRASOON AS PART OF TRAINING PROJECT.")

    elif choice == "Login":
        st.subheader("Login")
        userid = st.text_input("Userid")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(userid, password)
            if user:
                st.success("Login successful")
                st.session_state['user'] = userid
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.subheader("Register")
        user_id = st.text_input("New Userid")
        employee_id = st.text_input("Employee Id")
        username = st.text_input("Username")
        password = st.text_input("New Password", type="password")
        if st.button("Register"):
            register_user(user_id, employee_id, username, password)
            st.success("Registration successful")

    elif choice == "Attendance":
        st.title("Employee Attendance Tracking")

        employee_id = st.text_input("Enter Employee ID")
        if st.button("Login/Logout"):
            mark_attendance(employee_id)

    elif choice == "Leave Management":
        st.subheader("Request Leave")
        if 'user' not in st.session_state:
            st.warning("Please log in first.")
        else:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            reason = st.text_area("Reason")
            if st.button("Submit Leave Request"):
                request_leave(st.session_state['user'], start_date, end_date, reason)
                st.success("Leave request submitted successfully!")

    elif choice == "Data Visualization":
        st.subheader("Attendance Data Visualization")
        visualize_data()

if __name__ == "__main__":
    main()

