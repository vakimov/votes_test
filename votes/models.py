# -*- coding: utf-8 -*-
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


class Voting(models.Model):
    datetime = models.DateTimeField()
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(verbose_name='Описание')
    user = models.ForeignKey(User)
    voted_users = models.ManyToManyField(User, related_name='voted_voteings')

    @property
    def choices(self):
        return Choice.objects.filter(voting=self)  # .order_by('order')

    @property
    def total_votes(self):
        n = 0
        for ch in self.choices:
            n += ch.votes
        return n


class VotingDelay(models.Model):
    voting = models.ForeignKey(Voting)
    ip = models.IPAddressField()
    delay_level = models.IntegerField(default=0)
    relieve_datetime = models.DateTimeField()

    @property
    def delay(self):
        return min(timedelta(minutes=3 ** self.delay_level), timedelta(days=7))


class Choice(models.Model):
    description = models.CharField(max_length=200)
    order = models.IntegerField()
    voting = models.ForeignKey(Voting)
    votes = models.IntegerField(default=0)

    @property
    def votes_percent(self):
        return self.votes / self.voting.total_votes * 100
