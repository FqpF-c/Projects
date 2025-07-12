import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class ChurnPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Churn Prediction with Dynamic Pricing")
        self.root.geometry("900x650")
        self.root.configure(bg="#f0f0f0")
        
        self.model = None
        self.scaler = StandardScaler()
        self.data = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Data tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data")
        
        # Model tab
        self.model_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.model_frame, text="Model")
        
        # Prediction tab
        self.prediction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.prediction_frame, text="Prediction")
        
        # Dynamic Pricing tab
        self.pricing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pricing_frame, text="Dynamic Pricing")
        
        # Setup Data tab
        self.setup_data_tab()
        
        # Setup Model tab
        self.setup_model_tab()
        
        # Setup Prediction tab
        self.setup_prediction_tab()
        
        # Setup Dynamic Pricing tab
        self.setup_pricing_tab()
    
    def setup_data_tab(self):
        # Data frame components
        ttk.Label(self.data_frame, text="Customer Data", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Button to load data
        ttk.Button(self.data_frame, text="Load CSV Data", command=self.load_data).grid(row=1, column=0, pady=10, padx=5, sticky="w")
        
        # Display data info
        self.data_info_text = tk.Text(self.data_frame, height=10, width=80)
        self.data_info_text.grid(row=2, column=0, columnspan=2, pady=5, padx=5)
        self.data_info_text.insert(tk.END, "No data loaded. Please load a CSV file.")
        self.data_info_text.config(state=tk.DISABLED)
        
        # Frame for data preview
        preview_frame = ttk.LabelFrame(self.data_frame, text="Data Preview")
        preview_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Treeview for data preview
        self.tree = ttk.Treeview(preview_frame)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Frame for EDA visualization
        viz_frame = ttk.LabelFrame(self.data_frame, text="Data Visualization")
        viz_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Buttons for basic visualizations
        ttk.Button(viz_frame, text="Correlation Heatmap", command=lambda: self.visualize_data("correlation")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(viz_frame, text="Churn Distribution", command=lambda: self.visualize_data("churn_dist")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(viz_frame, text="Price vs Churn", command=lambda: self.visualize_data("price_churn")).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Configure grid weights
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(3, weight=1)
        self.data_frame.rowconfigure(4, weight=1)
    
    def setup_model_tab(self):
        # Model frame components
        ttk.Label(self.model_frame, text="Train Churn Prediction Model", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Model parameters frame
        params_frame = ttk.LabelFrame(self.model_frame, text="Model Parameters")
        params_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Model parameters
        ttk.Label(params_frame, text="Test Size (%)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.test_size_var = tk.StringVar(value="30")
        ttk.Entry(params_frame, textvariable=self.test_size_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(params_frame, text="Number of Estimators").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.n_estimators_var = tk.StringVar(value="100")
        ttk.Entry(params_frame, textvariable=self.n_estimators_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(params_frame, text="Random State").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.random_state_var = tk.StringVar(value="42")
        ttk.Entry(params_frame, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        # Target column selection
        ttk.Label(params_frame, text="Target Column").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.target_var = tk.StringVar(value="Churn")
        self.target_combobox = ttk.Combobox(params_frame, textvariable=self.target_var, width=15)
        self.target_combobox.grid(row=3, column=1, padx=5, pady=5)
        
        # Feature selection
        ttk.Label(params_frame, text="Features to Exclude").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.exclude_var = tk.StringVar(value="CustomerID")
        ttk.Entry(params_frame, textvariable=self.exclude_var, width=30).grid(row=4, column=1, padx=5, pady=5)
        ttk.Label(params_frame, text="(Comma-separated column names)").grid(row=4, column=2, sticky="w", padx=5, pady=5)
        
        # Train button
        ttk.Button(self.model_frame, text="Train Model", command=self.train_model).grid(row=2, column=0, pady=10, padx=5, sticky="w")
        
        # Model results frame
        results_frame = ttk.LabelFrame(self.model_frame, text="Model Results")
        results_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=10, width=80)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.results_text.insert(tk.END, "No model trained yet. Please train a model first.")
        self.results_text.config(state=tk.DISABLED)
        
        # Feature importance visualization frame
        importance_frame = ttk.LabelFrame(self.model_frame, text="Feature Importance")
        importance_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Canvas for feature importance plot
        self.importance_canvas_frame = ttk.Frame(importance_frame)
        self.importance_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Configure grid weights
        self.model_frame.columnconfigure(0, weight=1)
        self.model_frame.rowconfigure(3, weight=1)
        self.model_frame.rowconfigure(4, weight=1)
    
    def setup_prediction_tab(self):
        # Prediction frame components
        ttk.Label(self.prediction_frame, text="Predict Customer Churn", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Customer input frame
        input_frame = ttk.LabelFrame(self.prediction_frame, text="Customer Details")
        input_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Scrollable frame for inputs
        canvas = tk.Canvas(input_frame)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Placeholder for dynamic input fields
        ttk.Label(self.scrollable_frame, text="Load data and train a model to enable prediction").grid(row=0, column=0, padx=5, pady=5)
        
        # Predict button
        ttk.Button(self.prediction_frame, text="Predict Churn", command=self.predict_churn).grid(row=2, column=0, pady=10, padx=5, sticky="w")
        
        # Prediction results frame
        prediction_results_frame = ttk.LabelFrame(self.prediction_frame, text="Prediction Results")
        prediction_results_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Results text area
        self.prediction_text = tk.Text(prediction_results_frame, height=8, width=80)
        self.prediction_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.prediction_text.insert(tk.END, "No prediction yet. Please input customer details and click 'Predict Churn'.")
        self.prediction_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        self.prediction_frame.columnconfigure(0, weight=1)
        self.prediction_frame.rowconfigure(1, weight=1)
        self.prediction_frame.rowconfigure(3, weight=1)
    
    def setup_pricing_tab(self):
        # Dynamic Pricing frame components
        ttk.Label(self.pricing_frame, text="Dynamic Pricing Strategy", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Pricing parameters
        params_frame = ttk.LabelFrame(self.pricing_frame, text="Pricing Parameters")
        params_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Base price
        ttk.Label(params_frame, text="Base Price ($)").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.base_price_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.base_price_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # Max discount
        ttk.Label(params_frame, text="Maximum Discount (%)").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.max_discount_var = tk.StringVar(value="30")
        ttk.Entry(params_frame, textvariable=self.max_discount_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Pricing strategy
        ttk.Label(params_frame, text="Pricing Strategy").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.strategy_var = tk.StringVar(value="risk_based")
        ttk.Radiobutton(params_frame, text="Risk-Based", variable=self.strategy_var, value="risk_based").grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(params_frame, text="Value-Based", variable=self.strategy_var, value="value_based").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(params_frame, text="Hybrid", variable=self.strategy_var, value="hybrid").grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        # Calculate button
        ttk.Button(self.pricing_frame, text="Calculate Dynamic Prices", command=self.calculate_prices).grid(row=2, column=0, pady=10, padx=5, sticky="w")
        
        # Pricing results frame
        pricing_results_frame = ttk.LabelFrame(self.pricing_frame, text="Pricing Results")
        pricing_results_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Results text area
        self.pricing_text = tk.Text(pricing_results_frame, height=8, width=80)
        self.pricing_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        self.pricing_text.insert(tk.END, "No pricing calculated yet. Please train a model and calculate dynamic prices.")
        self.pricing_text.config(state=tk.DISABLED)
        
        # Pricing visualization frame
        viz_frame = ttk.LabelFrame(self.pricing_frame, text="Pricing Visualization")
        viz_frame.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="nsew")
        
        # Canvas for pricing plot
        self.pricing_canvas_frame = ttk.Frame(viz_frame)
        self.pricing_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Configure grid weights
        self.pricing_frame.columnconfigure(0, weight=1)
        self.pricing_frame.rowconfigure(3, weight=1)
        self.pricing_frame.rowconfigure(4, weight=1)
    
    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            self.data = pd.read_csv(file_path)
            
            # Update data info text
            self.data_info_text.config(state=tk.NORMAL)
            self.data_info_text.delete(1.0, tk.END)
            self.data_info_text.insert(tk.END, f"Data loaded successfully from: {file_path}\n\n")
            self.data_info_text.insert(tk.END, f"Number of rows: {self.data.shape[0]}\n")
            self.data_info_text.insert(tk.END, f"Number of columns: {self.data.shape[1]}\n\n")
            self.data_info_text.insert(tk.END, "Column information:\n")
            
            for col in self.data.columns:
                self.data_info_text.insert(tk.END, f"- {col}: {self.data[col].dtype}\n")
            
            self.data_info_text.config(state=tk.DISABLED)
            
            # Update data preview
            self.update_data_preview()
            
            # Update target column dropdown
            self.target_combobox['values'] = list(self.data.columns)
            
            # Set up prediction input fields
            self.setup_prediction_inputs()
            
            messagebox.showinfo("Success", "Data loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_data_preview(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        self.tree['columns'] = list(self.data.columns)
        self.tree['show'] = 'headings'
        
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Add data (first 10 rows)
        for i, row in self.data.head(10).iterrows():
            values = [str(row[col]) for col in self.data.columns]
            self.tree.insert('', 'end', values=values)
    
    def setup_prediction_inputs(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create input fields for each feature
        self.input_vars = {}
        row = 0
        
        if self.data is not None:
            for col in self.data.columns:
                if col != self.target_var.get() and col not in self.exclude_var.get().split(','):
                    ttk.Label(self.scrollable_frame, text=col).grid(row=row, column=0, sticky="w", padx=5, pady=5)
                    
                    # Create appropriate input widget based on data type
                    if self.data[col].dtype == 'object':
                        # Categorical variable
                        values = self.data[col].unique().tolist()
                        var = tk.StringVar()
                        widget = ttk.Combobox(self.scrollable_frame, textvariable=var, values=values, width=15)
                        if values:
                            var.set(values[0])
                    else:
                        # Numerical variable
                        var = tk.StringVar(value=str(self.data[col].mean()))
                        widget = ttk.Entry(self.scrollable_frame, textvariable=var, width=15)
                    
                    widget.grid(row=row, column=1, padx=5, pady=5)
                    self.input_vars[col] = var
                    row += 1
    
    def train_model(self):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded. Please load data first.")
            return
        
        try:
            # Get parameters
            test_size = float(self.test_size_var.get()) / 100
            n_estimators = int(self.n_estimators_var.get())
            random_state = int(self.random_state_var.get())
            target_col = self.target_var.get()
            exclude_cols = [col.strip() for col in self.exclude_var.get().split(',')]
            
            # Validate target column
            if target_col not in self.data.columns:
                messagebox.showerror("Error", f"Target column '{target_col}' not found in data.")
                return
            
            # Prepare data
            features = [col for col in self.data.columns if col != target_col and col not in exclude_cols]
            
            # Handle categorical variables
            X = pd.get_dummies(self.data[features])
            y = self.data[target_col]
            
            # Split data
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Scale numerical features
            self.feature_names = X.columns.tolist()
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
            self.model.fit(self.X_train, self.y_train)
            
            # Evaluate model
            y_pred = self.model.predict(self.X_test)
            accuracy = accuracy_score(self.y_test, y_pred)
            report = classification_report(self.y_test, y_pred)
            
            # Update results text
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Model trained successfully!\n\n")
            self.results_text.insert(tk.END, f"Accuracy: {accuracy:.4f}\n\n")
            self.results_text.insert(tk.END, "Classification Report:\n")
            self.results_text.insert(tk.END, report)
            self.results_text.config(state=tk.DISABLED)
            
            # Plot feature importance
            self.plot_feature_importance()
            
            # Update prediction inputs
            self.setup_prediction_inputs()
            
            messagebox.showinfo("Success", "Model trained successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to train model: {str(e)}")
    
    def plot_feature_importance(self):
        if self.model is None:
            return
        
        # Clear existing canvas
        for widget in self.importance_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Get feature importances
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[-10:]  # Top 10 features
        
        # Plot
        plt.barh(range(len(indices)), importances[indices], align='center')
        plt.yticks(range(len(indices)), [self.feature_names[i] for i in indices])
        plt.xlabel('Feature Importance')
        plt.title('Top 10 Features by Importance')
        plt.tight_layout()
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.importance_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def predict_churn(self):
        if self.model is None:
            messagebox.showerror("Error", "No model trained. Please train a model first.")
            return
        
        try:
            # Get input values
            input_data = {}
            for col, var in self.input_vars.items():
                value = var.get()
                # Convert to appropriate type
                if self.data[col].dtype == 'object':
                    input_data[col] = value
                else:
                    input_data[col] = float(value)
            
            # Create DataFrame
            input_df = pd.DataFrame([input_data])
            
            # Apply one-hot encoding
            input_encoded = pd.get_dummies(input_df)
            
            # Align columns with training data
            for col in self.X_train.columns:
                if col not in input_encoded.columns:
                    input_encoded[col] = 0
            
            input_encoded = input_encoded[self.X_train.columns]
            
            # Make prediction
            probability = self.model.predict_proba(input_encoded)[0][1]
            prediction = self.model.predict(input_encoded)[0]
            
            # Update results text
            self.prediction_text.config(state=tk.NORMAL)
            self.prediction_text.delete(1.0, tk.END)
            self.prediction_text.insert(tk.END, f"Churn Prediction Results:\n\n")
            self.prediction_text.insert(tk.END, f"Churn Probability: {probability:.2%}\n")
            self.prediction_text.insert(tk.END, f"Predicted Outcome: {'Will Churn' if prediction else 'Will Not Churn'}\n\n")
            
            # Add risk assessment
            if probability < 0.3:
                risk = "Low"
                suggestion = "Standard pricing and standard service level."
            elif probability < 0.7:
                risk = "Medium"
                suggestion = "Consider a moderate discount or enhanced service offering."
            else:
                risk = "High"
                suggestion = "Significant intervention needed. Consider substantial discount or premium service package."
            
            self.prediction_text.insert(tk.END, f"Risk Level: {risk}\n")
            self.prediction_text.insert(tk.END, f"Suggested Action: {suggestion}")
            self.prediction_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to predict: {str(e)}")
    
    def calculate_prices(self):
        if self.model is None or self.data is None:
            messagebox.showerror("Error", "No model trained. Please load data and train a model first.")
            return
        
        try:
            # Get pricing parameters
            base_price = float(self.base_price_var.get())
            max_discount = float(self.max_discount_var.get()) / 100
            strategy = self.strategy_var.get()
            
            # Make predictions on all test data
            probabilities = self.model.predict_proba(self.X_test)[:, 1]
            
            # Calculate prices based on strategy
            prices = []
            for prob in probabilities:
                if strategy == "risk_based":
                    # Higher risk (probability) = higher discount
                    discount = prob * max_discount
                    price = base_price * (1 - discount)
                elif strategy == "value_based":
                    # Calculate value score (simplified)
                    # Assuming lower churn risk = higher value
                    value_score = 1 - prob
                    discount = (1 - value_score) * max_discount
                    price = base_price * (1 - discount)
                else:  # hybrid
                    # Combine risk and value
                    risk_weight = 0.7
                    value_weight = 0.3
                    risk_discount = prob * max_discount
                    value_score = 1 - prob
                    value_discount = (1 - value_score) * max_discount
                    discount = (risk_weight * risk_discount) + (value_weight * value_discount)
                    price = base_price * (1 - discount)
                
                prices.append(price)
            
            # Calculate statistics
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Update results text
            self.pricing_text.config(state=tk.NORMAL)
            self.pricing_text.delete(1.0, tk.END)
            self.pricing_text.insert(tk.END, f"Dynamic Pricing Results:\n\n")
            self.pricing_text.insert(tk.END, f"Strategy: {strategy.replace('_', ' ').title()}\n")
            self.pricing_text.insert(tk.END, f"Base Price: ${base_price:.2f}\n")
            self.pricing_text.insert(tk.END, f"Maximum Discount: {max_discount:.2%}\n\n")
            self.pricing_text.insert(tk.END, f"Average Price: ${avg_price:.2f}\n")
            self.pricing_text.insert(tk.END, f"Minimum Price: ${min_price:.2f}\n")
            self.pricing_text.insert(tk.END, f"Maximum Price: ${max_price:.2f}\n")
            self.pricing_text.config(state=tk.DISABLED)
            
            # Plot price distribution
            self.plot_price_distribution(probabilities, prices)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate prices: {str(e)}")
    
    def plot_price_distribution(self, probabilities, prices):
        # Clear existing canvas
        for widget in self.pricing_canvas_frame.winfo_children():
            widget.destroy()
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Plot 1: Price vs. Churn Probability
        ax1.scatter(probabilities, prices, alpha=0.5)
        ax1.set_xlabel('Churn Probability')
        ax1.set_ylabel('Price ($)')
        ax1.set_title('Price vs. Churn Probability')
        
        # Plot 2: Price Distribution
        ax2.hist(prices, bins=20, alpha=0.7, color='skyblue')
        ax2.set_xlabel('Price ($)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Price Distribution')
        
        plt.tight_layout()
        
        # Embed plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.pricing_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def visualize_data(self, viz_type):
        if self.data is None:
            messagebox.showerror("Error", "No data loaded. Please load data first.")
            return
        
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            if viz_type == "correlation":
                # Select only numeric columns
                numeric_cols = self.data.select_dtypes(include=['number']).columns
                corr = self.data[numeric_cols].corr()
                
                # Plot correlation heatmap
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
                ax.set_title('Correlation Heatmap')
                
            elif viz_type == "churn_dist":
                # Churn distribution
                target_col = self.target_var.get()
                if target_col in self.data.columns:
                    counts = self.data[target_col].value_counts()
                    counts.plot(kind='bar', ax=ax)
                    ax.set_title('Churn Distribution')
                    ax.set_xlabel('Churn')
                    ax.set_ylabel('Count')
                    for i, v in enumerate(counts):
                        ax.text(i, v + 5, str(v), ha='center')
                else:
                    messagebox.showerror("Error", f"Target column {target_col} not found in data.")
                    plt.close(fig)
                    return
                
            elif viz_type == "price_churn":
                # Price vs. Churn
                target_col = self.target_var.get()
                price_col = None
                
                # Try to find a price-related column
                price_candidates = ['Price', 'MonthlyCharges', 'MonthlyCost', 'Cost', 'Charge']
                for col in price_candidates:
                    if col in self.data.columns:
                        price_col = col
                        break
                
                if price_col and target_col in self.data.columns:
                    sns.boxplot(x=target_col, y=price_col, data=self.data, ax=ax)
                    ax.set_title(f'{price_col} vs. {target_col}')
                else:
                    messagebox.showerror("Error", "Could not find appropriate price column or target column.")
                    plt.close(fig)
                    return
            
            plt.tight_layout()
            
            # Create new window for plot
            plot_window = tk.Toplevel(self.root)
            plot_window.title(f"Data Visualization - {viz_type}")
            plot_window.geometry("800x600")
            
            # Embed plot in window
            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to visualize data: {str(e)}")


def generate_sample_data():
    """Generate sample customer data for demo purposes"""
    np.random.seed(42)
    n_samples = 1000
    
    # Customer IDs
    customer_ids = [f"CID-{i:05d}" for i in range(1, n_samples + 1)]
    
    # Contract types
    contract_types = ['Monthly', 'One-year', 'Two-year']
    contract = np.random.choice(contract_types, n_samples, p=[0.5, 0.3, 0.2])
    
    # Tenure (months)
    tenure = np.random.randint(1, 72, n_samples)
    
    # Monthly charges ($)
    monthly_charges = 30 + 70 * np.random.beta(2, 5, n_samples)
    
    # Total charges
    total_charges = monthly_charges * tenure * (1 + np.random.normal(0, 0.1, n_samples))
    
    # Online security (Yes/No)
    online_security = np.random.choice(['Yes', 'No'], n_samples)
    
    # Tech support (Yes/No)
    tech_support = np.random.choice(['Yes', 'No'], n_samples)
    
    # Payment method
    payment_methods = ['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card']
    payment_method = np.random.choice(payment_methods, n_samples)
    
    # Paperless billing (Yes/No)
    paperless_billing = np.random.choice(['Yes', 'No'], n_samples)
    
    # Churn (dependent on other variables)
    churn_prob = 0.1 + 0.4 * (monthly_charges > 70).astype(int) - 0.2 * (tenure > 24).astype(int) + \
                 0.2 * (contract == 'Monthly').astype(int) - 0.1 * (online_security == 'Yes').astype(int) - \
                 0.1 * (tech_support == 'Yes').astype(int)
    churn = np.random.binomial(1, np.clip(churn_prob, 0.01, 0.99), n_samples)
    
    # Create DataFrame
    data = pd.DataFrame({
        'CustomerID': customer_ids,
        'Contract': contract,
        'Tenure': tenure,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'OnlineSecurity': online_security,
        'TechSupport': tech_support,
        'PaymentMethod': payment_method,
        'PaperlessBilling': paperless_billing,
        'Churn': churn
    })
    
    return data


def main():
    root = tk.Tk()
    app = ChurnPredictionApp(root)
    
    # Add menu
    menu_bar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Load Data", command=app.load_data)
    file_menu.add_separator()
    file_menu.add_command(label="Generate Sample Data", command=lambda: generate_and_load_sample(app))
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=show_about)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    
    root.config(menu=menu_bar)
    
    root.mainloop()


def generate_and_load_sample(app):
    """Generate sample data and load it into the app"""
    try:
        sample_data = generate_sample_data()
        
        # Save to temporary file
        temp_file = "temp_sample_data.csv"
        sample_data.to_csv(temp_file, index=False)
        
        # Set app.data
        app.data = sample_data
        
        # Update data info text
        app.data_info_text.config(state=tk.NORMAL)
        app.data_info_text.delete(1.0, tk.END)
        app.data_info_text.insert(tk.END, f"Sample data generated successfully\n\n")
        app.data_info_text.insert(tk.END, f"Number of rows: {app.data.shape[0]}\n")
        app.data_info_text.insert(tk.END, f"Number of columns: {app.data.shape[1]}\n\n")
        app.data_info_text.insert(tk.END, "Column information:\n")
        
        for col in app.data.columns:
            app.data_info_text.insert(tk.END, f"- {col}: {app.data[col].dtype}\n")
        
        app.data_info_text.config(state=tk.DISABLED)
        
        # Update data preview
        app.update_data_preview()
        
        # Update target column dropdown
        app.target_combobox['values'] = list(app.data.columns)
        
        # Set up prediction input fields
        app.setup_prediction_inputs()
        
        messagebox.showinfo("Success", "Sample data generated successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate sample data: {str(e)}")


def show_about():
    """Show about dialog"""
    about_text = """
    Customer Churn Prediction with Dynamic Pricing
    
    A simple application to predict customer churn and 
    implement dynamic pricing strategies.
    
    Features:
    - Load CSV data
    - Train machine learning model
    - Predict churn probability
    - Calculate dynamic pricing based on churn risk
    
    Created with Python and Tkinter
    """
    
    messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    main()