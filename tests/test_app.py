import json
import pytest


@pytest.fixture
def app_instance():
    from app import app, db, create_default_admin
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
        'SECRET_KEY': 'test-key'
    })
    with app.app_context():
        db.create_all()
        create_default_admin()
    yield app


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def login(client, username='admin', password='admin123'):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_admin_login_success(client):
    resp = login(client)
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data or b'Admin Dashboard' in resp.data


def test_admin_dashboard_access(client):
    login(client)
    resp = client.get('/admin_dashboard')
    assert resp.status_code == 200
    assert b'Admin Dashboard' in resp.data


def test_start_simulation_endpoint(client):
    login(client)
    resp = client.post('/start_simulation', data={
        'simulation_duration': '10',
        'request_interval': '1',
        'cache_size': '5',
        'content_catalog_size': '10',
        'user_count': '2',
        'log_interval': '5'
    })
    assert resp.status_code == 200
    payload = json.loads(resp.data)
    assert payload.get('success') is True
    assert isinstance(payload.get('session_id'), int)


def test_simulation_status_and_results(client, monkeypatch):
    # Force simulation_state to completed and set minimal satellite data
    from app import simulation_state
    class DummySatellite:
        def __init__(self):
            self.request_log = []
            self.performance_log = []
        def get_final_statistics(self):
            return {'total_requests': 0}
    simulation_state['running'] = False
    simulation_state['satellite'] = DummySatellite()

    login(client)
    status_resp = client.get('/simulation_status')
    assert status_resp.status_code == 200
    assert status_resp.json['status'] in ['running', 'completed']

    results_resp = client.get('/simulation_results')
    assert results_resp.status_code == 200
    assert 'statistics' in results_resp.json


def test_analytics_api(client):
    login(client)
    resp = client.get('/api/analytics')
    assert resp.status_code == 200
    data = resp.get_json()
    for key in ['total_users', 'total_sessions', 'completed_sessions', 'users_over_time', 'sessions_over_time']:
        assert key in data


