# This Python file uses the following encoding: utf-8

from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

# Questions
"""
Should we store the original Imported File - this would allow re-imports..
"""

class CsvImportProfile(models.Model):
    class Seperator:
        COMMA = ','
        FULL_STOP = '.'
        LIST = (
            (COMMA, 'Comma ,'),
            (FULL_STOP, 'Full Stop .'),
            )
        
    name = models.CharField(max_length=100,)
    # CSV columns mapping
    date_pos = models.IntegerField(help_text='Zero indexed position')
    amount_pos = models.IntegerField(help_text='Zero indexed position')
    name_pos = models.IntegerField(help_text='Zero indexed position') # where the name of transaction is
    ##transaction_name_template = models.CharField(max_length=100,help_text='e.g. ${row[4]} from (${row[0]})')
    
    # date_format replaced with dateutil.parser - only we need to know dayfirst / monthfirst!
    dayfirst = models.BooleanField(default=True) # unless ure in america!
    ##date_format = models.CharField(max_length=100,) # samples %d.%m.%Y - link to pydocs!
    ##decimal_seperator = models.CharField(max_length=100,choices=Seperator.LIST) #TODO: Not yet supported!
    
    # CSV file settings
    header_row = models.IntegerField(help_text='Zero indexed row')
    data_start_row = models.IntegerField(help_text='Zero indexed row')
    ##encoding = models.CharField(max_length=100,choices=('utf-8', 'iso8859-1')
    column_delimiter = models.CharField(max_length=100,help_text="such as: , ; \t ")
    
    
    #@classmethod
    def match(self, file_in):
        raise NotImplementedError
    
    ##def format_name(self, line):
        ##line.split(
    
    
class AccountType(models.Model):
    """
    Includes: Debit / Credit / Savings / Mortgage
    
    Populated by initial_data.yaml which will load fixture every run of syncdb
    """
    name = models.CharField(max_length=100,)
    

class Account(models.Model):
    
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
    institution = models.CharField(max_length=100,)
    currency = models.CharField(max_length=100,choices=Currency.LIST)
    type = models.ForeignKey(AccountType)
    owner = models.ManyToManyField(User, related_name='account_owner') # Signatories
    shared_with = models.ManyToManyField(User, related_name='account_share') # Shared access to non-owners
    
    initial_balance = models.DecimalField(max_digits=10,decimal_places=2)
    current_balance = models.DecimalField(max_digits=10,decimal_places=2)


class CategoryGroup(models.Model):
    name = models.CharField(max_length=100,) # e.g. Property

class Category(models.Model): # Rename "Label" as this would be more applicable to "Tenant"
    name = models.CharField(max_length=100,)  # i18n contents?
    category_group = models.ForeignKey(CategoryGroup)
    #user = models.ForeignKey(User) #why?
    
# TODO: Link this to an Account to stop rules applied when your account doesn't have these categories?
class CategoryRule(models.Model):
    RULE_DELIMITER = '||'
    
    name = models.CharField(max_length=100, help_text="Rule name")
    category = models.ForeignKey(Category)
    order = models.IntegerField() # apply rules in ascending order
    
    #TODO: How about JSON List?
    includes = models.CharField(max_length=100, help_text="contains all these strings, double-pipe delimited a||b")
    excludes = models.CharField(max_length=100, help_text="must not contain any of these strings, double-pipe delimited a||b")
    
    def matches(self, transaction):
        """ If transaction contains all includes and none of the excludes
        """
        # this can be done better!
        include_list = self.includes.split(self.RULE_DELIMITER)
        exclude_list = self.excludes.split(self.RULE_DELIMITER)
        
        if any([ell in transaction for ell in exclude_list]):
            # matched an exclude item
            return False
        elif all([ell in transaction for ell in include_list]):
            # matched all include items
            return True
        else:
            # didn't match all the includes
            return False
        
    
# TODO: Add Tagging here!
class Transaction(models.Model):
    name = models.CharField(max_length=100,)
    import_string = models.TextField() # accepts multiline
    account = models.ForeignKey(Account)
    date = models.DateField() # TODO: DateTime?
    
    ###payee = models.CharField(max_length=100,) #?
    ###reconceiled = models.BooleanField(default=True) # matched a planned transaction with real data ~ concept of linking planned and possible match of a real transaction which then merges the two together(?)
    ###amount = models.DecimalField(max_digits=10,decimal_places=2)
    ###category = models.ManyToManyField(Category, related_)

    # Transfers between accounts -- assign to "Transfer" Category?
    
    # filter on debit / credit / transfer - seperate field (payment_type?) or helper function?

    
    #!!!!!!!!!!!!!!!!! Still not sure about how to do split transactions !!!!!!!!!
    # e.g. should the creditor / payee always be in the top section? or can each part go each way?
    # if it's for a card payment, probably only one way - cash however, could be split afterwards!
class TransactionAmount(models.Model):
    """ All monitory parts are stored in TransactionAmounts so that transactions can be split
    """
    transaction = models.ForeignKey(Transaction)
    category = models.ManyToManyField(Category, related_)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    ###creditor = models.CharField(max_length=100,) #replaced with Payee
    payee = models.CharField(max_length=100)
    reconceiled = models.BooleanField(default=True) # matched a planned transaction with real data ~ concept of linking planned and possible match of a real transaction which then merges the two together(?)
    description = models.TextField() #TODO rename to Notes or Memo?
    
class RecurringTransaction(models.Model):
    # inherit from Transaction? add frequency, start and end dates etc.
    pass
    
class Budget(models.Model):
    name = models.CharField(max_length=100,)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True,blank=True)
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
    
    