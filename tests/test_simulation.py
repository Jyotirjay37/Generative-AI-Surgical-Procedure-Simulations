import pytest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from simulation_generator import SimulationGenerator
from patient_generator import PatientGenerator

class TestSimulationGenerator:
    def setup_method(self):
        self.sim_gen = SimulationGenerator()
        self.patient_gen = PatientGenerator()
    
    def test_generate_scenario_basic(self):
        """Test basic scenario generation"""
        patient = self.patient_gen.generate_patient()
        scenario = self.sim_gen.generate_scenario(
            procedure_type="laparoscopic_cholecystectomy",
            difficulty_level="beginner",
            patient_profile=patient
        )
        
        assert scenario is not None
        assert "steps" in scenario
        assert "patient" in scenario
        assert "procedure_type" in scenario
        assert scenario["procedure_type"] == "laparoscopic_cholecystectomy"
        assert scenario["difficulty_level"] == "beginner"
    
    def test_generate_scenario_with_complications(self):
        """Test scenario generation with complications enabled"""
        patient = self.patient_gen.generate_patient()
        scenario = self.sim_gen.generate_scenario(
            procedure_type="appendectomy",
            difficulty_level="intermediate",
            patient_profile=patient,
            complications_enabled=True
        )
        
        assert scenario is not None
        assert "complications" in scenario
        assert isinstance(scenario["complications"], list)
    
    def test_get_next_step(self):
        """Test getting next step in simulation"""
        patient = self.patient_gen.generate_patient()
        scenario = self.sim_gen.generate_scenario(
            procedure_type="knee_arthroscopy",
            difficulty_level="advanced",
            patient_profile=patient
        )
        
        # Test first step
        next_step = self.sim_gen.get_next_step(scenario, 0, {"score": 85})
        assert next_step is not None
        assert "instructions" in next_step
        assert "expected_actions" in next_step
    
    def test_generate_dynamic_complication(self):
        """Test dynamic complication generation"""
        patient = self.patient_gen.generate_patient()
        scenario = self.sim_gen.generate_scenario(
            procedure_type="laparoscopic_cholecystectomy",
            difficulty_level="intermediate",
            patient_profile=patient
        )
        
        complication = self.sim_gen.generate_dynamic_complication(scenario, 2)
        assert complication is not None
        assert "type" in complication
        assert "description" in complication
        assert "severity" in complication
    
    def test_generate_current_vitals(self):
        """Test current vitals generation"""
        patient = self.patient_gen.generate_patient()
        scenario = self.sim_gen.generate_scenario(
            procedure_type="appendectomy",
            difficulty_level="beginner",
            patient_profile=patient
        )
        
        vitals = self.sim_gen.generate_current_vitals(
            patient, 
            current_step=1, 
            complications=[]
        )
        
        assert vitals is not None
        assert "heart_rate" in vitals
        assert "blood_pressure" in vitals
        assert "temperature" in vitals
        assert "oxygen_saturation" in vitals
    
    def test_invalid_procedure_type(self):
        """Test handling of invalid procedure type"""
        patient = self.patient_gen.generate_patient()
        
        with pytest.raises(ValueError):
            self.sim_gen.generate_scenario(
                procedure_type="invalid_procedure",
                difficulty_level="beginner",
                patient_profile=patient
            )
    
    def test_invalid_difficulty_level(self):
        """Test handling of invalid difficulty level"""
        patient = self.patient_gen.generate_patient()
        
        with pytest.raises(ValueError):
            self.sim_gen.generate_scenario(
                procedure_type="laparoscopic_cholecystectomy",
                difficulty_level="expert",
                patient_profile=patient
            )

class TestPatientGenerator:
    def setup_method(self):
        self.patient_gen = PatientGenerator()
    
    def test_generate_patient_basic(self):
        """Test basic patient generation"""
        patient = self.patient_gen.generate_patient()
        
        assert patient is not None
        assert "age" in patient
        assert "gender" in patient
        assert "medical_history" in patient
        assert "vitals" in patient
        assert 18 <= patient["age"] <= 100
        assert patient["gender"] in ["male", "female"]
    
    def test_generate_patient_with_age_range(self):
        """Test patient generation with specific age range"""
        patient = self.patient_gen.generate_patient(age_range=[30, 50])
        
        assert 30 <= patient["age"] <= 50
    
    def test_generate_patient_with_gender(self):
        """Test patient generation with specific gender"""
        patient = self.patient_gen.generate_patient(gender="female")
        
        assert patient["gender"] == "female"
    
    def test_generate_patient_with_medical_history(self):
        """Test patient generation with medical history"""
        medical_history = ["diabetes", "hypertension"]
        patient = self.patient_gen.generate_patient(medical_history=medical_history)
        
        assert "diabetes" in patient["medical_history"]
        assert "hypertension" in patient["medical_history"]
    
    def test_patient_vitals_consistency(self):
        """Test that patient vitals are within reasonable ranges"""
        patient = self.patient_gen.generate_patient()
        vitals = patient["vitals"]
        
        assert 60 <= vitals["heart_rate"] <= 120
        assert 90 <= vitals["systolic_bp"] <= 180
        assert 60 <= vitals["diastolic_bp"] <= 110
        assert 36.5 <= vitals["temperature"] <= 38.5
        assert 95 <= vitals["oxygen_saturation"] <= 100
