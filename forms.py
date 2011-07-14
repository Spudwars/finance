from django import forms
from finance.models import Transaction, Category, Budget, BudgetEstimate

'''
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        #fields = ('transaction_type', 'notes', 'category', 'amount', 'date')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

class BudgetForm(forms.ModelForm):
    start_date = forms.DateTimeField(initial=datetime.datetime.now, required=False, widget=forms.SplitDateTimeWidget)
    class Meta:
        model = Budget
        fields = ('name', 'start_date')

class BudgetEstimateForm(forms.ModelForm):
    class Meta:
        model = BudgetEstimate
        fields = ('category', 'amount')
'''
