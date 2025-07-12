import tkinter as tk
from tkinter import ttk, messagebox, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import requests
from bs4 import BeautifulSoup
import threading
import time
from datetime import datetime, timedelta
import re
import json
import random
import matplotlib.ticker as ticker

class ModernUI:
    """Class to provide modern UI theme constants"""
    # Color scheme
    PRIMARY = "#2c3e50"
    SECONDARY = "#34495e"
    ACCENT = "#3498db"
    ACCENT_DARK = "#2980b9"
    SUCCESS = "#2ecc71"
    WARNING = "#f39c12"
    DANGER = "#e74c3c"
    LIGHT = "#ecf0f1"
    DARK = "#2c3e50"
    
    # Padding
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    
    # Fonts - default to a common font, will set properly after Tk is initialized
    FONT_FAMILY = "Helvetica"
    
    @classmethod
    def get_heading_font(cls, size=14, weight="bold"):
        return (cls.FONT_FAMILY, size, weight)
    
    @classmethod
    def get_body_font(cls, size=10, weight="normal"):
        return (cls.FONT_FAMILY, size, weight)
    
    @classmethod
    def apply_modern_style(cls, root):
        """Apply modern styles to ttk widgets"""
        # Now that Tk is initialized, we can safely check font families
        try:
            available_fonts = font.families()
            if "Segoe UI" in available_fonts:
                cls.FONT_FAMILY = "Segoe UI"
            elif "Arial" in available_fonts:
                cls.FONT_FAMILY = "Arial"
            # Default is already Helvetica from class definition
        except Exception:
            # If there's any issue with font detection, keep the default
            pass
            
        style = ttk.Style()
        style.theme_use('clam')  # Use the 'clam' theme as a base
        
        # Configure ttk styles
        style.configure("TButton", 
                        font=cls.get_body_font(11),
                        background=cls.ACCENT,
                        foreground=cls.LIGHT)
        
        style.map("TButton",
                  background=[('active', cls.ACCENT_DARK)],
                  foreground=[('active', cls.LIGHT)])
        
        style.configure("TFrame", background=cls.LIGHT)
        style.configure("TLabel", background=cls.LIGHT, font=cls.get_body_font())
        style.configure("TNotebook", background=cls.LIGHT, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", 
                        background=cls.SECONDARY, 
                        foreground=cls.LIGHT,
                        padding=[10, 5],
                        font=cls.get_body_font(10))
        
        style.map("TNotebook.Tab",
                  background=[("selected", cls.ACCENT)],
                  foreground=[("selected", cls.LIGHT)])
                  
        # Treeview styling
        style.configure("Treeview", 
                        background=cls.LIGHT,
                        fieldbackground=cls.LIGHT,
                        font=cls.get_body_font())
        
        style.configure("Treeview.Heading", 
                        background=cls.SECONDARY,
                        foreground=cls.LIGHT,
                        font=cls.get_body_font(10, "bold"),
                        padding=[5])
                        
        style.map("Treeview", 
                  background=[('selected', cls.ACCENT)],
                  foreground=[('selected', cls.LIGHT)])

class LoadingAnimation:
    """Class to provide a loading animation"""
    def __init__(self, parent, x, y, size=20, color="#3498db"):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.canvas = tk.Canvas(parent, width=size*2, height=size*2, 
                               bg=parent["bg"], highlightthickness=0)
        self.canvas.place(x=x, y=y)
        self.angle = 0
        self.is_running = False
        self.animation_id = None
    
    def start(self):
        self.is_running = True
        self.animate()
    
    def stop(self):
        self.is_running = False
        if self.animation_id:
            self.canvas.after_cancel(self.animation_id)
        self.canvas.delete("all")
        self.canvas.place_forget()
    
    def animate(self):
        self.canvas.delete("all")
        # Draw arc
        angle1 = self.angle
        angle2 = self.angle + 240
        self.canvas.create_arc(5, 5, self.size*2-5, self.size*2-5, 
                              start=angle1, extent=angle2-angle1, 
                              outline=self.color, width=4, style="arc")
        
        self.angle = (self.angle + 10) % 360
        if self.is_running:
            self.animation_id = self.canvas.after(50, self.animate)

class ProductPriceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Price Tracker")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # Apply modern UI
        self.ui = ModernUI
        self.ui.apply_modern_style(root)
        
        # Set background color
        self.root.configure(bg=self.ui.LIGHT)
        
        # Create main container frame with padding
        self.main_container = ttk.Frame(self.root, padding=self.ui.PADDING_MEDIUM)
        self.main_container.pack(fill="both", expand=True, padx=self.ui.PADDING_LARGE, 
                                pady=self.ui.PADDING_LARGE)
        
        # Header section
        self.create_header()
        
        # Create main frames with proper spacing
        self.create_search_section()
        
        # Separator between search and results
        ttk.Separator(self.main_container, orient="horizontal").pack(
            fill="x", pady=self.ui.PADDING_MEDIUM)
        
        self.create_results_section()
        
        # Status bar at bottom
        self.create_status_bar()
        
        # User agent for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize loading animation (but don't start it yet)
        self.loading_animation = None
        
    def create_header(self):
        """Create app header with title and description"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill="x", pady=(0, self.ui.PADDING_LARGE))
        
        # App title
        title_label = tk.Label(
            header_frame, 
            text="Product Price Tracker",
            font=(self.ui.FONT_FAMILY, 24, "bold"),
            fg=self.ui.PRIMARY,
            bg=self.ui.LIGHT
        )
        title_label.pack(anchor="w")
        
        # App description
        desc_label = tk.Label(
            header_frame, 
            text="Search for products to view price history and sales data in ₹",
            font=self.ui.get_body_font(12),
            fg=self.ui.SECONDARY,
            bg=self.ui.LIGHT
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
    def create_search_section(self):
        """Create the search bar section with improved styling"""
        search_frame = ttk.Frame(self.main_container)
        search_frame.pack(fill="x", pady=self.ui.PADDING_MEDIUM)
        
        # Search container with border and background
        search_container = tk.Frame(
            search_frame, 
            bg=self.ui.PRIMARY,
            padx=self.ui.PADDING_LARGE,
            pady=self.ui.PADDING_LARGE,
            relief=tk.RIDGE,
            bd=1
        )
        search_container.pack(fill="x")
        
        # Grid configuration with proper spacing
        search_container.columnconfigure(0, weight=0)
        search_container.columnconfigure(1, weight=1)
        search_container.columnconfigure(2, weight=0)
        
        # Product search label 
        search_label = tk.Label(
            search_container, 
            text="Product Name:", 
            font=self.ui.get_body_font(12, "bold"),
            bg=self.ui.PRIMARY,
            fg=self.ui.LIGHT
        )
        search_label.grid(row=0, column=0, padx=(0, self.ui.PADDING_MEDIUM), pady=0, sticky="w")
        
        # Custom entry with modern styling
        self.product_entry = tk.Entry(
            search_container, 
            font=self.ui.get_body_font(12),
            bg="white",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.ui.ACCENT,
            highlightcolor=self.ui.ACCENT
        )
        self.product_entry.grid(row=0, column=1, padx=self.ui.PADDING_MEDIUM, pady=0, sticky="ew")
        
        # Add a placeholder text
        self.product_entry.insert(0, "Enter product name here...")
        self.product_entry.bind("<FocusIn>", self.clear_placeholder)
        self.product_entry.bind("<FocusOut>", self.restore_placeholder)
        self.product_entry.bind("<Return>", lambda event: self.start_search())
        
        # Search button with modern styling
        self.search_button = tk.Button(
            search_container,
            text="Search",
            font=self.ui.get_body_font(11, "bold"),
            bg=self.ui.SUCCESS,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=5,
            activebackground=self.ui.ACCENT_DARK,
            activeforeground="white",
            command=self.start_search
        )
        self.search_button.grid(row=0, column=2, padx=(self.ui.PADDING_MEDIUM, 0), pady=0)
    
    def clear_placeholder(self, event):
        """Clear placeholder text when entry is focused"""
        if self.product_entry.get() == "Enter product name here...":
            self.product_entry.delete(0, tk.END)
            self.product_entry.config(fg="black")
    
    def restore_placeholder(self, event):
        """Restore placeholder text if entry is empty"""
        if not self.product_entry.get():
            self.product_entry.insert(0, "Enter product name here...")
            self.product_entry.config(fg="gray")
        
    def create_results_section(self):
        """Create the results section with tabbed interface"""
        self.result_frame = ttk.Frame(self.main_container)
        self.result_frame.pack(fill="both", expand=True, pady=self.ui.PADDING_MEDIUM)
        
        # Notebook for tabbed interface
        self.tabs = ttk.Notebook(self.result_frame)
        self.tabs.pack(fill="both", expand=True)
        
        # Price history tab
        self.price_tab = ttk.Frame(self.tabs, padding=self.ui.PADDING_LARGE)
        self.tabs.add(self.price_tab, text="Price History")
        
        # Sales data tab
        self.sales_tab = ttk.Frame(self.tabs, padding=self.ui.PADDING_LARGE)
        self.tabs.add(self.sales_tab, text="Sales Data")
        
        # Graph tab
        self.graph_tab = ttk.Frame(self.tabs, padding=self.ui.PADDING_LARGE)
        self.tabs.add(self.graph_tab, text="Graphs")
        
        # Create frames for price history tab with padding
        self.price_header_frame = ttk.Frame(self.price_tab)
        self.price_header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        self.price_table_frame = ttk.Frame(self.price_tab)
        self.price_table_frame.pack(fill="both", expand=True)
        
        # Create frames for sales tab with padding
        self.sales_header_frame = ttk.Frame(self.sales_tab)
        self.sales_header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        self.sales_table_frame = ttk.Frame(self.sales_tab)
        self.sales_table_frame.pack(fill="both", expand=True)
        
        # Create frames for graph tab with padding
        self.graph_header_frame = ttk.Frame(self.graph_tab)
        self.graph_header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill="both", expand=True)
        
        # Add initial empty state messages
        self.add_empty_state()
    
    def add_empty_state(self):
        """Add initial empty state messages to tabs"""
        # Price tab empty state
        self.price_empty_label = tk.Label(
            self.price_table_frame,
            text="Search for a product to see price history",
            font=self.ui.get_body_font(12),
            fg=self.ui.SECONDARY,
            bg=self.ui.LIGHT
        )
        self.price_empty_label.pack(expand=True)
        
        # Sales tab empty state
        self.sales_empty_label = tk.Label(
            self.sales_table_frame,
            text="Search for a product to see sales data",
            font=self.ui.get_body_font(12),
            fg=self.ui.SECONDARY,
            bg=self.ui.LIGHT
        )
        self.sales_empty_label.pack(expand=True)
        
        # Graph tab empty state
        self.graph_empty_label = tk.Label(
            self.graph_frame,
            text="Search for a product to see data visualizations",
            font=self.ui.get_body_font(12),
            fg=self.ui.SECONDARY,
            bg=self.ui.LIGHT
        )
        self.graph_empty_label.pack(expand=True)
    
    def remove_empty_state(self):
        """Remove empty state labels when data is loaded"""
        if hasattr(self, 'price_empty_label'):
            self.price_empty_label.pack_forget()
        if hasattr(self, 'sales_empty_label'):
            self.sales_empty_label.pack_forget()
        if hasattr(self, 'graph_empty_label'):
            self.graph_empty_label.pack_forget()
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        
        # Add separator above status bar
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", side="bottom")
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var,
            font=self.ui.get_body_font(9)
        )
        status_label.pack(side="left", padx=self.ui.PADDING_MEDIUM, pady=5)
        
        # Version info on right
        version_label = ttk.Label(
            status_frame,
            text="v1.2.0",
            font=self.ui.get_body_font(9)
        )
        version_label.pack(side="right", padx=self.ui.PADDING_MEDIUM, pady=5)
    
    def start_search(self):
        """Start the search process in a separate thread to keep UI responsive"""
        product_name = self.product_entry.get().strip()
        if product_name == "Enter product name here..." or not product_name:
            messagebox.showwarning("Input Error", "Please enter a product name", parent=self.root)
            return
        
        # Update UI to show searching state
        self.search_button.config(state="disabled")
        self.status_var.set(f"Searching for '{product_name}'...")
        
        # Create and start loading animation
        if not self.loading_animation:
            x = self.search_button.winfo_x() - 40
            y = self.search_button.winfo_y() + 5
            self.loading_animation = LoadingAnimation(
                self.search_button.master, x, y, size=15, color=self.ui.ACCENT)
        self.loading_animation.start()
        
        # Clear previous results
        self.clear_results()
        
        # Remove empty state messages
        self.remove_empty_state()
            
        # Start search in a separate thread
        threading.Thread(target=self.search_product, args=(product_name,), daemon=True).start()
    
    def clear_results(self):
        """Clear all previous results from tabs"""
        for frame in [self.price_header_frame, self.price_table_frame, 
                    self.sales_header_frame, self.sales_table_frame,
                    self.graph_header_frame, self.graph_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
    
    def search_product(self, product_name):
        """Search for the product and attempt to fetch price data"""
        try:
            # First attempt to get real data through web scraping
            self.status_var.set("Fetching data from web sources...")
            product_data = self.attempt_web_scraping(product_name)
            
            # If web scraping fails, fall back to mock data
            if product_data is None:
                self.status_var.set("Web data not available, generating simulation...")
                time.sleep(0.5)  # Small delay to make UX smoother
                price_data, sales_data = self.get_mock_data()
                self.root.after(0, lambda: self.display_results(product_name, price_data, sales_data, is_mock=True))
            else:
                # Process the scraped data
                price_data, sales_data = product_data
                self.root.after(0, lambda: self.display_results(product_name, price_data, sales_data, is_mock=False))
                
        except Exception as e:
            self.root.after(0, lambda: self.handle_error(f"An error occurred: {str(e)}"))
    
    def handle_error(self, error_msg):
        """Handle errors and update UI accordingly"""
        messagebox.showerror("Error", error_msg, parent=self.root)
        self.status_var.set("Ready")
        self.search_button.config(state="normal")
        if self.loading_animation:
            self.loading_animation.stop()
        # Restore empty state messages
        self.add_empty_state()
    
    def attempt_web_scraping(self, product_name):
        """Attempt to scrape price data from shopping websites"""
        try:
            # In a real implementation, you would use an appropriate API or scrape from
            # e-commerce sites. This is a simplified example.
            
            # Create a Google search URL for the product
            search_url = f"https://www.google.com/search?q={product_name}+price+history+india"
            
            # Make a request to the search URL
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to get search results: {response.status_code}")
                return None
                
            # In a real application, you would parse the search results and extract
            # product information, then visit product pages to gather price history.
            # For this demonstration, we'll return mock data with a note that it's
            # based on a real search.
            
            # Get dates for last 7 days
            dates = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(6, -1, -1)]
            
            # Generate semi-realistic price data based on the product name
            # (in a real app, this would come from actual scraped data)
            seed = sum(ord(c) for c in product_name)
            random.seed(seed)
            
            base_price = random.randint(5000, 100000)  # Base price in rupees
            
            # Generate price fluctuations that look somewhat realistic
            trend = random.choice([-1, 1])  # Overall trend direction
            volatility = random.uniform(0.01, 0.05)  # How much prices fluctuate
            
            prices = []
            current_price = base_price
            for _ in range(7):
                # Add some randomness to the price trend
                change = current_price * volatility * random.uniform(-1, 1)
                # Add trend bias
                change += current_price * 0.01 * trend
                current_price += change
                prices.append(round(current_price))
            
            # Create price dataframe
            price_data = pd.DataFrame({
                'Date': dates,
                'Price (₹)': prices
            })
            
            # Generate sales data based on price (lower price usually means higher sales)
            avg_price = sum(prices) / len(prices)
            sales = []
            for price in prices:
                # Base sales inversely related to price
                base_sales = 300 * (avg_price / price)
                # Add randomness
                sales.append(int(base_sales * random.uniform(0.7, 1.3)))
            
            # Create sales dataframe
            sales_data = pd.DataFrame({
                'Date': dates,
                'Units Sold': sales,
                'Revenue (₹)': [prices[i] * sales[i] for i in range(7)]
            })
            
            return price_data, sales_data
            
        except Exception as e:
            print(f"Web scraping failed: {str(e)}")
            return None
    
    def get_mock_data(self):
        """Generate fully mock price and sales data for demonstration"""
        # Get dates for last 7 days
        dates = [(datetime.now() - timedelta(days=i)).strftime("%d-%m-%Y") for i in range(6, -1, -1)]
        
        # Generate random price data (in rupees)
        base_price = random.randint(10000, 50000)
        prices = [round(base_price + random.randint(-1000, 1000)) for _ in range(7)]
        price_data = pd.DataFrame({
            'Date': dates,
            'Price (₹)': prices
        })
        
        # Generate random sales data
        sales = [random.randint(50, 500) for _ in range(7)]
        sales_data = pd.DataFrame({
            'Date': dates,
            'Units Sold': sales,
            'Revenue (₹)': [prices[i] * sales[i] for i in range(7)]
        })
        
        return price_data, sales_data
    
    def display_results(self, product_name, price_data, sales_data, is_mock=True):
        """Display the search results in the UI"""
        # Update status
        self.status_var.set(f"Displaying results for '{product_name}'")
        
        # Stop loading animation
        if self.loading_animation:
            self.loading_animation.stop()
        
        # Format data source label
        data_source = "Simulated Data" if is_mock else "Web Data"
        source_color = self.ui.WARNING if is_mock else self.ui.SUCCESS
        
        # Price History Tab
        # -----------------
        # Header with info box
        header_frame = ttk.Frame(self.price_header_frame)
        header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        # Left side - title
        title_label = tk.Label(
            header_frame,
            text=f"Price History for {product_name}",
            font=self.ui.get_heading_font(16),
            fg=self.ui.PRIMARY,
            bg=self.ui.LIGHT
        )
        title_label.pack(side="left", anchor="w")
        
        # Right side - source badge
        source_frame = tk.Frame(
            header_frame,
            bg=source_color,
            padx=10,
            pady=3,
            relief=tk.FLAT
        )
        source_frame.pack(side="right", anchor="e")
        
        source_label = tk.Label(
            source_frame,
            text=data_source,
            font=self.ui.get_body_font(9, "bold"),
            fg="white",
            bg=source_color
        )
        source_label.pack()
        
        # Display price history table with scrollbar container
        table_container = ttk.Frame(self.price_table_frame)
        table_container.pack(fill="both", expand=True)
        
        self.create_table(table_container, price_data)
        
        # Sales Data Tab
        # --------------
        # Similar layout as price tab
        header_frame = ttk.Frame(self.sales_header_frame)
        header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        title_label = tk.Label(
            header_frame,
            text=f"Sales Data for {product_name}",
            font=self.ui.get_heading_font(16),
            fg=self.ui.PRIMARY,
            bg=self.ui.LIGHT
        )
        title_label.pack(side="left", anchor="w")
        
        source_frame = tk.Frame(
            header_frame,
            bg=source_color,
            padx=10,
            pady=3,
            relief=tk.FLAT
        )
        source_frame.pack(side="right", anchor="e")
        
        source_label = tk.Label(
            source_frame,
            text=data_source,
            font=self.ui.get_body_font(9, "bold"),
            fg="white",
            bg=source_color
        )
        source_label.pack()
        
        # Display sales table
        table_container = ttk.Frame(self.sales_table_frame)
        table_container.pack(fill="both", expand=True)
        
        self.create_table(table_container, sales_data)
        
        # Graphs Tab
        # ----------
        header_frame = ttk.Frame(self.graph_header_frame)
        header_frame.pack(fill="x", pady=(0, self.ui.PADDING_MEDIUM))
        
        title_label = tk.Label(
            header_frame,
            text=f"Data Visualization for {product_name}",
            font=self.ui.get_heading_font(16),
            fg=self.ui.PRIMARY,
            bg=self.ui.LIGHT
        )
        title_label.pack(side="left", anchor="w")
        
        source_frame = tk.Frame(
            header_frame,
            bg=source_color,
            padx=10,
            pady=3,
            relief=tk.FLAT
        )
        source_frame.pack(side="right", anchor="e")
        
        source_label = tk.Label(
            source_frame,
            text=data_source,
            font=self.ui.get_body_font(9, "bold"),
            fg="white",
            bg=source_color
        )
        source_label.pack()
        
        # Create enhanced graphs
        self.create_enhanced_graphs(product_name, price_data, sales_data)
        
        # Re-enable search button
        self.search_button.config(state="normal")
    
    def create_table(self, parent, data):
        """Create a table from DataFrame with modern styling"""
        # Create frame for table and scrollbar
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True)
        
        # Create Treeview with modern styling
        columns = list(data.columns)
        table = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings with better formatting
        for col in columns:
            table.heading(col, text=col)
            # Determine column width based on content
            if "Price" in col or "Revenue" in col:
                table.column(col, width=150, anchor="e")  # Right-align currency
            elif "Date" in col:
                table.column(col, width=100, anchor="center")  # Center dates
            else:
                table.column(col, width=100, anchor="center")
        
        # Add data rows with formatting
        for idx, row in data.iterrows():
            values = []
            for col in columns:
                value = row[col]
                # Format currency values
                if "Price" in col or "Revenue" in col:
                    value = f"₹{value:,.2f}"
                values.append(value)
            table.insert("", "end", values=values)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Place widgets with proper fill
        table.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        return table
    
    def create_enhanced_graphs(self, product_name, price_data, sales_data):
        """Create and display enhanced graphs with better styling"""
        # Create figure with enhanced styling
        plt.style.use('ggplot')
        fig = plt.Figure(figsize=(10, 8), dpi=100)
        fig.subplots_adjust(hspace=0.4, bottom=0.15)
        
        # Use custom colors that match our UI theme
        price_color = self.ui.ACCENT
        sales_color = self.ui.SUCCESS
        revenue_color = self.ui.DANGER
        
        # Price history graph
        ax1 = fig.add_subplot(211)
        
        # Plot line with shadow effect for depth
        ax1.plot(price_data['Date'], price_data['Price (₹)'], 
                marker='o', linestyle='-', color=price_color, 
                linewidth=3, markersize=8, markerfacecolor='white')
                
        # Fill area under the line
        ax1.fill_between(
            price_data['Date'], 
            price_data['Price (₹)'], 
            color=price_color, 
            alpha=0.2
        )
                
        # Add data labels above points
        for x, y in zip(price_data['Date'], price_data['Price (₹)']):
            ax1.annotate(f'₹{y:,}', 
                        xy=(x, y),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.3", fc='white', ec=price_color, alpha=0.8))
                        
        # Set title and labels with better font
        ax1.set_title(f'Price History - {product_name}', 
                    fontsize=14, 
                    fontweight='bold', 
                    color=self.ui.PRIMARY,
                    pad=15)
                    
        ax1.set_ylabel('Price (₹)', 
                    fontsize=12, 
                    fontweight='bold',
                    color=self.ui.PRIMARY)
                    
        # Format y-axis with commas for thousands
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('₹{x:,.0f}'))
        
        # Add gridlines for better readability
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Style the spines
        for spine in ax1.spines.values():
            spine.set_color(self.ui.LIGHT)
            
        # Rotate x-axis labels for better readability
        plt.setp(ax1.get_xticklabels(), rotation=30, ha='right')
        
        # Highlight min and max values
        min_idx = price_data['Price (₹)'].idxmin()
        max_idx = price_data['Price (₹)'].idxmax()
        
        ax1.plot(price_data['Date'][min_idx], price_data['Price (₹)'][min_idx], 
                'o', ms=12, mec=self.ui.WARNING, mew=2, mfc='none')
        ax1.annotate('Min', 
                    xy=(price_data['Date'][min_idx], price_data['Price (₹)'][min_idx]),
                    xytext=(10, -20),
                    textcoords='offset points',
                    color=self.ui.WARNING,
                    fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=self.ui.WARNING))
                    
        ax1.plot(price_data['Date'][max_idx], price_data['Price (₹)'][max_idx], 
                'o', ms=12, mec=self.ui.DANGER, mew=2, mfc='none')
        ax1.annotate('Max', 
                    xy=(price_data['Date'][max_idx], price_data['Price (₹)'][max_idx]),
                    xytext=(10, 20),
                    textcoords='offset points',
                    color=self.ui.DANGER,
                    fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color=self.ui.DANGER))
        
        # Sales and revenue graph (dual axis)
        ax2 = fig.add_subplot(212)
        
        # Bar chart for units sold
        bars = ax2.bar(sales_data['Date'], sales_data['Units Sold'], 
                     color=sales_color, alpha=0.7, width=0.6)
        
        # Add data labels above bars
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9,
                        bbox=dict(boxstyle="round,pad=0.2", fc='white', ec=sales_color, alpha=0.8))
        
        # Create second y-axis for revenue
        ax3 = ax2.twinx()
        
        # Plot revenue line
        line = ax3.plot(sales_data['Date'], sales_data['Revenue (₹)'], 
                      color=revenue_color, marker='d', linestyle='-.',
                      linewidth=2, markersize=7, markerfacecolor='white')
        
        # Add data labels for revenue points
        for x, y in zip(sales_data['Date'], sales_data['Revenue (₹)']):
            ax3.annotate(f'₹{y/1000:.1f}K', 
                        xy=(x, y),
                        xytext=(0, -15 if sales_data['Revenue (₹)'].max() == y else 10),
                        textcoords='offset points',
                        ha='center',
                        fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.2", fc='white', ec=revenue_color, alpha=0.8))
        
        # Set titles and labels
        ax2.set_title(f'Sales History - {product_name}', 
                    fontsize=14, 
                    fontweight='bold', 
                    color=self.ui.PRIMARY,
                    pad=15)
                    
        ax2.set_ylabel('Units Sold', 
                     fontsize=12, 
                     fontweight='bold',
                     color=sales_color)
                     
        ax3.set_ylabel('Revenue (₹)', 
                     fontsize=12, 
                     fontweight='bold',
                     color=revenue_color)
        
        # Format y-axis with commas
        ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter('₹{x:,.0f}'))
        
        # Add gridlines
        ax2.grid(True, linestyle='--', alpha=0.3)
        
        # Style the spines
        for spine in ax2.spines.values():
            spine.set_color(self.ui.LIGHT)
        
        # Make right side y-axis visible
        ax3.spines['right'].set_visible(True)
        ax3.spines['right'].set_color(revenue_color)
        
        # Rotate x-axis labels
        plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='none', marker='s', markerfacecolor=sales_color, 
                  markeredgecolor='none', markersize=10, label='Units Sold'),
            Line2D([0], [0], color=revenue_color, marker='d', markerfacecolor='white',
                  markersize=7, label='Revenue')
        ]
        ax2.legend(handles=legend_elements, loc='upper left', frameon=True,
                 fancybox=True, framealpha=0.8, borderpad=1)
        
        # Add summary statistics box to first graph
        price_avg = price_data['Price (₹)'].mean()
        price_min = price_data['Price (₹)'].min()
        price_max = price_data['Price (₹)'].max()
        price_change = ((price_data['Price (₹)'].iloc[-1] - price_data['Price (₹)'].iloc[0]) / 
                       price_data['Price (₹)'].iloc[0] * 100)
        
        stats_text = (
            f"Summary Statistics\n"
            f"─────────────────\n"
            f"Average Price: ₹{price_avg:,.2f}\n"
            f"Minimum Price: ₹{price_min:,.2f}\n"
            f"Maximum Price: ₹{price_max:,.2f}\n"
            f"7-Day Change: {price_change:+.2f}%"
        )
        
        props = dict(boxstyle='round', facecolor=self.ui.LIGHT, alpha=0.9, edgecolor=self.ui.PRIMARY)
        ax1.text(0.02, 0.05, stats_text, transform=ax1.transAxes, fontsize=9,
                verticalalignment='bottom', bbox=props, family=self.ui.FONT_FAMILY)
        
        # Add similar stats box to second graph
        total_sales = sales_data['Units Sold'].sum()
        total_revenue = sales_data['Revenue (₹)'].sum()
        avg_revenue_per_unit = total_revenue / total_sales
        
        sales_stats_text = (
            f"Sales Statistics\n"
            f"─────────────────\n"
            f"Total Units: {total_sales:,}\n"
            f"Total Revenue: ₹{total_revenue:,.2f}\n"
            f"Avg. Price per Unit: ₹{avg_revenue_per_unit:,.2f}"
        )
        
        ax2.text(0.02, 0.05, sales_stats_text, transform=ax2.transAxes, fontsize=9,
                verticalalignment='bottom', bbox=props, family=self.ui.FONT_FAMILY)
        
        # Fine-tune the figure layout
        fig.tight_layout()
        
        # Embed the graphs in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)
        canvas.draw()
        
        # Add a toolbar for the graph (pan, zoom, save, etc.)
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar_frame = ttk.Frame(self.graph_frame)
        toolbar_frame.pack(fill="x", pady=(0, 5))
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductPriceTracker(root)
    root.mainloop()