from collections import namedtuple
from wtforms import Form, validators, SelectField

nt = namedtuple('form_data', 'label choices')

league_fields = {
    'num_teams': nt('Teams', [ (x,x) for x in range(6,15,2) ]),
    'num_rounds': nt('Rounds', [ (x,x) for x in range(1,21) ]),
    'num_k': nt('Kickers', [ (x,x) for x in range(0,3) ]),
    'num_qb': nt('Quarterbacks', [ (x,x) for x in range(0,3) ]),
    'num_rb': nt('Running Backs', [ (x,x) for x in range(0,3) ]),
    'num_wr': nt('Wide Receivers', [ (x,x) for x in range(0,3) ]),
    'num_te': nt('Tight Ends', [ (x,x) for x in range(0,3) ]),
    'num_wr/rb': nt('Flex: W/R', [ (x,x) for x in range(0,3) ]),
    'num_wr/rb/te': nt('Flex: W/R/T', [ (x,x) for x in range(0,3) ]),
    'num_wr/rb/te/qb': nt('SuperFlex: W/R/T/QB', [ (x,x) for x in range(0,3) ]),
    'num_def': nt('Defenses', [ (x,x) for x in range(0,3) ]),
}

class LeagueForm(Form):
    for fld, form_nt in league_fields.items():
        locals()[fld] = SelectField(form_nt.label, choices=form_nt.choices, validators=[validators.Required()])
