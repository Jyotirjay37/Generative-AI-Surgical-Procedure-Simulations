import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SimulationGenerator:
    def __init__(self):
        self.procedure_templates = self._load_procedure_templates()
        self.complication_library = self._load_complications()
        
    def _load_procedure_templates(self) -> Dict:
        """Load surgical procedure templates"""
        return {
            "laparoscopic_cholecystectomy": {
                "name": "Laparoscopic Cholecystectomy",
                "category": "General Surgery",
                "base_duration": 60,
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Patient Preparation",
                        "description": "Position patient supine, prep and drape surgical site",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Proper patient positioning",
                            "Sterile field maintenance",
                            "Antibiotic prophylaxis"
                        ],
                        "instruments": ["surgical drapes", "prep solution", "positioning aids"]
                    },
                    {
                        "step_number": 2,
                        "title": "Trocar Placement", 
                        "description": "Create pneumoperitoneum and insert trocars",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Safe entry technique",
                            "Proper CO2 insufflation",
                            "Trocar positioning"
                        ],
                        "instruments": ["veress needle", "trocars", "CO2 insufflator"]
                    },
                    {
                        "step_number": 3,
                        "title": "Diagnostic Laparoscopy",
                        "description": "Inspect abdominal cavity and identify anatomy",
                        "duration": "5-10 minutes", 
                        "critical_points": [
                            "Systematic inspection",
                            "Adhesion identification",
                            "Anatomical orientation"
                        ],
                        "instruments": ["laparoscope", "graspers"]
                    },
                    {
                        "step_number": 4,
                        "title": "Critical View of Safety",
                        "description": "Achieve critical view of safety before dissection",
                        "duration": "15-20 minutes",
                        "critical_points": [
                            "Clear identification of Calot's triangle",
                            "Only 2 structures entering gallbladder",
                            "Clear view of liver bed"
                        ],
                        "instruments": ["graspers", "dissector", "clip applier"]
                    },
                    {
                        "step_number": 5,
                        "title": "Gallbladder Dissection",
                        "description": "Dissect gallbladder from liver bed",
                        "duration": "15-25 minutes",
                        "critical_points": [
                            "Maintain proper plane",
                            "Hemostasis control",
                            "Avoid perforation"
                        ],
                        "instruments": ["electrocautery", "graspers", "irrigation"]
                    },
                    {
                        "step_number": 6,
                        "title": "Specimen Removal",
                        "description": "Remove gallbladder and close incisions",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Secure specimen in bag",
                            "Inspect for bleeding", 
                            "Remove CO2"
                        ],
                        "instruments": ["specimen bag", "sutures", "local anesthetic"]
                    }
                ]
            },
            "appendectomy": {
                "name": "Laparoscopic Appendectomy",
                "category": "General Surgery",
                "base_duration": 45,
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Patient Preparation",
                        "description": "Position patient and establish pneumoperitoneum",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Left lateral tilt positioning",
                            "Safe trocar insertion",
                            "Adequate visualization"
                        ],
                        "instruments": ["trocars", "CO2 insufflator", "laparoscope"]
                    },
                    {
                        "step_number": 2,
                        "title": "Appendix Identification",
                        "description": "Locate and mobilize the appendix",
                        "duration": "5-10 minutes",
                        "critical_points": [
                            "Identify cecum and ileocecal valve",
                            "Locate appendix base",
                            "Assess inflammation extent"
                        ],
                        "instruments": ["graspers", "atraumatic forceps"]
                    },
                    {
                        "step_number": 3,
                        "title": "Mesoappendix Division",
                        "description": "Divide mesoappendix and appendiceal artery",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Identify appendiceal artery",
                            "Sequential clip application",
                            "Avoid thermal injury"
                        ],
                        "instruments": ["clip applier", "electrocautery", "scissors"]
                    },
                    {
                        "step_number": 4,
                        "title": "Appendix Transection",
                        "description": "Transect appendix and remove specimen",
                        "duration": "5-10 minutes",
                        "critical_points": [
                            "Secure base with clips",
                            "Transect between clips",
                            "Remove specimen safely"
                        ],
                        "instruments": ["clip applier", "scissors", "specimen bag"]
                    },
                    {
                        "step_number": 5,
                        "title": "Closure",
                        "description": "Close incisions and apply dressings",
                        "duration": "5-10 minutes",
                        "critical_points": [
                            "Inspect for bleeding",
                            "Close fascial defects",
                            "Apply sterile dressings"
                        ],
                        "instruments": ["sutures", "dressings", "local anesthetic"]
                    }
                ]
            },
            "knee_arthroscopy": {
                "name": "Knee Arthroscopy",
                "category": "Orthopedic",
                "base_duration": 90,
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Patient Positioning",
                        "description": "Position patient supine with knee flexed at 90 degrees",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Proper knee positioning",
                            "Tourniquet application",
                            "Sterile field preparation"
                        ],
                        "instruments": ["positioning aids", "tourniquet", "surgical drapes"]
                    },
                    {
                        "step_number": 2,
                        "title": "Portal Placement",
                        "description": "Create anterolateral and anteromedial portals",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Proper portal positioning",
                            "Avoid neurovascular structures",
                            "Adequate portal spacing"
                        ],
                        "instruments": ["scalpel", "arthroscope", "cannulas"]
                    },
                    {
                        "step_number": 3,
                        "title": "Diagnostic Arthroscopy",
                        "description": "Systematic examination of knee compartments",
                        "duration": "15-20 minutes",
                        "critical_points": [
                            "Systematic compartment examination",
                            "Documentation of findings",
                            "Assessment of pathology"
                        ],
                        "instruments": ["arthroscope", "probe", "camera system"]
                    },
                    {
                        "step_number": 4,
                        "title": "Meniscal Assessment",
                        "description": "Evaluate meniscal integrity and pathology",
                        "duration": "20-30 minutes",
                        "critical_points": [
                            "Meniscal tear identification",
                            "Stability assessment",
                            "Treatment planning"
                        ],
                        "instruments": ["probe", "graspers", "meniscal instruments"]
                    },
                    {
                        "step_number": 5,
                        "title": "Cartilage Evaluation",
                        "description": "Assess articular cartilage surfaces",
                        "duration": "15-25 minutes",
                        "critical_points": [
                            "Cartilage defect mapping",
                            "ICRS classification",
                            "Treatment options"
                        ],
                        "instruments": ["probe", "measuring devices", "documentation tools"]
                    },
                    {
                        "step_number": 6,
                        "title": "Closure and Post-op",
                        "description": "Close portals and apply dressings",
                        "duration": "10-15 minutes",
                        "critical_points": [
                            "Portal closure",
                            "Dressing application",
                            "Post-operative instructions"
                        ],
                        "instruments": ["sutures", "dressings", "compression bandage"]
                    }
                ]
            },

        }
    
    def _load_complications(self) -> Dict:
        """Load complication scenarios"""
        return {
            "bleeding": {
                "severity": ["mild", "moderate", "severe"],
                "locations": ["trocar site", "liver bed", "mesenteric vessel"],
                "management": ["pressure", "electrocautery", "clip application", "conversion"]
            },
            "bowel_injury": {
                "severity": ["serosal", "full_thickness"],
                "locations": ["small bowel", "colon"],
                "management": ["primary repair", "resection", "conversion"]
            },
            "equipment_failure": {
                "type": ["CO2 insufflator", "electrocautery", "camera"],
                "management": ["backup equipment", "troubleshooting", "conversion"]
            }
        }
    
    def generate_scenario(self, procedure_type: str, difficulty_level: str, 
                         patient_profile: Dict, learning_objectives: List[str],
                         complications_enabled: bool = True) -> Dict:
        """Generate complete surgical simulation scenario"""
        
        template = self.procedure_templates.get(procedure_type)
        if not template:
            raise ValueError(f"Procedure type {procedure_type} not supported")
        
        # Customize based on difficulty level
        steps = self._customize_steps_for_difficulty(template['steps'], difficulty_level)
        
        # Add learning objective focus
        steps = self._enhance_steps_for_objectives(steps, learning_objectives)
        
        # Generate potential complications
        complications = []
        if complications_enabled:
            complications = self._generate_complications(procedure_type, difficulty_level)
        
        scenario = {
            "procedure_info": {
                "name": template['name'],
                "category": template['category'],
                "estimated_duration": self._calculate_duration(steps, difficulty_level)
            },
            "steps": steps,
            "complications": complications,
            "learning_objectives": learning_objectives,
            "difficulty_level": difficulty_level,
            "created_at": datetime.now().isoformat()
        }
        
        return scenario
    
    def _customize_steps_for_difficulty(self, base_steps: List[Dict], difficulty: str) -> List[Dict]:
        """Customize procedural steps based on difficulty level"""
        steps = json.loads(json.dumps(base_steps))  # Deep copy
        
        for step in steps:
            if difficulty == "beginner":
                # Add more detailed guidance
                step["guidance_level"] = "detailed"
                step["hints"] = self._generate_beginner_hints(step)
                step["duration"] = self._extend_duration(step["duration"], 1.5)
                
            elif difficulty == "intermediate":
                step["guidance_level"] = "moderate"
                step["decision_points"] = self._add_decision_points(step)
                
            elif difficulty == "advanced":
                step["guidance_level"] = "minimal"
                step["variations"] = self._add_technique_variations(step)
                step["duration"] = self._reduce_duration(step["duration"], 0.8)
                
            elif difficulty == "expert":
                step["guidance_level"] = "none"
                step["time_pressure"] = True
                step["duration"] = self._reduce_duration(step["duration"], 0.7)
        
        return steps
    
    def _generate_beginner_hints(self, step: Dict) -> List[str]:
        """Generate helpful hints for beginner level"""
        hints = [
            f"Take your time with {step['title'].lower()}",
            "Ensure proper visualization before proceeding",
            "Communicate with your team throughout the step"
        ]
        return hints
    
    def _add_decision_points(self, step: Dict) -> List[Dict]:
        """Add decision points for intermediate level"""
        return [
            {
                "scenario": "Unusual anatomy encountered",
                "options": ["Continue with caution", "Seek senior help", "Convert to open"],
                "correct_choice": "Seek senior help"
            }
        ]
    
    def _generate_complications(self, procedure_type: str, difficulty: str) -> List[Dict]:
        """Generate realistic complications for the procedure"""
        complications = []
        
        # Determine complication probability based on difficulty
        prob_map = {
            "beginner": 0.3,
            "intermediate": 0.5, 
            "advanced": 0.7,
            "expert": 0.8
        }
        
        if random.random() < prob_map.get(difficulty, 0.5):
            # Select appropriate complications for procedure
            if procedure_type == "laparoscopic_cholecystectomy":
                possible_complications = ["bleeding", "bowel_injury", "equipment_failure"]
            else:
                possible_complications = ["bleeding", "equipment_failure"]
            
            selected_complication = random.choice(possible_complications)
            complication_data = self.complication_library[selected_complication]
            
            complications.append({
                "type": selected_complication,
                "severity": random.choice(complication_data["severity"]),
                "location": random.choice(complication_data["locations"]),
                "trigger_step": random.randint(2, 5),
                "management_options": complication_data["management"]
            })
        
        return complications
    
    def get_next_step(self, simulation_data: Dict, current_step: int, assessment: Dict) -> Dict:
        """Get next step in simulation based on current progress"""
        steps = simulation_data['simulation']['steps']
        
        if current_step >= len(steps):
            return {"completed": True, "message": "Simulation completed successfully"}
        
        next_step = steps[current_step]
        
        # Check for triggered complications
        complications = simulation_data['simulation']['complications']
        for comp in complications:
            if comp.get('trigger_step') == current_step + 1:
                next_step['complication'] = comp
        
        return next_step
    
    def generate_current_vitals(self, patient: Dict, current_step: int, complications: List[Dict]) -> Dict:
        """Generate realistic patient vitals based on current simulation state"""
        base_vitals = patient['vitals']
        
        # Modify vitals based on procedure progress and complications
        current_vitals = {
            "heart_rate": base_vitals['heart_rate'] + random.randint(-5, 10),
            "blood_pressure": {
                "systolic": base_vitals['blood_pressure']['systolic'] + random.randint(-10, 5),
                "diastolic": base_vitals['blood_pressure']['diastolic'] + random.randint(-5, 5)
            },
            "oxygen_saturation": base_vitals['oxygen_saturation'] + random.randint(-2, 1),
            "temperature": base_vitals['temperature'] + random.uniform(-0.5, 0.3),
            "respiratory_rate": base_vitals['respiratory_rate'] + random.randint(-2, 3)
        }
        
        # Apply complication effects
        for comp in complications:
            if comp['type'] == 'bleeding' and comp['severity'] == 'severe':
                current_vitals['heart_rate'] += 20
                current_vitals['blood_pressure']['systolic'] -= 15
        
        return current_vitals
    
    def generate_dynamic_complication(self, simulation_data: Dict, current_step: int) -> Dict:
        """Generate a dynamic complication during simulation"""
        procedure_type = simulation_data['simulation']['procedure_info']['name']
        
        complications = ["unexpected_bleeding", "adhesions", "equipment_malfunction"]
        selected = random.choice(complications)
        
        complication_scenarios = {
            "unexpected_bleeding": {
                "description": "Unexpected bleeding from hepatic artery branch",
                "severity": "moderate",
                "immediate_actions": [
                    "Apply direct pressure",
                    "Identify bleeding source",
                    "Consider clip application"
                ],
                "time_limit": 300  # 5 minutes
            },
            "adhesions": {
                "description": "Dense adhesions obscuring critical view",
                "severity": "mild",
                "immediate_actions": [
                    "Careful adhesiolysis",
                    "Maintain visualization",
                    "Consider alternative approach"
                ],
                "time_limit": 600  # 10 minutes
            }
        }
        
        return complication_scenarios.get(selected, {})
    
    def _extend_duration(self, duration_str: str, factor: float) -> str:
        """Extend duration by factor"""
        # Parse duration string like "10-15 minutes"
        parts = duration_str.replace(" minutes", "").split("-")
        min_time = int(parts[0]) * factor
        max_time = int(parts[1]) * factor
        return f"{int(min_time)}-{int(max_time)} minutes"
    
    def _reduce_duration(self, duration_str: str, factor: float) -> str:
        """Reduce duration by factor"""
        parts = duration_str.replace(" minutes", "").split("-")
        min_time = int(parts[0]) * factor
        max_time = int(parts[1]) * factor
        return f"{int(min_time)}-{int(max_time)} minutes"
    
    def _calculate_duration(self, steps: List[Dict], difficulty: str) -> int:
        """Calculate total estimated duration"""
        total = 0
        for step in steps:
            duration_str = step['duration']
            avg = sum([int(x) for x in duration_str.replace(" minutes", "").split("-")]) / 2
            total += avg
        
        return int(total)
    
    def _enhance_steps_for_objectives(self, steps: List[Dict], objectives: List[str]) -> List[Dict]:
        """Enhance steps to focus on learning objectives"""
        for step in steps:
            step["learning_focus"] = []
            for objective in objectives:
                if objective.lower() in step['title'].lower() or objective.lower() in step['description'].lower():
                    step["learning_focus"].append(objective)
                    step["assessment_weight"] = 2.0  # Higher weight for objective-focused steps
        
        return steps