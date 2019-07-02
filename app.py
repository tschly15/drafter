#!Scripts/python
import json
import redis
from league import league_cls
from flask_session import Session
from flask_bootstrap import Bootstrap
from forms import league_fields, LeagueForm
from flask import Flask, request, redirect, url_for, session, render_template

#!/bin/python

# setup flask
app = Flask(__name__)
app.config.update(
    DEBUG = True,
    SESSION_TYPE = 'redis',
    SECRET_KEY = 'aldkfahbnadjllakdjfladif[qpqi34pvmcwh;pgjiern',
    SESSION_PERMANENT = False,
)

Bootstrap(app)
Session(app)

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():

    #ensure we begin with a clean session
    for key in list(session):
        del session[key]

    form = LeagueForm(request.form)
    if request.method == 'GET':
        return render_template('lea.html', form=form)

    for fld in form._fields:
        value = form._fields[fld].object_data
        label = form._fields[fld].label.text
        session['settings_{0}'.format(fld)] = (label, value)

    session.update(form.data)
    return redirect(url_for('confirm'))

@app.route('/confirm', methods=['GET','POST'])
def confirm():
    '''display all lg info'''

    if request.method == 'POST':

        if request.form.get('confirmed','') == 'True':
            #capture the necessary league fields
            session['league'] = league_cls(session=session).to_json()
            return redirect(url_for('draft_player'))

        return redirect(url_for('home'))

    return render_template('confirm.html', session=session)

@app.route("/draft_player", methods=['GET','POST'])
def draft_player():

    league = league_cls.from_json(session['league'])
    if request.method == 'POST':

        player = request.form['button']
        pobj = league.players.pop(player) #obj of player_cls
        pobj.pick = league.current_pick

        team_id = league.pick_to_team()
        league.teams[team_id].team_players[pobj.position].append(pobj)

        league.current_pick += 1
        session['league'] = league.to_json()

    return render_template('draft_player.html', league=league)

    '''
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    images= [
        {'type':'big', 'url':'....'},
        {'type':'big', 'url':'....'},
        {'type':'big', 'url':'....'},
    ]

    json_images = json.dumps(images)
    r.set('images', json_images)
    unpacked_images = json.loads(r.get('images'))
    images == unpacked_images
    '''

app.run(debug=True, port=5001)
