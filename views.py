# This Python file uses the following encoding: utf-8

from finance.models import CsvImportProfile, Transaction
from datetime import datetime

def import_qif(filename):
    # Rob does magic here
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

            # Check for duplicate transaction - is the import_string line enough
            
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
