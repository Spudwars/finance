# This Python file uses the following encoding: utf-8

import logging
##import warnings #TODO: use this in place of logging.warning?

# MUST use python-dateutil==1.5 as 2.0 is for python3 and breaks with:
#TypeError: iter() returned non-iterator of type '_timelex'
from dateutil.parser import parse

def parse_qif(qif_data, dayfirst=True): # date_format='%d/%m/%Y'):
    """
    import records from qif data - an iterable (file or list of lines)

    http://en.wikipedia.org/wiki/Quicken_Interchange_Format
    
    This helped:
    http://code.activestate.com/recipes/306103-quicken-qif-file-class-and-conversion/
    """
    
    ##types = {
        ##'Bank' : 'Bank account transactions',
        ##'Cash' : 'Cash account transactions',
        ##'CCard' : 'Credit card account transactions',
        ##'Invst' : 'Investment account transactions',
        ##'Oth A' : 'Asset account transactions',
        ##'Oth L' : 'Liability account transactions',
        ##'Cat' : 'Category list',
        ##'Class' : 'Class list',
        ##'Memorized' : 'Memorized transaction list',
        ##}
    
    transactions = []
    current_item = {}
    for line in qif_data:
        line = line.strip() # just in case
        if not line:
            # blank line
            continue
        else:
            pass
        
        field, value = line[0], line[1:]
        
        if field == '!': # header line
            if value.startswith('Type:'):
                data_type = value.split(':')[1]
                # TODO: Something?!
                pass

            elif values == 'Account':
                pass # Account list or which account follows
            else:
                # don't recognise this line; ignore it
                #!Option:AllXfr for example
                logging.warning('Skipping unknown header line: %s', line)
            continue
        else:
            # store imported rows
            #TODO: Improve this?
            current_item['import_string'] = current_item.get('import_string', '') + line + '\n'
            
        if field == '^' and current_item: # end of item (which has content)
            # save the item
            transactions.append(current_item)
            current_item = {}
        elif field == 'D':
            current_item['date'] = parse(value, dayfirst=dayfirst).date() # common
        elif field == 'T':
            current_item['amount'] = float(value.replace(',','')) #TODO: Better replacement of thousands - locale.utof not perfect!
        elif field == 'C':
            current_item['cleared'] = value
        elif field == 'P':
            current_item['payee'] = value # common
        elif field == 'M':
            current_item['memo'] = value
        elif field == 'N':
            #Num (check or reference number)
            current_item['number'] = value
        elif field == 'A':
            #Address (up to five lines; the sixth line is an optional message)
            current_item['address'] = value
        elif field == 'L':
            #Category (Category/Subcategory/Transfer/Class) 
            current_item['category'] = value #TODO: Use this as the default category for each split if none provided?
        elif field == 'S':
            #Category in split (Category/Transfer/Class)
            try:
                current_item['category_in_split'].append(value)
            except KeyError:
                current_item['category_in_split'] = [value]
        elif field == 'E':
            #Memo in split
            try:
                current_item['memo_in_split'].append(value)
            except KeyError:
                current_item['memo_in_split'] = [value]
        elif field == '$':
            #Dollar amount of split
            try:
                current_item['amount_in_split'].append(float(value))
            except KeyError:
                current_item['amount_in_split'] = [float(value)]
        else:
            logging.warning('Skipping unknown line: %s', line)

    return transactions
