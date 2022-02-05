import datetime

from dataclasses import field
from django.core.exceptions import NON_FIELD_ERRORS
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from Polls.models import Acao, Pergunta, Resposta, Respostas_usuario, Simulacao_cenarios, Usuario
from Portfolio.models import Carteiras
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = "__all__"
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }
        widgets = {
            'idade': forms.NumberInput(attrs={
                'autofocus': True
            })
        }

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        self.fields['perfil'].required = False
        self.fields['genero'].required = True

    def clean(self):
        cleaned_data = super().clean()
        idade = cleaned_data.get('idade')

        if (idade < 10 or idade > 99):
            self.add_error('idade', 'Idade Inválida')


class Perguntas(forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(Perguntas, self).__init__(*args, **kwargs)


class SurveyForm(forms.Form):

    #question_1 = forms.ChoiceField(widget=forms.RadioSelect, choices=())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #del self.fields["question_1"]
        for pergunta in Pergunta.objects.order_by('sequencia'):
            respostas = [(resposta.id, resposta.resposta)
                         for resposta in pergunta.resposta_set.all()]
            self.fields[f"pergunta_{pergunta.id}"] = forms.ChoiceField(
                widget=forms.RadioSelect, choices=respostas)
            self.fields[f"pergunta_{pergunta.id}"].label = pergunta.pergunta

    def save(self, userid):
        data = self.cleaned_data

        for pergunta in Pergunta.objects.order_by('sequencia'):
            choice = Resposta.objects.get(pk=data[f"pergunta_{pergunta.id}"])

            resp_user = Respostas_usuario()
            resp_user.data_inicial = datetime.datetime.now()
            resp_user.usuario = Usuario.objects.get(pk=userid)
            resp_user.resposta = choice
            resp_user.save()


class SimulatiomForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def quantidadeSimulacoes(self):
        return Simulacao_cenarios.objects.count()


class PortfolioForm(forms.Form):

    def __init__(self, acoes, *args, **kwargs):
        super().__init__(*args, **kwargs)

        acoesAll = Acao.objects.order_by('codigo')

        # adiciona todas as ações recomendadas antes
        if (acoes != None):
            for acao in acoes:
                # remove essa ação da lista geral para nao duplicar
                acoesAll = acoesAll.exclude(pk=acao.id)

                criaCamposForm.criaCamposBool(self, acao, True)

        # adiciona o restante
        for acao in acoesAll:
            criaCamposForm.criaCamposBool(self, acao, False)

    def save(self):
        data = self.cleaned_data

        selected = []

        # mudar para buscar cfe usuario
        for acao in Acao.objects.order_by('codigo'):
            checked = data[f"acao_{acao.id}"]
            if (checked):
                selected.append(acao)

        return selected

    def clean(self):
        data = super().clean()

        # mudar para buscar cfe usuario
        for acao in Acao.objects.order_by('codigo'):
            checked = data[f"acao_{acao.id}"]
            if (checked):
                return

        self.add_error(f"acao_{acao.id}", 'Selecione ao menos uma Ação')


class criaCamposForm():
    def criaCamposBool(form, obj, init):
        form.fields[f"acao_{obj.id}"] = forms.BooleanField(
            required=False, initial=init)
        form.fields[f"acao_{obj.id}"].label = obj.codigo + \
            ' - ' + obj.nome
