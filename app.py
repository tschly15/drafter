#!/usr/bin/env python

import json
from redis import Redis
from league import league_cls
from flask_session import Session
from flask_bootstrap import Bootstrap
from forms import league_fields, LeagueForm
from flask import Flask, request, redirect, url_for, session, render_template

# setup flask
app = Flask(__name__)
app.config.update(
    SESSION_TYPE = 'redis',
#   SESSION_REDIS = Redis(host='redis', port=6379),
    SECRET_KEY = 'f4ea57d983e77f074fb9209c425b238b56bdcc8c92d32c4f',
    SESSION_PERMANENT = False,
#   EXPLAIN_TEMPLATE_LOADING = True,
)

Bootstrap(app)
Session(app)

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = LeagueForm(request.form)

    if request.method == 'GET':
        #ensure we begin with a clean session
        for key in list(session):
            del session[key]
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

            if league.include_keepers == 'Y':
                return redirect(url_for('keepers'))

            return redirect(url_for('draft_player'))

        return redirect(url_for('home'))

    return render_template('confirm.html', session=session)


@app.route('/keepers', methods=['GET','POST'])
def keepers():
    league = league_cls.from_json(session['league'])

    if request.method == 'GET' or request.form.get('start_over','') == 'True':
        return render_template('keepers.html', league=league)
    elif request.form.get('confirmed','') == 'True':
        return redirect(url_for('draft_player'))
    elif request.form.get('start_over','') == 'True':
        return redirect(url_for('home'))

    user_selected = request.form['user_selected']

    if 'keeper_team_id' not in session:
        session['keeper_team_id'] = user_selected

    elif 'keeper_player_round' not in session:
        #request user to provide round
        session['keeper_player_round'] = user_selected

    elif 'keeper_player_rank' not in session:
        rank = int(user_selected)
        team_id = int(session['keeper_team_id'])

        player_obj = league.players[rank]
        player_obj.pick = league.pick_from_team(session)
        player_obj.team_id = team_id #set the player to manager's team
        player_obj.keeper_round = session['keeper_player_round']

        team = league.teams[team_id]
        position = team.determine_position(session, player_obj)
        team.team_players[position].append(rank)

        league.keepers[player_obj.pick] = rank

        for key in list(session):
            if key.startswith('keeper_'):
                del session[key]

        session['league'] = league.to_json()

    if request.form.get('confirmed','') == 'True':
        return redirect(url_for('draft_player'))

    return render_template('keepers.html', league=league)


@app.route("/draft_player", methods=['GET','POST'])
def draft_player():

    league = league_cls.from_json(session['league'])
    if request.method == 'POST':

        undo = request.form.get('undo_button','')
        if undo == 'UNDO':

            rank = int(league.drafted.pop(-1))

            #do not allow this to undo a keeper
            #TODO: maybe this condition changes to use current_pick
            if rank not in league.keepers.values():
                #mark player as unpicked (will now display in league pool)
                player_obj = league.players[rank]
                player_obj.pick = -1
                #remove the player from the manager's team
                league.teams[player_obj.team_id].drop_player(rank)

            #handle consecutive sleepers
            while int(league.drafted[-1]) in league.keepers.values():
                league.drafted.pop(-1)
                            
        else:
            #TODO: sort out str vs int issue for league.keepers
            # would like rank and team_id to remain an int
            rank = int(request.form['select_by_rank'])
            league.draft_player_with_rank(session, rank)

            #potential keeper pick 
            next_pick = str(len(league.drafted) + 1)
            while next_pick in league.keepers:
                keeper_rank = league.players[int(next_pick)].overall_rank
                league.drafted.append(keeper_rank)
                next_pick = str(len(league.drafted) + 1)

        session['league'] = league.to_json()

    return render_template('draft_player.html', league=league)


app.run(port=5002, host='0.0.0.0', debug=True)
