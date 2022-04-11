import datetime
from Polls.models import Perfil, Respostas_usuario, Simulacao_cenarios, Usuario, Motivo
from Polls.simulation import calculaSimulacoes
from Portfolio.models import Carteiras, Hist_alt_carteira

# Metodo para buscar as respostas do usuario e definir o perfil


class calculaPortfolio():

    def verificaPerfil(userid):

        pontos = 0
        for resposta in Respostas_usuario.objects.filter(usuario_id=userid):
            pontos += resposta.resposta.pontuacao

        ptos = int(pontos)

        try:
            perf = Perfil.objects.get(
                peso_inicial__lte=ptos, peso_final__gte=ptos)

            user = Usuario.objects.get(id=userid)
            user.perfil = perf
            user.save()

        except Exception as e:
            perf = 'Perfil Não Encontrado'
            print(e)

        return perf

    def getMotivos(nomeMotivo):

        try:
            return Motivo.objects.get(nome=nomeMotivo)
        except Exception as e:
            motivo = Motivo()
            motivo.nome = nomeMotivo
            motivo.aparece = False
            motivo.save()
            return motivo


# metodo para criação da carteira inicial

    def criaCarteiraSemAcoes(userid, tipoGrupo):

        cart = calculaPortfolio.verificaCarteira(userid)

        if (cart != None):
            return cart

        cart = Carteiras()
        cart.usuario = Usuario.objects.get(pk=userid)
        cart.tipo_grupo = tipoGrupo
        cart.nome = 'Carteira ' + 'Automática' if tipoGrupo == 0 else 'Manual'
        cart.save()

        # if (cart.tipo_grupo == 0):
        #  calculaPortfolio.registraAlteracoes(
        #   acoes, cart, 'C', True, True, None, None)

        return cart

    def criaAcoesCarteira(cart, acoes):
        if (acoes != None):
            cart.acoes.set(acoes)
            cart.save()

    def verificaCarteira(userid):
        cart = Carteiras.objects.filter(usuario_id=userid)

        if (cart.count() == 0):
            return None
        else:
            return cart[0]

    def salvaHistoricoCarteiraManual(cart, acoesSel, simula):

        acoesCart = cart.acoes.all()

        # verificar as acoes selecionadas
        for acSel in acoesSel:
            # Se a ação selecionada nao estiver na carteira, registra a alteração
            if (acSel not in acoesCart):
                calculaPortfolio.registraAlteracao(
                    acSel, cart, 'C', False, False, None, simula)

        # verifica as ações na carteira
        for acCat in acoesCart:
            if (acCat not in acoesSel):
                calculaPortfolio.registraAlteracao(
                    acCat, cart, 'V', False, False, None, simula)

    def salvaHistoricoCarteiraIA(cart, acoesSel, acoesRec, simula):
        acoesCart = cart.acoes.all()
        recomend = calculaPortfolio.getMotivos('Recomendação')

        # verifica as acoes selecionadas = COMPRAS
        for acSel in acoesSel:
            # se a ação nao estiver na carteira, houve alteração, nesse caso ADICIONADA
            if (acSel not in acoesCart):
                # verifica se a alteração foi recomendada ou nao
                if (acSel in acoesRec):
                    calculaPortfolio.registraAlteracao(
                        acSel, cart, 'C', True, True, recomend, simula)
                else:  # se nao for recomendação
                    calculaPortfolio.registraAlteracao(
                        acSel, cart, 'C', False, False, None, simula)

        # verificar as ações na carteira = VENDAS
        for acCart in acoesCart:
            # se a ação nao estiver na selecionadas, houve alteração, nesse caso foi REMOVIDA
            if (acCart not in acoesSel):
                # verificar se a venda foi recomendada ou nao
                if (acCart in acoesRec):
                    print('ok')
                    # calculaPortfolio.registraAlteracao(
                    # acCart, cart, 'V', False, False, None, simula)
                else:  # se nao for recomendação
                    calculaPortfolio.registraAlteracao(
                        acCart, cart, 'V', True, True, recomend, simula)
            else:  # se ela estiver selecionada, verifica se houve recomendação ou nao
                # verificar se a venda foi recomendada ou nao
                if (acCart not in acoesRec):
                    calculaPortfolio.registraAlteracao(
                        acCart, cart, 'V', False, False, None, simula)

         # Verifica as RECOMENDADAS
        for acRec in acoesRec:
            if (acRec not in acoesSel):
                calculaPortfolio.registraAlteracao(
                    acRec, cart, 'C', True, False, None, simula)

    def salvaPortfolio(carteira, acoesSelected, recomended, simula):

        # se for a ultima simulacao, entao nao vai alterar nada na carteira, nem no historico
        if (simula == calculaSimulacoes.getUltimaSimulacao()):
            return

        if (carteira.tipo_grupo == 0):
            calculaPortfolio.salvaHistoricoCarteiraIA(
                carteira, acoesSelected, recomended, simula)
        else:
            calculaPortfolio.salvaHistoricoCarteiraManual(
                carteira, acoesSelected, simula)

        # salva as acoes na carteira
        carteira.acoes.set(acoesSelected)
        carteira.save()


# metodo para salvar alteração de carteira


    def registraAlteracao(acao, carteira, oper, recIA, segRec, motivo, simulacao):

        if (motivo == None):
            if (carteira.tipo_grupo == 1):
                motivo = calculaPortfolio.getMotivos('Escolha Pessoal')
            else:
                motivo = calculaPortfolio.getMotivos('Não Seguiu')

        hist = Hist_alt_carteira()
        hist.acao = acao
        hist.carteira = carteira
        hist.data_alt = datetime.datetime.now()
        hist.operacao = oper
        hist.recomendacao_ia = recIA
        hist.seguiu_recomendacao = segRec
        hist.motivo = motivo
        hist.simulacao = Simulacao_cenarios.objects.get(
            pk=1) if simulacao == None else simulacao
        hist.save()

    def registraAlteracoes(acoes, carteira, oper, recIA, segRec, motivo, simulacao):
        if (acoes.count() == 0):
            return
        for acao in acoes:
            calculaPortfolio.registraAlteracao(
                acao, carteira, oper, recIA, segRec, motivo, simulacao)

    def getHistoricoAlteracao(carteira, simula):
        return Hist_alt_carteira.objects.filter(carteira=carteira, simulacao=simula)

    def getHistoricoAlteracaoCart(carteira):
        return Hist_alt_carteira.objects.filter(carteira=carteira)

    def getNaoSeguiuRecomendacao(simula, carteira):
        rec = calculaPortfolio.getMotivos('Não Seguiu')

        simA = Hist_alt_carteira.objects.filter(
            motivo=rec, simulacao=simula, carteira=carteira).order_by('operacao')

        if (not simA):
            return None

        return simA

    def getNomeOperacao(histAlt):

        if (histAlt == None):
            return ''

        if (histAlt.operacao == 'C'):  # se foi compra
            if (histAlt.recomendacao_ia):  # e foi recomendado, então ele nao comprou
                return 'Não Seguiu Recomendação de Compra'
            else:
                return 'Operação sem Recomendação'  # comprou sem recomendação
        else:  # se foi venda
            if (histAlt.recomendacao_ia):  # e foi recomendado, então ele nao vendeu
                return 'Venda sem Recomendação'
            else:
                return 'Não Seguiu Recomendação de Venda'  # vendeu sem recomendação
