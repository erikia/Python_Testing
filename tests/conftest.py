import pytest
import server
from flask import template_rendered
from contextlib import contextmanager
from tests.dataset import Dataset
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


@pytest.fixture(scope="function")
def client():
    app = server.app
    app.config.update({
        "TESTING": True,
    })
    init_data()
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def setup(request):
    server_url = "http://127.0.0.1:5000/"
    print("initiating chrome driver")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(server_url)
    driver.maximize_window()
    request.cls.driver = driver
    yield driver
    driver.close()


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


@pytest.fixture()
def template_info(client):

    def _http_method(method, url, data, **kwargs):
        if method == "post":
            return client.post(url, data=data, **kwargs)
        else:
            return client.get(url, **kwargs)

    def render_template_info(method="get", url=None, data="", status_code=200, **kwargs):

        with captured_templates(server.app) as templates:
            response = _http_method(method, url, data, **kwargs)
            assert response.status_code == status_code
            assert len(templates) == 1
            data = response.data.decode()
            template, context = templates[0]
            return template, context, data

    return render_template_info


def init_data():
    dataset = Dataset()
    server.clubs = dataset.clubs['clubs']
    server.competitions = dataset.competitions["competitions"]
    server.MAX_PLACES_PER_CLUB = dataset.max_places_per_club
    server.COST_PLACE = dataset.cost_place


def request_dataset(index_club, index_competition):
    dataset = Dataset()
    club = dataset.clubs["clubs"][index_club]
    competition = dataset.competitions["competitions"][index_competition]
    return club, competition

