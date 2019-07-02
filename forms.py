#add a default value for league settings
from collections import namedtuple
from wtforms import Form, validators, SelectField

nt = namedtuple('form_data', 'label default choices')

league_fields = {
    'num_teams': nt('Teams', 10, [ (x,x) for x in range(6,15,2) ]),
    'num_rounds': nt('Rounds', 6, [ (x,x) for x in range(1,21) ]),
    'num_kickers': nt('Kickers', 0, [ (x,x) for x in range(0,3) ]),
    'num_qb': nt('Quarterbacks', 1, [ (x,x) for x in range(0,3) ]),
    'num_rb': nt('Running Backs', 2, [ (x,x) for x in range(0,3) ]),
    'num_wr': nt('Wide Receivers', 2, [ (x,x) for x in range(0,3) ]),
    'num_te': nt('Tight Ends', 0, [ (x,x) for x in range(0,3) ]),
    'num_wr/rb': nt('Flex: W/R', 0, [ (x,x) for x in range(0,3) ]),
    'num_wr/rb/te': nt('Flex: W/R/T', 0, [ (x,x) for x in range(0,3) ]),
    'num_wr/rb/te/qb': nt('SuperFlex: W/R/T/QB', 0, [ (x,x) for x in range(0,3) ]),
    'num_def': nt('Defenses', 1, [ (x,x) for x in range(0,3) ]),
}

class LeagueForm(Form):
    for fld, form_nt in league_fields.items():
        locals()[fld] = SelectField(form_nt.label,
                                    default=form_nt.default,
                                    choices=form_nt.choices,
                                    validators=[validators.Required()])
