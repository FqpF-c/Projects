import pandas as pd
import numpy as np
import random
import os
import tkinter as tk
import seaborn as sns
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory

def generate_simple_dataset(num_transactions=10000, fraud_ratio=0.002, filename="creditcard.csv"):
    """
    Generate a simple credit card transaction dataset for fraud detection testing.
    This generator creates data compatible with the fraud detection program.
    
    Args:
        num_transactions: Number of transactions to generate
        fraud_ratio: Percentage of fraudulent transactions
        filename: Output CSV filename
    
    Returns:
        DataFrame containing the generated data
    """
    print(f"Generating {num_transactions} transactions with {fraud_ratio*100:.2f}% fraud rate...")
    
    # Calculate number of fraudulent transactions
    num_fraud = int(num_transactions * fraud_ratio)
    num_legit = num_transactions - num_fraud
    
    # Create empty dataframe with the right columns
    columns = [f'V{i+1}' for i in range(28)] + ['Amount', 'Class']
    data = []
    
    # Generate legitimate transactions
    for _ in range(num_legit):
        # Create normal distribution features
        features = np.random.normal(0, 1, 28)
        
        # Transaction amount (mostly smaller amounts)
        amount = np.random.choice([
            np.random.uniform(1, 20),       # Small purchases (coffee, etc.)
            np.random.uniform(20, 100),     # Medium purchases
            np.random.uniform(100, 500),    # Larger purchases
            np.random.uniform(500, 3000),   # Big purchases
        ], p=[0.5, 0.3, 0.15, 0.05])
        
        # Create a row with legitimate class (0)
        row = list(features) + [amount, 0]
        data.append(row)
    
    # Generate fraudulent transactions
    for _ in range(num_fraud):
        # Create features that look different from legitimate ones
        features = np.random.normal(0, 1, 28)
        
        # Modify some of the features to create patterns
        # Select random feature indices to modify
        fraud_indices = np.random.choice(range(28), size=8, replace=False)
        
        for idx in fraud_indices:
            # Create anomalous values for these features
            if idx % 3 == 0:
                features[idx] = np.random.normal(3, 1.5)  # Higher mean
            elif idx % 3 == 1:
                features[idx] = np.random.normal(-3, 1.5)  # Lower mean
            else:
                features[idx] = np.random.normal(0, 3)     # Higher variance
        
        # Fraudulent transactions often have unusual amounts
        amount = np.random.choice([
            np.random.uniform(500, 2000),    # Medium-high amounts
            np.random.uniform(2000, 5000),   # High amounts
            np.random.uniform(1, 10),        # Very small amounts (testing)
        ], p=[0.6, 0.3, 0.1])
        
        # Create a row with fraudulent class (1)
        row = list(features) + [amount, 1]
        data.append(row)
    
    # Create DataFrame and shuffle
    df = pd.DataFrame(data, columns=columns)
    df = df.sample(frac=1).reset_index(drop=True)  # Shuffle the data
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"Dataset saved to {filename}")
    
    # Print statistics
    print(f"Total transactions: {len(df)}")
    print(f"Fraudulent transactions: {df['Class'].sum()} ({df['Class'].sum()/len(df)*100:.2f}%)")
    print(f"Amount statistics: min=${df['Amount'].min():.2f}, max=${df['Amount'].max():.2f}, avg=${df['Amount'].mean():.2f}")
    
    return df

class DatasetGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Credit Card Dataset Generator")
        self.root.geometry("500x400")
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Credit Card Fraud Dataset Generator", 
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(main_frame, text="Dataset Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=10)
        
        # Number of transactions
        ttk.Label(params_frame, text="Number of Transactions:").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.num_transactions = tk.IntVar(value=10000)
        ttk.Entry(params_frame, textvariable=self.num_transactions, width=15).grid(column=1, row=0, padx=5)
        
        # Fraud ratio
        ttk.Label(params_frame, text="Fraud Ratio (%):").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.fraud_ratio = tk.DoubleVar(value=0.2)
        ttk.Entry(params_frame, textvariable=self.fraud_ratio, width=15).grid(column=1, row=1, padx=5)
        
        # Output directory
        ttk.Label(params_frame, text="Output Directory:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar(value=os.getcwd())
        ttk.Entry(params_frame, textvariable=self.output_dir, width=30).grid(column=1, row=2, columnspan=2, padx=5)
        ttk.Button(params_frame, text="Browse", command=self.browse_directory).grid(column=3, row=2, padx=5)
        
        # Output filename
        ttk.Label(params_frame, text="Filename:").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.filename = tk.StringVar(value="creditcard.csv")
        ttk.Entry(params_frame, textvariable=self.filename, width=15).grid(column=1, row=3, padx=5)
        
        # Preset buttons frame
        presets_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding="10")
        presets_frame.pack(fill=tk.X, pady=10)
        
        # Preset buttons
        ttk.Button(presets_frame, text="Small Dataset\n(1,000 transactions)", 
                  command=lambda: self.set_preset(1000, 0.2)).grid(column=0, row=0, padx=5, pady=5)
        
        ttk.Button(presets_frame, text="Standard Dataset\n(10,000 transactions)", 
                  command=lambda: self.set_preset(10000, 0.2)).grid(column=1, row=0, padx=5, pady=5)
        
        ttk.Button(presets_frame, text="Large Dataset\n(100,000 transactions)", 
                  command=lambda: self.set_preset(100000, 0.2)).grid(column=2, row=0, padx=5, pady=5)
        
        ttk.Button(presets_frame, text="High Fraud\n(5% fraud rate)", 
                  command=lambda: self.set_preset(10000, 5.0)).grid(column=3, row=0, padx=5, pady=5)
        
        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate Dataset", command=self.generate_dataset)
        generate_btn.pack(pady=20)
        
        # Status text
        self.status_text = tk.Text(main_frame, height=5, width=50)
        self.status_text.pack(fill=tk.X, pady=5)
        self.status_text.insert(tk.END, "Ready to generate dataset.\n")
        self.status_text.config(state=tk.DISABLED)
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = askdirectory()
        if directory:
            self.output_dir.set(directory)
    
    def set_preset(self, transactions, fraud_pct):
        """Set preset values"""
        self.num_transactions.set(transactions)
        self.fraud_ratio.set(fraud_pct)
    
    def generate_dataset(self):
        """Generate the dataset with current parameters"""
        try:
            # Enable status text for updating
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "Generating dataset...\n")
            self.root.update()
            
            # Get parameters
            num_transactions = self.num_transactions.get()
            fraud_ratio = self.fraud_ratio.get() / 100  # Convert percentage to ratio
            output_path = os.path.join(self.output_dir.get(), self.filename.get())
            
            # Redirect print output to status text
            import sys
            old_stdout = sys.stdout
            
            class TextRedirector:
                def __init__(self, text_widget):
                    self.text_widget = text_widget
                
                def write(self, string):
                    self.text_widget.insert(tk.END, string)
                    self.text_widget.see(tk.END)
                    self.text_widget.update()
                
                def flush(self):
                    pass
            
            sys.stdout = TextRedirector(self.status_text)
            
            # Generate dataset
            generate_simple_dataset(num_transactions, fraud_ratio, output_path)
            
            # Restore stdout
            sys.stdout = old_stdout
            
            # Add success message
            self.status_text.insert(tk.END, "\nDataset generated successfully!")
            messagebox.showinfo("Success", f"Dataset with {num_transactions} transactions and {fraud_ratio*100:.2f}% fraud rate has been generated successfully!")
            
        except Exception as e:
            self.status_text.insert(tk.END, f"\nError: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Disable text widget after operation
            self.status_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = DatasetGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()