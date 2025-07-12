import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_training_data(num_students=1000, num_courses=50, num_interactions=10000):
    """
    Generate synthetic training data for e-learning recommendation system
    """
    # Student profiles
    students = []
    for student_id in range(num_students):
        student = {
            'student_id': f'STU_{student_id}',
            'age_group': random.choice(['18-24', '25-34', '35-44', '45+']),
            'education_level': random.choice(['High School', 'Bachelors', 'Masters', 'PhD']),
            'learning_style': random.choice(['visual', 'auditory', 'reading', 'kinesthetic']),
            'study_time_preference': random.choice(['morning', 'afternoon', 'evening']),
            'device_preference': random.choice(['mobile', 'tablet', 'desktop'])
        }
        students.append(student)

    # Course catalog
    courses = []
    subjects = ['Mathematics', 'Programming', 'Data Science', 'Business', 'Language']
    for course_id in range(num_courses):
        course = {
            'course_id': f'CRS_{course_id}',
            'subject': random.choice(subjects),
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

    # Learning interactions
    interactions = []
    for _ in range(num_interactions):
        student = random.choice(students)
        course = random.choice(courses)

        interaction = {
            'interaction_id': f'INT_{_}',
            'student_id': student['student_id'],
            'course_id': course['course_id'],
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
            'title',               # Course title
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
            'course_id',           # Course identifier
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