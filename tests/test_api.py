import pytest
import json
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_procedures_endpoint(client):
    response = client.get('/api/procedures')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_generate_simulation(client):
    config = {
        "procedure_type": "laparoscopic_cholecystectomy",
        "difficulty_level": "beginner",
        "age_range": [30, 60],
        "gender": "female",
        "learning_objectives": ["trocar_placement"],
        "complications_enabled": True
    }
    
    response = client.post('/api/generate-simulation', 
                          data=json.dumps(config),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'