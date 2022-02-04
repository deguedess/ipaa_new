from django.db import models

from Polls.models import Acao, Simulacao_cenarios

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

    def __str__(self):
        return self.nome
