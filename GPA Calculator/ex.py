import pandas as pd
import numpy as np
import random
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# Define subject names
subject_names = ["Mathematics", "Physics", "Computer Science", "English", "Data Structures", "Algorithms"]

# Define credit hours for each subject
credits = [4, 3, 4, 2, 4, 3]

# Define possible grades (Indian system)
grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']

# Probability weights to make higher grades somewhat more likely
weights = [0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.05, 0.05]

# Grade point values (Indian 10-point system)
grade_values = {
    'O': 10.0,    # Outstanding
    'A+': 9.0,    # Excellent
    'A': 8.0,     # Very Good
    'B+': 7.0,    # Good
    'B': 6.0,     # Above Average
    'C': 5.0,     # Average
    'P': 4.0,     # Pass
    'F': 0.0      # Fail
}

# Function to calculate CGPA (Indian system)
def calculate_cgpa(student_grades, credits):
    total_credit_points = 0
    total_credits = sum(credits)
    
    for i, grade in enumerate(student_grades):
        grade_point = grade_values.get(grade, 0)
        credit = credits[i]
        total_credit_points += grade_point * credit
    
    return round(total_credit_points / total_credits, 2)

# Generate fake data for 52 students
data = []

for i in range(1, 53):
    # Create a roll number (format: CSE2023XXX)
    roll_number = f"CSE2023{i:03d}"
    
    # Generate a random name (Indian names)
    first_names = ["Rahul", "Priya", "Amit", "Neha", "Sachin", "Ananya", "Vikram", "Pooja", 
                  "Rohit", "Deepika", "Rajesh", "Kavita", "Vijay", "Sneha", "Arjun", "Meera",
                  "Aditya", "Nisha", "Vivek", "Simran", "Ravi", "Anjali", "Sanjay", "Isha",
                  "Nikhil", "Divya", "Kunal", "Trisha", "Varun", "Kritika"]
    last_names = ["Sharma", "Patel", "Singh", "Gupta", "Kumar", "Reddy", "Joshi", "Das",
                 "Verma", "Rao", "Mehta", "Nair", "Iyer", "Kapoor", "Malhotra", "Malik",
                 "Banerjee", "Roy", "Chatterjee", "Mukherjee", "Shah", "Goel", "Chauhan",
                 "Agarwal", "Mishra", "Desai", "Menon", "Pillai", "Patil", "Choudhary"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Generate random grades for each subject
    student_grades = random.choices(grades, weights=weights, k=len(subject_names))
    
    # Calculate CGPA
    cgpa = calculate_cgpa(student_grades, credits)
    
    # Create student record
    student = {'Roll Number': roll_number, 'Name': name}
    
    # Add grades for each subject
    for j, subject in enumerate(subject_names):
        student[subject] = student_grades[j]
    
    # Add CGPA
    student['CGPA'] = cgpa
    
    data.append(student)

# Create DataFrame
df = pd.DataFrame(data)

# Create Excel file
wb = Workbook()
ws = wb.active
ws.title = "Student Grades"

# Add headers
headers = ['Roll Number', 'Name'] + subject_names + ['CGPA']
ws.append(headers)

# Add credit row
credit_row = ['Credits', ''] + credits + ['']
ws.append(credit_row)

# Add student data
for _, student in df.iterrows():
    row = [student['Roll Number'], student['Name']]
    
    for subject in subject_names:
        row.append(student[subject])
    
    row.append(student['CGPA'])
    ws.append(row)

# Save the file
wb.save("student_grades_indian_sample.xlsx")

print("Sample Excel file 'student_grades_indian_sample.xlsx' created successfully with 52 student records using the Indian 10-point CGPA system.")