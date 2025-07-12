import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import pandas as pd
from datetime import datetime, timedelta
import os
from tkcalendar import Calendar  # You may need to install this: pip install tkcalendar

class Student:
    def __init__(self, name, roll_no, phone):
        self.name = name
        self.roll_no = roll_no
        self.phone = phone
        self.attendance = []  # List of attendance records (True/False)
        self.present_today = False

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Create students
        self.students = self.generate_students()
        
        # Generate fake attendance data
        self.generate_attendance_data()
        
        # Create random seating arrangement
        self.seating = []
        for i in range(4):  # 4 rows
            row = []
            for j in range(4):  # 4 columns
                bench = [None, None]  # 2 students per bench
                row.append(bench)
            self.seating.append(row)
            
        # Assign seats
        student_list = list(self.students.values())
        random.shuffle(student_list)
        
        student_idx = 0
        for i in range(4):
            for j in range(4):
                for k in range(2):
                    if student_idx < len(student_list):
                        self.seating[i][j][k] = student_list[student_idx]
                        student_idx += 1
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.root)
        
        # Tab 1: Seating arrangement
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text="Seating Arrangement")
        
        # Tab 2: List view for attendance
        self.tab2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab2, text="Attendance List")
        
        # Tab 3: Student details
        self.tab3 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab3, text="Student Details")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Current date
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create widgets for Tab 1
        self.create_tab1()
        
        # Create widgets for Tab 2 (Attendance List)
        self.create_tab2()
        
        # Create widgets for Tab 3 (Student Details)
        self.create_tab3()
    
    def generate_students(self):
        # Indian first names
        first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Shaurya", 
            "Dhruv", "Krishna", "Ishaan", "Advait", "Kabir", "Ananya", "Anika", "Diya", 
            "Myra", "Sara", "Pari", "Nisha", "Riya", "Aarohi", "Aanya", "Siya", "Navya"
        ]
        
        # Indian last names
        last_names = [
            "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Rao", 
            "Malhotra", "Chopra", "Reddy", "Nair", "Agarwal", "Mukherjee", "Iyer", 
            "Banerjee", "Chatterjee", "Kapoor", "Shah", "Das", "Mehta", "Chauhan"
        ]
        
        students = {}
        
        # Generate 32 students (4 rows * 4 columns * 2 students)
        for i in range(1, 33):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            roll_no = f"R{i:03d}"
            
            # Generate a random 10-digit phone number
            phone = "9" + "".join([str(random.randint(0, 9)) for _ in range(9)])
            
            students[roll_no] = Student(name, roll_no, phone)
        
        return students
    
    def generate_attendance_data(self):
        # Generate fake attendance data for 63 days
        today = datetime.now()
        
        for student in self.students.values():
            for i in range(63):
                day = today - timedelta(days=63-i)
                
                # About 85% attendance on average
                is_present = random.random() < 0.85
                student.attendance.append(is_present)
    
    def create_tab1(self):
        # Header frame
        header_frame = ttk.Frame(self.tab1)
        header_frame.pack(fill="x", pady=10)
        
        # Date label and selection
        ttk.Label(header_frame, text="Date:").pack(side="left", padx=10)
        
        # Date selection with calendar
        self.date_var = tk.StringVar(value=self.current_date)
        self.date_entry = ttk.Entry(header_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side="left", padx=5)
        
        # Calendar button
        cal_button = ttk.Button(header_frame, text="📅", width=3, command=self.show_calendar)
        cal_button.pack(side="left", padx=5)
        
        # Save button
        save_button = ttk.Button(header_frame, text="Save Attendance", command=self.save_attendance)
        save_button.pack(side="right", padx=10)
        
        # Download button
        download_button = ttk.Button(header_frame, text="Download Excel", command=self.download_excel)
        download_button.pack(side="right", padx=10)
        
        # Reset button
        reset_button = ttk.Button(header_frame, text="Reset Attendance", command=self.reset_attendance)
        reset_button.pack(side="right", padx=10)
        
        # Create seating arrangement frame
        seating_frame = ttk.Frame(self.tab1)
        seating_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create grid
        self.seat_buttons = []
        for i in range(4):  # rows
            row_buttons = []
            for j in range(4):  # columns
                bench_frame = ttk.Frame(seating_frame, borderwidth=2, relief="raised")
                bench_frame.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")
                
                bench_buttons = []
                for k in range(2):  # students per bench
                    student = self.seating[i][j][k]
                    if student:
                        button = tk.Button(
                            bench_frame,
                            text=f"{student.name}\n{student.roll_no}",
                            width=20,
                            height=3,
                            bg="white",
                            command=lambda r=i, c=j, s=k: self.toggle_attendance(r, c, s)
                        )
                        button.pack(fill="both", expand=True, padx=2, pady=2)
                        bench_buttons.append(button)
                    else:
                        # Empty seat
                        empty = tk.Label(bench_frame, text="Empty Seat", width=20, height=3, bg="gray")
                        empty.pack(fill="both", expand=True, padx=2, pady=2)
                        bench_buttons.append(None)
                
                row_buttons.append(bench_buttons)
            self.seat_buttons.append(row_buttons)
        
        # Configure grid weights
        for i in range(4):
            seating_frame.grid_rowconfigure(i, weight=1)
            seating_frame.grid_columnconfigure(i, weight=1)
    
    def create_tab2(self):
        # Create a frame for header
        header_frame = ttk.Frame(self.tab2)
        header_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(header_frame, text="Date:").pack(side="left", padx=5)
        self.list_date_var = tk.StringVar(value=self.current_date)
        self.list_date_entry = ttk.Entry(header_frame, textvariable=self.list_date_var, width=12)
        self.list_date_entry.pack(side="left", padx=5)
        
        # Calendar button for list view
        list_cal_button = ttk.Button(header_frame, text="📅", width=3, command=self.show_list_calendar)
        list_cal_button.pack(side="left", padx=5)
        
        # Create a frame for search
        search_frame = ttk.Frame(self.tab2)
        search_frame.pack(fill="x", pady=5, padx=10)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        self.list_search_var = tk.StringVar()
        list_search_entry = ttk.Entry(search_frame, textvariable=self.list_search_var)
        list_search_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        list_search_button = ttk.Button(search_frame, text="Search", command=self.search_attendance_list)
        list_search_button.pack(side="left", padx=5)
        
        # Mark all buttons
        mark_frame = ttk.Frame(self.tab2)
        mark_frame.pack(fill="x", pady=5, padx=10)
        
        mark_all_present = ttk.Button(mark_frame, text="Mark All Present", command=self.mark_all_present)
        mark_all_present.pack(side="left", padx=5)
        
        mark_all_absent = ttk.Button(mark_frame, text="Mark All Absent", command=self.mark_all_absent)
        mark_all_absent.pack(side="left", padx=5)
        
        save_button = ttk.Button(mark_frame, text="Save Attendance", command=self.save_attendance)
        save_button.pack(side="right", padx=5)
        
        # Create a treeview for attendance list
        list_frame = ttk.Frame(self.tab2)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.attendance_tree = ttk.Treeview(list_frame, columns=("Roll No", "Name", "Status"))
        self.attendance_tree.heading("#0", text="")
        self.attendance_tree.heading("Roll No", text="Roll No")
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Status", text="Status")
        
        self.attendance_tree.column("#0", width=0, stretch=tk.NO)
        self.attendance_tree.column("Roll No", width=100, anchor=tk.CENTER)
        self.attendance_tree.column("Name", width=200)
        self.attendance_tree.column("Status", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.attendance_tree.yview)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self.attendance_tree.pack(fill="both", expand=True)
        
        # Populate the attendance list
        self.update_attendance_list()
        
        # Bind double click event for toggling attendance
        self.attendance_tree.bind("<Double-1>", self.toggle_attendance_from_list)
        
    def create_tab3(self):
        # Create a frame for search
        search_frame = ttk.Frame(self.tab3)
        search_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Label(search_frame, text="Search by Roll No or Name:").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_student)
        search_button.pack(side="left", padx=5)
        
        # Create a treeview for student list
        list_frame = ttk.Frame(self.tab3)
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.student_tree = ttk.Treeview(list_frame, columns=("Roll No", "Name", "Phone", "Attendance"))
        self.student_tree.heading("#0", text="")
        self.student_tree.heading("Roll No", text="Roll No")
        self.student_tree.heading("Name", text="Name")
        self.student_tree.heading("Phone", text="Phone")
        self.student_tree.heading("Attendance", text="Attendance %")
        
        self.student_tree.column("#0", width=0, stretch=tk.NO)
        self.student_tree.column("Roll No", width=80, anchor=tk.CENTER)
        self.student_tree.column("Name", width=150)
        self.student_tree.column("Phone", width=100, anchor=tk.CENTER)
        self.student_tree.column("Attendance", width=100, anchor=tk.CENTER)
        
        self.student_tree.pack(fill="both", expand=True)
        
        # Populate the treeview
        self.update_student_list()
        
        # Bind select event
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)
        
        # Create a frame for student details
        details_frame = ttk.LabelFrame(self.tab3, text="Student Details")
        details_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Student details
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.detail_name = ttk.Label(details_frame, text="")
        self.detail_name.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Roll No:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.detail_roll = ttk.Label(details_frame, text="")
        self.detail_roll.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Phone:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.detail_phone = ttk.Label(details_frame, text="")
        self.detail_phone.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Total Attendance:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.detail_attendance = ttk.Label(details_frame, text="")
        self.detail_attendance.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Days Present:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.detail_days = ttk.Label(details_frame, text="")
        self.detail_days.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Attendance record (last 10 days)
        ttk.Label(details_frame, text="Recent Attendance:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        
        self.attendance_frame = ttk.Frame(details_frame)
        self.attendance_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights for details_frame
        details_frame.grid_columnconfigure(1, weight=1)
    
    def toggle_attendance(self, row, col, seat):
        student = self.seating[row][col][seat]
        if student:
            student.present_today = not student.present_today
            
            # Update button color
            button = self.seat_buttons[row][col][seat]
            if student.present_today:
                button.config(bg="light green")
            else:
                button.config(bg="white")
            
            # Update the attendance list view if it exists
            self.update_attendance_list()
    
    def save_attendance(self):
        # Save current attendance to the records
        for student in self.students.values():
            if len(student.attendance) >= 63:
                # Replace the oldest attendance record
                student.attendance.pop(0)
            
            student.attendance.append(student.present_today)
        
        # Update the student list in Tab 3
        self.update_student_list()
        
        # Update the attendance list in Tab 2
        self.update_attendance_list()
        
        messagebox.showinfo("Success", "Attendance has been saved successfully!")
    
    def reset_attendance(self):
        # Reset today's attendance
        for student in self.students.values():
            student.present_today = False
        
        # Reset button colors
        for i in range(4):
            for j in range(4):
                for k in range(2):
                    if self.seat_buttons[i][j][k]:
                        self.seat_buttons[i][j][k].config(bg="white")
        
        # Update the attendance list
        self.update_attendance_list()
        
        messagebox.showinfo("Reset", "Today's attendance has been reset!")
    
    def update_student_list(self):
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Add students to the list
        for student in self.students.values():
            present_days = sum(student.attendance)
            attendance_percent = round(present_days / len(student.attendance) * 100, 2)
            
            self.student_tree.insert("", "end", values=(
                student.roll_no,
                student.name,
                student.phone,
                f"{attendance_percent}% ({present_days}/{len(student.attendance)})"
            ))
    
    def on_student_select(self, event):
        selected_items = self.student_tree.selection()
        if selected_items:
            item = selected_items[0]
            roll_no = self.student_tree.item(item, "values")[0]
            student = self.students.get(roll_no)
            
            if student:
                # Update details
                self.detail_name.config(text=student.name)
                self.detail_roll.config(text=student.roll_no)
                self.detail_phone.config(text=student.phone)
                
                present_days = sum(student.attendance)
                total_days = len(student.attendance)
                attendance_percent = round(present_days / total_days * 100, 2)
                
                self.detail_attendance.config(text=f"{attendance_percent}%")
                self.detail_days.config(text=f"{present_days} out of {total_days}")
                
                # Clear attendance frame
                for widget in self.attendance_frame.winfo_children():
                    widget.destroy()
                
                # Show last 10 days attendance
                today = datetime.now()
                for i in range(min(10, len(student.attendance))):
                    day_idx = len(student.attendance) - 1 - i
                    day = today - timedelta(days=i)
                    day_str = day.strftime("%Y-%m-%d")
                    
                    status = "Present" if student.attendance[day_idx] else "Absent"
                    color = "green" if student.attendance[day_idx] else "red"
                    
                    frame = ttk.Frame(self.attendance_frame)
                    frame.pack(fill="x", pady=2)
                    
                    ttk.Label(frame, text=day_str).pack(side="left", padx=5)
                    ttk.Label(frame, text=status, foreground=color).pack(side="right", padx=5)
    
    def search_student(self):
        query = self.search_var.get().lower()
        if not query:
            self.update_student_list()
            return
        
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Add matching students to the list
        for student in self.students.values():
            if query in student.name.lower() or query in student.roll_no.lower():
                present_days = sum(student.attendance)
                attendance_percent = round(present_days / len(student.attendance) * 100, 2)
                
                self.student_tree.insert("", "end", values=(
                    student.roll_no,
                    student.name,
                    student.phone,
                    f"{attendance_percent}% ({present_days}/{len(student.attendance)})"
                ))
    
    def search_attendance_list(self):
        query = self.list_search_var.get().lower()
        if not query:
            self.update_attendance_list()
            return
        
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Add matching students to the list
        for student in self.students.values():
            if query in student.name.lower() or query in student.roll_no.lower():
                status = "Present" if student.present_today else "Absent"
                
                self.attendance_tree.insert("", "end", values=(
                    student.roll_no,
                    student.name,
                    status
                ))
    
    def download_excel(self):
        # Create a DataFrame with attendance data
        data = []
        for student in self.students.values():
            present_days = sum(student.attendance)
            attendance_percent = round(present_days / len(student.attendance) * 100, 2)
            
            row = {
                "Roll No": student.roll_no,
                "Name": student.name,
                "Phone": student.phone,
                "Days Present": present_days,
                "Total Days": len(student.attendance),
                "Attendance %": attendance_percent
            }
            
            # Add individual day attendance
            today = datetime.now()
            for i in range(len(student.attendance)):
                day = today - timedelta(days=len(student.attendance)-1-i)
                day_str = day.strftime("%Y-%m-%d")
                row[day_str] = "Present" if student.attendance[i] else "Absent"
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Attendance Report"
        )
        
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Attendance data has been saved to {file_path}")

    def show_calendar(self):
        # Create a top-level window for the calendar
        top = tk.Toplevel(self.root)
        top.title("Select Date")
        top.geometry("300x250")
        top.resizable(False, False)
        
        # Create a calendar
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Function to set the date
        def set_date():
            selected_date = cal.get_date()
            self.date_var.set(selected_date)
            self.list_date_var.set(selected_date)  # Keep both date fields in sync
            top.destroy()
        
        # Add a button to select the date
        select_button = ttk.Button(top, text="Select", command=set_date)
        select_button.pack(pady=10)
    
    def show_list_calendar(self):
        # Create a top-level window for the calendar
        top = tk.Toplevel(self.root)
        top.title("Select Date")
        top.geometry("300x250")
        top.resizable(False, False)
        
        # Create a calendar
        cal = Calendar(top, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Function to set the date
        def set_date():
            selected_date = cal.get_date()
            self.list_date_var.set(selected_date)
            self.date_var.set(selected_date)  # Keep both date fields in sync
            top.destroy()
        
        # Add a button to select the date
        select_button = ttk.Button(top, text="Select", command=set_date)
        select_button.pack(pady=10)
    
    def update_attendance_list(self):
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Add students to the list
        for student in self.students.values():
            status = "Present" if student.present_today else "Absent"
            
            item = self.attendance_tree.insert("", "end", values=(
                student.roll_no,
                student.name,
                status
            ))
            
            # Set row color based on status
            if student.present_today:
                self.attendance_tree.item(item, tags=("present",))
            else:
                self.attendance_tree.item(item, tags=("absent",))
        
        # Configure tags
        self.attendance_tree.tag_configure("present", background="light green")
        self.attendance_tree.tag_configure("absent", background="white")
    
    def toggle_attendance_from_list(self, event):
        # Get the selected item
        selected_items = self.attendance_tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.attendance_tree.item(item, "values")
            roll_no = values[0]
            
            student = self.students.get(roll_no)
            if student:
                # Toggle attendance
                student.present_today = not student.present_today
                
                # Update the attendance tree
                status = "Present" if student.present_today else "Absent"
                self.attendance_tree.item(item, values=(
                    student.roll_no,
                    student.name,
                    status
                ))
                
                # Update the tag
                if student.present_today:
                    self.attendance_tree.item(item, tags=("present",))
                else:
                    self.attendance_tree.item(item, tags=("absent",))
                
                # Update seating arrangement
                self.update_seat_colors()
    
    def update_seat_colors(self):
        # Update seat colors based on attendance
        for i in range(4):
            for j in range(4):
                for k in range(2):
                    if self.seat_buttons[i][j][k]:
                        student = self.seating[i][j][k]
                        if student and student.present_today:
                            self.seat_buttons[i][j][k].config(bg="light green")
                        else:
                            self.seat_buttons[i][j][k].config(bg="white")
    
    def mark_all_present(self):
        # Mark all students as present
        for student in self.students.values():
            student.present_today = True
        
        # Update both views
        self.update_attendance_list()
        self.update_seat_colors()
    
    def mark_all_absent(self):
        # Mark all students as absent
        for student in self.students.values():
            student.present_today = False
        
        # Update both views
        self.update_attendance_list()
        self.update_seat_colors()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystem(root)
    root.mainloop()