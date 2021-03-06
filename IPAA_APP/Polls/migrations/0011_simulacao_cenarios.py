# Generated by Django 3.2.8 on 2021-11-23 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0010_rename_simulacao_simulacao_cenario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Simulacao_cenarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Informe o nome da simulação', max_length=100)),
                ('descricao', models.CharField(help_text='Informe a descrição da simulação', max_length=300, null=True)),
                ('data_ini', models.DateField()),
                ('data_fim', models.DateField()),
            ],
        ),
    ]
