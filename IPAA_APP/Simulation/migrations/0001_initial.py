# Generated by Django 3.2.8 on 2021-11-23 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Polls', '0003_auto_20211118_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Simulacoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Informe o nome da simulação', max_length=100)),
                ('descricao', models.CharField(help_text='Informe a descrição da simulação', max_length=300)),
                ('data_inicial', models.DateTimeField()),
                ('data_final', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Simulacao_acao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_ant', models.DecimalField(decimal_places=2, max_digits=7)),
                ('valor_novo', models.DecimalField(decimal_places=2, max_digits=7)),
                ('acao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.acoes')),
                ('simulacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Simulation.simulacoes')),
            ],
        ),
    ]
