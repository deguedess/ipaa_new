from django.contrib import admin

from Polls.models import Acao, Grau_Instrucao, Motivo, Perfil, Pergunta, Profissao, Resposta, Simulacao_cenarios, Usuario, Respostas_usuario
from Portfolio.models import Carteiras, Hist_alt_carteira
from Simulation.models import Carteira_Simulacao, Simulacao_acao


# Register your models here.


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'aparece')
    list_filter = ('aparece', 'nome')


@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nome')


@admin.register(Grau_Instrucao)
class Grau_InstrucaoAdmin(admin.ModelAdmin):
    pass


@admin.register(Profissao)
class ProfissaoAdmin(admin.ModelAdmin):
    pass


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'peso_inicial', 'peso_final', 'tipo')


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'status')


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'resposta', 'sequencia', 'pontuacao')
    list_filter = ('pergunta', 'pontuacao')
    fields = ['pergunta', 'resposta', ('sequencia', 'pontuacao')]


@admin.register(Simulacao_cenarios)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'data_ini', 'data_fim')


@admin.register(Usuario)
class Usuario(admin.ModelAdmin):
    list_display = ('id', 'idade', 'genero', 'grau_instrucao',
                    'profissao', 'data_cadastro', 'perfil')


@admin.register(Respostas_usuario)
class Resposta_usuario(admin.ModelAdmin):
    list_display = ('usuario', 'resposta', 'data_final')


@admin.register(Carteiras)
class Carteira(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'tipo_grupo')


@admin.register(Hist_alt_carteira)
class Hist_alt_carteira(admin.ModelAdmin):
    list_display = ('data_alt', 'carteira', 'operacao',
                    'acao', 'recomendacao_ia', 'seguiu_recomendacao', 'simulacao', 'motivo')
    list_filter = ('acao', 'carteira')


@admin.register(Simulacao_acao)
class Simulacao_acao(admin.ModelAdmin):
    list_display = ('acao', 'simulacao', 'valor_ant',
                    'valor_novo', 'classificacao_ia', 'valor_movimentacao', 'valor_retorno', 'desvio_padrao')
    list_filter = ('simulacao', 'acao', 'classificacao_ia')


@admin.register(Carteira_Simulacao)
class Carteira_Simulacao(admin.ModelAdmin):
    list_display = ('carteira', 'simulacao', 'percentual')
    list_filter = ('carteira', 'simulacao')
