import os
import sys
import base64
import requests
import json
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk
import io
import threading
import webbrowser

# Global variables
SAMPLE_IMAGES_DIR = "sample_images"
GEMINI_API_KEY = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"  # Provided API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:generateContent"

# Function to create sample directory and instructions for test images
def setup_test_environment():
    """Create directories and instructions for test images"""
    if not os.path.exists(SAMPLE_IMAGES_DIR):
        os.makedirs(SAMPLE_IMAGES_DIR)
    
    # Create a README file with instructions
    with open(os.path.join(SAMPLE_IMAGES_DIR, "README.txt"), "w") as f:
        f.write("""
MEDICAL IMAGE ANALYSIS SAMPLE IMAGES

To test this application, please download some chest X-ray images from one of these sources:

1. Kaggle Chest X-Ray Dataset: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia
2. COVID-19 Radiography Database: https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database

Save the images in this folder and then use the application to analyze them.

For educational purposes only. Not for clinical use.
        """)
    
    # Open the folder for the user
    if sys.platform == "win32":
        os.system(f'explorer "{os.path.abspath(SAMPLE_IMAGES_DIR)}"')
    elif sys.platform == "darwin":
        os.system(f'open "{os.path.abspath(SAMPLE_IMAGES_DIR)}"')
    else:
        os.system(f'xdg-open "{os.path.abspath(SAMPLE_IMAGES_DIR)}"')

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to analyze medical image using Gemini API
def analyze_medical_image(image_path, api_key, callback):
    """Analyze medical image using Gemini API"""
    def run_analysis():
        try:
            # Check if API key is provided
            if api_key == "YOUR_GEMINI_API_KEY":
                callback({
                    "success": False,
                    "message": "Please enter your Gemini API key in the settings"
                })
                return
            
            # Encode image
            base64_image = encode_image(image_path)
            
            # Prepare headers and payload
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Analyze this medical chest X-ray image and provide the following information:\n1. Is this image normal or does it show signs of disease?\n2. If abnormal, what possible conditions are visible?\n3. What are the key features you observe?\n4. On a scale of 1-5, how confident are you in this assessment?\n\nProvide the analysis in a structured format."},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Make API request
            response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
            
            # Process response
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['candidates'][0]['content']['parts'][0]['text']
                callback({
                    "success": True,
                    "analysis": analysis_text
                })
            else:
                callback({
                    "success": False,
                    "message": f"API Error: {response.status_code} - {response.text}"
                })
                
        except Exception as e:
            callback({
                "success": False,
                "message": f"Error: {str(e)}"
            })
    
    # Run analysis in a separate thread to prevent GUI freezing
    threading.Thread(target=run_analysis).start()

# Function to test API key
def test_api_key(api_key, callback):
    def run_test():
        try:
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }
            
            # Simple test request
            test_payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": "Hello, this is a test request to verify the API key is working."}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:generateContent",
                headers=headers,
                data=json.dumps(test_payload)
            )
            
            if response.status_code == 200:
                callback(True, "API key is valid and working correctly!")
            else:
                callback(False, f"API key test failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            callback(False, f"Error testing API key: {str(e)}")
    
    # Run test in a separate thread
    threading.Thread(target=run_test).start()

# Main application class
class MedicalImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Image Analysis")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Store the API key
        self.api_key = tk.StringVar(value=GEMINI_API_KEY)
        
        # Create the notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Medical Image Analysis")
        
        # Create the settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Set up the analysis tab
        self.setup_analysis_tab()
        
        # Set up the settings tab
        self.setup_settings_tab()
    
    def setup_analysis_tab(self):
        # File selection
        file_frame = ttk.Frame(self.analysis_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Select a medical image to analyze:").pack(side=tk.LEFT, padx=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=50, state="readonly").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        btn_frame = ttk.Frame(self.analysis_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Analyze Image", command=self.analyze_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Get Sample Images", command=self.get_sample_images).pack(side=tk.LEFT, padx=5)
        
        # Image display and results
        content_frame = ttk.Frame(self.analysis_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image panel
        self.image_frame = ttk.LabelFrame(content_frame, text="Image Preview")
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results panel
        results_frame = ttk.LabelFrame(content_frame, text="Analysis Results")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, width=40, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)
    
    def setup_settings_tab(self):
        settings_inner_frame = ttk.Frame(self.settings_frame)
        settings_inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # API Key setting
        api_frame = ttk.Frame(settings_inner_frame)
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="Gemini API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*")
        self.api_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(settings_inner_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Test Key", command=self.test_key).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(settings_inner_frame, text="Instructions")
        instructions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        instructions = """
1. Get a Gemini API key from Google AI Studio (https://makersuite.google.com/app/apikey)
2. Enter your API key above and click "Save Settings"
3. Test your key to ensure it works correctly
4. Go to the "Medical Image Analysis" tab to analyze images
        """
        
        ttk.Label(instructions_frame, text=instructions, justify=tk.LEFT, wraplength=600).pack(padx=10, pady=10, anchor=tk.W)
    
    def browse_file(self):
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            initialdir=os.path.abspath(SAMPLE_IMAGES_DIR) if os.path.exists(SAMPLE_IMAGES_DIR) else os.getcwd(),
            title="Select a medical image",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path.set(filename)
            self.load_image(filename)
    
    def load_image(self, path):
        try:
            # Open and resize image
            img = Image.open(path)
            
            # Calculate resize dimensions to maintain aspect ratio
            display_height = 300
            aspect_ratio = img.width / img.height
            display_width = int(display_height * aspect_ratio)
            
            # Limit max width
            if display_width > 400:
                display_width = 400
                display_height = int(display_width / aspect_ratio)
            
            img = img.resize((display_width, display_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.image_label.config(image=self.photo)
            
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {str(e)}")
    
    def analyze_image(self):
        file_path = self.file_path.get()
        
        if not file_path:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        # Update results text
        self.update_results("Analyzing image... This may take a moment.")
        
        # Call API function with callback
        analyze_medical_image(file_path, self.api_key.get(), self.handle_analysis_result)
    
    def handle_analysis_result(self, result):
        if result["success"]:
            self.update_results(result["analysis"])
        else:
            self.update_results(result["message"])
    
    def update_results(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
    
    def get_sample_images(self):
        self.update_results("Setting up sample images directory and instructions...")
        setup_test_environment()
        self.update_results("Sample images directory has been opened.\n\nPlease download chest X-ray images from the recommended sources in the README file.")
    
    def save_settings(self):
        global GEMINI_API_KEY
        GEMINI_API_KEY = self.api_key.get()
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def test_key(self):
        self.update_results("Testing API key...")
        test_api_key(self.api_key.get(), self.handle_test_result)
    
    def handle_test_result(self, success, message):
        if success:
            messagebox.showinfo("API Test", message)
        else:
            messagebox.showerror("API Test", message)
        
        self.update_results(message)

# Main function
def main():
    root = tk.Tk()
    app = MedicalImageAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()