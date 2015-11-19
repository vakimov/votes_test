# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0003_voting_voted_users'),
    ]

    operations = [
        migrations.CreateModel(
            name='VotingDelay',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('ip', models.IPAddressField()),
                ('delay_level', models.IntegerField(default=0)),
                ('relieve_datetime', models.DateTimeField()),
                ('voting', models.ForeignKey(to='votes.Voting')),
            ],
        ),
    ]
