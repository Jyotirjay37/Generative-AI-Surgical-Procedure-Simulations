import random
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class PatientGenerator:
    def __init__(self):
        self.medical_conditions = self._load_medical_conditions()
        self.medications = self._load_medications()
        
    def _load_medical_conditions(self) -> Dict:
        """Load medical condition templates"""
        return {
            "diabetes": {
                "type": "metabolic",
                "complications": ["delayed wound healing", "infection risk"],
                "management": ["glucose monitoring", "insulin adjustment"]
            },
            "hypertension": {
                "type": "cardiovascular", 
                "complications": ["bleeding risk", "anesthesia considerations"],
                "management": ["blood pressure monitoring", "medication adjustment"]
            },
            "obesity": {
                "type": "metabolic",
                "complications": ["difficult visualization", "trocar placement challenges"],
                "management": ["positioning considerations", "equipment selection"]
            },
            "previous_surgery": {
                "type": "surgical_history",
                "complications": ["adhesions", "altered anatomy"],
                "management": ["careful dissection", "adhesiolysis"]
            }
        }
    
    def _load_medications(self) -> List[str]:
        """Load common medications"""
        return [
            "metformin", "lisinopril", "atorvastatin", "metoprolol",
            "omeprazole", "aspirin", "warfarin", "levothyroxine"
        ]
    
    def generate_patient(self, age_range: Tuple[int, int] = (20, 80), 
                        gender: str = "random", 
                        medical_history: List[str] = None) -> Dict:
        """Generate a realistic patient profile"""
        
        if gender == "random":
            gender = random.choice(["male", "female"])
        
        age = random.randint(age_range[0], age_range[1])
        
        # Generate demographics
        patient = {
            "demographics": {
                "age": age,
                "gender": gender,
                "weight": self._generate_weight(age, gender),
                "height": self._generate_height(gender),
                "bmi": None  # Will calculate
            },
            "medical_history": medical_history or self._generate_medical_history(age),
            "medications": self._generate_medications(age),
            "allergies": self._generate_allergies(),
            "social_history": self._generate_social_history(age),
            "vitals": self._generate_baseline_vitals(age),
            "lab_results": self._generate_lab_results(age),
            "imaging": self._generate_imaging_findings()
        }
        
        # Calculate BMI
        weight_kg = patient["demographics"]["weight"]
        height_m = patient["demographics"]["height"] / 100
        patient["demographics"]["bmi"] = round(weight_kg / (height_m ** 2), 1)
        
        return patient
    
    def _generate_weight(self, age: int, gender: str) -> int:
        """Generate realistic weight based on demographics"""
        if gender == "male":
            base_weight = random.randint(65, 95)
        else:
            base_weight = random.randint(55, 85)
        
        # Age factor
        if age > 50:
            base_weight += random.randint(0, 15)
        
        return base_weight
    
    def _generate_height(self, gender: str) -> int:
        """Generate realistic height in centimeters"""
        if gender == "male":
            return random.randint(165, 190)
        else:
            return random.randint(155, 180)
    
    def _generate_medical_history(self, age: int) -> List[str]:
        """Generate age-appropriate medical history"""
        conditions = []
        
        # Age-based probability of conditions
        if age > 40:
            if random.random() < 0.3:
                conditions.append("hypertension")
            if random.random() < 0.2:
                conditions.append("diabetes")
        
        if age > 50:
            if random.random() < 0.4:
                conditions.append("obesity")
            if random.random() < 0.3:
                conditions.append("previous_surgery")
        
        # Random additional conditions
        all_conditions = list(self.medical_conditions.keys())
        if random.random() < 0.2:
            additional = random.choice([c for c in all_conditions if c not in conditions])
            conditions.append(additional)
        
        return conditions
    
    def _generate_medications(self, age: int) -> List[str]:
        """Generate realistic medication list"""
        medications = []
        
        # Age-based medications
        if age > 45:
            if random.random() < 0.4:
                medications.append("atorvastatin")
            if random.random() < 0.3:
                medications.append("lisinopril")
        
        if age > 60:
            if random.random() < 0.2:
                medications.append("aspirin")
        
        # Random additional medications
        if random.random() < 0.3:
            additional = random.choice(self.medications)
            if additional not in medications:
                medications.append(additional)
        
        return medications
    
    def _generate_allergies(self) -> List[str]:
        """Generate patient allergies"""
        common_allergies = ["penicillin", "latex", "iodine", "eggs", "shellfish"]
        
        allergies = []
        if random.random() < 0.2:  # 20% chance of allergies
            num_allergies = random.randint(1, 2)
            allergies = random.sample(common_allergies, num_allergies)
        
        return allergies
    
    def _generate_social_history(self, age: int) -> Dict:
        """Generate social history"""
        return {
            "smoking": random.choice(["never", "former", "current"]) if age > 18 else "never",
            "alcohol": random.choice(["none", "social", "moderate"]) if age > 21 else "none",
            "occupation": random.choice(["teacher", "engineer", "nurse", "retired", "student"]),
            "exercise": random.choice(["sedentary", "light", "moderate", "active"])
        }
    
    def _generate_baseline_vitals(self, age: int) -> Dict:
        """Generate baseline vital signs"""
        return {
            "heart_rate": random.randint(60, 100),
            "blood_pressure": {
                "systolic": random.randint(110, 140),
                "diastolic": random.randint(70, 90)
            },
            "respiratory_rate": random.randint(12, 20),
            "temperature": round(random.uniform(36.5, 37.2), 1),
            "oxygen_saturation": random.randint(95, 100)
        }
    
    def _generate_lab_results(self, age: int) -> Dict:
        """Generate realistic laboratory results"""
        return {
            "complete_blood_count": {
                "hemoglobin": round(random.uniform(12.0, 16.0), 1),
                "hematocrit": round(random.uniform(36.0, 48.0), 1),
                "white_blood_cells": round(random.uniform(4.0, 11.0), 1),
                "platelets": random.randint(150, 450)
            },
            "basic_metabolic_panel": {
                "sodium": random.randint(135, 145),
                "potassium": round(random.uniform(3.5, 5.0), 1),
                "chloride": random.randint(98, 108),
                "glucose": random.randint(80, 120),
                "creatinine": round(random.uniform(0.6, 1.2), 1)
            },
            "liver_function": {
                "alt": random.randint(10, 40),
                "ast": random.randint(10, 40),
                "bilirubin": round(random.uniform(0.2, 1.2), 1)
            },
            "coagulation": {
                "pt": round(random.uniform(11.0, 13.0), 1),
                "ptt": round(random.uniform(25.0, 35.0), 1),
                "inr": round(random.uniform(0.9, 1.1), 1)
            }
        }
    
    def _generate_imaging_findings(self) -> Dict:
        """Generate imaging study results"""
        return {
            "ultrasound": {
                "gallbladder_wall_thickness": round(random.uniform(2.0, 8.0), 1),
                "stones_present": random.choice([True, False]),
                "pericholecystic_fluid": random.choice([True, False]),
                "murphy_sign": random.choice([True, False])
            },
            "ct_findings": {
                "inflammation": random.choice(["none", "mild", "moderate", "severe"]),
                "complications": random.choice(["none", "perforation", "abscess"]),
                "anatomy_variants": random.choice([True, False])
            }
        }