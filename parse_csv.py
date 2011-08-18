# This Python file uses the following encoding: utf-8

import csv

# MUST use python-dateutil==1.5 as 2.0 is for python3 and breaks with:
#TypeError: iter() returned non-iterator of type '_timelex'
from dateutil.parser import parse

from finance.transaction_match import rule_match

#TODO: Accept only how many lines to skip and return transactions as dicts
#   - this is v. easy if there's a header row and you use csv.DictReader!!
#    - storing a real transactions is then done at a higher level
def parse_csv_v2(csv_stream, skip_rows=0, dayfirst=True):
    """
    csv_stream : file like object supporting .next()
    skip_rows : number of rows at start of file to skip
    dayfirst : for parsing dates - False for US dates which are month first
    """
    # use row_mapping upon dictreader or use trial and error:
    ##row_mapping : either index or col name based:
       ##[0:parse_dt, 1:None, 2:float, 3:rule_match]
       ##['date':parse_dt, 'name':None, 'amount':float, 'details':rule_match]
       
    # this is try and error:
    transactions = []
    reader = csv.DictReader(csv_stream, fieldnames=None) #TODO: we're using CSV DictReader, so we can accept excel etc...
    for n in range(skip_rows):
        reader.next()
    for row_dict in reader:
        for key, val in row_dict.iteritems():
            try:
                # amount
                row_dict[key] = float(val)
                continue
            except ValueError:
                pass
            try:
                # datetime
                row_dict[key] = parse(val, dayfirst=dayfirst)
                continue
            except ValueError:
                pass
            try:
                row_dict[key] = rule_match(val)
            except ValueError:
                pass
            #cannot cast to new format
            continue
        transactions.append(row_dict) #TODO: would a yield of the dict be enough here?
    return transactions
        



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