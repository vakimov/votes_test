# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('votes', '0002_voting_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='voted_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='voted_voteings'),
        ),
    ]
