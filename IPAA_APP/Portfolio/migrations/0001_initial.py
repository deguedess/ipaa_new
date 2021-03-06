# Generated by Django 3.2.8 on 2021-11-23 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Polls', '0003_auto_20211118_1815'),
        ('Simulation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carteiras',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Informe o nome da carteira', max_length=100)),
                ('tipo_grupo', models.IntegerField()),
                ('acoes', models.ManyToManyField(help_text='Informe as ações da carteira', to='Polls.Acoes')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.usuarios')),
            ],
        ),
        migrations.CreateModel(
            name='Hist_alt_carteira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_alt', models.DateTimeField(auto_now_add=True)),
                ('operacao', models.IntegerField()),
                ('recomendacao_ia', models.BooleanField()),
                ('seguiu_recomendacao', models.BooleanField()),
                ('acao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.acoes')),
                ('carteira', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portfolio.carteiras')),
                ('motivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.motivos')),
                ('simulacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Simulation.simulacoes')),
            ],
        ),
    ]
