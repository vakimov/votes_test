# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


class Voting(models.Model):
    # TODO: добавить дату голосования
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(verbose_name='Описание')
    user = models.ForeignKey(User)

    @property
    def choices(self):
        return Choice.objects.filter(voting=self)  # .order_by('order')

    @property
    def total_votes(self):
        n = 0
        for ch in self.choices:
            n += ch.votes
        return n


class Choice(models.Model):
    description = models.CharField(max_length=200)
    order = models.IntegerField()
    voting = models.ForeignKey(Voting)
    votes = models.IntegerField(default=0)

    @property
    def votes_percent(self):
        return self.votes / self.voting.total_votes * 100
