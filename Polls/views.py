from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView

from Polls.models import Pergunta, Usuario, Acao
from django.template import loader
from django.views import generic

from Polls.portfolio import calculaPortfolio
from .forms import RegisterUserForm, SurveyForm, PortfolioForm


# Create your views here.


def index(request):
    form = RegisterUserForm()

    if request.method == 'POST':
        try:
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                request.session['usuario'] = user.id
                return redirect('polls')
            else:
                for field in form:
                    print("Field Error:", field.name,  field.errors)
        except Exception as e:
            print(e)
            raise

    context = {
        'form': form,

    }

    return render(request, 'index.html', context)


def polls(request):
    form = SurveyForm()

    if request.method == 'POST':
        try:
            form = SurveyForm(request.POST)
            if form.is_valid():
                form = form.save(request.session['usuario'])
                return redirect('portfolio')
            else:
                for field in form:
                    print("Field Error:", field.name,  field.errors)
        except Exception as e:
            print(e)
            raise

    context = {
        "form": form,
    }
    return render(request, 'polls.html', context)


def portfolio(request):
    userid = request.session['usuario']

    tipo = userid % 2

    perf = calculaPortfolio.verificaPerfil(userid)

    # TODO
    acoesRec = None

    if (tipo == 0):
        acoesRec = Acao.objects.order_by('codigo')[:3]

    cart = calculaPortfolio.criaCarteira(
        userid, tipo, acoesRec)

    form = PortfolioForm(cart.acoes.all())

    if request.method == 'POST':
        form = PortfolioForm(acoesRec, request.POST)

        if form.is_valid():
            selected = form.save()

            calculaPortfolio.salvaPortfolio(cart, selected, acoesRec)

        else:
            for field in form:
                print("Field Error:", field.name,  field.errors)

    context = {
        "perf": perf,
        "form": form,
        "cart": cart,
    }
    return render(request, 'portfolio.html', context)


class UsuarioListView(generic.ListView):
    model = Usuario


class PerguntaListView(generic.ListView):
    model = Pergunta
    context_object_name = 'Perguntas'
    queryset = Pergunta.objects.filter()[:1]
    template_name = 'books/my_arbitrary_template_name_list.html'


class UserCreate(CreateView):
    model = Usuario
    fields = ['idade', 'genero', 'grau_instrucao', 'profissao']


def detail(request, question_id):
    question = get_object_or_404(Pergunta, pk=question_id)
    return render(request, 'detail.html', {'Pergunta': question})
