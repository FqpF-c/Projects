import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta

class LibrarySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("700x500")
        
        # Initialize database
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the tabs
        self.create_books_tab()
        self.create_members_tab()
        self.create_borrowing_tab()
        
    def create_tables(self):
        # Books table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            available INTEGER DEFAULT 1
        )
        ''')
        
        # Members table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            fine REAL DEFAULT 0.0
        )
        ''')
        
        # Borrowings table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            member_id INTEGER,
            borrow_date TEXT,
            due_date TEXT,
            return_date TEXT,
            FOREIGN KEY (book_id) REFERENCES books (id),
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
        ''')
        
        self.conn.commit()

    # Books Tab
    def create_books_tab(self):
        books_frame = ttk.Frame(self.notebook)
        self.notebook.add(books_frame, text="Books")
        
        # Book management controls
        controls_frame = ttk.LabelFrame(books_frame, text="Book Management")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.title_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Author:").grid(row=0, column=2, padx=5, pady=5)
        self.author_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.author_var, width=20).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Book", command=self.add_book).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(controls_frame, text="Delete Book", command=self.delete_book).grid(row=0, column=5, padx=5, pady=5)
        
        # Books treeview
        self.books_tree = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Status"), show="headings")
        self.books_tree.heading("ID", text="ID")
        self.books_tree.heading("Title", text="Title")
        self.books_tree.heading("Author", text="Author")
        self.books_tree.heading("Status", text="Status")
        
        self.books_tree.column("ID", width=50)
        self.books_tree.column("Title", width=200)
        self.books_tree.column("Author", width=200)
        self.books_tree.column("Status", width=100)
        
        self.books_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh books list
        self.refresh_books()
        
    # Members Tab
    def create_members_tab(self):
        members_frame = ttk.Frame(self.notebook)
        self.notebook.add(members_frame, text="Members")
        
        # Member management controls
        controls_frame = ttk.LabelFrame(members_frame, text="Member Management")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Phone:").grid(row=0, column=2, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.phone_var, width=20).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Member", command=self.add_member).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(controls_frame, text="Pay Fine", command=self.pay_fine).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(controls_frame, text="Add Fine", command=self.add_custom_fine).grid(row=0, column=6, padx=5, pady=5)
        
        # Members treeview
        self.members_tree = ttk.Treeview(members_frame, columns=("ID", "Name", "Phone", "Fine"), show="headings")
        self.members_tree.heading("ID", text="ID")
        self.members_tree.heading("Name", text="Name")
        self.members_tree.heading("Phone", text="Phone")
        self.members_tree.heading("Fine", text="Fine Due")
        
        self.members_tree.column("ID", width=50)
        self.members_tree.column("Name", width=200)
        self.members_tree.column("Phone", width=150)
        self.members_tree.column("Fine", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(members_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        
        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Bind double-click event for editing
        self.members_tree.bind("<Double-1>", self.edit_member)
        
        # Refresh members list
        self.refresh_members()
        
    # Borrowing Tab
    def create_borrowing_tab(self):
        borrowing_frame = ttk.Frame(self.notebook)
        self.notebook.add(borrowing_frame, text="Borrowing")
        
        # Split the frame into top and bottom sections
        top_frame = ttk.Frame(borrowing_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        bottom_frame = ttk.Frame(borrowing_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== TOP SECTION: AVAILABLE BOOKS & MEMBER SELECTION =====
        
        # Create left and right panels for the top section
        books_panel = ttk.LabelFrame(top_frame, text="Books")
        books_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        member_panel = ttk.LabelFrame(top_frame, text="Select Member")
        member_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5, ipadx=10)
        
        # Member selection dropdown
        ttk.Label(member_panel, text="Select Member:").pack(pady=(10, 5))
        
        self.member_var = tk.StringVar()
        self.member_dropdown = ttk.Combobox(member_panel, textvariable=self.member_var, state="readonly", width=25)
        self.member_dropdown.pack(pady=5)
        
        ttk.Button(member_panel, text="Return Selected Book", 
                  command=self.return_book).pack(pady=20)
        
        # Books display with colors and borrow buttons
        self.books_canvas = tk.Canvas(books_panel)
        scrollbar = ttk.Scrollbar(books_panel, orient="vertical", command=self.books_canvas.yview)
        self.books_frame = ttk.Frame(self.books_canvas)
        
        self.books_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.books_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.books_canvas.create_window((0, 0), window=self.books_frame, anchor="nw", tags="self.books_frame")
        
        self.books_frame.bind("<Configure>", 
                             lambda e: self.books_canvas.configure(scrollregion=self.books_canvas.bbox("all")))
        
        # ===== BOTTOM SECTION: BORROWING RECORDS =====
        
        # Borrowings treeview
        ttk.Label(bottom_frame, text="Borrowing Records", font=("", 11, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.borrowings_tree = ttk.Treeview(bottom_frame, 
                                           columns=("ID", "Book", "Member", "Borrow Date", "Due Date", "Status"), 
                                           show="headings")
        self.borrowings_tree.heading("ID", text="ID")
        self.borrowings_tree.heading("Book", text="Book")
        self.borrowings_tree.heading("Member", text="Member")
        self.borrowings_tree.heading("Borrow Date", text="Borrow Date")
        self.borrowings_tree.heading("Due Date", text="Due Date")
        self.borrowings_tree.heading("Status", text="Status")
        
        self.borrowings_tree.column("ID", width=30)
        self.borrowings_tree.column("Book", width=150)
        self.borrowings_tree.column("Member", width=150)
        self.borrowings_tree.column("Borrow Date", width=100)
        self.borrowings_tree.column("Due Date", width=100)
        self.borrowings_tree.column("Status", width=80)
        
        scrollbar = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.borrowings_tree.yview)
        self.borrowings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.borrowings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize
        self.load_members_dropdown()
        self.refresh_book_buttons()
        self.refresh_borrowings()
    
    # Book Operations
    def add_book(self):
        title = self.title_var.get()
        author = self.author_var.get()
        
        if not title or not author:
            messagebox.showwarning("Warning", "Please enter title and author")
            return
            
        try:
            self.cursor.execute(
                "INSERT INTO books (title, author, available) VALUES (?, ?, ?)",
                (title, author, 1)
            )
            self.conn.commit()
            self.title_var.set("")
            self.author_var.set("")
            self.refresh_books()
            messagebox.showinfo("Success", "Book added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def delete_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete")
            return
            
        book_id = self.books_tree.item(selected[0], "values")[0]
        
        # Check if book is borrowed
        self.cursor.execute(
            "SELECT COUNT(*) FROM borrowings WHERE book_id = ? AND return_date IS NULL", 
            (book_id,)
        )
        if self.cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", "Cannot delete book because it is currently borrowed")
            return
            
        try:
            self.cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            self.conn.commit()
            self.refresh_books()
            messagebox.showinfo("Success", "Book deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_books(self):
        # Clear the treeview
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
            
        # Fetch all books
        try:
            self.cursor.execute("""
                SELECT id, title, author, available FROM books
            """)
            books = self.cursor.fetchall()
            
            for book in books:
                book_id, title, author, available = book
                status = "Available" if available else "Borrowed"
                self.books_tree.insert("", tk.END, values=(book_id, title, author, status))
                
            # Also refresh the book buttons in the borrowing tab if it exists
            if hasattr(self, 'books_frame'):
                self.refresh_book_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    # Member Operations
    def add_member(self):
        name = self.name_var.get()
        phone = self.phone_var.get()
        
        if not name:
            messagebox.showwarning("Warning", "Please enter member name")
            return
            
        try:
            self.cursor.execute(
                "INSERT INTO members (name, phone, fine) VALUES (?, ?, ?)",
                (name, phone, 0.0)
            )
            self.conn.commit()
            self.name_var.set("")
            self.phone_var.set("")
            self.refresh_members()
            messagebox.showinfo("Success", "Member added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def pay_fine(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member")
            return
            
        member_id = self.members_tree.item(selected[0], "values")[0]
        
        # Check if member has fine
        self.cursor.execute("SELECT name, fine FROM members WHERE id = ?", (member_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Member not found")
            return
            
        name, fine = result
        
        if fine <= 0:
            messagebox.showinfo("Info", "No fine to pay")
            return
            
        # Confirm payment
        if messagebox.askyesno("Confirm Payment", f"Pay fine of ${fine:.2f} for {name}?"):
            try:
                self.cursor.execute("UPDATE members SET fine = 0 WHERE id = ?", (member_id,))
                self.conn.commit()
                self.refresh_members()
                messagebox.showinfo("Success", f"Fine of ${fine:.2f} paid successfully")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                
    def add_custom_fine(self):
        """Add a custom fine amount to a selected member"""
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a member to add a fine")
            return
            
        member_id = self.members_tree.item(selected[0], "values")[0]
        member_name = self.members_tree.item(selected[0], "values")[1]
        
        # Prompt for fine amount
        fine_amount = simpledialog.askfloat("Add Fine", 
                                           f"Enter fine amount for {member_name}:",
                                           minvalue=0.01,
                                           maxvalue=1000.0)
        
        if fine_amount is None:  # User cancelled
            return
            
        # Prompt for reason
        reason = simpledialog.askstring("Fine Reason", 
                                       "Enter reason for fine (optional):")
        
        try:
            # Update member's fine
            self.cursor.execute(
                "UPDATE members SET fine = fine + ? WHERE id = ?",
                (fine_amount, member_id)
            )
            
            self.conn.commit()
            self.refresh_members()
            
            messagebox.showinfo("Success", 
                               f"Fine of ${fine_amount:.2f} added to {member_name}" +
                               (f"\nReason: {reason}" if reason else ""))
                               
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def edit_member(self, event):
        """Handle double-click on member to edit"""
        selected = self.members_tree.selection()
        if not selected:
            return
            
        item = selected[0]
        member_id = self.members_tree.item(item, "values")[0]
        
        # Fetch member data
        self.cursor.execute("SELECT id, name, phone, fine FROM members WHERE id = ?", (member_id,))
        member = self.cursor.fetchone()
        
        if not member:
            messagebox.showerror("Error", "Member not found")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Member - {member[1]}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        edit_window.grab_set()  # Make window modal
        
        ttk.Label(edit_window, text="Edit Member", font=("", 14, "bold")).pack(pady=10)
        
        form_frame = ttk.Frame(edit_window)
        form_frame.pack(padx=20, pady=10, fill=tk.X)
        
        # Member ID (read-only)
        ttk.Label(form_frame, text="Member ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_var = tk.StringVar(value=member[0])
        ttk.Entry(form_frame, textvariable=id_var, state="readonly", width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=member[1])
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Phone
        ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        phone_var = tk.StringVar(value=member[2])
        ttk.Entry(form_frame, textvariable=phone_var, width=30).grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Current Fine (read-only)
        ttk.Label(form_frame, text="Current Fine:").grid(row=3, column=0, sticky=tk.W, pady=5)
        fine_var = tk.StringVar(value=f"${member[3]:.2f}")
        ttk.Entry(form_frame, textvariable=fine_var, state="readonly", width=10).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Fine management buttons
        fine_buttons_frame = ttk.Frame(form_frame)
        fine_buttons_frame.grid(row=3, column=2, sticky=tk.W, pady=5)
        
        if member[3] > 0:
            ttk.Button(fine_buttons_frame, text="Pay Fine", 
                     command=lambda: self.pay_member_fine(member[0], edit_window)).pack(side=tk.LEFT, padx=2)
                     
        ttk.Button(fine_buttons_frame, text="Add Fine", 
                 command=lambda: self.add_member_fine(member[0], member[1], edit_window)).pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save Changes", 
                 command=lambda: self.save_member_changes(member[0], name_var.get(), phone_var.get(), edit_window)
                 ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Cancel", 
                 command=edit_window.destroy).pack(side=tk.LEFT, padx=10)
                 
    def add_member_fine(self, member_id, member_name, parent_window=None):
        """Add a custom fine amount from the edit window"""
        # Prompt for fine amount
        fine_amount = simpledialog.askfloat("Add Fine", 
                                           f"Enter fine amount for {member_name}:",
                                           minvalue=0.01,
                                           maxvalue=1000.0,
                                           parent=parent_window)
        
        if fine_amount is None:  # User cancelled
            return
            
        # Prompt for reason
        reason = simpledialog.askstring("Fine Reason", 
                                       "Enter reason for fine (optional):",
                                       parent=parent_window)
        
        try:
            # Update member's fine
            self.cursor.execute(
                "UPDATE members SET fine = fine + ? WHERE id = ?",
                (fine_amount, member_id)
            )
            
            self.conn.commit()
            self.refresh_members()
            
            # Update the fine field in the edit window if it exists
            if parent_window:
                # Recalculate the current fine
                self.cursor.execute("SELECT fine FROM members WHERE id = ?", (member_id,))
                current_fine = self.cursor.fetchone()[0]
                
                # Find the fine display field and update it
                for widget in parent_window.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Entry) and child.cget("state") == "readonly":
                                try:
                                    var_name = child.cget("textvariable")
                                    var = parent_window.nametowidget(var_name)
                                    if "$" in var.get():
                                        var.set(f"${current_fine:.2f}")
                                except:
                                    # If the above approach doesn't work, iterate through all variables
                                    for var_name in parent_window.children:
                                        try:
                                            var = parent_window.nametowidget(var_name)
                                            if hasattr(var, 'get') and "$" in var.get():
                                                var.set(f"${current_fine:.2f}")
                                        except:
                                            pass
            
            messagebox.showinfo("Success", 
                               f"Fine of ${fine_amount:.2f} added to {member_name}" +
                               (f"\nReason: {reason}" if reason else ""),
                               parent=parent_window)
                               
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=parent_window)
                 
    def pay_member_fine(self, member_id, window=None):
        """Pay fine for a member from the edit window"""
        # Check current fine
        self.cursor.execute("SELECT name, fine FROM members WHERE id = ?", (member_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Member not found", parent=window)
            return
            
        name, fine = result
        
        if fine <= 0:
            messagebox.showinfo("Info", "No fine to pay", parent=window)
            return
            
        # Confirm payment
        if messagebox.askyesno("Confirm Payment", f"Pay fine of ${fine:.2f} for {name}?", parent=window):
            try:
                self.cursor.execute("UPDATE members SET fine = 0 WHERE id = ?", (member_id,))
                self.conn.commit()
                self.refresh_members()
                
                # Update the fine field in the edit window if it exists
                if window:
                    for widget in window.winfo_children():
                        if isinstance(widget, ttk.Frame):
                            for w in widget.winfo_children():
                                if isinstance(w, ttk.Entry) and w.cget("state") == "readonly":
                                    for var in w.cget("textvariable"):
                                        if var.get().startswith("$"):
                                            var.set("$0.00")
                
                messagebox.showinfo("Success", f"Fine of ${fine:.2f} paid successfully", parent=window)
                
                # Close the window if it exists
                if window:
                    window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=window)
                
    def save_member_changes(self, member_id, name, phone, window):
        """Save changes to member details"""
        if not name:
            messagebox.showwarning("Warning", "Name cannot be empty", parent=window)
            return
            
        try:
            self.cursor.execute(
                "UPDATE members SET name = ?, phone = ? WHERE id = ?",
                (name, phone, member_id)
            )
            self.conn.commit()
            self.refresh_members()
            messagebox.showinfo("Success", "Member details updated successfully", parent=window)
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=window)
    
    def refresh_members(self):
        # Clear the treeview
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
            
        # Fetch all members
        try:
            self.cursor.execute("""
                SELECT id, name, phone, fine FROM members
            """)
            members = self.cursor.fetchall()
            
            for member in members:
                member_id, name, phone, fine = member
                self.members_tree.insert("", tk.END, values=(member_id, name, phone, f"${fine:.2f}"))
                
            # Also refresh the members dropdown if it exists
            if hasattr(self, 'member_dropdown'):
                self.load_members_dropdown()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def load_members_dropdown(self):
        """Load all members into the dropdown combobox"""
        try:
            self.cursor.execute("SELECT id, name FROM members ORDER BY name")
            members = self.cursor.fetchall()
            
            # Format as "ID: Name" for easy selection
            member_list = [f"{member[0]}: {member[1]}" for member in members]
            self.member_dropdown['values'] = member_list
            
            # Select the first member if available
            if member_list:
                self.member_dropdown.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred loading members: {str(e)}")
            
    def refresh_book_buttons(self):
        """Refresh the book buttons in the borrowing tab"""
        # Clear existing buttons
        for widget in self.books_frame.winfo_children():
            widget.destroy()
            
        try:
            # Get all books
            self.cursor.execute("""
                SELECT id, title, author, available FROM books ORDER BY title
            """)
            books = self.cursor.fetchall()
            
            # Create a frame for each book
            for i, book in enumerate(books):
                book_id, title, author, available = book
                
                # Create a frame with colored background
                bg_color = "#90EE90" if available else "#FFCCCC"  # Green if available, red if not
                
                book_frame = tk.Frame(self.books_frame, bd=1, relief=tk.RAISED, bg=bg_color)
                book_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5, ipadx=5, ipady=5)
                
                # Book information
                info_frame = tk.Frame(book_frame, bg=bg_color)
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                tk.Label(info_frame, text=f"ID: {book_id}", bg=bg_color, font=("", 9, "bold")).pack(anchor=tk.W)
                tk.Label(info_frame, text=f"Title: {title}", bg=bg_color).pack(anchor=tk.W)
                tk.Label(info_frame, text=f"Author: {author}", bg=bg_color).pack(anchor=tk.W)
                
                status_text = "Available" if available else "Borrowed"
                tk.Label(info_frame, text=f"Status: {status_text}", bg=bg_color, 
                        fg="dark green" if available else "dark red").pack(anchor=tk.W)
                
                # Button frame
                button_frame = tk.Frame(book_frame, bg=bg_color)
                button_frame.pack(side=tk.RIGHT, padx=5, pady=5)
                
                # Only show borrow button if book is available
                if available:
                    borrow_btn = tk.Button(button_frame, text="Borrow", bg="#4CAF50", fg="white",
                                         command=lambda bid=book_id: self.issue_book(bid))
                    borrow_btn.pack(pady=5)
            
            # Update the canvas scroll region
            self.books_frame.update_idletasks()
            self.books_canvas.configure(scrollregion=self.books_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred refreshing book buttons: {str(e)}")
    
    # Borrowing Operations
    def issue_book(self, book_id=None):
        # If book_id is not provided, try to get it from the entry field (old UI)
        if book_id is None:
            if hasattr(self, 'book_id_var'):
                book_id = self.book_id_var.get()
            else:
                messagebox.showwarning("Warning", "No book selected")
                return
        
        # Get member ID from dropdown
        member_name = self.member_var.get()
        if not member_name:
            messagebox.showwarning("Warning", "Please select a member")
            return
            
        # Extract the ID from the selected member (format: "ID: Name")
        member_id = member_name.split(':')[0].strip()
            
        # Check if book exists and is available
        self.cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Book not found")
            return
            
        if not result[0]:
            messagebox.showerror("Error", "Book is not available")
            return
            
        try:
            # Set borrow date and due date (14 days from now)
            borrow_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            
            # Insert borrowing record
            self.cursor.execute(
                "INSERT INTO borrowings (book_id, member_id, borrow_date, due_date) VALUES (?, ?, ?, ?)",
                (book_id, member_id, borrow_date, due_date)
            )
            
            # Update book availability
            self.cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
            
            self.conn.commit()
            
            # Clear any variables and refresh UI
            if hasattr(self, 'book_id_var'):
                self.book_id_var.set("")
            if hasattr(self, 'member_id_var'):
                self.member_id_var.set("")
                
            self.refresh_books()
            self.refresh_book_buttons()
            self.refresh_borrowings()
            messagebox.showinfo("Success", "Book issued successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def return_book(self):
        selected = self.borrowings_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a borrowing record to return")
            return
            
        borrow_id = self.borrowings_tree.item(selected[0], "values")[0]
        
        # Check if book is already returned
        self.cursor.execute("SELECT return_date, book_id, member_id, due_date FROM borrowings WHERE id = ?", (borrow_id,))
        result = self.cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", "Borrowing record not found")
            return
            
        return_date, book_id, member_id, due_date = result
        
        if return_date:
            messagebox.showinfo("Info", "Book already returned")
            return
            
        try:
            # Set return date
            return_date = datetime.now().strftime("%Y-%m-%d")
            
            # Calculate fine if returned late (using datetime objects)
            today = datetime.now()
            due = datetime.strptime(due_date, "%Y-%m-%d")
            
            fine = 0.0
            if today > due:
                days_late = (today - due).days
                fine = days_late * 0.5  # $0.50 per day late
                
                # Add fine to member
                self.cursor.execute(
                    "UPDATE members SET fine = fine + ? WHERE id = ?",
                    (fine, member_id)
                )
            
            # Update borrowing record
            self.cursor.execute(
                "UPDATE borrowings SET return_date = ? WHERE id = ?",
                (return_date, borrow_id)
            )
            
            # Update book availability
            self.cursor.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
            
            self.conn.commit()
            self.refresh_books()
            self.refresh_borrowings()
            self.refresh_members()
            self.refresh_book_buttons()
            
            if fine > 0:
                messagebox.showinfo("Book Returned", f"Book returned with a fine of ${fine:.2f}")
            else:
                messagebox.showinfo("Success", "Book returned successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_borrowings(self):
        # Clear the treeview
        for item in self.borrowings_tree.get_children():
            self.borrowings_tree.delete(item)
            
        # Fetch all borrowings with book and member names
        try:
            self.cursor.execute("""
                SELECT b.id, bk.title, m.name, b.borrow_date, b.due_date, b.return_date
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.id
                JOIN members m ON b.member_id = m.id
                ORDER BY b.borrow_date DESC
            """)
            borrowings = self.cursor.fetchall()
            
            for borrowing in borrowings:
                borrow_id, title, name, borrow_date, due_date, return_date = borrowing
                status = "Returned" if return_date else "Borrowed"
                self.borrowings_tree.insert("", tk.END, values=(borrow_id, title, name, borrow_date, due_date, status))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def add_sample_data(app):
    # Add sample books
    sample_books = [
        ("To Kill a Mockingbird", "Harper Lee"),
        ("1984", "George Orwell"),
        ("The Great Gatsby", "F. Scott Fitzgerald"),
        ("Pride and Prejudice", "Jane Austen"),
        ("The Hobbit", "J.R.R. Tolkien"),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling"),
        ("The Catcher in the Rye", "J.D. Salinger"),
        ("Lord of the Flies", "William Golding"),
        ("The Hunger Games", "Suzanne Collins"),
        ("The Alchemist", "Paulo Coelho")
    ]
    
    for title, author in sample_books:
        try:
            app.cursor.execute(
                "INSERT INTO books (title, author, available) VALUES (?, ?, ?)",
                (title, author, 1)
            )
        except:
            pass  # Skip if already exists
    
    # Add sample members (A-Z names)
    sample_members = [
        ("Alice Johnson", "555-1001"),
        ("Bob Smith", "555-1002"),
        ("Charlie Brown", "555-1003"),
        ("David Wilson", "555-1004"),
        ("Emma Davis", "555-1005"),
        ("Frank Miller", "555-1006"),
        ("Grace Taylor", "555-1007"),
        ("Henry Martin", "555-1008"),
        ("Irene Walker", "555-1009"),
        ("Jack Thompson", "555-1010"),
        ("Karen White", "555-1011"),
        ("Leo Anderson", "555-1012"),
        ("Mary Harris", "555-1013"),
        ("Noah Clark", "555-1014"),
        ("Olivia Lewis", "555-1015"),
        ("Peter Young", "555-1016"),
        ("Quinn Wright", "555-1017"),
        ("Rachel Allen", "555-1018"),
        ("Samuel Scott", "555-1019"),
        ("Tina King", "555-1020"),
        ("Uma Green", "555-1021"),
        ("Victor Hall", "555-1022"),
        ("Wendy Baker", "555-1023"),
        ("Xavier Reed", "555-1024"),
        ("Yasmin Cook", "555-1025"),
        ("Zack Phillips", "555-1026")
    ]
    
    for name, phone in sample_members:
        try:
            app.cursor.execute(
                "INSERT INTO members (name, phone, fine) VALUES (?, ?, ?)",
                (name, phone, 0.0)
            )
        except:
            pass  # Skip if already exists
    
    app.conn.commit()
    
    # Refresh the UI
    app.refresh_books()
    app.refresh_members()
    app.refresh_borrowings()

def main():
    root = tk.Tk()
    app = LibrarySystem(root)
    
    # Add sample data
    add_sample_data(app)
    
    root.mainloop()

if __name__ == "__main__":
    main()