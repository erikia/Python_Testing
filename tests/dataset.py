class Dataset:
    def __init__(self):
        self.clubs = {"clubs": [
            {
                "name": "Simply Lift",
                "email": "john@simplylift.co",
                "points": "15"
            },
            {
                "name": "Iron Temple",
                "email": "admin@irontemple.com",
                "points": "4"
            }
        ]}

        self.competitions = {"competitions": [
                {
                    "name": "Spring Festival",
                    "date": "2023-03-27 10:00:00",
                    "numberOfPlaces": "25",
                    "over": False
                },
                {
                    "name": "Fall Classic",
                    "date": "2020-10-22 13:30:00",
                    "numberOfPlaces": "13",
                    "over": True
                }
        ]}
        self.cost_place = 2
        self.max_places_per_club = 12