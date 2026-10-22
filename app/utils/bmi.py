"""
BMI (Body Mass Index) Calculation Utility & Integrated Machine Learning Health Assessment
Formula: BMI = weight_kg / (height_m * height_m)
where height_m = height_cm / 100.0
"""

from app.services.ml_service import (
    predict_health_status, predict_lifestyle_risk, get_personalized_action_plan, DISCLAIMER_TEXT
)

def calculate_bmi(height_cm, weight_kg):
    """
    Calculates BMI value accurately and classifies into standard adult WHO categories.
    
    Args:
        height_cm (float): Height in centimeters.
        weight_kg (float): Weight in kilograms.
        
    Returns:
        dict: {
            'bmi': float (rounded to 2 decimal places),
            'bmi_2dp': float,
            'bmi_1dp': float (for backward compatibility),
            'bmi_formatted': str (e.g. "22.86"),
            'category': str,
            'color': str (Bootstrap color class),
            'badge_bg': str,
            'health_tip': str,
            'is_valid': bool
        } or None if inputs are invalid.
    """
    if height_cm is None or weight_kg is None:
        return None
        
    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)
    except (ValueError, TypeError):
        return None

    if height_cm <= 0 or weight_kg <= 0:
        return None

    # Realistic physical boundaries check
    if height_cm < 40 or height_cm > 300 or weight_kg < 10 or weight_kg > 400:
        return None

    height_m = height_cm / 100.0
    bmi_raw = weight_kg / (height_m * height_m)
    bmi_2dp = round(bmi_raw, 2)
    bmi_1dp = round(bmi_raw, 1)

    if bmi_2dp < 18.5:
        category = "Underweight"
        color = "info"
        badge_bg = "#0284c7"
        health_tip = "Consider nutrient-dense meals and strength training to build healthy muscle mass."
    elif 18.5 <= bmi_2dp < 25.0:
        category = "Normal weight"
        color = "success"
        badge_bg = "#10b981"
        health_tip = "Great job! Maintain your balanced diet, regular exercise, and healthy sleep habits."
    elif 25.0 <= bmi_2dp < 30.0:
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
        'bmi': bmi_2dp,
        'bmi_2dp': bmi_2dp,
        'bmi_1dp': bmi_1dp,
        'bmi_formatted': f"{bmi_2dp:.2f}",
        'category': category,
        'color': color,
        'badge_bg': badge_bg,
        'health_tip': health_tip,
        'is_valid': True
    }

def get_integrated_health_assessment(height_cm, weight_kg, gender='Female', lifestyle_data=None):
    """
    Performs comprehensive health assessment:
      1. Mathematical BMI calculation (WHO adult categories, 2 decimal places).
      2. ML Model 1 health-status prediction based on body metrics (Dataset 1).
      3. Optional ML Model 2 lifestyle risk prediction if lifestyle_data is supplied (Dataset 2).
      4. Wellness suggestions and non-medical disclaimer.
    """
    bmi_result = calculate_bmi(height_cm, weight_kg)
    if not bmi_result:
        return {
            'success': False,
            'error': 'Invalid height or weight values provided.',
            'disclaimer': DISCLAIMER_TEXT
        }

    # Run Model 1: Body Metrics Health Status Classifier
    ml_body_metrics = predict_health_status(gender=gender, height_cm=height_cm, weight_kg=weight_kg)

    # Optional Model 2: Lifestyle risk assessment
    ml_lifestyle = None
    if lifestyle_data and isinstance(lifestyle_data, dict):
        # Merge height and weight into lifestyle data if missing
        if 'Height' not in lifestyle_data:
            lifestyle_data['Height'] = height_cm
        if 'Weight' not in lifestyle_data:
            lifestyle_data['Weight'] = weight_kg
        if 'Gender' not in lifestyle_data:
            lifestyle_data['Gender'] = gender
        ml_lifestyle = predict_lifestyle_risk(lifestyle_data)

    # Generate personalized recommendations
    personalized_plan = get_personalized_action_plan(
        bmi_result['category'],
        ml_body_metrics.get('predicted_label') if ml_body_metrics else None
    )

    return {
        'success': True,
        'height': float(height_cm),
        'weight': float(weight_kg),
        'gender': gender,
        'bmi': bmi_result['bmi'],
        'bmi_formatted': bmi_result['bmi_formatted'],
        'standard_category': bmi_result['category'],
        'standard_color': bmi_result['color'],
        'standard_badge_bg': bmi_result['badge_bg'],
        'standard_tip': bmi_result['health_tip'],
        'ml_status': ml_body_metrics,
        'ml_lifestyle': ml_lifestyle,
        'personalized_plan': personalized_plan,
        'disclaimer': DISCLAIMER_TEXT
    }
