# Surgical Simulation Platform API Documentation

## Overview

The Surgical Simulation Platform provides a RESTful API for managing surgical simulations, patient profiles, and performance assessments. This document outlines all available endpoints, request/response formats, and usage examples.

## Base URL

- Development: `http://localhost:5000`
- Production: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication for development purposes. In production, consider implementing JWT tokens or API keys.

## Endpoints

### 1. Get Available Procedures

**GET** `/api/procedures`

Returns a list of available surgical procedures with their details.

#### Response

```json
[
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
  }
]
```

#### Example Usage

```bash
curl -X GET http://localhost:5000/api/procedures
```

### 2. Generate Simulation

**POST** `/api/generate-simulation`

Creates a new surgical simulation with a patient profile and scenario.

#### Request Body

```json
{
  "procedure_type": "laparoscopic_cholecystectomy",
  "difficulty_level": "beginner",
  "age_range": [30, 60],
  "gender": "female",
  "learning_objectives": ["trocar_placement", "gallbladder_dissection"],
  "complications_enabled": true,
  "medical_history": ["diabetes", "hypertension"]
}
```

#### Parameters

- `procedure_type` (string, required): Type of surgical procedure
- `difficulty_level` (string, required): Difficulty level (beginner/intermediate/advanced)
- `age_range` (array, optional): Patient age range [min, max]
- `gender` (string, optional): Patient gender (male/female/random)
- `learning_objectives` (array, optional): Specific learning objectives
- `complications_enabled` (boolean, optional): Enable complications in simulation
- `medical_history` (array, optional): Patient medical history

#### Response

```json
{
  "simulation_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": {
    "age": 45,
    "gender": "female",
    "medical_history": ["diabetes", "hypertension"],
    "vitals": {
      "heart_rate": 85,
      "systolic_bp": 140,
      "diastolic_bp": 90,
      "temperature": 37.2,
      "oxygen_saturation": 98
    }
  },
  "simulation": {
    "procedure_type": "laparoscopic_cholecystectomy",
    "difficulty_level": "beginner",
    "steps": [...],
    "complications": [...],
    "learning_objectives": [...]
  },
  "status": "success"
}
```

#### Example Usage

```bash
curl -X POST http://localhost:5000/api/generate-simulation \
  -H "Content-Type: application/json" \
  -d '{
    "procedure_type": "laparoscopic_cholecystectomy",
    "difficulty_level": "beginner",
    "age_range": [30, 60],
    "gender": "female"
  }'
```

### 3. Process Simulation Step

**POST** `/api/simulation/{simulation_id}/step`

Processes a simulation step and provides feedback and next instructions.

#### Request Body

```json
{
  "step_number": 2,
  "actions": [
    {
      "action_type": "incision",
      "location": "umbilical",
      "depth": "superficial",
      "time_taken": 45
    }
  ],
  "time_taken": 120
}
```

#### Parameters

- `step_number` (integer, required): Current step number
- `actions` (array, required): User actions performed
- `time_taken` (integer, required): Time taken for the step in seconds

#### Response

```json
{
  "assessment": {
    "score": 85,
    "feedback": "Good technique with proper depth control",
    "improvements": ["Consider using smaller incision for better cosmesis"],
    "time_score": 90,
    "technique_score": 80
  },
  "next_step": {
    "step_number": 3,
    "instructions": "Insert trocar at 10mm port",
    "expected_actions": ["trocar_insertion"],
    "time_limit": 60,
    "complications": []
  },
  "status": "success"
}
```

#### Example Usage

```bash
curl -X POST http://localhost:5000/api/simulation/550e8400-e29b-41d4-a716-446655440000/step \
  -H "Content-Type: application/json" \
  -d '{
    "step_number": 2,
    "actions": [{"action_type": "incision", "location": "umbilical"}],
    "time_taken": 120
  }'
```

### 4. Get Patient Vitals

**GET** `/api/simulation/{simulation_id}/vitals`

Returns current patient vitals for the simulation.

#### Response

