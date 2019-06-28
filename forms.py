from collections import namedtuple
nt = namedtuple('form_data', 'label choices')

league_fields = {
    'num_teams': nt('Teams', [ (x,x) for x in range(6,15,2) ]),
    'num_rounds': nt('Rounds', [ (x,x) for x in range(1,21) ]),
    'num_k': nt('Kickers', [ (x,x) for x in range(0,3) ]),
    'num_qb': nt('Quarterbacks', [ (x,x) for x in range(0,3) ]),
    'num_rb': nt('Running Backs', [ (x,x) for x in range(0,3) ]),
    'num_wr': nt('Wide Receivers', [ (x,x) for x in range(0,3) ]),
    'num_te': nt('Tight Ends', [ (x,x) for x in range(0,3) ]),
    'num_flx1': nt('Flex: W/R', [ (x,x) for x in range(0,3) ]),
    'num_flx2': nt('Flex: W/R/T', [ (x,x) for x in range(0,3) ]),
    'num_flx3': nt('SuperFlex: W/R/T/QB', [ (x,x) for x in range(0,3) ]),
    'num_def': nt('Defenses', [ (x,x) for x in range(0,3) ]),
}
