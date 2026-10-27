"""
Machine Learning Service for Student Health Status and Lifestyle Assessment
Loads pre-trained pipelines for:
  1. Body Metrics Health Status Classifier (Dataset 1: 500 Person Gender Height Weight)
  2. Multi-Factor Lifestyle & Obesity Risk Classifier (Dataset 2: UCI Lifestyle Dataset)
"""

import os
import joblib
import pandas as pd
import numpy as np

# Absolute or relative paths to artifacts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, 'ml_artifacts')

MODEL_1_PATH = os.path.join(ARTIFACTS_DIR, 'model_bmi_rf.joblib')
MODEL_2_PATH = os.path.join(ARTIFACTS_DIR, 'model_lifestyle_rf.joblib')

# In-memory singletons for fast inference
_MODEL_1 = None
_MODEL_2 = None

# Dataset 1 Index Mapping & Non-medical Wellness Guidance
DATASET_1_CLASSES = {
    0: {
        'label': 'Extremely Weak',
        'badge_class': 'bg-danger text-white',
        'color': '#ef4444',
        'explanation': "The machine learning model identifies a body metric profile significantly below typical weight-to-height ranges.",
        'suggestions': [
            "Focus on nutrient-dense, calorie-rich balanced meals including nuts, seeds, and healthy oils.",
            "Consider strength-building exercises to promote healthy muscle development.",
            "Consult with a campus nutritionist or healthcare provider for tailored nourishment guidance."
        ]
    },
    1: {
        'label': 'Weak',
        'badge_class': 'bg-info text-dark',
        'color': '#0ea5e9',
        'explanation': "The model detects a slender profile that sits beneath standard balanced weight-to-height curves.",
        'suggestions': [
            "Incorporate protein-rich foods into each meal (legumes, eggs, yogurt, or tofu).",
            "Pair regular meals with nourishing healthy snacks throughout your study day.",
            "Engage in resistance training rather than excessive prolonged cardiovascular workouts."
        ]
    },
    2: {
        'label': 'Normal',
        'badge_class': 'bg-success text-white',
        'color': '#10b981',
        'explanation': "The model recognizes a well-balanced body metric proportion matching typical healthy student benchmarks.",
        'suggestions': [
            "Maintain your current balanced diet of vegetables, fruits, whole grains, and lean proteins.",
            "Continue regular cardiovascular movement (30 minutes of brisk walking or sports most days).",
            "Keep consistent 7–9 hours of sleep and daily hydration to sustain your vibrant energy levels."
        ]
    },
    3: {
        'label': 'Overweight',
        'badge_class': 'bg-warning text-dark',
        'color': '#f59e0b',
        'explanation': "The model flags a weight profile slightly above median weight-to-height benchmarks.",
        'suggestions': [
            "Prioritize mindful portion control and reduce intake of high-sugar beverages and ultra-processed snacks.",
            "Integrate active walking or cycling into your daily campus commute.",
            "Aim for at least 150 minutes of moderate-intensity physical activity per week."
        ]
    },
    4: {
        'label': 'Obesity',
        'badge_class': 'bg-orange text-white',
        'color': '#ea580c',
        'explanation': "The model identifies body metric patterns corresponding to higher weight-to-height distribution categories.",
        'suggestions': [
            "Adopt gradual, sustainable lifestyle adjustments focused on fiber-rich whole foods and hydration.",
            "Break long sedentary study hours with 10-minute active walking or stretching intervals.",
            "Reach out to health professionals or wellness counseling for personalized guidance."
        ]
    },
    5: {
        'label': 'Extreme Obesity',
        'badge_class': 'bg-danger text-white',
        'color': '#b91c1c',
        'explanation': "The model identifies body metric metrics placed in the highest weight-to-height bracket in the reference dataset.",
        'suggestions': [
            "Engage in low-impact physical activities like swimming, walking, or gentle cycling to protect joints.",
            "Maintain a mindful daily hydration and balanced whole-food meal schedule.",
            "Consult a licensed medical doctor or health counselor for a comprehensive personal health assessment."
        ]
    }
}

