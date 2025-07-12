import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from loan_prediction_system import LoanEligibilityModel
import joblib
from tkinter.font import Font
# Using try/except for ttkthemes in case it's not installed
try:
    from ttkthemes import ThemedTk
except ImportError:
    ThemedTk = None
# Using try/except for PIL in case it's not installed
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None
import os

class LoanEligibilityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Loan Eligibility Predictor")
        self.root.geometry("1280x800")
        
        # Set app theme
        self.root.configure(bg="#f5f5f7")
        
        # Set custom fonts
        self.header_font = Font(family="Helvetica", size=16, weight="bold")
        self.section_font = Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = Font(family="Helvetica", size=10)
        self.result_font = Font(family="Helvetica", size=12, weight="bold")
        
        # Load the trained model
        try:
            self.model = LoanEligibilityModel.load_model('loan_eligibility_model.joblib')
        except FileNotFoundError:
            messagebox.showerror("Error", "Model file not found! Please train the model first.")
            root.destroy()
            return
            
        # Configure custom styles
        self.configure_styles()
        
        # Create main container
        self.main_frame = ttk.Frame(root, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create header frame
        self.create_header()
        
        # Create notebook for tabs
        self.create_notebook()
        
        # Create application form tab
        self.create_application_tab()
        
        # Create dashboard tab
        self.create_dashboard_tab()
        
        # Create history tab
        self.create_history_tab()
        
        # Initialize loan requirements data
        self.initialize_loan_requirements()
        
        # Update requirements display
        self.update_requirements()

    def configure_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        
        # Main frames
        style.configure("Main.TFrame", background="#f5f5f7")
        
        # Header style
        style.configure("Header.TLabel", 
                        font=self.header_font, 
                        background="#0066cc", 
                        foreground="white",
                        padding=10)
        
        # Section headers
        style.configure("Section.TLabel", 
                        font=self.section_font, 
                        background="#f5f5f7", 
                        foreground="#333333",
                        padding=(0, 10, 0, 5))
        
        # Normal labels
        style.configure("TLabel", 
                        font=self.normal_font, 
                        background="#f5f5f7",
                        foreground="#333333")
        
        # Entry fields
        style.configure("TEntry", 
                        font=self.normal_font, 
                        fieldbackground="white")
        
        # Comboboxes
        style.configure("TCombobox", 
                        font=self.normal_font,
                        fieldbackground="white")
        
        # Buttons
        style.configure("TButton", 
                        font=self.normal_font,
                        padding=8)
        
        style.configure("Primary.TButton",
                        background="#0066cc",
                        foreground="black")
        
        style.map("Primary.TButton",
                  background=[("active", "#004d99")],
                  foreground=[("active", "black")])
        
        # Notebook tabs
        style.configure("TNotebook", 
                        background="#f5f5f7",
                        tabmargins=[2, 5, 2, 0])
        
        style.configure("TNotebook.Tab", 
                        font=self.normal_font,
                        padding=[15, 5],
                        background="#e0e0e0")
        
        style.map("TNotebook.Tab",
                  background=[("selected", "#0066cc")],
                  foreground=[("selected", "white")])
        
        # Frames
        style.configure("Card.TFrame", 
                        background="white", 
                        relief="raised")
        
        # Result styles
        style.configure("Approved.TLabel", 
                        font=self.result_font,
                        foreground="#28a745",
                        background="white")
        
        style.configure("Denied.TLabel", 
                        font=self.result_font,
                        foreground="#dc3545",
                        background="white")
                        
        # Progress bar
        style.configure("Confidence.Horizontal.TProgressbar", 
                        troughcolor="#f0f0f0", 
                        background="#0066cc")

    def create_header(self):
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # App logo/name
        logo_frame = ttk.Frame(header_frame, style="Header.TFrame")
        logo_frame.pack(fill=tk.X)
        
        # Load logo if available and PIL is installed
        if Image is not None and ImageTk is not None:
            try:
                logo_img = Image.open("loan_logo.png")
                logo_img = logo_img.resize((40, 40), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(logo_frame, image=self.logo_photo, style="Header.TLabel")
                logo_label.pack(side=tk.LEFT, padx=10)
            except:
                pass  # No logo available or can't load
        
        app_name = ttk.Label(logo_frame, text="Loan Eligibility Predictor", style="Header.TLabel")
        app_name.pack(side=tk.LEFT, padx=10)

    def create_notebook(self):
        """Create notebook for tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def create_application_tab(self):
        """Create application form tab"""
        self.app_tab = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(self.app_tab, text="New Application")
        
        # Split into two columns using a PanedWindow
        self.app_paned = ttk.PanedWindow(self.app_tab, orient=tk.HORIZONTAL)
        self.app_paned.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel for form
        self.left_panel = ttk.Frame(self.app_paned, style="Main.TFrame")
        
        # Create right panel for requirements (with fixed width)
        self.right_panel = ttk.Frame(self.app_paned, style="Main.TFrame")
        
        # Add both panels to the PanedWindow
        self.app_paned.add(self.left_panel, weight=3)  # Form gets more space
        self.app_paned.add(self.right_panel, weight=1)  # Requirements panel gets less space
        
        # Create scrollable form
        self.create_application_form()
        
        # Create requirements panel
        self.create_requirements_panel()

    def create_application_form(self):
        """Create the application form with inputs"""
        # Create canvas with scrollbar for the form
        canvas_frame = ttk.Frame(self.left_panel, style="Main.TFrame")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        form_canvas = tk.Canvas(canvas_frame, bg="#f5f5f7", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=form_canvas.yview)
        
        self.scrollable_frame = ttk.Frame(form_canvas, style="Main.TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all"))
        )
        
        form_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        form_canvas.configure(yscrollcommand=scrollbar.set)
        
        form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Form content
        self.create_form_sections()
        
        # Bind mousewheel for scrolling
        form_canvas.bind_all("<MouseWheel>", lambda e: form_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # For Linux and Mac (if needed)
        form_canvas.bind_all("<Button-4>", lambda e: form_canvas.yview_scroll(-1, "units"))
        form_canvas.bind_all("<Button-5>", lambda e: form_canvas.yview_scroll(1, "units"))

    def create_form_sections(self):
        """Create form sections with all inputs"""
        # Personal Information Section
        personal_frame = ttk.LabelFrame(self.scrollable_frame, text="Personal Information", padding=15)
        personal_frame.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=10)
        
        # Gender
        ttk.Label(personal_frame, text="Gender:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(personal_frame, textvariable=self.gender_var, width=25, state="readonly")
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        gender_combo.set('Male')
        
        # Marital Status
        ttk.Label(personal_frame, text="Marital Status:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.marital_var = tk.StringVar()
        marital_combo = ttk.Combobox(personal_frame, textvariable=self.marital_var, width=25, state="readonly")
        marital_combo['values'] = ('Single', 'Married', 'Divorced', 'Widowed')
        marital_combo.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)
        marital_combo.set('Single')
        
        # Education
        ttk.Label(personal_frame, text="Education:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.education_var = tk.StringVar()
        education_combo = ttk.Combobox(personal_frame, textvariable=self.education_var, width=25, state="readonly")
        education_combo['values'] = ('Graduate', 'Not Graduate')
        education_combo.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        education_combo.set('Graduate')
        
        # Employment Information Section
        employment_frame = ttk.LabelFrame(self.scrollable_frame, text="Employment Information", padding=15)
        employment_frame.grid(row=1, column=0, sticky=tk.EW, padx=10, pady=10)
        
        # Employment Status
        ttk.Label(employment_frame, text="Employment Status:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.employment_var = tk.StringVar()
        employment_combo = ttk.Combobox(employment_frame, textvariable=self.employment_var, width=25, state="readonly")
        employment_combo['values'] = ('Employed', 'Self-employed', 'Unemployed')
        employment_combo.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        employment_combo.set('Employed')
        
        # Financial Information Section
        financial_frame = ttk.LabelFrame(self.scrollable_frame, text="Financial Information", padding=15)
        financial_frame.grid(row=2, column=0, sticky=tk.EW, padx=10, pady=10)
        
        # Annual Income
        ttk.Label(financial_frame, text="Annual Income ($):").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.income_var = tk.StringVar()
        income_entry = ttk.Entry(financial_frame, textvariable=self.income_var, width=25)
        income_entry.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        
        # Co-applicant Income
        ttk.Label(financial_frame, text="Co-applicant Income ($):").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.coapplicant_income_var = tk.StringVar()
        coapplicant_income_entry = ttk.Entry(financial_frame, textvariable=self.coapplicant_income_var, width=25)
        coapplicant_income_entry.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)
        
        # Credit Score
        ttk.Label(financial_frame, text="Credit Score:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.credit_var = tk.StringVar()
        credit_entry = ttk.Entry(financial_frame, textvariable=self.credit_var, width=25)
        credit_entry.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        
        # Credit History
        ttk.Label(financial_frame, text="Credit History:").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.credit_history_var = tk.StringVar()
        credit_history_combo = ttk.Combobox(financial_frame, textvariable=self.credit_history_var, width=25, state="readonly")
        credit_history_combo['values'] = ('Good (1+ year)', 'Limited (< 1 year)', 'None')
        credit_history_combo.grid(row=3, column=1, padx=10, pady=8, sticky=tk.W)
        credit_history_combo.set('Good (1+ year)')
        
        # Loan Information Section
        loan_frame = ttk.LabelFrame(self.scrollable_frame, text="Loan Information", padding=15)
        loan_frame.grid(row=3, column=0, sticky=tk.EW, padx=10, pady=10)
        
        # Loan Type
        ttk.Label(loan_frame, text="Loan Type:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.loan_type_var = tk.StringVar()
        loan_type_combo = ttk.Combobox(loan_frame, textvariable=self.loan_type_var, width=25, state="readonly")
        loan_type_combo['values'] = ('Home Loan', 'Education Loan', 'Car Loan', 'Personal Loan', 'Business Loan')
        loan_type_combo.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        loan_type_combo.set('Home Loan')
        loan_type_combo.bind('<<ComboboxSelected>>', self.update_requirements)
        
        # Loan Amount
        ttk.Label(loan_frame, text="Loan Amount ($):").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.loan_amount_var = tk.StringVar()
        loan_amount_entry = ttk.Entry(loan_frame, textvariable=self.loan_amount_var, width=25)
        loan_amount_entry.grid(row=1, column=1, padx=10, pady=8, sticky=tk.W)
        
        # Loan Term
        ttk.Label(loan_frame, text="Loan Term (months):").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.loan_term_var = tk.StringVar()
        loan_term_combo = ttk.Combobox(loan_frame, textvariable=self.loan_term_var, width=25, state="readonly")
        loan_term_combo['values'] = ('12', '24', '36', '48', '60', '72', '84', '120', '180', '240', '300', '360')
        loan_term_combo.grid(row=2, column=1, padx=10, pady=8, sticky=tk.W)
        loan_term_combo.set('36')
        
        # Property Information (for Home Loans)
        property_frame = ttk.LabelFrame(self.scrollable_frame, text="Property Information", padding=15)
        property_frame.grid(row=4, column=0, sticky=tk.EW, padx=10, pady=10)
        
        # Property Area
        ttk.Label(property_frame, text="Property Area:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.property_area_var = tk.StringVar()
        property_area_combo = ttk.Combobox(property_frame, textvariable=self.property_area_var, width=25, state="readonly")
        property_area_combo['values'] = ('Urban', 'Suburban', 'Rural')
        property_area_combo.grid(row=0, column=1, padx=10, pady=8, sticky=tk.W)
        property_area_combo.set('Urban')
        
        # Action Buttons
        action_frame = ttk.Frame(self.scrollable_frame, style="Main.TFrame")
        action_frame.grid(row=5, column=0, pady=20)
        
        predict_btn = ttk.Button(action_frame, text="Check Eligibility", 
                               command=self.predict_eligibility, style="Primary.TButton")
        predict_btn.grid(row=0, column=0, padx=5)
        
        clear_btn = ttk.Button(action_frame, text="Clear Form", 
                             command=self.clear_form)
        clear_btn.grid(row=0, column=1, padx=5)
        
        # Result Section
        self.create_result_section()

    def create_result_section(self):
        """Create the result section"""
        self.result_frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame")
        self.result_frame.grid(row=6, column=0, sticky=tk.EW, padx=10, pady=15)
        self.result_frame.grid_remove()  # Hide initially
        
        # Result content
        result_container = ttk.Frame(self.result_frame, style="Card.TFrame")
        result_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Result header
        result_header = ttk.Frame(result_container, style="Card.TFrame")
        result_header.pack(fill=tk.X, pady=(0, 15))
        
        self.result_title = ttk.Label(result_header, text="Loan Application Result", font=self.section_font, background="white")
        self.result_title.pack(side=tk.LEFT)
        
        # Result status
        self.eligibility_label = ttk.Label(result_container, text="", style="Approved.TLabel")
        self.eligibility_label.pack(pady=10, anchor=tk.W)
        
        # Confidence progress bar
        confidence_frame = ttk.Frame(result_container, style="Card.TFrame")
        confidence_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(confidence_frame, text="Confidence:", background="white").pack(side=tk.LEFT)
        
        self.confidence_var = tk.IntVar()
        self.confidence_bar = ttk.Progressbar(confidence_frame, orient=tk.HORIZONTAL, 
                                             length=250, mode='determinate', 
                                             variable=self.confidence_var,
                                             style="Confidence.Horizontal.TProgressbar")
        self.confidence_bar.pack(side=tk.LEFT, padx=10)
        
        self.confidence_label = ttk.Label(confidence_frame, text="", background="white")
        self.confidence_label.pack(side=tk.LEFT)
        
        # Recommendation
        recommendation_frame = ttk.Frame(result_container, style="Card.TFrame")
        recommendation_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(recommendation_frame, text="Recommendation:", background="white", font=self.normal_font).pack(anchor=tk.W)
        
        self.recommendation_label = ttk.Label(recommendation_frame, text="", 
                                            background="white", wraplength=550)
        self.recommendation_label.pack(pady=(5, 0), anchor=tk.W)

    def create_requirements_panel(self):
        """Create the requirements panel"""
        # Requirements card
        requirements_card = ttk.Frame(self.right_panel, style="Card.TFrame")
        requirements_card.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Header
        req_header = ttk.Frame(requirements_card, style="Card.TFrame", padding=10)
        req_header.pack(fill=tk.X)
        
        req_title = ttk.Label(req_header, text="Loan Requirements", 
                             font=self.section_font, background="white")
        req_title.pack(side=tk.LEFT)
        
        # Requirements text with styling
        self.requirements_text = tk.Text(requirements_card, wrap=tk.WORD, width=30, height=30,
                                      font=self.normal_font, bg="white", relief="flat",
                                      padx=15, pady=10)
        self.requirements_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags
        self.requirements_text.tag_configure('header', font=('Helvetica', 13, 'bold'))
        self.requirements_text.tag_configure('category', font=('Helvetica', 11, 'bold'), foreground="#0066cc")
        self.requirements_text.tag_configure('item', lmargin1=20, lmargin2=20)
        self.requirements_text.tag_configure('note', font=('Helvetica', 9, 'italic'), foreground="#666666")
        self.requirements_text.tag_configure('bullet', foreground="#0066cc")

    def create_dashboard_tab(self):
        """Create dashboard tab with visualizations"""
        dashboard_tab = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(dashboard_tab, text="Dashboard")
        
        # Dashboard Header
        dash_header = ttk.Frame(dashboard_tab, style="Header.TFrame")
        dash_header.pack(fill=tk.X)
        
        dash_title = ttk.Label(dash_header, text="Application Dashboard", style="Header.TLabel")
        dash_title.pack(padx=20, pady=10)
        
        # Dashboard content - Statistics cards
        stats_frame = ttk.Frame(dashboard_tab, style="Main.TFrame")
        stats_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # Create statistics cards
        self.create_stat_card(stats_frame, "Total Applications", "24", 0)
        self.create_stat_card(stats_frame, "Approved", "16", 1)
        self.create_stat_card(stats_frame, "Pending", "5", 2)
        self.create_stat_card(stats_frame, "Rejected", "3", 3)
        
        # Charts section - would include actual charts in a real implementation
        charts_frame = ttk.Frame(dashboard_tab, style="Main.TFrame")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create placeholder for charts
        self.create_chart_placeholder(charts_frame, "Loan Applications by Type", 0, 0)
        self.create_chart_placeholder(charts_frame, "Monthly Application Volume", 0, 1)
        self.create_chart_placeholder(charts_frame, "Approval Rate by Loan Type", 1, 0)
        self.create_chart_placeholder(charts_frame, "Average Loan Amount", 1, 1)

    def create_stat_card(self, parent, title, value, column):
        """Create a statistics card for the dashboard"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.grid(row=0, column=column, padx=10, sticky=tk.NSEW)
        
        card_content = ttk.Frame(card, style="Card.TFrame")
        card_content.pack(padx=20, pady=15)
        
        # Card title
        ttk.Label(card_content, text=title, 
                 background="white", foreground="#666666").pack(anchor=tk.W)
        
        # Card value
        ttk.Label(card_content, text=value, 
                 font=("Helvetica", 24, "bold"), 
                 background="white").pack(anchor=tk.W, pady=5)
        
        # Configure column weights
        parent.columnconfigure(column, weight=1)

    def create_chart_placeholder(self, parent, title, row, column):
        """Create a placeholder for a chart"""
        chart_frame = ttk.Frame(parent, style="Card.TFrame")
        chart_frame.grid(row=row, column=column, padx=10, pady=10, sticky=tk.NSEW)
        
        # Chart title
        ttk.Label(chart_frame, text=title, 
                 font=self.section_font,
                 background="white").pack(anchor=tk.W, padx=15, pady=10)
        
        # Chart placeholder
        placeholder = ttk.Frame(chart_frame, height=200, style="Card.TFrame")
        placeholder.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Chart would be created here in a real implementation
        ttk.Label(placeholder, text="Chart visualization placeholder", 
                 background="white").pack(expand=True)
        
        # Configure grid weights
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(column, weight=1)

    def create_history_tab(self):
        """Create application history tab"""
        history_tab = ttk.Frame(self.notebook, style="Main.TFrame")
        self.notebook.add(history_tab, text="Application History")
        
        # History Header
        history_header = ttk.Frame(history_tab, style="Header.TFrame")
        history_header.pack(fill=tk.X)
        
        history_title = ttk.Label(history_header, text="Application History", style="Header.TLabel")
        history_title.pack(padx=20, pady=10)
        
        # Search and filter controls
        filter_frame = ttk.Frame(history_tab, style="Main.TFrame")
        filter_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 10))
        
        filter_var = tk.StringVar()
        filter_combo = ttk.Combobox(filter_frame, textvariable=filter_var, width=15, state="readonly")
        filter_combo['values'] = ('All', 'Approved', 'Pending', 'Denied')
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.set('All')
        
        ttk.Label(filter_frame, text="Date Range:").pack(side=tk.LEFT, padx=(20, 10))
        
        date_from = ttk.Entry(filter_frame, width=12)
        date_from.pack(side=tk.LEFT, padx=5)
        date_from.insert(0, "2024-01-01")
        
        ttk.Label(filter_frame, text="to").pack(side=tk.LEFT, padx=5)
        
        date_to = ttk.Entry(filter_frame, width=12)
        date_to.pack(side=tk.LEFT, padx=5)
        date_to.insert(0, "2024-04-15")
        
        search_btn = ttk.Button(filter_frame, text="Search")
        search_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        # Applications table
        table_frame = ttk.Frame(history_tab, style="Card.TFrame")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create treeview for history
        self.create_history_table(table_frame)

    def create_history_table(self, parent):
        """Create application history table"""
        # Add padding inside the card
        inner_frame = ttk.Frame(parent, style="Card.TFrame")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Table header
        header_frame = ttk.Frame(inner_frame, style="Card.TFrame")
        header_frame.pack(fill=tk.X)
        
        # Create the table with scrollbar
        table_container = ttk.Frame(inner_frame, style="Card.TFrame")
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_container)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(table_container, orient='horizontal')
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ('date', 'applicant', 'loan_type', 'amount', 'term', 'status')
        self.history_tree = ttk.Treeview(table_container, columns=columns, 
                                       show='headings', selectmode='browse',
                                       yscrollcommand=y_scrollbar.set,
                                       xscrollcommand=x_scrollbar.set)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.history_tree.yview)
        x_scrollbar.config(command=self.history_tree.xview)
        
        # Define headings
        self.history_tree.heading('date', text='Date')
        self.history_tree.heading('applicant', text='Applicant')
        self.history_tree.heading('loan_type', text='Loan Type')
        self.history_tree.heading('amount', text='Amount')
        self.history_tree.heading('term', text='Term')
        self.history_tree.heading('status', text='Status')
        
        # Define column widths and alignments
        self.history_tree.column('date', width=100, anchor='center')
        self.history_tree.column('applicant', width=150)
        self.history_tree.column('loan_type', width=120)
        self.history_tree.column('amount', width=100, anchor='e')
        self.history_tree.column('term', width=80, anchor='center')
        self.history_tree.column('status', width=100, anchor='center')
        
        # Pack the treeview
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add sample data
        sample_history = [
            ('2024-04-10', 'John Smith', 'Home Loan', '$250,000', '360 mo', 'Approved'),
            ('2024-03-22', 'Sarah Johnson', 'Car Loan', '$35,000', '60 mo', 'Approved'),
            ('2024-03-15', 'Michael Brown', 'Personal Loan', '$15,000', '36 mo', 'Denied'),
            ('2024-03-01', 'Emily Davis', 'Education Loan', '$50,000', '120 mo', 'Approved'),
            ('2024-02-18', 'Robert Wilson', 'Business Loan', '$100,000', '84 mo', 'Pending'),
            ('2024-02-10', 'Jennifer Taylor', 'Car Loan', '$28,500', '48 mo', 'Approved'),
            ('2024-01-25', 'Thomas Anderson', 'Home Loan', '$320,000', '360 mo', 'Approved'),
            ('2024-01-12', 'Lisa Martinez', 'Personal Loan', '$8,000', '24 mo', 'Denied'),
            ('2024-01-05', 'David Thompson', 'Business Loan', '$75,000', '60 mo', 'Approved')
        ]
        
        # Add sample data to the treeview
        for item in sample_history:
            self.history_tree.insert('', tk.END, values=item, tags=(item[5].lower(),))
        
        # Configure row tags for status colors
        self.history_tree.tag_configure('approved', background='#e6f7e6')  # Light green
        self.history_tree.tag_configure('denied', background='#f7e6e6')    # Light red
        self.history_tree.tag_configure('pending', background='#f7f7e6')   # Light yellow

    def initialize_loan_requirements(self):
        """Initialize loan requirements data"""
        self.loan_requirements = {
            'Home Loan': {
                'Minimum Requirements': [
                    'Income: $50,000+',
                    'Credit Score: 640+',
                    'Must be employed/self-employed',
                    'Loan Term: Up to 30 years',
                    'Down Payment: At least 3.5% of property value'
                ],
                'Preferred Criteria': [
                    'Income: $80,000+',
                    'Credit Score: 700+',
                    'Debt-to-Income Ratio: Below 36%',
                    'Down Payment: 20% or more'
                ],
                'Automatic Approval': [
                    'Credit Score: 800+',
                    'Income: $150,000+',
                    'Employment Status: Employed',
                    'Clean credit history for past 7 years',
                    'Down Payment: 20%+'
                ],
                'Automatic Rejection': [
                    'Credit Score below 500',
                    'Income below $25,000',
                    'Unemployed status',
                    'Recent bankruptcy or foreclosure'
                ]
            },
            'Education Loan': {
                'Minimum Requirements': [
                    'Income: $30,000+',
                    'Credit Score: 620+',
                    'All employment statuses accepted',
                    'Loan Term: Up to 15 years',
                    'Proof of enrollment in accredited institution'
                ],
                'Preferred Criteria': [
                    'Income: $50,000+',
                    'Credit Score: 680+',
                    'Co-signer with good credit history'
                ],
                'Automatic Approval': [
                    'Credit Score: 750+',
                    'Income: $100,000+',
                    'Employment Status: Employed',
                    'Co-signer with excellent credit'
                ],
                'Automatic Rejection': [
                    'Credit Score below 500',
                    'Previous student loan default'
                ]
            },
            'Car Loan': {
                'Minimum Requirements': [
                    'Income: $25,000+',
                    'Credit Score: 600+',
                    'Must be employed/self-employed',
                    'Loan Term: Up to 7 years',
                    'Down Payment: At least 10% for used cars'
                ],
                'Preferred Criteria': [
                    'Income: $40,000+',
                    'Credit Score: 660+',
                    'Down Payment: 20% or more'
                ],
                'Automatic Approval': [
                    'Credit Score: 750+',
                    'Income: $80,000+',
                    'Employment Status: Employed',
                    'Down Payment: 20%+'
                ],
                'Automatic Rejection': [
                    'Credit Score below 500',
                    'Unemployed status',
                    'Previous vehicle repossession'
                ]
            },
            'Personal Loan': {
                'Minimum Requirements': [
                    'Income: $30,000+',
                    'Credit Score: 630+',
                    'Must be employed/self-employed',
                    'Loan Term: Up to 5 years'
                ],
                'Preferred Criteria': [
                    'Income: $50,000+',
                    'Credit Score: 680+',
                    'Debt-to-Income Ratio: Below 40%'
                ],
                'Automatic Approval': [
                    'Credit Score: 750+',
                    'Income: $100,000+',
                    'Employment Status: Employed',
                    'Clean credit history for past 5 years'
                ],
                'Automatic Rejection': [
                    'Credit Score below 550',
                    'Income below $20,000',
                    'Unemployed status'
                ]
            },
            'Business Loan': {
                'Minimum Requirements': [
                    'Business Income: $100,000+',
                    'Credit Score: 650+',
                    'Business Age: At least 2 years',
                    'Loan Term: Up to 10 years'
                ],
                'Preferred Criteria': [
                    'Business Income: $250,000+',
                    'Credit Score: 700+',
                    'Business Age: 5+ years',
                    'Profitable for at least 2 years'
                ],
                'Automatic Approval': [
                    'Credit Score: 780+',
                    'Business Income: $500,000+',
                    'Business Age: 10+ years',
                    'Strong financial statements'
                ],
                'Automatic Rejection': [
                    'Credit Score below 600',
                    'Business Age: Less than 1 year',
                    'Negative cash flow'
                ]
            }
        }

    def update_requirements(self, event=None):
        """Update the requirements text based on selected loan type"""
        loan_type = self.loan_type_var.get()
        requirements = self.loan_requirements[loan_type]
        
        self.requirements_text.configure(state='normal')
        self.requirements_text.delete(1.0, tk.END)
        
        # Add loan type header
        self.requirements_text.insert(tk.END, f"{loan_type} Requirements\n\n", 'header')
        
        for category, items in requirements.items():
            self.requirements_text.insert(tk.END, f"{category}\n", 'category')
            for item in items:
                self.requirements_text.insert(tk.END, "• ", 'bullet')
                self.requirements_text.insert(tk.END, f"{item}\n", 'item')
            self.requirements_text.insert(tk.END, "\n")
        
        # Add some additional information
        self.requirements_text.insert(tk.END, "Note: Final loan approval is subject to additional verification and may include additional requirements based on individual circumstances.", 'note')
        
        self.requirements_text.configure(state='disabled')

    def validate_inputs(self):
        """Validate user inputs"""
        # Validate income
        try:
            income = float(self.income_var.get())
            if income <= 0:
                raise ValueError("Income must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid income amount")
            return False

        # Validate credit score
        try:
            credit_score = int(self.credit_var.get())
            if not (300 <= credit_score <= 850):
                raise ValueError("Credit score must be between 300 and 850")
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid credit score (300-850)")
            return False
            
        # Validate loan amount
        try:
            loan_amount = float(self.loan_amount_var.get())
            if loan_amount <= 0:
                raise ValueError("Loan amount must be positive")
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid loan amount")
            return False
            
        # Validate co-applicant income (if provided)
        if self.coapplicant_income_var.get():
            try:
                coapplicant_income = float(self.coapplicant_income_var.get())
                if coapplicant_income < 0:
                    raise ValueError("Co-applicant income cannot be negative")
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid co-applicant income amount")
                return False

        return True

    def predict_eligibility(self):
        """Make prediction based on user inputs"""
        if not self.validate_inputs():
            return
            
        try:
            income = float(self.income_var.get())
            credit_score = float(self.credit_var.get())
            loan_amount = float(self.loan_amount_var.get())
            loan_term = int(self.loan_term_var.get())
            
            # Handle optional co-applicant income
            coapplicant_income = 0
            if self.coapplicant_income_var.get():
                coapplicant_income = float(self.coapplicant_income_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all required fields")
            return

        # Create applicant data
        applicant_data = {
            'gender': self.gender_var.get(),
            'marital_status': self.marital_var.get(),
            'education': self.education_var.get(),
            'income': income,
            'coapplicant_income': coapplicant_income,
            'loan_amount': loan_amount,
            'loan_term': loan_term,
            'credit_score': credit_score,
            'credit_history': self.credit_history_var.get(),
            'property_area': self.property_area_var.get(),
            'employment_status': self.employment_var.get(),
            'loan_type': self.loan_type_var.get()
        }

        # Make prediction
        df = pd.DataFrame([applicant_data])
        predictions, probabilities = self.model.predict(df)
        
        # Show result frame
        self.result_frame.grid()
        
        # Update result labels
        result = predictions[0]
        probability = max(probabilities[0]) * 100
        
        # Update confidence progress bar and label
        self.confidence_var.set(int(probability))
        self.confidence_label.config(text=f"{probability:.1f}%")
        
        # Update eligibility status
        if result == "Eligible":
            self.eligibility_label.config(
                text="Status: Approved",
                style="Approved.TLabel"
            )
            self.result_title.config(text="Application Approved")
        else:
            self.eligibility_label.config(
                text="Status: Not Approved",
                style="Denied.TLabel"
            )
            self.result_title.config(text="Application Not Approved")
        
        # Add recommendation based on result
        if result == "Eligible":
            recommendation = "Congratulations! Based on the information provided, you are likely to be approved for this loan. Please proceed to the next steps to complete your application."
        else:
            # Generate specific recommendation based on applicant data
            if credit_score < 640:
                recommendation = "Your credit score appears to be below our minimum requirements. Consider improving your credit score before reapplying."
            elif income < 50000 and self.loan_type_var.get() == "Home Loan":
                recommendation = "Your income is below our recommended threshold for this loan type. Consider applying for a smaller loan amount or improving your income situation."
            elif self.employment_var.get() == "Unemployed" and self.loan_type_var.get() != "Education Loan":
                recommendation = "Employment status is a factor in your rejection. Most loans require stable employment."
            else:
                recommendation = "Based on the combination of factors, your application does not meet our current lending criteria. Consider improving your financial situation or exploring other loan options."
        
        self.recommendation_label.config(text=recommendation)
        
        # Scroll to show the result
        self.scrollable_frame.update_idletasks()
        self.result_frame.update_idletasks()

    def clear_form(self):
        """Clear all input fields and hide result"""
        self.gender_var.set("Male")
        self.marital_var.set("Single")
        self.education_var.set("Graduate")
        self.income_var.set("")
        self.coapplicant_income_var.set("")
        self.loan_amount_var.set("")
        self.loan_term_var.set("36")
        self.credit_var.set("")
        self.credit_history_var.set("Good (1+ year)")
        self.property_area_var.set("Urban")
        self.employment_var.set("Employed")
        self.loan_type_var.set("Home Loan")
        self.result_frame.grid_remove()
        self.update_requirements()

def main():
    # Use ThemedTk for better appearance if available
    if ThemedTk is not None:
        try:
            root = ThemedTk(theme="arc")
        except:
            # Fallback to standard Tk
            root = tk.Tk()
    else:
        # Fallback to standard Tk
        root = tk.Tk()
        
    app = LoanEligibilityGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()