import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import pandas as pd
from app.services.ml_service import predict_health_status
from app.utils.bmi import calculate_bmi

test_cases = [
    # Severely Underweight (BMI < 16)
    {'gender': 'Female', 'h': 160, 'w': 36.2, 'desc': 'Severe Underweight (BMI 14.1)'},
    {'gender': 'Male',   'h': 170, 'w': 40.8, 'desc': 'Severe Underweight (BMI 14.1)'},
    {'gender': 'Female', 'h': 175, 'w': 43.3, 'desc': 'Severe Underweight (BMI 14.1)'},
    {'gender': 'Male',   'h': 185, 'w': 48.4, 'desc': 'Severe Underweight (BMI 14.1)'},
    
    # Mild/Moderate Underweight (BMI 16.0 - 18.4)
    {'gender': 'Female', 'h': 155, 'w': 41.0, 'desc': 'Underweight (BMI 17.1)'},
    {'gender': 'Male',   'h': 165, 'w': 46.0, 'desc': 'Underweight (BMI 16.9)'},
    {'gender': 'Female', 'h': 170, 'w': 50.0, 'desc': 'Underweight (BMI 17.3)'},
    {'gender': 'Male',   'h': 180, 'w': 56.0, 'desc': 'Underweight (BMI 17.3)'},

    # Normal Weight (BMI 18.5 - 24.9)
    {'gender': 'Female', 'h': 160, 'w': 54.0, 'desc': 'Normal (BMI 21.1)'},
    {'gender': 'Male',   'h': 175, 'w': 67.0, 'desc': 'Normal (BMI 21.9)'},
    {'gender': 'Female', 'h': 170, 'w': 63.0, 'desc': 'Normal (BMI 21.8)'},
    {'gender': 'Male',   'h': 185, 'w': 75.0, 'desc': 'Normal (BMI 21.9)'},

    # Overweight (BMI 25.0 - 29.9)
    {'gender': 'Female', 'h': 160, 'w': 70.0, 'desc': 'Overweight (BMI 27.3)'},
    {'gender': 'Male',   'h': 175, 'w': 83.0, 'desc': 'Overweight (BMI 27.1)'},

    # Obese (BMI 30.0 - 34.9)
    {'gender': 'Female', 'h': 160, 'w': 82.0, 'desc': 'Obese (BMI 32.0)'},
    {'gender': 'Male',   'h': 175, 'w': 98.0, 'desc': 'Obese (BMI 32.0)'},

    # Severe Obesity (BMI >= 35.0)
    {'gender': 'Female', 'h': 160, 'w': 100.0, 'desc': 'Severe Obesity (BMI 39.1)'},
    {'gender': 'Male',   'h': 175, 'w': 120.0, 'desc': 'Severe Obesity (BMI 39.2)'},
]

print(f"{'Profile Description':<32} | {'Height':<6} {'Weight':<6} | {'Calc BMI':<8} {'Standard Category':<18} | {'ML Model 1 Pred':<18} {'Conf':<6} | {'Status'}")
print("-" * 115)
for tc in test_cases:
    bmi_res = calculate_bmi(tc['h'], tc['w'])
    ml_res = predict_health_status(tc['gender'], tc['h'], tc['w'])
    calc_bmi = f"{bmi_res['bmi']:.2f}"
    std_cat = bmi_res['category']
    ml_pred = ml_res['predicted_label']
    conf = f"{ml_res['confidence']}%"
    
    # Check consistency
    matches = (std_cat == 'Normal weight' and ml_pred == 'Normal') or \
              (std_cat == 'Underweight' and ml_pred in ('Weak', 'Extremely Weak')) or \
              (std_cat == 'Overweight' and ml_pred == 'Overweight') or \
              ('Obese' in std_cat and ml_pred in ('Obesity', 'Extreme Obesity'))
    status_str = "MATCH" if matches else "DISCREPANCY"
    print(f"{tc['desc']:<32} | {tc['h']:<6} {tc['w']:<6} | {calc_bmi:<8} {std_cat:<18} | {ml_pred:<18} {conf:<6} | {status_str}")
