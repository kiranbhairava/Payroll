
############main thing######################
import streamlit as st
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text
import calendar
from app import generate_exact_payslip_pdf
import inflect

from datetime import datetime

# Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Kiran%40123'
DB_NAME = 'ems'

# Create the SQLAlchemy engine
engine = create_engine(f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Declare the database model
Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employee_salary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    designation = Column(String(100))
    month_year = Column(String(7), nullable=False)  # Format: 'MM-YYYY'
    date_of_joining = Column(Date)
    pan_card = Column(String(50))

    basic_pay = Column(Float, default=0.0)
    hra = Column(Float, default=0.0)
    lta = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    total_addition = Column(Float, default=0.0)

    provident_fund = Column(Float, default=0.0)
    esi = Column(Float, default=0.0)
    professional_tax = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)

    days_worked = Column(Integer, default=0)
    net_salary = Column(Float, default=0.0)

    salary_in_words = Column(Text)


def number_to_words(number):
    p = inflect.engine()
    words = p.number_to_words(int(number))
    decimal_part = int((number % 1) * 100)
    if decimal_part > 0:
        words += f" and {decimal_part}/100"
    return words.capitalize() + " only"

# def number_to_words(number):
#     p = inflect.engine()
#     # Convert the integer part to words
#     integer_part = int(number)
#     words = p.number_to_words(integer_part)

#     # Extract and convert the decimal part to words
#     decimal_part = int(round((number % 1) * 100))  # Round to handle floating-point precision
#     if decimal_part > 0:
#         paisa_words = p.number_to_words(decimal_part)
#         words += f" and {paisa_words} paisa"

#     return words.capitalize() + " only"

def calculate_net_salary(total_addition, month_year, days_worked, total_deductions):
    try:
        month, year = map(int, month_year.split('-'))
        if not (1 <= month <= 12 and 1900 <= year <= 2100):
            raise ValueError("Invalid month or year")
        
        # Get the actual number of days in the month
        total_days = calendar.monthrange(year, month)[1]
        
        # Ensure days_worked doesn't exceed the actual days in the month
        days_worked = min(days_worked, total_days)
        
        daily_salary = total_addition / total_days
        gross_salary = daily_salary * days_worked
        net_salary = gross_salary - total_deductions
        
        return max(net_salary, 0)  # Ensure net salary is not negative
    except ValueError as e:
        st.error(f"Error in salary calculation: {str(e)}")
        return 0

def distribute_salary(total_salary):
    basic_pay = total_salary * 0.5
    hra = total_salary * 0.3
    lta = total_salary * 0.1
    other_allowance = total_salary * 0.1
    return basic_pay, hra, lta, other_allowance

