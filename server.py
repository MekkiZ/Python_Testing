import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import *


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        json.dumps(listOfCompetitions, indent=4, sort_keys=True, default=str)
        return listOfCompetitions


def loop_func(competitions):
    date = datetime.now()
    current_date = date.strftime("%Y-%m-%d %H:%M:%S")

    lis_for_past_com = []
    competition = [competiton for competiton in competitions
                   if competiton['date'] >= current_date]
    numero = [b for b in competitions
              if b['date'] < current_date]
    for i in numero:
        if i['date'] < current_date:
            i["numberOfPlaces"] = str(0)
            lis_for_past_com.append(i)

    return lis_for_past_com, competition


def substraction_tot(a, b):
    """
    simple function to substracts two int for testing it after.
    :param a: integer
    :param b: integer
    :return: return result in path PurchasePlaces
    """
    return int(a) - int(b)


def app_main(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = 'something_special'
    competitions = loadCompetitions()
    clubs = loadClubs()
    list_data = []
    date = datetime.now()
    current_date = date.strftime("%Y-%m-%d %H:%M:%S")

    @app.route('/')
    def index():
        return render_template('index.html', club=view_table())

    @app.route('/showSummary', methods=['GET', 'POST'])
    def showSummary():
        """
        connexion part
        :return: render templat jinja
        """
        if request.method == 'POST':
            res_form = request.form['email']
            for el in clubs:
                list_data.append(el['email'])
            if res_form in list_data:
                club = [club for club in clubs if club['email'] == request.form['email']][0]
                lis_for_past_com, competition = loop_func(competitions)
                return render_template('welcome.html', club=club, numero=lis_for_past_com, competitions=competition)
            else:
                flash('This mail is not in our database, please contact us')
                return redirect(url_for('index'))
        else:
            return render_template('welcome.html')

    @app.route('/book/<competition>/<club>')
    def book(competition, club):
        foundClub = [c for c in clubs if c['name'] == club][0]
        foundCompetition = [c for c in competitions
                            if c['name'] == competition and
                            c['date'] >= current_date][0]
        if foundClub and foundCompetition:
            print(foundClub)
            print(foundCompetition)
            return render_template('booking.html', club=foundClub, competition=foundCompetition)
        else:
            flash("Something went wrong-please try again")
            return redirect(url_for('book'))
        return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/purchasePlaces', methods=['POST'])
    def purchasePlaces():
        # TODO : verifier un probleme de mise a jour des point.
        form_request = request.form['places']
        competition = [c for c in competitions if c['name'] == request.form['competition']][0]
        club = [c for c in clubs if c['name'] == request.form['club']][0]
        lis_for_past_com, rest_comp = loop_func(competitions)
        if int(form_request) > 12:
            flash('vous ne pouvez pas depaser plus de 12 place par reservation')
            return render_template('welcome.html', club=club, numero=lis_for_past_com, competitions=rest_comp)
        else:
            places_required = int(request.form['places'])
            init_point = club['points']
            if int(club['points']) > 0:
                if int(request.form['places']) <= int(club['points']):
                    club['points'] = substraction_tot(int(init_point), places_required)
                    competition['numberOfPlaces'] = substraction_tot(int(competition['numberOfPlaces']), places_required)
                else:
                    flash('Be careful you took more place than you have')
            else:
                flash('Great-booking complete!')
                flash("You don't have enough points to register to competition")
                return render_template('welcome.html', club=club, numero=lis_for_past_com, competitions=rest_comp)
            return render_template('welcome.html', club=club, numero=lis_for_past_com, competitions=rest_comp)

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    def view_table():
        club = [club for club in clubs]
        print(club)
        return club

    return app


if __name__ == '__main__':
    app_main().run(debug=True)
