import pytest
from app.utils.bmi import calculate_bmi, get_integrated_health_assessment
from app.services.ml_service import get_model_1, get_model_2, predict_health_status, predict_lifestyle_risk

def test_calculate_bmi_normal():
    # 175 cm, 70 kg -> BMI = 70 / (1.75^2) = 22.8571... -> 22.86 (2 decimal places)
    res = calculate_bmi(175, 70)
    assert res is not None
    assert res['bmi'] == 22.86
    assert res['bmi_1dp'] == 22.9
    assert res['category'] == "Normal weight"
    assert res['color'] == "success"

def test_calculate_bmi_underweight():
    # 180 cm, 55 kg -> BMI = 55 / (1.8^2) = 16.9753... -> 16.98
    res = calculate_bmi(180, 55)
    assert res is not None
    assert res['bmi'] == 16.98
    assert res['bmi_1dp'] == 17.0
    assert res['category'] == "Underweight"
    assert res['color'] == "info"

def test_calculate_bmi_overweight():
    # 170 cm, 78 kg -> BMI = 78 / (1.7^2) = 26.9896... -> 26.99
    res = calculate_bmi(170, 78)
    assert res is not None
    assert res['bmi'] == 26.99
    assert res['bmi_1dp'] == 27.0
    assert res['category'] == "Overweight"
    assert res['color'] == "warning"

def test_calculate_bmi_obese():
    # 165 cm, 90 kg -> BMI = 90 / (1.65^2) = 33.0578... -> 33.06
    res = calculate_bmi(165, 90)
    assert res is not None
    assert res['bmi'] == 33.06
    assert res['bmi_1dp'] == 33.1
    assert res['category'] == "Obese"
    assert res['color'] == "danger"

def test_bmi_category_boundaries():
    # Boundary: 18.49 -> Underweight
    res_under = calculate_bmi(100, 18.49)
    assert res_under['category'] == "Underweight"
    
    # Boundary: 18.50 -> Normal weight
    res_normal_low = calculate_bmi(100, 18.50)
    assert res_normal_low['category'] == "Normal weight"
    
    # Boundary: 24.99 -> Normal weight
    res_normal_high = calculate_bmi(100, 24.99)
    assert res_normal_high['category'] == "Normal weight"
    
    # Boundary: 25.00 -> Overweight
    res_over_low = calculate_bmi(100, 25.00)
    assert res_over_low['category'] == "Overweight"
    
    # Boundary: 29.99 -> Overweight
    res_over_high = calculate_bmi(100, 29.99)
    assert res_over_high['category'] == "Overweight"
    
    # Boundary: 30.00 -> Obese
    res_obese_low = calculate_bmi(100, 30.00)
    assert res_obese_low['category'] == "Obese"

def test_calculate_bmi_invalid_input():
    assert calculate_bmi(0, 70) is None
    assert calculate_bmi(170, -5) is None
    assert calculate_bmi("invalid", 70) is None
    assert calculate_bmi(None, None) is None
    assert calculate_bmi(10, 70) is None  # Below realistic height bound
    assert calculate_bmi(170, 5) is None   # Below realistic weight bound

def test_model_1_loading_and_prediction():
    model = get_model_1()
    assert model is not None
    pred = predict_health_status(gender='Female', height_cm=165, weight_kg=60)
    assert pred['success'] is True
    assert pred['predicted_label'] in ['Extremely Weak', 'Weak', 'Normal', 'Overweight', 'Obesity', 'Extreme Obesity']
    assert 0 <= pred['confidence'] <= 100
    assert len(pred['suggestions']) > 0
    assert 'Disclaimer' in pred['disclaimer']

def test_model_2_loading_and_prediction():
    model = get_model_2()
    assert model is not None
    sample = {
        'Gender': 'Female',
        'Age': 22,
        'Height': 165,
        'Weight': 60,
        'family_history_with_overweight': 'no',
        'FAVC': 'no',
        'FCVC': 2.0,
        'NCP': 3.0,
        'CAEC': 'Sometimes',
        'SMOKE': 'no',
        'CH2O': 2.0,
        'SCC': 'no',
        'FAF': 1.0,
        'TUE': 1.0,
        'CALC': 'Sometimes',
        'MTRANS': 'Public_Transportation'
    }
    pred = predict_lifestyle_risk(sample)
    assert pred['success'] is True
    assert pred['predicted_label'] != 'Unavailable'
    assert 0 <= pred['confidence'] <= 100

def test_integrated_health_assessment():
    res = get_integrated_health_assessment(175, 70, gender='Male')
    assert res['success'] is True
    assert res['bmi'] == 22.86
    assert res['standard_category'] == "Normal weight"
    assert res['ml_status']['success'] is True
    assert 'disclaimer' in res
