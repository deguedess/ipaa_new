# Generated by Django 3.2.8 on 2022-03-29 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0019_delete_simulacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulacao_cenarios',
            name='indice_previsao',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