DATASET_2_CLASSES = {
    'Insufficient_Weight': {
        'label': 'Insufficient Weight',
        'badge_class': 'bg-info text-dark',
        'risk_level': 'Low Weight Risk',
        'explanation': "Multi-factor assessment indicates nutritional or caloric intake may be insufficient relative to daily expenditure.",
        'suggestions': [
            "Ensure regular intake of 3 wholesome meals per day plus wholesome snacks.",
            "Monitor daily physical exertion against caloric consumption."
        ]
    },
    'Normal_Weight': {
        'label': 'Optimal Healthy Weight',
        'badge_class': 'bg-success text-white',
        'risk_level': 'Optimal Balance',
        'explanation': "Lifestyle and anthropometric data indicate healthy equilibrium between diet, physical activity, and body mass.",
        'suggestions': [
            "Outstanding balance! Continue your positive hydration and physical activity habits.",
            "Maintain consistent sleep hygiene to preserve optimal metabolism."
        ]
    },
    'Overweight_Level_I': {
        'label': 'Overweight Level I (Mild)',
        'badge_class': 'bg-warning text-dark',
        'risk_level': 'Mild Risk',
        'explanation': "Initial indicator that body mass is trending above standard baselines, modulated by lifestyle habits.",
        'suggestions': [
            "Increase daily water intake to replace sugary beverages.",
            "Add at least 30 minutes of aerobic activity 3 to 4 times a week."
        ]
    },
    'Overweight_Level_II': {
        'label': 'Overweight Level II (Moderate)',
        'badge_class': 'bg-warning text-dark',
        'risk_level': 'Moderate Risk',
        'explanation': "Noticeable divergence above median baseline with potential lifestyle contributing factors.",
        'suggestions': [
            "Limit high-calorie snacking between meals and increase vegetable intake.",
            "Reduce prolonged sedentary screen time with hourly mobility breaks."
        ]
    },
    'Obesity_Type_I': {
        'label': 'Obesity Type I',
        'badge_class': 'bg-orange text-white',
        'risk_level': 'Elevated Health Risk',
        'explanation': "Multi-factor behavioral analysis signals elevated weight category warranting positive habit interventions.",
        'suggestions': [
            "Structure consistent meal timings and focus on home-cooked whole food nutrition.",
            "Engage in regular low-to-moderate physical exercise."
        ]
    },
    'Obesity_Type_II': {
        'label': 'Obesity Type II',
        'badge_class': 'bg-danger text-white',
        'risk_level': 'High Health Risk',
        'explanation': "Significant statistical correlation with higher health risk indicators across activity and body metric metrics.",
        'suggestions': [
            "Prioritize joint-friendly physical movement such as brisk walking or water aerobics.",
            "Work with health counselors for customized fitness and dietary support."
        ]
    },
    'Obesity_Type_III': {
        'label': 'Obesity Type III (Severe)',
        'badge_class': 'bg-danger text-white',
        'risk_level': 'Severe Health Risk',
        'explanation': "Pattern corresponds to the highest category in the clinical obesity dataset.",
        'suggestions': [
            "Prioritize consulting a medical healthcare professional for specialized care.",
            "Focus on gentle daily movement, hydration, and mental well-being."
        ]
    }
}

DISCLAIMER_TEXT = (
    "Disclaimer: BMI is a preliminary screening measure, and machine learning "
    "predictions are statistical pattern estimates derived from research datasets. "
    "Neither BMI nor model predictions constitute a medical diagnosis or clinical advice. "
    "Please consult a qualified healthcare provider for personalized medical evaluation."
)

def get_model_1():
    """Lazy load Model 1 (Dataset 1 Random Forest pipeline)."""
    global _MODEL_1
    if _MODEL_1 is None:
        if os.path.exists(MODEL_1_PATH):
            _MODEL_1 = joblib.load(MODEL_1_PATH)
        else:
            raise FileNotFoundError(f"Model 1 artifact not found at {MODEL_1_PATH}")
    return _MODEL_1

def get_model_2():
    """Lazy load Model 2 (Dataset 2 Random Forest pipeline)."""
    global _MODEL_2
    if _MODEL_2 is None:
        if os.path.exists(MODEL_2_PATH):
            _MODEL_2 = joblib.load(MODEL_2_PATH)
        else:
            raise FileNotFoundError(f"Model 2 artifact not found at {MODEL_2_PATH}")
    return _MODEL_2

