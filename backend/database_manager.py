import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
import os

class DatabaseManager:
    def __init__(self, db_path: str = "surgical_simulations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simulations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulations (
                id TEXT PRIMARY KEY,
                procedure_type TEXT NOT NULL,
                difficulty_level TEXT NOT NULL,
                patient_data TEXT NOT NULL,
                simulation_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Step assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                technical_score REAL NOT NULL,
                non_technical_score REAL NOT NULL,
                overall_score REAL NOT NULL,
                time_taken INTEGER NOT NULL,
                user_actions TEXT NOT NULL,
                feedback TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations (id)
            )
        ''')
        
        # Complications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id TEXT NOT NULL,
                complication_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                trigger_step INTEGER NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_time INTEGER NULL,
                management_actions TEXT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id TEXT NULL,
                simulation_id TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP NULL,
                session_data TEXT NULL,
                FOREIGN KEY (simulation_id) REFERENCES simulations (id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                simulation_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_data TEXT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (simulation_id) REFERENCES simulations (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_simulation(self, simulation_id: str, simulation_data: Dict, 
                       patient_data: Dict) -> bool:
        """Save a new simulation to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO simulations 
                (id, procedure_type, difficulty_level, patient_data, simulation_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                simulation_id,
                simulation_data['procedure_info']['name'],
                simulation_data['difficulty_level'],
                json.dumps(patient_data),
                json.dumps(simulation_data)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving simulation: {e}")
            return False
    
    def get_simulation(self, simulation_id: str) -> Dict:
        """Retrieve simulation data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT patient_data, simulation_data, status
            FROM simulations WHERE id = ?
        ''', (simulation_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            patient_data = json.loads(result[0])
            simulation_data = json.loads(result[1])
            
            # Get step assessments
            step_assessments = self.get_step_assessments(simulation_id)
            
            # Merge simulation data with additional fields
            merged_data = {
                **simulation_data,
                "simulation_id": simulation_id,
                "patient": patient_data,
                "status": result[2],
                "step_assessments": step_assessments,
                "current_step": len(step_assessments)
            }
            
            return merged_data
        
        return {}
    
    def update_simulation_progress(self, simulation_id: str, step_number: int,
                                 assessment: Dict, user_actions: List[Dict]) -> bool:
        """Update simulation progress with step assessment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO step_assessments 
                (simulation_id, step_number, technical_score, non_technical_score,
                 overall_score, time_taken, user_actions, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                simulation_id,
                step_number,
                assessment['technical_score'],
                assessment['non_technical_score'],
                assessment['overall_score'],
                assessment['time_taken'],
                json.dumps(user_actions),
                json.dumps(assessment['feedback'])
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating simulation progress: {e}")
            return False
    
    def get_step_assessments(self, simulation_id: str) -> List[Dict]:
        """Get all step assessments for a simulation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT step_number, technical_score, non_technical_score, 
                   overall_score, time_taken, user_actions, feedback, timestamp
            FROM step_assessments 
            WHERE simulation_id = ?
            ORDER BY step_number
        ''', (simulation_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in results:
            assessments.append({
                "step_number": row[0],
                "technical_score": row[1],
                "non_technical_score": row[2],
                "overall_score": row[3],
                "time_taken": row[4],
                "user_actions": json.loads(row[5]),
                "feedback": json.loads(row[6]),
                "timestamp": row[7]
            })
        
        return assessments
    
    def add_complication(self, simulation_id: str, complication: Dict) -> bool:
        """Add a complication to the simulation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO complications 
                (simulation_id, complication_type, severity, trigger_step, management_actions)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                simulation_id,
                complication['type'],
                complication['severity'],
                complication.get('trigger_step', 0),
                json.dumps(complication.get('management_options', []))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding complication: {e}")
            return False
    
    def complete_simulation(self, simulation_id: str, final_assessment: Dict) -> bool:
        """Mark simulation as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE simulations 
                SET completed_at = CURRENT_TIMESTAMP, status = 'completed'
                WHERE id = ?
            ''', (simulation_id,))
            
            # Save final assessment as performance metric
            cursor.execute('''
                INSERT INTO performance_metrics
                (simulation_id, metric_name, metric_value, metric_data)
                VALUES (?, ?, ?, ?)
            ''', (
                simulation_id,
                "final_assessment",
                final_assessment['scores']['overall_average'],
                json.dumps(final_assessment)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error completing simulation: {e}")
            return False
    
    def get_user_statistics(self, user_id: str = None) -> Dict:
        """Get user performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get completed simulations
        if user_id:
            cursor.execute('''
                SELECT s.procedure_type, s.difficulty_level, pm.metric_value
                FROM simulations s
                JOIN performance_metrics pm ON s.id = pm.simulation_id
                JOIN user_sessions us ON s.id = us.simulation_id
                WHERE s.status = 'completed' AND us.user_id = ?
                AND pm.metric_name = 'final_assessment'
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT s.procedure_type, s.difficulty_level, pm.metric_value
                FROM simulations s
                JOIN performance_metrics pm ON s.id = pm.simulation_id
                WHERE s.status = 'completed'
                AND pm.metric_name = 'final_assessment'
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"message": "No completed simulations found"}
        
        # Analyze statistics
        total_simulations = len(results)
        avg_score = sum(row[2] for row in results) / total_simulations
        
        procedure_stats = {}
        for row in results:
            procedure = row[0]
            if procedure not in procedure_stats:
                procedure_stats[procedure] = {"count": 0, "scores": []}
            procedure_stats[procedure]["count"] += 1
            procedure_stats[procedure]["scores"].append(row[2])
        
        # Calculate averages per procedure
        for proc, stats in procedure_stats.items():
            stats["average_score"] = sum(stats["scores"]) / len(stats["scores"])
        
        return {
            "total_simulations": total_simulations,
            "overall_average": round(avg_score, 1),
            "procedure_breakdown": procedure_stats,
            "last_updated": datetime.now().isoformat()
        }
    
    def cleanup_old_simulations(self, days_old: int = 30) -> int:
        """Clean up simulations older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor.execute('''
                DELETE FROM simulations 
                WHERE created_at < ? AND status = 'completed'
            ''', (cutoff_date.isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up simulations: {e}")
            return 0