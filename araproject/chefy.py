import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import requests
from io import BytesIO

# Set up Google Gemini API
genai.configure(api_key="AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU")
model = genai.GenerativeModel('gemini-1.5-flash')

# Define countries with their flags and top chefs
countries = {
    "Italy": {
        "flag": "🇮🇹",
        "chefs": [
            {"name": "Chef Massimo Bottura 👨‍🍳", "signature_dish": "The Crunchy Part of the Lasagna", "no_boil": "Risotto al Limone", "no_oil": "Steamed Vegetable Antipasti"},
            {"name": "Chef Carlo Cracco 👨‍🍳", "signature_dish": "Risotto with Saffron and Bone Marrow", "no_boil": "Beef Carpaccio", "no_oil": "Steamed Sea Bass with Herbs"},
            {"name": "Chef Giorgio Locatelli 👨‍🍳", "signature_dish": "Agnolotti del Plin", "no_boil": "Panzanella Salad", "no_oil": "Poached Pears in Red Wine"},
            {"name": "Chef Nadia Santini 👩‍🍳", "signature_dish": "Tortelli di Zucca", "no_boil": "Bresaola with Arugula", "no_oil": "Steamed Artichokes with Lemon"},
            {"name": "Chef Gennaro Contaldo 👨‍🍳", "signature_dish": "Pasta alla Genovese", "no_boil": "Insalata Caprese", "no_oil": "Baked Herb Frittata"}
        ]
    },
    "Japan": {
        "flag": "🇯🇵",
        "chefs": [
            {"name": "Chef Masaharu Morimoto 👨‍🍳", "signature_dish": "Tuna Pizza", "no_boil": "Sashimi Platter", "no_oil": "Cucumber Sunomono"},
            {"name": "Chef Yoshihiro Murata 👨‍🍳", "signature_dish": "Kaiseki Ryori", "no_boil": "Temari Sushi", "no_oil": "Ohitashi Spinach"},
            {"name": "Chef Seiji Yamamoto 👨‍🍳", "signature_dish": "Hamo (Pike Conger) with Plum Sauce", "no_boil": "Fresh Tofu with Dashi", "no_oil": "Steamed Chawanmushi"},
            {"name": "Chef Hiroyuki Hiramatsu 👨‍🍳", "signature_dish": "Crispy Langoustines", "no_boil": "Tataki of Beef", "no_oil": "Ponzu Marinated Scallops"},
            {"name": "Chef Nobu Matsuhisa 👨‍🍳", "signature_dish": "Black Cod with Miso", "no_boil": "Yellowtail Sashimi with Jalapeño", "no_oil": "Steamed Lobster with Yuzu"}
        ]
    },
    "India": {
        "flag": "🇮🇳",
        "chefs": [
            {"name": "Chef Sanjeev Kapoor 👨‍🍳", "signature_dish": "Shaam Savera", "no_boil": "Bhel Puri", "no_oil": "Steamed Dhokla"},
            {"name": "Chef Vikas Khanna 👨‍🍳", "signature_dish": "Tandoori Lobster", "no_boil": "Kachumber Salad", "no_oil": "Steamed Modak"},
            {"name": "Chef Ranveer Brar 👨‍🍳", "signature_dish": "Ghee Roast Chicken", "no_boil": "Dahi Bhalla", "no_oil": "Fruit Chaat"},
            {"name": "Chef Vineet Bhatia 👨‍🍳", "signature_dish": "Chocolate Samosa", "no_boil": "Watermelon Gazpacho", "no_oil": "Steamed Rice Idli"},
            {"name": "Chef Manish Mehrotra 👩‍🍳", "signature_dish": "Mishti Doi Cannoli", "no_boil": "Papdi Chaat", "no_oil": "Coconut Steamed Fish"}
        ]
    },
    "Mexico": {
        "flag": "🇲🇽",
        "chefs": [
            {"name": "Chef Enrique Olvera 👨‍🍳", "signature_dish": "Mole Madre", "no_boil": "Aguachile de Camarón", "no_oil": "Jicama Salad"},
            {"name": "Chef Gabriela Cámara 👩‍🍳", "signature_dish": "Red Snapper Tostadas", "no_boil": "Ceviche Verde", "no_oil": "Nopales Salad"},
            {"name": "Chef Ricardo Muñoz Zurita 👨‍🍳", "signature_dish": "Chiles en Nogada", "no_boil": "Ensalada de Frutas con Chile", "no_oil": "Steamed Tamales"},
            {"name": "Chef Daniela Soto-Innes 👩‍🍳", "signature_dish": "Cucumber Aguachile", "no_boil": "Tuna Tostada", "no_oil": "Citrus Fruit Salad"},
            {"name": "Chef Alejandro Ruiz 👨‍🍳", "signature_dish": "Mole Negro Oaxaqueño", "no_boil": "Tlayuda", "no_oil": "Steamed Corn with Epazote"}
        ]
    },
    "France": {
        "flag": "🇫🇷",
        "chefs": [
            {"name": "Chef Alain Ducasse 👨‍🍳", "signature_dish": "Mediterranean Sea Bass", "no_boil": "Beef Tartare", "no_oil": "Steamed Vegetables Aioli"},
            {"name": "Chef Anne-Sophie Pic 👩‍🍳", "signature_dish": "Berlingots with Châteauneuf-du-Pape", "no_boil": "Seafood Carpaccio", "no_oil": "Poached Eggs with Herbs"},
            {"name": "Chef Guy Savoy 👨‍🍳", "signature_dish": "Artichoke Soup with Black Truffle", "no_boil": "Oysters in Granité", "no_oil": "Steamed Foie Gras"},
            {"name": "Chef Michel Roux Jr 👨‍🍳", "signature_dish": "Soufflé Suissesse", "no_boil": "Salmon Gravlax", "no_oil": "Poached Pears Belle Hélène"},
            {"name": "Chef Hélène Darroze 👩‍🍳", "signature_dish": "Foie Gras with Black Cherry", "no_boil": "Steak Tartare", "no_oil": "Steamed Turbot with Champagne"}
        ]
    },
    "China": {
        "flag": "🇨🇳",
        "chefs": [
            {"name": "Chef Martin Yan 👨‍🍳", "signature_dish": "Peking Duck", "no_boil": "Century Egg Tofu", "no_oil": "Steamed Fish with Ginger"},
            {"name": "Chef Ken Hom 👨‍🍳", "signature_dish": "Hand-Pulled Noodles", "no_boil": "Cold Cucumber Salad", "no_oil": "Steamed Pork Buns"},
            {"name": "Chef Tony Lu 👨‍🍳", "signature_dish": "Braised Hairy Crab with Tofu", "no_boil": "Jellyfish Salad", "no_oil": "Steamed Egg Custard"},
            {"name": "Chef Lan Guijun 👨‍🍳", "signature_dish": "Dan Dan Noodles", "no_boil": "White Cut Chicken", "no_oil": "Steamed Winter Melon Soup"},
            {"name": "Chef Jereme Leung 👨‍🍳", "signature_dish": "Xiao Long Bao (Soup Dumplings)", "no_boil": "Yunnan Ham with Melon", "no_oil": "Steamed Pearl Meatballs"}
        ]
    }
}

