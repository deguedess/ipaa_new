from django.db import models

from Polls.models import Acao, Motivo, Simulacao_cenarios, Usuario


# Create your models here.
#
# Carteira


class Carteiras(models.Model):
    nome = models.CharField(
        max_length=100, help_text='Informe o nome da carteira')

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, null=False)

    tipo_grupo = models.IntegerField()  # 0 = IA, 1 = Manual

    acoes = models.ManyToManyField(
        Acao, help_text='Informe as ações da carteira')

    def __str__(self):
        return str(self.usuario.id) + " - " + self.nome

    class Meta:
        verbose_name = 'Carteira'
        verbose_name_plural = 'Carteiras'


#
# Historico da carteira


class Hist_alt_carteira(models.Model):
    acao = models.ForeignKey(
        Acao, on_delete=models.CASCADE, null=False)

    carteira = models.ForeignKey(
        Carteiras, on_delete=models.CASCADE, null=False)

    data_alt = models.DateTimeField(
        null=False, blank=False, auto_now_add=True)

    oper = (
        ('C', 'Compra'),
        ('V', 'Venda'),
    )

    operacao = models.CharField(
        max_length=1,
        choices=oper,
        blank=True,
        help_text='Tipo de Operação',
    )

    recomendacao_ia = models.BooleanField()

    seguiu_recomendacao = models.BooleanField()

    motivo = models.ForeignKey(
        Motivo, on_delete=models.CASCADE, null=False)

    simulacao = models.ForeignKey(
        Simulacao_cenarios, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.carteira.nome

    class Meta:
        verbose_name = 'Histórico Carteira'
        verbose_name_plural = 'Histórico Carteiras'
