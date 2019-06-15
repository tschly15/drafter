import common
from flask import Flask, request, redirect, url_for, session, render_template
from flask_bootstrap import Bootstrap

# setup flask
app = Flask(__name__)
Bootstrap(app)

app.config.update(
    SECRET_KEY='aldkfahbnadjllakdjfladif[qpqi34pvmcwh;pgjiern',
    DEBUG = True
)

@app.route('/test', methods=['GET'])
def test():
    return "<html><title>Inside Draft App</title><h1>Draft App</h1><p>Welcome</p></html>"

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

app.run()
