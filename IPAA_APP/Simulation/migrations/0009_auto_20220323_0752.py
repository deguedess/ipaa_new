# Generated by Django 3.2.8 on 2022-03-23 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Simulation', '0008_simulacao_acao_valor_movimentacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='simulacao_acao',
            name='desvio_padrao',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='simulacao_acao',
            name='valor_retorno',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
    ]
