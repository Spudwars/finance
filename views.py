# This Python file uses the following encoding: utf-8
##import logging

from finance.models import Category, CategoryRule, CsvImportProfile, Transaction

from finance.parse_csv import parse_csv
from finance.parse_qif import parse_qif


"""
import_qif has been made very generic, populating a dict. so that others can
use it in their projects.

import_csv has model dependancies for rule matching.
"""

# TODO: Accept split transactions

def import_qif(filename, account):
    """
    """
    with open(filename) as qif_file:
        transactions = parse_qif(qif_file)
        
    for t in transactions:
        #TODO: Category chosen from payee?
        category = Category.objects.get_or_create(
            name = t['category']
        )
        # create and save Transactions in DB
        new_transaction = Transaction(account=account,
            account=account,
            name = '', #TODO: populate!
            import_string = t['import_string'],
            date = t['date'],
            amount = t['amount'],
            payee = t['payee'], #TODO: Parse into parts based on rules
            category = category, 
        )
        
        new_transaction.save()
    return len(transactions)

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
    
    with open(filename) as csv_file:
        transactions = parse_csv(csv_file, profile, account)
        
    for t in transactions:
        # create and save Transactions in DB
        
        # find a matching Category
        for rule in CategoryRule.objects.all(): #TODO: filter for categories within Account
            if rule.matches(t['name']):
                # we've found a match for this row
                category = rule.category
                break
        else:
            category = None
            
        new_transaction = Transaction(
            account=account,
            name = '', #TODO: populate!
            import_string = t['import_string'],
            date = t['date'],
            amount = t['amount'],
            payee = t['payee'],
            category = category,
        )
        new_transaction.save()
        
    return len(transactions)
                                 


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
