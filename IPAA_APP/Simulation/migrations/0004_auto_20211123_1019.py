# Generated by Django 3.2.8 on 2021-11-23 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0008_simulacao'),
        ('Portfolio', '0003_alter_hist_alt_carteira_simulacao'),
        ('Simulation', '0003_rename_simulacoes_simulacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulacao_acao',
            name='simulacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.simulacao'),
        ),
        migrations.DeleteModel(
            name='Simulacao',
        ),
    ]
