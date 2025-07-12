#!/usr/bin/env python3
"""
APK Analyzer with Full GUI - Analyzes Android applications (APK files)
Provides a complete graphical interface for analysis and results display
"""

import os
import sys
import zipfile
import tempfile
import subprocess
import re
import math
import shutil
import threading
import webbrowser
from collections import Counter, defaultdict
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class APKAnalysis:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.package_name = os.path.basename(apk_path).replace('.apk', '')
        self.output_dir = os.path.join("analysis_results", self.package_name)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        self.temp_dir = tempfile.mkdtemp()
        
        # Results storage
        self.opcodes = []
        self.permissions = []
        self.api_findings = defaultdict(list)
        self.opcode_counts = Counter()
        self.suspicious_score = 0
        
        # Analysis thresholds - adjustable to reduce false positives
        self.suspicious_threshold = 3  # Number of suspicious patterns needed to flag as suspicious
    
    def __del__(self):
        """Clean up temporary files"""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def analyze(self):
        """Run the full analysis"""
        try:
            # Extract APK contents
            self.extract_apk_contents()
            
            # Analyze components
            self.analyze_manifest()
            self.analyze_dex_files()
            
            # Generate reports
            self.generate_reports()
            
            return True, "Analysis completed successfully"
        except Exception as e:
            return False, f"Error during analysis: {str(e)}"
    
    def extract_apk_contents(self):
        """Extract contents from the APK file"""
        try:
            with zipfile.ZipFile(self.apk_path, 'r') as zip_ref:
                # Extract only the files we need to analyze
                for file in zip_ref.namelist():
                    if file == 'AndroidManifest.xml' or file.endswith('.dex'):
                        # Extract to temp directory
                        zip_ref.extract(file, self.temp_dir)
        except Exception as e:
            raise Exception(f"Failed to extract APK contents: {str(e)}")
    
    def analyze_manifest(self):
        """Analyze the AndroidManifest.xml file"""
        manifest_path = os.path.join(self.temp_dir, 'AndroidManifest.xml')
        if not os.path.exists(manifest_path):
            return
        
        # Define sensitive permissions with risk levels
        sensitive_permissions = {
            'android.permission.SEND_SMS': ('High', 'Can send SMS messages, potentially incurring charges'),
            'android.permission.RECEIVE_SMS': ('Medium', 'Can read SMS messages'),
            'android.permission.READ_CONTACTS': ('Medium', 'Can read contact data'),
            'android.permission.INTERNET': ('Low', 'Can access the internet'),
            'android.permission.ACCESS_FINE_LOCATION': ('High', 'Can access precise location'),
            'android.permission.ACCESS_COARSE_LOCATION': ('Medium', 'Can access approximate location'),
            'android.permission.CAMERA': ('Medium', 'Can access the camera'),
            'android.permission.RECORD_AUDIO': ('Medium', 'Can record audio'),
            'android.permission.READ_PHONE_STATE': ('Medium', 'Can read phone state'),
            'android.permission.READ_CALL_LOG': ('Medium', 'Can read call history'),
            'android.permission.WRITE_EXTERNAL_STORAGE': ('Low', 'Can write to external storage'),
            'android.permission.READ_EXTERNAL_STORAGE': ('Low', 'Can read from external storage')
        }
        
        try:
            # Open manifest file in binary mode
            with open(manifest_path, 'rb') as f:
                manifest_data = f.read()
            
            # Simple pattern matching for permissions
            # This is not as accurate as proper XML parsing but works for basic detection
            for perm, (risk, desc) in sensitive_permissions.items():
                perm_bytes = perm.encode('utf-8')
                if perm_bytes in manifest_data:
                    self.permissions.append({
                        'permission': perm,
                        'risk_level': risk,
                        'description': desc
                    })
                    
                    # Increase suspicious score for higher risk permissions
                    if risk == 'High':
                        self.suspicious_score += 1
                    elif risk == 'Medium':
                        self.suspicious_score += 0.5
        except Exception as e:
            print(f"Error analyzing manifest: {e}")
    
    def analyze_dex_files(self):
        """Analyze DEX files for code patterns"""
        dex_files = [os.path.join(self.temp_dir, f) for f in os.listdir(self.temp_dir) if f.endswith('.dex')]
        
        if not dex_files:
            return
        
        # Define suspicious API patterns with risk levels
        suspicious_apis = {
            'SMS': {
                'patterns': ['sendTextMessage', 'sendMultipartTextMessage', 'SmsManager'],
                'risk': 'High',
                'description': 'App can send SMS messages'
            },
            'Location': {
                'patterns': ['getLastKnownLocation', 'requestLocationUpdates', 'LocationManager'],
                'risk': 'Medium',
                'description': 'App can track location'
            },
            'Device ID': {
                'patterns': ['getDeviceId', 'getSubscriberId', 'getLine1Number', 'IMEI', 'IMSI'],
                'risk': 'Medium',
                'description': 'App can collect device identifiers'
            },
            'Dynamic Code': {
                'patterns': ['DexClassLoader', 'PathClassLoader', 'loadDex', 'loadClass'],
                'risk': 'High',
                'description': 'App can load code dynamically (could bypass security)'
            },
            'Shell Commands': {
                'patterns': ['Runtime.exec', 'ProcessBuilder', 'createSubprocess'],
                'risk': 'High',
                'description': 'App can execute shell commands'
            },
            'Network': {
                'patterns': ['HttpURLConnection', 'Socket', 'createConnection'],
                'risk': 'Low',
                'description': 'App uses network connections'
            },
            'Crypto': {
                'patterns': ['Cipher', 'Crypto', 'encrypt', 'decrypt'],
                'risk': 'Low',
                'description': 'App uses cryptography (may be for legitimate security)'
            }
        }
        
        for dex_file in dex_files:
            try:
                # Analyze the DEX file using simplified approach
                with open(dex_file, 'rb') as f:
                    dex_content = f.read()
                
                # Look for suspicious patterns
                for category, info in suspicious_apis.items():
                    for pattern in info['patterns']:
                        pattern_bytes = pattern.encode('utf-8')
                        if pattern_bytes in dex_content:
                            # Found a match, add to findings
                            self.api_findings[category].append({
                                'pattern': pattern,
                                'risk': info['risk'],
                                'description': info['description']
                            })
                            
                            # Only count each category once for suspicious score
                            if category not in self.opcode_counts:
                                self.opcode_counts[category] = 1
                                
                                # Increase suspicious score based on risk
                                if info['risk'] == 'High':
                                    self.suspicious_score += 1.5
                                elif info['risk'] == 'Medium':
                                    self.suspicious_score += 0.75
                                else:
                                    self.suspicious_score += 0.25
                
                # Look for opcode-like patterns (very simplified)
                common_opcodes = [
                    'invoke-virtual', 'invoke-direct', 'invoke-static',
                    'const-string', 'new-instance', 'iget', 'iput',
                    'if-eq', 'if-ne', 'goto', 'return'
                ]
                
                for opcode in common_opcodes:
                    opcode_bytes = opcode.encode('utf-8')
                    count = dex_content.count(opcode_bytes)
                    if count > 0:
                        self.opcode_counts[opcode] += count
                        self.opcodes.extend([opcode] * count)
            
            except Exception as e:
                print(f"Error analyzing DEX file {dex_file}: {e}")
    
    def generate_reports(self):
        """Generate analysis reports"""
        # Generate permission report
        self._generate_permission_report()
        
        # Generate API findings report
        self._generate_api_report()
        
        # Generate opcode frequency report
        self._generate_opcode_report()
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_permission_report(self):
        """Generate a report of requested permissions"""
        if not self.permissions:
            return
        
        # Create CSV file
        perm_csv = os.path.join(self.output_dir, 'permissions.csv')
        df = pd.DataFrame(self.permissions)
        df.to_csv(perm_csv, index=False)
    
    def _generate_api_report(self):
        """Generate a report of API findings"""
        if not self.api_findings:
            return
        
        # Create a flattened list for CSV
        api_list = []
        for category, findings in self.api_findings.items():
            for finding in findings:
                api_list.append({
                    'category': category,
                    'pattern': finding['pattern'],
                    'risk': finding['risk'],
                    'description': finding['description']
                })
        
        if api_list:
            # Create CSV file
            api_csv = os.path.join(self.output_dir, 'api_findings.csv')
            df = pd.DataFrame(api_list)
            df.to_csv(api_csv, index=False)
    
    def _generate_opcode_report(self):
        """Generate a report of opcode frequencies"""
        if not self.opcode_counts:
            return
        
        # Create CSV file
        opcode_csv = os.path.join(self.output_dir, 'opcode_frequency.csv')
        df = pd.DataFrame([
            {'opcode': opcode, 'count': count}
            for opcode, count in self.opcode_counts.most_common()
        ])
        df.to_csv(opcode_csv, index=False)
        
        # Create a visualization if there are enough opcodes
        if len(df) >= 5:
            plt.figure(figsize=(10, 6))
            top_n = min(15, len(df))
            plt.bar(df['opcode'].head(top_n), df['count'].head(top_n))
            plt.title('Top Opcode Frequencies')
            plt.xlabel('Opcode/Pattern')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            plot_file = os.path.join(self.output_dir, 'opcode_frequency.png')
            plt.savefig(plot_file)
            plt.close()
    
    def _generate_summary_report(self):
        """Generate a summary report"""
        summary_file = os.path.join(self.output_dir, 'summary.html')
        
        # Determine overall risk assessment
        if self.suspicious_score >= self.suspicious_threshold:
            risk_assessment = "High"
            risk_color = "red"
        elif self.suspicious_score >= self.suspicious_threshold / 2:
            risk_assessment = "Medium"
            risk_color = "orange"
        else:
            risk_assessment = "Low"
            risk_color = "green"
        
        # Create HTML summary
        with open(summary_file, 'w') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>APK Analysis Summary: {self.package_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .risk-high {{ color: red; font-weight: bold; }}
                    .risk-medium {{ color: orange; font-weight: bold; }}
                    .risk-low {{ color: green; font-weight: bold; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; }}
                    th {{ background-color: #f2f2f2; text-align: left; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body>
                <h1>APK Analysis Summary</h1>
                <p><strong>File:</strong> {os.path.basename(self.apk_path)}</p>
                <p><strong>Package:</strong> {self.package_name}</p>
                <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Risk Assessment</h2>
                <p>Overall Risk: <span class="risk-{risk_color.lower()}">{risk_assessment}</span></p>
                <p>Risk Score: {self.suspicious_score:.2f} (Threshold for High Risk: {self.suspicious_threshold})</p>
                
                <h2>Requested Permissions ({len(self.permissions)})</h2>
            """)
            
            # Permissions table
            if self.permissions:
                f.write("""
                <table>
                    <tr>
                        <th>Permission</th>
                        <th>Risk Level</th>
                        <th>Description</th>
                    </tr>
                """)
                
                for perm in self.permissions:
                    risk_class = f"risk-{perm['risk_level'].lower()}"
                    f.write(f"""
                    <tr>
                        <td>{perm['permission']}</td>
                        <td class="{risk_class}">{perm['risk_level']}</td>
                        <td>{perm['description']}</td>
                    </tr>
                    """)
                
                f.write("</table>")
            else:
                f.write("<p>No sensitive permissions detected.</p>")
            
            # API findings
            f.write(f"<h2>API Usage Patterns ({sum(len(findings) for findings in self.api_findings.values())})</h2>")
            
            if self.api_findings:
                f.write("""
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Pattern</th>
                        <th>Risk Level</th>
                        <th>Description</th>
                    </tr>
                """)
                
                for category, findings in self.api_findings.items():
                    for finding in findings:
                        risk_class = f"risk-{finding['risk'].lower()}"
                        f.write(f"""
                        <tr>
                            <td>{category}</td>
                            <td>{finding['pattern']}</td>
                            <td class="{risk_class}">{finding['risk']}</td>
                            <td>{finding['description']}</td>
                        </tr>
                        """)
                
                f.write("</table>")
            else:
                f.write("<p>No suspicious API usage patterns detected.</p>")
            
            # Conclusion
            f.write(f"""
                <h2>Conclusion</h2>
                <p>This APK has been analyzed and determined to have a <span class="risk-{risk_color.lower()}">{risk_assessment}</span> risk level.</p>
                
                <p><em>Note: This is an automated analysis and may not detect all potential issues. 
                Manual review is recommended for security-critical applications.</em></p>
            </body>
            </html>
            """)
        
        return risk_assessment, self.suspicious_score

class APKAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("APK Analyzer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set app icon if available
        try:
            self.root.iconbitmap('app_icon.ico')  # Replace with your icon if needed
        except:
            pass
        
        # Initialize variables
        self.apk_path = tk.StringVar()
        self.current_analysis = None
        self.analysis_running = False
        
        # Create the main application frame
        self.create_widgets()
        
        # Ensure the output directory exists
        os.makedirs("analysis_results", exist_ok=True)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create file selection frame
        file_frame = ttk.LabelFrame(main_frame, text="APK File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="APK File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.apk_path, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)
        ttk.Button(file_frame, text="Analyze", command=self.start_analysis).grid(row=0, column=3, sticky=tk.E, padx=5, pady=5)
        
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.create_summary_tab()
        self.create_permissions_tab()
        self.create_api_tab()
        self.create_opcodes_tab()
        self.create_log_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Open Results Folder", command=self.open_results_folder).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="View Report", command=self.view_html_report).pack(side=tk.RIGHT, padx=5)
    
    def create_summary_tab(self):
        """Create the summary tab"""
        self.summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_tab, text="Summary")
        
        # Create summary widgets
        summary_frame = ttk.Frame(self.summary_tab, padding=10)
        summary_frame.pack(fill=tk.BOTH, expand=True)
        
        # App info frame
        app_info_frame = ttk.LabelFrame(summary_frame, text="Application Information", padding=10)
        app_info_frame.pack(fill=tk.X, pady=5)
        
        # App info grid
        self.app_name_var = tk.StringVar(value="")
        self.app_package_var = tk.StringVar(value="")
        self.app_size_var = tk.StringVar(value="")
        
        ttk.Label(app_info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(app_info_frame, textvariable=self.app_name_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(app_info_frame, text="Package:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(app_info_frame, textvariable=self.app_package_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(app_info_frame, text="Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(app_info_frame, textvariable=self.app_size_var).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        app_info_frame.grid_columnconfigure(1, weight=1)
        
        # Risk assessment frame
        risk_frame = ttk.LabelFrame(summary_frame, text="Risk Assessment", padding=10)
        risk_frame.pack(fill=tk.X, pady=10)
        
        self.risk_level_var = tk.StringVar(value="Unknown")
        self.risk_score_var = tk.StringVar(value="0.0")
        
        risk_level_label = ttk.Label(risk_frame, text="Risk Level:")
        risk_level_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.risk_level_display = ttk.Label(risk_frame, textvariable=self.risk_level_var, font=("Arial", 12, "bold"))
        self.risk_level_display.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(risk_frame, text="Risk Score:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(risk_frame, textvariable=self.risk_score_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        risk_frame.grid_columnconfigure(1, weight=1)
        
        # Key findings frame
        findings_frame = ttk.LabelFrame(summary_frame, text="Key Findings", padding=10)
        findings_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.findings_text = scrolledtext.ScrolledText(findings_frame, wrap=tk.WORD, height=10)
        self.findings_text.pack(fill=tk.BOTH, expand=True)
        self.findings_text.config(state=tk.DISABLED)
    
    def create_permissions_tab(self):
        """Create the permissions tab"""
        self.permissions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.permissions_tab, text="Permissions")
        
        # Create a frame with padding
        perm_frame = ttk.Frame(self.permissions_tab, padding=10)
        perm_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for permissions
        columns = ("Permission", "Risk Level", "Description")
        self.perm_tree = ttk.Treeview(perm_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.perm_tree.heading(col, text=col)
            self.perm_tree.column(col, width=100)
        
        # Adjust column widths
        self.perm_tree.column("Permission", width=250)
        self.perm_tree.column("Risk Level", width=100)
        self.perm_tree.column("Description", width=350)
        
        # Add scrollbars
        perm_scroll_y = ttk.Scrollbar(perm_frame, orient=tk.VERTICAL, command=self.perm_tree.yview)
        self.perm_tree.configure(yscrollcommand=perm_scroll_y.set)
        
        # Pack widgets
        self.perm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        perm_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_api_tab(self):
        """Create the API findings tab"""
        self.api_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_tab, text="API Calls")
        
        # Create a frame with padding
        api_frame = ttk.Frame(self.api_tab, padding=10)
        api_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for API findings
        columns = ("Category", "Pattern", "Risk Level", "Description")
        self.api_tree = ttk.Treeview(api_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.api_tree.heading(col, text=col)
            self.api_tree.column(col, width=100)
        
        # Adjust column widths
        self.api_tree.column("Category", width=150)
        self.api_tree.column("Pattern", width=200)
        self.api_tree.column("Risk Level", width=100)
        self.api_tree.column("Description", width=350)
        
        # Add scrollbars
        api_scroll_y = ttk.Scrollbar(api_frame, orient=tk.VERTICAL, command=self.api_tree.yview)
        self.api_tree.configure(yscrollcommand=api_scroll_y.set)
        
        # Pack widgets
        self.api_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        api_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_opcodes_tab(self):
        """Create the opcodes tab"""
        self.opcodes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.opcodes_tab, text="Opcodes")
        
        # Create a frame with padding
        opcodes_frame = ttk.Frame(self.opcodes_tab, padding=10)
        opcodes_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split into two frames - one for chart, one for table
        left_frame = ttk.Frame(opcodes_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(opcodes_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create frame for the chart
        self.chart_frame = ttk.LabelFrame(left_frame, text="Opcode Frequency Chart", padding=10)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Create treeview for opcode frequencies
        opcode_frame = ttk.LabelFrame(right_frame, text="Opcode Frequencies", padding=10)
        opcode_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        columns = ("Opcode", "Count")
        self.opcode_tree = ttk.Treeview(opcode_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.opcode_tree.heading(col, text=col)
            self.opcode_tree.column(col, width=100)
        
        # Add scrollbars
        opcode_scroll_y = ttk.Scrollbar(opcode_frame, orient=tk.VERTICAL, command=self.opcode_tree.yview)
        self.opcode_tree.configure(yscrollcommand=opcode_scroll_y.set)
        
        # Pack widgets
        self.opcode_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        opcode_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_log_tab(self):
        """Create the log tab"""
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="Log")
        
        # Create a frame with padding
        log_frame = ttk.Frame(self.log_tab, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrolled text widget for the log
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Disable editing
        self.log_text.config(state=tk.DISABLED)
    
    def browse_file(self):
        """Open file browser to select APK file"""
        file_path = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        
        if file_path:
            self.apk_path.set(file_path)
            self.log(f"Selected APK file: {file_path}")
    
    def start_analysis(self):
        """Start the APK analysis process"""
        apk_path = self.apk_path.get()
        if not apk_path:
            messagebox.showwarning("No File Selected", "Please select an APK file first.")
            return
        
        if not os.path.isfile(apk_path):
            messagebox.showerror("Invalid File", "The selected file does not exist or is not accessible.")
            return
            
        if not apk_path.lower().endswith('.apk'):
            if not messagebox.askyesno("Warning", "The selected file doesn't have an .apk extension. Continue anyway?"):
                return
        
        # Clear previous analysis results
        self.clear_ui()
        
        # Update UI
        self.status_var.set("Analyzing APK...")
        self.analysis_running = True
        
        # Run analysis in a separate thread to keep UI responsive
        self.log(f"Starting analysis of {apk_path}")
        threading.Thread(target=self._run_analysis, args=(apk_path,), daemon=True).start()
    
    def _run_analysis(self, apk_path):
        """Run the analysis in a separate thread"""
        try:
            # Initialize analysis object
            self.current_analysis = APKAnalysis(apk_path)
            
            # Perform analysis
            success, message = self.current_analysis.analyze()
            
            if success:
                # Update UI with results
                self.root.after(0, self.update_ui_with_results)
                self.log(f"Analysis completed successfully: {apk_path}")
                self.root.after(0, lambda: self.status_var.set("Analysis completed"))
            else:
                self.log(f"Analysis failed: {message}")
                self.root.after(0, lambda: self.status_var.set("Analysis failed"))
                self.root.after(0, lambda: messagebox.showerror("Analysis Failed", message))
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.log(error_msg)
            self.root.after(0, lambda: self.status_var.set("Analysis error"))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.analysis_running = False
    
    def clear_ui(self):
        """Clear the UI elements"""
        # Clear summary tab
        self.app_name_var.set("")
        self.app_package_var.set("")
        self.app_size_var.set("")
        self.risk_level_var.set("Unknown")
        self.risk_score_var.set("0.0")
        
        self.findings_text.config(state=tk.NORMAL)
        self.findings_text.delete(1.0, tk.END)
        self.findings_text.config(state=tk.DISABLED)
        
        # Clear permissions tab
        for item in self.perm_tree.get_children():
            self.perm_tree.delete(item)
            
        # Clear API tab
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
            
        # Clear opcodes tab
        for item in self.opcode_tree.get_children():
            self.opcode_tree.delete(item)
            
        # Clear any existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
    
    def update_ui_with_results(self):
        """Update the UI with analysis results"""
        if not self.current_analysis:
            return
            
        # Update app info
        self.app_name_var.set(os.path.basename(self.current_analysis.apk_path))
        self.app_package_var.set(self.current_analysis.package_name)
        
        try:
            size_bytes = os.path.getsize(self.current_analysis.apk_path)
            size_mb = size_bytes / (1024 * 1024)
            self.app_size_var.set(f"{size_mb:.2f} MB ({size_bytes:,} bytes)")
        except:
            self.app_size_var.set("Unknown")
        
        # Update risk assessment
        risk_score = self.current_analysis.suspicious_score
        self.risk_score_var.set(f"{risk_score:.2f}")
        
        if risk_score >= self.current_analysis.suspicious_threshold:
            risk_level = "High"
            self.risk_level_display.config(foreground="red")
        elif risk_score >= self.current_analysis.suspicious_threshold / 2:
            risk_level = "Medium"
            self.risk_level_display.config(foreground="orange")
        else:
            risk_level = "Low"
            self.risk_level_display.config(foreground="green")
            
        self.risk_level_var.set(risk_level)
        
        # Update findings text
        self.findings_text.config(state=tk.NORMAL)
        self.findings_text.delete(1.0, tk.END)
        
        findings_text = []
        
        # Add permission findings
        if self.current_analysis.permissions:
            high_risk_perms = [p for p in self.current_analysis.permissions if p['risk_level'] == 'High']
            med_risk_perms = [p for p in self.current_analysis.permissions if p['risk_level'] == 'Medium']
            
            if high_risk_perms:
                findings_text.append(f"• Found {len(high_risk_perms)} high-risk permissions")
            if med_risk_perms:
                findings_text.append(f"• Found {len(med_risk_perms)} medium-risk permissions")
        
        # Add API findings
        if self.current_analysis.api_findings:
            for category, findings in self.current_analysis.api_findings.items():
                high_risk = any(f['risk'] == 'High' for f in findings)
                if high_risk:
                    findings_text.append(f"• Detected high-risk {category} behavior")
                else:
                    findings_text.append(f"• Detected {category} behavior")
        
        if not findings_text:
            findings_text.append("No significant security concerns detected.")
        
        self.findings_text.insert(tk.END, "\n".join(findings_text))
        self.findings_text.config(state=tk.DISABLED)
        
        # Update permissions tab
        self.update_permissions_tree()
        
        # Update API tab
        self.update_api_tree()
        
        # Update opcodes tab
        self.update_opcodes_tree()
        self.generate_opcode_chart()
    
    def update_permissions_tree(self):
        """Update the permissions treeview"""
        # Clear existing items
        for item in self.perm_tree.get_children():
            self.perm_tree.delete(item)
            
        if not self.current_analysis or not self.current_analysis.permissions:
            return
            
        # Add permissions to tree
        for perm in self.current_analysis.permissions:
            tag = perm['risk_level'].lower()
            self.perm_tree.insert("", tk.END, values=(
                perm['permission'],
                perm['risk_level'],
                perm['description']
            ), tags=(tag,))
        
        # Configure tag colors
        self.perm_tree.tag_configure('high', foreground='red')
        self.perm_tree.tag_configure('medium', foreground='orange')
        self.perm_tree.tag_configure('low', foreground='green')
    
    def update_api_tree(self):
        """Update the API findings treeview"""
        # Clear existing items
        for item in self.api_tree.get_children():
            self.api_tree.delete(item)
            
        if not self.current_analysis or not self.current_analysis.api_findings:
            return
            
        # Add API findings to tree
        for category, findings in self.current_analysis.api_findings.items():
            for finding in findings:
                tag = finding['risk'].lower()
                self.api_tree.insert("", tk.END, values=(
                    category,
                    finding['pattern'],
                    finding['risk'],
                    finding['description']
                ), tags=(tag,))
        
        # Configure tag colors
        self.api_tree.tag_configure('high', foreground='red')
        self.api_tree.tag_configure('medium', foreground='orange')
        self.api_tree.tag_configure('low', foreground='green')
    
    def update_opcodes_tree(self):
        """Update the opcodes treeview"""
        # Clear existing items
        for item in self.opcode_tree.get_children():
            self.opcode_tree.delete(item)
            
        if not self.current_analysis or not self.current_analysis.opcode_counts:
            return
            
        # Add opcodes to tree
        for opcode, count in self.current_analysis.opcode_counts.most_common():
            self.opcode_tree.insert("", tk.END, values=(opcode, count))
    
    def generate_opcode_chart(self):
        """Generate a chart for opcode frequencies"""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        if not self.current_analysis or not self.current_analysis.opcode_counts:
            return
            
        # Get top opcodes
        top_opcodes = self.current_analysis.opcode_counts.most_common(10)
        if not top_opcodes:
            return
            
        # Create figure
        fig = plt.Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Extract data
        labels = [op[0] for op in top_opcodes]
        values = [op[1] for op in top_opcodes]
        
        # Create bar chart
        bars = ax.bar(labels, values)
        
        # Customize chart
        ax.set_title('Top 10 Opcode Frequencies')
        ax.set_ylabel('Count')
        ax.set_xlabel('Opcode')
        fig.tight_layout()
        
        # Rotate x labels if needed
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def log(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        # Enable text widget, add message, then disable again
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)  # Scroll to end
        self.log_text.config(state=tk.DISABLED)
    
    def open_results_folder(self):
        """Open the results folder in the file explorer"""
        if not self.current_analysis:
            messagebox.showinfo("No Analysis", "No analysis has been performed yet.")
            return
            
        # Try to open the folder with the default file manager
        result_dir = self.current_analysis.output_dir
        if not os.path.exists(result_dir):
            messagebox.showinfo("Folder Not Found", "The results folder could not be found.")
            return
            
        try:
            if sys.platform == 'win32':
                os.startfile(result_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', result_dir])
            else:  # Linux
                subprocess.run(['xdg-open', result_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")
    
    def view_html_report(self):
        """Open the HTML report in a web browser"""
        if not self.current_analysis:
            messagebox.showinfo("No Analysis", "No analysis has been performed yet.")
            return
            
        report_path = os.path.join(self.current_analysis.output_dir, 'summary.html')
        if not os.path.exists(report_path):
            messagebox.showinfo("Report Not Found", "The HTML report could not be found.")
            return
            
        # Open the report in the default web browser
        try:
            self.log(f"Opening HTML report: {report_path}")
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open report: {str(e)}")

def main():
    # Create and run the application
    root = tk.Tk()
    app = APKAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()