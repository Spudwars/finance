from unittest import TestCase

from finance.parse_csv import parse_csv

SAMPLE_CSV = """\
010203 12001234,31/05/2011,DIRECT DEBIT PAYMENT TO LA LEISURE LTD NO1 REF FA12948 MANDATE NO 0013,-33.99
010203 12001234,31/05/2011,DIRECT DEBIT PAYMENT TO LA LEISURE LTD NO1 REF FA12947 MANDATE NO 0012,-33.99
010203 12001234,31/05/2011,DIRECT DEBIT PAYMENT TO DIRECT LINE INS REF 54321234/000001/P MANDATE NO 0015,-14.87
010203 12001234,31/05/2011,CARD PAYMENT TO CO-OP GROUP 54321234.24 GBP ON 29-05-2011,-18.24
010203 12001234,25/05/2011,DIRECT DEBIT PAYMENT TO SOUTHERN WATER REF 0001234543212 MANDATE NO 0014,-23.70
010203 12001234,19/05/2011,DIRECT DEBIT PAYMENT TO NPOWER REF 001 54321234 MANDATE NO 0019,-85.00
010203 12001234,18/05/2011,CARD PAYMENT TO ASDA SUPERSTORE17.63 GBP ON 16-05-2011,-17.63
010203 12001234,18/05/2011,CARD PAYMENT TO ASDA STORES/PETROL/35.00 GBP ON 16-05-2011,-35.00
010203 12001234,16/05/2011,FASTER PAYMENTS RECEIPT REF SAVOLAINEN RM,650.00
010203 12001234,16/05/2011,REGULAR TRANSFER FROM MR CHRISTOPHER JESSE,650.00
"""


class TestImportCsv(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_parse_csv_sample(self):
        ts = parse_csv(SAMPLE_CSV)
        
        assert len(ts) == 10