/* Student Wellness Companion (Wellvia) - Chart.js Render Utilities */

function renderStudentCharts(chartData) {
    if (!chartData || !chartData.labels) return;

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'top' }
        },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true }
        }
    };

    // 1. Sleep & Study Hours Bar Chart
    const ctxSleep = document.getElementById('chartSleepStudy');
    if (ctxSleep) {
        new Chart(ctxSleep, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Sleep Hours',
                        data: chartData.sleep,
                        backgroundColor: '#0d9488',
                        borderRadius: 6
                    },
                    {
                        label: 'Study Hours',
                        data: chartData.study,
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }
                ]
            },
            options: commonOptions
        });
    }

    // 2. Mood vs Stress Line Chart
    const ctxMoodStress = document.getElementById('chartMoodStress');
    if (ctxMoodStress) {
        new Chart(ctxMoodStress, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Mood (1-5)',
                        data: chartData.mood,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Stress Level (1-5)',
                        data: chartData.stress,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: { min: 1, max: 5, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    // 3. Wellness Score Trend Line Chart
    const ctxScore = document.getElementById('chartWellnessScore');
    if (ctxScore) {
        new Chart(ctxScore, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Wellness Score',
                    data: chartData.score,
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: { min: 0, max: 100 }
                }
            }
        });
    }

    // 4. Habit Completion Doughnut Chart
    const ctxDonut = document.getElementById('chartHabitCompletion');
    if (ctxDonut && chartData.habit_completion) {
        new Chart(ctxDonut, {
            type: 'doughnut',
            data: {
                labels: chartData.habit_completion.labels,
                datasets: [{
                    data: chartData.habit_completion.counts,
                    backgroundColor: [
                        '#0d9488', '#0284c7', '#6366f1',
                        '#10b981', '#f59e0b', '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' }
                }
            }
        });
    }

    // 5. BMI & Weight Longitudinal Trend Chart
    const ctxBmiWeight = document.getElementById('chartBmiWeight');
    if (ctxBmiWeight && chartData.bmi_history && chartData.bmi_history.labels && chartData.bmi_history.labels.length > 0) {
        new Chart(ctxBmiWeight, {
            type: 'line',
            data: {
                labels: chartData.bmi_history.labels,
                datasets: [
                    {
                        label: 'BMI',
                        data: chartData.bmi_history.bmi,
                        borderColor: '#0d9488',
                        backgroundColor: 'rgba(13, 148, 136, 0.15)',
                        borderWidth: 3,
                        tension: 0.3,
                        yAxisID: 'yBMI',
                        pointRadius: 5,
                        pointBackgroundColor: '#0d9488',
                        pointHoverRadius: 7
                    },
                    {
                        label: 'Weight (kg)',
                        data: chartData.bmi_history.weight,
                        borderColor: '#6366f1',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'yWeight',
                        pointRadius: 4,
                        pointBackgroundColor: '#6366f1',
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            afterBody: function(tooltipItems) {
                                const idx = tooltipItems[0].dataIndex;
                                const category = chartData.bmi_history.categories ? chartData.bmi_history.categories[idx] : '';
                                const status = chartData.bmi_history.ml_status ? chartData.bmi_history.ml_status[idx] : '';
                                let extra = '';
                                if (category) extra += `Standard: ${category}\n`;
                                if (status) extra += `ML Status: ${status}`;
                                return extra;
                            }
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    yBMI: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'BMI' },
                        suggestedMin: 16,
                        suggestedMax: 32
                    },
                    yWeight: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Weight (kg)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }
}

function renderAdminCharts(analytics) {
    if (!analytics) return;

    // Mood Distribution Pie
    const ctxMood = document.getElementById('adminMoodChart');
    if (ctxMood) {
        new Chart(ctxMood, {
            type: 'pie',
            data: {
                labels: ['Very Happy', 'Happy', 'Neutral', 'Sad', 'Very Sad'],
                datasets: [{
                    data: analytics.mood_dist,
                    backgroundColor: ['#10b981', '#34d399', '#f59e0b', '#f97316', '#ef4444']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Stress Distribution Pie
    const ctxStress = document.getElementById('adminStressChart');
    if (ctxStress) {
        new Chart(ctxStress, {
            type: 'pie',
            data: {
                labels: ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
                datasets: [{
                    data: analytics.stress_dist,
                    backgroundColor: ['#10b981', '#60a5fa', '#f59e0b', '#f97316', '#ef4444']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // Sleep Trend Line
    const ctxSleepTrend = document.getElementById('adminSleepTrendChart');
    if (ctxSleepTrend) {
        new Chart(ctxSleepTrend, {
            type: 'line',
            data: {
                labels: analytics.trend_dates,
                datasets: [{
                    label: 'Avg Sleep Duration (Hours)',
                    data: analytics.trend_sleep,
                    borderColor: '#0d9488',
                    backgroundColor: 'rgba(13, 148, 136, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

/**
 * Renders the 6 dedicated bar charts for the redesigned Progress page
 */
function renderStudentBarCharts(chartData) {
    if (!chartData || !chartData.labels) return;

    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true }
        }
    };

    // 1. Sleep Bar Chart
    const elSleep = document.getElementById('chartSleepBar');
    if (elSleep) {
        new Chart(elSleep, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Sleep Hours',
                    data: chartData.sleep || [],
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: { suggestedMax: 10, ticks: { callback: v => v + 'h' } }
                }
            }
        });
    }

    // 2. Water Bar Chart
    const elWater = document.getElementById('chartWaterBar');
    if (elWater) {
        new Chart(elWater, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Water Glasses',
                    data: chartData.water || [],
                    backgroundColor: 'rgba(14, 165, 233, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: { suggestedMax: 10, ticks: { callback: v => v + ' gl' } }
                }
            }
        });
    }

    // 3. Exercise Bar Chart
    const elEx = document.getElementById('chartExerciseBar');
    if (elEx) {
        new Chart(elEx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Exercise (Minutes)',
                    data: chartData.exercise || [],
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: { suggestedMax: 60, ticks: { callback: v => v + 'm' } }
                }
            }
        });
    }

    // 4. Study Bar Chart
    const elStudy = document.getElementById('chartStudyBar');
    if (elStudy) {
        new Chart(elStudy, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Study Hours',
                    data: chartData.study || [],
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: { suggestedMax: 8, ticks: { callback: v => v + 'h' } }
                }
            }
        });
    }

    // 5. Stress Level Bar Chart
    const elStress = document.getElementById('chartStressBar');
    if (elStress) {
        new Chart(elStress, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Stress Rating (1-5)',
                    data: chartData.stress || [],
                    backgroundColor: 'rgba(244, 63, 94, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: { min: 1, max: 5, ticks: { stepSize: 1 } }
                }
            }
        });
    }

    // 6. Mood Categorical Bar Chart
    const elMood = document.getElementById('chartMoodBar');
    if (elMood) {
        new Chart(elMood, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Mood Category',
                    data: chartData.mood || [],
                    backgroundColor: 'rgba(20, 184, 166, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                ...baseOptions,
                scales: {
                    ...baseOptions.scales,
                    y: {
                        min: 1,
                        max: 5,
                        ticks: {
                            stepSize: 1,
                            callback: v => {
                                const map = { 1: 'Sad 😞', 2: 'Low 🙁', 3: 'Neutral 😐', 4: 'Good 🙂', 5: 'Great 😊' };
                                return map[v] || v;
                            }
                        }
                    }
                }
            }
        });
    }
}