def predict_health_status(gender: str, height_cm: float, weight_kg: float) -> dict:
    """
    Predict health status category using Model 1 (Random Forest trained on Dataset 1).
    
    Args:
        gender: 'Male' or 'Female'
        height_cm: Height in centimeters (e.g. 175.0)
        weight_kg: Weight in kilograms (e.g. 70.0)
        
    Returns:
        dict containing predicted index, label, confidence, explanation, suggestions.
    """
    try:
        model = get_model_1()
        
        # Normalize gender
        norm_gender = 'Male' if str(gender).strip().lower() in ('male', 'm', '1') else 'Female'
        h = float(height_cm)
        w = float(weight_kg)
        bmi = round(w / ((h / 100.0) ** 2), 2)
        
        input_df = pd.DataFrame([{
            'Gender': norm_gender,
            'Height': h,
            'Weight': w,
            'BMI': bmi
        }])
        
        pred_idx = int(model.predict(input_df)[0])
        proba = model.predict_proba(input_df)[0]
        confidence = float(np.max(proba))
        
        meta = DATASET_1_CLASSES.get(pred_idx, {
            'label': f'Category {pred_idx}',
            'badge_class': 'bg-secondary text-white',
            'color': '#64748b',
            'explanation': 'Model classified body metrics into category ' + str(pred_idx),
            'suggestions': ['Maintain balanced meals, daily physical movement, and sufficient hydration.']
        })
        
        return {
            'success': True,
            'predicted_index': pred_idx,
            'predicted_label': meta['label'],
            'badge_class': meta['badge_class'],
            'color': meta['color'],
            'confidence': round(confidence * 100, 1),
            'explanation': meta['explanation'],
            'suggestions': meta['suggestions'],
            'disclaimer': DISCLAIMER_TEXT
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'predicted_label': 'Unavailable',
            'explanation': 'Machine learning model could not process inputs.',
            'disclaimer': DISCLAIMER_TEXT
        }

def analyze_lifestyle_factors(lifestyle_data: dict) -> dict:
    """
    Evaluates student lifestyle inputs to identify protective health habits
    versus risk/improvement areas based on behavioral and physiological criteria.
    """
    protective = []
    risks = []
    
    # 1. Hydration
    ch2o = float(lifestyle_data.get('CH2O', 2.0))
    if ch2o >= 2.0:
        protective.append({
            'title': 'Optimal Hydration',
            'detail': f'Drinking ~{ch2o:.1f}L of water daily promotes healthy metabolism and alertness.',
            'icon': 'bi-droplet-fill'
        })
    else:
        risks.append({
            'title': 'Sub-optimal Hydration',
            'detail': 'Daily water intake is under 2L. Increasing water intake can boost daytime study focus.',
            'icon': 'bi-droplet'
        })

    # 2. Physical Activity Frequency
    faf = float(lifestyle_data.get('FAF', 1.0))
    if faf >= 2.0:
        protective.append({
            'title': 'Consistent Exercise',
            'detail': 'Engaging in physical activity multiple days per week protects cardiovascular fitness.',
            'icon': 'bi-activity'
        })
    elif faf == 0.0:
        risks.append({
            'title': 'Sedentary Activity Level',
            'detail': '0 reported workout days per week. Adding 15-minute walks can significantly enhance well-being.',
            'icon': 'bi-exclamation-triangle'
        })

    # 3. Vegetables
    fcvc = float(lifestyle_data.get('FCVC', 2.0))
    if fcvc >= 2.5:
        protective.append({
            'title': 'High Vegetable Intake',
            'detail': 'Regular vegetable consumption provides rich fiber, minerals, and antioxidants.',
            'icon': 'bi-flower1'
        })
    elif fcvc <= 1.5:
        risks.append({
            'title': 'Low Vegetable Consumption',
            'detail': 'Infrequent vegetable portions. Incorporating greens supports digestive balance.',
            'icon': 'bi-basket'
        })

    # 4. High Calorie Food Frequency
    favc = str(lifestyle_data.get('FAVC', 'no')).strip().lower()
    if favc == 'no':
        protective.append({
            'title': 'Mindful Caloric Intake',
            'detail': 'Infrequent consumption of ultra-processed or high-calorie fast food.',
            'icon': 'bi-shield-check'
        })
    else:
        risks.append({
            'title': 'Frequent High-Calorie Food',
            'detail': 'Regular intake of calorie-dense meals. Replacing some with whole foods can improve vitality.',
            'icon': 'bi-fire'
        })

    # 5. Screen Time / Device Usage
    tue = float(lifestyle_data.get('TUE', 1.0))
    if tue >= 2.0:
        risks.append({
            'title': 'Extended Device Screen Time',
            'detail': 'Over 5 hours of recreational screen time daily increases sedentary study fatigue.',
            'icon': 'bi-display'
        })
    elif tue == 0.0:
        protective.append({
            'title': 'Low Sedentary Screen Time',
            'detail': 'Well-managed recreational screen time leaves more hours for active rest and sleep.',
            'icon': 'bi-phone'
        })

    # 6. Transportation Mode
    mtrans = str(lifestyle_data.get('MTRANS', '')).strip()
    if mtrans in ('Walking', 'Bike'):
        protective.append({
            'title': 'Active Campus Transit',
            'detail': f'Using {mtrans.lower()} for transport provides effortless daily baseline caloric expenditure.',
            'icon': 'bi-bicycle'
        })

    # 7. Family History
    fam = str(lifestyle_data.get('family_history_with_overweight', 'no')).strip().lower()
    if fam == 'yes':
        risks.append({
            'title': 'Genetic Weight Predisposition',
            'detail': 'Family history of overweight indicates proactive habit mindfulness is beneficial.',
            'icon': 'bi-people'
        })

    return {'protective': protective, 'risks': risks}