# Popular dishes for each country
popular_dishes = {
    "Italy": [
        "Spaghetti Carbonara", "Margherita Pizza", "Lasagna", "Risotto Milanese",
        "Tiramisu", "Panna Cotta", "Osso Buco", "Caprese Salad",
        "Fettuccine Alfredo", "Gnocchi", "Minestrone Soup", "Bruschetta",
        "Pasta Primavera", "Cannoli", "Polenta", "Focaccia",
        "Ravioli", "Gelato", "Pesto Pasta", "Saltimbocca",
        "Arancini", "Cacio e Pepe", "Panzanella", "Calzone",
        "Cioppino", "Biscotti", "Limoncello", "Prosciutto e Melone",
        "Ribollita", "Burrata", "Tagliatelle al Ragù", "Vitello Tonnato",
        "Fritto Misto", "Torta Caprese", "Zabaglione"
    ],
    "Japan": [
        "Sushi", "Ramen", "Tempura", "Udon",
        "Sashimi", "Yakitori", "Miso Soup", "Okonomiyaki",
        "Tonkatsu", "Gyoza", "Teriyaki Chicken", "Onigiri",
        "Shabu Shabu", "Takoyaki", "Sukiyaki", "Donburi",
        "Matcha Ice Cream", "Tamagoyaki", "Katsu Curry", "Yakiniku",
        "Unagi", "Kaiseki", "Chawanmushi", "Yakisoba",
        "Oden", "Nikujaga", "Karaage", "Dorayaki",
        "Mochi", "Ochazuke", "Nabemono", "Chirashi",
        "Hiyashi Chuka", "Mentaiko", "Shojin Ryori"
    ],
    "India": [
        "Butter Chicken", "Chicken Tikka Masala", "Samosas", "Biryani",
        "Palak Paneer", "Naan", "Dosa", "Chana Masala",
        "Tandoori Chicken", "Aloo Gobi", "Malai Kofta", "Gulab Jamun",
        "Masala Chai", "Rogan Josh", "Raita", "Dal Makhani",
        "Pani Puri", "Vindaloo", "Chole Bhature", "Rasmalai",
        "Vada Pav", "Idli Sambhar", "Dhokla", "Korma",
        "Pakora", "Kofta", "Jalebi", "Kulfi",
        "Pav Bhaji", "Thali", "Uttapam", "Bhel Puri",
        "Kathi Roll", "Keema Matar", "Bombay Sandwich"
    ],
    "Mexico": [
        "Tacos", "Enchiladas", "Guacamole", "Chiles Rellenos",
        "Tamales", "Quesadillas", "Mole Poblano", "Pozole",
        "Fajitas", "Ceviche", "Churros", "Tostadas",
        "Elote", "Chilaquiles", "Huevos Rancheros", "Flautas",
        "Carnitas", "Pico de Gallo", "Arroz con Leche", "Horchata",
        "Sopes", "Menudo", "Tortas", "Aguachile",
        "Barbacoa", "Cochinita Pibil", "Mole Negro", "Tlayudas",
        "Chapulines", "Chiles en Nogada", "Pambazo", "Birria",
        "Tres Leches Cake", "Esquites", "Michelada"
    ],
    "France": [
        "Coq au Vin", "Beef Bourguignon", "Crème Brûlée", "Quiche Lorraine",
        "Ratatouille", "Croissants", "Bouillabaisse", "Escargot",
        "Cassoulet", "French Onion Soup", "Tarte Tatin", "Macarons",
        "Crêpes", "Pot-au-Feu", "Soufflé", "Baguette",
        "Salade Niçoise", "Duck Confit", "Fondue", "Pâté",
        "Couscous", "Croque Monsieur", "Madeleines", "Blanquette de Veau",
        "Éclair", "Foie Gras", "Rillettes", "Pain au Chocolat",
        "Moules Marinières", "Chateaubriand", "Profiteroles", "Jambon-Beurre",
        "Galette des Rois", "Clafoutis", "Tarte Flambée"
    ],
    "China": [
        "Kung Pao Chicken", "Dim Sum", "Mapo Tofu", "Hot Pot",
        "Peking Duck", "Spring Rolls", "Wonton Soup", "Chow Mein",
        "Sweet and Sour Pork", "Xiaolongbao", "Zhajiangmian", "Char Siu",
        "Dan Dan Noodles", "Congee", "Sichuan Hot Pot", "Dumplings",
        "Century Egg", "Beef Noodle Soup", "Fried Rice", "Crispy Duck",
        "Egg Tarts", "Scallion Pancakes", "Tea Eggs", "Buddha's Delight",
        "Beggar's Chicken", "Dongpo Pork", "General Tso's Chicken", "Har Gow",
        "Mooncakes", "Tangyuan", "Zongzi", "Ma Po Tofu",
        "Yunnan Rice Noodles", "Chinese Hamburger", "Hand-Pulled Noodles"
    ]
}

