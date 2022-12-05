import json
from flask import Flask, render_template, request, redirect, flash, url_for, make_response
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        listOfCompetitions = checkCompetitionIsOver(listOfCompetitions)
        return listOfCompetitions


def checkCompetitionIsOver(listOfCompetitions):
    competitions = []
    for competition in listOfCompetitions:
        competition_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
        competition['over'] = competition_date < datetime.now()
        competitions.append(competition)
    return competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
MAX_PLACES_PER_CLUB = 12
COST_PLACE = 3


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form['email']][0]
        return render_template('welcome.html', club=club, competitions=competitions)
    except IndexError:
        flash("Sorry, that email wasn't found.")
        response = make_response(render_template('index.html'))
        return response, 401


@app.route('/book/<competition>/<club>')
def book(competition, club):
    try:
        foundClub = [c for c in clubs if c['name'] == club][0]
        foundCompetition = [c for c in competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            if not foundCompetition['over']:
                return render_template('booking.html', club=foundClub, competition=foundCompetition)
        flash("Something went wrong-please try again")
        response = make_response(render_template('welcome.html', club=club, competitions=competitions))
        return response, 403
    except IndexError:
        flash("Something went wrong-please try again")
        response = make_response(render_template('index.html', club=club, competitions=competitions))
        return response, 400


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]

    if not competition['over']:
        placesRequired = int(request.form['places'])
        total_points_to_deducted = placesRequired * COST_PLACE
        if total_points_to_deducted <= int(club["points"]):
            if placesRequired <= MAX_PLACES_PER_CLUB:
                competition['numberOfPlaces'] = str(int(competition['numberOfPlaces'])-placesRequired)
                club["points"] = str(int(club["points"]) - total_points_to_deducted)
                flash('Great-booking complete !')
                return render_template('welcome.html', club=club, competitions=competitions)
            else:
                message = "You should book no more than 12 places per competition"
        else:
            message = "You should not book more than yours available points"
    else:
        message = "The competition is over, the booking is closed !"
    flash(message)
    response = make_response(render_template('welcome.html', club=club, competitions=competitions))
    return response, 403


@app.route('/points')
def points():
    return render_template('board_point.html', clubs=clubs)


@app.route('/logout/')
def logout():
    return redirect(url_for('index'))