def get_personalized_action_plan(standard_category: str, ml_label: str) -> dict:
    """
    Auto-recommends actionable Wellvia challenges and daily habits tailored
    to the student's combined standard BMI category and ML classification.
    """
    cat = (standard_category or '').lower()
    ml = (ml_label or '').lower()
    
    if 'under' in cat or 'weak' in ml:
        return {
            'theme': 'Nourish & Strengthen',
            'accent_color': '#0284c7',
            'key_focus': 'Focus on muscle-building exercise, nutrient-dense calories, and consistent hydration.',
            'recommended_challenges': [
                {'title': 'Hydration Boost', 'badge': '+20 Pts', 'desc': 'Drink at least 8 glasses of water throughout your study day.'},
                {'title': 'Consistent Habit Tracker', 'badge': '+50 Pts', 'desc': 'Log your daily meals, sleep, and physical activity all week.'}
            ],
            'daily_tips': [
                'Pair complex carbohydrates with healthy proteins at each meal (e.g. oats with nuts, eggs, or yogurt).',
                'Engage in bodyweight strength exercises (pushups, squats) 2-3 times weekly rather than excessive cardio.'
            ]
        }
    elif 'over' in cat or 'obese' in cat or 'over' in ml or 'obese' in ml:
        return {
            'theme': 'Active Movement & Mindful Portions',
            'accent_color': '#f59e0b',
            'key_focus': 'Focus on daily step counts, reducing liquid sugars, and active study break stretches.',
            'recommended_challenges': [
                {'title': 'Study Break Stretches', 'badge': '+20 Pts', 'desc': 'Take a 10-minute active stretching break during study sessions.'},
                {'title': 'Hydration Boost', 'badge': '+20 Pts', 'desc': 'Replace sugary sodas or energy drinks with refreshing pure water.'},
                {'title': 'Weekly Exercise Master', 'badge': '+50 Pts', 'desc': 'Complete at least 3 exercise sessions this week (minimum 20 mins).' }
            ],
            'daily_tips': [
                'Take a brisk 15-minute walk around campus between lectures to kickstart circulation.',
                'Eat slowly and mindfully without phone screens to recognize natural fullness cues.'
            ]
        }
    else:
        return {
            'theme': 'Maintain Equilibrium & Vitality',
            'accent_color': '#10b981',
            'key_focus': 'Outstanding balance! Keep your positive consistency in sleep, hydration, and movement.',
            'recommended_challenges': [
                {'title': '8-Hour Sleep Night', 'badge': '+20 Pts', 'desc': 'Get 8 hours of restorative sleep tonight to consolidate memory.'},
                {'title': 'Hydration Boost', 'badge': '+20 Pts', 'desc': 'Maintain your optimal 8 glasses of water intake today.'},
                {'title': 'Weekly Exercise Master', 'badge': '+50 Pts', 'desc': 'Hit at least 3 active workouts or sports sessions this week.'}
            ],
            'daily_tips': [
                'Maintain a regular sleep schedule even during stressful exam preparation weeks.',
                'Continue balanced meal plates filled with half vegetables, one-quarter lean protein, and whole grains.'
            ]
        }

