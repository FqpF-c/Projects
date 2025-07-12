import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import io
import openpyxl

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"
genai.configure(api_key=GEMINI_API_KEY)

# Create Gemini model instance
model = genai.GenerativeModel('gemini-1.5-flash')

# Sleep data collection and stress detection application
st.title("Sleep Habit Stress Detector")
st.write("Track your sleep patterns and get AI-powered stress level analysis")

# User information
with st.sidebar:
    st.header("User Profile")
    user_name = st.text_input("Name", "John Doe")
    user_age = st.number_input("Age", 18, 100, 35)
    user_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    user_occupation = st.text_input("Occupation", "Software Engineer")

# Initialize or retrieve sleep data
if 'sleep_data' not in st.session_state:
    st.session_state.sleep_data = []

# Sleep data collection form
st.header("Log Your Sleep")
with st.form("sleep_log_form"):
    col1, col2 = st.columns(2)
    with col1:
        sleep_date = st.date_input("Date", datetime.now().date() - timedelta(days=1))
        sleep_time = st.time_input("Sleep Time", datetime.strptime("23:00", "%H:%M").time())
    with col2:
        wake_time = st.time_input("Wake Time", datetime.strptime("07:00", "%H:%M").time())
        sleep_quality = st.slider("Sleep Quality (1-10)", 1, 10, 7)
    
    # Additional sleep metrics
    st.subheader("Additional Sleep Metrics")
    col3, col4 = st.columns(2)
    with col3:
        wakeups = st.number_input("Number of Wakeups", 0, 20, 1)
        dreams = st.checkbox("Did you dream?")
    with col4:
        caffeine = st.number_input("Caffeine Intake (mg)", 0, 1000, 100)
        exercise = st.number_input("Exercise Duration (minutes)", 0, 300, 30)
    
    # Subjective feelings
    st.subheader("How do you feel today?")
    mood = st.select_slider("Mood", options=["Very Bad", "Bad", "Neutral", "Good", "Very Good"], value="Neutral")
    stress_feeling = st.select_slider("Perceived Stress Level", options=["None", "Low", "Moderate", "High", "Extreme"], value="Low")
    
    submit_button = st.form_submit_button("Log Sleep Data")

# Process the form submission
if submit_button:
    # Calculate total sleep duration
    sleep_dt = datetime.combine(sleep_date, sleep_time)
    wake_dt = datetime.combine(sleep_date + timedelta(days=1) if wake_time < sleep_time else sleep_date, wake_time)
    duration = (wake_dt - sleep_dt).total_seconds() / 3600  # hours
    
    # Create a sleep entry
    sleep_entry = {
        "date": sleep_date.strftime("%Y-%m-%d"),
        "sleep_time": sleep_time.strftime("%H:%M"),
        "wake_time": wake_time.strftime("%H:%M"),
        "duration": round(duration, 2),
        "quality": sleep_quality,
        "wakeups": wakeups,
        "had_dreams": dreams,
        "caffeine_mg": caffeine,
        "exercise_min": exercise,
        "mood": mood,
        "perceived_stress": stress_feeling
    }
    
    # Add to session state
    st.session_state.sleep_data.append(sleep_entry)
    st.success("Sleep data logged successfully!")

