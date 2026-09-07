import pytest
from app.utils.bmi import calculate_bmi

def test_calculate_bmi_normal():
    # 175 cm, 70 kg -> BMI = 70 / (1.75^2) = 22.86 -> 22.9
    res = calculate_bmi(175, 70)
    assert res is not None
    assert res['bmi'] == 22.9
    assert res['category'] == "Normal weight"
    assert res['color'] == "success"

def test_calculate_bmi_underweight():
    # 180 cm, 55 kg -> BMI = 55 / (1.8^2) = 16.98 -> 17.0
    res = calculate_bmi(180, 55)
    assert res is not None
    assert res['bmi'] == 17.0
    assert res['category'] == "Underweight"
    assert res['color'] == "info"

def test_calculate_bmi_overweight():
    # 170 cm, 78 kg -> BMI = 78 / (1.7^2) = 26.98 -> 27.0
    res = calculate_bmi(170, 78)
    assert res is not None
    assert res['bmi'] == 27.0
    assert res['category'] == "Overweight"
    assert res['color'] == "warning"

def test_calculate_bmi_obese():
    # 165 cm, 90 kg -> BMI = 90 / (1.65^2) = 33.05 -> 33.1
    res = calculate_bmi(165, 90)
    assert res is not None
    assert res['bmi'] == 33.1
    assert res['category'] == "Obese"
    assert res['color'] == "danger"

def test_calculate_bmi_invalid_input():
    assert calculate_bmi(0, 70) is None
    assert calculate_bmi(170, -5) is None
    assert calculate_bmi("invalid", 70) is None
    assert calculate_bmi(None, None) is None
