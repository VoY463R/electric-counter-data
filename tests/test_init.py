import pytest
from init import app, db, save_data_to_csv, parse_saving_request, save_energy_data
from datetime import datetime
from flask import session, request
import csv
import os
from models import DataSaved
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "test_secret_key"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_save_data_to_csv():
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    filename = "test_data.csv"

    save_data_to_csv(data, filename)
    assert os.path.exists(filename)

    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["age"] == "25"

    os.remove(filename)

def test_parse_saving_request(client):
    response = client.get('/saving?down_time=2023-01-01%2000:00:00&up_time=2023-01-01%2012:00:00&used_elec=100')
    assert response.status_code == 302

def test_save_energy_data(client):
    down_time = datetime(2024, 1, 1, 0, 0, 0)
    up_time = datetime(2024, 1, 1, 12, 0, 0)
    used_elec = 100

    with app.app_context():
        save_energy_data(down_time, up_time, used_elec)

        saved_data = DataSaved.query.first()
        assert saved_data.low_date == down_time
        assert saved_data.high_date == up_time
        assert saved_data.used_energy == used_elec
        


def test_login(client):
    response = client.post('/', data={
        'username': 'testuser',
        'password': 'testpassword',

    })
    
    assert response.status_code == 200
    assert response.headers['Location'] == '/dashboard'
    
def test_firebase(client):
    response = client.get('/firebase', follow_redirects=True)

    assert response.status_code == 200