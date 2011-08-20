# This Python file uses the following encoding: utf-8

from django.contrib import admin

from finance.models import Account, AccountType, Budget, BudgetEstimate, Category, CategoryGroup, CategoryRule, CsvImportProfile, RecurringTransaction, Transaction, TransactionPart, TransactionType

class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'type', 'current_balance')
admin.site.register(Account, AccountAdmin)

class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(AccountType, AccountTypeAdmin)

class BudgetEstimateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'budget', 'amount') # 'is_active'
    list_filter = ('budget', 'category',)
    search_fields = ('name',)
admin.site.register(BudgetEstimate, BudgetEstimateAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_group')
admin.site.register(Category, CategoryAdmin)

class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(CategoryGroup, CategoryGroupAdmin)

class TransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('name', 'date', 'payee', 'transaction_type')
    list_filter = ('account', 'transaction_type')
    search_fields = ('name', 'import_string')
admin.site.register(Transaction, TransactionAdmin)

class TransactionPartAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'amount', 'category', 'reconceiled')
    list_filter = ('category', 'reconceiled')
admin.site.register(TransactionPart, TransactionPartAdmin)


admin.site.register(Budget)
admin.site.register(CategoryRule)
admin.site.register(CsvImportProfile)
admin.site.register(RecurringTransaction)
admin.site.register(TransactionType)


