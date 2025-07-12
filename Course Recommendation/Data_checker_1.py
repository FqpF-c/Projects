from flask import Flask, request, jsonify, send_file
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from werkzeug.utils import secure_filename
from pyngrok import ngrok
import os

# Initialize Flask
app = Flask(__name__)

# Basic configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set ngrok auth token
ngrok.set_auth_token("2sAOOCsyWgvmMS2bL5mD1MaJVXD_3LAxHpip6wfqH3SQRrEqm")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SimpleRecommender:
    def __init__(self, students_df, courses_df, interactions_df):
        self.students_df = students_df
        self.courses_df = courses_df
        self.interactions_df = interactions_df
        self.model = NearestNeighbors(n_neighbors=5, metric='cosine')

    def prepare_data(self):
        # Create simple course features
        self.course_features = pd.get_dummies(self.courses_df[['subject', 'difficulty_level']])

        # Train the model
        self.model.fit(self.course_features)

    def recommend_courses(self, student_id, n_recommendations=5):
        # Get courses the student has taken
        taken_courses = self.interactions_df[
            self.interactions_df['student_id'] == student_id
        ]['course_id'].tolist()

        if not taken_courses:
            # If no courses taken, recommend most popular courses
            popular_courses = self.interactions_df.groupby('course_id')['assessment_score'].mean()
            return popular_courses.nlargest(n_recommendations).index.tolist()

        # Get similar courses to the ones taken
        recommendations = []
        for course_id in taken_courses:
            course_idx = self.courses_df[self.courses_df['course_id'] == course_id].index[0]
            _, indices = self.model.kneighbors([self.course_features.iloc[course_idx]])

            for idx in indices[0]:
                rec_course = self.courses_df.iloc[idx]['course_id']
                if rec_course not in taken_courses and rec_course not in recommendations:
                    recommendations.append(rec_course)
                    if len(recommendations) >= n_recommendations:
                        break

        return recommendations[:n_recommendations]

    def get_student_performance(self, student_id):
        student_data = self.interactions_df[self.interactions_df['student_id'] == student_id]
        if len(student_data) == 0:
            return {
                'courses_taken': 0,
                'avg_score': 0.0,
                'subjects': []
            }
        return {
            'courses_taken': len(student_data),
            'avg_score': float(student_data['assessment_score'].mean()),
            'subjects': self.courses_df[
                self.courses_df['course_id'].isin(student_data['course_id'])
            ]['subject'].unique().tolist()
        }

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduRecommend | Smart Course Recommendations</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4361ee;
                --primary-dark: #3a56d4;
                --secondary: #7209b7;
                --success: #06d6a0;
                --warning: #ffd166;
                --danger: #ef476f;
                --light: #f8f9fa;
                --dark: #212529;
                --gray-100: #f8f9fa;
                --gray-200: #e9ecef;
                --gray-300: #dee2e6;
                --gray-400: #ced4da;
                --gray-500: #adb5bd;
                --gray-600: #6c757d;
                --gray-700: #495057;
                --gray-800: #343a40;
                --gray-900: #212529;
                --transition: all 0.3s ease;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                --radius: 8px;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Poppins', sans-serif;
                background-color: #f5f7ff;
                color: var(--gray-800);
                line-height: 1.6;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .header {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
                padding: 2rem 0;
                margin-bottom: 2rem;
                border-radius: 0 0 20px 20px;
                box-shadow: var(--shadow);
            }
            
            .header-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
                max-width: 600px;
                margin-bottom: 1rem;
            }
            
            .card {
                background: white;
                border-radius: var(--radius);
                box-shadow: var(--shadow);
                padding: 2rem;
                margin-bottom: 2rem;
                transition: var(--transition);
            }
            
            .card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-5px);
            }
            
            .card-title {
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                color: var(--primary);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .upload-area {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }
            
            .file-input-group {
                position: relative;
                padding: 1.5rem;
                border: 2px dashed var(--gray-300);
                border-radius: var(--radius);
                text-align: center;
                transition: var(--transition);
            }
            
            .file-input-group:hover {
                border-color: var(--primary);
                background-color: rgba(67, 97, 238, 0.05);
            }
            
            .file-input-group label {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
            }
            
            .file-input-group i {
                font-size: 2rem;
                margin-bottom: 0.5rem;
                color: var(--primary);
            }
            
            .file-input-group input[type="file"] {
                position: absolute;
                width: 0;
                height: 0;
                opacity: 0;
            }
            
            .file-input-group .file-name {
                margin-top: 0.5rem;
                font-size: 0.875rem;
                color: var(--gray-600);
            }
            
            .file-label {
                font-weight: 600;
                margin-bottom: 0.25rem;
                font-size: 1rem;
            }
            
            .file-hint {
                font-size: 0.85rem;
                color: var(--gray-600);
            }
            
            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background-color: var(--primary);
                color: white;
                border: none;
                border-radius: var(--radius);
                font-weight: 600;
                cursor: pointer;
                transition: var(--transition);
                font-size: 1rem;
                text-align: center;
                text-decoration: none;
            }
            
            .btn:hover {
                background-color: var(--primary-dark);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            
            .btn-lg {
                padding: 1rem 2rem;
                font-size: 1.125rem;
            }
            
            .btn-block {
                display: block;
                width: 100%;
            }
            
            .submit-btn {
                margin-top: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            
            #loading {
                display: none;
                text-align: center;
                padding: 2rem;
            }
            
            .loader {
                display: inline-block;
                width: 50px;
                height: 50px;
                border: 4px solid rgba(67, 97, 238, 0.2);
                border-radius: 50%;
                border-top-color: var(--primary);
                animation: spin 1s ease-in-out infinite;
                margin-bottom: 1rem;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .results-wrapper {
                display: none;
                animation: fadeIn 0.5s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }
            
            .results-title {
                font-size: 1.5rem;
                color: var(--primary);
                font-weight: 600;
            }
            
            .download-btn {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background-color: var(--success);
                color: white;
                border-radius: var(--radius);
                text-decoration: none;
                font-weight: 500;
                font-size: 0.9rem;
                transition: var(--transition);
            }
            
            .download-btn:hover {
                background-color: #05b589;
                transform: translateY(-2px);
            }
            
            .results-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            
            .student-card {
                background: white;
                border-radius: var(--radius);
                overflow: hidden;
                box-shadow: var(--shadow);
                transition: var(--transition);
            }
            
            .student-card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-5px);
            }
            
            .student-header {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                padding: 1.5rem;
                color: white;
            }
            
            .student-id {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .student-body {
                padding: 1.5rem;
            }
            
            .performance-section {
                margin-bottom: 1.5rem;
            }
            
            .section-title {
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                color: var(--gray-700);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .stat {
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid var(--gray-200);
            }
            
            .stat:last-child {
                border-bottom: none;
            }
            
            .stat-label {
                color: var(--gray-600);
                font-size: 0.875rem;
            }
            
            .stat-value {
                font-weight: 500;
                font-size: 0.875rem;
            }
            
            .badge {
                display: inline-block;
                padding: 0.25em 0.75em;
                font-size: 0.75rem;
                font-weight: 500;
                border-radius: 50px;
                margin-right: 0.25rem;
                margin-bottom: 0.25rem;
            }
            
            .badge-primary {
                background-color: rgba(67, 97, 238, 0.1);
                color: var(--primary);
            }
            
            .badge-secondary {
                background-color: rgba(114, 9, 183, 0.1);
                color: var(--secondary);
            }
            
            .badge-success {
                background-color: rgba(6, 214, 160, 0.1);
                color: var(--success);
            }
            
            .badge-danger {
                background-color: rgba(239, 71, 111, 0.1);
                color: var(--danger);
            }
            
            .badge-warning {
                background-color: rgba(255, 209, 102, 0.1);
                color: #e6b800;
            }
            
            .recommended-courses {
                margin-top: 1.5rem;
            }
            
            .course-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.75rem;
                background-color: var(--gray-100);
                border-radius: var(--radius);
                margin-bottom: 0.5rem;
                transition: var(--transition);
            }
            
            .course-item:hover {
                background-color: rgba(67, 97, 238, 0.1);
            }
            
            .course-icon {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
                background-color: var(--primary);
                color: white;
                border-radius: 50%;
                font-size: 0.75rem;
            }
            
            .error {
                padding: 1rem;
                background-color: rgba(239, 71, 111, 0.1);
                color: var(--danger);
                border-radius: var(--radius);
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .footer {
                text-align: center;
                padding: 2rem 0;
                color: var(--gray-600);
                font-size: 0.875rem;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 2rem;
                }
                
                .card {
                    padding: 1.5rem;
                }
                
                .results-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            /* File name display style */
            .file-name-display {
                background-color: rgba(67, 97, 238, 0.1);
                color: var(--primary);
                padding: 0.5rem 1rem;
                border-radius: var(--radius);
                margin-top: 0.5rem;
                display: none;
                animation: fadeIn 0.3s ease;
                font-size: 0.85rem;
            }
            
            /* Empty state / students not found */
            .empty-state {
                text-align: center;
                padding: 3rem 2rem;
                background-color: var(--gray-100);
                border-radius: var(--radius);
                color: var(--gray-600);
            }
            
            .empty-state i {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: var(--gray-400);
            }
            
            /* Score indicator */
            .score-indicator {
                position: relative;
                height: 4px;
                background-color: var(--gray-200);
                border-radius: 4px;
                overflow: hidden;
                margin: 0.5rem 0;
            }
            
            .score-bar {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                transition: width 1s ease;
            }
            
            .score-high {
                background-color: var(--success);
            }
            
            .score-medium {
                background-color: var(--warning);
            }
            
            .score-low {
                background-color: var(--danger);
            }

            .course-title {
                font-weight: 500;
                font-size: 0.9rem;
            }

            .course-id {
                font-size: 0.75rem;
                color: var(--gray-500);
                margin-top: 3px;
            }
        </style>
    </head>
    <body>
        <header class="header">
            <div class="container">
                <div class="header-content">
                    <h1><i class="fas fa-graduation-cap"></i> EduRecommend</h1>
                    <p>Upload your e-learning data and discover personalized course recommendations for your students</p>
                </div>
            </div>
        </header>
        
        <main class="container">
            <div class="card">
                <h2 class="card-title"><i class="fas fa-cloud-upload-alt"></i> Data Upload</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="upload-area">
                        <div class="file-input-group">
                            <label for="students">
                                <i class="fas fa-users"></i>
                                <span class="file-label">Students Data</span>
                                <span class="file-hint">Upload your students CSV file</span>
                                <input type="file" id="students" name="students" accept=".csv" required>
                                <div id="students-file-name" class="file-name-display"></div>
                            </label>
                        </div>
                        
                        <div class="file-input-group">
                            <label for="courses">
                                <i class="fas fa-book"></i>
                                <span class="file-label">Courses Data</span>
                                <span class="file-hint">Upload your courses CSV file</span>
                                <input type="file" id="courses" name="courses" accept=".csv" required>
                                <div id="courses-file-name" class="file-name-display"></div>
                            </label>
                        </div>
                        
                        <div class="file-input-group">
                            <label for="interactions">
                                <i class="fas fa-chart-line"></i>
                                <span class="file-label">Interactions Data</span>
                                <span class="file-hint">Upload your learning interactions CSV file</span>
                                <input type="file" id="interactions" name="interactions" accept=".csv" required>
                                <div id="interactions-file-name" class="file-name-display"></div>
                            </label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-lg btn-block submit-btn">
                        <i class="fas fa-magic"></i> Generate Recommendations
                    </button>
                </form>
            </div>
            
            <div id="loading">
                <div class="loader"></div>
                <p>Analyzing data and generating personalized recommendations...</p>
                <p class="text-muted">This may take a moment depending on the size of your data</p>
            </div>
            
            <div id="results" class="results-wrapper">
                <!-- Results will be inserted here by JavaScript -->
            </div>
        </main>
        
        <footer class="footer">
            <div class="container">
                <p>&copy; 2025 EduRecommend - Smart Course Recommendation System</p>
            </div>
        </footer>

        <script>
            // Handle file input display
            document.getElementById('students').addEventListener('change', function(e) {
                const fileName = e.target.files[0]?.name || '';
                const fileNameDisplay = document.getElementById('students-file-name');
                if (fileName) {
                    fileNameDisplay.textContent = fileName;
                    fileNameDisplay.style.display = 'block';
                } else {
                    fileNameDisplay.style.display = 'none';
                }
            });
            
            document.getElementById('courses').addEventListener('change', function(e) {
                const fileName = e.target.files[0]?.name || '';
                const fileNameDisplay = document.getElementById('courses-file-name');
                if (fileName) {
                    fileNameDisplay.textContent = fileName;
                    fileNameDisplay.style.display = 'block';
                } else {
                    fileNameDisplay.style.display = 'none';
                }
            });
            
            document.getElementById('interactions').addEventListener('change', function(e) {
                const fileName = e.target.files[0]?.name || '';
                const fileNameDisplay = document.getElementById('interactions-file-name');
                if (fileName) {
                    fileNameDisplay.textContent = fileName;
                    fileNameDisplay.style.display = 'block';
                } else {
                    fileNameDisplay.style.display = 'none';
                }
            });
            
            // Form submission
            document.getElementById('uploadForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                
                fetch('/recommend', {
                    method: 'POST',
                    body: new FormData(this)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    // Create results container
                    let html = `
                        <div class="results-header">
                            <h2 class="results-title"><i class="fas fa-chart-bar"></i> Recommendation Results</h2>
                            <a href="/download" class="download-btn" download>
                                <i class="fas fa-file-download"></i> Download Full Report
                            </a>
                        </div>
                    `;
                    
                    // Ensure data is treated as an array
                    const resultsArray = Array.isArray(data) ? data : [data];
                    
                    if (resultsArray.length === 0) {
                        html += `
                            <div class="empty-state">
                                <i class="fas fa-search"></i>
                                <h3>No students found</h3>
                                <p>There were no students in the data you provided. Please check your files and try again.</p>
                            </div>
                        `;
                    } else {
                        html += '<div class="results-grid">';
                        
                        resultsArray.forEach(item => {
                            // Calculate score class
                            let scoreClass = 'score-medium';
                            if (item.performance.avg_score >= 80) {
                                scoreClass = 'score-high';
                            } else if (item.performance.avg_score < 60) {
                                scoreClass = 'score-low';
                            }
                            
                            // Create subject badges with different colors
                            const subjectBadges = item.performance.subjects.map((subject, index) => {
                                const badgeTypes = ['badge-primary', 'badge-secondary', 'badge-success', 'badge-warning', 'badge-danger'];
                                const badgeType = badgeTypes[index % badgeTypes.length];
                                return `<span class="badge ${badgeType}">${subject}</span>`;
                            }).join('');
                            
                            // Create course recommendations
                            const courseItems = item.recommendations.map((course, index) => {
                                const courseTitle = item.course_titles[index] || 'Untitled Course';
                                return `
                                    <div class="course-item">
                                        <div class="course-icon">${index + 1}</div>
                                        <div>
                                            <div class="course-title">${courseTitle}</div>
                                            <div class="course-id">${course}</div>
                                        </div>
                                    </div>
                                `;
                            }).join('');
                            
                            html += `
                                <div class="student-card">
                                    <div class="student-header">
                                        <div class="student-id">
                                            <i class="fas fa-user-graduate"></i> ${item.student_name || ('Student ' + item.student_id)}
                                        </div>
                                    </div>
                                    <div class="student-body">
                                        <div class="performance-section">
                                            <div class="section-title">
                                                <i class="fas fa-chart-pie"></i> Performance Overview
                                            </div>
                                            <div class="stat">
                                                <div class="stat-label">Courses Completed</div>
                                                <div class="stat-value">${item.performance.courses_taken}</div>
                                            </div>
                                            <div class="stat">
                                                <div class="stat-label">Average Score</div>
                                                <div class="stat-value">${item.performance.avg_score.toFixed(2)}</div>
                                            </div>
                                            <div class="score-indicator">
                                                <div class="score-bar ${scoreClass}" style="width: ${Math.min(100, item.performance.avg_score)}%;"></div>
                                            </div>
                                        </div>
                                        
                                        <div class="subject-section">
                                            <div class="section-title">
                                                <i class="fas fa-tags"></i> Subject Areas
                                            </div>
                                            <div class="subject-badges">
                                                ${subjectBadges || '<span class="text-muted">No subjects taken yet</span>'}
                                            </div>
                                        </div>
                                        
                                        <div class="recommended-courses">
                                            <div class="section-title">
                                                <i class="fas fa-lightbulb"></i> Recommended Courses
                                            </div>
                                            ${courseItems || '<div class="empty-text">No recommendations available</div>'}
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                    }
                    
                    const resultsElement = document.getElementById('results');
                    resultsElement.innerHTML = html;
                    resultsElement.style.display = 'block';
                    
                    // Animate score bars
                    setTimeout(() => {
                        const scoreBars = document.querySelectorAll('.score-bar');
                        scoreBars.forEach(bar => {
                            const width = bar.style.width;
                            bar.style.width = '0%';
                            setTimeout(() => {
                                bar.style.width = width;
                            }, 50);
                        });
                    }, 100);
                    
                    // Scroll to results
                    resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                })
                .catch(error => {
                    document.getElementById('results').innerHTML = `
                        <div class="error">
                            <i class="fas fa-exclamation-circle"></i>
                            <div>
                                <strong>Error:</strong> ${error.message}
                            </div>
                        </div>
                    `;
                    document.getElementById('results').style.display = 'block';
                })
                .finally(() => {
                    document.getElementById('loading').style.display = 'none';
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Save uploaded files
        files = {}
        for key in ['students', 'courses', 'interactions']:
            file = request.files[key]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                files[key] = filepath

        # Read data
        students_df = pd.read_csv(files['students'])
        courses_df = pd.read_csv(files['courses'])
        interactions_df = pd.read_csv(files['interactions'])

        # Convert IDs to strings if they aren't already
        students_df['student_id'] = students_df['student_id'].astype(str)
        courses_df['course_id'] = courses_df['course_id'].astype(str)
        interactions_df['student_id'] = interactions_df['student_id'].astype(str)
        interactions_df['course_id'] = interactions_df['course_id'].astype(str)

        # Initialize recommender
        recommender = SimpleRecommender(students_df, courses_df, interactions_df)
        recommender.prepare_data()

        # Create a mapping from course_id to course_title
        course_title_map = {}
        if 'course_title' in courses_df.columns:
            course_title_map = dict(zip(courses_df['course_id'], courses_df['course_title']))

        # Generate recommendations for each student
        results = []
        for student_id in students_df['student_id']:
            recommendations = recommender.recommend_courses(student_id)
            performance = recommender.get_student_performance(student_id)
            
            # Get student name if available
            student_name = None
            if 'student_name' in students_df.columns:
                student_name = students_df[students_df['student_id'] == student_id]['student_name'].values[0]
            
            # Get course titles for recommendations
            course_titles = []
            for course_id in recommendations:
                if course_id in course_title_map:
                    course_titles.append(course_title_map[course_id])
                else:
                    course_titles.append("Course " + course_id)

            results.append({
                'student_id': student_id,
                'student_name': student_name,
                'recommendations': recommendations,
                'course_titles': course_titles,
                'performance': performance
            })

        # Save results to CSV
        output_df = pd.DataFrame([{
            'student_id': r['student_id'],
            'student_name': r['student_name'] if r['student_name'] else r['student_id'],
            'courses_taken': r['performance']['courses_taken'],
            'average_score': r['performance']['avg_score'],
            'subjects': ', '.join(r['performance']['subjects']),
            'recommendations': ', '.join([f"{title} ({id})" for id, title in zip(r['recommendations'], r['course_titles'])])
        } for r in results])

        output_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'recommendations.csv'), index=False)

        # Clean up input files
        for filepath in files.values():
            os.remove(filepath)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], 'recommendations.csv'),
            as_attachment=True,
            download_name='recommendations.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting E-Learning Recommender System...")
    ngrok.kill()  # Kill any existing ngrok processes

    try:
        # Start ngrok
        public_url = ngrok.connect(5000).public_url
        print(f"🚀 EduRecommend is now running!")
        print(f"📊 Access your recommendation system at: {public_url}")
        print(f"📝 Use the sample data files (students_data.csv, courses_data.csv, interactions_data.csv) for testing")
        print(f"⭐ For the best experience, use a modern browser like Chrome or Firefox")
        
        # Start Flask
        app.run(port=5000)
    except Exception as e:
        print(f"❌ Error: {str(e)}")