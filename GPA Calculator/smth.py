import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import random

class CGPACalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("College CGPA Calculator (Indian 10-Point System)")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Default values
        self.num_subjects = 6
        self.credits = [3] * self.num_subjects
        self.subject_names = [f"Subject {i+1}" for i in range(self.num_subjects)]
        
        # Data storage
        self.student_data = pd.DataFrame(columns=['Roll Number', 'Name'] + self.subject_names + ['CGPA'])
        self.excel_file_path = "student_grades.xlsx"
        
        # Initialize the notebook (tab control)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create the three tabs
        self.setup_tab()
        self.input_tab()
        self.visualization_tab()
        
        # Load existing data if file exists
        if os.path.exists(self.excel_file_path):
            try:
                self.load_data(self.excel_file_path)
                messagebox.showinfo("Data Loaded", f"Existing data loaded from {self.excel_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load existing data: {str(e)}")
    
    def setup_tab(self):
        """Create the setup tab for configuring subjects and credits"""
        setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(setup_frame, text="Setup")
        
        # Number of subjects selection
        ttk.Label(setup_frame, text="Number of Subjects:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.subject_var = tk.StringVar(value=str(self.num_subjects))
        subject_combo = ttk.Combobox(setup_frame, textvariable=self.subject_var, values=["4", "5", "6", "7"], state="readonly", width=5)
        subject_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        subject_combo.bind("<<ComboboxSelected>>", self.update_subject_count)
        
        # Frame for subjects and credits
        self.subjects_frame = ttk.LabelFrame(setup_frame, text="Subject Configuration")
        self.subjects_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Create subject name and credit entries
        self.subject_entries = []
        self.credit_entries = []
        
        for i in range(self.num_subjects):
            ttk.Label(self.subjects_frame, text=f"Subject {i+1} Name:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            subject_entry = ttk.Entry(self.subjects_frame, width=30)
            subject_entry.insert(0, self.subject_names[i])
            subject_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
            ttk.Label(self.subjects_frame, text="Credit:").grid(row=i, column=2, padx=10, pady=5, sticky="w")
            credit_entry = ttk.Entry(self.subjects_frame, width=5)
            credit_entry.insert(0, str(self.credits[i]))
            credit_entry.grid(row=i, column=3, padx=10, pady=5, sticky="w")
            
            self.subject_entries.append(subject_entry)
            self.credit_entries.append(credit_entry)
        
        # Save configuration button
        save_btn = ttk.Button(setup_frame, text="Save Configuration", command=self.save_configuration)
        save_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        # Generate sample data button
        sample_btn = ttk.Button(setup_frame, text="Generate Sample Data", command=self.generate_sample_data)
        sample_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    def update_subject_count(self, event=None):
        """Update the number of subject entries when the count changes"""
        try:
            new_count = int(self.subject_var.get())
            if new_count == self.num_subjects:
                return
                
            # Clear existing entries
            for entry in self.subject_entries + self.credit_entries:
                entry.destroy()
            
            # Reset lists
            self.subject_entries = []
            self.credit_entries = []
            
            # Extend or shrink subject names and credits lists
            if new_count > self.num_subjects:
                self.subject_names.extend([f"Subject {i+1}" for i in range(self.num_subjects, new_count)])
                self.credits.extend([3] * (new_count - self.num_subjects))
            else:
                self.subject_names = self.subject_names[:new_count]
                self.credits = self.credits[:new_count]
            
            self.num_subjects = new_count
            
            # Create new entries
            for i in range(self.num_subjects):
                ttk.Label(self.subjects_frame, text=f"Subject {i+1} Name:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
                subject_entry = ttk.Entry(self.subjects_frame, width=30)
                subject_entry.insert(0, self.subject_names[i])
                subject_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
                
                ttk.Label(self.subjects_frame, text="Credit:").grid(row=i, column=2, padx=10, pady=5, sticky="w")
                credit_entry = ttk.Entry(self.subjects_frame, width=5)
                credit_entry.insert(0, str(self.credits[i]))
                credit_entry.grid(row=i, column=3, padx=10, pady=5, sticky="w")
                
                self.subject_entries.append(subject_entry)
                self.credit_entries.append(credit_entry)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error updating subject count: {str(e)}")
    
    def save_configuration(self):
        """Save the subject names and credits configuration"""
        try:
            # Update subject names
            for i in range(self.num_subjects):
                self.subject_names[i] = self.subject_entries[i].get()
                self.credits[i] = float(self.credit_entries[i].get())
            
            # Update DataFrame columns
            new_columns = ['Roll Number', 'Name'] + self.subject_names + ['CGPA']
            
            # Create new DataFrame with updated columns
            if not self.student_data.empty:
                # Save data for roll numbers and names
                roll_and_name = self.student_data[['Roll Number', 'Name']].copy()
                
                # Create new DataFrame with same index
                self.student_data = pd.DataFrame(index=self.student_data.index, columns=new_columns)
                
                # Restore roll numbers and names
                self.student_data[['Roll Number', 'Name']] = roll_and_name
            else:
                self.student_data = pd.DataFrame(columns=new_columns)
            
            # Recreate the input tab to reflect new subjects
            for child in self.input_frame.winfo_children():
                child.destroy()
            
            self.setup_input_widgets()
            
            # Update the visualization tab
            self.update_visualization()
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {str(e)}")
    
    def input_tab(self):
        """Create the input tab for entering student data"""
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Student Data Input")
        
        self.setup_input_widgets()
    
    def setup_input_widgets(self):
        """Set up the input widgets based on current configuration"""
        # Student info section
        info_frame = ttk.LabelFrame(self.input_frame, text="Student Information")
        info_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        ttk.Label(info_frame, text="Roll Number:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.roll_entry = ttk.Entry(info_frame, width=15)
        self.roll_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.name_entry = ttk.Entry(info_frame, width=30)
        self.name_entry.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # Grades section
        grades_frame = ttk.LabelFrame(self.input_frame, text="Subject Grades")
        grades_frame.pack(fill="x", padx=10, pady=10, expand=False)
        
        # Create grade entries for each subject
        self.grade_entries = []
        
        for i in range(self.num_subjects):
            ttk.Label(grades_frame, text=f"{self.subject_names[i]} (Credits: {self.credits[i]}):").grid(
                row=i, column=0, padx=10, pady=5, sticky="w")
            
            # Indian grading system: O, A+, A, B+, B, C, P, F
            grade_entry = ttk.Combobox(grades_frame, values=["O", "A+", "A", "B+", "B", "C", "P", "F"], width=5)
            grade_entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.grade_entries.append(grade_entry)
            
            # Bind event to update in real-time when grade is changed
            grade_entry.bind("<<ComboboxSelected>>", self.update_grade_realtime)
        
        # Buttons frame
        btn_frame = ttk.Frame(self.input_frame)
        btn_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Button(btn_frame, text="Add Student", command=self.add_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Student", command=self.update_current_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save to Excel", command=self.save_to_excel).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Import from Excel", command=self.import_from_excel).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Auto-Save Changes", command=self.toggle_autosave).pack(side="left", padx=5)
        
        # Initialize auto-save flag
        self.auto_save = False
        
        # Data view section with search functionality
        view_frame = ttk.LabelFrame(self.input_frame, text="Student Records")
        view_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        # Add search functionality
        search_frame = ttk.Frame(view_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search by Name:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_student)
        
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).pack(side="left", padx=5)
        
        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(view_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Treeview for student data
        self.tree = ttk.Treeview(tree_frame)
        self.tree["columns"] = tuple(['Roll Number', 'Name'] + self.subject_names + ['CGPA'])
        
        # Configure columns
        self.tree.column("#0", width=0, stretch=False)
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center")
            self.tree.heading(col, text=col)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.load_selected_student)
        
        # Add delete button
        delete_btn = ttk.Button(view_frame, text="Delete Selected", command=self.delete_selected)
        delete_btn.pack(side="bottom", pady=5)
        
        # Add status bar to show auto-save status
        self.status_var = tk.StringVar()
        self.status_var.set("Auto-Save: OFF")
        status_bar = ttk.Label(view_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side="bottom", fill="x", padx=5, pady=2)
        
        # Populate the tree with existing data
        self.update_treeview()

    def toggle_autosave(self):
        """Toggle auto-save mode for grade changes"""
        self.auto_save = not self.auto_save
        self.status_var.set(f"Auto-Save: {'ON' if self.auto_save else 'OFF'}")
        
        message = "Auto-Save is now ON. Changes will be automatically saved to Excel." if self.auto_save else "Auto-Save is now OFF. You need to click 'Save to Excel' to save changes."
        messagebox.showinfo("Auto-Save", message)
    
    def update_grade_realtime(self, event=None):
        """Update grade in real-time as it's changed"""
        # Check if a student is currently selected
        if not self.roll_entry.get().strip():
            return
        
        # If auto-save is on, update the student record immediately
        if hasattr(self, 'auto_save') and self.auto_save:
            self.update_current_student()
            self.save_to_excel()
        else:
            # Just update the student record without saving to Excel
            self.update_current_student()

    def update_current_student(self):
        """Update the currently selected student's record"""
        try:
            roll = self.roll_entry.get().strip()
            name = self.name_entry.get().strip()
            
            if not roll or not name:
                messagebox.showerror("Error", "Roll Number and Name are required!")
                return
            
            # Gather grades
            grades = {}
            for i, entry in enumerate(self.grade_entries):
                grades[self.subject_names[i]] = entry.get()
            
            # Calculate CGPA
            cgpa = self.calculate_cgpa(grades)
            
            # Check if this roll number exists
            if roll in self.student_data['Roll Number'].values:
                # Update existing record
                idx = self.student_data[self.student_data['Roll Number'] == roll].index[0]
                self.student_data.at[idx, 'Name'] = name
                for subject, grade in grades.items():
                    self.student_data.at[idx, subject] = grade
                self.student_data.at[idx, 'CGPA'] = cgpa
                
                # Update UI
                self.update_treeview()
                self.update_visualization()
                
                # Select the updated student in the treeview
                for item in self.tree.get_children():
                    if self.tree.item(item, 'values')[0] == roll:
                        self.tree.selection_set(item)
                        self.tree.see(item)
                        break
                
                return True
            else:
                messagebox.showinfo("Info", "No existing record found with this Roll Number. Use 'Add Student' to create a new record.")
                return False
        
        except Exception as e:
            messagebox.showerror("Error", f"Error updating student: {str(e)}")
            return False
    
    def add_student(self):
        """Add or update a student record"""
        try:
            roll = self.roll_entry.get().strip()
            name = self.name_entry.get().strip()
            
            if not roll or not name:
                messagebox.showerror("Error", "Roll Number and Name are required!")
                return
            
            # Gather grades
            grades = {}
            for i, entry in enumerate(self.grade_entries):
                grades[self.subject_names[i]] = entry.get()
            
            # Calculate CGPA
            cgpa = self.calculate_cgpa(grades)
            
            # Check if this roll number already exists
            if roll in self.student_data['Roll Number'].values:
                # Update existing record
                idx = self.student_data[self.student_data['Roll Number'] == roll].index[0]
                self.student_data.at[idx, 'Name'] = name
                for subject, grade in grades.items():
                    self.student_data.at[idx, subject] = grade
                self.student_data.at[idx, 'CGPA'] = cgpa
                
                messagebox.showinfo("Success", f"Updated student record for {roll}")
            else:
                # Add new record
                new_record = {'Roll Number': roll, 'Name': name, 'CGPA': cgpa}
                new_record.update(grades)
                
                self.student_data = pd.concat([self.student_data, pd.DataFrame([new_record])], ignore_index=True)
                messagebox.showinfo("Success", f"Added new student: {roll}")
            
            # Update UI
            self.update_treeview()
            self.update_visualization()
            
            # Auto-save if enabled
            if hasattr(self, 'auto_save') and self.auto_save:
                self.save_to_excel()
            
            self.clear_form()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error adding student: {str(e)}")

    def save_to_excel(self):
        """Save student data to Excel file"""
        try:
            # If we already have a file path and it's not a new save operation, use it
            if self.excel_file_path and os.path.exists(self.excel_file_path):
                file_path = self.excel_file_path
            else:
                # Create new Excel file
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    initialfile=self.excel_file_path
                )
                
                if not file_path:
                    return
            
            # Create a Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Student Grades"
            
            # Add headers
            headers = ['Roll Number', 'Name'] + self.subject_names + ['CGPA']
            ws.append(headers)
            
            # Add credit row (for reference)
            credit_row = ['Credits', ''] + self.credits + ['']
            ws.append(credit_row)
            
            # Add student data
            for _, student in self.student_data.iterrows():
                row = [student['Roll Number'], student['Name']]
                
                for subject in self.subject_names:
                    row.append(student[subject] if pd.notna(student[subject]) else '')
                
                row.append(student['CGPA'])
                ws.append(row)
            
            # Save the file
            wb.save(file_path)
            self.excel_file_path = file_path
            
            # Only show message if not auto-saving
            if not (hasattr(self, 'auto_save') and self.auto_save):
                messagebox.showinfo("Success", f"Data saved to {file_path}")
            
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saving to Excel: {str(e)}")
            return False

    def search_student(self, event=None):
        """Search for students by name"""
        search_term = self.search_entry.get().lower().strip()
        
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # If search term is empty, show all students
        if not search_term:
            self.update_treeview()
            return
        
        # Filter students by name
        for _, student in self.student_data.iterrows():
            if search_term in student['Name'].lower():
                values = [student['Roll Number'], student['Name']]
                
                # Add subject grades
                for subject in self.subject_names:
                    values.append(student[subject] if pd.notna(student[subject]) else '')
                
                # Add CGPA
                values.append(student['CGPA'])
                
                self.tree.insert('', 'end', values=values)
    
    def clear_search(self):
        """Clear the search field and show all students"""
        self.search_entry.delete(0, 'end')
        self.update_treeview()

    def visualization_tab(self):
        """Create the visualization tab for displaying analytics"""
        vis_frame = ttk.Frame(self.notebook)
        self.notebook.add(vis_frame, text="Analytics & Visualization")
        
        # Control frame
        control_frame = ttk.Frame(vis_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(control_frame, text="Select Student:").pack(side="left", padx=5)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(control_frame, textvariable=self.student_var, state="readonly", width=30)
        self.student_combo.pack(side="left", padx=5)
        self.student_combo.bind("<<ComboboxSelected>>", self.update_student_visualization)
        
        # Create a frame for plots
        self.plot_frame = ttk.Frame(vis_frame)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize with empty plots
        self.update_visualization()
    
    def update_visualization(self):
        """Update all visualizations"""
        # Clear the plot frame
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        # Update student dropdown
        if not self.student_data.empty:
            students = [f"{row['Roll Number']} - {row['Name']}" for _, row in self.student_data.iterrows()]
            self.student_combo['values'] = students
            if students:
                self.student_combo.current(0)
        
        # Create plots based on available data
        if not self.student_data.empty:
            # Create figure with multiple subplots
            fig = plt.Figure(figsize=(12, 8), dpi=100)
            
            # Individual student performance plot
            self.update_student_visualization()
            
            # Class average plot
            self.plot_class_average(fig.add_subplot(212))
            
            # Add the figure to the frame
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            # Show message when no data available
            ttk.Label(self.plot_frame, text="No data available for visualization. Please add student records.").pack(pady=50)
    
    def update_student_visualization(self, event=None):
        """Update visualization for selected student"""
        # Clear existing visualization
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        if not self.student_data.empty and self.student_var.get():
            selected = self.student_var.get().split(" - ")[0]  # Get roll number
            
            # Find the student
            student = self.student_data[self.student_data['Roll Number'] == selected].iloc[0]
            
            # Create figure
            fig = plt.Figure(figsize=(12, 8), dpi=100)
            
            # Student grades chart
            ax1 = fig.add_subplot(211)
            self.plot_student_grades(ax1, student)
            
            # Class average
            ax2 = fig.add_subplot(212)
            self.plot_class_average(ax2)
            
            # Add the figure to the frame
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def plot_student_grades(self, ax, student):
        """Plot individual student grades"""
        # Grade values for plotting (Indian 10-point system)
        grade_values = {
            'O': 10.0,    # Outstanding
            'A+': 9.0,    # Excellent
            'A': 8.0,     # Very Good
            'B+': 7.0,    # Good
            'B': 6.0,     # Above Average
            'C': 5.0,     # Average
            'P': 4.0,     # Pass
            'F': 0.0,     # Fail
            '': 0.0,
            None: 0.0
        }
        
        # Get grades
        grades = [grade_values.get(student[subject], 0) for subject in self.subject_names]
        
        # Set title
        ax.set_title(f"Performance of {student['Name']} (CGPA: {student['CGPA']})")
        
        # Create bar chart
        bars = ax.bar(self.subject_names, grades)
        
        # Set labels
        ax.set_ylabel('Grade Points (0-10)')
        ax.set_ylim(0, 11)
        ax.set_yticks([0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ax.set_yticklabels(['F', 'P', 'C', 'B', 'B+', 'A', 'A+', 'O'])
        
        # Add value labels
        for bar, grade, subject in zip(bars, grades, self.subject_names):
            letter_grade = [k for k, v in grade_values.items() if v == grade and k != '']
            letter_grade = letter_grade[0] if letter_grade else 'N/A'
            ax.text(bar.get_x() + bar.get_width()/2, grade + 0.3, letter_grade, 
                    ha='center', va='bottom', fontweight='bold')
    
    def plot_class_average(self, ax):
        """Plot class average performance by subject"""
        # Grade values (Indian 10-point system)
        grade_values = {
            'O': 10.0,    # Outstanding
            'A+': 9.0,    # Excellent
            'A': 8.0,     # Very Good
            'B+': 7.0,    # Good
            'B': 6.0,     # Above Average
            'C': 5.0,     # Average
            'P': 4.0,     # Pass
            'F': 0.0,     # Fail
            '': 0.0,
            None: 0.0
        }
        
        # Calculate averages
        averages = []
        for subject in self.subject_names:
            # Convert letter grades to numeric, then calculate mean
            numeric_grades = [grade_values.get(grade, 0) for grade in self.student_data[subject] if grade]
            avg = sum(numeric_grades) / len(numeric_grades) if numeric_grades else 0
            averages.append(avg)
        
        # Create bar chart
        ax.set_title("Class Average Performance by Subject")
        bars = ax.bar(self.subject_names, averages, color='orange')
        
        # Set labels
        ax.set_ylabel('Average Grade Points (0-10)')
        ax.set_ylim(0, 11)
        ax.set_yticks([0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        ax.set_yticklabels(['F', 'P', 'C', 'B', 'B+', 'A', 'A+', 'O'])
        
        # Add value labels
        for bar, avg in zip(bars, averages):
            ax.text(bar.get_x() + bar.get_width()/2, avg + 0.2, f'{avg:.2f}', 
                    ha='center', va='bottom')
    
    def add_student(self):
        """Add or update a student record"""
        try:
            roll = self.roll_entry.get().strip()
            name = self.name_entry.get().strip()
            
            if not roll or not name:
                messagebox.showerror("Error", "Roll Number and Name are required!")
                return
            
            # Gather grades
            grades = {}
            for i, entry in enumerate(self.grade_entries):
                grades[self.subject_names[i]] = entry.get()
            
            # Calculate CGPA
            cgpa = self.calculate_cgpa(grades)
            
            # Check if this roll number already exists
            if roll in self.student_data['Roll Number'].values:
                # Update existing record
                idx = self.student_data[self.student_data['Roll Number'] == roll].index[0]
                self.student_data.at[idx, 'Name'] = name
                for subject, grade in grades.items():
                    self.student_data.at[idx, subject] = grade
                self.student_data.at[idx, 'CGPA'] = cgpa
                
                messagebox.showinfo("Success", f"Updated student record for {roll}")
            else:
                # Add new record
                new_record = {'Roll Number': roll, 'Name': name, 'CGPA': cgpa}
                new_record.update(grades)
                
                self.student_data = pd.concat([self.student_data, pd.DataFrame([new_record])], ignore_index=True)
                messagebox.showinfo("Success", f"Added new student: {roll}")
            
            # Update UI
            self.update_treeview()
            self.update_visualization()
            self.clear_form()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error adding student: {str(e)}")
    
    def calculate_cgpa(self, grades):
        """Calculate CGPA based on grades and credits (Indian 10-point system)"""
        # Grade values (Indian 10-point system)
        grade_values = {
            'O': 10.0,    # Outstanding
            'A+': 9.0,    # Excellent
            'A': 8.0,     # Very Good
            'B+': 7.0,    # Good
            'B': 6.0,     # Above Average
            'C': 5.0,     # Average
            'P': 4.0,     # Pass
            'F': 0.0,     # Fail
            '': 0.0,
            None: 0.0
        }
        
        total_credit_points = 0
        total_credits = 0
        
        for i, subject in enumerate(self.subject_names):
            grade = grades.get(subject, '')
            if grade:
                grade_point = grade_values.get(grade, 0)
                credit = self.credits[i]
                total_credit_points += grade_point * credit
                total_credits += credit
        
        if total_credits == 0:
            return 0
        
        return round(total_credit_points / total_credits, 2)
    
    def clear_form(self):
        """Clear the input form"""
        self.roll_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        
        for entry in self.grade_entries:
            entry.set('')
    
    def delete_selected(self):
        """Delete the selected student record"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showinfo("Info", "Please select a record to delete")
            return
        
        try:
            for item in selected:
                roll = self.tree.item(item, 'values')[0]
                self.student_data = self.student_data[self.student_data['Roll Number'] != roll]
            
            self.update_treeview()
            self.update_visualization()
            messagebox.showinfo("Success", "Record(s) deleted successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting record: {str(e)}")
    
    def load_selected_student(self, event=None):
        """Load selected student into the form for editing"""
        selected = self.tree.selection()
        
        if not selected:
            return
        
        try:
            values = self.tree.item(selected[0], 'values')
            roll = values[0]
            
            # Find the student record
            student = self.student_data[self.student_data['Roll Number'] == roll].iloc[0]
            
            # Fill form with student data
            self.roll_entry.delete(0, 'end')
            self.roll_entry.insert(0, student['Roll Number'])
            
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, student['Name'])
            
            # Fill grades
            for i, subject in enumerate(self.subject_names):
                self.grade_entries[i].set(student[subject] if pd.notna(student[subject]) else '')
        
        except Exception as e:
            messagebox.showerror("Error", f"Error loading student: {str(e)}")
    
    def update_treeview(self):
        """Update the treeview with current data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add rows
        for _, student in self.student_data.iterrows():
            values = [student['Roll Number'], student['Name']]
            
            # Add subject grades
            for subject in self.subject_names:
                values.append(student[subject] if pd.notna(student[subject]) else '')
            
            # Add CGPA
            values.append(student['CGPA'])
            
            self.tree.insert('', 'end', values=values)
    
    def save_to_excel(self):
        """Save student data to Excel file"""
        try:
            # Create new Excel file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=self.excel_file_path
            )
            
            if not file_path:
                return
            
            # Create a Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Student Grades"
            
            # Add headers
            headers = ['Roll Number', 'Name'] + self.subject_names + ['CGPA']
            ws.append(headers)
            
            # Add credit row (for reference)
            credit_row = ['Credits', ''] + self.credits + ['']
            ws.append(credit_row)
            
            # Add student data
            for _, student in self.student_data.iterrows():
                row = [student['Roll Number'], student['Name']]
                
                for subject in self.subject_names:
                    row.append(student[subject] if pd.notna(student[subject]) else '')
                
                row.append(student['CGPA'])
                ws.append(row)
            
            # Save the file
            wb.save(file_path)
            self.excel_file_path = file_path
            
            messagebox.showinfo("Success", f"Data saved to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saving to Excel: {str(e)}")
    
    def import_from_excel(self):
        """Import student data from Excel file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            self.load_data(file_path)
            messagebox.showinfo("Success", f"Data imported from {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {str(e)}")
    
    def load_data(self, file_path):
        """Load data from Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name="Student Grades")
            
            # Check for credit row (second row)
            if len(df) >= 2 and df.iloc[0, 0] == "Credits":
                # Extract credits
                credits_row = df.iloc[0]
                self.credits = []
                
                for i in range(2, len(credits_row) - 1):
                    try:
                        self.credits.append(float(credits_row.iloc[i]))
                    except:
                        self.credits.append(3.0)  # Default
                
                # Remove credits row
                df = df.drop(0)
            
            # Set headers
            headers = list(df.columns)
            
            # Update subject names
            self.subject_names = headers[2:-1]  # Exclude Roll Number, Name, and CGPA
            self.num_subjects = len(self.subject_names)
            
            # Make sure credits list is the right length
            if len(self.credits) != self.num_subjects:
                self.credits = [3.0] * self.num_subjects
            
            # Update student data
            self.student_data = df.copy()
            
            # Update UI to reflect new data
            self.update_subject_count()
            
            # Recreate the input tab
            for child in self.input_frame.winfo_children():
                child.destroy()
            
            self.setup_input_widgets()
            
            # Update visualization
            self.update_visualization()
        
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def generate_sample_data(self):
        """Generate sample data with 52 students for the configured subjects"""
        try:
            # Save current configuration first
            self.save_configuration()
            
            # Grade values (Indian 10-point system)
            grades = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']
            # Make higher grades more common
            weights = [0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.05, 0.05]
            
            # Create sample data
            new_data = []
            
            for i in range(1, 53):
                # Create roll number (format: CSE2023XXX)
                roll_number = f"CSE2023{i:03d}"
                
                # Generate a random name
                first_names = ["Rahul", "Priya", "Amit", "Neha", "Sachin", "Ananya", "Vikram", "Pooja", 
                              "Rohit", "Deepika", "Rajesh", "Kavita", "Vijay", "Sneha", "Arjun", "Meera",
                              "Aditya", "Nisha", "Vivek", "Simran", "Ravi", "Anjali", "Sanjay", "Isha"]
                last_names = ["Sharma", "Patel", "Singh", "Gupta", "Kumar", "Reddy", "Joshi", "Das",
                             "Verma", "Rao", "Mehta", "Nair", "Iyer", "Kapoor", "Malhotra", "Malik",
                             "Banerjee", "Roy", "Chatterjee", "Mukherjee", "Shah", "Goel", "Chauhan"]
                
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                
                # Generate random grades for each subject
                student_grades = random.choices(grades, weights=weights, k=len(self.subject_names))
                
                # Calculate CGPA
                grades_dict = {self.subject_names[j]: student_grades[j] for j in range(len(self.subject_names))}
                cgpa = self.calculate_cgpa(grades_dict)
                
                # Create student record
                new_record = {'Roll Number': roll_number, 'Name': name, 'CGPA': cgpa}
                
                # Add grades for each subject
                for j, subject in enumerate(self.subject_names):
                    new_record[subject] = student_grades[j]
                
                new_data.append(new_record)
            
            # Create DataFrame and update student_data
            self.student_data = pd.DataFrame(new_data)
            
            # Update UI
            self.update_treeview()
            self.update_visualization()
            
            messagebox.showinfo("Success", f"Generated sample data for {len(new_data)} students")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error generating sample data: {str(e)}")

def main():
    root = tk.Tk()
    app = CGPACalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()