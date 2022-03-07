# Generated by Django 3.2.8 on 2022-02-23 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0015_auto_20220223_1649'),
        ('Portfolio', '0005_auto_20220223_1649'),
        ('Simulation', '0005_alter_simulacao_acao_simulacao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='simulacao_acao',
            options={'verbose_name': 'Simulação de Ação', 'verbose_name_plural': 'Simulação de Ações'},
        ),
        migrations.CreateModel(
            name='Carteira_Simulacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentual', models.DecimalField(decimal_places=2, max_digits=7)),
                ('carteira', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Portfolio.carteiras')),
                ('simulacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polls.simulacao_cenarios')),
            ],
            options={
                'verbose_name': 'Carteira Simulação',
                'verbose_name_plural': 'Carteira Simulações',
            },
        ),
    ]