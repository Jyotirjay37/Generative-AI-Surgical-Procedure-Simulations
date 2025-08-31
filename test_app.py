#!/usr/bin/env python3
"""
Test script for Surgical Simulation Platform
This script tests the main components of the application
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from simulation_generator import SimulationGenerator
        print("✅ SimulationGenerator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import SimulationGenerator: {e}")
        return False
    
    try:
        from patient_generator import PatientGenerator
        print("✅ PatientGenerator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import PatientGenerator: {e}")
        return False
    
    try:
        from assessment_engine import AssessmentEngine
        print("✅ AssessmentEngine imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AssessmentEngine: {e}")
        return False
    
    try:
        from database_manager import DatabaseManager
        print("✅ DatabaseManager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DatabaseManager: {e}")
        return False
    
    return True

def test_patient_generation():
    """Test patient generation functionality"""
    print("\n🧪 Testing patient generation...")
    
    try:
        from patient_generator import PatientGenerator
        patient_gen = PatientGenerator()
        
        # Test basic patient generation
        patient = patient_gen.generate_patient()
        assert patient is not None
        assert 'demographics' in patient
        assert 'age' in patient['demographics']
        assert 'gender' in patient['demographics']
        assert 'medical_history' in patient
        assert 'vitals' in patient
        
        print("✅ Basic patient generation works")
        
        # Test patient with specific parameters
        patient = patient_gen.generate_patient(
            age_range=(30, 50),
            gender="female",
            medical_history=["diabetes"]
        )
        assert 30 <= patient['demographics']['age'] <= 50
        assert patient['demographics']['gender'] == "female"
        assert "diabetes" in patient['medical_history']
        
        print("✅ Patient generation with parameters works")
        return True
        
    except Exception as e:
        print(f"❌ Patient generation test failed: {e}")
        return False

def test_simulation_generation():
    """Test simulation generation functionality"""
    print("\n🧪 Testing simulation generation...")
    
    try:
        from simulation_generator import SimulationGenerator
        from patient_generator import PatientGenerator
        
        sim_gen = SimulationGenerator()
        patient_gen = PatientGenerator()
        
        # Generate a patient
        patient = patient_gen.generate_patient()
        
        # Generate a simulation
        simulation = sim_gen.generate_scenario(
            procedure_type="laparoscopic_cholecystectomy",
            difficulty_level="beginner",
            patient_profile=patient,
            learning_objectives=["technical_skills", "patient_safety"]
        )
        
        assert simulation is not None
        assert 'steps' in simulation
        assert 'procedure_info' in simulation
        assert 'difficulty_level' in simulation
        assert simulation['procedure_info']['name'] == "Laparoscopic Cholecystectomy"
        
        print("✅ Simulation generation works")
        return True
        
    except Exception as e:
        print(f"❌ Simulation generation test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🧪 Testing database functionality...")
    
    try:
        from database_manager import DatabaseManager
        
        # Initialize database
        db = DatabaseManager()
        db.init_database()
        
        print("✅ Database initialization works")
        
        # Test saving and retrieving simulation
        test_simulation = {
            'procedure_info': {
                'name': 'Test Procedure',
                'category': 'General Surgery',
                'estimated_duration': 60
            },
            'difficulty_level': 'beginner',
            'steps': []
        }
        
        test_patient = {
            'demographics': {'age': 30, 'gender': 'male'},
            'medical_history': [],
            'vitals': {}
        }
        
        simulation_id = f"test-{datetime.now().timestamp()}"
        db.save_simulation(simulation_id, test_simulation, test_patient)
        
        # Retrieve simulation
        retrieved = db.get_simulation(simulation_id)
        assert retrieved is not None
        assert 'simulation' in retrieved
        assert retrieved['simulation']['procedure_info']['name'] == 'Test Procedure'
        
        print("✅ Database save/retrieve works")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_assessment():
    """Test assessment functionality"""
    print("\n🧪 Testing assessment functionality...")
    
    try:
        from assessment_engine import AssessmentEngine
        
        assessment_engine = AssessmentEngine()
        
        # Test step assessment
        test_data = {
            'simulation': {
                'procedure_info': {
                    'name': 'Laparoscopic Cholecystectomy'
                },
                'steps': [
                    {
                        'title': 'Patient Preparation',
                        'description': 'Position patient supine, prep and drape surgical site',
                        'duration': '10-15 minutes'
                    }
                ]
            }
        }
        
        assessment = assessment_engine.assess_step(
            test_data, 1, [{'type': 'incision', 'accuracy': 0.8}], 60
        )
        
        assert assessment is not None
        assert 'overall_score' in assessment
        assert 'feedback' in assessment
        
        print("✅ Assessment functionality works")
        return True
        
    except Exception as e:
        print(f"❌ Assessment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏥 Surgical Simulation Platform - Component Tests")
    print("="*60)
    
    tests = [
        test_imports,
        test_patient_generation,
        test_simulation_generation,
        test_database,
        test_assessment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("  python start.py")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
