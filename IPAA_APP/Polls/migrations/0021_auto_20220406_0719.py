# Generated by Django 3.2.8 on 2022-04-06 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0020_auto_20220329_0728'),
    ]

    operations = [

        migrations.AddField(
            model_name='motivo',
            name='aparece',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]