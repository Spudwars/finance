# This Python file uses the following encoding: utf-8

import csv
import logging

# MUST use python-dateutil==1.5 as 2.0 is for python3 and breaks with:
#TypeError: iter() returned non-iterator of type '_timelex'
from dateutil.parser import parse

def parse_csv(csv_stream, fieldnames, dayfirst=True, skip_rows=0, max_rows=None):
    """
    csv_stream : file like object supporting .read
    fieldnames : ordered list of fields, e.g.: (None, 'date', 'payee', None, 'amount')
    dayfirst : for parsing dates - False for US dates which are month first
    skip_rows : number of rows at start of file to skip (e.g. skip one header row)
    max_rows : read this many rows (excluding any skip_rows)- used for testing file format
    
    raises ValueError if there's an issue with parsing any of the rows
    """
    dialect = csv.Sniffer().sniff(csv_stream.read(1024))
    logging.info("Dialect determined as %s", dialect)
    csv_stream.seek(0)
    reader = csv.DictReader(csv_stream, fieldnames=fieldnames, dialect=dialect)
    
    transactions = []
    for row_num, row_dict in enumerate(reader):
        if row_num < skip_rows:
            continue # skip this row
        elif max_rows and row_num == max_rows + skip_rows:
            break # read enough rows now!
        else:
            pass # build a new transaction from the row
        
        new_row = {}
        for field in fieldnames:
            val = row_dict[field]
            if field == 'amount':
                new_row[field] = float(val) #TODO: support profile.decimal_seperator, use locale? "fullstop" == '.'
            elif field == 'date':
                new_row[field] = parse(val, dayfirst=dayfirst).date() # only take date part
            elif field == 'payee':
                new_row[field] = unicode(val, encoding='UTF-8') # read in everything as Unicode UTF-8 to accept £ symbols etc.
            else:
                # we're not interested in any other fields used as padding
                continue
        ##assert sorted(new_row.keys()) == sorted([f for f in fieldnames if f]), "Not all columns present"
        if set([f for f in fieldnames if f]) - set(new_row.keys()):
            raise ValueError("Not all columns present") # TODO: Allow for empty lines in file?

        transactions.append(new_row)
    return transactions
        
