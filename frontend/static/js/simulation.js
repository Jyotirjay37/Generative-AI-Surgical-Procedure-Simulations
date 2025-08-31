// Simulation Interface JavaScript

class SimulationInterface {
    constructor() {
        this.simulationId = null;
        this.currentStep = 1;
        this.totalSteps = 6;
        this.startTime = null;
        this.stepStartTime = null;
        this.selectedInstrument = null;
        this.vitalsUpdateInterval = null;
        this.timerInterval = null;
        this.simulationData = null;
        this.userActions = [];
        
        this.init();
    }
    
    init() {
        this.simulationId = this.getSimulationIdFromUrl();
        if (!this.simulationId) {
            this.redirectToDashboard();
            return;
        }
        
        this.setupEventListeners();
        this.loadSimulation();
        this.startTimer();
        this.startVitalsMonitoring();
        this.initializeSurgicalCanvas();
    }
    
    getSimulationIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id');
    }
    
    setupEventListeners() {
        // Instrument selection
        document.querySelectorAll('.instrument-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectInstrument(item.dataset.instrument);
            });
        });
        
        // Anatomical structure selection
        document.querySelectorAll('.hotspot').forEach(hotspot => {
            hotspot.addEventListener('click', (e) => {
                const structure = e.currentTarget.onclick.toString().match(/'([^']+)'/)?.[1];
                if (structure) {
                    this.selectAnatomicalStructure(structure);
                }
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Window beforeunload warning
        window.addEventListener('beforeunload', (e) => {
            if (this.simulationData) {
                e.preventDefault();
                e.returnValue = 'Are you sure you want to leave? Simulation progress will be lost.';
            }
        });
    }
    
    async loadSimulation() {
        try {
            console.log('Loading simulation with ID:', this.simulationId);
            const response = await fetch(`/api/simulation/${this.simulationId}`);
            const data = await response.json();
            
            console.log('Simulation data received:', data);
            
            if (data.status === 'success') {
                this.simulationData = data.simulation; // Fix: access the simulation property
                
                // Validate simulation data structure
                if (!this.simulationData) {
                    throw new Error('Simulation data is null or undefined');
                }
                
                if (!this.simulationData.procedure_info) {
                    throw new Error('Procedure information is missing');
                }
                
                if (!this.simulationData.steps || !Array.isArray(this.simulationData.steps)) {
                    throw new Error('Simulation steps are missing or invalid');
                }
                
                if (!this.simulationData.patient) {
                    throw new Error('Patient data is missing');
                }
                
                console.log('Simulation data validated successfully');
                this.updateSimulationInterface();
                this.loadCurrentStep();
                this.showAlert('Simulation loaded successfully', 'success', 10000);
            } else {
                throw new Error(data.error || 'Failed to load simulation');
            }
            
        } catch (error) {
            console.error('Error loading simulation:', error);
            this.showAlert('Failed to load simulation: ' + error.message, 'danger');
            setTimeout(() => this.redirectToDashboard(), 5000); // Increased timeout
        }
    }
    
    updateSimulationInterface() {
        const data = this.simulationData;
        
        console.log('Updating simulation interface with data:', data);
        
        // Update procedure title
        const titleElement = document.getElementById('procedure-title');
        if (titleElement && data.procedure_info && data.procedure_info.name) {
            titleElement.textContent = data.procedure_info.name;
        } else {
            console.error('Procedure info not found:', data.procedure_info);
            titleElement.textContent = 'Unknown Procedure';
        }
        
        // Update total steps
        const totalStepsElement = document.getElementById('total-steps');
        if (totalStepsElement && data.steps) {
            this.totalSteps = data.steps.length;
            totalStepsElement.textContent = this.totalSteps;
        } else {
            console.error('Steps not found:', data.steps);
            this.totalSteps = 0;
            totalStepsElement.textContent = '0';
        }
        
        // Update patient information
        if (data.patient) {
            this.updatePatientInfo(data.patient);
        } else {
            console.error('Patient data not found:', data.patient);
        }
        
        // Update progress tracking
        if (data.steps) {
            this.updateProgressTracking(data.steps);
        } else {
            console.error('Steps data not found for progress tracking');
        }
    }
    
    updatePatientInfo(patient) {
        if (!patient) {
            console.error('Patient data is null or undefined');
            return;
        }
        
        const elements = {
            'patient-age': patient.demographics?.age || 'N/A',
            'patient-gender': patient.demographics?.gender || 'N/A',
            'patient-bmi': patient.demographics?.bmi ? patient.demographics.bmi.toFixed(1) : 'N/A',
            'patient-history': patient.medical_history?.join(', ') || 'None'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Update initial vitals
        if (patient.vitals) {
            this.updateVitals(patient.vitals);
        } else {
            console.error('Patient vitals not found');
        }
    }
    
    updateProgressTracking(steps) {
        const container = document.getElementById('steps-progress');
        if (!container) return;
        
        container.innerHTML = '';
        
        steps.forEach((step, index) => {
            const stepNumber = index + 1;
            const stepElement = this.createStepElement(step, stepNumber);
            container.appendChild(stepElement);
        });
    }
    
    createStepElement(step, stepNumber) {
        const stepDiv = document.createElement('div');
        const isCompleted = stepNumber < this.currentStep;
        const isActive = stepNumber === this.currentStep;
        
        stepDiv.className = `step-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`;
        stepDiv.innerHTML = `
            <div class="step-number">${stepNumber}</div>
            <div class="step-info">
                <div class="step-name">${step.title}</div>
                <div class="step-status">${isCompleted ? 'Completed' : isActive ? 'In Progress' : 'Pending'}</div>
            </div>
            <div class="step-score">${isCompleted ? '85%' : '--'}</div>
        `;
        
        return stepDiv;
    }
    
    loadCurrentStep() {
        if (!this.simulationData) {
            console.error('Simulation data not available');
            return;
        }
        
        const steps = this.simulationData.steps;
        if (!steps || !Array.isArray(steps)) {
            console.error('Steps data not available or not an array:', steps);
            return;
        }
        
        const currentStepData = steps[this.currentStep - 1];
        
        if (!currentStepData) {
            console.log('No more steps, completing simulation');
            this.completeSimulation();
            return;
        }
        
        // Update step information
        this.updateStepInfo(currentStepData);
        
        // Update current step indicator
        const currentStepElement = document.getElementById('current-step');
        if (currentStepElement) {
            currentStepElement.textContent = `Step ${this.currentStep}`;
        }
        
        // Start step timer
        this.stepStartTime = Date.now();
        
        // Update available instruments
        this.updateAvailableInstruments(currentStepData.instruments || []);
    }
    
    updateStepInfo(stepData) {
        // Update step title
        const titleElement = document.getElementById('step-title');
        if (titleElement) {
            titleElement.textContent = stepData.title;
        }
        
        // Update step description
        const descElement = document.getElementById('step-description');
        if (descElement) {
            descElement.textContent = stepData.description;
        }
        
        // Update critical points
        const criticalPointsElement = document.getElementById('critical-points');
        if (criticalPointsElement && stepData.critical_points) {
            criticalPointsElement.innerHTML = `
                <h4>Critical Points:</h4>
                <ul>
                    ${stepData.critical_points.map(point => `<li>${point}</li>`).join('')}
                </ul>
            `;
        }
    }
    
    updateAvailableInstruments(availableInstruments) {
        document.querySelectorAll('.instrument-item').forEach(item => {
            const instrument = item.dataset.instrument;
            if (availableInstruments.length === 0 || availableInstruments.includes(instrument)) {
                item.classList.remove('disabled');
            } else {
                item.classList.add('disabled');
            }
        });
    }
    
    selectInstrument(instrumentName) {
        // Remove previous selection
        document.querySelectorAll('.instrument-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add selection to clicked instrument
        const selectedItem = document.querySelector(`[data-instrument="${instrumentName}"]`);
        if (selectedItem && !selectedItem.classList.contains('disabled')) {
            selectedItem.classList.add('selected');
            this.selectedInstrument = instrumentName;
            
            // Record action
            this.recordAction({
                type: 'instrument_selection',
                instrument: instrumentName,
                timestamp: Date.now(),
                step: this.currentStep
            });
            
            this.showAlert(`Selected: ${instrumentName}`, 'info', 5000);
        }
    }
    
    selectAnatomicalStructure(structureName) {
        if (!this.selectedInstrument) {
            this.showAlert('Please select an instrument first', 'warning');
            return;
        }
        
        // Record action
        this.recordAction({
            type: 'anatomical_interaction',
            structure: structureName,
            instrument: this.selectedInstrument,
            timestamp: Date.now(),
            step: this.currentStep,
            accuracy: this.calculateAccuracy(structureName)
        });
        
        this.showAlert(`Used ${this.selectedInstrument} on ${structureName}`, 'success', 5000);
        
        // Visual feedback
        this.highlightAnatomicalStructure(structureName);
    }
    
    calculateAccuracy(structureName) {
        // Simple accuracy calculation based on current step and structure
        const currentStepData = this.simulationData.simulation.steps[this.currentStep - 1];
        const relevantStructures = this.getRelevantStructures(currentStepData);
        
        if (relevantStructures.includes(structureName)) {
            return Math.random() * 0.3 + 0.7; // 70-100% for correct structures
        } else {
            return Math.random() * 0.5; // 0-50% for incorrect structures
        }
    }
    
    getRelevantStructures(stepData) {
        // Map step types to relevant anatomical structures
        const structureMap = {
            'trocar': ['abdomen', 'peritoneum'],
            'dissection': ['gallbladder', 'hepatic-artery', 'cystic-artery'],
            'inspection': ['liver', 'gallbladder', 'omentum']
        };
        
        const stepType = stepData.title.toLowerCase();
        for (const [key, structures] of Object.entries(structureMap)) {
            if (stepType.includes(key)) {
                return structures;
            }
        }
        
        return ['gallbladder']; // Default
    }
    
    highlightAnatomicalStructure(structureName) {
        const hotspot = document.querySelector(`[onclick*="${structureName}"]`);
        if (hotspot) {
            hotspot.style.animation = 'pulse 1s ease';
            setTimeout(() => {
                hotspot.style.animation = '';
            }, 1000);
        }
    }
    
    recordAction(action) {
        this.userActions.push(action);
        console.log('Action recorded:', action);
    }
    
    async completeStep() {
        if (!this.stepStartTime) return;
        
        const stepTime = Math.floor((Date.now() - this.stepStartTime) / 1000);
        
        try {
            this.showLoading('Assessing performance...');
            
            const response = await fetch(`/api/simulation/${this.simulationId}/step`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    step_number: this.currentStep,
                    actions: this.userActions.filter(a => a.step === this.currentStep),
                    time_taken: stepTime
                })
            });
            
            const assessment = await response.json();
            this.hideLoading();
            
            if (assessment.status === 'success') {
                this.showStepFeedback(assessment);
            } else {
                throw new Error(assessment.error);
            }
            
        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error completing step: ${error.message}`, 'danger');
        }
    }
    
    showStepFeedback(assessment) {
        // Update assessment modal content
        const summaryElement = document.getElementById('assessment-summary');
        if (summaryElement) {
            summaryElement.innerHTML = `
                <div class="score-display">
                    <div class="score-item technical">
                        <div class="score-value">${Math.round(assessment.assessment.technical_score)}%</div>
                        <div class="score-label">Technical Score</div>
                    </div>
                    <div class="score-item communication">
                        <div class="score-value">${Math.round(assessment.assessment.non_technical_score)}%</div>
                        <div class="score-label">Communication</div>
                    </div>
                    <div class="score-item overall">
                        <div class="score-value">${Math.round(assessment.assessment.overall_score)}%</div>
                        <div class="score-label">Overall</div>
                    </div>
                </div>
                <div class="feedback-text">
                    <h4>Feedback</h4>
                    <p>${assessment.assessment.feedback.summary}</p>
                    ${assessment.assessment.feedback.recommendations ? 
                        `<h4>Recommendations</h4>
                         <ul>${assessment.assessment.feedback.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>` 
                        : ''}
                </div>
            `;
        }
        
        // Show feedback modal
        this.showModal('feedback-modal');
    }
    
    continueToNextStep() {
        this.closeModal('feedback-modal');
        
        // Check for complications
        if (this.hasComplicationAtStep(this.currentStep + 1)) {
            this.triggerComplication();
            return;
        }
        
        // Move to next step
        this.currentStep++;
        if (this.currentStep > this.totalSteps) {
            this.completeSimulation();
        } else {
            this.loadCurrentStep();
            this.updateProgressDisplay();
        }
    }
    
    hasComplicationAtStep(stepNumber) {
        if (!this.simulationData.simulation.complications) return false;
        
        return this.simulationData.simulation.complications.some(
            comp => comp.trigger_step === stepNumber
        );
    }
    
    triggerComplication() {
        const complications = this.simulationData.simulation.complications;
        const currentComplication = complications.find(
            comp => comp.trigger_step === this.currentStep
        );
        
        if (currentComplication) {
            this.showComplicationModal(currentComplication);
        }
    }
    
    showComplicationModal(complication) {
        const detailsElement = document.getElementById('complication-details');
        const optionsElement = document.getElementById('management-options');
        
        if (detailsElement) {
            detailsElement.innerHTML = `
                <h4><i class="fas fa-exclamation-triangle"></i> ${complication.type.replace('_', ' ').toUpperCase()}</h4>
                <p><strong>Severity:</strong> ${complication.severity}</p>
                <p><strong>Location:</strong> ${complication.location}</p>
                <p>Immediate assessment and management required.</p>
            `;
        }
        
        if (optionsElement) {
            optionsElement.innerHTML = '';
            complication.management_options.forEach((option, index) => {
                const optionDiv = document.createElement('div');
                optionDiv.className = 'management-option';
                optionDiv.textContent = option;
                optionDiv.onclick = () => this.selectManagementOption(index, option);
                optionsElement.appendChild(optionDiv);
            });
        }
        
        // Start complication timer
        this.startComplicationTimer(complication.time_limit || 300);
        
        this.showModal('complication-modal');
    }
    
    selectManagementOption(index, option) {
        // Remove previous selections
        document.querySelectorAll('.management-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        
        // Select current option
        document.querySelectorAll('.management-option')[index].classList.add('selected');
        
        // Record decision
        this.recordAction({
            type: 'complication_management',
            option: option,
            timestamp: Date.now(),
            step: this.currentStep
        });
        
        // Auto-close modal after selection
        setTimeout(() => {
            this.closeModal('complication-modal');
            this.continueToNextStep();
        }, 2000);
    }
    
    startComplicationTimer(seconds) {
        const timerElement = document.getElementById('complication-timer');
        if (!timerElement) return;
        
        let timeLeft = seconds;
        
        const complicationTimer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const secs = timeLeft % 60;
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(complicationTimer);
                this.handleComplicationTimeout();
            }
            
            timeLeft--;
        }, 1000);
    }
    
    handleComplicationTimeout() {
        this.showAlert('Time expired for complication management', 'danger');
        this.closeModal('complication-modal');
        // Continue with penalty
        this.recordAction({
            type: 'complication_timeout',
            timestamp: Date.now(),
            step: this.currentStep
        });
        this.continueToNextStep();
    }
    
    updateProgressDisplay() {
        // Update current step indicator
        const currentStepElement = document.getElementById('current-step');
        if (currentStepElement) {
            currentStepElement.textContent = `Step ${this.currentStep}`;
        }
        
        // Update step items
        document.querySelectorAll('.step-item').forEach((item, index) => {
            const stepNumber = index + 1;
            item.classList.remove('completed', 'active');
            
            if (stepNumber < this.currentStep) {
                item.classList.add('completed');
            } else if (stepNumber === this.currentStep) {
                item.classList.add('active');
            }
        });
    }
    
    async updateVitals(vitals = null) {
        if (!vitals) {
            try {
                const response = await fetch(`/api/simulation/${this.simulationId}/vitals`);
                const data = await response.json();
                if (data.status === 'success') {
                    vitals = data.vitals;
                }
            } catch (error) {
                console.error('Error fetching vitals:', error);
                return;
            }
        }
        
        if (vitals) {
            document.getElementById('heart-rate').textContent = vitals.heart_rate;
            document.getElementById('blood-pressure').textContent = 
                `${vitals.blood_pressure.systolic}/${vitals.blood_pressure.diastolic}`;
            document.getElementById('oxygen-sat').textContent = vitals.oxygen_saturation;
            document.getElementById('temperature').textContent = vitals.temperature;
        }
    }
    
    startVitalsMonitoring() {
        this.vitalsUpdateInterval = setInterval(() => {
            this.updateVitals();
        }, 5000); // Update every 5 seconds
    }
    
    startTimer() {
        this.startTime = Date.now();
        
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const timerElement = document.getElementById('simulation-timer');
            if (timerElement) {
                timerElement.textContent = this.formatTime(elapsed);
            }
            
            // Update step timer
            if (this.stepStartTime) {
                const stepElapsed = Math.floor((Date.now() - this.stepStartTime) / 1000);
                const stepTimerElement = document.getElementById('step-timer');
                if (stepTimerElement) {
                    stepTimerElement.textContent = this.formatTime(stepElapsed);
                }
            }
        }, 1000);
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    handleKeyboardShortcuts(e) {
        // Keyboard shortcuts for common actions
        switch (e.key) {
            case ' ': // Spacebar
                e.preventDefault();
                this.completeStep();
                break;
            case 'h':
                this.requestHelp();
                break;
            case 'p':
                this.pauseSimulation();
                break;
            case 'Escape':
                if (document.querySelectorAll('.modal.show').length === 0) {
                    this.pauseSimulation();
                }
                break;
        }
    }
    
    initializeSurgicalCanvas() {
        const canvas = document.getElementById('surgical-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Draw basic surgical field background
        this.drawSurgicalField(ctx, canvas.width, canvas.height);
        
        // Handle canvas interactions
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            this.handleCanvasClick(x, y);
        });
        
        // Resize handler
        window.addEventListener('resize', () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            this.drawSurgicalField(ctx, canvas.width, canvas.height);
        });
    }
    
    drawSurgicalField(ctx, width, height) {
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw surgical field background
        const gradient = ctx.createRadialGradient(width/2, height/2, 0, width/2, height/2, width/2);
        gradient.addColorStop(0, '#2d3748');
        gradient.addColorStop(1, '#1a202c');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
        
        // Draw anatomical outlines (simplified)
        this.drawAnatomicalStructures(ctx, width, height);
    }
    
    drawAnatomicalStructures(ctx, width, height) {
        // Draw simplified anatomical structures
        ctx.strokeStyle = '#4a5568';
        ctx.lineWidth = 2;
        
        // Gallbladder outline
        ctx.beginPath();
        ctx.ellipse(width * 0.4, height * 0.3, 40, 60, 0, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Liver edge
        ctx.beginPath();
        ctx.moveTo(width * 0.2, height * 0.4);
        ctx.quadraticCurveTo(width * 0.5, height * 0.2, width * 0.8, height * 0.4);
        ctx.stroke();
        
        // Add labels
        ctx.fillStyle = '#a0aec0';
        ctx.font = '12px Arial';
        ctx.fillText('Gallbladder', width * 0.32, height * 0.4);
        ctx.fillText('Liver', width * 0.45, height * 0.35);
    }
    
    handleCanvasClick(x, y) {
        // Determine what was clicked based on coordinates
        const canvas = document.getElementById('surgical-canvas');
        const width = canvas.width;
        const height = canvas.height;
        
        // Check if click is on gallbladder area
        const gbCenterX = width * 0.4;
        const gbCenterY = height * 0.3;
        const distance = Math.sqrt((x - gbCenterX)**2 + (y - gbCenterY)**2);
        
        if (distance < 50) {
            this.selectAnatomicalStructure('gallbladder');
        }
    }
    
    async pauseSimulation() {
        // Stop timers
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        if (this.vitalsUpdateInterval) {
            clearInterval(this.vitalsUpdateInterval);
            this.vitalsUpdateInterval = null;
        }
        
        // Show pause dialog
        const resume = confirm('Simulation paused. Click OK to resume or Cancel to exit.');
        
        if (resume) {
            this.resumeSimulation();
        } else {
            this.exitSimulation();
        }
    }
    
    resumeSimulation() {
        // Restart timers
        this.startTimer();
        this.startVitalsMonitoring();
        this.showAlert('Simulation resumed', 'info', 5000);
    }
    
    exitSimulation() {
        // Clean up intervals
        if (this.timerInterval) clearInterval(this.timerInterval);
        if (this.vitalsUpdateInterval) clearInterval(this.vitalsUpdateInterval);
        
        // Confirm exit
        const confirmExit = confirm('Are you sure you want to exit? Progress will be lost.');
        if (confirmExit) {
            this.redirectToDashboard();
        } else {
            this.resumeSimulation();
        }
    }
    
    async completeSimulation() {
        try {
            this.showLoading('Generating final assessment...');
            
            const response = await fetch(`/api/simulation/${this.simulationId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            this.hideLoading();
            
            if (result.status === 'success') {
                this.showFinalAssessment(result.final_assessment);
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            this.hideLoading();
            this.showAlert(`Error completing simulation: ${error.message}`, 'danger');
        }
    }
    
    showFinalAssessment(assessment) {
        // Create final assessment modal content
        const modalContent = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2><i class="fas fa-trophy"></i> Simulation Complete</h2>
                </div>
                <div class="modal-body">
                    <div class="final-scores">
                        <div class="score-highlight">
                            <h3>Overall Score: ${assessment.scores.overall_average}%</h3>
                            <p class="performance-level">${assessment.final_feedback.performance_level}</p>
                        </div>
                        <div class="score-breakdown">
                            <div class="score-row">
                                <span>Technical Skills:</span>
                                <span>${assessment.scores.technical_average}%</span>
                            </div>
                            <div class="score-row">
                                <span>Communication:</span>
                                <span>${assessment.scores.non_technical_average}%</span>
                            </div>
                            <div class="score-row">
                                <span>Total Time:</span>
                                <span>${assessment.performance_metrics.total_time_minutes} min</span>
                            </div>
                        </div>
                    </div>
                    <div class="learning-plan">
                        <h4>Your Learning Plan</h4>
                        <ul>
                            ${assessment.learning_plan.practice_recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.viewDetailedResults()">View Details</button>
                    <button class="btn btn-primary" onclick="this.redirectToDashboard()">Return to Dashboard</button>
                </div>
            </div>
        `;
        
        // Show final assessment
        document.body.insertAdjacentHTML('beforeend', `<div id="final-assessment-modal" class="modal show">${modalContent}</div>`);
    }
    
    requestHelp() {
        const currentStepData = this.simulationData.simulation.steps[this.currentStep - 1];
        
        let helpText = `<h4>Step ${this.currentStep}: ${currentStepData.title}</h4>`;
        helpText += `<p>${currentStepData.description}</p>`;
        
        if (currentStepData.hints) {
            helpText += '<h5>Hints:</h5><ul>';
            currentStepData.hints.forEach(hint => {
                helpText += `<li>${hint}</li>`;
            });
            helpText += '</ul>';
        }
        
        this.showAlert(helpText, 'info', 8000);
        
        // Record help request
        this.recordAction({
            type: 'help_requested',
            step: this.currentStep,
            timestamp: Date.now()
        });
    }
    
    reportComplication() {
        // Allow user to report unexpected complications
        const complicationText = prompt('Describe the complication you observed:');
        if (complicationText) {
            this.recordAction({
                type: 'user_reported_complication',
                description: complicationText,
                step: this.currentStep,
                timestamp: Date.now()
            });
            
            this.showAlert('Complication reported. Instructor will be notified.', 'warning');
        }
    }
    
    adjustCamera(action) {
        // Handle camera adjustments
        this.recordAction({
            type: 'camera_adjustment',
            action: action,
            step: this.currentStep,
            timestamp: Date.now()
        });
        
        // Visual feedback
        const viewport = document.getElementById('surgical-viewport');
        if (viewport) {
            viewport.classList.add('camera-adjusting');
            setTimeout(() => {
                viewport.classList.remove('camera-adjusting');
            }, 500);
        }
        
        this.showAlert(`Camera ${action.replace('-', ' ')}`, 'info', 3000);
    }
    
    // Utility Methods
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'flex';
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
        }
    }
    
    showAlert(message, type = 'info', duration = 5000) {
        const alertsContainer = document.getElementById('alerts-container');
        if (!alertsContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${this.getAlertIcon(type)}"></i>
            ${message}
        `;
        
        alertsContainer.appendChild(alert);
        
        // Auto-remove
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
    
    redirectToDashboard() {
        window.location.href = '/';
    }
    
    cleanup() {
        // Clean up intervals and event listeners
        if (this.timerInterval) clearInterval(this.timerInterval);
        if (this.vitalsUpdateInterval) clearInterval(this.vitalsUpdateInterval);
    }
}

// Global simulation instance
let simulationInterface;

// Global functions for HTML event handlers
function completeStep() {
    if (simulationInterface) {
        simulationInterface.completeStep();
    }
}

function continueToNextStep() {
    if (simulationInterface) {
        simulationInterface.continueToNextStep();
    }
}

function requestHelp() {
    if (simulationInterface) {
        simulationInterface.requestHelp();
    }
}

function reportComplication() {
    if (simulationInterface) {
        simulationInterface.reportComplication();
    }
}

function pauseSimulation() {
    if (simulationInterface) {
        simulationInterface.pauseSimulation();
    }
}

function exitSimulation() {
    if (simulationInterface) {
        simulationInterface.exitSimulation();
    }
}

function adjustCamera(action) {
    if (simulationInterface) {
        simulationInterface.adjustCamera(action);
    }
}

function selectAnatomicalStructure(structure) {
    if (simulationInterface) {
        simulationInterface.selectAnatomicalStructure(structure);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    simulationInterface = new SimulationInterface();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (simulationInterface) {
        simulationInterface.cleanup();
    }
});