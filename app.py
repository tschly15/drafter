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
)

Bootstrap(app)
Session(app)

class LForm(Form):
    for fld, form_nt in league_fields.items():
        locals()[fld] = SelectField(form_nt.label, choices=form_nt.choices, validators=[validators.Required()])


@app.route("/", methods=['GET','POST'])
def index():
    form = LForm(request.form)
    if request.method == 'GET':
        return render_template('lea.html', form=form)

    session['pick'] = 1

    #capture the necessary league fields
    session.update(dict([ (fld, val.data)
                           for fld, val in form._fields.items() ]))

    session['league'] = league_cls(session).to_json()
    return render_template('confirm.html', form=form, session=session)


@app.route("/draft_player", methods=['GET','POST'])
def draft_player():
    print(league_cls.from_json(session['league']))

    if request.method == 'POST':
        session['league'] = league_cls.from_json(session['league'])

        player = request.form['button']
        pobj = session['league'].players[player] #obj of player_cls

        #do these values stick when league goes back to json?
        pobj.pick = session['pick']
        pobj.team_id = common.pick_to_team(session['num_teams'], session['pick'])

        session['pick'] += 1
        session['league'] = session['league'].to_json()

    return render_template('display_players.html', session=session)

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

app.run(debug=True)
#app.run(debug=True, port=5001)
