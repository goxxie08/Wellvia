import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Scale, AlertCircle, CheckCircle, ChevronDown, ChevronUp, History, Info } from 'lucide-react';

export function BodyMetricsPage() {
  const { user: authUser, refreshUser } = useAuth();
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [gender, setGender] = useState('Female');

  // Lifestyle parameters for Model 2
  const [includeLifestyle, setIncludeLifestyle] = useState(false);
  const [age, setAge] = useState(21);
  const [familyHistory, setFamilyHistory] = useState('no');
  const [favc, setFavc] = useState('no');
  const [fcvc, setFcvc] = useState(2.0);
  const [ncp, setNcp] = useState(3.0);
  const [caec, setCaec] = useState('Sometimes');
  const [smoke, setSmoke] = useState('no');
  const [ch2o, setCh2o] = useState(2.0);
  const [scc, setScc] = useState('no');
  const [faf, setFaf] = useState(1.0);
  const [tue, setTue] = useState(1.0);
  const [calc, setCalc] = useState('Sometimes');
  const [mtrans, setMtrans] = useState('Public_Transportation');

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [assessment, setAssessment] = useState(null);
  const [userData, setUserData] = useState(null);
  const [bmiHistory, setBmiHistory] = useState([]);

  const getStorageKey = () => `wellvia_lifestyle_${authUser?.id || 'default'}`;

  const loadSavedLifestyle = () => {
    try {
      const saved = localStorage.getItem(getStorageKey());
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.Age) setAge(parsed.Age);
        if (parsed.family_history_with_overweight) setFamilyHistory(parsed.family_history_with_overweight);
        if (parsed.FAVC) setFavc(parsed.FAVC);
        if (parsed.FCVC != null) setFcvc(parsed.FCVC);
        if (parsed.NCP != null) setNcp(parsed.NCP);
        if (parsed.CAEC) setCaec(parsed.CAEC);
        if (parsed.SMOKE) setSmoke(parsed.SMOKE);
        if (parsed.CH2O != null) setCh2o(parsed.CH2O);
        if (parsed.SCC) setScc(parsed.SCC);
        if (parsed.FAF != null) setFaf(parsed.FAF);
        if (parsed.TUE != null) setTue(parsed.TUE);
        if (parsed.CALC) setCalc(parsed.CALC);
        if (parsed.MTRANS) setMtrans(parsed.MTRANS);
        setIncludeLifestyle(true);
      }
    } catch (e) {
      console.warn('Could not parse saved lifestyle inputs', e);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await api.getBodyMetrics();
      if (res.success) {
        if (res.user) {
          setUserData(res.user);
          if (res.user.height) setHeight(res.user.height);
          if (res.user.weight) setWeight(res.user.weight);
          if (res.user.gender) setGender(res.user.gender);
          if (res.user.ml_lifestyle_risk) {
            loadSavedLifestyle();
          }
        }
        if (res.assessment) setAssessment(res.assessment);
        if (res.bmi_history) setBmiHistory(res.bmi_history);
      }
    } catch (err) {
      setError(err.message || 'Failed to load body metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [authUser?.id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const lifestylePayload = includeLifestyle ? {
        Age: parseFloat(age),
        family_history_with_overweight: familyHistory,
        FAVC: favc,
        FCVC: parseFloat(fcvc),
        NCP: parseFloat(ncp),
        CAEC: caec,
        SMOKE: smoke,
        CH2O: parseFloat(ch2o),
        SCC: scc,
        FAF: parseFloat(faf),
        TUE: parseFloat(tue),
        CALC: calc,
        MTRANS: mtrans
      } : null;

      const payload = {
        height: parseFloat(height),
        weight: parseFloat(weight),
        gender,
        include_lifestyle: includeLifestyle,
        lifestyle_payload: lifestylePayload
      };

      if (includeLifestyle && lifestylePayload) {
        try {
          localStorage.setItem(getStorageKey(), JSON.stringify(lifestylePayload));
        } catch (e) {
          console.warn('Could not cache lifestyle answers', e);
        }
      }

      const res = await api.saveBodyMetrics(payload);
      if (res.success) {
        setSuccess(res.message);
        if (res.assessment) setAssessment(res.assessment);
        if (res.user) setUserData(res.user);
        if (res.bmi_history) setBmiHistory(res.bmi_history);
        if (refreshUser) {
          await refreshUser();
        }
        await fetchData();
      }
    } catch (err) {
      setError(err.message || 'Failed to save body metrics.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 0' }}>
        <div className="spinner-border text-teal" style={{ width: '2.5rem', height: '2.5rem', color: 'var(--teal-primary)' }} />
        <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Loading body metrics & ML models...</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '980px', margin: '0 auto' }}>
      
      {/* Title */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Scale className="text-teal" size={30} style={{ color: 'var(--teal-primary)' }} />
          Body Metrics & ML Health Assessment
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Calculate your Body Mass Index (BMI) and evaluate physiological health status using Scikit-Learn Random Forest models.
        </p>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#fca5a5',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem 1rem',
          color: '#6ee7b7',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <CheckCircle size={18} />
          <span>{success}</span>
        </div>
      )}

      <div className="grid-2" style={{ alignItems: 'start' }}>
        
        {/* Form Card */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#fff', marginBottom: '1.25rem' }}>
            Enter Physical Measurements
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Biological Gender</label>
              <select
                className="form-select"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              >
                <option value="Female">Female</option>
                <option value="Male">Male</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Height (cm)</label>
                <input
                  type="number"
                  step="0.5"
                  min="50"
                  max="250"
                  className="form-input"
                  placeholder="e.g. 170"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Weight (kg)</label>
                <input
                  type="number"
                  step="0.5"
                  min="20"
                  max="300"
                  className="form-input"
                  placeholder="e.g. 65"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Collapsible ML Lifestyle Questionnaire */}
            <div style={{
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '1rem',
              margin: '1rem 0',
              background: 'rgba(15, 23, 42, 0.4)'
            }}>
              <div
                onClick={() => setIncludeLifestyle(!includeLifestyle)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#fff' }}>
                    Multi-Factor Lifestyle Risk Assessment (ML Model 2)
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Optional 16-parameter dietary and physical activity questionnaire
                  </div>
                </div>
                {includeLifestyle ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </div>

              {includeLifestyle && (
                <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Age</label>
                      <input type="number" min="14" max="80" className="form-input" value={age} onChange={(e) => setAge(e.target.value)} />
                    </div>
                    <div>
                      <label className="form-label">Family Overweight History</label>
                      <select className="form-select" value={familyHistory} onChange={(e) => setFamilyHistory(e.target.value)}>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Frequent High Caloric Food (FAVC)</label>
                      <select className="form-select" value={favc} onChange={(e) => setFavc(e.target.value)}>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Daily Water Consumption (Liters)</label>
                      <input type="number" step="0.5" min="1" max="5" className="form-input" value={ch2o} onChange={(e) => setCh2o(e.target.value)} />
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Vegetable Consumption (FCVC)</label>
                      <select className="form-select" value={fcvc} onChange={(e) => setFcvc(e.target.value)}>
                        <option value="1.0">Rarely / Never</option>
                        <option value="2.0">Sometimes</option>
                        <option value="3.0">Always / With Every Meal</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Daily Main Meals (NCP)</label>
                      <input type="number" min="1" max="4" step="1" className="form-input" value={ncp} onChange={(e) => setNcp(e.target.value)} />
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Food Between Meals (CAEC)</label>
                      <select className="form-select" value={caec} onChange={(e) => setCaec(e.target.value)}>
                        <option value="no">No snacking</option>
                        <option value="Sometimes">Sometimes</option>
                        <option value="Frequently">Frequently</option>
                        <option value="Always">Always</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Monitors Calories (SCC)</label>
                      <select className="form-select" value={scc} onChange={(e) => setScc(e.target.value)}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Physical Activity Frequency (FAF)</label>
                      <select className="form-select" value={faf} onChange={(e) => setFaf(e.target.value)}>
                        <option value="0.0">No activity</option>
                        <option value="1.0">1 to 2 days/week</option>
                        <option value="2.0">2 to 4 days/week</option>
                        <option value="3.0">4+ days/week</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Recreational Screen Time (TUE)</label>
                      <select className="form-select" value={tue} onChange={(e) => setTue(e.target.value)}>
                        <option value="0.0">0 to 2 hours (Low)</option>
                        <option value="1.0">3 to 5 hours (Medium)</option>
                        <option value="2.0">5+ hours (High)</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Smokes Tobacco (SMOKE)</label>
                      <select className="form-select" value={smoke} onChange={(e) => setSmoke(e.target.value)}>
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label">Alcohol Consumption (CALC)</label>
                      <select className="form-select" value={calc} onChange={(e) => setCalc(e.target.value)}>
                        <option value="no">Never / None</option>
                        <option value="Sometimes">Sometimes</option>
                        <option value="Frequently">Frequently</option>
                      </select>
                    </div>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.75rem' }}>
                    <div>
                      <label className="form-label">Primary Transportation (MTRANS)</label>
                      <select className="form-select" value={mtrans} onChange={(e) => setMtrans(e.target.value)}>
                        <option value="Public_Transportation">Public Transportation</option>
                        <option value="Walking">Walking</option>
                        <option value="Automobile">Automobile</option>
                        <option value="Motorbike">Motorbike</option>
                        <option value="Bike">Bicycle</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
              disabled={saving}
            >
              {saving ? 'Analyzing ML inferences...' : 'Calculate & Save Assessment'}
            </button>
          </form>
        </div>

        {/* Current Assessment Display */}
        <div>
          <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#fff', marginBottom: '1rem' }}>
              Integrated ML Assessment
            </h2>

            {assessment && (assessment.bmi != null || assessment.bmi_formatted) ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '2.75rem', fontWeight: 800, color: 'var(--teal-primary)', lineHeight: 1 }}>
                    {assessment.bmi_formatted || (typeof assessment.bmi === 'object' ? assessment.bmi?.bmi_formatted : Number(assessment.bmi).toFixed(2))}
                  </div>
                  <div>
                    <span className="badge badge-teal" style={{ fontSize: '0.85rem' }}>
                      {assessment.standard_category || assessment.category || (typeof assessment.bmi === 'object' ? assessment.bmi?.category : '') || userData?.bmi_category || 'Normal weight'}
                    </span>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      Prime Healthy Range: 18.5 – 24.9
                    </div>
                  </div>
                </div>

                {/* Standard Health Tip */}
                {(assessment.standard_tip || assessment.health_tip || (typeof assessment.bmi === 'object' ? assessment.bmi?.health_tip : null)) && (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1rem', fontStyle: 'italic' }}>
                    "{assessment.standard_tip || assessment.health_tip || assessment.bmi?.health_tip}"
                  </p>
                )}

                {/* ML Model 1 Health Classifier Box */}
                {(assessment.ml_status?.predicted_label || assessment.ml_health_status || userData?.ml_health_status) && (
                  <div style={{
                    background: 'rgba(20, 184, 166, 0.1)',
                    border: '1px solid rgba(20, 184, 166, 0.25)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.85rem',
                    marginBottom: '0.85rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--teal-primary)', fontWeight: 600 }}>
                        ML Model 1: Body Metrics Health Status
                      </div>
                      {assessment.ml_status?.confidence && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {assessment.ml_status.confidence}% confidence
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
                      {assessment.ml_status?.predicted_label || assessment.ml_health_status || userData?.ml_health_status}
                    </div>
                    {assessment.ml_status?.explanation && (
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {assessment.ml_status.explanation}
                      </div>
                    )}
                  </div>
                )}

                {/* ML Model 2 Lifestyle Risk Box */}
                {(assessment.ml_lifestyle?.predicted_label || assessment.ml_lifestyle_risk || userData?.ml_lifestyle_risk) && (
                  <div style={{
                    background: 'rgba(139, 92, 246, 0.1)',
                    border: '1px solid rgba(139, 92, 246, 0.25)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.85rem',
                    marginBottom: '0.85rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--purple-primary)', fontWeight: 600 }}>
                        ML Model 2: Multi-Factor Lifestyle Risk
                      </div>
                      {assessment.ml_lifestyle?.risk_level && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {assessment.ml_lifestyle.risk_level}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
                      {assessment.ml_lifestyle?.predicted_label || assessment.ml_lifestyle_risk || userData?.ml_lifestyle_risk}
                    </div>
                    {assessment.ml_lifestyle?.explanation && (
                      <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                        {assessment.ml_lifestyle.explanation}
                      </div>
                    )}
                  </div>
                )}

                {/* Suggestions / Personalized Action Plan */}
                {((assessment.ml_status?.suggestions && assessment.ml_status.suggestions.length > 0) ||
                  (assessment.personalized_plan?.daily_tips && assessment.personalized_plan.daily_tips.length > 0)) && (
                  <div style={{ marginTop: '1rem' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                      Personalized Habit Guidance:
                    </div>
                    <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                      {(assessment.ml_status?.suggestions || assessment.personalized_plan?.daily_tips || []).map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
                <Info size={32} style={{ margin: '0 auto 0.75rem auto', opacity: 0.5 }} />
                <p style={{ fontSize: '0.9rem' }}>Submit your height and weight to view your real-time BMI classification and ML prediction results.</p>
              </div>
            )}
          </div>

          {/* Historical Logs */}
          {bmiHistory.length > 0 && (
            <div className="glass-card">
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <History size={16} /> Recent BMI History
              </h3>
              <table className="data-table" style={{ marginTop: '0.5rem' }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Weight</th>
                    <th>BMI</th>
                    <th>Classification</th>
                  </tr>
                </thead>
                <tbody>
                  {bmiHistory.map((h, i) => (
                    <tr key={h.id || i}>
                      <td style={{ color: 'var(--text-muted)' }}>{String(h.recorded_at).slice(0, 10)}</td>
                      <td>{h.weight} kg</td>
                      <td style={{ fontWeight: 600 }}>{Number(h.bmi).toFixed(1)}</td>
                      <td>
                        <span className="badge badge-teal" style={{ fontSize: '0.7rem' }}>
                          {h.bmi_category}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
