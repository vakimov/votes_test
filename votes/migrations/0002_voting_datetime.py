# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 18, 23, 50, 17, 79395, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
