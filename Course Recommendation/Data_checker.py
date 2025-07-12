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
    <html>
    <head>
        <title>Simple E-Learning Recommender</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            #loading, #result { margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>E-Learning Course Recommender</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label>Students Data (CSV):</label><br>
                <input type="file" name="students" accept=".csv" required>
            </div>
            <div class="form-group">
                <label>Courses Data (CSV):</label><br>
                <input type="file" name="courses" accept=".csv" required>
            </div>
            <div class="form-group">
                <label>Interactions Data (CSV):</label><br>
                <input type="file" name="interactions" accept=".csv" required>
            </div>
            <button type="submit">Generate Recommendations</button>
        </form>
        <div id="loading" style="display: none;">Processing...</div>
        <div id="result"></div>

        <script>
            document.getElementById('uploadForm').onsubmit = function(e) {
                e.preventDefault();

                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').innerHTML = '';

                fetch('/recommend', {
                    method: 'POST',
                    body: new FormData(this)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }

                    let html = '<h2>Results</h2>';
                    html += `<p><a href="/download" download>Download Full Report (CSV)</a></p>`;

                    // Ensure data is treated as an array
                    const resultsArray = Array.isArray(data) ? data : [data];

                    resultsArray.forEach(item => {
                        html += `
                            <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ddd;">
                                <h3>Student ${item.student_id}</h3>
                                <p>Courses Taken: ${item.performance.courses_taken}</p>
                                <p>Average Score: ${item.performance.avg_score.toFixed(2)}</p>
                                <p>Subjects: ${item.performance.subjects.join(', ')}</p>
                                <p>Recommended Courses: ${item.recommendations.join(', ')}</p>
                            </div>
                        `;
                    });

                    document.getElementById('result').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('result').innerHTML = `<div class="error" style="color: red;">Error: ${error.message}</div>`;
                })
                .finally(() => {
                    document.getElementById('loading').style.display = 'none';
                });
            };
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

        # Generate recommendations for each student
        results = []
        for student_id in students_df['student_id']:
            recommendations = recommender.recommend_courses(student_id)
            performance = recommender.get_student_performance(student_id)

            results.append({
                'student_id': student_id,  # No longer converting to int
                'recommendations': recommendations,
                'performance': performance
            })

        # Save results to CSV
        output_df = pd.DataFrame([{
            'student_id': r['student_id'],
            'courses_taken': r['performance']['courses_taken'],
            'average_score': r['performance']['avg_score'],
            'subjects': ', '.join(r['performance']['subjects']),
            'recommendations': ', '.join(map(str, r['recommendations']))
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
        print(f"Public URL: {public_url}")

        # Start Flask
        app.run(port=5000)
    except Exception as e:
        print(f"Error: {str(e)}")