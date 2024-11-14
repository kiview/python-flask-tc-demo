import pytest
from testcontainers.postgres import PostgresContainer
from app import create_app, db
from app.models import FastestLap, RaceWinner
import os

@pytest.fixture(scope="function")
def postgres_container():
    with PostgresContainer("postgres:15") as container:
        yield container

@pytest.fixture(scope="function")
def test_app(postgres_container):
    # Get connection details from testcontainer
    db_url = postgres_container.get_connection_url()
    
    # Create test app with container database
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['TESTING'] = True
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()

def test_home_page(test_client):
    """Test that home page loads successfully"""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'F1 Fastest Laps' in response.data

def test_team_stats_page(test_client):
    """Test that team stats page loads successfully"""
    response = test_client.get('/team-stats')
    assert response.status_code == 200
    assert b'Team Performance' in response.data

def test_season_data_flow(test_client, test_app):
    """Test the full flow of selecting a season and getting data"""
    # First request should show form but no data
    response = test_client.get('/')
    assert b'Select Season' in response.data
    assert b'table' not in response.data
    
    # Post request to get season data
    with test_app.app_context():
        response = test_client.post('/', data={'season': '2023'})
        assert response.status_code == 200
        
        # Check if data was stored in database
        laps = FastestLap.query.filter_by(season=2023).all()
        assert len(laps) > 0
        
        # Check if response contains table with data
        assert b'table' in response.data
        assert bytes(laps[0].driver, 'utf-8') in response.data

def test_race_winner_data(test_client, test_app):
    """Test race winner data storage and retrieval"""
    with test_app.app_context():
        # Create some test data
        winner = RaceWinner(
            season=2023,
            race='Test Grand Prix',
            driver='Test Driver',
            team='Test Team'
        )
        db.session.add(winner)
        db.session.commit()
        
        # Check team stats page
        response = test_client.get('/team-stats')
        assert response.status_code == 200
        assert b'Test Team' in response.data

def test_error_handling(test_client):
    """Test error handling for invalid season"""
    response = test_client.post('/', data={'season': '9999'})
    assert response.status_code == 200
    assert b'Error' in response.data

def test_database_constraints(test_app):
    """Test database constraints and model validation"""
    with test_app.app_context():
        # Test required fields
        invalid_lap = FastestLap()
        with pytest.raises(Exception):
            db.session.add(invalid_lap)
            db.session.commit()
            
        # Important: Roll back the failed transaction
        db.session.rollback()
        
        # Test valid data
        valid_lap = FastestLap(
            season=2023,
            race='Test Race',
            driver='Test Driver',
            team='Test Team',
            lap_time='1:23.456',
            lap_number=1
        )
        db.session.add(valid_lap)
        db.session.commit()
        
        # Verify data was saved
        saved_lap = FastestLap.query.filter_by(race='Test Race').first()
        assert saved_lap is not None
        assert saved_lap.driver == 'Test Driver' 