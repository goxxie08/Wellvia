"""
BMI (Body Mass Index) Calculation Utility & Health Insights
Formula: BMI = weight_kg / (height_m ^ 2) = weight_kg / ((height_cm / 100) ^ 2)
"""

def calculate_bmi(height_cm, weight_kg):
    """
    Calculates BMI value and classifies into standard WHO categories.
    
    Args:
        height_cm (float): Height in centimeters.
        weight_kg (float): Weight in kilograms.
        
    Returns:
        dict: {
            'bmi': float (rounded to 1 decimal place),
            'category': str,
            'color': str (Bootstrap color class),
            'badge_bg': str,
            'health_tip': str
        }
    """
    if not height_cm or not weight_kg:
        return None
        
    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)
    except (ValueError, TypeError):
        return None

    if height_cm <= 0 or weight_kg <= 0:
        return None

    height_m = height_cm / 100.0
    bmi_raw = weight_kg / (height_m ** 2)
    bmi = round(bmi_raw, 1)

    if bmi < 18.5:
        category = "Underweight"
        color = "info"
        badge_bg = "#0284c7"
        health_tip = "Consider nutrient-dense meals and strength training to build healthy muscle mass."
    elif 18.5 <= bmi < 25.0:
        category = "Normal weight"
        color = "success"
        badge_bg = "#10b981"
        health_tip = "Great job! Maintain your balanced diet, regular exercise, and healthy sleep habits."
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        color = "warning"
        badge_bg = "#f59e0b"
        health_tip = "Focus on active daily movement, portion control, and staying well-hydrated throughout the day."
    else:
        category = "Obese"
        color = "danger"
        badge_bg = "#ef4444"
        health_tip = "Prioritize daily brisk walks, balanced whole foods, and consulting a health professional for personalized guidance."

    return {
        'bmi': bmi,
        'category': category,
        'color': color,
        'badge_bg': badge_bg,
        'health_tip': health_tip
    }
