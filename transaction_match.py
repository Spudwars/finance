# This Python file uses the following encoding: utf-8

from dateutil.parser import parse

from finance.models import CategoryRule, TransactionType

"""
DIRECT DEBIT PAYMENT TO DIRECT LINE INS REF 54321234/000001/P MANDATE NO 0015
CARD PAYMENT TO CO-OP GROUP 54321234.24 GBP ON 29-05-2011
FASTER PAYMENTS RECEIPT REF SAVOLAINEN RM
REGULAR TRANSFER FROM MR CHRISTOPHER JESSE
"""

# Some have details of the actual payment date (ON DATE) in addition to the transaction date

# , amount_string - use this arg to remove payment amount from string
def match_transaction_type(entry): #, amount='', currency='GBP'): 
    """
    Matches entry against strings which start against rules 
    and reutrns the remaining string and the transaction type
    
    Strips amount and  currency from the end of the entry for returning
    """
    for trans_type in TransactionType.objects.all().order_by('order'):
        result = trans_type.matches(entry)
        if result:
            # we've found a match for this row
            return trans_type, result
    else:
        # no transaction type found
        raise ValueError, "String does not match any rules"
    
    # This needs to be done better with more test cases to work out
    # what we really want to do:
    ## try and match " ON "
    #on_dt_str = " ON "
    #if on_dt_str in entry:
        #entry
        #start = entry.index(on_dt_str) + len(on_dt_str)
        #cost_removed = rstrip(currency).replace(', ' + str(abs(amount)), '').strip()
        #on_dt = parse(dcost_removed)   #TODO: include dayfirst argument for US transactions
        ## strip off the price from the end
         ##TODO: rstrip is wrong here as it removes any and all chars, not a series of chars!!!
         ## rpartition might be better for splitting it out, but that requires a few additional steps
         ## perhaps just a regex?
        #entry_part = entry[len(rule):entry.index(on_dt_str)]
        #return rules[rule], entry_part, on_dt
    #else:
        #return rules[rule], entry[len(rule):].rstrip(currency).strip().replace(str(amount),''), None
    #raise ValueError, "String does not match any rules"



def match_category(payee): 
    """
    """
    # find a matching Category
    for rule in CategoryRule.objects.all(): #TODO: filter for categories within Account
        if rule.matches(payee):
            # we've found a match for this row
            return rule.category
    else:
        # no category found
        return None

#TODO: Possibly add an optional FK to transaction type which we can
#  then filter on to reduce the chances of matching against the wrong
#  type of transaction
# e.g.:
#'transfer' :[
    #('CHRISTOPHER', 'chris_rent')
    #],
#'card_payment' : [
    #('PETROL', 'petrol'),
    #('ASDA SUPERSTORE', 'food'),
    #],
#'direct_debit' : [
    #('WATER', 'water_supply'), # belongs to utilities
    #('NPOWER', 'dual_fuel'), # belongs to utilities
    #('LA LEISURE LTD', 'gym'),
    #('DIRECT LINE INS', 'dog'),
    #],