# Display logged sleep data
if st.session_state.sleep_data:
    st.header("Your Sleep History")
    sleep_df = pd.DataFrame(st.session_state.sleep_data)
    st.dataframe(sleep_df)
    
    # Visualize sleep patterns
    if len(sleep_df) >= 3:  # Only show visualizations with enough data
        st.header("Sleep Pattern Visualization")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Sleep duration over time
        sns.lineplot(x=sleep_df.index, y='duration', data=sleep_df, marker='o', ax=ax1)
        ax1.set_title('Sleep Duration Over Time')
        ax1.set_xlabel('Entry Number')
        ax1.set_ylabel('Hours')
        
        # Sleep quality over time
        sns.lineplot(x=sleep_df.index, y='quality', data=sleep_df, marker='o', color='green', ax=ax2)
        ax2.set_title('Sleep Quality Over Time')
        ax2.set_xlabel('Entry Number')
        ax2.set_ylabel('Quality (1-10)')
        
        st.pyplot(fig)
    
    # Get stress analysis from Gemini
    if st.button("Analyze Stress Levels"):
        with st.spinner("Analyzing your sleep patterns with Gemini AI..."):
            # Prepare data for Gemini
            sleep_summary = {
                "user_profile": {
                    "name": user_name,
                    "age": user_age,
                    "gender": user_gender,
                    "occupation": user_occupation
                },
                "sleep_data": st.session_state.sleep_data,
                "average_metrics": {
                    "avg_duration": round(sleep_df['duration'].mean(), 2),
                    "avg_quality": round(sleep_df['quality'].mean(), 2),
                    "avg_wakeups": round(sleep_df['wakeups'].mean(), 2),
                }
            }
            
            # Prompt for Gemini
            prompt = f"""
            You are an AI specializing in sleep science and stress management. Analyze the following sleep data and provide:
            1. An assessment of the person's stress level based on their sleep patterns
            2. Key observations about their sleep quality and habits
            3. Personalized recommendations to improve sleep and reduce stress
            4. A stress level estimation (Low, Moderate, High, Severe)
            
            Here is the sleep data: {json.dumps(sleep_summary, indent=2)}
            
            Respond in a structured JSON format with these sections: 
            {{
                "stress_assessment": "detailed analysis of stress indicators",
                "key_observations": ["list of key findings"],
                "recommendations": ["list of personalized recommendations"],
                "stress_level": "estimated level"
            }}
            """
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            try:
                analysis = json.loads(response.text)
                
                # Display the analysis in a well-formatted UI
                st.header("AI Stress Analysis Results")
                
                # Create columns for better layout
                col1, col2 = st.columns([1, 2])
                
                # Stress level indicator with color and larger display
                with col1:
                    stress_level = analysis.get("stress_level", "Unknown")
                    stress_colors = {
                        "None": "#4CAF50", 
                        "Low": "#8BC34A", 
                        "Moderate": "#FFC107", 
                        "High": "#FF5722", 
                        "Severe": "#F44336",
                        "Extreme": "#B71C1C"
                    }
                    color = stress_colors.get(stress_level, "#9E9E9E")
                    
                    # Display stress level in a card-like container
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                        <h2 style="color: white; margin: 0;">STRESS LEVEL</h2>
                        <h1 style="color: white; margin: 10px 0 0 0; font-size: 2.5rem;">{stress_level}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed assessment
                with col2:
                    st.subheader("Stress Assessment")
                    st.write(analysis.get("stress_assessment", "No assessment available"))
                
                # Create a tabbed interface for observations and recommendations
                tab1, tab2 = st.tabs(["Key Observations", "Recommendations"])
                
                with tab1:
                    observations = analysis.get("key_observations", ["No observations available"])
                    for i, obs in enumerate(observations):
                        st.markdown(f"**{i+1}.** {obs}")
                        
                        # Add divider except after the last item
                        if i < len(observations) - 1:
                            st.markdown("---")
                
                with tab2:
                    recommendations = analysis.get("recommendations", ["No recommendations available"])
                    for i, rec in enumerate(recommendations):
                        # Process markdown in recommendations
                        st.markdown(f"{rec}")
                        
                        # Add divider except after the last item
                        if i < len(recommendations) - 1:
                            st.markdown("---")
                
                # Add export option for the analysis
                st.markdown("### Export Analysis")
                export_analysis = st.button("Export Analysis to Text File")
                if export_analysis:
                    analysis_text = f"""# Sleep Habit Stress Analysis
                    
## Stress Level: {stress_level}

## Assessment
{analysis.get('stress_assessment', 'No assessment available')}

## Key Observations
{"".join(['- ' + obs + '\\n' for obs in analysis.get('key_observations', ['No observations available'])])}

## Recommendations
{"".join(['- ' + rec + '\\n' for rec in analysis.get('recommendations', ['No recommendations available'])])}

Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
                    st.download_button(
                        label="Download Analysis",
                        data=analysis_text,
                        file_name=f"sleep_stress_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
            
            except json.JSONDecodeError:
                st.error("Failed to parse Gemini's response. Here's the raw output:")
                st.write(response.text)
                
                # Attempt to format raw text
                try:
                    # Try to clean and format the response text
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith('```json') and cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[7:-3].strip()
                    
                    analysis = json.loads(cleaned_text)
                    st.success("Successfully parsed the cleaned response!")
                    
                    # Display the analysis with the same formatting as above
                    # (Duplicate code from above for brevity in this example)
                    st.header("AI Stress Analysis Results")
                    st.subheader("Stress Level")
                    st.markdown(f"**{analysis.get('stress_level', 'Unknown')}**")
                    # Display other sections...
                    
                except Exception:
                    st.warning("Could not automatically format the response. You may need to adjust the prompt.")
            
            except Exception as e:
                st.error(f"Error analyzing sleep data: {str(e)}")

# Data import and export section
st.header("Import or Export Sleep Data")

# Import data from Excel
st.subheader("Import Sleep Data")
uploaded_file = st.file_uploader("Upload Excel file with sleep data", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        with st.spinner("Processing your Excel file..."):
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            
            # Check required columns
            required_columns = ["date", "sleep_time", "wake_time", "quality"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Your Excel file is missing these required columns: {', '.join(missing_columns)}")
                st.write("Your Excel file should have these columns: date, sleep_time, wake_time, quality")
                
                # Show sample format
                st.expander("View Sample Format").dataframe(pd.DataFrame({
                    "date": ["2025-04-01", "2025-04-02"],
                    "sleep_time": ["23:00", "23:30"],
                    "wake_time": ["07:00", "07:30"],
                    "quality": [7, 8],
                    "wakeups": [2, 1],
                    "had_dreams": [True, False],
                    "caffeine_mg": [100, 150],
                    "exercise_min": [30, 45],
                    "mood": ["Good", "Very Good"],
                    "perceived_stress": ["Low", "None"]
                }))
            else:
                # Process each row into the expected format
                imported_data = []
                for _, row in df.iterrows():
                    # Convert date if needed
                    if isinstance(row['date'], datetime):
                        date_str = row['date'].strftime("%Y-%m-%d")
                    else:
                        date_str = row['date']
                    
                    # Format times if needed
                    sleep_time = row['sleep_time']
                    if isinstance(sleep_time, datetime):
                        sleep_time = sleep_time.strftime("%H:%M")
                    
                    wake_time = row['wake_time']
                    if isinstance(wake_time, datetime):
                        wake_time = wake_time.strftime("%H:%M")
                    
                    # Set optional fields with defaults
                    sleep_entry = {
                        "date": date_str,
                        "sleep_time": sleep_time,
                        "wake_time": wake_time,
                        "quality": row.get('quality', 5),
                        "wakeups": row.get('wakeups', 0),
                        "had_dreams": bool(row.get('had_dreams', False)),
                        "caffeine_mg": row.get('caffeine_mg', 0),
                        "exercise_min": row.get('exercise_min', 0),
                        "mood": row.get('mood', "Neutral"),
                        "perceived_stress": row.get('perceived_stress', "Low")
                    }
                    
                    # Calculate duration if not provided
                    if 'duration' in row:
                        sleep_entry["duration"] = row['duration']
                    else:
                        try:
                            # Parse times to calculate duration
                            sleep_dt = datetime.strptime(sleep_time, "%H:%M")
                            wake_dt = datetime.strptime(wake_time, "%H:%M")
                            
                            # Adjust for overnight sleep
                            if wake_dt.time() < sleep_dt.time():
                                wake_dt = wake_dt + timedelta(days=1)
                                
                            duration = (wake_dt - sleep_dt).total_seconds() / 3600
                            sleep_entry["duration"] = round(duration, 2)
                        except:
                            sleep_entry["duration"] = 8.0  # Default if calculation fails
                    
                    imported_data.append(sleep_entry)
                
                # Confirm import
                st.success(f"Successfully processed {len(imported_data)} sleep records")
                
                if st.button("Add imported data to existing records"):
                    # Add to current session state
                    st.session_state.sleep_data.extend(imported_data)
                    st.success(f"Added {len(imported_data)} records to your sleep data!")
                    st.experimental_rerun()
                    
                if st.button("Replace existing data with imported data"):
                    # Replace session state
                    st.session_state.sleep_data = imported_data
                    st.success(f"Replaced sleep data with {len(imported_data)} imported records!")
                    st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error processing your Excel file: {str(e)}")
        st.write("Make sure your file is properly formatted with the required columns.")

# Export data option
if st.session_state.sleep_data:
    st.subheader("Export Sleep Data")
    export_format = st.radio("Export Format", ["CSV", "Excel"])
    
    if st.button("Export Sleep Data"):
        sleep_df = pd.DataFrame(st.session_state.sleep_data)
        
        if export_format == "CSV":
            csv = sleep_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"sleep_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:  # Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                sleep_df.to_excel(writer, index=False, sheet_name='Sleep Data')
            buffer.seek(0)
            
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name=f"sleep_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Help section
with st.expander("How to Use This App"):
    st.markdown("""
    1. **Fill in your profile** information in the sidebar
    2. **Log your sleep data** daily using the form OR import existing sleep data from an Excel file
    3. **Analyze your stress levels** with the Gemini AI after logging several days of data
    4. **Review the visualizations** to see patterns in your sleep
    5. **Export your data** in CSV or Excel format for personal records or to share with a healthcare provider
    
    ### Excel Import Format
    When importing data from Excel, your file should include these columns:
    - **Required columns**: date, sleep_time, wake_time, quality
    - **Optional columns**: wakeups, had_dreams, caffeine_mg, exercise_min, mood, perceived_stress, duration
    
    The AI analysis uses Gemini's advanced language models to detect potential stress patterns based on your sleep habits.
    This is not a medical diagnostic tool but can help you gain insights into your sleep-stress relationship.
    """)