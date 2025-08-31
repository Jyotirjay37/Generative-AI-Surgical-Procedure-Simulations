// Dashboard specific functionality
class Dashboard {
    constructor() {
        this.charts = {};
        this.init();
    }
    
    init() {
        this.loadRecentActivity();
        this.updatePerformanceMetrics();
    }
    
    async loadRecentActivity() {
        // Load recent simulation activity
        try {
            const response = await fetch('/api/recent-activity');
            const activities = await response.json();
            this.renderRecentActivity(activities);
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }
    
    renderRecentActivity(activities) {
        const container = document.getElementById('recent-simulations');
        if (!container || !activities.length) return;
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-${activity.status === 'completed' ? 'check-circle' : 'clock'}"></i>
                </div>
                <div class="activity-details">
                    <h4>${activity.procedure_name}</h4>
                    <p>${activity.status} • Score: ${activity.score}% • ${activity.time_ago}</p>
                </div>
            </div>
        `).join('');
    }
    
    updatePerformanceMetrics() {
        // Update dashboard performance metrics
        const metrics = {
            avgScore: 82.5,
            completedSims: 15,
            totalTime: 24
        };
        
        document.getElementById('avg-score').textContent = `${metrics.avgScore}%`;
        document.getElementById('completed-sims').textContent = metrics.completedSims;
        document.getElementById('total-time').textContent = `${metrics.totalTime}h`;
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dashboard')) {
        new Dashboard();
    }
});