import json
from flask import (
    Flask, render_template, request,
    redirect, flash, url_for
)


def loadClubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def loadCompetitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next(
        (club for club in clubs if club['email'] == email), None
    )
    if club:
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )
    else:
        flash("Désolé, l'email n'est pas reconnu. Veuillez réessayer.")
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions
                         if c['name'] == competition][0]
    if found_club and found_competition:
        return render_template(
            'booking.html',
            club=found_club,
            competition=found_competition
        )
    else:
        flash("Something went wrong-please try again.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions
         if c['name'] == request.form['competition']),
        None
    )
    club = next(
        (c for c in clubs if c['name'] == request.form['club']),
        None
    )

    if not competition or not club:
        flash("Something went wrong-please try again.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    places_required = int(request.form['places'])

    if places_required <= 0:
        flash("Le nombre de places à réserver doit être supérieur à zéro.")
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    total_places_reservees = sum(club.get('placesReservees', {}).values())

    if total_places_reservees + places_required > 12:
        flash(
            f"Vous avez déjà réservé {total_places_reservees} places. "
            f"Vous ne pouvez réserver que "
            f"{12 - total_places_reservees} places supplémentaires."
        )
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    if places_required > int(competition['numberOfPlaces']):
        flash(
            f"Il n'y a pas assez de places disponibles. "
            f"Il reste {competition['numberOfPlaces']} places."
        )
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    if places_required > int(club['points']):
        flash(
            f"Vous n'avez pas assez de points pour réserver "
            f"{places_required} places. Vous avez {club['points']} points."
        )
        return render_template(
            'welcome.html',
            club=club,
            competitions=competitions
        )

    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - places_required
    )
    club['points'] = int(club['points']) - places_required

    if 'placesReservees' not in club:
        club['placesReservees'] = {}

    club['placesReservees'][competition['name']] = (
        club['placesReservees'].get(competition['name'], 0) +
        places_required
    )

    flash(
        f"Réservation réussie ! Vous avez réservé "
        f"{places_required} places pour {competition['name']}."
    )
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions
    )


@app.route('/public-points')
def publicPoints():
    return render_template('public_points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
