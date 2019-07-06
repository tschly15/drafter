#!Scripts/python
###!bin/python
import json
import redis
from league import league_cls
from flask_session import Session
from flask_bootstrap import Bootstrap
from forms import league_fields, LeagueForm
from flask import Flask, request, redirect, url_for, session, render_template

# setup flask
app = Flask(__name__)
app.config.update(
    DEBUG = True,
    SESSION_TYPE = 'redis',
    SECRET_KEY = 'f4ea57d983e77f074fb9209c425b238b56bdcc8c92d32c4f',
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
        return render_template('league.html', form=form)

    for fld in form._fields:
        value = form._fields[fld].data
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
            league = league_cls(session=session)
            session['league'] = league.to_json()

            if league.keepers == 'Y':
                return redirect(url_for('keepers'))

            return redirect(url_for('draft_player'))

        return redirect(url_for('home'))

    return render_template('confirm.html', session=session)


@app.route('/keepers', methods=['GET','POST'])
def keepers():
    league = league_cls.from_json(session['league'])

    if request.method == 'POST':
        user_selected = request.form['user_selected']
        if 'keeper_team_id' not in session:
            session['keeper_team_id'] = user_selected
        elif 'keeper_player_rank' not in session:
            session['keeper_player_rank'] = user_selected
            player_obj = league.players[int(session['keeper_player_rank'])]
            player_obj.team_id = session['keeper_team_id']
            #TODO:
            #request user to provide round
            #figure out the pick # and then set it
            player_obj.pick = 'keeper'
            #set the player to manager's team

        if request.form.get('confirmed','') == 'True':
            return redirect(url_for('draft_player'))

    return render_template('keepers.html', league=league)


@app.route("/draft_player", methods=['GET','POST'])
def draft_player():

    league = league_cls.from_json(session['league'])
    if request.method == 'POST':

        undo = request.form.get('undo_button','')
        if undo == 'UNDO':

            #TODO: do not allow this to undo a keeper

            rank = int(league.drafted.pop(-1))
            player_obj = league.players[rank]

            #mark player as unpicked (will now display in league pool)
            player_obj.pick = ''
            #remove the player from the manager's team
            league.teams[player_obj.team_id].drop_player(rank)
                            
        else:
            rank = int(request.form['select_by_rank'])
            league.drafted.append(rank)

            team_id = league.pick_to_team()
            team = league.teams[team_id]

            player_obj = league.players[rank] #obj of player_cls
            player_obj.pick = str(len(league.drafted))
            player_obj.team_id = team_id #handy for UNDO

            #1. attempt to assign as player's given position
            #2. attempt to assign to a flex position
            #3. attempt to assign to the bench

            pos = player_obj.position
            applicable_positions = [ fld
                                     for fld in session
                                     if fld.count(pos)
                                        and int(session[fld][1]) > 0 ]

            #move to the front of the line
            key = 'settings_num_{0}'.format(pos)
            if key in applicable_positions:
                applicable_positions.remove(key)
                applicable_positions.insert(0, key)

            for position in applicable_positions:
                pos_key = position.rsplit('_',1)[1].upper()
                if len(team.team_players[pos_key]) < int(session[position][1]):
                    break
            else:
                pos_key = 'BN'

            league.teams[team_id].team_players[pos_key].append(rank)

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
