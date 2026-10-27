import pytest
from app import create_app
from app.models.db import execute_query
from app.services.ml_service import (
    get_model_1, get_model_2, predict_health_status, predict_lifestyle_risk, DISCLAIMER_TEXT
)
from app.utils.bmi import calculate_bmi, get_integrated_health_assessment

@pytest.fixture
def app_instance():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()

@pytest.fixture
def student_auth_session(client):
    """Log in as existing or test student user."""
    with client.session_transaction() as sess:
        sess['user_id'] = 14  # Kelly from seed/existing DB
        sess['username'] = 'Kelly'
        sess['role'] = 'student'
    return client

def test_models_exist_and_load():
    m1 = get_model_1()
    assert m1 is not None
    m2 = get_model_2()
    assert m2 is not None

def test_model_1_predictions_across_categories():
    # Test typical normal weight (Female, 174cm, 65kg)
    res_normal = predict_health_status('Female', 174, 65)
    assert res_normal['success'] is True
    assert res_normal['predicted_label'] == 'Normal'
    assert 'disclaimer' in res_normal
    assert len(res_normal['suggestions']) > 0

    # Test extreme obesity
    res_heavy = predict_health_status('Male', 165, 140)
    assert res_heavy['success'] is True
    assert res_heavy['predicted_label'] in ['Obesity', 'Extreme Obesity']

    # Test very weak
    res_light = predict_health_status('Female', 175, 45)
    assert res_light['success'] is True
    assert res_light['predicted_label'] in ['Extremely Weak', 'Weak']

def test_model_2_prediction_with_lifestyle():
    lifestyle_payload = {
        'Gender': 'Female',
        'Age': 21.0,
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
    res = predict_lifestyle_risk(lifestyle_payload)
    assert res['success'] is True
    assert res['predicted_class'] == 'Normal_Weight'
    assert 'Optimal' in res['predicted_label'] or 'Normal' in res['predicted_label']
    assert len(res['suggestions']) > 0
    assert len(res['protective_factors']) > 0
    assert 'risk_factors' in res

def test_personalized_action_plan_generation():
    from app.services.ml_service import get_personalized_action_plan
    plan_normal = get_personalized_action_plan("Normal weight", "Normal")
    assert plan_normal['theme'] is not None
    assert len(plan_normal['recommended_challenges']) > 0

    plan_over = get_personalized_action_plan("Overweight", "Overweight")
    assert "Active" in plan_over['theme'] or "Movement" in plan_over['theme']

def test_progress_chart_data_includes_bmi(app_instance, student_auth_session):
    from app.services.analytics import get_student_analytics_data
    with app_instance.app_context():
        chart_data, insights = get_student_analytics_data(user_id=14, days=7)
        assert 'bmi_history' in chart_data
        assert 'labels' in chart_data['bmi_history']
        assert 'bmi' in chart_data['bmi_history']
        assert 'weight' in chart_data['bmi_history']

def test_api_bmi_assess_valid(student_auth_session):
    resp = student_auth_session.post('/api/bmi/assess', json={
        'height': 174,
        'weight': 65,
        'gender': 'Female'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['bmi'] == 21.47
    assert data['standard_category'] == 'Normal weight'
    assert data['ml_status']['success'] is True
    assert data['ml_status']['predicted_label'] == 'Normal'
    assert 'Disclaimer' in data['disclaimer']

def test_api_bmi_assess_with_lifestyle(student_auth_session):
    resp = student_auth_session.post('/api/bmi/assess', json={
        'height': 170,
        'weight': 65,
        'gender': 'Female',
        'lifestyle': {
            'Gender': 'Female',
            'Age': 20,
            'Height': 170,
            'Weight': 65,
            'family_history_with_overweight': 'no',
            'FAVC': 'no',
            'FCVC': 2.0,
            'NCP': 3.0,
            'CAEC': 'Sometimes',
            'SMOKE': 'no',
            'CH2O': 2.0,
            'SCC': 'no',
            'FAF': 2.0,
            'TUE': 1.0,
            'CALC': 'no',
            'MTRANS': 'Walking'
        }
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['ml_lifestyle'] is not None
    assert data['ml_lifestyle']['success'] is True

def test_api_bmi_assess_invalid_input(student_auth_session):
    resp_invalid_str = student_auth_session.post('/api/bmi/assess', json={
        'height': 'invalid_text',
        'weight': 70
    })
    assert resp_invalid_str.status_code == 400
    data = resp_invalid_str.get_json()
    assert data['success'] is False

    resp_out_of_bounds = student_auth_session.post('/api/bmi/assess', json={
        'height': 5,
        'weight': 70
    })
    assert resp_out_of_bounds.status_code == 400

    resp_empty = student_auth_session.post('/api/bmi/assess', data="not json", content_type="text/plain")
    assert resp_empty.status_code == 400

def test_body_metrics_get_page(student_auth_session):
    resp = student_auth_session.get('/body-metrics?legacy=1')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Body Metrics & ML Health Assessment" in html
    assert "Mathematical BMI" in html
    assert "ML Health-Status Prediction" in html
    assert "Non-Medical Screening Notice" in html

def test_body_metrics_post_and_history_persistence(app_instance, student_auth_session):
    resp = student_auth_session.post('/body-metrics?legacy=1', data={
        'height': '174.0',
        'weight': '65.0',
        'gender': 'Female'
    }, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Body metrics saved!" in html
    assert "21.47" in html or "Normal" in html

    # Verify database was updated within app context
    with app_instance.app_context():
        user = execute_query("SELECT height, weight, gender, bmi, bmi_category, ml_health_status FROM users WHERE id = %s", (14,), fetchone=True)
        assert user['height'] == 174.0
        assert user['weight'] == 65.0
        assert user['gender'] == 'Female'
        assert user['bmi'] is not None
        assert user['ml_health_status'] is not None

        # Verify history entry was written
        history = execute_query("SELECT * FROM bmi_history WHERE user_id = %s ORDER BY id DESC LIMIT 1", (14,), fetchone=True)
        assert history is not None
        assert history['user_id'] == 14
        assert history['height'] == 174.0
        assert history['weight'] == 65.0

def test_dashboard_renders_bmi_and_history(student_auth_session):
    resp = student_auth_session.get('/dashboard?legacy=1')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Body Metrics & ML" in html
    assert "⚖️" in html
