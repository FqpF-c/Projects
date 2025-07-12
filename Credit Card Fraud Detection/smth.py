import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import os
import random
import requests
import json

class GeminiFraudDetection:
    def __init__(self, root):
        self.root = root
        self.root.title("Safe Transaction Monitor - Credit Card Fraud Detection")
        self.root.geometry("950x650")
        self.root.configure(bg="#f5f5f5")
        
        # Set application style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), background='#4CAF50')
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'))
        
        # Gemini API Key
        self.gemini_api_key = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"
        
        # Create main notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.welcome_tab = ttk.Frame(self.notebook)
        self.generate_tab = ttk.Frame(self.notebook)
        self.check_tab = ttk.Frame(self.notebook)
        self.help_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.welcome_tab, text="Welcome")
        self.notebook.add(self.generate_tab, text="Create Data")
        self.notebook.add(self.check_tab, text="Check Transaction")
        self.notebook.add(self.help_tab, text="Help & Guide")
        
        # Set up each tab
        self.setup_welcome_tab()
        self.setup_generate_tab()
        self.setup_check_tab()
        self.setup_help_tab()
        
    def setup_welcome_tab(self):
        # Welcome header
        header_frame = ttk.Frame(self.welcome_tab)
        header_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(header_frame, text="Safe Transaction Monitor", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="A simple tool to help you understand and detect unusual card transactions", 
                  font=('Arial', 12)).pack(pady=5)
        
        # Quick start guide
        guide_frame = ttk.LabelFrame(self.welcome_tab, text="Quick Start Guide")
        guide_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        steps = [
            ("1. Create Sample Data", "Generate sample transaction data to work with"),
            ("2. Check Transactions", "Analyze specific transactions to see if they look suspicious")
        ]
        
        for i, (title, desc) in enumerate(steps):
            step_frame = ttk.Frame(guide_frame)
            step_frame.pack(fill=tk.X, pady=10, padx=10)
            
            ttk.Label(step_frame, text=title, font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(step_frame, text=desc).grid(row=1, column=0, sticky=tk.W, padx=20)
            
            btn_text = "Start" if i == 0 else "Go to Step"
            ttk.Button(step_frame, text=btn_text, 
                      command=lambda tab=i+1: self.notebook.select(tab)).grid(row=0, column=1, rowspan=2, padx=10)
        
        # What is fraud detection section
        info_frame = ttk.LabelFrame(self.welcome_tab, text="What is Transaction Fraud Detection?")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = """Transaction fraud detection helps protect your finances by looking for unusual patterns.

Just like you might notice if someone else used your card for a strange purchase, 
this tool helps spot potentially suspicious activity by using Gemini AI to analyze transaction patterns.

Using this tool, you can:
• Generate realistic sample transaction data
• Check if specific transactions appear unusual
• Get easy-to-understand explanations of the results
• Receive AI-powered insights about potential fraud"""
        
        ttk.Label(info_frame, text=info_text, wraplength=600, justify=tk.LEFT).pack(pady=10, padx=10)
    
    def setup_generate_tab(self):
        # Header
        ttk.Label(self.generate_tab, text="Create Sample Transaction Data", 
                 style="Header.TLabel").pack(pady=10)
        ttk.Label(self.generate_tab, text="Generate realistic credit card transactions to work with").pack()
        
        # Main content frame
        content_frame = ttk.Frame(self.generate_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Parameters
        params_frame = ttk.LabelFrame(content_frame, text="Data Settings")
        params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Number of transactions
        ttk.Label(params_frame, text="Number of Transactions:").grid(column=0, row=0, sticky=tk.W, pady=5, padx=5)
        self.num_transactions = tk.IntVar(value=1000)
        transaction_scale = ttk.Scale(params_frame, from_=100, to=10000, 
                                     orient=tk.HORIZONTAL, variable=self.num_transactions,
                                     length=200, command=lambda v: self.update_scale_label())
        transaction_scale.grid(column=1, row=0, sticky=tk.W, pady=5)
        self.transaction_label = ttk.Label(params_frame, text="1,000")
        self.transaction_label.grid(column=2, row=0, sticky=tk.W, pady=5, padx=5)
        
        # Fraud percentage
        ttk.Label(params_frame, text="Unusual Transaction %:").grid(column=0, row=1, sticky=tk.W, pady=5, padx=5)
        self.fraud_percent = tk.DoubleVar(value=1.0)
        fraud_scale = ttk.Scale(params_frame, from_=0.1, to=10.0, 
                              orient=tk.HORIZONTAL, variable=self.fraud_percent,
                              length=200, command=lambda v: self.update_scale_label())
        fraud_scale.grid(column=1, row=1, sticky=tk.W, pady=5)
        self.fraud_label = ttk.Label(params_frame, text="1.0%")
        self.fraud_label.grid(column=2, row=1, sticky=tk.W, pady=5, padx=5)
        
        # Common spending categories
        ttk.Label(params_frame, text="Common Spending Categories:").grid(column=0, row=2, sticky=tk.W, pady=5, padx=5)
        self.categories_var = tk.StringVar(value="Groceries,Restaurants,Gas,Online Shopping,Utilities")
        categories_entry = ttk.Entry(params_frame, textvariable=self.categories_var, width=40)
        categories_entry.grid(column=1, row=2, columnspan=2, sticky=tk.W, pady=5, padx=5)
        
        # File settings
        ttk.Label(params_frame, text="Save Location:").grid(column=0, row=3, sticky=tk.W, pady=5, padx=5)
        self.save_path = tk.StringVar(value=os.path.join(os.getcwd(), "transaction_data.csv"))
        path_entry = ttk.Entry(params_frame, textvariable=self.save_path, width=40)
        path_entry.grid(column=1, row=3, columnspan=2, sticky=tk.W, pady=5, padx=5)
        
        browse_btn = ttk.Button(params_frame, text="Browse", command=self.browse_save_location)
        browse_btn.grid(column=3, row=3, pady=5, padx=5)
        
        # Generate button with progress
        generate_frame = ttk.Frame(params_frame)
        generate_frame.grid(column=0, row=4, columnspan=4, pady=20, padx=5)
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate Transaction Data", 
                                      command=self.generate_data)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(generate_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        # Right side - Preview
        preview_frame = ttk.LabelFrame(content_frame, text="Data Preview")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sample data visualization
        self.preview_canvas_frame = ttk.Frame(preview_frame)
        self.preview_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initial empty preview
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.text(0.5, 0.5, "Generate data to see preview", 
                ha='center', va='center', fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        self.preview_canvas = FigureCanvasTkAgg(fig, master=self.preview_canvas_frame)
        self.preview_canvas.draw()
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Status messages
        self.generate_status = tk.StringVar(value="Ready to generate transaction data")
        status_label = ttk.Label(preview_frame, textvariable=self.generate_status)
        status_label.pack(pady=5)
        
        # Update the scale labels initially
        self.update_scale_label()
        
    def setup_check_tab(self):
        # Header
        ttk.Label(self.check_tab, text="Check Individual Transactions", 
                 style="Header.TLabel").pack(pady=10)
        ttk.Label(self.check_tab, text="Check if specific transactions appear unusual using Gemini AI").pack()
        
        # Main content
        content_frame = ttk.Frame(self.check_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Transaction input
        input_frame = ttk.LabelFrame(content_frame, text="Transaction Details")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Transaction details inputs
        details_frame = ttk.Frame(input_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Define dropdown options
        self.categories = ["Groceries", "Restaurants", "Gas", "Online Shopping", "Utilities", 
                           "Electronics", "Travel", "Entertainment", "Jewelry", "Luxury Goods"]
        self.locations = ["Local", "Online", "Nearby City", "Different State", "International"]
        self.times = ["Morning", "Afternoon", "Evening", "Late Night"]
        self.days = ["Weekday", "Weekend", "Holiday"]
        
        # Common transaction details
        fields = [
            ("Transaction Amount ($):", "amount", 100, None),
            ("Merchant Category:", "category", "Restaurants", self.categories),
            ("Transaction Location:", "location", "Local", self.locations),
            ("Time of Day:", "time", "Evening", self.times),
            ("Day of Week:", "day", "Weekday", self.days)
        ]
        
        self.transaction_inputs = {}
        
        for i, (label_text, field_name, default_value, options) in enumerate(fields):
            ttk.Label(details_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if options is None:  # This is a numeric field
                var = tk.DoubleVar(value=default_value)
                widget = ttk.Entry(details_frame, width=20)
                widget.insert(0, str(default_value))
            else:  # This is a dropdown field
                var = tk.StringVar(value=default_value)
                widget = ttk.Combobox(details_frame, textvariable=var, values=options, width=18, state="readonly")
            
            widget.grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            self.transaction_inputs[field_name] = widget
        
        # Transaction history
        history_frame = ttk.LabelFrame(input_frame, text="User Transaction History")
        history_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(history_frame, text="Usual Transaction Locations:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.usual_locations = tk.StringVar(value="Local,Online,Nearby City")
        ttk.Entry(history_frame, textvariable=self.usual_locations, width=30).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(history_frame, text="Usual Merchant Categories:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.usual_categories = tk.StringVar(value="Groceries,Restaurants,Gas")
        ttk.Entry(history_frame, textvariable=self.usual_categories, width=30).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(history_frame, text="Recent Transactions (last hour):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.recent_count = tk.IntVar(value=0)
        ttk.Spinbox(history_frame, from_=0, to=10, textvariable=self.recent_count, width=5).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(history_frame, text="Average Transaction Amount:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.avg_amount = tk.DoubleVar(value=50)
        ttk.Entry(history_frame, textvariable=self.avg_amount, width=10).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Additional context
        context_frame = ttk.LabelFrame(input_frame, text="Additional Context (Optional)")
        context_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(context_frame, text="Add any other relevant details:").pack(anchor=tk.W, pady=5)
        self.additional_context = tk.Text(context_frame, height=4, width=40)
        self.additional_context.pack(fill=tk.X, padx=5, pady=5)
        
        # Check transaction button
        check_frame = ttk.Frame(input_frame)
        check_frame.pack(fill=tk.X, pady=20, padx=10)
        
        self.check_btn = ttk.Button(check_frame, text="Check This Transaction", 
                                   command=self.check_transaction)
        self.check_btn.pack()
        
        # Right panel - Results display
        results_frame = ttk.LabelFrame(content_frame, text="AI Transaction Analysis")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results display area with initial message
        self.result_display = ttk.Frame(results_frame)
        self.result_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.initial_result_msg = ttk.Label(self.result_display, 
                                          text="Enter transaction details and click 'Check This Transaction' to analyze", 
                                          wraplength=300)
        self.initial_result_msg.pack(pady=50)
        
        # Add loading indicator (initially hidden)
        self.loading_label = ttk.Label(self.result_display, text="Analyzing transaction...", font=('Arial', 12))
        self.loading_progress = ttk.Progressbar(self.result_display, orient='horizontal', mode='indeterminate', length=200)
    
    def setup_help_tab(self):
        # Header
        ttk.Label(self.help_tab, text="Help & User Guide", 
                 style="Header.TLabel").pack(pady=10)
        
        # Create a scrollable frame
        main_frame = ttk.Frame(self.help_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Help content sections
        sections = [
            {
                "title": "Understanding Credit Card Fraud",
                "content": """Credit card fraud happens when someone uses your card details without permission. 
This tool helps you understand what unusual transactions might look like.

Common signs of suspicious transactions:
• Unusual locations
• Unusually large amounts
• Multiple transactions in a short time
• Purchases from categories you don't normally use""",
            },
            {
                "title": "How This Tool Uses AI",
                "content": """This tool uses Gemini 2.0 Flash, a powerful AI model from Google, to analyze transactions.

The AI evaluates:
• The transaction details you provide
• Your typical spending patterns
• Common fraud patterns and red flags

It then provides an analysis of whether the transaction appears normal or suspicious, along with an explanation of its reasoning.""",
            },
            {
                "title": "How to Use This Tool",
                "content": """1. Create Sample Data: Generate realistic transaction data to work with (optional)
2. Check Transactions: Enter a transaction's details and your typical spending patterns
3. Review AI Analysis: See Gemini's assessment of the transaction risk

The system will analyze the transaction and explain why it might be suspicious or normal.""",
            },
            {
                "title": "Understanding the Results",
                "content": """When the AI checks a transaction, it will tell you:

• If the transaction looks normal or suspicious
• The confidence level (how sure the AI is)
• Why the transaction might be suspicious
• Suggested actions based on the risk level

Remember: This is just a tool to help spot potentially unusual patterns. 
A flagged transaction isn't definitely fraud, and the system might miss some fraudulent transactions.""",
            },
            {
                "title": "Frequently Asked Questions",
                "content": """Q: Will this work with my real credit card data?
A: Yes, you can enter details from your real transactions to check them.

Q: How accurate is this system?
A: The Gemini AI model is quite sophisticated and can identify many fraud patterns, but it's not perfect.

Q: Can I use this to protect my actual cards?
A: This is an educational tool. For real protection, use your bank's fraud monitoring services.""",
            }
        ]
        
        for i, section in enumerate(sections):
            section_frame = ttk.LabelFrame(scrollable_frame, text=section["title"])
            section_frame.pack(fill=tk.X, expand=True, pady=10)
            
            content_label = ttk.Label(section_frame, text=section["content"], 
                                     wraplength=800, justify=tk.LEFT)
            content_label.pack(padx=10, pady=10)
    
    def update_scale_label(self):
        # Update transaction count label
        self.transaction_label.config(text=f"{self.num_transactions.get():,}")
        # Update fraud percentage label
        self.fraud_label.config(text=f"{self.fraud_percent.get():.1f}%")
    
    def browse_save_location(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.getcwd(),
            title="Save Transaction Data As"
        )
        if filename:
            self.save_path.set(filename)
    
    def generate_data(self):
        """Generate transaction data with user-friendly features"""
        try:
            # Get parameters
            num_transactions = self.num_transactions.get()
            fraud_ratio = self.fraud_percent.get() / 100
            save_path = self.save_path.get()
            categories = self.categories_var.get().split(',')
            
            # Update status and disable button
            self.generate_status.set("Generating transaction data...")
            self.generate_btn.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            self.root.update()
            
            # Create data generator and run in small batches to update progress
            data = self.generate_transaction_data(num_transactions, fraud_ratio, categories, save_path)
            
            # Create preview visualizations
            self.create_data_preview(data)
            
            # Update status
            self.generate_status.set(f"Successfully created {num_transactions} transactions ({fraud_ratio*100:.1f}% unusual)")
            self.progress_bar['value'] = 100
            
            # Re-enable button
            self.generate_btn.config(state=tk.NORMAL)
            
            # Suggest next step
            messagebox.showinfo("Success", 
                               f"Transaction data created successfully!\n\nNext step: Go to 'Check Transaction' tab to analyze transactions.")
            
        except Exception as e:
            self.generate_status.set(f"Error: {str(e)}")
            self.generate_btn.config(state=tk.NORMAL)
            messagebox.showerror("Error", f"Failed to generate data: {str(e)}")
    
    def generate_transaction_data(self, num_transactions, fraud_ratio, categories, save_path):
        """Generate user-friendly transaction data with improved logic"""
        # Calculate normal and fraudulent counts
        num_fraud = int(num_transactions * fraud_ratio)
        num_normal = num_transactions - num_fraud
        
        # Progress increment
        progress_step = 100 / num_transactions
        progress = 0
        
        # Create dataframe columns
        columns = [
            'Amount', 'Category', 'DayType', 'TimeOfDay', 'Location', 
            'MerchantType', 'PrevActivity', 'FrequencyLevel', 'IsUnusual'
        ]
        
        data = []
        
        # Location types
        locations = ['Local', 'Online', 'Nearby City', 'Different State', 'International']
        location_weights_normal = [0.4, 0.3, 0.2, 0.08, 0.02]
        location_weights_fraud = [0.1, 0.2, 0.1, 0.3, 0.3]
        
        # Merchant types
        merchant_types = ['Retail Store', 'Restaurant', 'Online Shop', 'Gas Station', 
                         'Supermarket', 'Service Provider', 'ATM', 'Unknown']
        merchant_weights_normal = [0.2, 0.25, 0.15, 0.15, 0.15, 0.07, 0.03, 0.0]
        merchant_weights_fraud = [0.1, 0.05, 0.3, 0.05, 0.05, 0.05, 0.1, 0.3]
        
        # Day types
        day_types = ['Weekday', 'Weekend', 'Holiday']
        day_weights_normal = [0.7, 0.25, 0.05]
        day_weights_fraud = [0.3, 0.3, 0.4]
        
        # Time of day
        times = ['Morning', 'Afternoon', 'Evening', 'Late Night']
        time_weights_normal = [0.25, 0.35, 0.35, 0.05]
        time_weights_fraud = [0.1, 0.2, 0.3, 0.4]
        
        # Previous activity levels
        prev_activity = ['Low', 'Medium', 'High']
        
        # Frequency levels
        frequency = ['Rare', 'Occasional', 'Frequent']
        
        # Generate normal transactions
        for i in range(num_normal):
            # Amount - normal distribution around typical amounts
            amount = max(0.1, np.random.choice([
                np.random.normal(10, 5),    # Small transactions
                np.random.normal(50, 20),   # Medium transactions
                np.random.normal(200, 50),  # Larger transactions
            ], p=[0.3, 0.5, 0.2]))
            
            # Category
            category = np.random.choice(categories)
            
            # Location
            location = np.random.choice(locations, p=location_weights_normal)
            
            # Merchant type
            merchant = np.random.choice(merchant_types, p=merchant_weights_normal)
            
            # Day type
            day_type = np.random.choice(day_types, p=day_weights_normal)
            
            # Time of day
            time_of_day = np.random.choice(times, p=time_weights_normal)
            
            # Previous activity
            prev = np.random.choice(prev_activity, p=[0.2, 0.6, 0.2])
            
            # Frequency
            freq = np.random.choice(frequency, p=[0.2, 0.5, 0.3])
            
            # Create row and add to data
            row = [amount, category, day_type, time_of_day, location, 
                  merchant, prev, freq, 0]  # 0 = normal
            data.append(row)
            
            # Update progress
            progress += progress_step
            if i % 50 == 0:
                self.progress_bar['value'] = progress
                self.root.update()
        
        # Generate unusual/fraudulent transactions
        for i in range(num_fraud):
            # Amount - different distribution
            amount = max(0.1, np.random.choice([
                np.random.normal(5, 2),       # Very small test transactions
                np.random.normal(1000, 500),  # Large transactions
                np.random.normal(3000, 1000), # Very large transactions
            ], p=[0.2, 0.5, 0.3]))
            
            # Category - possibly something unusual for the user
            if random.random() < 0.7:  # 70% chance of unusual category
                all_possible = ['Jewelry', 'Electronics', 'Gaming', 'Travel', 
                               'Entertainment', 'Luxury Goods', 'Donations']
                category = np.random.choice([c for c in all_possible if c not in categories])
            else:
                category = np.random.choice(categories)
            
            # Location
            location = np.random.choice(locations, p=location_weights_fraud)
            
            # Merchant type
            merchant = np.random.choice(merchant_types, p=merchant_weights_fraud)
            
            # Day type
            day_type = np.random.choice(day_types, p=day_weights_fraud)
            
            # Time of day
            time_of_day = np.random.choice(times, p=time_weights_fraud)
            
            # Previous activity
            prev = np.random.choice(prev_activity, p=[0.6, 0.3, 0.1])
            
            # Frequency
            freq = np.random.choice(frequency, p=[0.7, 0.2, 0.1])
            
            # Create row and add to data
            row = [amount, category, day_type, time_of_day, location, 
                  merchant, prev, freq, 1]  # 1 = unusual
            data.append(row)
            
            # Update progress
            progress += progress_step
            if i % 10 == 0:
                self.progress_bar['value'] = progress
                self.root.update()
        
        # Convert to DataFrame and shuffle
        df = pd.DataFrame(data, columns=columns)
        df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
        
        # Save to CSV
        df.to_csv(save_path, index=False)
        
        return df
    
    def create_data_preview(self, data):
        """Create visualizations for the data preview"""
        # Clear the previous visualization
        for widget in self.preview_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 1, figsize=(5, 7))
        
        # Top plot: Transaction amounts by type
        normal = data[data['IsUnusual'] == 0]['Amount']
        unusual = data[data['IsUnusual'] == 1]['Amount']
        
        # Create box plot
        ax = axes[0]
        ax.boxplot([normal, unusual], labels=['Normal', 'Unusual'])
        ax.set_title('Transaction Amounts')
        ax.set_ylabel('Amount ($)')
        
        # Bottom plot: Transaction counts by category
        ax = axes[1]
        category_counts = data.groupby(['Category', 'IsUnusual']).size().unstack(fill_value=0)
        category_counts.plot(kind='bar', ax=ax)
        ax.set_title('Transactions by Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Count')
        ax.legend(['Normal', 'Unusual'])
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Create canvas and add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.preview_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def check_transaction(self):
        """Check an individual transaction for fraud using Gemini API"""
        try:
            # Clear previous results
            for widget in self.result_display.winfo_children():
                widget.destroy()
            
            # Create and show loading indicator
            loading_frame = ttk.Frame(self.result_display)
            loading_frame.pack(fill=tk.X, pady=10)
            
            loading_label = ttk.Label(loading_frame, text="Analyzing transaction...", font=('Arial', 12))
            loading_label.pack(pady=10)
            
            loading_progress = ttk.Progressbar(loading_frame, orient='horizontal', mode='indeterminate', length=200)
            loading_progress.pack(pady=10)
            loading_progress.start(10)
            
            self.check_btn.config(state=tk.DISABLED)
            self.root.update()
            
            # Get transaction inputs
            amount = float(self.transaction_inputs['amount'].get())
            
            # For combobox inputs, we need to use the get() method of the StringVar
            if isinstance(self.transaction_inputs['category'], ttk.Combobox):
                category = self.transaction_inputs['category'].get()
                location = self.transaction_inputs['location'].get()
                time = self.transaction_inputs['time'].get()
                day = self.transaction_inputs['day'].get()
            else:
                # Fallback for text entries if needed
                category = self.transaction_inputs['category'].get()
                location = self.transaction_inputs['location'].get()
                time = self.transaction_inputs['time'].get()
                day = self.transaction_inputs['day'].get()
            
            # Get user history
            usual_locations = self.usual_locations.get().split(',')
            usual_categories = self.usual_categories.get().split(',')
            recent_count = self.recent_count.get()
            avg_amount = self.avg_amount.get()
            
            # Get additional context
            additional_context = self.additional_context.get("1.0", tk.END).strip()
            
            # Create the prompt for Gemini API
            prompt = self.create_gemini_prompt(
                amount, category, location, time, day,
                usual_locations, usual_categories, recent_count, avg_amount,
                additional_context
            )
            
            # Call Gemini API
            response = self.call_gemini_api(prompt)
            
            # Hide loading indicator
            loading_frame.destroy()
            self.check_btn.config(state=tk.NORMAL)
            
            # Display result
            self.display_gemini_result(response)
            
        except Exception as e:
            # Show error in result area
            for widget in self.result_display.winfo_children():
                widget.destroy()
            
            # Clean up any loading indicators if they exist
            for widget in self.result_display.winfo_children():
                if isinstance(widget, ttk.Frame) and "loading" in str(widget):
                    widget.destroy()
            
            # Re-enable check button
            self.check_btn.config(state=tk.NORMAL)
            
            # Display error message
            error_frame = ttk.Frame(self.result_display)
            error_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ttk.Label(error_frame, text="Error checking transaction:", 
                    font=('Arial', 12, 'bold')).pack(anchor=tk.W)
            ttk.Label(error_frame, text=str(e), wraplength=400).pack(anchor=tk.W, pady=5)
    
    def create_gemini_prompt(self, amount, category, location, time, day, 
                           usual_locations, usual_categories, recent_count, avg_amount,
                           additional_context):
        """Create a structured prompt for Gemini API"""
        
        # Create more nuanced prompt to improve classification accuracy
        prompt = f"""As a credit card fraud detection system, analyze this transaction for suspicious activity.

TRANSACTION DETAILS:
- Amount: ${amount:.2f}
- Merchant Category: {category}
- Location: {location}
- Time of Day: {time}
- Day Type: {day}
- Recent Transaction Count (last hour): {recent_count}

USER HISTORY:
- Usual Transaction Locations: {', '.join(usual_locations)}
- Usual Merchant Categories: {', '.join(usual_categories)}
- Average Transaction Amount: ${avg_amount:.2f}

"""
        
        if additional_context:
            prompt += f"ADDITIONAL CONTEXT:\n{additional_context}\n\n"
            
        prompt += """ANALYSIS INSTRUCTIONS:
1. Evaluate if this transaction appears normal or suspicious based on the provided details.
2. Consider these factors when determining risk:
   - Is the location outside usual patterns?
   - Is the amount significantly higher than average?
   - Is the category unusual for this user?
   - Is the timing (time of day, day type) suspicious?
   - Are there multiple recent transactions?
3. Assign a risk level (Low, Medium, or High) based on your analysis.
4. Provide a fraud probability percentage (0-100%) that reflects your confidence.
5. List specific suspicious patterns if any are detected.
6. Recommend appropriate actions based on the risk level.

NOT ALL TRANSACTIONS ARE FRAUDULENT. Many legitimate transactions may have one unusual characteristic but are still normal. Only classify as suspicious if multiple risk factors are present.

Format your response with clear sections:
- TRANSACTION ASSESSMENT: [Normal/Suspicious]
- RISK LEVEL: [Low/Medium/High]
- FRAUD PROBABILITY: [X%]
- SUSPICIOUS PATTERNS: [List if any, or "None detected"]
- RECOMMENDED ACTIONS: [List of suggested actions]
- EXPLANATION: [Detailed reasoning for your assessment]

Make your analysis practical and easy to understand for non-technical users."""
        
        return prompt
    
    def call_gemini_api(self, prompt):
        """Call the Gemini API with the given prompt"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 32,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def display_gemini_result(self, response):
        """Display the results from Gemini API with improved parsing"""
        try:
            # Extract text from response
            ai_text = response['candidates'][0]['content']['parts'][0]['text']
            
            # Parse the structured response
            assessment = "Unknown"
            risk_level = "Unknown"
            probability = "Unknown"
            patterns = []
            actions = []
            explanation = ""
            
            # More robust parsing based on section headers
            sections = ai_text.split('\n\n')
            current_section = None
            
            for section in sections:
                if "TRANSACTION ASSESSMENT:" in section:
                    assessment = section.split(":", 1)[1].strip()
                    current_section = "assessment"
                elif "RISK LEVEL:" in section:
                    risk_level = section.split(":", 1)[1].strip()
                    current_section = "risk"
                elif "FRAUD PROBABILITY:" in section:
                    probability = section.split(":", 1)[1].strip()
                    current_section = "probability"
                elif "SUSPICIOUS PATTERNS:" in section:
                    patterns_text = section.split(":", 1)[1].strip()
                    current_section = "patterns"
                    if patterns_text.lower() != "none detected" and patterns_text.lower() != "none":
                        pattern_lines = patterns_text.split("\n")
                        for line in pattern_lines:
                            clean_line = line.strip()
                            if clean_line and (clean_line.startswith("-") or clean_line.startswith("•")):
                                patterns.append(clean_line[1:].strip())
                            elif clean_line and not clean_line.lower().startswith("none"):
                                patterns.append(clean_line)
                elif "RECOMMENDED ACTIONS:" in section:
                    actions_text = section.split(":", 1)[1].strip()
                    current_section = "actions"
                    action_lines = actions_text.split("\n")
                    for line in action_lines:
                        clean_line = line.strip()
                        if clean_line and (clean_line.startswith("-") or clean_line.startswith("•")):
                            actions.append(clean_line[1:].strip())
                        elif clean_line:
                            actions.append(clean_line)
                elif "EXPLANATION:" in section:
                    explanation = section.split(":", 1)[1].strip()
                    current_section = "explanation"
                elif current_section == "patterns" and patterns_text.lower() != "none detected":
                    pattern_lines = section.split("\n")
                    for line in pattern_lines:
                        clean_line = line.strip()
                        if clean_line and (clean_line.startswith("-") or clean_line.startswith("•")):
                            patterns.append(clean_line[1:].strip())
                        elif clean_line and not clean_line.lower().startswith("none"):
                            patterns.append(clean_line)
                elif current_section == "actions":
                    action_lines = section.split("\n")
                    for line in action_lines:
                        clean_line = line.strip()
                        if clean_line and (clean_line.startswith("-") or clean_line.startswith("•")):
                            actions.append(clean_line[1:].strip())
                        elif clean_line:
                            actions.append(clean_line)
                elif current_section == "explanation":
                    explanation += "\n\n" + section
            
            # Remove duplicates
            if patterns:
                patterns = list(dict.fromkeys(patterns))
            if actions:
                actions = list(dict.fromkeys(actions))
            
            # Determine color based on risk level
            if risk_level.lower() == "low":
                color = "#4CAF50"  # Green
            elif risk_level.lower() == "medium":
                color = "#FF9800"  # Orange
            else:
                color = "#F44336"  # Red
            
            # Create result display
            result_frame = ttk.Frame(self.result_display)
            result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Header with result
            header_frame = ttk.Frame(result_frame)
            header_frame.pack(fill=tk.X, pady=10)
            
            result_label = ttk.Label(
                header_frame, 
                text=f"{assessment.upper()} TRANSACTION",
                font=('Arial', 16, 'bold'))
            result_label.pack(side=tk.LEFT, padx=5)
            
            # Create colored risk indicator
            risk_frame = ttk.Frame(header_frame)
            risk_frame.pack(side=tk.RIGHT, padx=5)
            
            risk_canvas = tk.Canvas(risk_frame, width=100, height=30, bg=color, highlightthickness=0)
            risk_canvas.create_text(50, 15, text=f"{risk_level} Risk", fill="white", font=('Arial', 10, 'bold'))
            risk_canvas.pack()
            
            # Probability gauge
            gauge_frame = ttk.Frame(result_frame)
            gauge_frame.pack(fill=tk.X, pady=10)
            
            ttk.Label(gauge_frame, text="Fraud Probability:").pack(anchor=tk.W)
            
            # Extract just the percentage number
            try:
                prob_number = float(probability.rstrip('%').strip())
            except:
                prob_number = 0  # Default if parsing fails
            
            # Create gauge canvas
            gauge_canvas = tk.Canvas(gauge_frame, width=400, height=30, bg='#E0E0E0', highlightthickness=0)
            gauge_canvas.pack(fill=tk.X, pady=5)
            
            # Draw gauge
            gauge_width = min(400 * (prob_number / 100), 400)
            gauge_canvas.create_rectangle(0, 0, gauge_width, 30, fill=color, outline="")
            gauge_canvas.create_text(gauge_width/2 if gauge_width > 50 else 20, 15, 
                                    text=probability, fill="white" if gauge_width > 50 else "black", 
                                    font=('Arial', 10, 'bold'))
            
            # Add suspicious patterns section
            if patterns:
                patterns_frame = ttk.LabelFrame(result_frame, text="Suspicious Patterns Detected")
                patterns_frame.pack(fill=tk.X, pady=10)
                
                for pattern in patterns:
                    pattern_frame = ttk.Frame(patterns_frame)
                    pattern_frame.pack(fill=tk.X, pady=2)
                    
                    # Clean up pattern text (remove leading dashes or bullets)
                    pattern_text = pattern
                    if pattern.startswith("-") or pattern.startswith("•"):
                        pattern_text = pattern[1:].strip()
                    
                    ttk.Label(pattern_frame, text="•", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
                    ttk.Label(pattern_frame, text=pattern_text, wraplength=350).pack(side=tk.LEFT, pady=2)
            
            # Add recommended actions section
            if actions:
                actions_frame = ttk.LabelFrame(result_frame, text="Recommended Actions")
                actions_frame.pack(fill=tk.X, pady=10)
                
                for action in actions:
                    action_frame = ttk.Frame(actions_frame)
                    action_frame.pack(fill=tk.X, pady=2)
                    
                    # Clean up action text (remove leading dashes or bullets)
                    action_text = action
                    if action.startswith("-") or action.startswith("•"):
                        action_text = action[1:].strip()
                    
                    ttk.Label(action_frame, text="✓", font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
                    ttk.Label(action_frame, text=action_text, wraplength=350).pack(side=tk.LEFT, pady=2)
            
            # Add explanation section
            if explanation:
                explain_frame = ttk.LabelFrame(result_frame, text="Detailed Explanation")
                explain_frame.pack(fill=tk.X, pady=10)
                
                explanation_text = tk.Text(explain_frame, height=8, width=40, wrap=tk.WORD)
                explanation_text.pack(fill=tk.BOTH, padx=5, pady=5)
                explanation_text.insert(tk.END, explanation)
                explanation_text.config(state=tk.DISABLED)
                
                # Add scrollbar if needed
                scrollbar = ttk.Scrollbar(explain_frame, command=explanation_text.yview)
                explanation_text.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
        except Exception as e:
            # If parsing fails, just display the raw response
            result_frame = ttk.Frame(self.result_display)
            result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ttk.Label(result_frame, text="AI Analysis Result:", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W)
            
            result_text = tk.Text(result_frame, height=20, width=50, wrap=tk.WORD)
            result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            try:
                result_text.insert(tk.END, response['candidates'][0]['content']['parts'][0]['text'])
            except:
                result_text.insert(tk.END, f"Error parsing response: {str(e)}\n\nRaw response: {str(response)}")
            
            result_text.config(state=tk.DISABLED)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(result_frame, command=result_text.yview)
            result_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def main():
    root = tk.Tk()
    app = GeminiFraudDetection(root)
    root.mainloop()

if __name__ == "__main__":
    main()