# This Python file uses the following encoding: utf-8

# MUST use python-dateutil==1.5 as 2.0 is for python3 and breaks with:
#TypeError: iter() returned non-iterator of type '_timelex'
from dateutil.parser import parse

"""
DIRECT DEBIT PAYMENT TO DIRECT LINE INS REF 54321234/000001/P MANDATE NO 0015
CARD PAYMENT TO CO-OP GROUP 54321234.24 GBP ON 29-05-2011
FASTER PAYMENTS RECEIPT REF SAVOLAINEN RM
REGULAR TRANSFER FROM MR CHRISTOPHER JESSE
"""

def parse_csv(csv_data, profile, dayfirst=True):
    """ Returns a list of transaction dictionaries   (????? easier for testing but a bad idea ?????)
    """
    transactions = []
    for n, line in enumerate(csv_data):
        if not line:
            break # end of file
        elif n < profile.data_start_row: #0 indexed
            # skip intro rows
            continue

        cols = [col.strip() for col in line.split(profile.column_delimiter)]

        # Check for duplicate transaction - is the import_string line enough
        transaction = dict(
            name = cols[profile.name_pos], #TODO: create from subsections of transaction?
            import_string = line,
            date = parse(value, dayfirst=dayfirst) ,
            amount = float(cols[profile.amount_pos]),
            #creditor='',
            
        )
        transactions.append(transaction)
    return transactions