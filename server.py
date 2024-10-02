import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


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
    club = next((club for club in clubs if club['email'] == email), None)
    if club:
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        # Message flash pour les emails non valides
        flash("Désolé, l'email n'est pas reconnu . Veuillez réessayer.")
        return redirect(url_for('index'))
    
@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # Vérification que le nombre de places demandées est supérieur à 0
    if placesRequired <= 0:
        flash("Le nombre de places à réserver doit être supérieur à zéro.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Initialiser le nombre de places réservées si ce n’est pas déjà fait
    if 'placesReservees' not in club:
        club['placesReservees'] = {}

    # Calcul du total des places réservées par le club pour tous les événements
    totalPlacesReservees = sum(club['placesReservees'].values())

    # Vérification : la somme des places réservées ne doit pas dépasser 12, tous événements confondus
    if totalPlacesReservees + placesRequired > 12:
        flash(f"Vous avez déjà réservé {totalPlacesReservees} places. Vous ne pouvez réserver que {12 - totalPlacesReservees} places supplémentaires.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification des places disponibles dans la compétition
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Il n'y a pas assez de places disponibles. Il reste {competition['numberOfPlaces']} places.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérification des points disponibles pour le club
    if placesRequired > int(club['points']):
        flash(f"Vous n'avez pas assez de points pour réserver {placesRequired} places. Vous avez {club['points']} points.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Mise à jour des places et des points
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    # Mise à jour des places réservées pour cet événement
    if competition['name'] not in club['placesReservees']:
        club['placesReservees'][competition['name']] = 0
    club['placesReservees'][competition['name']] += placesRequired

    # Recalcul du total des places réservées pour tous les événements
    totalPlacesReservees = sum(club['placesReservees'].values())

    # Message de confirmation de la réservation
    flash(f"Réservation réussie ! Vous avez réservé {placesRequired} places pour {competition['name']}. Total des places réservées : {totalPlacesReservees} sur 12.")
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/public-points')
def publicPoints():
    # Récupérer la liste des clubs et leurs points pour les afficher publiquement
    return render_template('public_points.html', clubs=clubs)



# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))