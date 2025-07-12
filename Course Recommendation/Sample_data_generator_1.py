import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_training_data(num_students=1000, num_courses=50, num_interactions=10000):
    """
    Generate synthetic training data for e-learning recommendation system with realistic names
    """
    # Sample student names
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
        "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy",
        "Christopher", "Lisa", "Daniel", "Margaret", "Matthew", "Betty", "Anthony", "Sandra", "Mark", "Ashley",
        "Donald", "Dorothy", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
        "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Melissa", "George", "Deborah", "Timothy", "Stephanie",
        "Ronald", "Rebecca", "Edward", "Sharon", "Jason", "Laura", "Jeffrey", "Cynthia", "Ryan", "Kathleen",
        "Jacob", "Amy", "Gary", "Angela", "Nicholas", "Shirley", "Eric", "Emma", "Jonathan", "Anna",
        "Stephen", "Samantha", "Larry", "Nicole", "Justin", "Katherine", "Scott", "Christine", "Brandon", "Helen",
        "Benjamin", "Debra", "Samuel", "Rachel", "Gregory", "Olivia", "Alexander", "Yolanda", "Patrick", "Sophia",
        "Frank", "Victoria", "Raymond", "Amber", "Jack", "Ava", "Dennis", "Mia", "Jerry", "Madison"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
        "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
        "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter",
        "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
        "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
        "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez",
        "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross",
        "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington",
        "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander", "Russell", "Griffin", "Diaz", "Hayes"
    ]
    
    # Course names by subject
    course_titles = {
        'Mathematics': [
            "Calculus Fundamentals", "Linear Algebra", "Discrete Mathematics", "Statistical Methods", 
            "Algebra & Geometry", "Probability Theory", "Advanced Calculus", "Mathematical Physics",
            "Numerical Analysis", "Math for Machine Learning", "Nonlinear Dynamics", "Game Theory",
            "Applied Mathematics", "Differential Equations", "Number Theory", "Mathematical Logic"
        ],
        'Programming': [
            "Python for Beginners", "Advanced Java Programming", "Full Stack Web Development", 
            "Mobile App Development", "Data Structures & Algorithms", "C++ Fundamentals",
            "JavaScript Frameworks", "Rust Programming", "Swift for iOS", "Kotlin for Android",
            "Ruby on Rails", "Functional Programming", "Object-Oriented Design", "API Design & Development",
            "Database Programming", "Cybersecurity Coding", "Cloud Development", "Game Programming"
        ],
        'Data Science': [
            "Data Analysis with Python", "Machine Learning Fundamentals", "Big Data Processing", 
            "Data Visualization Techniques", "Statistical Learning", "Natural Language Processing",
            "Deep Learning Architectures", "Computer Vision", "Data Engineering", "Time Series Analysis",
            "Recommender Systems", "A/B Testing", "Reinforcement Learning", "Data Ethics & Privacy",
            "Predictive Analytics", "Business Intelligence", "Data Mining", "Applied ML Projects"
        ],
        'Business': [
            "Marketing Fundamentals", "Financial Management", "Strategic Leadership", "Business Analytics", 
            "Project Management", "Entrepreneurship Essentials", "Supply Chain Management",
            "Operations Research", "Business Law", "Digital Marketing", "Corporate Finance",
            "International Business", "Organizational Behavior", "Human Resource Management",
            "Negotiation Skills", "Business Ethics", "Change Management", "Business Communication"
        ],
        'Language': [
            "Spanish for Beginners", "Business English", "Mandarin Chinese", "French Language & Culture", 
            "Japanese Fundamentals", "German for Travelers", "Italian Cooking & Language",
            "Russian Essentials", "Arabic Writing System", "Korean Conversation", "Portuguese Basics",
            "Hindi Language", "Greek Language & Mythology", "Latin Fundamentals", "Hebrew Alphabet",
            "Swedish for Beginners", "Dutch Language Basics", "Vietnamese Communication"
        ]
    }

    # Student profiles
    students = []
    for student_id in range(num_students):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        student = {
            'student_id': f"STU_{student_id}",
            'student_name': full_name,
            'age_group': random.choice(['18-24', '25-34', '35-44', '45+']),
            'education_level': random.choice(['High School', 'Bachelors', 'Masters', 'PhD']),
            'learning_style': random.choice(['visual', 'auditory', 'reading', 'kinesthetic']),
            'study_time_preference': random.choice(['morning', 'afternoon', 'evening']),
            'device_preference': random.choice(['mobile', 'tablet', 'desktop'])
        }
        students.append(student)

    # Course catalog
    courses = []
    subjects = list(course_titles.keys())
    course_id_counter = 0
    
    # Ensure we have enough courses for each subject
    for subject in subjects:
        # Get titles for this subject
        available_titles = course_titles[subject].copy()
        # Determine how many courses to create for this subject
        courses_per_subject = max(1, num_courses // len(subjects))
        
        # Create courses for this subject
        for _ in range(min(courses_per_subject, len(available_titles))):
            # Get a random title that hasn't been used yet
            title = random.choice(available_titles)
            available_titles.remove(title)  # Remove to avoid duplicates
            
            course = {
                'course_id': f"CRS_{course_id_counter}",
                'course_title': title,
                'subject': subject,
                'difficulty_level': random.choice(['beginner', 'intermediate', 'advanced']),
                'duration_hours': random.randint(10, 100),
                'content_types': {
                    'video': random.random(),
                    'text': random.random(),
                    'quiz': random.random(),
                    'interactive': random.random()
                }
            }
            courses.append(course)
            course_id_counter += 1

    # If we need more courses, add additional ones with potentially repeated titles
    while len(courses) < num_courses:
        subject = random.choice(subjects)
        title = random.choice(course_titles[subject])
        
        course = {
            'course_id': f"CRS_{course_id_counter}",
            'course_title': title,
            'subject': subject,
            'difficulty_level': random.choice(['beginner', 'intermediate', 'advanced']),
            'duration_hours': random.randint(10, 100),
            'content_types': {
                'video': random.random(),
                'text': random.random(),
                'quiz': random.random(),
                'interactive': random.random()
            }
        }
        courses.append(course)
        course_id_counter += 1

    # Learning interactions
    interactions = []
    for _ in range(num_interactions):
        student = random.choice(students)
        course = random.choice(courses)

        interaction = {
            'interaction_id': f'INT_{_}',
            'student_id': student['student_id'],
            'student_name': student['student_name'],
            'course_id': course['course_id'],
            'course_title': course['course_title'],
            'timestamp': datetime.now() - timedelta(days=random.randint(0, 365)),
            'completion_rate': random.random(),
            'assessment_score': random.randint(0, 100),
            'time_spent_minutes': random.randint(5, 180),
            'content_type_engagement': {
                'video_watched': random.random(),
                'text_read': random.random(),
                'quiz_completed': random.random(),
                'interactive_completed': random.random()
            },
            'satisfaction_rating': random.randint(1, 5)
        }
        interactions.append(interaction)

    return pd.DataFrame(students), pd.DataFrame(courses), pd.DataFrame(interactions)

# Example schema for actual production data
class DataSchema:
    STUDENT_FEATURES = {
        'demographic_data': [
            'student_id',          # Unique identifier
            'student_name',        # Full name of student
            'age_group',           # Age range
            'education_level',     # Current education level
            'location',            # Geographic location
            'language_preference', # Preferred learning language
            'professional_field'   # Current or target profession
        ],

        'learning_preferences': [
            'learning_style',          # Visual/Auditory/Reading/Kinesthetic
            'study_time_preference',   # Preferred study hours
            'device_preference',       # Preferred device for learning
            'content_type_preference', # Preferred content types
            'pace_preference'          # Preferred learning speed
        ],

        'technical_context': [
            'device_types',        # Devices used for learning
            'internet_speed',      # Average connection speed
            'browser_type',        # Preferred browser
            'accessibility_needs'  # Any accessibility requirements
        ]
    }

    COURSE_FEATURES = {
        'metadata': [
            'course_id',           # Unique identifier
            'course_title',        # Course title
            'subject',             # Subject area
            'difficulty_level',    # Beginner/Intermediate/Advanced
            'prerequisites',       # Required prior knowledge
            'duration_hours',      # Estimated completion time
            'creation_date',       # When the course was created
            'last_updated'         # Last content update
        ],

        'content_attributes': [
            'content_types',       # Types of content included
            'interactive_elements',# Interactive features
            'assessment_methods',  # Types of assessments
            'learning_objectives', # Course objectives
            'skill_level_gain'    # Expected skill improvement
        ]
    }

    INTERACTION_FEATURES = {
        'engagement_metrics': [
            'interaction_id',      # Unique identifier
            'student_id',          # Student identifier
            'student_name',        # Student name
            'course_id',           # Course identifier
            'course_title',        # Course title
            'timestamp',           # When interaction occurred
            'session_duration',    # Length of study session
            'completion_rate',     # Progress through course
            'assessment_scores',   # Scores on tests/quizzes
            'engagement_level'     # Overall engagement metric
        ],

        'behavioral_data': [
            'content_type_usage',  # Time spent on different content types
            'navigation_patterns', # How user moves through content
            'repeat_visits',       # Content revisit frequency
            'time_of_day',        # When user typically studies
            'device_used'         # Device used for session
        ],

        'performance_metrics': [
            'exercise_completion', # Completion rate of exercises
            'quiz_attempts',       # Number of quiz attempts
            'assignment_grades',   # Grades received
            'time_to_complete',    # Time taken to complete units
            'error_patterns'       # Common mistakes made
        ]
    }

students_df, courses_df, interactions_df = generate_sample_training_data(
    num_students=100,    # Starting with smaller numbers for testing
    num_courses=20,
    num_interactions=500
)

# View the first few rows of each dataset
print("\nStudent Data:")
print(students_df.head())

print("\nCourse Data:")
print(courses_df.head())

print("\nInteractions Data:")
print(interactions_df.head())

# Save the data to CSV files if you want to use it later
students_df.to_csv('students_data.csv', index=False)
courses_df.to_csv('courses_data.csv', index=False)
interactions_df.to_csv('interactions_data.csv', index=False)

print("\nSample data files have been generated:")
print("- students_data.csv: Contains information about 100 students with realistic names")
print("- courses_data.csv: Contains information about 20 courses with meaningful titles")
print("- interactions_data.csv: Contains 500 learning interactions between students and courses")
print("\nYou can now use these files with your EduRecommend application.")