def predict_lifestyle_risk(lifestyle_data: dict) -> dict:
    """
    Predict obesity and lifestyle risk using Model 2 (trained on Dataset 2).
    Requires full lifestyle inputs - does not invent missing features.
    Also returns protective habits and risk area breakdowns.
    """
    try:
        model = get_model_2()
        
        required_keys = [
            'Gender', 'Age', 'Height', 'Weight', 'family_history_with_overweight',
            'FAVC', 'FCVC', 'NCP', 'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE',
            'CALC', 'MTRANS'
        ]
        
        for k in required_keys:
            if k not in lifestyle_data or lifestyle_data[k] is None:
                return {
                    'success': False,
                    'error': f"Missing required lifestyle feature: '{k}'.",
                    'disclaimer': DISCLAIMER_TEXT
                }
                
        # Normalize Height: Model 2 expects height in meters!
        h = float(lifestyle_data['Height'])
        if h > 3.0: # passed in cm
            h = h / 100.0
            
        row = {
            'Gender': 'Male' if str(lifestyle_data['Gender']).strip().lower() in ('male', 'm', '1') else 'Female',
            'Age': float(lifestyle_data['Age']),
            'Height': float(h),
            'Weight': float(lifestyle_data['Weight']),
            'family_history_with_overweight': str(lifestyle_data['family_history_with_overweight']),
            'FAVC': str(lifestyle_data['FAVC']),
            'FCVC': float(lifestyle_data['FCVC']),
            'NCP': float(lifestyle_data['NCP']),
            'CAEC': str(lifestyle_data['CAEC']),
            'SMOKE': str(lifestyle_data['SMOKE']),
            'CH2O': float(lifestyle_data['CH2O']),
            'SCC': str(lifestyle_data['SCC']),
            'FAF': float(lifestyle_data['FAF']),
            'TUE': float(lifestyle_data['TUE']),
            'CALC': str(lifestyle_data['CALC']),
            'MTRANS': str(lifestyle_data['MTRANS'])
        }
        
        input_df = pd.DataFrame([row])
        pred_label = str(model.predict(input_df)[0])
        proba = model.predict_proba(input_df)[0]
        confidence = float(np.max(proba))
        
        meta = DATASET_2_CLASSES.get(pred_label, {
            'label': pred_label.replace('_', ' '),
            'badge_class': 'bg-secondary text-white',
            'risk_level': 'Moderate',
            'explanation': f"Lifestyle classification result: {pred_label}",
            'suggestions': ['Focus on balanced daily nutrition, hydration, and regular movement.']
        })
        
        # Analyze behavioral breakdown (protective vs risk factors)
        factors = analyze_lifestyle_factors(lifestyle_data)
        
        return {
            'success': True,
            'predicted_class': pred_label,
            'predicted_label': meta['label'],
            'badge_class': meta['badge_class'],
            'risk_level': meta['risk_level'],
            'confidence': round(confidence * 100, 1),
            'explanation': meta['explanation'],
            'suggestions': meta['suggestions'],
            'protective_factors': factors['protective'],
            'risk_factors': factors['risks'],
            'disclaimer': DISCLAIMER_TEXT
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'predicted_label': 'Unavailable',
            'explanation': 'Machine learning model could not process lifestyle inputs.',
            'disclaimer': DISCLAIMER_TEXT
        }
