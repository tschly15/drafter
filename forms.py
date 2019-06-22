from collections import namedtuple
nt = namedtuple('form_data', 'label choices')

league_fields = {
    'num_teams': nt('Teams', [ (x,x) for x in range(6,15,2) ]),
    'num_rounds': nt('Rounds', [ (x,x) for x in range(1,21) ]),
    'num_kickers': nt('Kickers', [ (x,x) for x in range(0,3) ]),
    'num_qbs': nt('Quarterbacks', [ (x,x) for x in range(0,3) ]),
    'num_rbs': nt('Running Backs', [ (x,x) for x in range(0,3) ]),
    'num_wrs': nt('Wide Receivers', [ (x,x) for x in range(0,3) ]),
    'num_tes': nt('Tight Ends', [ (x,x) for x in range(0,3) ]),
    'num_flx1': nt('Flex: W/R', [ (x,x) for x in range(0,3) ]),
    'num_flx2': nt('Flex: W/R/T', [ (x,x) for x in range(0,3) ]),
    'num_flx3': nt('SuperFlex: W/R/T/QB', [ (x,x) for x in range(0,3) ]),
    'num_defs': nt('Defenses', [ (x,x) for x in range(0,3) ]),
}
