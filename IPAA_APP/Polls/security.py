

from Polls.models import Respostas_usuario
from Polls.portfolio import calculaPortfolio


class checkAccess():

    def canAccessSimulation(userid, simula):

        cart = calculaPortfolio.verificaCarteira(userid)

        if (cart == None):
            return True

        print(simula)

        if (simula == None):
            hist = calculaPortfolio.getHistoricoAlteracaoCart(cart)
        else:
            hist = calculaPortfolio.getHistoricoAlteracao(cart, simula)

        print(hist)
        return False if hist.exists() else True

    def canAccessPolls(userid):
        return False if Respostas_usuario.objects.filter(usuario_id=userid).exists() else True
