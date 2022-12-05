from server import loadClubs, loadCompetitions
import server
import json
from tests.conftest import request_dataset
from tests.dataset import Dataset

class TestLogout:

    def test_should_status_code_redirect(self, client):
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        data = response.data.decode()
        assert "<title>GUDLFT Registration</title>" in data


class TestIndex:

    def test_index_should_status_code_ok_with_good_templates(self, template_info):
        template, context, data = template_info("get", '/')
        assert template.name == 'index.html'


class TestPointsBoardt:

    def test_should_display_points_board_point(self, template_info):

        template, context, data = template_info(method="get", url='/points')
        assert template.name == 'board_point.html'
        assert "Clubs" in data
        assert "Points" in data
        assert "<table>" in data


class TestJson:

    def test_loadClubs_should_get_clubs_data(self, monkeypatch):

        def mock_get(*args, **kwargs):
            return Dataset().clubs

        monkeypatch.setattr(json, "load", mock_get)
        result = loadClubs()
        assert result == Dataset().clubs["clubs"]

    def test_loadCompetition_should_get_competitions_data(self, monkeypatch):

        def mock_get(*args, **kwargs):
            return Dataset().competitions

        monkeypatch.setattr(json, "load", mock_get)
        result = loadCompetitions()
        assert result == Dataset().competitions["competitions"]


class TestShowSummary:

    def test_showsummary_should_status_code_ok_with_good_template(self, template_info):
        club, competition = request_dataset(0, 0)
        template, context, data = template_info(
                            "post",
                            '/showSummary',
                            data={'email': club['email']})
        assert template.name == 'welcome.html'

    def test_showsummary_should_redirect_to_index_if_unknow_email(self, template_info):
        template, context, data = template_info(
                            "post",
                            '/showSummary',
                            data={'email': 'bad@simplylift.co'},
                            status_code=401)
        assert template.name == 'index.html'
        assert "<li>Sorry, that email wasn&#39;t found.</li>" in data

    def test_showsummary_should_undisplayed_booking_when_competition_is_over(self, client):
        club, competition = request_dataset(0, 0)
        response = client.post(
            '/showSummary',
            data={'email': club['email']},
            follow_redirects=True)
        data = response.data.decode()
        assert "<a href=\"/book/Fall%20Classic/Simply%20Lift\">Book Places</a>" not in data


class TestBook:

    def test_book_should_status_code_ok_with_good_template(self, template_info):
        club, competition = request_dataset(0, 0)
        template, context, data = template_info(
                            "get",
                            f"/book/{competition['name']}/{club['name']}")
        assert template.name == 'booking.html'

    def test_book_should_redirect_to_welcome_if_bad_url(self, template_info):

        template, context, data = template_info(
                            "get",
                            "/book/wrong/bad",
                            status_code=400)
        assert template.name == 'index.html'
        assert "Something went wrong-please try again" in data

    def test_book_should_no_reservation_when_competition_is_over(self, template_info):
        club, competition = request_dataset(0, 1)
        template, context, data = template_info(
                            "get",
                            f"/book/{competition['name']}/{club['name']}",
                            status_code=403)
        assert template.name == 'welcome.html'
        assert "Something went wrong-please try again" in data


class TestPurchasePlaces:

    def test_should_status_code_ok_with_good_template(self, template_info):
        club, competition = request_dataset(0, 0)
        placesRequired = 1
        template, context, data = template_info(
                            "post",
                            "/purchasePlaces",
                            data={
                                "competition": competition['name'],
                                "club": club['name'],
                                "places": placesRequired
                            })

        assert template.name == 'welcome.html'

    def test_should_redirect_to_welcome_if_booking_is_more_than_available_points(self, client):
        club, competition = request_dataset(1, 0)
        placesRequired = 3
        rv = client.post(
            '/purchasePlaces',
            data={
                "competition": competition['name'],
                "club": club['name'],
                "places": placesRequired},
            follow_redirects=True)
        assert rv.status_code == 403
        data = rv.data.decode()
        assert "You should not book more than yours available points" in data

    def test_should_redirect_to_welcome_if_club_books_more_than_12_places(self, client):
        server.COST_PLACE = 1
        club, competition = request_dataset(0, 0)
        placesRequired = 13
        rv = client.post(
            '/purchasePlaces',
            data={
                "competition": competition['name'],
                "club": club['name'],
                "places": placesRequired},
            follow_redirects=True)
        assert rv.status_code == 403
        data = rv.data.decode()
        assert "You should book no more than 12 places per competition" in data

    def test_should_redirect_to_welcome_if_club_books_on_past_competition(self, client):
        club, competition = request_dataset(0, 1)
        placesRequired = 1
        rv = client.post(
            '/purchasePlaces',
            data={
                "competition": competition['name'],
                "club": club['name'],
                "places": placesRequired},
            follow_redirects=True)
        assert rv.status_code == 403
        data = rv.data.decode()
        assert "The competition is over, the booking is closed !" in data

    def test_should_deducted_points_of_clubs_balance(self, template_info):
        club, competition = request_dataset(0, 0)
        placesRequired = 1
        expected = int(club["points"]) - (server.COST_PLACE * placesRequired)
        template, context, data = template_info(
                            method="post",
                            url='/purchasePlaces',
                            data={
                                "competition": competition['name'],
                                "club": club['name'],
                                "places": placesRequired},
                            status_code=200)
        assert context["club"]["points"] == str(expected)



