// Main JavaScript for Surgical Simulation Platform

class SurgicalSimulationPlatform {
    constructor() {
        this.currentSection = 'dashboard';
        this.apiBase = '/api';
        this.currentSimulation = null;
        this.procedures = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadProcedures();
        this.loadUserStatistics();
        this.initializeCharts();
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('href').replace('#', '');
                this.showSection(section);
            });
        });
        
        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
        
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
        
        // Procedure selection change
        const procedureSelect = document.getElementById('procedure-select');
        if (procedureSelect) {
            procedureSelect.addEventListener('change', this.onProcedureChange.bind(this));
        }
    }
    
    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeLink = document.querySelector(`[href="#${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // Load section-specific data
        this.loadSectionData(sectionName);
    }
    
    loadSectionData(sectionName) {
        switch (sectionName) {
            case 'procedures':
                this.refreshProcedures();
                break;
            case 'statistics':
                this.loadStatistics();
                break;
        }
    }
    
    async loadProcedures() {
        try {
            const response = await fetch(`${this.apiBase}/procedures`);
            this.procedures = await response.json();
            this.renderProcedures();
            this.populateProcedureSelect();
        } catch (error) {
            console.error('Error loading procedures:', error);
            this.showAlert('Error loading procedures', 'danger');
        }
    }
    
    renderProcedures() {
        const container = document.getElementById('procedures-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.procedures.forEach(procedure => {
            const procedureCard = this.createProcedureCard(procedure);
            container.appendChild(procedureCard);
        });
    }
    
    createProcedureCard(procedure) {
        const card = document.createElement('div');
        card.className = 'card procedure-card';
        card.onclick = () => this.selectProcedure(procedure);
        
        card.innerHTML = `
            <div class="procedure-header">
                <h3>${procedure.name}</h3>
                <div class="procedure-category">${procedure.category}</div>
            </div>
            <div class="procedure-content">
                <div class="procedure-details">
                    <div class="detail-row">
                        <span class="label">Duration:</span>
                        <span class="value">${procedure.duration}</span>
                    </div>
                </div>
                <div class="difficulty-badges">
                    ${procedure.difficulty.map(level => 
                        `<span class="difficulty-badge ${level}">${level}</span>`
                    ).join('')}
                </div>
                <button class="btn btn-primary" onclick="event.stopPropagation(); selectProcedureForSimulation('${procedure.id}')">
                    <i class="fas fa-play"></i> Start Simulation
                </button>
            </div>
        `;
        
        return card;
    }
    
    populateProcedureSelect() {
        const select = document.getElementById('procedure-select');
        if (!select) return;
        
        select.innerHTML = '<option value="">Select a procedure...</option>';
        
        this.procedures.forEach(procedure => {
            const option = document.createElement('option');
            option.value = procedure.id;
            option.textContent = procedure.name;
            select.appendChild(option);
        });
    }
    
    onProcedureChange() {
        const select = document.getElementById('procedure-select');
        const selectedProcedure = this.procedures.find(p => p.id === select.value);
        
        if (selectedProcedure) {
            this.updateLearningObjectives(selectedProcedure);
            this.updateDifficultyOptions(selectedProcedure);
        }
    }
    
    updateLearningObjectives(procedure) {
        const container = document.getElementById('learning-objectives');
        if (!container) return;
        
        const objectives = this.getProcedureObjectives(procedure.id);
        
        container.innerHTML = '';
        objectives.forEach(objective => {
            const item = document.createElement('div');
            item.className = 'objective-item';
            item.innerHTML = `
                <input type="checkbox" id="obj-${objective.id}" value="${objective.id}">
                <label for="obj-${objective.id}">${objective.name}</label>
            `;
            container.appendChild(item);
        });
    }
    
    getProcedureObjectives(procedureId) {
        const objectiveMap = {
            'laparoscopic_cholecystectomy': [
                {id: 'trocar_placement', name: 'Trocar Placement'},
                {id: 'critical_view', name: 'Critical View of Safety'},
                {id: 'dissection', name: 'Gallbladder Dissection'},
                {id: 'hemostasis', name: 'Hemostasis Control'}
            ],
            'appendectomy': [
                {id: 'identification', name: 'Appendix Identification'},
                {id: 'mesoappendix', name: 'Mesoappendix Division'},
                {id: 'base_division', name: 'Base Division'}
            ],
            'knee_arthroscopy': [
                {id: 'portal_placement', name: 'Portal Placement'},
                {id: 'diagnostic_scope', name: 'Diagnostic Arthroscopy'},
                {id: 'meniscal_repair', name: 'Meniscal Repair'}
            ]
        };
        
        return objectiveMap[procedureId] || [];
    }
    
    updateDifficultyOptions(procedure) {
        const select = document.getElementById('difficulty-select');
        if (!select) return;
        
        select.innerHTML = '';
        procedure.difficulty.forEach(level => {
            const option = document.createElement('option');
            option.value = level;
            option.textContent = level.charAt(0).toUpperCase() + level.slice(1);
            select.appendChild(option);
        });
    }
    
    async startSimulation() {
        console.log('startSimulation called');
        const config = this.getSimulationConfig();
        console.log('Config:', config);
        
        if (!this.validateConfig(config)) {
            this.showAlert('Please complete all required fields', 'warning');
            return;
        }
        
        this.showLoading('Generating simulation...');
        
        try {
            console.log('Sending request to:', `${this.apiBase}/generate-simulation`);
            const response = await fetch(`${this.apiBase}/generate-simulation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Response result:', result);
            
            if (result.status === 'success') {
                this.currentSimulation = result;
                this.hideLoading();
                this.closeModal('procedure-modal');
                
                // Redirect to simulation page
                window.location.href = `/simulation?id=${result.simulation_id}`;
            } else {
                throw new Error(result.error || 'Failed to generate simulation');
            }
            
        } catch (error) {
            console.error('Error in startSimulation:', error);
            this.hideLoading();
            this.showAlert(`Error generating simulation: ${error.message}`, 'danger');
        }
    }
    
    getSimulationConfig() {
        const procedureSelect = document.getElementById('procedure-select');
        const difficultySelect = document.getElementById('difficulty-select');
        const genderSelect = document.getElementById('gender-select');
        const ageMin = document.getElementById('age-min');
        const ageMax = document.getElementById('age-max');
        const complicationsEnabled = document.getElementById('complications-enabled');
        const realTimeFeedback = document.getElementById('real-time-feedback');
        const timePressure = document.getElementById('time-pressure');
        
        // Get selected learning objectives
        const objectiveCheckboxes = document.querySelectorAll('#learning-objectives input[type="checkbox"]:checked');
        const learningObjectives = Array.from(objectiveCheckboxes).map(cb => cb.value);
        
        return {
            procedure_type: procedureSelect.value,
            difficulty_level: difficultySelect.value,
            gender: genderSelect.value,
            age_range: [parseInt(ageMin.value), parseInt(ageMax.value)],
            learning_objectives: learningObjectives,
            complications_enabled: complicationsEnabled.checked,
            real_time_feedback: realTimeFeedback.checked,
            time_pressure: timePressure.checked
        };
    }
    
    validateConfig(config) {
        if (!config.procedure_type) {
            this.showAlert('Please select a procedure', 'warning');
            return false;
        }
        
        if (!config.difficulty_level) {
            this.showAlert('Please select a difficulty level', 'warning');
            return false;
        }
        
        if (config.age_range[0] >= config.age_range[1]) {
            this.showAlert('Invalid age range', 'warning');
            return false;
        }
        
        return true;
    }
    
    async loadUserStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/user-statistics`);
            const stats = await response.json();
            this.updateDashboardStats(stats);
        } catch (error) {
            console.error('Error loading user statistics:', error);
        }
    }
    
    updateDashboardStats(stats) {
        // Update average score
        const avgScoreElement = document.getElementById('avg-score');
        if (avgScoreElement && stats.overall_average) {
            avgScoreElement.textContent = `${stats.overall_average}%`;
        }
        
        // Update completed simulations
        const completedElement = document.getElementById('completed-sims');
        if (completedElement && stats.total_simulations) {
            completedElement.textContent = stats.total_simulations;
        }
        
        // Update total time (mock calculation for now)
        const totalTimeElement = document.getElementById('total-time');
        if (totalTimeElement) {
            const estimatedHours = Math.round(stats.total_simulations * 1.2);
            totalTimeElement.textContent = `${estimatedHours}h`;
        }
    }
    
    initializeCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performance-chart');
        if (performanceCtx && typeof Chart !== 'undefined') {
            new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Performance Score',
                        data: [65, 72, 78, 85],
                        borderColor: 'rgb(37, 99, 235)',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 4,
                            hoverRadius: 6
                        },
                        line: {
                            borderWidth: 3
                        }
                    }
                }
            });
        }
    }
    
    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBase}/user-statistics`);
            const stats = await response.json();
            this.renderStatisticsCharts(stats);
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }
    
    renderStatisticsCharts(stats) {
        // Score Distribution Chart
        const scoreCtx = document.getElementById('score-distribution-chart');
        if (scoreCtx && typeof Chart !== 'undefined') {
            new Chart(scoreCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Excellent (90+)', 'Good (75-89)', 'Fair (60-74)', 'Poor (<60)'],
                    datasets: [{
                        data: [30, 45, 20, 5],
                        backgroundColor: [
                            'rgb(16, 185, 129)',
                            'rgb(37, 99, 235)', 
                            'rgb(245, 158, 11)',
                            'rgb(220, 38, 38)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
        
        // Procedure Mastery Chart
        const masteryCtx = document.getElementById('procedure-mastery-chart');
        if (masteryCtx && typeof Chart !== 'undefined') {
            new Chart(masteryCtx, {
                type: 'radar',
                data: {
                    labels: ['Cholecystectomy', 'Appendectomy', 'Arthroscopy', 'Hernia Repair'],
                    datasets: [{
                        label: 'Mastery Level',
                        data: [85, 70, 60, 40],
                        backgroundColor: 'rgba(37, 99, 235, 0.2)',
                        borderColor: 'rgb(37, 99, 235)',
                        pointBackgroundColor: 'rgb(37, 99, 235)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }
    
    // Modal Management
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('show');
            modal.style.display = 'none';
        });
        document.body.style.overflow = '';
    }
    
    // Loading Management
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            const messageElement = overlay.querySelector('p');
            if (messageElement) {
                messageElement.textContent = message;
            }
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    // Alert Management
    showAlert(message, type = 'info', duration = 5000) {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) {
            // Create temporary alert if no container
            console.log(`${type.toUpperCase()}: ${message}`);
            return;
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${this.getAlertIcon(type)}"></i>
            ${message}
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, duration);
    }
    
    getAlertIcon(type) {
        const iconMap = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'danger': 'times-circle'
        };
        return iconMap[type] || 'info-circle';
    }
    
    // Utility Methods
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Global Functions (called from HTML)
let platform;

document.addEventListener('DOMContentLoaded', () => {
    platform = new SurgicalSimulationPlatform();
});

function showProcedureSelection() {
    platform.showModal('procedure-modal');
}

function closeProcedureModal() {
    platform.closeModal('procedure-modal');
}

function selectProcedureForSimulation(procedureId) {
    const select = document.getElementById('procedure-select');
    if (select) {
        select.value = procedureId;
        platform.onProcedureChange();
    }
    showProcedureSelection();
}

function startSimulation() {
    platform.startSimulation();
}

function refreshProcedures() {
    platform.loadProcedures();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SurgicalSimulationPlatform;
}