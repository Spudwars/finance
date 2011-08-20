from unittest import TestCase
from datetime import datetime

from finance.transaction_match import match_transaction_type, match_category

class TestTransactionMatch(TestCase):
    def setUp(self):
        #TODO: setup dummy rules
        pass
    
    def tearDown(self):
        pass

    def test_no_match(self):
        assert match_transaction_type('NOTHING_HERE!') == None
    
    def test_direct_debit(self):
        res = match_transaction_type('DIRECT DEBIT PAYMENT TO DIRECT LINE INS REF 54321234/000001/P MANDATE NO 0015')
        assert res == ('direct_debit', 'DIRECT LINE INS REF 54321234/000001/P MANDATE NO 0015', None)

    def test_card_payment(self):
        res = match_transaction_type('CARD PAYMENT TO CO-OP GROUP 54321234.24 GBP ON 29-05-2011', amount=abs(-34.24))
        assert res == ('card_payment', "CO-OP GROUP 543212", datetime(2011,5,29)) # why does this fail - it strips off the last "2" when you rstrip the numeric and a "."
        res = match_transaction_type('CARD PAYMENT TO ASDA SUPERSTORE,33.64 GBP ON 11-07-2011, 33.64GBP')
        assert res == ('card_payment', 'ASDA SUPERSTORE')
        
    def test_transfer(self):
        res = match_transaction_type('FASTER PAYMENTS RECEIPT REF SAVOLAINEN RM')
        assert res == ('transfer', 'SAVOLAINEN RM', None)
        
        res = match_transaction_type('REGULAR TRANSFER FROM MR CHRISTOPHER JESSE')        
        assert res == ('transfer', 'MR CHRISTOPHER JESSE', None)
        
        
class TestCategoryMatch(TestCase):
    def setUp(self):
        #TODO: setup dummy rules
        pass
    
    def tearDown(self):
        pass
    
    def test_no_match(self):
        assert match_category('card_payment', 'FISH') == None
        
    def test_petrol(self):
        res = match_category('card_payment','ASDA STORES/PETROL/35.00 GBP')
        assert res == 'petrol'
        
    def test_utilities(self):
        res = match_category('direct_debit','NPOWER REF 001 54321234 MANDATE NO 0019')
        assert res == 'dual_fuel'
        res = match_category('direct_debit','SOUTHERN WATER REF 0001234543212 MANDATE NO 0014')
        assert res == 'water_supply'
        