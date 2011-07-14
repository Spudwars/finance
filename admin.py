# This Python file uses the following encoding: utf-8

from django.contrib import admin

from finance.models import BudgetEstimate, Transaction


class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'date', 'amount')
    list_filter = ('category', 'reconceiled',)
    search_fields = ('name','import_string ',)


class BudgetEstimateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'budget', 'amount') # 'is_active'
    list_filter = ('budget', 'category',)
    search_fields = ('name',)


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(BudgetEstimate, BudgetEstimateAdmin)