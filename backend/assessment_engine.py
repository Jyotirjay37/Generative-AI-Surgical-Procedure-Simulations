import json
import random
from typing import Dict, List, Any
from datetime import datetime

class AssessmentEngine:
    def __init__(self):
        self.scoring_criteria = self._load_scoring_criteria()
        self.feedback_templates = self._load_feedback_templates()
    
    def _load_scoring_criteria(self) -> Dict:
        """Load assessment criteria for different procedures"""
        return {
            "laparoscopic_cholecystectomy": {
                "technical_skills": {
                    "trocar_placement": {"max_score": 20, "weight": 0.15},
                    "camera_navigation": {"max_score": 15, "weight": 0.10},
                    "tissue_handling": {"max_score": 25, "weight": 0.20},
                    "critical_view_achievement": {"max_score": 30, "weight": 0.25},
                    "dissection_technique": {"max_score": 25, "weight": 0.20},
                    "hemostasis": {"max_score": 15, "weight": 0.10}
                },
                "non_technical_skills": {
                    "communication": {"max_score": 20, "weight": 0.30},
                    "decision_making": {"max_score": 25, "weight": 0.35},
                    "time_management": {"max_score": 20, "weight": 0.20},
                    "team_leadership": {"max_score": 15, "weight": 0.15}
                }
            },
            "appendectomy": {
                "technical_skills": {
                    "appendix_identification": {"max_score": 25, "weight": 0.25},
                    "mesoappendix_division": {"max_score": 30, "weight": 0.30},
                    "base_division": {"max_score": 25, "weight": 0.25},
                    "specimen_removal": {"max_score": 20, "weight": 0.20}
                },
                "non_technical_skills": {
                    "communication": {"max_score": 20, "weight": 0.30},
                    "decision_making": {"max_score": 25, "weight": 0.35},
                    "situational_awareness": {"max_score": 20, "weight": 0.35}
                }
            }
        }
    
    def _load_feedback_templates(self) -> Dict:
        """Load feedback message templates"""
        return {
            "excellent": [
                "Outstanding technique demonstrated",
                "Perfect execution of critical steps",
                "Excellent decision-making under pressure"
            ],
            "good": [
                "Good technique with minor areas for improvement",
                "Solid understanding of procedure demonstrated",
                "Appropriate response to complications"
            ],
            "needs_improvement": [
                "Technique needs refinement in key areas", 
                "Consider additional practice on critical steps",
                "Review anatomical landmarks and approach"
            ],
            "poor": [
                "Significant technical errors identified",
                "Safety concerns with current approach",
                "Requires substantial additional training"
            ]
        }
    
    def assess_step(self, simulation_data: Dict, step_number: int, 
                   user_actions: List[Dict], time_taken: int) -> Dict:
        """Assess performance on a single simulation step"""
        
        procedure_type = simulation_data['simulation']['procedure_info']['name'].lower().replace(" ", "_")
        current_step = simulation_data['simulation']['steps'][step_number - 1]
        
        # Technical skill assessment
        technical_score = self._assess_technical_skills(
            procedure_type, current_step, user_actions, time_taken
        )
        
        # Non-technical skill assessment  
        non_technical_score = self._assess_non_technical_skills(
            current_step, user_actions, time_taken
        )
        
        # Overall step score
        overall_score = (technical_score * 0.7) + (non_technical_score * 0.3)
        
        # Generate feedback
        feedback = self._generate_step_feedback(
            overall_score, technical_score, non_technical_score, 
            current_step, user_actions
        )
        
        return {
            "step_number": step_number,
            "technical_score": technical_score,
            "non_technical_score": non_technical_score,
            "overall_score": overall_score,
            "feedback": feedback,
            "time_taken": time_taken,
            "timestamp": datetime.now().isoformat(),
            "areas_for_improvement": self._identify_improvement_areas(
                technical_score, non_technical_score, user_actions
            )
        }
    
    def _assess_technical_skills(self, procedure_type: str, step: Dict, 
                                actions: List[Dict], time_taken: int) -> float:
        """Assess technical skill performance"""
        if procedure_type not in self.scoring_criteria:
            return 0.0
        
        criteria = self.scoring_criteria[procedure_type]["technical_skills"]
        total_score = 0.0
        total_weight = 0.0
        
        # Assess each relevant technical skill for this step
        for skill, scoring in criteria.items():
            if self._is_skill_relevant_to_step(skill, step):
                skill_score = self._score_technical_skill(skill, actions, time_taken)
                weighted_score = skill_score * scoring["weight"]
                total_score += weighted_score
                total_weight += scoring["weight"]
        
        return (total_score / total_weight * 100) if total_weight > 0 else 0.0
    
    def _assess_non_technical_skills(self, step: Dict, actions: List[Dict], 
                                   time_taken: int) -> float:
        """Assess non-technical skills (communication, decision-making, etc.)"""
        scores = []
        
        # Communication assessment
        communication_score = self._assess_communication(actions)
        scores.append(communication_score * 0.30)
        
        # Decision-making assessment
        decision_score = self._assess_decision_making(actions, step)
        scores.append(decision_score * 0.35)
        
        # Time management assessment
        time_score = self._assess_time_management(time_taken, step)
        scores.append(time_score * 0.20)
        
        # Situational awareness assessment
        awareness_score = self._assess_situational_awareness(actions)
        scores.append(awareness_score * 0.15)
        
        return sum(scores)
    
    def _score_technical_skill(self, skill: str, actions: List[Dict], time_taken: int) -> float:
        """Score a specific technical skill"""
        score = 0.0
        
        # Analyze actions for skill-specific performance
        for action in actions:
            if skill in action.get('skill_category', '').lower():
                # Score based on action quality
                if action.get('accuracy', 0) > 0.8:
                    score += 20
                elif action.get('accuracy', 0) > 0.6:
                    score += 15
                else:
                    score += 5
                
                # Penalize for excessive time
                expected_time = action.get('expected_time', 300)
                if time_taken > expected_time * 1.5:
                    score *= 0.8
        
        return min(score, 100.0)
    
    def _assess_communication(self, actions: List[Dict]) -> float:
        """Assess communication effectiveness"""
        communication_actions = [a for a in actions if a.get('type') == 'communication']
        
        if not communication_actions:
            return 50.0  # Neutral score for no communication tracked
        
        score = 0.0
        for comm in communication_actions:
            if comm.get('clarity', 0) > 0.8:
                score += 25
            if comm.get('timing', 0) > 0.8:
                score += 25
            if comm.get('professionalism', 0) > 0.8:
                score += 25
        
        return min(score, 100.0)
    
    def _assess_decision_making(self, actions: List[Dict], step: Dict) -> float:
        """Assess decision-making quality"""
        decision_actions = [a for a in actions if a.get('type') == 'decision']
        
        if not decision_actions:
            return 70.0  # Default score if no decisions tracked
        
        correct_decisions = 0
        total_decisions = len(decision_actions)
        
        for decision in decision_actions:
            if decision.get('outcome') == 'correct':
                correct_decisions += 1
            elif decision.get('outcome') == 'safe_alternative':
                correct_decisions += 0.7
        
        return (correct_decisions / total_decisions * 100) if total_decisions > 0 else 70.0
    
    def _assess_time_management(self, time_taken: int, step: Dict) -> float:
        """Assess time management effectiveness"""
        # Parse expected duration
        duration_str = step.get('duration', '10-15 minutes')
        duration_parts = duration_str.replace(' minutes', '').split('-')
        expected_min = int(duration_parts[0]) * 60  # Convert to seconds
        expected_max = int(duration_parts[1]) * 60
        
        if expected_min <= time_taken <= expected_max:
            return 100.0
        elif time_taken < expected_min:
            # Too fast might indicate rushing
            return max(70.0, 100.0 - (expected_min - time_taken) / expected_min * 30)
        else:
            # Too slow
            return max(30.0, 100.0 - (time_taken - expected_max) / expected_max * 50)
    
    def _assess_situational_awareness(self, actions: List[Dict]) -> float:
        """Assess situational awareness"""
        awareness_indicators = [
            'monitors_vitals', 'checks_equipment', 'communicates_status',
            'identifies_complications', 'requests_assistance'
        ]
        
        score = 70.0  # Base score
        for action in actions:
            action_type = action.get('type', '')
            if any(indicator in action_type for indicator in awareness_indicators):
                score += 10
        
        return min(score, 100.0)
    
    def _is_skill_relevant_to_step(self, skill: str, step: Dict) -> bool:
        """Check if a skill is relevant to the current step"""
        step_title = step['title'].lower()
        step_desc = step['description'].lower()
        
        skill_keywords = {
            'trocar_placement': ['trocar', 'insertion', 'pneumoperitoneum'],
            'camera_navigation': ['laparoscopy', 'visualization', 'camera'],
            'tissue_handling': ['dissection', 'grasping', 'manipulation'],
            'critical_view_achievement': ['critical view', 'safety', 'triangle'],
            'dissection_technique': ['dissect', 'separate', 'divide'],
            'hemostasis': ['bleeding', 'clip', 'cautery', 'hemostasis']
        }
        
        if skill in skill_keywords:
            keywords = skill_keywords[skill]
            return any(keyword in step_title or keyword in step_desc for keyword in keywords)
        
        return False
    
    def _generate_step_feedback(self, overall_score: float, technical_score: float,
                               non_technical_score: float, step: Dict, 
                               actions: List[Dict]) -> Dict:
        """Generate detailed feedback for the step"""
        
        # Determine performance level
        if overall_score >= 90:
            level = "excellent"
        elif overall_score >= 75:
            level = "good"
        elif overall_score >= 60:
            level = "needs_improvement"
        else:
            level = "poor"
        
        # Generate specific feedback messages
        feedback = {
            "overall_level": level,
            "summary": random.choice(self.feedback_templates[level]),
            "technical_feedback": self._generate_technical_feedback(technical_score, actions),
            "non_technical_feedback": self._generate_non_technical_feedback(non_technical_score),
            "recommendations": self._generate_recommendations(overall_score, step)
        }
        
        return feedback
    
    def _generate_technical_feedback(self, score: float, actions: List[Dict]) -> str:
        """Generate technical skill feedback"""
        if score >= 85:
            return "Excellent technical execution with proper instrument handling and surgical technique."
        elif score >= 70:
            return "Good technical skills demonstrated with room for refinement in precision."
        elif score >= 55:
            return "Technical skills need improvement. Focus on instrument control and anatomical identification."
        else:
            return "Significant technical deficiencies identified. Additional practice and supervision recommended."
    
    def _generate_non_technical_feedback(self, score: float) -> str:
        """Generate non-technical skill feedback"""
        if score >= 85:
            return "Outstanding communication and decision-making throughout the procedure."
        elif score >= 70:
            return "Good team interaction and appropriate clinical decisions made."
        elif score >= 55:
            return "Communication and decision-making skills need development."
        else:
            return "Poor team communication and questionable clinical decisions observed."
    
    def _generate_recommendations(self, score: float, step: Dict) -> List[str]:
        """Generate specific recommendations for improvement"""
        recommendations = []
        
        if score < 70:
            recommendations.extend([
                f"Review {step['title'].lower()} technique in textbook",
                "Practice on simulation models before next attempt",
                "Seek mentorship for technique refinement"
            ])
        
        if score < 85:
            recommendations.extend([
                "Focus on smooth, deliberate movements",
                "Improve communication with surgical team"
            ])
        
        return recommendations
    
    def _identify_improvement_areas(self, technical_score: float, 
                                  non_technical_score: float, 
                                  actions: List[Dict]) -> List[str]:
        """Identify specific areas needing improvement"""
        areas = []
        
        if technical_score < 70:
            areas.append("Technical Skills")
        if non_technical_score < 70:
            areas.append("Communication & Decision Making")
        
        # Analyze specific action patterns
        if any(a.get('hesitation_time', 0) > 30 for a in actions):
            areas.append("Confidence & Decision Speed")
        
        if any(a.get('accuracy', 1.0) < 0.6 for a in actions):
            areas.append("Precision & Accuracy")
        
        return areas
    
    def generate_final_assessment(self, simulation_data: Dict) -> Dict:
        """Generate comprehensive final assessment"""
        
        # Collect all step assessments
        step_assessments = simulation_data.get('step_assessments', [])
        
        if not step_assessments:
            return {"error": "No step assessments found"}
        
        # Calculate overall scores
        technical_scores = [a['technical_score'] for a in step_assessments]
        non_technical_scores = [a['non_technical_score'] for a in step_assessments]
        overall_scores = [a['overall_score'] for a in step_assessments]
        
        avg_technical = sum(technical_scores) / len(technical_scores)
        avg_non_technical = sum(non_technical_scores) / len(non_technical_scores)
        avg_overall = sum(overall_scores) / len(overall_scores)
        
        # Calculate total time
        total_time = sum(a['time_taken'] for a in step_assessments)
        
        # Generate performance trends
        trends = self._analyze_performance_trends(step_assessments)
        
        # Generate comprehensive feedback
        final_feedback = self._generate_final_feedback(
            avg_overall, trends, simulation_data
        )
        
        # Generate learning recommendations
        learning_plan = self._generate_learning_plan(
            avg_technical, avg_non_technical, trends
        )
        
        return {
            "simulation_id": simulation_data.get('simulation_id'),
            "completion_date": datetime.now().isoformat(),
            "scores": {
                "technical_average": round(avg_technical, 1),
                "non_technical_average": round(avg_non_technical, 1), 
                "overall_average": round(avg_overall, 1),
                "individual_steps": [
                    {
                        "step": a['step_number'],
                        "score": a['overall_score'],
                        "time": a['time_taken']
                    } for a in step_assessments
                ]
            },
            "performance_metrics": {
                "total_time_minutes": round(total_time / 60, 1),
                "complications_handled": len([
                    a for a in step_assessments 
                    if 'complication' in a.get('feedback', {}).get('summary', '')
                ]),
                "safety_violations": self._count_safety_violations(step_assessments),
                "efficiency_rating": self._calculate_efficiency(total_time, simulation_data)
            },
            "trends": trends,
            "final_feedback": final_feedback,
            "learning_plan": learning_plan,
            "certification_eligible": avg_overall >= 75,
            "next_difficulty_ready": avg_overall >= 85
        }
    
    def _analyze_performance_trends(self, assessments: List[Dict]) -> Dict:
        """Analyze performance trends across steps"""
        scores = [a['overall_score'] for a in assessments]
        
        # Calculate trend direction
        if len(scores) > 1:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 5:
                trend = "improving"
            elif avg_second < avg_first - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "direction": trend,
            "consistency": self._calculate_consistency(scores),
            "peak_performance_step": scores.index(max(scores)) + 1,
            "lowest_performance_step": scores.index(min(scores)) + 1
        }
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate performance consistency"""
        if len(scores) < 2:
            return 100.0
        
        variance = sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency percentage (lower std_dev = higher consistency)
        consistency = max(0, 100 - (std_dev * 2))
        return round(consistency, 1)
    
    def _generate_final_feedback(self, overall_score: float, trends: Dict, 
                                simulation_data: Dict) -> Dict:
        """Generate comprehensive final feedback"""
        procedure_name = simulation_data['simulation']['procedure_info']['name']
        difficulty = simulation_data['simulation']['difficulty_level']
        
        if overall_score >= 90:
            performance_level = "Outstanding"
            message = f"Exceptional performance on {procedure_name} at {difficulty} level."
        elif overall_score >= 75:
            performance_level = "Proficient"
            message = f"Good performance on {procedure_name} with areas for refinement."
        elif overall_score >= 60:
            performance_level = "Developing"
            message = f"Developing skills demonstrated. Continue practice on {procedure_name}."
        else:
            performance_level = "Novice"
            message = f"Foundational skills need development before attempting {procedure_name}."
        
        return {
            "performance_level": performance_level,
            "summary_message": message,
            "trend_analysis": f"Performance trend: {trends['direction']}",
            "consistency_note": f"Consistency rating: {trends['consistency']}%"
        }
    
    def _generate_learning_plan(self, technical_avg: float, non_technical_avg: float,
                               trends: Dict) -> Dict:
        """Generate personalized learning plan"""
        plan = {
            "immediate_focus": [],
            "practice_recommendations": [],
            "next_steps": []
        }
        
        # Technical skill focus
        if technical_avg < 70:
            plan["immediate_focus"].append("Technical Skill Development")
            plan["practice_recommendations"].extend([
                "Practice basic laparoscopic skills on trainer",
                "Review anatomical landmarks",
                "Work on instrument handling precision"
            ])
        
        # Non-technical skill focus
        if non_technical_avg < 70:
            plan["immediate_focus"].append("Communication & Decision Making")
            plan["practice_recommendations"].extend([
                "Practice team communication scenarios",
                "Review decision-making frameworks",
                "Participate in team-based simulations"
            ])
        
        # Next steps based on overall performance
        if technical_avg >= 85 and non_technical_avg >= 85:
            plan["next_steps"].append("Ready for increased difficulty level")
            plan["next_steps"].append("Consider mentoring junior trainees")
        elif technical_avg >= 75 and non_technical_avg >= 75:
            plan["next_steps"].append("Practice additional procedure variations")
            plan["next_steps"].append("Focus on efficiency improvements")
        else:
            plan["next_steps"].append("Repeat current difficulty level")
            plan["next_steps"].append("Seek additional supervision")
        
        return plan
    
    def _count_safety_violations(self, assessments: List[Dict]) -> int:
        """Count safety violations across all steps"""
        violations = 0
        for assessment in assessments:
            feedback = assessment.get('feedback', {})
            if 'safety' in feedback.get('summary', '').lower():
                violations += 1
        return violations
    
    def _calculate_efficiency(self, total_time: int, simulation_data: Dict) -> str:
        """Calculate efficiency rating"""
        expected_duration = simulation_data['simulation']['procedure_info'].get('estimated_duration', 60) * 60
        
        if total_time <= expected_duration:
            return "Excellent"
        elif total_time <= expected_duration * 1.2:
            return "Good"
        elif total_time <= expected_duration * 1.5:
            return "Acceptable"
        else:
            return "Needs Improvement"