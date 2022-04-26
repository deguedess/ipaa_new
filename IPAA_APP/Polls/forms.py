import datetime

from django.core.exceptions import NON_FIELD_ERRORS
from django import forms
from Polls.models import Acao, Motivo, Pergunta, Resposta, Respostas_usuario, Usuario
from Polls.portfolio import calculaPortfolio
from Polls.simulation import calculaSimulacoes
from Portfolio.models import Carteiras
from django.utils.translation import ugettext_lazy as _

# Formulário de cadastro do usuário


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

    def getCarteira(userid):
        return Carteiras.objects.get(usuario_id=userid)

    def getAcoesSimulacao(self, simula, disabled, recomended):

        simu = calculaSimulacoes.getAcoesSimulacoes(simula)

        if (recomended == None):
            recomended = []

        for obj in simu:
            criaCamposForm.criaCamposBool(
                self, obj.acao, True if obj.acao in recomended else False)
            self.fields[f"acao_{obj.acao.id}"].widget.attrs['disabled'] = disabled

        return self

    def save(self, listaAcoesSimula, listaAll):

        selected = []

        for acSimula in listaAcoesSimula:
            acao = acSimula.acao

            if (f"acao_{acao.id}" in listaAll):
                selected.append(acao)

        return selected

    def cleanCheck(self, listaAcoesSimula, listaAll, ultimoCenario):

        if (ultimoCenario):
            return

        values = SimulatiomForm.save(self, listaAcoesSimula, listaAll)

        if (values == None or not values):
            self.add_error(
                None, 'Você deve selecionar ao menos uma ação antes de prosseguir')


class PortfolioForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getAcoesPortfolio(self, recomend):

        simu = calculaSimulacoes.getAcoesSimulacoes(
            calculaSimulacoes.getSimulacaoInicial())

        acoesAll = []
        for si in simu:
            acoesAll.append(si.acao)

        # adiciona todas as ações recomendadas antes
        if (recomend != None):
            for acao in recomend:
                # remove essa ação da lista geral para nao duplicar
                acoesAll.remove(acao)

                criaCamposForm.criaCamposBool(self, acao, True)

        # adiciona o restante
        for acao in acoesAll:

            criaCamposForm.criaCamposBool(self, acao, False)

        return self

    def save(self, listaAcoesSimula, listaAll):

        selected = []

        for acSimula in listaAcoesSimula:
            acao = acSimula.acao

            if (f"acao_{acao.id}" in listaAll):
                selected.append(acao)

        return selected

    def cleanCheck(self, listaAcoesSimula, listaAll):

        values = PortfolioForm.save(self, listaAcoesSimula, listaAll)

        if (values == None or not values):
            self.add_error(
                None, 'Você deve selecionar ao menos uma ação antes de prosseguir')


class MotivoForm(forms.Form):

    hists = []

    def __init__(self, simulacao, carteira, *args, **kwargs):
        super().__init__(*args, **kwargs)

        MotivoForm.hists = calculaPortfolio.getNaoSeguiuRecomendacao(
            simula=simulacao, carteira=carteira)

        if (MotivoForm.hists == None):
            return

        for hist in MotivoForm.hists:
            self.fields[f"hist_{hist.id}"] = forms.ModelChoiceField(
                queryset=Motivo.objects.filter(aparece=True)
            )
            self.fields[f"hist_{hist.id}"].label = calculaPortfolio.getNomeOperacao(hist) + \
                ' - ' + hist.acao.codigo

    def save(self):
        data = self.cleaned_data

        if (MotivoForm.hists == None):
            return

        for hist in MotivoForm.hists:
            choice = data[f"hist_{hist.id}"]

            hist.motivo = choice
            hist.save()

# Metodo generico para geração dos campos na tela


class criaCamposForm():
    def criaCamposBool(form, obj, init):
        form.fields[f"acao_{obj.id}"] = forms.BooleanField(
            required=False, initial=init)
        form.fields[f"acao_{obj.id}"].label = obj.codigo + \
            ' - ' + obj.nome
