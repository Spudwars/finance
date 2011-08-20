# This Python file uses the following encoding: utf-8
import logging
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from settings import DEBUG
from finance.parse_csv import parse_csv


"""
Questions:
----------
* Should we store the original Imported File - this would allow re-imports..
* Duplicate detection for stopping multiple imports of lines? Or perhaps have a "find and merge duplicates" function?


TODO:
-----
* Add more Categories.
* Category optionally only be applied to certain TransactionTypes to restrict usage
* Add descriptions to categories in intial_data.yaml
* Spot gaps (possible missing transaction range) between two imported files

"""

def setup_logging():
    logger = logging.getLogger()
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
setup_logging()


class AccountType(models.Model):
    """
    Includes: Debit / Credit / Savings / Mortgage
    
    Populated by initial_data.yaml which will load fixture every run of syncdb
    """
    def __unicode__(self):
        return '%s' % self.name
    name = models.CharField(max_length=100,)
    

class Account(models.Model):
    def __unicode__(self):
        return '%s %s' % (self.name, self.institution)
    
    class Currency:
        STIRLING = '£'
        DOLLAR = '$'
        EURO = '€'
        
        LIST = (
            (STIRLING, 'Pound Stirling £'),
            (DOLLAR, 'Dollar $'),
            (EURO, 'Euro €'),
            )
            
    name = models.CharField(max_length=100,)
    #account_number = models.CharField(max_length=100,)
    institution = models.CharField(max_length=100,blank=True)
    currency = models.CharField(max_length=100,choices=Currency.LIST, default=Currency.STIRLING)
    type = models.ForeignKey(AccountType)
    owner = models.ManyToManyField(User, related_name='account_owner') # Signatories
    shared_with = models.ManyToManyField(User, related_name='account_share') # Shared access to non-owners
    # initial_balance_dt ???
    initial_balance = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    current_balance = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    

    
class CategoryGroup(models.Model):
    def __unicode__(self):
        return '%s' % (self.name)
    
    name = models.CharField(max_length=100,) # e.g. Property

    
class Category(models.Model): # Rename "Label" as this would be more applicable to "Tenant"    
    def __unicode__(self):
        return '%s %s' % (self.name, self.category_group)
    
    name = models.CharField(max_length=100,)  # i18n contents?
    category_group = models.ForeignKey(CategoryGroup)
    #user = models.ForeignKey(User) #why?
    description = models.TextField(blank=True)
    
# TODO: Link this to an Account to stop rules applied when your account doesn't have these categories?
class CategoryRule(models.Model):
    def __unicode__(self):
        return '%s %s' % (self.name, self.category)
    
    AND_DELIMITER = '&&'
    OR_DELIMITER = '||'
    
    name = models.CharField(max_length=100, help_text="Rule name")
    category = models.ForeignKey(Category)
    order = models.IntegerField(default=10) # apply rules in ascending order
    
    #TODO: How about JSON List?
    includes = models.CharField(max_length=100, default='', help_text="contains all these strings, double-ampersand delimited a&&b")
    excludes = models.CharField(max_length=100, default='', help_text="must not contain any of these strings, double-pipe delimited a||b")
    
    def matches(self, transaction):
        """ If transaction contains all includes and none of the excludes
        
        TODO: This suffers from UnicodeDecodeError such as 
        'ascii' codec can't decode byte 0xc2 in position 68: ordinal not in range(128)
        
        """
        # this can be done better!
        include_list = self.includes.split(self.AND_DELIMITER)
        exclude_list = self.excludes.split(self.OR_DELIMITER)
        
        if exclude_list and any([el.strip() in transaction for el in exclude_list]):
            # matched an exclude item
            return False
        elif include_list and all([el.strip() in transaction for el in include_list]):
            # matched all include items
            return True
        else:
            # didn't match all the includes
            return False
        
class Budget(models.Model):
    def __unicode__(self):
        return '%s %s' % (self.name, self.start_date)
    
    name = models.CharField(max_length=100,)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    #is_active ?
    
    @property
    def current(self):
        return self.start_date < datetime.now() < self.end_date
    
    def monthly_estimate(self):
        # something like this:
        return self.budget_estimate.aggregate(total=models.Sum('amount'))['total']
    

class BudgetEstimate(models.Model):
    """
    Calendar Month budget
    """
    def __unicode__(self):
        return '%s %s %s' % (self.name, self.category, amount)
    
    name = models.CharField(max_length=100,)
    budget = models.ForeignKey(Budget)
    category = models.ForeignKey(Category)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    #is_active ?
    
    def yearly_estimate(self):
        return self.amount * 12
    
    def transactions(self, start_date, end_date):
        # Estimates should only report on expenses to prevent incomes from 
        # (incorrectly) artificially inflating totals.
        return Transaction.objects.filter(category=self.category, date__range=(start_date, end_date)).order_by('date')
    
    def actual_amount(self, start_date, end_date):
        trans = self.transactions(start_date, end_date)
        return trans.aggregate(total=models.Sum('amount'))['total']
    
    
