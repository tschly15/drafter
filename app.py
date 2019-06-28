#!bin/python ##
import json
import redis
import common
from league import league_cls
from forms import league_fields
from flask_session import Session
from flask_bootstrap import Bootstrap
from wtforms import Form, validators, SelectField
from flask import Flask, request, redirect, url_for, session, render_template

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

class LForm(Form):
    for fld, form_nt in league_fields.iteritems(): ##
        locals()[fld] = SelectField(form_nt.label, choices=form_nt.choices, validators=[validators.Required()])


@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():

    #clean the session
    for key in ('league','pick'):
        try:
            del session[key]
        except:
            pass

    form = LForm(request.form)
    if request.method == 'GET':
        return render_template('lea.html', form=form)

    #proceed = request.form['button']
    session['pick'] = 1

    #capture the necessary league fields
    session.update(dict([ (fld, val.data)
                           for fld, val in form._fields.iteritems() ])) ##
    session['league'] = league_cls(session=session).to_json()

    return redirect(url_for('confirm'))

@app.route('/confirm', methods=['GET','POST'])
def confirm():
    '''display all lg info'''

    if request.method == 'POST':

        if request.form.get('confirmed','') == 'True':
            return redirect(url_for('draft_player'))

        return redirect(url_for('home'))

    return render_template('confirm.html')

@app.route("/draft_player", methods=['GET','POST'])
def draft_player():

    league = league_cls.from_json(session['league'])
    if request.method == 'POST':

        player = request.form['button']
        pobj = league.players[player] #obj of player_cls

        pobj.pick = session['pick']
        pobj.team_id = common.pick_to_team(session['num_teams'], session['pick'])

        session['pick'] += 1
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
