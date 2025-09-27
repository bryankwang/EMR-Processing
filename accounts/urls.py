from django.urls import path
from . import views
urlpatterns = [
    path('', views.login, name='accounts.login'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
]