def main():
    st.title("Employee Payroll Management System")

    # Employee search
    st.header("Search Employee")
    search_id = st.text_input("Enter Employee ID to Search")
    if st.button("Search"):
        try:
            employee = session.query(Employee).filter_by(employee_id=search_id).one_or_none()
            if employee:
                st.session_state.employee_data = {
                    'employee_id': employee.employee_id,
                    'designation': employee.designation,
                    'employee_name': employee.employee_name,
                    'date_of_joining': employee.date_of_joining,
                    'month_year': employee.month_year,
                    'pan_card': employee.pan_card,
                    'basic_pay': employee.basic_pay,
                    'hra': employee.hra,
                    'lta': employee.lta,
                    'other_allowance': employee.other_allowance,
                    'total_addition': employee.total_addition,
                    'provident_fund': employee.provident_fund,
                    'esi': employee.esi,
                    'professional_tax': employee.professional_tax,
                    'tax': employee.tax,
                    'total_deductions': employee.total_deductions,
                    'days_worked': employee.days_worked,
                    'net_salary': employee.net_salary,
                    'salary_in_words': employee.salary_in_words
                }
                st.success("Employee record found and details loaded.")
            else:
                st.error("No employee found with the given ID.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Initialize session state for form fields if not already done
    if 'employee_data' not in st.session_state:
        st.session_state.employee_data = {}

    # Employee details
    st.header("Employee Details")
    employee_id = st.text_input("Employee ID", value=st.session_state.employee_data.get('employee_id', ''))
    designation = st.text_input("Designation", value=st.session_state.employee_data.get('designation', ''))
    employee_name = st.text_input("Name", value=st.session_state.employee_data.get('employee_name', ''))
    
    date_of_joining = st.session_state.employee_data.get('date_of_joining')
    if isinstance(date_of_joining, str):
        try:
            date_of_joining = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
        except ValueError:
            date_of_joining = None
    date_of_joining = st.date_input("Date of Joining", value=date_of_joining)
    
    month_year = st.text_input("Month-Year (MM-YYYY)", value=st.session_state.employee_data.get('month_year', ''))
    pan_card = st.text_input("PAN Card", value=st.session_state.employee_data.get('pan_card', ''))

    # Salary input method selection
    salary_input_method = st.radio("Salary Input Method", ["Component-wise", "Total Salary"])

    if salary_input_method == "Component-wise":
        # Salary components
        basic_pay = st.number_input("Basic Pay", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('basic_pay', 0.0))
        hra = st.number_input("HRA", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('hra', 0.0))
        lta = st.number_input("LTA", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('lta', 0.0))
        other_allowance = st.number_input("Other Allowance", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('other_allowance', 0.0))
        
        total_addition = basic_pay + hra + lta + other_allowance
    else:
        # Total salary input
        total_salary = st.number_input("Total Salary", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('total_addition', 0.0))
        basic_pay, hra, lta, other_allowance = distribute_salary(total_salary)
        total_addition = total_salary

    st.number_input("Total Addition", min_value=0.0, step=0.01, value=total_addition, disabled=True)

    # Display individual components
    st.write(f"Basic Pay: {basic_pay:.2f}")
    st.write(f"HRA: {hra:.2f}")
    st.write(f"LTA: {lta:.2f}")
    st.write(f"Other Allowance: {other_allowance:.2f}")

    # Deductions
    provident_fund = st.number_input("Provident Fund", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('provident_fund', 0.0))
    esi = st.number_input("ESI", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('esi', 0.0))
    professional_tax = st.number_input("Professional Tax", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('professional_tax', 0.0))
    tax = st.number_input("Tax", min_value=0.0, step=0.01, value=st.session_state.employee_data.get('tax', 0.0))
    
    total_deductions = provident_fund + esi + professional_tax + tax
    st.number_input("Total Deductions", min_value=0.0, step=0.01, value=total_deductions, disabled=True)

    if month_year:
        try:
            month, year = map(int, month_year.split('-'))
            total_days_in_month = calendar.monthrange(year, month)[1]
            days_worked = st.number_input("Days Worked", min_value=0, max_value=total_days_in_month, step=1, value=min(st.session_state.employee_data.get('days_worked', 0), total_days_in_month))
        except ValueError:
            st.error("Invalid Month-Year format. Please use MM-YYYY.")
            days_worked = st.number_input("Days Worked", min_value=0, max_value=31, step=1, value=st.session_state.employee_data.get('days_worked', 0))
    else:
        days_worked = st.number_input("Days Worked", min_value=0, max_value=31, step=1, value=st.session_state.employee_data.get('days_worked', 0))

    # Calculate net salary
    if month_year and total_addition > 0 and days_worked > 0:
        net_salary = calculate_net_salary(total_addition, month_year, days_worked, total_deductions)
        st.number_input("Net Salary", min_value=0.0, step=0.01, value=net_salary, disabled=True)
    else:
        st.warning("Please enter valid Month-Year, Total Addition, and Days Worked to calculate Net Salary.")
        net_salary = 0

    if net_salary > 0:
        salary_in_words = number_to_words(net_salary)
        st.write(f"Salary in words: {salary_in_words}")

    if st.button("Save"):
        if not month_year or not employee_id or not employee_name:
            st.error("Please fill in all required fields (Month-Year, Employee ID, Name).")
        else:
            try:
                existing_employee = session.query(Employee).filter_by(employee_id=employee_id).one_or_none()
                if existing_employee:
                    existing_employee.designation = designation
                    existing_employee.employee_name = employee_name
                    existing_employee.date_of_joining = date_of_joining
                    existing_employee.month_year = month_year
                    existing_employee.pan_card = pan_card
                    existing_employee.basic_pay = basic_pay
                    existing_employee.hra = hra
                    existing_employee.lta = lta
                    existing_employee.other_allowance = other_allowance
                    existing_employee.total_addition = total_addition
                    existing_employee.provident_fund = provident_fund
                    existing_employee.esi = esi
                    existing_employee.professional_tax = professional_tax
                    existing_employee.tax = tax
                    existing_employee.total_deductions = total_deductions
                    existing_employee.days_worked = days_worked
                    existing_employee.net_salary = net_salary
                    existing_employee.salary_in_words = number_to_words(net_salary)
                    session.commit()
                    st.success("Employee record updated successfully.")
                else:
                    new_employee = Employee(
                        employee_id=employee_id,
                        designation=designation,
                        employee_name=employee_name,
                        date_of_joining=date_of_joining,
                        month_year=month_year,
                        pan_card=pan_card,
                        basic_pay=basic_pay,
                        hra=hra,
                        lta=lta,
                        other_allowance=other_allowance,
                        total_addition=total_addition,
                        provident_fund=provident_fund,
                        esi=esi,
                        professional_tax=professional_tax,
                        tax=tax,
                        total_deductions=total_deductions,
                        days_worked=days_worked,
                        net_salary=net_salary,
                        salary_in_words=number_to_words(net_salary)

                    )
                    session.add(new_employee)
                    session.commit()
                    st.success("New employee record added successfully.")
            except IntegrityError:
                session.rollback()
                st.error("An error occurred: Duplicate record.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.button("Generate Payslip"):
        try:
            search_id = st.session_state.employee_data.get('employee_id', '')
            employee = session.query(Employee).filter_by(employee_id=search_id).one()

            # Generate the payslip PDF
            download_html = generate_exact_payslip_pdf(employee)

            # Display the download link for the PDF
            st.markdown(download_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred while generating the payslip: {str(e)}")

if __name__ == "__main__":
    main()