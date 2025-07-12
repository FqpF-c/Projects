import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import google.generativeai as genai
import threading

class MusicRecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Recommendation & Content Generation")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f5f5f5")
        
        # Configure custom styles
        self.configure_styles()
        
        # Configure API key
        self.api_key = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # User preferences
        self.preferences = {
            "favorite_genres": [],
            "favorite_artists": [],
            "mood": "",
            "energy_level": "",
            "release_year_range": "",
            "instruments": []
        }
        
        # File path for saving preferences
        self.preferences_file = "music_preferences.json"
        
        # Create UI
        self.create_ui()
        
        # Load preferences if file exists
        self.load_preferences()
        
    def configure_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        
        # Configure colors
        bg_color = "#f5f5f5"
        accent_color = "#4a86e8"
        
        # Configure the notebook style
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e0e0", padding=[10, 5], font=("Arial", 11))
        style.map("TNotebook.Tab", background=[("selected", accent_color)], 
                 foreground=[("selected", "white")])
        
        # Configure frames
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color)
        style.configure("TLabelframe.Label", font=("Arial", 11, "bold"), background=bg_color)
        
        # Configure buttons
        style.configure("TButton", font=("Arial", 10), background=accent_color)
        style.map("TButton", background=[("active", "#3a76d8")])
        
        # Configure labels
        style.configure("TLabel", background=bg_color, font=("Arial", 10))
        
        # Configure entry fields
        style.configure("TEntry", fieldbackground="white")
        
        # Configure combobox
        style.configure("TCombobox", fieldbackground="white")

    def create_ui(self):
        # Create main notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for each tab
        self.preferences_frame = ttk.Frame(self.notebook)
        self.recommendation_frame = ttk.Frame(self.notebook)
        self.content_generation_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(self.preferences_frame, text="Preferences")
        self.notebook.add(self.recommendation_frame, text="Get Recommendations")
        self.notebook.add(self.content_generation_frame, text="Generate Content")
        
        # Set up each tab
        self.setup_preferences_tab()
        self.setup_recommendation_tab()
        self.setup_content_generation_tab()

    def setup_preferences_tab(self):
        # Frame for genre selection
        genre_frame = ttk.LabelFrame(self.preferences_frame, text="Favorite Genres")
        genre_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.genre_var = tk.StringVar()
        common_genres = ["Rock", "Pop", "Hip Hop", "R&B", "Country", "Electronic", 
                        "Jazz", "Classical", "Metal", "Folk", "Blues", "Reggae", "Indie"]
        
        self.genre_entry = ttk.Combobox(genre_frame, textvariable=self.genre_var, values=common_genres)
        self.genre_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_genre_btn = ttk.Button(genre_frame, text="Add Genre", command=self.add_genre)
        self.add_genre_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.genre_listbox = tk.Listbox(genre_frame, height=5)
        self.genre_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        self.remove_genre_btn = ttk.Button(genre_frame, text="Remove Selected Genre", command=self.remove_genre)
        self.remove_genre_btn.pack(padx=5, pady=5)
        
        # Frame for artist selection
        artist_frame = ttk.LabelFrame(self.preferences_frame, text="Favorite Artists")
        artist_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.artist_var = tk.StringVar()
        self.artist_entry = ttk.Entry(artist_frame, textvariable=self.artist_var)
        self.artist_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_artist_btn = ttk.Button(artist_frame, text="Add Artist", command=self.add_artist)
        self.add_artist_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.artist_listbox = tk.Listbox(artist_frame, height=5)
        self.artist_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        self.remove_artist_btn = ttk.Button(artist_frame, text="Remove Selected Artist", command=self.remove_artist)
        self.remove_artist_btn.pack(padx=5, pady=5)
        
        # Mood selection
        mood_frame = ttk.LabelFrame(self.preferences_frame, text="Mood")
        mood_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.mood_var = tk.StringVar()
        moods = ["Happy", "Sad", "Energetic", "Calm", "Romantic", "Angry", "Nostalgic", "Focused", "Dreamy", "Upbeat"]
        self.mood_combobox = ttk.Combobox(mood_frame, textvariable=self.mood_var, values=moods)
        self.mood_combobox.pack(padx=5, pady=5)
        
        # Energy level
        energy_frame = ttk.LabelFrame(self.preferences_frame, text="Energy Level")
        energy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.energy_var = tk.StringVar()
        energy_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
        self.energy_combobox = ttk.Combobox(energy_frame, textvariable=self.energy_var, values=energy_levels)
        self.energy_combobox.pack(padx=5, pady=5)
        
        # Release year range
        year_frame = ttk.LabelFrame(self.preferences_frame, text="Release Year Range")
        year_frame.pack(fill=tk.X, padx=10, pady=5)
        
        year_inner_frame = ttk.Frame(year_frame)
        year_inner_frame.pack(padx=5, pady=5)
        
        ttk.Label(year_inner_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.year_from_var = tk.StringVar()
        self.year_from_entry = ttk.Entry(year_inner_frame, textvariable=self.year_from_var, width=10)
        self.year_from_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(year_inner_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.year_to_var = tk.StringVar()
        self.year_to_entry = ttk.Entry(year_inner_frame, textvariable=self.year_to_var, width=10)
        self.year_to_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Instruments
        instrument_frame = ttk.LabelFrame(self.preferences_frame, text="Featured Instruments")
        instrument_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.instrument_var = tk.StringVar()
        common_instruments = ["Guitar", "Piano", "Drums", "Bass", "Violin", "Saxophone", 
                             "Trumpet", "Synth", "Flute", "Cello", "Harp"]
        
        self.instrument_entry = ttk.Combobox(instrument_frame, textvariable=self.instrument_var, values=common_instruments)
        self.instrument_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.add_instrument_btn = ttk.Button(instrument_frame, text="Add Instrument", command=self.add_instrument)
        self.add_instrument_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.instrument_listbox = tk.Listbox(instrument_frame, height=5)
        self.instrument_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        self.remove_instrument_btn = ttk.Button(instrument_frame, text="Remove Selected Instrument", command=self.remove_instrument)
        self.remove_instrument_btn.pack(padx=5, pady=5)
        
        # Buttons to save and load preferences
        btn_frame = ttk.Frame(self.preferences_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.save_btn = ttk.Button(btn_frame, text="Save Preferences", command=self.save_preferences)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_btn = ttk.Button(btn_frame, text="Load Preferences", command=self.load_preferences_dialog)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)

    def setup_recommendation_tab(self):
        frame = ttk.Frame(self.recommendation_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Get Music Recommendations Based On Your Preferences", font=("Arial", 14)).pack(pady=10)
        
        self.recommendation_btn = ttk.Button(frame, text="Get Recommendations", command=self.get_recommendations)
        self.recommendation_btn.pack(pady=10)
        
        # Text area for displaying recommendations
        self.recommendation_text = tk.Text(frame, height=20, width=80, wrap=tk.WORD)
        self.recommendation_text.pack(pady=10, fill=tk.BOTH, expand=True)
        self.recommendation_text.config(state=tk.DISABLED)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.recommendation_text, command=self.recommendation_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recommendation_text.config(yscrollcommand=scrollbar.set)

    def setup_content_generation_tab(self):
        frame = ttk.Frame(self.content_generation_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Content Generation", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Content request input
        input_frame = ttk.LabelFrame(frame, text="What would you like to generate?")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.content_input_var = tk.StringVar()
        self.content_input_text = tk.Text(input_frame, height=4, width=70, wrap=tk.WORD)
        self.content_input_text.pack(padx=10, pady=10, fill=tk.X)
        
        # Example prompts to help users
        examples_frame = ttk.Frame(frame)
        examples_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(examples_frame, text="Examples:", font=("Arial", 10, "italic")).pack(anchor="w")
        example_btn1 = ttk.Button(examples_frame, text="Write a short story", 
                                 command=lambda: self.set_example_prompt("Write a short story about a musician who discovers a magical instrument"))
        example_btn1.pack(side=tk.LEFT, padx=5, pady=5)
        
        example_btn2 = ttk.Button(examples_frame, text="Create a poem", 
                                 command=lambda: self.set_example_prompt("Create a poem about the changing seasons"))
        example_btn2.pack(side=tk.LEFT, padx=5, pady=5)
        
        example_btn3 = ttk.Button(examples_frame, text="Explain a concept", 
                                 command=lambda: self.set_example_prompt("Explain how sound waves work in simple terms"))
        example_btn3.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Style the generate button
        style = ttk.Style()
        style.configure("Generate.TButton", font=("Arial", 12, "bold"))
        
        generate_frame = ttk.Frame(frame)
        generate_frame.pack(pady=15)
        
        self.generate_btn = ttk.Button(generate_frame, text="Generate Content", style="Generate.TButton", 
                                     command=self.generate_content)
        self.generate_btn.pack(ipadx=10, ipady=5)
        
        # Create a frame for the result with a title
        result_frame = ttk.LabelFrame(frame, text="Generated Content")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text area for displaying generated content with styled tag
        self.content_text = tk.Text(result_frame, height=20, width=80, wrap=tk.WORD)
        self.content_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.content_text.config(state=tk.DISABLED)
        self.content_text.tag_configure("title", font=("Arial", 12, "bold"))
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.content_text, command=self.content_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=scrollbar.set)
        
    def set_example_prompt(self, prompt):
        """Set an example prompt in the content input text area"""
        self.content_input_text.delete(1.0, tk.END)
        self.content_input_text.insert(tk.END, prompt)

    # Preference management functions
    def add_genre(self):
        genre = self.genre_var.get().strip()
        if genre and genre not in self.preferences["favorite_genres"]:
            self.preferences["favorite_genres"].append(genre)
            self.genre_listbox.insert(tk.END, genre)
            self.genre_var.set("")

    def remove_genre(self):
        try:
            selected_idx = self.genre_listbox.curselection()[0]
            genre = self.genre_listbox.get(selected_idx)
            self.genre_listbox.delete(selected_idx)
            self.preferences["favorite_genres"].remove(genre)
        except (IndexError, ValueError):
            messagebox.showinfo("Info", "Please select a genre to remove")

    def add_artist(self):
        artist = self.artist_var.get().strip()
        if artist and artist not in self.preferences["favorite_artists"]:
            self.preferences["favorite_artists"].append(artist)
            self.artist_listbox.insert(tk.END, artist)
            self.artist_var.set("")

    def remove_artist(self):
        try:
            selected_idx = self.artist_listbox.curselection()[0]
            artist = self.artist_listbox.get(selected_idx)
            self.artist_listbox.delete(selected_idx)
            self.preferences["favorite_artists"].remove(artist)
        except (IndexError, ValueError):
            messagebox.showinfo("Info", "Please select an artist to remove")

    def add_instrument(self):
        instrument = self.instrument_var.get().strip()
        if instrument and instrument not in self.preferences["instruments"]:
            self.preferences["instruments"].append(instrument)
            self.instrument_listbox.insert(tk.END, instrument)
            self.instrument_var.set("")

    def remove_instrument(self):
        try:
            selected_idx = self.instrument_listbox.curselection()[0]
            instrument = self.instrument_listbox.get(selected_idx)
            self.instrument_listbox.delete(selected_idx)
            self.preferences["instruments"].remove(instrument)
        except (IndexError, ValueError):
            messagebox.showinfo("Info", "Please select an instrument to remove")

    def save_preferences(self):
        # Update preferences with current UI values
        self.update_preferences_from_ui()
        
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
            messagebox.showinfo("Success", "Preferences saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {str(e)}")

    def load_preferences_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Select Preferences File"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.preferences = json.load(f)
                self.update_ui_from_preferences()
                messagebox.showinfo("Success", "Preferences loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preferences: {str(e)}")

    def load_preferences(self):
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
                self.update_ui_from_preferences()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preferences: {str(e)}")

    def update_preferences_from_ui(self):
        # Update mood, energy level and year range from UI
        self.preferences["mood"] = self.mood_var.get()
        self.preferences["energy_level"] = self.energy_var.get()
        
        year_from = self.year_from_var.get().strip()
        year_to = self.year_to_var.get().strip()
        
        if year_from and year_to:
            self.preferences["release_year_range"] = f"{year_from}-{year_to}"
        elif year_from:
            self.preferences["release_year_range"] = f"{year_from}-present"
        elif year_to:
            self.preferences["release_year_range"] = f"up to {year_to}"
        else:
            self.preferences["release_year_range"] = ""

    def update_ui_from_preferences(self):
        # Clear current listboxes
        self.genre_listbox.delete(0, tk.END)
        self.artist_listbox.delete(0, tk.END)
        self.instrument_listbox.delete(0, tk.END)
        
        # Update genres
        for genre in self.preferences["favorite_genres"]:
            self.genre_listbox.insert(tk.END, genre)
        
        # Update artists
        for artist in self.preferences["favorite_artists"]:
            self.artist_listbox.insert(tk.END, artist)
        
        # Update instruments
        for instrument in self.preferences["instruments"]:
            self.instrument_listbox.insert(tk.END, instrument)
        
        # Update mood and energy
        self.mood_var.set(self.preferences["mood"])
        self.energy_var.set(self.preferences["energy_level"])
        
        # Update year range
        year_range = self.preferences["release_year_range"]
        if year_range:
            if "-" in year_range:
                years = year_range.split("-")
                if len(years) == 2:
                    if years[1].lower() == "present":
                        self.year_from_var.set(years[0])
                        self.year_to_var.set("")
                    else:
                        self.year_from_var.set(years[0])
                        self.year_to_var.set(years[1])
            elif year_range.startswith("up to"):
                year_to = year_range.replace("up to", "").strip()
                self.year_from_var.set("")
                self.year_to_var.set(year_to)

    # Recommendation and content generation functions
    def get_recommendations(self):
        # Update preferences from UI
        self.update_preferences_from_ui()
        
        # Start the recommendation in a separate thread
        self.recommendation_text.config(state=tk.NORMAL)
        self.recommendation_text.delete(1.0, tk.END)
        self.recommendation_text.insert(tk.END, "Generating recommendations...\n")
        self.recommendation_text.config(state=tk.DISABLED)
        
        threading.Thread(target=self._get_recommendations_thread).start()

    def _get_recommendations_thread(self):
        try:
            # Construct the prompt for the AI
            prompt = "Please recommend 10 songs based on the following music preferences:\n\n"
            
            if self.preferences["favorite_genres"]:
                prompt += f"Favorite Genres: {', '.join(self.preferences['favorite_genres'])}\n"
            
            if self.preferences["favorite_artists"]:
                prompt += f"Favorite Artists: {', '.join(self.preferences['favorite_artists'])}\n"
            
            if self.preferences["mood"]:
                prompt += f"Mood: {self.preferences['mood']}\n"
            
            if self.preferences["energy_level"]:
                prompt += f"Energy Level: {self.preferences['energy_level']}\n"
            
            if self.preferences["release_year_range"]:
                prompt += f"Release Year Range: {self.preferences['release_year_range']}\n"
            
            if self.preferences["instruments"]:
                prompt += f"Featured Instruments: {', '.join(self.preferences['instruments'])}\n"
            
            prompt += "\nFor each song, provide the title, artist, album, and a brief explanation of why it matches my preferences."
            
            # Call the Gemini API
            response = self.model.generate_content(prompt)
            
            # Update the UI with the recommendation
            self.root.after(0, self._update_recommendation_ui, response.text)
            
        except Exception as e:
            error_msg = f"Error generating recommendations: {str(e)}"
            self.root.after(0, self._show_error, error_msg)

    def _update_recommendation_ui(self, text):
        self.recommendation_text.config(state=tk.NORMAL)
        self.recommendation_text.delete(1.0, tk.END)
        self.recommendation_text.insert(tk.END, text)
        self.recommendation_text.config(state=tk.DISABLED)

    def generate_content(self):
        # Get content type and input
        content_type = self.content_type_var.get()
        content_input = self.content_input_var.get().strip()
        
        # Update the UI to show we're generating
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "Generating content...\n")
        self.content_text.config(state=tk.DISABLED)
        
        # Start the content generation in a separate thread
        threading.Thread(target=self._generate_content_thread, args=(content_type, content_input)).start()

    def _generate_content_thread(self, content_type, content_input):
        try:
            # Update preferences from UI
            self.update_preferences_from_ui()
            
            # Construct the prompt
            prompt = f"Please generate a music-related {content_type} "
            
            if content_input:
                prompt += f"about {content_input} "
            
            prompt += "taking into account the following preferences:\n\n"
            
            if self.preferences["favorite_genres"]:
                prompt += f"Favorite Genres: {', '.join(self.preferences['favorite_genres'])}\n"
            
            if self.preferences["favorite_artists"]:
                prompt += f"Favorite Artists: {', '.join(self.preferences['favorite_artists'])}\n"
            
            if self.preferences["mood"]:
                prompt += f"Mood: {self.preferences['mood']}\n"
            
            if self.preferences["energy_level"]:
                prompt += f"Energy Level: {self.preferences['energy_level']}\n"
            
            if self.preferences["release_year_range"]:
                prompt += f"Release Year Range: {self.preferences['release_year_range']}\n"
            
            if self.preferences["instruments"]:
                prompt += f"Featured Instruments: {', '.join(self.preferences['instruments'])}\n"
            
            # Call the Gemini API
            response = self.model.generate_content(prompt)
            
            # Update the UI with the generated content
            self.root.after(0, self._update_content_ui, response.text)
            
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            self.root.after(0, self._show_error, error_msg)

    def _update_content_ui(self, text):
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, text)
        self.content_text.config(state=tk.DISABLED)

    def _show_error(self, error_msg):
        messagebox.showerror("Error", error_msg)
        
        # Also update the text area
        if self.notebook.index(self.notebook.select()) == 1:  # Recommendation tab
            self.recommendation_text.config(state=tk.NORMAL)
            self.recommendation_text.delete(1.0, tk.END)
            self.recommendation_text.insert(tk.END, f"Error: {error_msg}")
            self.recommendation_text.config(state=tk.DISABLED)
        else:  # Content generation tab
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Error: {error_msg}")
            self.content_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicRecommendationApp(root)
    root.mainloop()