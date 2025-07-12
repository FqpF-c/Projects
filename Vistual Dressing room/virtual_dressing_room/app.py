# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'virtual_dressing_room_secret_key'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Sample clothing data - in a real app, this would be in a database
CLOTHING_ITEMS = {
    'tops': [
        {'id': 't1', 'name': 'T-Shirt (White)', 'image': 'static/clothes/tshirt_white.png', 'category': 'tops'},
        {'id': 't2', 'name': 'T-Shirt (Black)', 'image': 'static/clothes/tshirt_black.png', 'category': 'tops'},
        {'id': 't3', 'name': 'Formal Shirt', 'image': 'static/clothes/formal_shirt.png', 'category': 'tops'},
        {'id': 't4', 'name': 'Hoodie', 'image': 'static/clothes/hoodie.png', 'category': 'tops'}
    ],
    'bottoms': [
        {'id': 'b1', 'name': 'Jeans (Blue)', 'image': 'static/clothes/jeans_blue.png', 'category': 'bottoms'},
        {'id': 'b2', 'name': 'Jeans (Black)', 'image': 'static/clothes/jeans_black.png', 'category': 'bottoms'},
        {'id': 'b3', 'name': 'Formal Pants', 'image': 'static/clothes/formal_pants.png', 'category': 'bottoms'},
        {'id': 'b4', 'name': 'Shorts', 'image': 'static/clothes/shorts.png', 'category': 'bottoms'}
    ],
    'outerwear': [
        {'id': 'o1', 'name': 'Jacket', 'image': 'static/clothes/jacket.png', 'category': 'outerwear'},
        {'id': 'o2', 'name': 'Coat', 'image': 'static/clothes/coat.png', 'category': 'outerwear'}
    ],
    'accessories': [
        {'id': 'a1', 'name': 'Hat', 'image': 'static/clothes/hat.png', 'category': 'accessories'},
        {'id': 'a2', 'name': 'Scarf', 'image': 'static/clothes/scarf.png', 'category': 'accessories'},
        {'id': 'a3', 'name': 'Glasses', 'image': 'static/clothes/glasses.png', 'category': 'accessories'}
    ]
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'user_photo' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['user_photo']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to ensure unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            unique_filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Store the file path in session
            session['user_photo'] = file_path
            
            return redirect(url_for('dressing_room'))
        else:
            flash('Invalid file type. Please upload a PNG, JPG, or JPEG file.')
    
    return render_template('upload_photo.html')

@app.route('/dressing_room')
def dressing_room():
    # Get user photo from session
    user_photo = session.get('user_photo')
    
    if not user_photo:
        # If no photo uploaded, use default model
        user_photo = 'static/default_model.png'
    
    # If the file doesn't exist (might have been deleted), use default
    if not os.path.exists(user_photo):
        user_photo = 'static/default_model.png'
    
    return render_template('dressing_room.html', 
                           user_photo=user_photo, 
                           clothing_items=CLOTHING_ITEMS)

@app.route('/try_on', methods=['POST'])
def try_on():
    data = request.get_json()
    selected_items = data.get('selected_items', [])
    
    # In a real app, this is where you'd process the image
    # For this demo, we just return success and the selected items
    return json.dumps({
        'success': True,
        'message': 'Outfit created successfully!',
        'selected_items': selected_items
    })

@app.route('/save_outfit', methods=['POST'])
def save_outfit():
    data = request.get_json()
    outfit_name = data.get('outfit_name', 'My Outfit')
    selected_items = data.get('selected_items', [])
    
    # In a real app, you would save this to a database
    # For this demo, we just return success
    return json.dumps({
        'success': True,
        'message': f'Outfit "{outfit_name}" saved successfully!'
    })

if __name__ == '__main__':
    app.run(debug=True)