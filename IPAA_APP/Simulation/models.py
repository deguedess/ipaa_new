from django.db import models

from Polls.models import Acao, Simulacao_cenarios
from Portfolio.models import Carteiras

# Create your models here.
#


#
# Ações da simulação


class Simulacao_acao(models.Model):
    acao = models.ForeignKey(
        Acao, on_delete=models.CASCADE, null=False)

    simulacao = models.ForeignKey(
        Simulacao_cenarios, on_delete=models.CASCADE, null=False)

    valor_ant = models.DecimalField(
        max_digits=7, decimal_places=2)

    valor_novo = models.DecimalField(
        max_digits=7, decimal_places=2)

    classificacao_ia = models.CharField(
        max_length=100, blank=True)

    valor_movimentacao = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)

    valor_retorno = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)

    desvio_padrao = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)

    dividend_yeld = models.DecimalField(
        max_digits=7, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.simulacao.nome + " - " + self.acao.nome

    class Meta:
        verbose_name = 'Simulação de Ação'
        verbose_name_plural = 'Simulação de Ações'


class Carteira_Simulacao(models.Model):
    carteira = models.ForeignKey(
        Carteiras, on_delete=models.CASCADE, null=False)

    simulacao = models.ForeignKey(
        Simulacao_cenarios, on_delete=models.CASCADE, null=False)

    percentual = models.DecimalField(
        max_digits=7, decimal_places=2)

    class Meta:
        verbose_name = 'Carteira Simulação'
        verbose_name_plural = 'Carteira Simulações'
