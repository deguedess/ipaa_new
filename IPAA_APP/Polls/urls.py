from django.urls import path
from . import views

app_name = 'IPAA'
urlpatterns = [
    path('', views.index, name='index'),
    path('polls', views.polls, name='polls'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('<int:pk>/simulation', views.simulation, name='simulation'),
    path('end', views.end, name='end'),
    path('error', views.error, name='error'),
    path('config', views.config, name='config'),
    path('configCluster', views.configCluster, name='configCluster'),
    path('motivo', views.motivo, name='motivo'),

]
