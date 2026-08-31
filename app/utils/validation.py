import re

def validate_registration(username, email, password, confirm_password):
    """Validate student registration inputs."""
    errors = []
    
    if not username or len(username.strip()) < 3 or len(username.strip()) > 50:
        errors.append("Username must be between 3 and 50 characters.")
    
    if not re.match(r"^[a-zA-Z0-9_.]+$", username.strip()):
        errors.append("Username can only contain letters, numbers, underscores, and dots.")
        
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not email or not re.match(email_regex, email.strip()):
        errors.append("Please enter a valid email address.")
        
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")
        
    if password != confirm_password:
        errors.append("Passwords do not match.")
        
    return errors

def validate_wellness_input(data):
    """Validate daily wellness logging inputs."""
    errors = []
    
    # Sleep hours (0.0 to 24.0)
    sleep_hours = data.get('sleep_hours')
    if sleep_hours is not None and sleep_hours != '':
        try:
            val = float(sleep_hours)
            if val < 0.0 or val > 24.0:
                errors.append("Sleep hours must be between 0 and 24.")
        except ValueError:
            errors.append("Sleep hours must be a valid number.")

    # Sleep quality (1 to 5)
    sleep_quality = data.get('sleep_quality')
    if sleep_quality is not None and sleep_quality != '':
        try:
            val = int(sleep_quality)
            if val < 1 or val > 5:
                errors.append("Sleep quality rating must be between 1 and 5.")
        except ValueError:
            errors.append("Sleep quality must be an integer.")

    # Water glasses (0 to 30)
    water_glasses = data.get('water_glasses')
    if water_glasses is not None and water_glasses != '':
        try:
            val = int(water_glasses)
            if val < 0 or val > 30:
                errors.append("Water glasses must be between 0 and 30.")
        except ValueError:
            errors.append("Water glasses must be an integer.")

    # Exercise duration (0 to 600 mins)
    exercise_duration = data.get('exercise_duration')
    if exercise_duration is not None and exercise_duration != '':
        try:
            val = int(exercise_duration)
            if val < 0 or val > 600:
                errors.append("Exercise duration must be between 0 and 600 minutes.")
        except ValueError:
            errors.append("Exercise duration must be an integer.")

    # Mood (1 to 5)
    mood = data.get('mood')
    if mood is not None and mood != '':
        try:
            val = int(mood)
            if val < 1 or val > 5:
                errors.append("Mood rating must be between 1 and 5.")
        except ValueError:
            errors.append("Mood rating must be an integer.")

    # Stress (1 to 5)
    stress_level = data.get('stress_level')
    if stress_level is not None and stress_level != '':
        try:
            val = int(stress_level)
            if val < 1 or val > 5:
                errors.append("Stress level rating must be between 1 and 5.")
        except ValueError:
            errors.append("Stress level must be an integer.")

    # Study hours (0.0 to 24.0)
    study_hours = data.get('study_hours')
    if study_hours is not None and study_hours != '':
        try:
            val = float(study_hours)
            if val < 0.0 or val > 24.0:
                errors.append("Study hours must be between 0 and 24.")
        except ValueError:
            errors.append("Study hours must be a valid number.")

    return errors
