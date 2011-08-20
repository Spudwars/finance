# This Python file uses the following encoding: utf-8
import logging
from django.http import HttpResponse

from finance.models import Account, AccountType, Category, CategoryGroup,\
     CategoryRule, CsvImportProfile, Transaction, TransactionType, TransactionPart
from finance.parse_csv import parse_csv
from finance.parse_qif import parse_qif

from finance.transaction_match import match_transaction_type, match_category  #TODO: watch out for circular import


"""
import_qif has been made very generic, populating a dict. so that others can
use it in their projects.

import_csv has model dependancies for rule matching.
"""

#TODO: profile to chose where to get category from?
def _get_category(category_name):
    group, _ = CategoryGroup.objects.get_or_create(name='General') #TODO: change category group?
    category, _ = Category.objects.get_or_create(
        name = category_name,
        category_group = group, 
        )
    return category


def import_qif(filename, account):
    """
    """
    with open(filename, 'rb') as qif_file:
        transactions = parse_qif(qif_file)
    logging.info("%d QIF transactions found in file %s", len(transactions), filename)
    for t in transactions:
        try:
            trans_type, payee = match_transaction_type(t['payee'])
        except ValueError:
            logging.warning("Transaction type cannot be determined: %s", t['payee'])
            trans_type = None
            payee = t['payee']

        # create and save Transactions in DB            
        new_transaction = Transaction(
            account = account,
            name = payee, #TODO: populate or remove as we don't need a name?!
            date = t['date'],
            transaction_type = trans_type,
            payee = payee,
            ##paid_on = paid_on_dt,
            import_string = t['import_string'],
        )  
        new_transaction.save()
        
        if t.get('amount_in_split'):
            part_list = []
            for n, amount in t['amount_in_split']:
                # create and save Transactions in DB
                if t.get('category_in_split'):
                    # assumed category_in_split has same number of items as amount
                    split_category = _get_category(t['category_in_split'][n])
                else:
                    split_category = match_category(payee)
                    
                t_part = TransactionPart(
                    transaction = new_transaction,
                    amount = '%.2f' % amount,
                    category = split_category,
                    description  = '', #TODO: iterate over t['memo'] field if available
                )
                t_part.save() #TODO: Required again after?
                part_list.append(t_part)
            logging.debug("Imported %s - %s", new_transaction, part_list)
                    
        else:
            # create a single transactionamount
            if t.get('category'):
                # Category from QIF takes priority if available
                category = _get_category(category_name)
            else:
                category = match_category(payee)
            t_part = TransactionPart(
                transaction = new_transaction,
                amount = '%.2f' % t['amount'],
                description = t.get('memo', ''),
                category = category,
            )
            t_part.save() #TODO: Required again after?
            logging.debug("Imported %s - %s", new_transaction, t_part)
    return len(transactions)

def import_csv(filename, account):
    '''
    '''
    # CSVs come in many formats, find a matching profile
    for profile in CsvImportProfile.objects.all().order_by('order'):
        if profile.match(filename):
            logging.info("Found matching CSV profile: %s", profile)
            break
    else:
        raise ValueError, "No profiles matched the file"
    
    with open(filename, 'rb') as csv_file:
        transactions = parse_csv(csv_file, profile.get_fieldnames(), 
                                 dayfirst=profile.date_day_first,
                                 skip_rows=profile.data_start_row)
    logging.info("%d CSV transactions found in file %s", len(transactions), filename)
    for t in transactions:
        # split payee string into parts
        try:
            trans_type, payee = match_transaction_type(t['payee'])
        except ValueError:
            logging.warning("Transaction type cannot be determined: %s", t['payee'])
            trans_type = None
            payee = t['payee']

        # create and save Transactions in DB            
        new_transaction = Transaction(
            account = account,
            name = payee, #TODO: populate or remove as we don't need a name?!
            date = t['date'],
            transaction_type = trans_type,
            payee = payee,
            ##paid_on = paid_on_dt,
            ##import_string = t['import_string'], # DictReader doesn't give us the original line
        )
        new_transaction.save()
            
        t_part = TransactionPart(
            transaction = new_transaction,
            amount = '%.2f' % t['amount'],
            category = match_category(payee),
        )
        t_part.save()
        logging.debug("Imported %s - %s", new_transaction, t_part)
    
    return len(transactions)
                                 


def import_transactions(filename, destination_account):
    if filename.upper().endswith('QIF'):
        num_trans = import_qif(filename, destination_account)

    elif filename.upper().endswith('CSV'):
        num_trans = import_csv(filename, destination_account)

    return num_trans #could return within the if statements, but feels tider here(?)


def reapply_category_rules(rule, transactions):
    """ rule object and transactions queryset
    """
    # apply search_text_field from Nile and then reassign transactions to rule.category
    pass

def identify_duplicate_transactions(account):
    pass
    ##TransactionPart.objects.filter(transaction__account=account).aggregate()

def test_views(request):
    account, _ = Account.objects.get_or_create(
        name = "Test Account",
        type = AccountType.objects.get(name='Debit'),
        institution = 'MyBank',
    )
    account.owner.add(request.user)
    
    #TODO: Get account details from the filename / rows
    
    num_qif = import_transactions('apps/finance/tests/transactions.qif', account)
    num_csv = import_transactions('apps/finance/tests/transactions.csv', account)
    return HttpResponse('%d QIF transactions imported\n%d CSV transactions imported' % (num_qif,num_csv))