import json
import redis
import common
from flask import Flask, request, redirect, url_for, session, render_template
from flask_bootstrap import Bootstrap
from flask_session import Session

# setup flask
app = Flask(__name__)
app.config.update(
    DEBUG = True,
    SESSION_TYPE = 'redis',
    SECRET_KEY='aldkfahbnadjllakdjfladif[qpqi34pvmcwh;pgjiern',
)

Bootstrap(app)
Session(app)


@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        proceed = request.form['button']
        session['pick'] = 1
        session['teams'] = int(request.form['button'])
        return redirect(url_for('display_players'))
    return render_template('home.html')

@app.route("/display_players", methods=['GET','POST'])
def display_players():
    #enc = encoder()
    #print enc.encode(sc)
    if request.method == 'GET':
        session['player_dct'] = common.build_players(refresh=False)
        session['tester'] = 'one'
        
    else:
        player = request.form['button']
        pdct = session['player_dct'].pop(player)
        session['team_id'] = common.pick_to_team(session['teams'], session['pick'])
        print(session['pick'], session['team_id'], pdct)
        session['pick'] += 1
        print(session['player_dct'])

    return render_template('display_players.html', player_dct=session['player_dct'], session=session)

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

app.run()
