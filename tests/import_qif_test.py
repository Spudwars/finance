from unittest import TestCase
from datetime import datetime

from finance.parse_qif import parse_qif


NORMAL_TRANSACTIONS = """\
!Type:Bank
D6/ 1/94
T-1,000.00
N1005
PBank Of Mortgage
L[linda]
S[linda]
$-253.64
SMort Int
$-746.36
^
D6/ 2/94
T75.00
PDeposit
^
D6/ 3/94
T-10.00
PJoBob Biggs
MJ.B. gets bucks
LEntertain
A1010 Rodeo Dr.
AWaco, Tx
A80505
A
A
A
^
"""


SAMPLE = """\
!Type:Oth L
D14/07/2011
T700.00
PREGULAR TRANSFER FROM MR CHRISTOPHER JESSE REFERENCE - CJ Mortgage, 700.00GBP
^
D13/07/2011
T-33.64
PCARD PAYMENT TO ASDA SUPERSTORE,33.64 GBP ON 11-07-2011, 33.64GBP
^
D12/07/2011
T-11.99
PCARD PAYMENT TO THE Q GARDEN CO AT ABBEY,11.99 GBP ON 10-07-2011, 11.99GBP
^\
"""

class TestImportQif(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_parse_normarl_transactions(self):
        ts = parse_qif(NORMAL_TRANSACTIONS.splitlines(), dayfirst=False)    
        assert len(ts) == 3
        
        assert ts == [
            {'amount': -1000.0,
             'amount_in_split': [-253.63999999999999, -746.36000000000001],
             'category': '[linda]',
             'category_in_split': ['[linda]', 'Mort Int'],
             'date': datetime(1994, 6, 1, 0, 0),
             'import_string': 'D6/ 1/94\nT-1,000.00\nN1005\nPBank Of Mortgage\nL[linda]\nS[linda]\n$-253.64\nSMort Int\n$-746.36\n^\n',
             'number': '1005',
             'payee': 'Bank Of Mortgage'},
            {'amount': 75.0,
             'date': datetime(1994, 6, 2, 0, 0),
             'import_string': 'D6/ 2/94\nT75.00\nPDeposit\n^\n',
             'payee': 'Deposit'},
            {'address': '',
             'amount': -10.0,
             'category': 'Entertain',
             'date': datetime(1994, 6, 3, 0, 0),
             'import_string': 'D6/ 3/94\nT-10.00\nPJoBob Biggs\nMJ.B. gets bucks\nLEntertain\nA1010 Rodeo Dr.\nAWaco, Tx\nA80505\nA\nA\nA\n^\n',
             'memo': 'J.B. gets bucks',
             'payee': 'JoBob Biggs'}
        ]
    
    
    def test_parse_sample(self):
        ts = parse_qif(SAMPLE.splitlines())  
        assert len(ts) == 3
    