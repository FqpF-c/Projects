import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import google.generativeai as genai
import threading
import numpy as np
import cv2
from datetime import datetime
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import custom modules for CT scan analysis
from reference_database import CTScanReferenceDatabase
from ct_rules_analyzer import CTScanRulesAnalyzer

# Configure API key for Google Gemini
GOOGLE_API_KEY = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"
genai.configure(api_key=GOOGLE_API_KEY)

class NeurologicalDisorderDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neurological Disorder Detection System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize analyzers
        self.reference_db = CTScanReferenceDatabase()
        self.rules_analyzer = CTScanRulesAnalyzer()
        
        # Initialize UI
        self.setup_ui()
        
        # Initialize Gemini model
        self.model = None
        self.initialize_model()
        
        # For storing analysis results
        self.current_image_path = None
        self.analysis_results = None
        
        # Get reference counts
        self.ref_count = self.reference_db.get_reference_count()
        
        # Update status with reference information
        self.status_var.set(f"Ready. Reference DB: {self.ref_count['normal']} normal, {self.ref_count['abnormal']} abnormal scans")
        
        # Define known normal CT scan patterns to help reduce false positives
        self.normal_patterns = [
            "normal ventricle size",
            "normal cortical thickness",
            "normal gray-white matter differentiation",
            "no visible atrophy",
            "age-appropriate findings",
            "normal brain structure",
            "no abnormal hypodensities",
            "symmetric brain structures",
            "normal sulci"
        ]
    
    def initialize_model(self):
        """Initialize the Gemini model in a separate thread"""
        def load_model():
            try:
                # Initialize specified Gemini model with improved image processing
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.status_var.set("Model loaded successfully. Ready to analyze CT scans.")
            except Exception as e:
                self.status_var.set(f"Error loading model: {str(e)}")
                messagebox.showerror("Model Error", f"Failed to initialize Gemini model: {str(e)}")
        
        self.status_var.set("Loading Gemini model...")
        threading.Thread(target=load_model).start()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Left panel for image and controls
        left_panel = ttk.LabelFrame(main_frame, text="CT Scan Image")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image display area
        self.image_label = ttk.Label(left_panel)
        self.image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        load_btn = ttk.Button(control_frame, text="Load CT Scan", command=self.load_image)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(control_frame, text="Analyze Image", command=self.analyze_image)
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(control_frame, text="Clear", command=self.clear_display)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(control_frame, text="Save Results", command=self.save_results)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Analysis method selection
        analysis_frame = ttk.LabelFrame(left_panel, text="Analysis Method")
        analysis_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.analysis_method = tk.StringVar(value="hybrid")
        
        ttk.Radiobutton(analysis_frame, text="Gemini AI", 
                      variable=self.analysis_method, value="gemini").pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Radiobutton(analysis_frame, text="Rules-Based", 
                      variable=self.analysis_method, value="rules").pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Radiobutton(analysis_frame, text="Reference Database", 
                      variable=self.analysis_method, value="reference").pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Radiobutton(analysis_frame, text="Hybrid (Combined)", 
                      variable=self.analysis_method, value="hybrid").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add reference database controls
        ref_db_frame = ttk.LabelFrame(left_panel, text="Reference Database")
        ref_db_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add to reference database buttons
        add_normal_btn = ttk.Button(ref_db_frame, text="Add as Normal Reference", 
                                   command=lambda: self.add_to_reference(True))
        add_normal_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        add_abnormal_btn = ttk.Button(ref_db_frame, text="Add as Abnormal Reference", 
                                     command=lambda: self.add_to_reference(False))
        add_abnormal_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Display reference count
        self.ref_count_var = tk.StringVar()
        self.update_ref_count_display()
        ref_count_label = ttk.Label(ref_db_frame, textvariable=self.ref_count_var)
        ref_count_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Add comparison visualization button
        vis_btn = ttk.Button(ref_db_frame, text="Compare with References", 
                           command=self.create_reference_comparison)
        vis_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add rules calibration controls
        rules_frame = ttk.LabelFrame(left_panel, text="Rules-Based Analysis")
        rules_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add buttons for rules calibration
        calibrate_btn = ttk.Button(rules_frame, text="Calibrate Rules", command=self.calibrate_rules)
        calibrate_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        visualize_btn = ttk.Button(rules_frame, text="Visualize Rules Analysis", command=self.visualize_rules_analysis)
        visualize_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Right panel for results
        right_panel = ttk.LabelFrame(main_frame, text="Analysis Results")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Results text area
        self.results_text = tk.Text(right_panel, wrap=tk.WORD, width=40, height=20)
        self.results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Graph frame for visualization of progression
        self.graph_frame = ttk.LabelFrame(right_panel, text="Progression Visualization")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def update_ref_count_display(self):
        """Update the reference count display"""
        self.ref_count = self.reference_db.get_reference_count()
        self.ref_count_var.set(f"References: {self.ref_count['normal']} normal, {self.ref_count['abnormal']} abnormal")
    
    def load_image(self):
        """Load a CT scan image from disk"""
        file_path = filedialog.askopenfilename(
            title="Select CT Scan",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.display_image(file_path)
                self.status_var.set(f"Image loaded: {os.path.basename(file_path)}")
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Image loaded. Click 'Analyze Image' to process the CT scan.")
                
                # Clear previous graph if any
                for widget in self.graph_frame.winfo_children():
                    widget.destroy()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                self.status_var.set("Error loading image")
    
    def display_image(self, file_path):
        """Display the loaded image in the UI"""
        try:
            img = Image.open(file_path)
            
            # Resize image to fit in the display area while maintaining aspect ratio
            display_width = 500
            display_height = 400
            img.thumbnail((display_width, display_height))
            
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
        except Exception as e:
            messagebox.showerror("Display Error", f"Failed to display image: {str(e)}")
    
    def analyze_image(self):
        """Analyze the loaded CT scan using the selected method"""
        if not self.current_image_path:
            messagebox.showinfo("Info", "Please load a CT scan image first.")
            return
        
        # Check if Gemini model is needed and loaded
        method = self.analysis_method.get()
        if method in ["gemini", "hybrid"] and not self.model:
            messagebox.showinfo("Info", "The Gemini model is still loading. Please wait.")
            return
            
        self.status_var.set(f"Analyzing CT scan using {method} method...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing... Please wait.\n")
        
        # Run analysis in a separate thread to keep UI responsive
        threading.Thread(target=lambda: self.run_analysis(method)).start()
    
    def run_analysis(self, method):
        """Run the analysis using the specified method"""
        try:
            if method == "gemini":
                self.run_gemini_analysis()
            elif method == "rules":
                self.run_rules_analysis()
            elif method == "reference":
                self.run_reference_analysis()
            elif method == "hybrid":
                self.run_hybrid_analysis()
            else:
                error_msg = f"Unknown analysis method: {method}"
                self.root.after(0, lambda: self.update_status_with_error(error_msg))
                
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def run_gemini_analysis(self):
        """Run the Gemini-based analysis"""
        try:
            # Load image for Gemini
            img = Image.open(self.current_image_path)
            
            # Apply advanced pre-processing to enhance detection of neurodegenerative features
            processed_images = self.enhance_brain_ct(img)
            
            # Create a combined analysis from multiple processed versions
            all_results = []
            
            # Process each enhanced version of the image
            for idx, processed_img in enumerate(processed_images):
                self.status_var.set(f"Analyzing image variant {idx+1}/{len(processed_images)}...")
                
                # Update UI to keep user informed
                self.root.update_idletasks()
                
                # Updated prompt for Alzheimer's and neurodegenerative focus
                prompt = f"""
                You are an advanced neuroradiological analysis system specialized in detecting neurodegenerative disorders from brain CT scans. You are particularly skilled at identifying ALZHEIMER'S DISEASE and other forms of dementia.

                Carefully analyze this brain CT scan for signs of neurodegeneration with special attention to:

                1. VENTRICULAR ENLARGEMENT - this is a key sign of Alzheimer's and other neurodegenerative disorders. Look specifically for:
                   - Dilated lateral ventricles
                   - Enlarged third ventricle
                   - Temporal horn dilatation

                2. CORTICAL ATROPHY patterns - pay close attention to:
                   - Widened sulci (the grooves between gyri)
                   - Reduced overall brain volume
                   - Thinning of the cortex, especially in temporal and parietal regions

                3. HIPPOCAMPAL ATROPHY - visible as:
                   - Enlargement of the hippocampal fissure
                   - Decrease in hippocampal volume

                4. WHITE MATTER CHANGES - look for:
                   - Periventricular hypodensities 
                   - Deep white matter hypodensities

                If ANY of these signs are present, even if subtle or borderline, lean toward classifying as abnormal. For Alzheimer's specifically, look for the combination of ventricular enlargement WITH cortical atrophy, particularly affecting temporal regions.

                Consider that this is image variant {idx+1} of {len(processed_images)}. Each variant has been processed to emphasize different characteristics.

                Format your response as a JSON object with these fields:
                {{
                    "detection": true or false,
                    "confidence_level": number between 0-100,
                    "disorder_type": "string name of disorder if detected",
                    "progression_stage": "string describing stage", 
                    "progression_percentage": number between 0-100,
                    "key_observations": ["observation 1", "observation 2"],
                    "affected_regions": ["region 1", "region 2"],
                    "recommendations": ["recommendation 1", "recommendation 2"]
                }}
                
                IMPORTANT: For neurodegenerative disorders, the presence of enlarged ventricles combined with cortical atrophy is highly significant, even if subtle. In such cases, report with high confidence.
                """
                
                # Run inference on this processed image variant
                response = self.model.generate_content([prompt, processed_img])
                
                # Process response for this image variant
                result_text = response.text
                
                # Try to extract JSON from the response
                try:
                    # Extract JSON if it's within markdown code blocks
                    if "```json" in result_text and "```" in result_text.split("```json")[1]:
                        json_str = result_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in result_text and "```" in result_text.split("```")[1]:
                        json_str = result_text.split("```")[1].split("```")[0].strip()
                    else:
                        # Try to find JSON object in plain text
                        import re
                        json_match = re.search(r'({.*})', result_text.replace('\n', ' '), re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            json_str = result_text
                    
                    # Parse the JSON for this variant
                    variant_result = json.loads(json_str)
                    all_results.append(variant_result)
                    
                except json.JSONDecodeError:
                    # If we can't parse JSON, skip this variant
                    print(f"Failed to parse JSON for variant {idx+1}")
                    continue
            
            # Once all variants are analyzed, combine and prioritize results
            if all_results:
                self.analysis_results = self.combine_variant_results(all_results)
                # Update UI with combined results
                self.root.after(0, self.display_results)
            else:
                # If no variants produced valid results, display error
                self.root.after(0, lambda: self.update_status_with_error("Analysis failed: No valid results from any image variant"))
                
        except Exception as e:
            error_msg = f"Gemini analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def run_rules_analysis(self):
        """Run the rules-based analysis"""
        try:
            # Ask for patient age (optional)
            self.get_patient_age_and_analyze(self.analyze_with_rules)
            
        except Exception as e:
            error_msg = f"Rules analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def analyze_with_rules(self, patient_age=None):
        """Analyze using rules with optional patient age"""
        try:
            # Analyze using rules
            result = self.rules_analyzer.analyze_ct_scan(self.current_image_path, patient_age)
            
            # Store results
            self.analysis_results = result
            
            # Update UI
            self.root.after(0, self.display_results)
            
        except Exception as e:
            error_msg = f"Rules analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def run_reference_analysis(self):
        """Run the reference database analysis"""
        try:
            # Check if we have enough reference data
            ref_count = self.reference_db.get_reference_count()
            if ref_count["normal"] < 5 or ref_count["abnormal"] < 5:
                msg = f"Reference database has insufficient data: {ref_count['normal']} normal, {ref_count['abnormal']} abnormal. " \
                      f"Recommended minimum: 5 of each type."
                
                # Ask if user wants to continue anyway
                if not messagebox.askyesno("Limited Reference Data", 
                                         msg + "\n\nDo you want to continue with limited data?"):
                    self.status_var.set("Analysis cancelled: Insufficient reference data")
                    return
            
            # Get comparison result
            result = self.reference_db.compare_with_references(self.current_image_path)
            
            # Store results
            self.analysis_results = result
            
            # Ensure required fields exist
            if "detection" in result:
                if result["detection"] and "disorder_type" not in result:
                    result["disorder_type"] = "Unspecified neurodegenerative disorder"
                
                # Add empty observation fields if needed for the display function
                if "key_observations" not in result:
                    if result["detection"]:
                        result["key_observations"] = [
                            f"Scan appears similar to abnormal references (similarity: {result['abnormal_similarity']:.2f})",
                            f"Less similar to normal references (similarity: {result['normal_similarity']:.2f})"
                        ]
                    else:
                        result["key_observations"] = [
                            f"Scan appears similar to normal references (similarity: {result['normal_similarity']:.2f})",
                            f"Less similar to abnormal references (similarity: {result['abnormal_similarity']:.2f})"
                        ]
                
                if "affected_regions" not in result and result["detection"]:
                    result["affected_regions"] = ["Based on reference patterns"]
                    
                if "recommendations" not in result:
                    if result["detection"]:
                        result["recommendations"] = [
                            "Consult with a specialist for diagnosis",
                            "Consider additional diagnostic tests",
                            "Review patient's clinical history and symptoms"
                        ]
                    else:
                        result["recommendations"] = [
                            "Regular follow-up as needed",
                            "Consider clinical correlation with patient symptoms"
                        ]
                
                # Update UI
                self.root.after(0, self.display_results)
            else:
                self.root.after(0, lambda: self.update_status_with_error("Analysis failed: Invalid reference database result"))
                
        except Exception as e:
            error_msg = f"Reference analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def run_hybrid_analysis(self):
        """Run a hybrid analysis combining multiple methods"""
        try:
            # Ask for patient age (optional) for rules-based component
            self.get_patient_age_and_analyze(self.perform_hybrid_analysis)
            
        except Exception as e:
            error_msg = f"Hybrid analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def perform_hybrid_analysis(self, patient_age=None):
        """Perform the actual hybrid analysis with optional patient age"""
        try:
            self.status_var.set("Running hybrid analysis...")
            
            results = {}
            confidences = {}
            
            # 1. Run rules-based analysis
            try:
                rules_result = self.rules_analyzer.analyze_ct_scan(self.current_image_path, patient_age)
                results["rules"] = rules_result
                confidences["rules"] = rules_result.get("confidence_level", 0)
            except Exception as e:
                print(f"Rules analysis failed in hybrid mode: {e}")
                results["rules"] = None
            
            # 2. Run reference-based analysis if we have enough reference data
            ref_count = self.reference_db.get_reference_count()
            if ref_count["normal"] >= 3 and ref_count["abnormal"] >= 3:
                try:
                    ref_result = self.reference_db.compare_with_references(self.current_image_path)
                    results["reference"] = ref_result
                    confidences["reference"] = ref_result.get("confidence_level", 0)
                except Exception as e:
                    print(f"Reference analysis failed in hybrid mode: {e}")
                    results["reference"] = None
            
            # 3. Run Gemini analysis if model is loaded
            if self.model:
                try:
                    # We'll use a simplified version to speed up hybrid analysis
                    img = Image.open(self.current_image_path)
                    processed_images = self.enhance_brain_ct(img)[:1]  # Just use first processed image
                    
                    prompt = """
                    You are an advanced neuroradiological analysis system. Analyze this brain CT scan for signs of 
                    neurodegeneration, especially Alzheimer's Disease. Focus on ventricle enlargement, cortical atrophy,
                    hippocampal atrophy, and white matter changes. Format your response as a JSON object with these fields:
                    {
                        "detection": true or false,
                        "confidence_level": number between 0-100,
                        "disorder_type": "string name of disorder if detected",
                        "progression_stage": "string describing stage", 
                        "progression_percentage": number between 0-100,
                        "key_observations": ["observation 1", "observation 2"],
                        "affected_regions": ["region 1", "region 2"],
                        "recommendations": ["recommendation 1", "recommendation 2"]
                    }
                    """
                    
                    response = self.model.generate_content([prompt, processed_images[0]])
                    result_text = response.text
                    
                    # Extract JSON
                    try:
                        if "```json" in result_text and "```" in result_text.split("```json")[1]:
                            json_str = result_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in result_text and "```" in result_text.split("```")[1]:
                            json_str = result_text.split("```")[1].split("```")[0].strip()
                        else:
                            import re
                            json_match = re.search(r'({.*})', result_text.replace('\n', ' '), re.DOTALL)
                            if json_match:
                                json_str = json_match.group(1)
                            else:
                                json_str = result_text
                        
                        ai_result = json.loads(json_str)
                        results["gemini"] = ai_result
                        confidences["gemini"] = ai_result.get("confidence_level", 0)
                    except:
                        print("Failed to parse Gemini JSON in hybrid mode")
                        results["gemini"] = None
                except Exception as e:
                    print(f"Gemini analysis failed in hybrid mode: {e}")
                    results["gemini"] = None
            
            # Now combine the results with weighted voting
            combined_result = self.combine_hybrid_results(results, confidences)
            
            # Store and display
            self.analysis_results = combined_result
            self.root.after(0, self.display_results)
            
        except Exception as e:
            error_msg = f"Hybrid analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status_with_error(error_msg))
    
    def combine_hybrid_results(self, results, confidences):
        """Combine results from multiple analysis methods"""
        # Default empty result
        combined = {
            "detection": False,
            "confidence_level": 0,
            "key_observations": [],
            "affected_regions": [],
            "recommendations": []
        }
        
        # Weight by reliability of each method (adjustable)
        method_weights = {
            "rules": 0.4,
            "reference": 0.35,
            "gemini": 0.25
        }
        
        # Count up weighted votes for detection
        detection_score = 0
        total_weight = 0
        
        available_methods = []
        
        for method, result in results.items():
            if result is not None:
                available_methods.append(method)
                if "detection" in result:
                    # Weight by both method reliability and confidence
                    confidence = confidences.get(method, 50) / 100
                    weight = method_weights[method] * confidence
                    
                    detection_score += weight * (1 if result["detection"] else 0)
                    total_weight += weight
        
        # If we have no valid results, return empty
        if total_weight == 0:
            combined["detection"] = False
            combined["confidence_level"] = 0
            combined["key_observations"].append("Analysis failed: no valid results from any method")
            return combined
        
        # Calculate overall detection result and confidence
        detection_probability = detection_score / total_weight
        combined["detection"] = detection_probability >= 0.5
        combined["confidence_level"] = max(min(round(abs(detection_probability - 0.5) * 200), 100), 30)
        
        # Add note about which methods were used
        method_names = {
            "rules": "Rules-Based Analysis",
            "reference": "Reference Database",
            "gemini": "Gemini AI"
        }
        methods_str = ", ".join([method_names[m] for m in available_methods])
        combined["key_observations"].append(f"Hybrid analysis using: {methods_str}")
        
        # If it's a positive detection, gather other information
        if combined["detection"]:
            # Find disorder type - use the most confident method that detected something
            max_confidence = 0
            for method, result in results.items():
                if result is not None and result.get("detection", False):
                    if confidences.get(method, 0) > max_confidence and "disorder_type" in result:
                        max_confidence = confidences.get(method, 0)
                        combined["disorder_type"] = result["disorder_type"]
            
            # Default if none found
            if "disorder_type" not in combined:
                combined["disorder_type"] = "Unspecified neurodegenerative disorder"
            
            # Calculate progression as weighted average of methods that detected
            progression_values = []
            progression_weights = []
            
            for method, result in results.items():
                if result is not None and result.get("detection", False) and "progression_percentage" in result:
                    confidence = confidences.get(method, 50)
                    progression_values.append(result["progression_percentage"])
                    progression_weights.append(confidence)
            
            if progression_values:
                weighted_sum = sum(p * w for p, w in zip(progression_values, progression_weights))
                total_progression_weight = sum(progression_weights)
                combined["progression_percentage"] = weighted_sum / total_progression_weight
                
                # Set stage based on progression
                if combined["progression_percentage"] < 25:
                    combined["progression_stage"] = "Early"
                elif combined["progression_percentage"] < 50:
                    combined["progression_stage"] = "Mild"
                elif combined["progression_percentage"] < 75:
                    combined["progression_stage"] = "Moderate"
                else:
                    combined["progression_stage"] = "Severe"
        
        # Collect observations, regions and recommendations from all methods
        observations = set()
        regions = set()
        recommendations = set()
        
        for method, result in results.items():
            if result is not None:
                if "key_observations" in result:
                    observations.update(result["key_observations"])
                if "affected_regions" in result:
                    regions.update(result["affected_regions"])
                if "recommendations" in result:
                    recommendations.update(result["recommendations"])
        
        # Add unique items to the combined result
        for obs in observations:
            if obs not in combined["key_observations"]:
                combined["key_observations"].append(obs)
        
        combined["affected_regions"] = list(regions)
        combined["recommendations"] = list(recommendations)
        
        return combined
    
    def get_patient_age_and_analyze(self, analyze_func):
        """Get patient age and then run the analyze function"""
        # Create dialog window for age input
        age_dialog = tk.Toplevel(self.root)
        age_dialog.title("Patient Age")
        age_dialog.geometry("300x150")
        age_dialog.transient(self.root)
        age_dialog.grab_set()
        
        ttk.Label(age_dialog, text="Enter patient age (optional):").pack(pady=10)
        
        age_var = tk.StringVar()
        age_entry = ttk.Entry(age_dialog, textvariable=age_var)
        age_entry.pack(pady=5)
        
        def process_age():
            try:
                age = int(age_var.get()) if age_var.get() else None
                age_dialog.destroy()
                analyze_func(age)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid age or leave blank.")
                
        ttk.Button(age_dialog, text="Analyze", command=process_age).pack(pady=10)
        ttk.Button(age_dialog, text="Skip (Unknown Age)", 
                  command=lambda: [age_dialog.destroy(), analyze_func(None)]).pack(pady=5)
        
        # Center dialog on parent
        age_dialog.update_idletasks()
        width = age_dialog.winfo_width()
        height = age_dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        age_dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def enhance_brain_ct(self, img):
        """Apply advanced pre-processing to enhance neurodegenerative markers"""
        try:
            # Convert to numpy array for OpenCV processing
            img_np = np.array(img)
            
            # Check if the image is grayscale or needs conversion
            if len(img_np.shape) == 3 and img_np.shape[2] > 1:
                img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_np.astype(np.uint8)
            
            # Apply adaptive histogram equalization for better contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            img_enhanced = clahe.apply(img_gray.astype(np.uint8))
            
            # Create multiple enhanced versions to highlight different features
            
            # 1. Edge enhancement to highlight cortical boundaries and atrophy
            # Gaussian blur to reduce noise
            img_blur = cv2.GaussianBlur(img_enhanced, (3, 3), 0)
            # Laplacian for edge detection (sensitive to ventricle borders)
            laplacian = cv2.Laplacian(img_blur, cv2.CV_64F)
            laplacian = np.uint8(np.absolute(laplacian))
            
            # 2. Thresholding to better separate ventricles (often enlarged in neurodegeneration)
            _, ventricle_mask = cv2.threshold(img_enhanced, 30, 255, cv2.THRESH_BINARY_INV)
            
            # 3. Canny edge detection for sulci (widened in atrophy)
            edges = cv2.Canny(img_enhanced, 50, 150)
            
            # 4. Create a composite enhanced image
            # Normalize all images to 0-255 range
            img_enhanced_norm = cv2.normalize(img_enhanced, None, 0, 255, cv2.NORM_MINMAX)
            laplacian_norm = cv2.normalize(laplacian, None, 0, 255, cv2.NORM_MINMAX)
            
            # Weight the images to create a composite highlighting key features
            # Higher weight to original enhanced image but incorporate edge information
            composite = cv2.addWeighted(img_enhanced_norm, 0.7, laplacian_norm, 0.3, 0)
            
            # 5. Apply local contrast enhancement specifically for gray-white matter boundaries
            # Create a mask of mid-range intensities (gray-white boundaries)
            _, gray_white_mask = cv2.threshold(img_enhanced, 70, 255, cv2.THRESH_BINARY)
            _, upper_mask = cv2.threshold(img_enhanced, 180, 255, cv2.THRESH_BINARY)
            gray_white_mask = cv2.bitwise_xor(gray_white_mask, upper_mask)
            
            # Apply additional contrast enhancement to the gray-white boundary areas
            local_contrast = np.copy(composite)
            local_contrast[gray_white_mask > 0] = local_contrast[gray_white_mask > 0] * 1.2
            local_contrast = np.clip(local_contrast, 0, 255).astype(np.uint8)
            
            # 6. Perform ventricle analysis to highlight enlargement
            # Dilate the ventricle mask to ensure full coverage
            kernel = np.ones((3,3), np.uint8)
            ventricle_mask_dilated = cv2.dilate(ventricle_mask, kernel, iterations=2)
            
            # Create ventricle emphasized image
            ventricle_highlight = np.copy(composite)
            # Darken the ventricle areas to emphasize them
            ventricle_highlight[ventricle_mask_dilated > 0] = ventricle_highlight[ventricle_mask_dilated > 0] * 0.7
            ventricle_highlight = np.clip(ventricle_highlight, 0, 255).astype(np.uint8)
            
            # 7. Final composite combining all enhancements
            final_enhanced = cv2.addWeighted(local_contrast, 0.6, ventricle_highlight, 0.4, 0)
            
            # Convert both the original enhanced and the specialized processed images back to PIL
            img_enhanced_pil = Image.fromarray(img_enhanced)
            final_enhanced_pil = Image.fromarray(final_enhanced)
            
            # Create an array of processed images for the model to analyze
            # Using the original plus two enhanced versions increases detection capabilities
            img_array = [img, img_enhanced_pil, final_enhanced_pil]
            
            # Log processing info
            self.status_var.set("Image pre-processing completed with neurodegenerative emphasis")
            
            # Return the array of processed images
            return img_array
            
        except Exception as e:
            # If pre-processing fails, fall back to original image
            print(f"Advanced image pre-processing failed: {e}")
            self.status_var.set(f"Basic pre-processing only: {str(e)}")
            return [img]
            
    def combine_variant_results(self, all_results):
        """Combine results from multiple image variants with emphasis on detecting neurodegeneration"""
        if not all_results:
            return None
            
        if len(all_results) == 1:
            return all_results[0]
            
        # Count detections and non-detections
        detection_count = sum(1 for r in all_results if r.get("detection", False))
        
        # If any variant detects neurodegeneration, prioritize it
        if detection_count > 0:
            # Find the detection with highest confidence
            detected_results = [r for r in all_results if r.get("detection", False)]
            most_confident = max(detected_results, key=lambda x: x.get("confidence_level", 0))
            
            # For key_observations, combine from all variants that detected something
            all_observations = []
            all_regions = []
            all_recommendations = []
            
            for r in detected_results:
                # Add unique observations
                for obs in r.get("key_observations", []):
                    if obs not in all_observations:
                        all_observations.append(obs)
                
                # Add unique affected regions
                for region in r.get("affected_regions", []):
                    if region not in all_regions:
                        all_regions.append(region)
                
                # Add unique recommendations
                for rec in r.get("recommendations", []):
                    if rec not in all_recommendations:
                        all_recommendations.append(rec)
            
            # Update the most confident result with combined information
            most_confident["key_observations"] = all_observations
            most_confident["affected_regions"] = all_regions
            most_confident["recommendations"] = all_recommendations
            
            # Increase confidence level since multiple variants detected issues
            if detection_count > 1:
                most_confident["confidence_level"] = min(most_confident.get("confidence_level", 0) + 10, 100)
                
            return most_confident
        else:
            # No variants detected anything, return the most confident negative result
            return max(all_results, key=lambda x: x.get("confidence_level", 0))
    
    def display_results(self):
        """Display the analysis results in the UI"""
        results = self.analysis_results
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Extract confidence level
        confidence = results.get("confidence_level", 50) 
        
        # Display results based on detection
        if results["detection"]:
            self.results_text.insert(tk.END, f"⚠️ NEURODEGENERATIVE DISORDER DETECTED (Confidence: {confidence}%)\n\n", "heading")
            
            if "disorder_type" in results:
                self.results_text.insert(tk.END, f"Type: {results['disorder_type']}\n\n")
            
            # Progression info
            if "progression_stage" in results:
                self.results_text.insert(tk.END, f"Progression Stage: {results['progression_stage']}\n")
            if "progression_percentage" in results:
                self.results_text.insert(tk.END, f"Progression: {results['progression_percentage']}%\n\n")
            
            # Key observations
            if "key_observations" in results and results["key_observations"]:
                self.results_text.insert(tk.END, "Key Observations:\n", "subheading")
                for observation in results["key_observations"]:
                    self.results_text.insert(tk.END, f"• {observation}\n")
                self.results_text.insert(tk.END, "\n")
            
            # Affected regions
            if "affected_regions" in results and results["affected_regions"]:
                self.results_text.insert(tk.END, "Affected Brain Regions:\n", "subheading")
                for region in results["affected_regions"]:
                    self.results_text.insert(tk.END, f"• {region}\n")
                self.results_text.insert(tk.END, "\n")
            
            # Recommendations
            if "recommendations" in results and results["recommendations"]:
                self.results_text.insert(tk.END, "Recommendations:\n", "subheading")
                for rec in results["recommendations"]:
                    self.results_text.insert(tk.END, f"• {rec}\n")
                    
            # Create visualization
            self.create_progression_visualization()
        else:
            self.results_text.insert(tk.END, f"✓ NO NEURODEGENERATIVE DISORDER DETECTED (Confidence: {confidence}%)\n\n", "heading")
            self.results_text.insert(tk.END, "The scan appears normal without significant signs of neurodegeneration.\n\n")
            
            if "key_observations" in results and results["key_observations"]:
                self.results_text.insert(tk.END, "Observations:\n", "subheading")
                for observation in results["key_observations"]:
                    self.results_text.insert(tk.END, f"• {observation}\n")
                self.results_text.insert(tk.END, "\n")
            
            if "recommendations" in results and results["recommendations"]:
                self.results_text.insert(tk.END, "Recommendations:\n", "subheading")
                for rec in results["recommendations"]:
                    self.results_text.insert(tk.END, f"• {rec}\n")
            
        # Add text tags for styling
        self.results_text.tag_configure("heading", font=("Arial", 12, "bold"))
        self.results_text.tag_configure("subheading", font=("Arial", 10, "bold"))
        
        # Update status
        self.status_var.set("Analysis complete.")
    
    def create_progression_visualization(self):
        """Create a visual representation of the disease progression"""
        # Clear previous visualization
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        if not self.analysis_results or not self.analysis_results.get("detection") or "progression_percentage" not in self.analysis_results:
            return
            
        # Create figure for plot
        fig, ax = plt.subplots(figsize=(5, 3))
        
        # Get progression percentage
        progression = self.analysis_results.get("progression_percentage", 0)
        
        # Create gauge chart for progression
        stages = ["Early", "Mild", "Moderate", "Severe"]
        stage_colors = ["#00ff00", "#ffff00", "#ffa500", "#ff0000"]
        stage_ranges = [0, 25, 50, 75, 100]
        
        # Plot the stages background
        for i in range(len(stages)):
            ax.axvspan(stage_ranges[i], stage_ranges[i+1], alpha=0.3, color=stage_colors[i], ec="none")
            
        # Plot the progression marker
        ax.arrow(0, 0, progression, 0, head_width=0.5, head_length=2, fc='blue', ec='blue', linewidth=8)
        
        # Customize plot
        ax.set_xlim(0, 100)
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
        
        for i, stage in enumerate(stages):
            ax.text((stage_ranges[i] + stage_ranges[i+1]) / 2, 0.5, stage, ha='center', fontsize=9)
            
        ax.set_title(f"Disease Progression: {progression:.1f}%")
        ax.grid(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        # Embed the plot in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def add_to_reference(self, is_normal):
        """Add current scan to reference database"""
        if not self.current_image_path:
            messagebox.showinfo("Info", "Please load a CT scan image first.")
            return
        
        # If we have analysis results, use them as metadata
        metadata = None
        if self.analysis_results:
            metadata = {
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # If it's an abnormal reference, add disorder information
            if not is_normal and "disorder_type" in self.analysis_results:
                metadata["disorder_type"] = self.analysis_results["disorder_type"]
                metadata["progression_percentage"] = self.analysis_results.get("progression_percentage", 50)
                metadata["progression_stage"] = self.analysis_results.get("progression_stage", "Moderate")
        
        try:
            # Add to reference database
            self.reference_db.add_reference_scan(self.current_image_path, is_normal, metadata)
            
            # Update reference count display
            self.update_ref_count_display()
            
            # Show success message
            category = "normal" if is_normal else "abnormal"
            messagebox.showinfo("Success", f"Image added to {category} reference database.")
            self.status_var.set(f"Added to {category} reference database.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to reference database: {str(e)}")
    
    def create_reference_comparison(self):
        """Create visualization comparing current scan with reference database"""
        if not self.current_image_path:
            messagebox.showinfo("Info", "Please load a CT scan image first.")
            return
            
        try:
            # Create a temporary file for the comparison visualization
            output_path = os.path.join(os.path.dirname(self.current_image_path), 
                                      f"comparison_{os.path.basename(self.current_image_path)}")
            
            # Generate comparison visualization
            self.reference_db.export_comparison_visualization(self.current_image_path, output_path)
            
            # Show success message
            messagebox.showinfo("Success", f"Comparison visualization saved to {output_path}")
            self.status_var.set(f"Comparison created: {os.path.basename(output_path)}")
            
            # Try to open the visualization
            try:
                import webbrowser
                webbrowser.open(output_path)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create comparison: {str(e)}")
    
    def calibrate_rules(self):
        """Open a dialog to select normal and abnormal CT scans for rules calibration"""
        # Ask for directory with normal CT scans
        messagebox.showinfo("Calibration", "Select directory containing NORMAL CT scans")
        normal_dir = filedialog.askdirectory(title="Select Directory with Normal CT Scans")
        if not normal_dir:
            return
            
        # Ask for directory with abnormal CT scans
        messagebox.showinfo("Calibration", "Select directory containing ABNORMAL CT scans")
        abnormal_dir = filedialog.askdirectory(title="Select Directory with Abnormal CT Scans")
        if not abnormal_dir:
            return
            
        # Get all image files from directories
        normal_images = []
        abnormal_images = []
        
        # Supported image extensions
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']
        
        # Get normal images
        for filename in os.listdir(normal_dir):
            if any(filename.lower().endswith(ext) for ext in valid_extensions):
                normal_images.append(os.path.join(normal_dir, filename))
                
        # Get abnormal images
        for filename in os.listdir(abnormal_dir):
            if any(filename.lower().endswith(ext) for ext in valid_extensions):
                abnormal_images.append(os.path.join(abnormal_dir, filename))
        
        if len(normal_images) == 0 or len(abnormal_images) == 0:
            messagebox.showerror("Error", "Not enough images found. Need at least one normal and one abnormal scan.")
            return
            
        # Show calibration progress
        self.status_var.set(f"Calibrating rules using {len(normal_images)} normal and {len(abnormal_images)} abnormal scans...")
        self.root.update_idletasks()
        
        # Run calibration in a separate thread
        def run_calibration():
            try:
                stats = self.rules_analyzer.calibrate_rules(normal_images, abnormal_images)
                self.root.after(0, lambda: self.show_calibration_results(stats))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Calibration Error", f"Error during calibration: {str(e)}"))
                self.root.after(0, lambda: self.status_var.set("Calibration failed."))
                
        threading.Thread(target=run_calibration).start()
    
    def show_calibration_results(self, stats):
        """Display calibration results"""
        if "error" in stats:
            messagebox.showerror("Calibration Error", stats["error"])
            self.status_var.set("Calibration failed.")
            return
            
        # Create a summary of calibration results
        result_window = tk.Toplevel(self.root)
        result_window.title("Calibration Results")
        result_window.geometry("500x400")
        
        # Add scrollable text area
        result_text = tk.Text(result_window, wrap=tk.WORD, width=60, height=20)
        result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=result_text.yview)
        
        # Add results content
        result_text.insert(tk.END, "Rules Calibration Results\n\n", "heading")
        
        # Show statistics for each feature
        if "ventricle_size" in stats:
            result_text.insert(tk.END, "Ventricular Size:\n", "subheading")
            vs_stats = stats["ventricle_size"]
            result_text.insert(tk.END, f"Normal scans: mean={vs_stats['normal_mean']:.2f}, std={vs_stats['normal_std']:.2f}\n")
            result_text.insert(tk.END, f"Abnormal scans: mean={vs_stats['abnormal_mean']:.2f}, std={vs_stats['abnormal_std']:.2f}\n")
            result_text.insert(tk.END, "New thresholds:\n")
            for name, val in vs_stats["thresholds"].items():
                result_text.insert(tk.END, f"- {name}: {val:.2f}\n")
            result_text.insert(tk.END, "\n")
        
        if "sulci_width" in stats:
            result_text.insert(tk.END, "Cortical Atrophy (Sulci Width):\n", "subheading")
            sw_stats = stats["sulci_width"]
            result_text.insert(tk.END, f"Normal scans: mean={sw_stats['normal_mean']:.2f}, std={sw_stats['normal_std']:.2f}\n")
            result_text.insert(tk.END, f"Abnormal scans: mean={sw_stats['abnormal_mean']:.2f}, std={sw_stats['abnormal_std']:.2f}\n")
            result_text.insert(tk.END, "New thresholds:\n")
            for name, val in sw_stats["thresholds"].items():
                result_text.insert(tk.END, f"- {name}: {val:.2f}\n")
            result_text.insert(tk.END, "\n")
        
        if "symmetry" in stats:
            result_text.insert(tk.END, "Brain Symmetry:\n", "subheading")
            sym_stats = stats["symmetry"]
            result_text.insert(tk.END, f"Normal scans: mean={sym_stats['normal_mean']:.2f}, std={sym_stats['normal_std']:.2f}\n")
            result_text.insert(tk.END, f"Abnormal scans: mean={sym_stats['abnormal_mean']:.2f}, std={sym_stats['abnormal_std']:.2f}\n")
            result_text.insert(tk.END, "New thresholds:\n")
            for name, val in sym_stats["thresholds"].items():
                result_text.insert(tk.END, f"- {name}: {val:.2f}\n")
            result_text.insert(tk.END, "\n")
        
        if "gray_white_ratio" in stats:
            result_text.insert(tk.END, "Gray-White Matter Differentiation:\n", "subheading")
            gw_stats = stats["gray_white_ratio"]
            result_text.insert(tk.END, f"Normal scans: mean={gw_stats['normal_mean']:.2f}, std={gw_stats['normal_std']:.2f}\n")
            result_text.insert(tk.END, f"Abnormal scans: mean={gw_stats['abnormal_mean']:.2f}, std={gw_stats['abnormal_std']:.2f}\n")
            result_text.insert(tk.END, "New thresholds:\n")
            for name, val in gw_stats["thresholds"].items():
                result_text.insert(tk.END, f"- {name}: {val:.2f}\n")
            result_text.insert(tk.END, "\n")
        
        # Add overall summary
        result_text.insert(tk.END, "\nCalibration complete. The rules have been updated based on your reference images.\n")
        result_text.insert(tk.END, "These rules will now be used for future analysis.\n")
        
        # Add text styles
        result_text.tag_configure("heading", font=("Arial", 12, "bold"))
        result_text.tag_configure("subheading", font=("Arial", 10, "bold"))
        
        # Update status
        self.status_var.set("Rules calibration completed successfully.")
    
    def visualize_rules_analysis(self):
        """Visualize the rules-based analysis of the current image"""
        if not self.current_image_path:
            messagebox.showinfo("Info", "Please load a CT scan image first.")
            return
            
        try:
            # Ask for patient age (optional)
            self.get_patient_age_and_analyze(self.run_rules_visualization)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error initializing visualization: {str(e)}")
    
    def run_rules_visualization(self, patient_age):
        """Run the rules-based analysis visualization with the given patient age"""
        try:
            self.status_var.set("Running rules-based analysis...")
            
            # Run analysis in a separate thread
            def analyze_thread():
                try:
                    # Analyze using rules
                    result = self.rules_analyzer.analyze_ct_scan(self.current_image_path, patient_age)
                    
                    # Create visualization
                    output_path = os.path.join(os.path.dirname(self.current_image_path), 
                                              f"rules_analysis_{os.path.basename(self.current_image_path)}")
                    vis_path = self.rules_analyzer.visualize_analysis(self.current_image_path, result, output_path)
                    
                    # Store results
                    self.analysis_results = result
                    
                    # Show results in UI
                    self.root.after(0, lambda: self.show_rules_results(result, vis_path))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Analysis Error", 
                                                                   f"Error in rules analysis: {str(e)}"))
                    self.root.after(0, lambda: self.status_var.set("Rules analysis failed."))
            
            threading.Thread(target=analyze_thread).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error running visualization: {str(e)}")
    
    def show_rules_results(self, result, visualization_path):
        """Display the rules-based analysis results"""
        # Update status
        self.status_var.set("Rules analysis complete.")
        
        # Display results in results panel
        self.results_text.delete(1.0, tk.END)
        
        # Format header based on detection result
        if result["detection"]:
            self.results_text.insert(tk.END, f"⚠️ NEURODEGENERATIVE DISORDER DETECTED (Confidence: {result['confidence_level']:.1f}%)\n\n", "heading")
            if "disorder_type" in result:
                self.results_text.insert(tk.END, f"Type: {result['disorder_type']}\n\n")
                
            # Progression info if available
            if "progression_stage" in result:
                self.results_text.insert(tk.END, f"Progression Stage: {result['progression_stage']}\n")
            if "progression_percentage" in result:
                self.results_text.insert(tk.END, f"Progression: {result['progression_percentage']:.1f}%\n\n")
        else:
            self.results_text.insert(tk.END, f"✓ NO NEURODEGENERATIVE DISORDER DETECTED (Confidence: {result['confidence_level']:.1f}%)\n\n", "heading")
        
        # Key observations
        if "key_observations" in result and result["key_observations"]:
            self.results_text.insert(tk.END, "Key Observations:\n", "subheading")
            for observation in result["key_observations"]:
                self.results_text.insert(tk.END, f"• {observation}\n")
            self.results_text.insert(tk.END, "\n")
        
        # Affected regions
        if "affected_regions" in result and result["affected_regions"]:
            self.results_text.insert(tk.END, "Affected Brain Regions:\n", "subheading")
            for region in result["affected_regions"]:
                self.results_text.insert(tk.END, f"• {region}\n")
            self.results_text.insert(tk.END, "\n")
        
        # Recommendations
        if "recommendations" in result and result["recommendations"]:
            self.results_text.insert(tk.END, "Recommendations:\n", "subheading")
            for rec in result["recommendations"]:
                self.results_text.insert(tk.END, f"• {rec}\n")
            
        # Add text tags for styling
        self.results_text.tag_configure("heading", font=("Arial", 12, "bold"))
        self.results_text.tag_configure("subheading", font=("Arial", 10, "bold"))
        
        # Create progression visualization if this is a positive detection
        if result["detection"] and "progression_percentage" in result:
            self.create_progression_visualization()
            
        # Display visualization image
        try:
            # Open visualization in default image viewer
            import webbrowser
            webbrowser.open(visualization_path)
        except:
            messagebox.showinfo("Visualization", f"Analysis visualization saved to:\n{visualization_path}")
    
    def update_status_with_error(self, error_msg):
        """Update status bar with error message"""
        self.status_var.set(error_msg)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Error: {error_msg}\n\nPossible causes:\n- API key may be invalid\n- Internet connection issues\n- Image format not supported\n- Image too large or complex")
        messagebox.showerror("Analysis Error", error_msg)
    
    def clear_display(self):
        """Clear the current display"""
        self.image_label.configure(image=None)
        self.image_label.image = None
        self.results_text.delete(1.0, tk.END)
        self.current_image_path = None
        self.analysis_results = None
        
        # Clear visualization
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        self.status_var.set("Display cleared")
    
    def save_results(self):
        """Save the analysis results to a file"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Analysis Results"
        )
        
        if file_path:
            try:
                # Add metadata to results
                save_data = self.analysis_results.copy()
                save_data["analysis_timestamp"] = datetime.now().isoformat()
                save_data["image_analyzed"] = os.path.basename(self.current_image_path) if self.current_image_path else "Unknown"
                save_data["analysis_method"] = self.analysis_method.get()
                
                with open(file_path, 'w') as f:
                    json.dump(save_data, f, indent=4)
                    
                self.status_var.set(f"Results saved to {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Analysis results saved successfully.")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save results: {str(e)}")


def main():
    root = tk.Tk()
    app = NeurologicalDisorderDetectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()