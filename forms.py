from collections import namedtuple
from wtforms import Form, validators, SelectField

nt = namedtuple('form_data', 'label default choices')

league_fields = {
    'num_teams': nt('Teams', 6, [ (x,x) for x in range(6,15,2) ]),
    'num_rounds': nt('Rounds', 6, [ (x,x) for x in range(1,21) ]),
    'num_K': nt('Kickers', 0, [ (x,x) for x in range(0,3) ]),
    'num_QB': nt('Quarterbacks', 1, [ (x,x) for x in range(0,3) ]),
    'num_RB': nt('Running Backs', 1, [ (x,x) for x in range(0,3) ]),
    'num_WR': nt('Wide Receivers', 1, [ (x,x) for x in range(0,3) ]),
    'num_TE': nt('Tight Ends', 0, [ (x,x) for x in range(0,3) ]),
    'num_WR/RB': nt('Flex: W/R', 0, [ (x,x) for x in range(0,3) ]),
    'num_WR/RB/TE': nt('Flex: W/R/T', 1, [ (x,x) for x in range(0,3) ]),
    'num_WR/RB/TE/QB': nt('SuperFlex: W/R/T/QB', 0, [ (x,x) for x in range(0,3) ]),
    'num_DST': nt('Defenses', 1, [ (x,x) for x in range(0,3) ]),
    'num_BN': nt('Bench', 6, [ (x,x) for x in range(0,11) ]),
}

class LeagueForm(Form):
    for fld, form_nt in league_fields.items():
        locals()[fld] = SelectField(form_nt.label,
                                    default=form_nt.default,
                                    choices=form_nt.choices,
                                    validators=[validators.Required()])