```json
{
  "vitals": {
    "heart_rate": 88,
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "temperature": 37.4,
    "oxygen_saturation": 97,
    "status": "stable"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

#### Example Usage

```bash
curl -X GET http://localhost:5000/api/simulation/550e8400-e29b-41d4-a716-446655440000/vitals
```

### 5. Complete Simulation

**POST** `/api/simulation/{simulation_id}/complete`

Completes the simulation and generates final assessment.

#### Response

```json
{
  "final_assessment": {
    "overall_score": 82,
    "time_score": 85,
    "technique_score": 80,
    "safety_score": 90,
    "feedback": "Overall good performance with room for improvement in technique",
    "recommendations": [
      "Practice trocar placement for better precision",
      "Work on reducing procedure time"
    ],
    "certification_level": "competent"
  },
  "simulation_summary": {
    "total_steps": 8,
    "total_time": 45,
    "complications_handled": 2,
    "patient_outcome": "successful"
  },
  "status": "success"
}
```

#### Example Usage

```bash
curl -X POST http://localhost:5000/api/simulation/550e8400-e29b-41d4-a716-446655440000/complete
```

### 6. Generate Complication

**POST** `/api/complications/generate`

Generates a dynamic complication during simulation.

#### Request Body

```json
{
  "simulation_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_step": 3
}
```

#### Response

```json
{
  "complication": {
    "type": "bleeding",
    "description": "Unexpected bleeding from cystic artery",
    "severity": "moderate",
    "required_actions": ["clamp_artery", "suction_blood"],
    "time_pressure": true,
    "patient_impact": {
      "heart_rate_change": 15,
      "blood_pressure_change": -10
    }
  },
  "status": "success"
}
```

#### Example Usage

```bash
curl -X POST http://localhost:5000/api/complications/generate \
  -H "Content-Type: application/json" \
  -d '{
    "simulation_id": "550e8400-e29b-41d4-a716-446655440000",
    "current_step": 3
  }'
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error description",
  "status": "error",
  "code": 400
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Simulation or resource not found
- `500 Internal Server Error`: Server-side error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Data Types

### Action Types

- `incision`: Surgical incision
- `trocar_insertion`: Inserting trocar
- `dissection`: Tissue dissection
- `clipping`: Vessel clipping
- `suturing`: Wound suturing
- `suction`: Blood/fluid suction

### Complication Types

- `bleeding`: Unexpected bleeding
- `organ_damage`: Accidental organ damage
- `equipment_failure`: Equipment malfunction
- `anesthesia_complication`: Anesthesia-related issues

### Difficulty Levels

- `beginner`: Basic procedures for novices
- `intermediate`: Moderate complexity procedures
- `advanced`: Complex procedures for experienced surgeons

## WebSocket Support

For real-time updates, consider implementing WebSocket connections for:

- Live patient vitals updates
- Real-time feedback during procedures
- Multi-user collaboration features

## SDK Examples

### Python

```python
import requests

class SurgicalSimAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_procedures(self):
        response = requests.get(f"{self.base_url}/api/procedures")
        return response.json()
    
    def generate_simulation(self, config):
        response = requests.post(
            f"{self.base_url}/api/generate-simulation",
            json=config
        )
        return response.json()
    
    def process_step(self, simulation_id, step_data):
        response = requests.post(
            f"{self.base_url}/api/simulation/{simulation_id}/step",
            json=step_data
        )
        return response.json()

# Usage
api = SurgicalSimAPI()
procedures = api.get_procedures()
simulation = api.generate_simulation({
    "procedure_type": "laparoscopic_cholecystectomy",
    "difficulty_level": "beginner"
})
```

### JavaScript

```javascript
class SurgicalSimAPI {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async getProcedures() {
        const response = await fetch(`${this.baseUrl}/api/procedures`);
        return await response.json();
    }
    
    async generateSimulation(config) {
        const response = await fetch(`${this.baseUrl}/api/generate-simulation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        return await response.json();
    }
    
    async processStep(simulationId, stepData) {
        const response = await fetch(`${this.baseUrl}/api/simulation/${simulationId}/step`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(stepData)
        });
        return await response.json();
    }
}

// Usage
const api = new SurgicalSimAPI();
const procedures = await api.getProcedures();
const simulation = await api.generateSimulation({
    procedure_type: 'laparoscopic_cholecystectomy',
    difficulty_level: 'beginner'
});
```

## Versioning

API versioning is handled through URL prefixes. Current version is v1:

- `/api/v1/procedures`
- `/api/v1/generate-simulation`

## Support

For API support and questions:

- Email: support@surgicalsim.com
- Documentation: https://docs.surgicalsim.com
- GitHub Issues: https://github.com/surgicalsim/platform/issues
