from tests.conftest import request_dataset
import server

class TestIntegration:
    def test_login_and_logout_with_good_email(self, template_info):
        club, competition = request_dataset(0, 0)
        index_template, index_context, index_data = template_info("get", "/")
        assert index_template.name == 'index.html'
        login_template, login_context, login_data = template_info(
                                                "post",
                                                "/showSummary",
                                                data={'email': club['email']})
        assert login_template.name == 'welcome.html'
        assert club['email'] in login_data
        logout_template, logout_context, logout_data = template_info('get', '/logout', follow_redirects=True)
        assert logout_template.name == 'index.html'

    def test_login_and_logout_with_bad_email(self, template_info):
        index_template, index_context, index_data = template_info("get", "/")
        assert index_template.name == 'index.html'
        login_template, login_context, login_data = template_info(
                                                "post",
                                                "/showSummary",
                                                data={'email': 'bad@gmail.com'},
                                                status_code=401)
        assert login_template.name == 'index.html'
        assert "Sorry, that email wasn&#39;t found." in login_data
        logout_template, logout_context, logout_data = template_info('get', '/logout', follow_redirects=True)
        assert logout_template.name == 'index.html'

    def test_login_and_books_places(self, template_info):
        club, competition = request_dataset(0, 0)
        placesRequired = 1
        remaining_places = int(competition["numberOfPlaces"]) - placesRequired
        remaining_points = int(club["points"]) - placesRequired

        index_template, index_context, index_data = template_info("get", "/")
        assert index_template.name == 'index.html'

        login_template, login_context, login_data = template_info(
                                                "post",
                                                "/showSummary",
                                                data={'email': club['email']})
        assert login_template.name == 'welcome.html'
        assert club['email'] in login_data
        assert competition["name"] in login_data
        assert 'Number of Places: ' + competition["numberOfPlaces"] in login_data

        book_template, book_context, book_data = template_info(
                                            'get',
                                            f"/book/{competition['name']}/{club['name']}",
                                            follow_redirects=True)
        assert book_template.name == 'booking.html'
        assert book_context['club'] == club
        assert book_context['competition'] == competition

        purchase_template, purchase_context, purchase_data = template_info(
                                                        "post",
                                                        "/purchasePlaces",
                                                        data={
                                                            "competition": competition['name'],
                                                            "club": club['name'],
                                                            "places": placesRequired
                                                        })
        club['points'] = str(int(club["points"]) - (server.COST_PLACE * placesRequired))
        competition['numberOfPlaces'] = str(remaining_places)
        assert book_context['club'] == club
        assert book_context['competition'] == competition
        assert purchase_template.name == 'welcome.html'
        assert club['email'] in purchase_data
        assert 'Great-booking complete !' in purchase_data
        assert 'Number of Places: ' + str(remaining_places) in purchase_data

    def test_login_and_books_places_with_not_enough_points(self, template_info):
        club, competition = request_dataset(1, 0)
        placesRequired = 3

        index_template, index_context, index_data = template_info("get", "/")
        assert index_template.name == 'index.html'

        login_template, login_context, login_data = template_info(
                                                "post",
                                                "/showSummary",
                                                data={'email': club['email']})
        assert login_template.name == 'welcome.html'
        assert club['email'] in login_data
        assert competition["name"] in login_data
        assert 'Number of Places: ' + competition["numberOfPlaces"] in login_data

        book_template, book_context, book_data = template_info(
                                            'get',
                                            f"/book/{competition['name']}/{club['name']}",
                                            follow_redirects=True)
        assert book_template.name == 'booking.html'
        assert book_context['club'] == club
        assert book_context['competition'] == competition

        purchase_template, purchase_context, purchase_data = template_info(
                                                        "post",
                                                        "/purchasePlaces",
                                                        data={
                                                            "competition": competition['name'],
                                                            "club": club['name'],
                                                            "places": placesRequired
                                                        },
                                                        status_code=403)
        assert book_context['club'] == club
        assert book_context['competition'] == competition
        assert purchase_template.name == 'welcome.html'
        assert club['email'] in purchase_data
        assert 'You should not book more than yours available points' in purchase_data
        assert 'Number of Places: ' + competition["numberOfPlaces"] in purchase_data