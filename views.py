# This Python file uses the following encoding: utf-8

from finance.models import CsvImportProfile, Transaction
from datetime import datetime

def import_qif(filename):
    # Rob does magic here
    """
    import records from qif file

    http://en.wikipedia.org/wiki/Quicken_Interchange_Format
    """

    # The properties for any non-investment account:
    transaction_properties = { "C": None, "D": "date", "E": "splitMemo", "L": "category", "P": "payee",
                               "M": "memo", "N": "number", "S": "splitCategory", "T": "amount",
                               "U": None, "$": "splitAmount"}


    # For each type of account, a conversion from QIF poerty letter to rdf property name:
    properties = {
        "Mort": transaction_properties,
        "Account": {"D": "description", "L": "limit", "N": "name", "T":  "type"},
        "Bank": transaction_properties,
        "Bill": transaction_properties,
        "Cat":   {"B": None, "D": "description", "I": None, "N": "name", "T": None},   # Category
        "CCard": transaction_properties,
        "Class": {"D": "description", "N": "name"},
        "Invst": { "D": "date", "L": "link", "P": "payee", "M": "memo",
                   "N": "number", "T": "amount", "U": "amount2", "$": "splitAmount" },
        "Oth_A": transaction_properties,
        "Oth_L": transaction_properties,
        "Cash" : transaction_properties,
    }

    while line != '':
        if line[0] == '\n': # blank line
            pass
        elif line[0] == '!': # header line
            if line[1:5].lower == 'type':
                if line[1:-1].lower in ['account']:
                    current_model = Transaction
                elif line[1:-1].lower == 'cat':
                    current_model = Category
            elif line[1:-1].lower == 'account':
                current_model = Account
            else:
                # don't recognise this line; ignore it
                logger.warning('Skipping unknown line')

            current_model = current_model()
        elif line[0] == '^': # end of item
            # save the item
            current_model.save()
            current_model = current_model()
        else:
            try:
                getattr(current_model, 'qif_'+properties.get(line[0]))(line[1:-1].trim())
            except: 
                logger.exception()

        line = infile.readline()
    return items



if __name__ == "__main__":
    with open("../resources/example.qif") as f:
        items = qif_importer(f)
        for item in items[1:]:
    pass

def import_csv(filename, profile, account):
    '''
    csvReader = csv.reader(
            UTF8Recoder(csvdata, settings['encoding']),
            delimiter=settings['delimiter'])

        transactions = []
        linesSkipped = 0
        for row in csvReader:
    '''
    #TODO: Use csv reader / dict reader
    num_created = 0
    with open(filename) as csv_file:
        for x in range(profile.data_start_row):
            # skip rows
            csv_file.readline() # or csv_file.next()?

        for line in csv_file:
            if not line:
                break # end of file

            cols = [col.strip() for col in line.split(profile.column_delimiter)]

            for rule in CategoryRule.objects.all(): #TODO: filter for categories within Account
                if rule.matches(cols[profile.name_pos]):
                    # we've found a match for this row
                    break
            else:
                rule = None

            trans_date = datetime.strptime(cols[profile.date_pos],profile.date_format) #TODO: improve using a generic date parser which tries different techniques in turn?

            transaction = Transaction(
                name='', #TODO: create from subsections of transaction?
                import_string=line,
                account=account,
                date=trans_date,
                amount=float(cols[profile.amount_pos]),
                #creditor='',
                category=rule.category if rule else None,
            )
            transaction.save()
            num_created +=1
        #end open file
    return num_created


def import_transactions(filename, destination_account):
    if filename.upper().endswith('QIF'):
        num_trans = import_qif(filename, destination_account)

    elif filename.upper().endswith('CSV'):
        for profile in CsvImportProfile.objects.all():
            if profile.match(filename):
                num_trans = import_csv(filename, profile, destination_account)
                break
        else:
            raise ValueError, "No profile matches"
    return num_trans #could return within the if statements, but feels tider here(?)


def reapply_category_rules(rule, transactions):
    """ rule object and transactions queryset
    """
    # apply search_text_field from Nile and then reassign transactions to rule.category
    pass