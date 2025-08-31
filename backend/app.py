from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import uuid
import time
from datetime import datetime
import os

from simulation_generator import SimulationGenerator
from patient_generator import PatientGenerator
from assessment_engine import AssessmentEngine
from database_manager import DatabaseManager

app = Flask(__name__, 
           template_folder='../frontend/templates', 
           static_folder='../frontend/static')
CORS(app)

# Initialize components
simulation_gen = SimulationGenerator()
patient_gen = PatientGenerator()
assessment_engine = AssessmentEngine()
db_manager = DatabaseManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/test-static')
def test_static():
    """Test static file serving"""
    return f"""
    <h1>Static File Test</h1>
    <p>Static folder: {app.static_folder}</p>
    <p>Template folder: {app.template_folder}</p>
    <p>Main CSS exists: {os.path.exists(os.path.join(app.static_folder, 'css', 'main.css'))}</p>
    <p>Dashboard CSS exists: {os.path.exists(os.path.join(app.static_folder, 'css', 'dashboard.css'))}</p>
    <p>Main JS exists: {os.path.exists(os.path.join(app.static_folder, 'js', 'main.js'))}</p>
    <p>Dashboard JS exists: {os.path.exists(os.path.join(app.static_folder, 'js', 'dashboard.js'))}</p>
    """

@app.route('/simulation')
def simulation_page():
    """Simulation interface page"""
    simulation_id = request.args.get('id')
    return render_template('simulation.html', simulation_id=simulation_id)

@app.route('/api/procedures', methods=['GET'])
def get_procedures():
    """Get available surgical procedures"""
    procedures = [
        {
            "id": "laparoscopic_cholecystectomy",
            "name": "Laparoscopic Cholecystectomy",
            "category": "General Surgery",
            "difficulty": ["beginner", "intermediate", "advanced"],
            "duration": "45-90 minutes"
        },
        {
            "id": "appendectomy",
            "name": "Appendectomy",
            "category": "General Surgery", 
            "difficulty": ["beginner", "intermediate"],
            "duration": "30-60 minutes"
        },
        {
            "id": "knee_arthroscopy",
            "name": "Knee Arthroscopy",
            "category": "Orthopedic",
            "difficulty": ["intermediate", "advanced"],
            "duration": "60-120 minutes"
        }
    ]
    return jsonify(procedures)

@app.route('/api/generate-simulation', methods=['POST'])
def generate_simulation():
    """Generate a new surgical simulation"""
    try:
        config = request.json
        
        # Generate patient profile
        patient = patient_gen.generate_patient(
            age_range=config.get('age_range', [20, 80]),
            gender=config.get('gender', 'random'),
            medical_history=config.get('medical_history', [])
        )
        
        # Generate simulation scenario
        simulation = simulation_gen.generate_scenario(
            procedure_type=config['procedure_type'],
            difficulty_level=config['difficulty_level'],
            patient_profile=patient,
            learning_objectives=config.get('learning_objectives', []),
            complications_enabled=config.get('complications_enabled', True)
        )
        
        # Store simulation in database
        simulation_id = str(uuid.uuid4())
        db_manager.save_simulation(simulation_id, simulation, patient)
        
        return jsonify({
            "simulation_id": simulation_id,
            "patient": patient,
            "simulation": simulation,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/simulation/<simulation_id>/step', methods=['POST'])
def process_simulation_step(simulation_id):
    """Process a simulation step and provide feedback"""
    try:
        data = request.json
        step_number = data['step_number']
        user_actions = data['actions']
        time_taken = data['time_taken']
        
        # Get simulation data
        simulation_data = db_manager.get_simulation(simulation_id)
        
        # Assess performance
        assessment = assessment_engine.assess_step(
            simulation_data,
            step_number,
            user_actions,
            time_taken
        )
        
        # Generate next step or complications
        next_step = simulation_gen.get_next_step(
            simulation_data,
            step_number,
            assessment
        )
        
        # Update simulation state
        db_manager.update_simulation_progress(
            simulation_id,
            step_number,
            assessment,
            user_actions
        )
        
        return jsonify({
            "assessment": assessment,
            "next_step": next_step,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/simulation/<simulation_id>', methods=['GET'])
def get_simulation_data(simulation_id):
    """Get simulation data by ID"""
    try:
        simulation_data = db_manager.get_simulation(simulation_id)
        if not simulation_data:
            return jsonify({"error": "Simulation not found"}), 404
            
        return jsonify({
            "simulation": simulation_data,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/simulation/<simulation_id>/vitals', methods=['GET'])
def get_patient_vitals(simulation_id):
    """Get current patient vitals for the simulation"""
    try:
        simulation_data = db_manager.get_simulation(simulation_id)
        current_vitals = simulation_gen.generate_current_vitals(
            simulation_data['patient'],
            simulation_data['current_step'],
            simulation_data['complications']
        )
        
        return jsonify({
            "vitals": current_vitals,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/simulation/<simulation_id>/complete', methods=['POST'])
def complete_simulation(simulation_id):
    """Complete simulation and generate final assessment"""
    try:
        # Get complete simulation data
        simulation_data = db_manager.get_simulation(simulation_id)
        
        # Generate final assessment
        final_assessment = assessment_engine.generate_final_assessment(
            simulation_data
        )
        
        # Mark simulation as complete
        db_manager.complete_simulation(simulation_id, final_assessment)
        
        return jsonify({
            "final_assessment": final_assessment,
            "simulation_summary": simulation_data,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/api/complications/generate', methods=['POST'])
def generate_complication():
    """Generate a dynamic complication during simulation"""
    try:
        data = request.json
        simulation_id = data['simulation_id']
        current_step = data['current_step']
        
        simulation_data = db_manager.get_simulation(simulation_id)
        complication = simulation_gen.generate_dynamic_complication(
            simulation_data,
            current_step
        )
        
        # Update simulation with complication
        db_manager.add_complication(simulation_id, complication)
        
        return jsonify({
            "complication": complication,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db_manager.get_connection()
        
        # Check application status
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "connected",
                "simulation_engine": "operational",
                "assessment_engine": "operational"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/metrics')
def metrics():
    """Application metrics endpoint"""
    try:
        import psutil
        
        return jsonify({
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "active_connections": len(psutil.net_connections()),
            "uptime": time.time() - psutil.boot_time(),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Initialize database
    db_manager.init_database()
    
    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)