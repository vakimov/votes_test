from django.contrib import admin

from .models import Voting, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice


class VotingAdmin(admin.ModelAdmin):
    inlines = [
        ChoiceInline,
    ]

admin.site.register(Voting, VotingAdmin)
