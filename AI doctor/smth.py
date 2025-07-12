import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="AI Virtual Doctor",
    page_icon="🩺",
    layout="centered"
)

# ----- CONSTANTS & SETUP -----
DISCLAIMER = """
This application provides preliminary health information only and is not a substitute for professional 
medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified
health provider with any questions regarding a medical condition. Never disregard professional medical
advice or delay seeking it because of something you have read on this application.
"""

HEALTH_KEYWORDS = [
    "symptom", "pain", "doctor", "medical", "health", "disease", "condition",
    "treatment", "medicine", "illness", "diagnosis", "sick", "cure", "remedy",
    "fever", "cough", "headache", "nausea", "dizzy", "throat", "stomach", "chest",
    "breathing", "blood", "heart", "medication", "pharmacy", "hospital", "clinic"
]

GEMINI_SYSTEM_PROMPT = """
You are an AI health assistant designed to provide preliminary health information only.

IMPORTANT GUIDELINES:
1. Always clarify you're not a doctor and cannot provide medical diagnoses
2. For serious symptoms (difficulty breathing, severe pain, etc.), always advise seeking immediate medical attention
3. Only respond to health-related queries
4. For non-medical questions, politely explain you can only discuss health topics
5. Never prescribe specific medications or dosages
6. Provide general information about common conditions based on symptoms
7. Suggest whether the user should consult a doctor based on symptom severity
8. For mild conditions, you may suggest general self-care approaches
9. Always be honest about limitations and uncertainties
10. Maintain a compassionate, informative tone
11. When analyzing images, clearly state that visual assessments have significant limitations
12. Emphasize that image-based analysis is particularly prone to errors and should never replace in-person medical examination

Your response MUST include these sections:
1. SYMPTOM ANALYSIS: Analyze the user's symptoms in detail
2. POSSIBLE CONDITIONS: List 2-4 possible conditions that match these symptoms, from most to least likely
3. CARE RECOMMENDATIONS:
   - For mild conditions: Suggest general home remedies and over-the-counter options (no prescription medications)
   - For moderate/severe conditions: Clearly state medical attention is needed
4. SPECIALIST RECOMMENDATION: Suggest what type of doctor/specialist would typically handle these symptoms
5. WARNING SIGNS: List specific symptoms that would indicate the need for urgent medical attention
6. LIMITATIONS: Acknowledge the limitations of this preliminary assessment

Additional guidelines:
- Be comprehensive but avoid unnecessary medical jargon
- For any concerning symptoms, emphasize the importance of seeking professional medical care
- Format your response in a clear, organized way with headers for each section
- For image analysis, be especially cautious about making definitive statements

Remember: Your purpose is to provide preliminary guidance only, not to replace professional medical advice.
"""

# ----- FUNCTIONS -----

def is_health_related(query):
    """Check if query is health-related using simple keyword matching"""
    return any(keyword in query.lower() for keyword in HEALTH_KEYWORDS)

def get_gemini_response(query, image=None, chat_history=None):
    """Generate a response from Gemini for health-related queries"""
    try:
        # Check if query is health-related (unless there's an image)
        if not image and not is_health_related(query):
            return "I'm designed to help with health-related questions only. Could you please ask me about health symptoms or medical information instead?"
        
        # Convert chat history to Gemini's format
        gemini_history = []
        if chat_history:
            for message in chat_history:
                role = "user" if message["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [message["content"]]})
        
        # Add system prompt to the beginning if it's not there
        if not gemini_history or gemini_history[0]["parts"][0] != GEMINI_SYSTEM_PROMPT:
            gemini_history.insert(0, {"role": "model", "parts": [GEMINI_SYSTEM_PROMPT]})
        
        # Generate response
        chat = model.start_chat(history=gemini_history)
        
        if image:
            # If image is provided, send both the image and text query
            response = chat.send_message([image, query])
        else:
            # Otherwise just send the text query
            response = chat.send_message(query)
        
        # Add disclaimer
        full_response = response.text + "\n\n*Note: This is preliminary information only. Please consult a healthcare professional for proper medical advice.*"
        
        return full_response
    
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# ----- MAIN APP -----

# Sidebar
st.sidebar.title("About")
st.sidebar.info("This AI Virtual Doctor provides preliminary health assessments based on your symptoms.")
st.sidebar.warning("Always consult a real doctor for proper medical diagnosis and treatment.")

# Main content area
st.title("🩺 AI Virtual Doctor")
st.caption("Describe your symptoms for a preliminary assessment")

# Display disclaimer
with st.expander("**IMPORTANT MEDICAL DISCLAIMER**", expanded=True):
    st.warning(DISCLAIMER)

# Initialize Gemini API
try:
    # Use the provided API key
    api_key = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"
    
    genai.configure(api_key=api_key)
    
    # Use gemini-1.5-pro for multimodal capabilities (text + images)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
except Exception as e:
    st.error(f"Failed to initialize Gemini API: {str(e)}")
    st.stop()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your virtual health assistant. Please describe your symptoms, and I'll try to provide some preliminary guidance. Remember, I'm not a substitute for professional medical advice."
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Add image uploader with clear warning
st.warning("⚠️ **IMPORTANT**: AI analysis of medical images has significant limitations and should not replace professional medical examination. The assessment provided based on images is not diagnostic and may not be accurate.")

uploaded_file = st.file_uploader("Upload an image of your visible symptoms (optional)", 
                                 type=["jpg", "jpeg", "png"])
image_data = None

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_container_width=True)
    
    # Add an option to analyze just the image without text input
    if st.button("Analyze this image"):
        # Convert the image to the format expected by Gemini
        bytes_data = uploaded_file.getvalue()
        image_data = {"mime_type": uploaded_file.type, "data": bytes_data}
        
        # Add a generic query about the image
        generic_query = "What can you tell me about this medical image? What possible conditions might it show?"
        
        # Display the processing message
        with st.spinner("Analyzing image..."):
            response = get_gemini_response(
                generic_query,
                image=image_data,
                chat_history=st.session_state.messages
            )
            
            # Display the response below the image
            st.markdown("### Image Analysis")
            st.write(response)
            
            # Add to chat history
            st.session_state.messages.append({"role": "user", "content": "I uploaded an image for analysis."})
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Convert the image to the format expected by Gemini for later use
    bytes_data = uploaded_file.getvalue()
    image_data = {"mime_type": uploaded_file.type, "data": bytes_data}

# Text input for symptoms
text_input = st.chat_input("Describe your symptoms...")

# Process user input (text and possibly image)
if text_input:
    # Determine if we should include the image
    include_image = uploaded_file is not None
    
    # Add user message to chat (text only in history)
    st.session_state.messages.append({"role": "user", "content": text_input})
    
    # Display the user message in the UI
    with st.chat_message("user"):
        st.write(text_input)
        if include_image:
            st.image(image, caption="Uploaded image", use_container_width=True)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your symptoms..."):
            if include_image:
                response = get_gemini_response(
                    text_input,
                    image=image_data,
                    chat_history=st.session_state.messages[:-1]  # Exclude most recent message
                )
            else:
                response = get_gemini_response(
                    text_input,
                    chat_history=st.session_state.messages[:-1]  # Exclude most recent message
                )
            st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear the image uploader after processing
    uploaded_file = None
    st.rerun()