# App title and description with enhanced styling
st.set_page_config(page_title="International Recipe Advisor", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for improved appearance
st.markdown("""
<style>
    /* Main styles */
    .main-title {
        font-size: 3rem !important;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 10px;
        font-weight: 800;
    }
    .subtitle {
        font-size: 1.2rem !important;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 30px;
        font-style: italic;
    }
    .stButton>button {
        background-color: #ff5a5f;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #ff4b4b;
    }
    
    /* Country flag styles */
    .country-flag {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 5px;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .country-flag:hover {
        transform: scale(1.2);
    }
    .country-name {
        text-align: center;
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* Chef card styles */
    .chef-card {
        border-radius: 10px;
        padding: 20px;
        background-color: #f9f9f9;
        border: 2px solid #e6e6e6;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .chef-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        border-color: #ff4b4b;
    }
    .chef-name {
        font-weight: bold;
        font-size: 1.3rem;
        margin: 10px 0 5px 0;
        color: #2c3e50;
    }
    .chef-dish {
        font-style: italic;
        color: #555;
        margin-bottom: 10px;
    }
    .chef-options {
        display: flex;
        justify-content: space-around;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed #ddd;
    }
    .chef-option {
        background-color: #f0f8ff;
        border-radius: 15px;
        padding: 5px 10px;
        font-size: 0.8rem;
        color: #000000;  /* Changed from #555 to black */
        margin: 0 2px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        font-weight: bold;  /* Added for better visibility */
    }
    
    /* Chat interface styling */
    .stChatMessage {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .sidebar-chef {
        background-color: #f0f8ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #4682b4;
    }
    .sidebar-title {
        color: #2c3e50;
        font-size: 1.2rem;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .sidebar-chef-info {
        font-size: 1.5rem;
        margin-bottom: 5px;
    }
    .sidebar-chef-details {
        color: #555;
        font-style: italic;
        margin-bottom: 15px;
    }
    
    /* Popular dishes section */
    .scrollable-dishes {
        max-height: 400px;
        overflow-y: auto;
        padding-right: 10px;
    }
    .scrollable-dishes::-webkit-scrollbar {
        width: 5px;
    }
    .scrollable-dishes::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    .scrollable-dishes::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    .scrollable-dishes::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    .dish-button {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 8px 12px;
        margin: 5px 0;
        text-align: left;
        transition: all 0.3s;
        display: block;
        width: 100%;
        cursor: pointer;
        font-size: 0.9rem;
        color: #333;
    }
    .dish-button:hover {
        background-color: #fff8e1;
        border-color: #ffcc80;
        transform: translateX(5px);
    }
    
    /* Fix for text colors */
    .stChatMessage[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p,
    .stChatMessage[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] li,
    .stChatMessage[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] span {
        color: #000000 !important;
    }
    
    /* Force all text to be visible */
    p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: #000000;
    }
    
    /* Special button styles */
    .specialty-button {
        background-color: #3498db;
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 8px 12px;
        margin: 5px 0;
        text-align: center;
        width: 100%;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
    }
    .specialty-button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
    }
    .no-oil-button {
        background-color: #27ae60;
    }
    .no-oil-button:hover {
        background-color: #219653;
    }
    .no-boil-button {
        background-color: #e74c3c;
    }
    .no-boil-button:hover {
        background-color: #c0392b;
    }
    
    /* Fix user message text to be black in light mode */
    [data-testid="stChatMessageContent"] {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌎 International Recipe Advisor 🍳</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Discover authentic recipes from top chefs around the world!</p>", unsafe_allow_html=True)

# Initialize session state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None
    
if 'selected_chef' not in st.session_state:
    st.session_state.selected_chef = None
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'selected_dish' not in st.session_state:
    st.session_state.selected_dish = None
    
if 'no_oil_request' not in st.session_state:
    st.session_state.no_oil_request = False
    
if 'no_boil_request' not in st.session_state:
    st.session_state.no_boil_request = False

# Display country flags for selection
if st.session_state.selected_country is None:
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Select a Country</h2>", unsafe_allow_html=True)
    
    # Create columns for country flags
    cols = st.columns(len(countries))
    
    for i, (country_name, country_info) in enumerate(countries.items()):
        with cols[i]:
            # Display country flag with clickable functionality
            st.markdown(f"""
            <div onclick="parent.postMessage({{command: 'streamlitClicked', target: '{country_name}Flag', key: '{country_name}Flag'}}, '*')" class="country-flag">
                {country_info['flag']}
            </div>
            <div class="country-name">{country_name}</div>
            """, unsafe_allow_html=True)
            
            # Hidden button to capture the click event
            if st.button(f"Select {country_name}", key=f"{country_name}Flag", help=f"Select {country_name}"):
                st.session_state.selected_country = country_name
                st.rerun()

# If a country is selected, display its chefs
elif st.session_state.selected_chef is None:
    country = st.session_state.selected_country
    country_info = countries[country]
    
    # Back button to return to country selection
    col1, col2, col3 = st.columns([1, 10, 1])
    with col1:
        if st.button("←", help="Back to country selection"):
            st.session_state.selected_country = None
            st.rerun()
            
    with col2:
        st.markdown(f"""
        <h2 style='text-align: center; margin-bottom: 30px;'>
            {country_info['flag']} Top Chefs from {country}
        </h2>
        """, unsafe_allow_html=True)
    
    # Display chef cards
    chefs = country_info['chefs']
    
    # Create rows of chefs (3 chefs per row)
    for i in range(0, len(chefs), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(chefs):
                chef = chefs[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div class="chef-card">
                        <div style="position: relative;">
                            <img src="/api/placeholder/300/200" alt="Chef" style="width: 100%; border-radius: 8px;">
                            <div style="position: absolute; top: 10px; right: 10px; font-size: 36px; background-color: rgba(0,0,0,0.7); border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                                {chef['name'].split()[-1]}
                            </div>
                            <div style="position: absolute; top: 10px; left: 10px; font-size: 24px; background-color: rgba(0,0,0,0.7); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                {country_info['flag']}
                            </div>
                        </div>
                        <div class="chef-name">{chef['name']}</div>
                        <div class="chef-dish" style="color: #000000;">Signature: {chef['signature_dish']}</div>
                        <div class="chef-options">
                            <span class="chef-option" style="color: #000000; font-weight: bold;">
                                🥗 No Oil: {chef['no_oil']}
                            </span>
                            <span class="chef-option" style="color: #000000; font-weight: bold;">
                                🧊 No Boil: {chef['no_boil']}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Button to select chef
                    if st.button(f"Chat with {chef['name'].split(' ')[1]}", key=f"chef_{chef['name']}"):
                        st.session_state.selected_chef = chef
                        st.session_state.chat_history = []
                        st.rerun()
                    
                    # No Oil and No Boil buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🥗 No Oil Recipe", key=f"no_oil_{chef['name']}"):
                            st.session_state.selected_chef = chef
                            st.session_state.chat_history = []
                            # Create initial message requesting no-oil recipe
                            st.session_state.no_oil_request = True
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🧊 No Boil Recipe", key=f"no_boil_{chef['name']}"):
                            st.session_state.selected_chef = chef
                            st.session_state.chat_history = []
                            # Create initial message requesting no-boil recipe
                            st.session_state.no_boil_request = True
                            st.rerun()

# If a chef is selected, display chat interface
else:
    chef = st.session_state.selected_chef
    country = st.session_state.selected_country
    country_flag = countries[country]['flag']
    
    # Setup sidebar
    st.sidebar.markdown("<div class='sidebar-title'>Your Current Chef</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div class='sidebar-chef'>
        <div class='sidebar-chef-info'>{country_flag} {chef['name']}</div>
        <div class='sidebar-chef-details'>{country} - Signature: {chef['signature_dish']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # No Oil and No Boil buttons in sidebar
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button(f"🥗 No Oil", key="sidebar_no_oil"):
            # Set flag for no-oil request
            st.session_state.no_oil_request = True
            st.rerun()
    
    with col2:
        if st.sidebar.button(f"🧊 No Boil", key="sidebar_no_boil"):
            # Set flag for no-boil request
            st.session_state.no_boil_request = True
            st.rerun()
    
    if st.sidebar.button("Change Chef", type="primary", use_container_width=True):
        st.session_state.selected_chef = None
        st.session_state.chat_history = []
        st.session_state.selected_dish = None
        st.session_state.no_oil_request = False
        st.session_state.no_boil_request = False
        st.rerun()
        
    if st.sidebar.button("Change Country", use_container_width=True):
        st.session_state.selected_country = None
        st.session_state.selected_chef = None
        st.session_state.chat_history = []
        st.session_state.selected_dish = None
        st.session_state.no_oil_request = False
        st.session_state.no_boil_request = False
        st.rerun()
    
    # Add popular dishes section in sidebar
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-title'>Popular Dishes</div>", unsafe_allow_html=True)
    
    # Display popular dishes in a scrollable area
    st.sidebar.markdown("<div class='scrollable-dishes'>", unsafe_allow_html=True)
    for dish in popular_dishes[country]:
        if st.sidebar.button(dish, key=f"dish_{dish}", use_container_width=True):
            st.session_state.selected_dish = dish
            st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Enhanced chat interface
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #f9f7f7; padding: 15px; border-radius: 10px; border-left: 5px solid #ff5a5f;">
        <div style="font-size: 2rem; margin-right: 15px;">{country_flag}</div>
        <div style="flex-grow: 1;">
            <h2 style="margin: 0; color: #2c3e50;">{chef['name']}</h2>
            <p style="margin: 0; color: #7f8c8d;">Expert in {country} cuisine • Signature dish: {chef['signature_dish']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Specialty buttons in main chat area
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"🥗 No Oil: {chef['no_oil']}", key="header_no_oil_button"):
            st.session_state.no_oil_request = True
            st.rerun()
    
    with col2:
        if st.button(f"🧊 No Boil: {chef['no_boil']}", key="header_no_boil_button"):
            st.session_state.no_boil_request = True
            st.rerun()

    # Process any special requests (No Oil, No Boil, Selected Dish)
    if st.session_state.no_oil_request:
        # Create user message requesting no-oil recipe
        user_message = f"Can you share your no-oil recipe for {chef['no_oil']}?"
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="color: #000000;">
                {user_message}
            </div>
            """, unsafe_allow_html=True)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Generate chef's response for no-oil recipe
        prompt = f"""
        You are {chef['name']}, an expert chef specialized in {country} cuisine. 
        Your signature dish is {chef['signature_dish']}.
        
        The user has specifically requested your no-oil recipe for {chef['no_oil']}.
        
        Please provide a detailed authentic recipe for {chef['no_oil']}, which is a {country} dish that uses no oil.
        
        Structure your response like this:
        1. Brief introduction about {chef['no_oil']} and why it's special without oil
        2. List all ingredients with precise measurements
        3. Step-by-step cooking instructions (numbered)
        4. Cooking tips and traditional variations
        5. Suggested presentation and pairings
        
        Make the recipe authentic and traditional to {country}.
        """
        
        try:
            with st.spinner(f"Chef {chef['name']} is preparing the recipe..."):
                response = model.generate_content(prompt)
                chef_response = response.text
            
            # Display chef's response
            with st.chat_message("assistant", avatar=country_flag):
                st.markdown(f"""
                <div style="color: #000000;">
                    {chef_response}
                </div>
                """, unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": chef_response})
            
            # Reset request flag
            st.session_state.no_oil_request = False
            st.rerun()
        
        except Exception as e:
            st.error(f"Error generating recipe: {str(e)}")
            st.session_state.no_oil_request = False
    
    elif st.session_state.no_boil_request:
        # Create user message requesting no-boil recipe
        user_message = f"Can you share your no-boil recipe for {chef['no_boil']}?"
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="color: #000000;">
                {user_message}
            </div>
            """, unsafe_allow_html=True)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Generate chef's response for no-boil recipe
        prompt = f"""
        You are {chef['name']}, an expert chef specialized in {country} cuisine. 
        Your signature dish is {chef['signature_dish']}.
        
        The user has specifically requested your no-boil recipe for {chef['no_boil']}.
        
        Please provide a detailed authentic recipe for {chef['no_boil']}, which is a {country} dish that doesn't require boiling.
        
        Structure your response like this:
        1. Brief introduction about {chef['no_boil']} and why it's special without boiling
        2. List all ingredients with precise measurements
        3. Step-by-step cooking instructions (numbered)
        4. Cooking tips and traditional variations
        5. Suggested presentation and pairings
        
        Make the recipe authentic and traditional to {country}.
        """
        
        try:
            with st.spinner(f"Chef {chef['name']} is preparing the recipe..."):
                response = model.generate_content(prompt)
                chef_response = response.text
            
            # Display chef's response
            with st.chat_message("assistant", avatar=country_flag):
                st.markdown(f"""
                <div style="color: #000000;">
                    {chef_response}
                </div>
                """, unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": chef_response})
            
            # Reset request flag
            st.session_state.no_boil_request = False
            st.rerun()
        
        except Exception as e:
            st.error(f"Error generating recipe: {str(e)}")
            st.session_state.no_boil_request = False
            
    elif st.session_state.selected_dish:
        dish = st.session_state.selected_dish
        
        # Create user message requesting dish recipe
        user_message = f"I'd like to make {dish}. Can you share your recipe for it?"
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="color: ;">
                {user_message}
            </div>
            """, unsafe_allow_html=True)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Generate chef's response using Gemini
        prompt = f"""
        You are {chef['name']}, an expert chef specialized in {country} cuisine.
        Your signature dish is {chef['signature_dish']}.
        You also offer special recipes that don't require boiling ({chef['no_boil']}) 
        and recipes without oil ({chef['no_oil']}).
        
        Please provide a detailed authentic recipe for {dish}, which is a classic {country} dish.
        
        Structure your response like this:
        1. Brief introduction about {dish} and its origins/cultural significance in {country}
        2. List all ingredients with precise measurements
        3. Step-by-step cooking instructions (numbered)
        4. Cooking tips and traditional variations
        5. Suggested presentation and pairings
        
        Make the recipe authentic and traditional to {country}.
        If the dish traditionally uses oil or requires boiling, mention that you can also offer alternative
        no-oil dishes like {chef['no_oil']} or no-boil dishes like {chef['no_boil']}.
        """
        
        try:
            with st.spinner(f"Chef {chef['name']} is preparing the {dish} recipe..."):
                response = model.generate_content(prompt)
                chef_response = response.text
            
            # Display chef's response
            with st.chat_message("assistant", avatar=country_flag):
                st.markdown(f"""
                <div style="color: #ffffff;">
                    {chef_response}
                </div>
                """, unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": chef_response})
            
            # Reset selected dish
            st.session_state.selected_dish = None
            st.rerun()
            
        except Exception as e:
            st.error(f"Error generating recipe: {str(e)}")
            st.session_state.selected_dish = None
    
    # Chat container with styling
    chat_container = st.container()
    with chat_container:
        # Display chat history with enhanced styling
        for message in st.session_state.chat_history:
            role_icon = "👤" if message["role"] == "user" else country_flag
            
            with st.chat_message(message["role"], avatar=role_icon):
                st.markdown(f"""
                <div style="color: #ffffff;">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input - Make sure it's outside the container but still visible
    user_query = st.chat_input(f"Ask {chef['name']} for recipe advice...")
    
    # Process new user query from the chat input
    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="color: #ffffff;">
                {user_query}
            </div>
            """, unsafe_allow_html=True)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Generate chef's response using Gemini
        prompt = f"""
        You are {chef['name']}, an expert chef specialized in {country} cuisine. 
        Your signature dish is {chef['signature_dish']}.
        You also offer special recipes that don't require boiling ({chef['no_boil']}) 
        and recipes without oil ({chef['no_oil']}).
        
        You ONLY provide recipes and cooking advice related to {country} cuisine.
        If asked about other cuisines, politely redirect to {country} dishes.
        
        When providing recipes:
        1. List ingredients with measurements
        2. Provide step-by-step cooking instructions
        3. Add tips for authentic {country} flavor
        4. Suggest sides or drinks that pair well with the dish
        
        If the user asks for a no-oil recipe, suggest your specialty "{chef['no_oil']}" or other {country} dishes without oil.
        If the user asks for a no-boil recipe, suggest your specialty "{chef['no_boil']}" or other {country} dishes that don't require boiling.
        
        The user's question is: {user_query}
        """
        
        try:
            with st.spinner(f"Chef {chef['name']} is thinking..."):
                response = model.generate_content(prompt)
                chef_response = response.text
            
            # Display chef's response
            with st.chat_message("assistant", avatar=country_flag):
                st.markdown(f"""
                <div style="color: #ffffff;">
                    {chef_response}
                </div>
                """, unsafe_allow_html=True)
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": chef_response})
            st.rerun()
        
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")