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
