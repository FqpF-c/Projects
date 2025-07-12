import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)

# Generate 14 days of sample sleep data
start_date = datetime(2025, 3, 22)
end_date = start_date + timedelta(days=13)

dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]

# Create fluctuating sleep-wake times to simulate real patterns
base_sleep_hour = 23  # 11 PM
base_sleep_min = 0
sleep_hour_var = 1  # 1 hour variation
sleep_min_var = 30  # 30 min variation

base_wake_hour = 7  # 7 AM
base_wake_min = 0
wake_hour_var = 1
wake_min_var = 30

# Generate sleep and wake times
sleep_times = []
wake_times = []
durations = []
wakeups = []
qualities = []
dream_flags = []
caffeine_amounts = []
exercise_mins = []
moods = []
stress_levels = []

mood_options = ["Very Bad", "Bad", "Neutral", "Good", "Very Good"]
stress_options = ["None", "Low", "Moderate", "High", "Extreme"]

# First create a pattern with some stress indicators
for i in range(14):
    # Weekend vs weekday effects
    is_weekend = (start_date + timedelta(days=i)).weekday() >= 5
    
    # Sleep time (later on weekends)
    sleep_hour_adj = base_sleep_hour + (1 if is_weekend else 0)
    sleep_hour = sleep_hour_adj + np.random.randint(-sleep_hour_var, sleep_hour_var + 1)
    sleep_min = base_sleep_min + np.random.randint(-sleep_min_var, sleep_min_var + 1)
    
    while sleep_min >= 60:
        sleep_hour += 1
        sleep_min -= 60
    while sleep_min < 0:
        sleep_hour -= 1
        sleep_min += 60
        
    sleep_hour = max(20, min(sleep_hour, 2))  # Limit between 8 PM and 2 AM
    
    # Format with leading zeros
    sleep_time = f"{sleep_hour % 24:02d}:{sleep_min:02d}"
    sleep_times.append(sleep_time)
    
    # Wake time (later on weekends)
    wake_hour_adj = base_wake_hour + (1 if is_weekend else 0)
    wake_hour = wake_hour_adj + np.random.randint(-wake_hour_var, wake_hour_var + 1)
    wake_min = base_wake_min + np.random.randint(-wake_min_var, wake_min_var + 1)
    
    while wake_min >= 60:
        wake_hour += 1
        wake_min -= 60
    while wake_min < 0:
        wake_hour -= 1
        wake_min += 60
        
    wake_hour = max(5, min(wake_hour, 11))  # Limit between 5 AM and 11 AM
    
    # Format with leading zeros
    wake_time = f"{wake_hour:02d}:{wake_min:02d}"
    wake_times.append(wake_time)
    
    # Calculate duration (simplified)
    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    
    # Handle overnight sleep crossing midnight
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)
    
    duration = (wake_dt - sleep_dt).total_seconds() / 3600  # hours
    durations.append(round(duration, 2))
    
    # Generate a stress pattern (higher in middle days)
    stress_factor = 0
    if 4 <= i <= 9:  # Middle period with higher stress
        stress_factor = (i - 3) * 0.5 if i < 7 else (10 - i) * 0.5
    
    # Sleep quality (lower during higher stress)
    quality = max(1, min(10, round(np.random.normal(8 - stress_factor, 1.5))))
    qualities.append(quality)
    
    # Wake-ups (more during higher stress)
    wakeup_count = max(0, min(5, round(np.random.normal(1 + stress_factor, 1))))
    wakeups.append(wakeup_count)
    
    # Dreams (random)
    dream_flags.append(random.choice([True, False]))
    
    # Caffeine (more during higher stress)
    caffeine = round(max(0, min(500, np.random.normal(100 + stress_factor * 30, 50))))
    caffeine_amounts.append(caffeine)
    
    # Exercise (less during higher stress)
    exercise = max(0, min(120, round(np.random.normal(40 - stress_factor * 10, 20))))
    exercise_mins.append(exercise)
    
    # Mood (worse during higher stress)
    mood_idx = max(0, min(4, round(np.random.normal(3 - stress_factor, 1))))
    moods.append(mood_options[mood_idx])
    
    # Perceived stress (higher during stressful period)
    stress_idx = max(0, min(4, round(np.random.normal(1 + stress_factor, 1))))
    stress_levels.append(stress_options[stress_idx])

# Create DataFrame
data = {
    "date": dates,
    "sleep_time": sleep_times,
    "wake_time": wake_times,
    "duration": durations,
    "quality": qualities,
    "wakeups": wakeups,
    "had_dreams": dream_flags,
    "caffeine_mg": caffeine_amounts,
    "exercise_min": exercise_mins,
    "mood": moods,
    "perceived_stress": stress_levels
}

df = pd.DataFrame(data)

# Save to Excel file
df.to_excel("sample_sleep_data.xlsx", index=False)

print("Sample sleep data Excel file created: sample_sleep_data.xlsx")

# Preview the data
print("\nPreview of the data:")
print(df.head(5))