class CsvImportProfile(models.Model):
    def __unicode__(self):
        return '%s' % (self.name)
    
    class Seperator:
        COMMA = 'comma'
        FULL_STOP = 'fullstop'
        LIST = (
            (COMMA, 'Comma (,)'),
            (FULL_STOP, 'Full Stop (.)'),
            )
        
    name = models.CharField(max_length=100,)
    ##transaction_name_template = models.CharField(max_length=100,help_text='e.g. ${row[4]} from (${row[0]})')
    order = models.IntegerField(help_text='Order in which profile is tested for a match')
    # CSV columns mapping
    date_pos = models.IntegerField(help_text='Zero indexed position')
    payee_pos = models.IntegerField(help_text='Zero indexed position')
    amount_pos = models.IntegerField(help_text='Zero indexed position')
    # CSV settings
    data_start_row = models.IntegerField(default=0, help_text='Zero indexed row where data begins. Set to 1 if you have a single header row')
    date_day_first = models.BooleanField(default=True) # unless ure in america!
    decimal_seperator = models.CharField(max_length=5,choices=Seperator.LIST,default=Seperator.FULL_STOP) #TODO: Not yet supported!
    
    def match(self, file_in):
        with open(file_in, 'rb') as csv_file:
            try:
                result = parse_csv(csv_file, self.get_fieldnames(), 
                                   dayfirst=self.date_day_first,
                                   skip_rows=self.data_start_row,
                                   max_rows=2)
                #TODO: we could assert 2 transactions were found, but that
                #  would mean that you'd always need two transactions in every
                #  file you want to import
            except:
                return False
            else:
                return True
    
    def get_fieldnames(self):
        fieldnames = [None] * (max(self.date_pos, self.payee_pos, self.amount_pos) +1)
        fieldnames[self.date_pos] = 'date'
        fieldnames[self.payee_pos] = 'payee'
        fieldnames[self.amount_pos] = 'amount'
        return fieldnames
    
    ##def format_name(self, line):
        ##line.split(
        ## render transaction_name_template
    
    
class TransactionType(models.Model):
    def __unicode__(self):
        return '%s' % (self.name)
    
    ##AND_DELIMITER = '&&'
    OR_DELIMITER = '||'
    
    name = models.CharField(max_length=100, help_text='e.g. transfer, card_payment, direct_debit')
    order = models.IntegerField(default=10) # apply matching in ascending order
    includes = models.CharField(max_length=100, blank=True, help_text='transaction includes any of these strings double-pipe delimited a||b') # used for matching
    
    def matches(self, transaction):
        #TODO: Maybe use the clever includes/excludes of CategoryRules?
        include_list = self.includes.split(self.OR_DELIMITER)
        if any([el.strip() in transaction for el in include_list ]):
            # remove the parts we matched on
            for each_part in include_list:
                transaction.replace(each_part.strip(), '')
            # skip anything after a comma and remove any whitespace left over
            return transaction.split(',')[0].strip()
        else:
            return False
        
    ####TODO: better to do a class method with icontains in the DB? No - wrong way round!!
    ###@classmethod
    ###def get_matching(transaction):
        ###TransactionType.objects.filter(includes__icontains=transaction)
    
# TODO: Add Tagging here!
class Transaction(models.Model):
    def __unicode__(self):
        return '%s : %s' % (self.date, self.name)
    
    name = models.CharField(max_length=100,) #TODO: Remove - not required?
    account = models.ForeignKey(Account)
    import_string = models.TextField(blank=True) # accepts multiline    
    date = models.DateField() # date recorded by Bank
    paid_on = models.DateField(null=True) # date recorded within transfer of actual card swipe (optional)
    payee = models.CharField(max_length=100)
    transaction_type = models.ForeignKey(TransactionType, null=True)
    # Transfers between accounts -- assign to "Transfer" Category?
    
    # filter on debit / credit / transfer - seperate field (payment_type?) or helper function?

    
    #!!!!!!!!!!!!!!!!! Still not sure about how to do split transactions !!!!!!!!!
    # e.g. should the creditor / payee always be in the top section? or can each part go each way?
    # if it's for a card payment, probably only one way - cash however, could be split afterwards!
class TransactionPart(models.Model):
    """ All monitory parts are stored in TransactionAmounts so that transactions can be split
    """
    def __unicode__(self):
        return '%d: %s %s' % (self.id, self.amount, self.category)
    
    transaction = models.ForeignKey(Transaction)
    category = models.ForeignKey(Category, null=True) #, related_name="") # surely this can't be many to many for budgeting? # but it would be good for Tagging
    amount = models.DecimalField(max_digits=10,decimal_places=2)    
    reconceiled = models.NullBooleanField() # matched a planned transaction with real data ~ concept of linking planned and possible match of a real transaction which then merges the two together(?)
    description = models.TextField(blank=True) #TODO rename to Notes or Memo?
    
#TODO: Attach a signal to TransactionPart to update Account current balance    
    
class RecurringTransaction(models.Model):
    # inherit from Transaction? add frequency, start and end dates etc.
    # match against real transaction parts and set their reconceiled = True
    pass
    

    