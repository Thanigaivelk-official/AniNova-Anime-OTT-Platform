from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plans_view, name='plans'),
    path('checkout/<int:plan_id>/', views.initiate_checkout, name='checkout'),
]
