import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import requests
import base64
import json
import io

class BoneCancerDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bone Cancer Detection from X-ray Images")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Gemini API settings
        self.api_key = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"  # In a real app, use a secure method to store this
        self.model_name = "gemini-2.0-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        self.create_widgets()
        self.image_path = None
        self.encoded_image = None
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        header_frame.pack(fill=tk.X)
        
        header_label = tk.Label(header_frame, text="Bone Cancer Detection System", 
                               font=("Arial", 20, "bold"), bg="#2c3e50", fg="white")
        header_label.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Left panel for controls
        left_panel = tk.Frame(content_frame, bg="#f0f0f0", width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        instructions_label = tk.Label(left_panel, text="Instructions:", 
                                    font=("Arial", 12, "bold"), bg="#f0f0f0")
        instructions_label.pack(anchor=tk.W, pady=(0, 5))
        
        instructions_text = (
            "1. Click 'Load X-ray Image' to select an X-ray image\n"
            "2. Review the loaded image\n"
            "3. Click 'Detect Cancer' to analyze the image\n"
            "4. View the results in the results section"
        )
        instructions_details = tk.Label(left_panel, text=instructions_text, 
                                      justify=tk.LEFT, bg="#f0f0f0", wraplength=200)
        instructions_details.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        self.load_button = tk.Button(left_panel, text="Load X-ray Image", 
                                   command=self.load_image, bg="#3498db", fg="white",
                                   font=("Arial", 11), padx=10, pady=5)
        self.load_button.pack(fill=tk.X, pady=5)
        
        self.detect_button = tk.Button(left_panel, text="Detect Cancer", 
                                     command=self.detect_cancer, bg="#2ecc71", fg="white",
                                     font=("Arial", 11), padx=10, pady=5, state=tk.DISABLED)
        self.detect_button.pack(fill=tk.X, pady=5)
        
        self.clear_button = tk.Button(left_panel, text="Clear", 
                                    command=self.clear_all, bg="#e74c3c", fg="white",
                                    font=("Arial", 11), padx=10, pady=5)
        self.clear_button.pack(fill=tk.X, pady=5)
        
        # Right panel for image and results
        right_panel = tk.Frame(content_frame, bg="#f0f0f0")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image display area
        image_frame = tk.LabelFrame(right_panel, text="X-ray Image", bg="#f0f0f0", font=("Arial", 12))
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.image_label = tk.Label(image_frame, bg="black")
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results area
        results_frame = tk.LabelFrame(right_panel, text="Detection Results", bg="#f0f0f0", font=("Arial", 12))
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.result_label = tk.Label(results_frame, text="No results yet. Please load an image and run detection.",
                                   bg="#f0f0f0", font=("Arial", 11), wraplength=500, pady=10)
        self.result_label.pack()
        
        # Status bar
        status_frame = tk.Frame(self.root, bg="#2c3e50", pady=5)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg="#2c3e50", fg="white")
        self.status_label.pack()
        
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select X-ray Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        
        if not self.image_path:
            return
        
        try:
            # Load and display the image
            image = Image.open(self.image_path)
            
            # Resize to fit display area while maintaining aspect ratio
            display_width, display_height = 400, 400
            image.thumbnail((display_width, display_height))
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            
            # Enable detect button
            self.detect_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"Loaded image: {os.path.basename(self.image_path)}")
            
            # Encode image for API
            self.encode_image()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def encode_image(self):
        try:
            # Resize image to a reasonable size for the API (not too large)
            image = Image.open(self.image_path)
            image = image.resize((512, 512), Image.LANCZOS)
            
            # Convert to bytes
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_bytes = buffered.getvalue()
            
            # Encode to base64
            self.encoded_image = base64.b64encode(img_bytes).decode('utf-8')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.encoded_image = None
    
    def detect_cancer(self):
        if self.encoded_image is None:
            messagebox.showerror("Error", "No image is loaded or image processing failed.")
            return
        
        try:
            self.status_label.config(text="Analyzing image with Gemini AI...")
            self.root.update()
            
            # Prepare the prompt for Gemini
            prompt = """
            You are a medical AI specializing in bone radiology. Analyze this X-ray image for signs of bone cancer. 
            Look for the following indicators:
            - Osteolytic lesions (bone destruction)
            - Periosteal reaction
            - Soft tissue mass
            - Pathological fractures
            - Cortical bone destruction
            
            Provide:
            1. Your assessment (detected or not detected)
            2. Confidence level (as a percentage)
            3. Brief explanation of findings
            4. Recommendations
            
            Format your response as JSON with these keys: 
            {
                "detection": true/false,
                "confidence": percentage (0-100),
                "findings": "explanation...",
                "recommendations": "advice..."
            }
            """
            
            # Prepare the request to Gemini API
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": self.encoded_image
                                }
                            }
                        ]
                    }
                ],
                "generation_config": {
                    "temperature": 0.4,
                    "top_p": 0.95
                }
            }
            
            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
            
            # Extract the response content
            response_json = response.json()
            
            # Parse the model's response (which may be JSON inside markdown code blocks)
            try:
                result_text = response_json['candidates'][0]['content']['parts'][0]['text']
                
                # Check if the response is wrapped in markdown code blocks
                if result_text.startswith('```json') and result_text.endswith('```'):
                    # Extract the JSON content from within the code block
                    json_text = result_text.replace('```json', '', 1)
                    json_text = json_text.rsplit('```', 1)[0].strip()
                    result_json = json.loads(json_text)
                else:
                    # Try parsing directly if not in code blocks
                    result_json = json.loads(result_text)
                
                # Extract results
                detection = result_json.get('detection', False)
                confidence = result_json.get('confidence', 0)
                findings = result_json.get('findings', "No detailed findings provided.")
                recommendations = result_json.get('recommendations', "No recommendations provided.")
                
                # Format the display result
                if detection:
                    result_text = f"DETECTED: Bone cancer detected with {confidence:.1f}% confidence.\n\n"
                    result_text += f"Findings: {findings}\n\n"
                    result_text += f"Recommendation: {recommendations}"
                    result_color = "#e74c3c"  # Red for positive detection
                else:
                    result_text = f"NOT DETECTED: No signs of bone cancer. {confidence:.1f}% confidence.\n\n"
                    result_text += f"Findings: {findings}\n\n"
                    result_text += f"Recommendation: {recommendations}"
                    result_color = "#2ecc71"  # Green for negative detection
                
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                # If the response is not valid JSON or doesn't have the expected structure
                result_text = "The AI returned an analysis, but in an unexpected format. Raw response:\n\n"
                
                # Get the text response if possible
                try:
                    result_text += response_json['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    result_text += str(response_json)
                
                result_color = "black"
            
            # Update results
            self.result_label.config(text=result_text, fg=result_color)
            self.status_label.config(text="Analysis complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {str(e)}")
            self.status_label.config(text="Analysis failed")
    
    def clear_all(self):
        # Clear image
        self.image_label.config(image='')
        self.image_path = None
        self.encoded_image = None
        
        # Reset buttons and results
        self.detect_button.config(state=tk.DISABLED)
        self.result_label.config(text="No results yet. Please load an image and run detection.", fg="black")
        self.status_label.config(text="Ready")

def main():
    root = tk.Tk()
    app = BoneCancerDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()