# This Python file uses the following encoding: utf-8

from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User

from finance.models import Category, Transaction

class TenancyAgreement(models.Model): #TODO: Inherit from User like UserProfile?
    class Period:
        DAY = 'DAY'
        MONTH = 'MONTH'
        
        LIST = (
            (DAY, 'Day'),
            (MONTH, 'Month'),
            )
        
    user = models.ForeignKey(User) # TODO: many to many?
    category = models.ForeignKey(Category)
    start_date = models.DateField(auto_now=True) # move in
    end_date = models.DateField() # move out
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    rent_frequency = models.IntegerField()
    rent_period = models.CharField(max_length=50, choices=Period.LIST) # month/day

    deposit_amount = models.DecimalField(max_digits=10,decimal_places=2)
    deposit_paid = models.BooleanField()
    deposit_protection_scheme_submitted = models.DateField() # maybe this should be associated to an item in the statement, i.e. FK to Transaction?
    rentPaidTotal = 0    # clocked up over time
    
    def rent_payments(self):
        return self.category.objects.transaction_set.all()
        
    def get_rent_timedelta(self):
        if self.rent_period == self.Period.DAY:
            return timedelta(days=self.rent_frequency)
        elif self.rent_period == self.Period.MONTH:
            return timedelta()# TODO: calendar months!!!
        else:
            raise NotImplementedError

    @property
    def rent_per_day(self):
        return self.amount / self.get_rent_timedelta.days
        
    def get_total_rent_paid(self):
        return self.category.objects.transaction_set.aggregate(
            total=models.Sum('amount'))['total']