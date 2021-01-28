from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('payments/', login_required(views.payments), name = 'payments'),
    path('payments/excel', login_required(views.excel_payments), name = 'payments_excel'),
    path('overdue/', login_required(views.overdue_view), name = 'overdue'),
    path('overdue/excel', login_required(views.excel_overdues), name='overdues_excel'),
    path('payments_purpose/', login_required(views.payments_purpose), name='payments_purpose'),
    path('payments_purpose/excel', login_required(views.excel_payments_purpose), name = 'payments_purpose_excel'),
    path('verifications/', login_required(views.verifications), name='verifications'),
    path('verifications/excel', login_required(views.excel_verifications), name='excel_verifications'),

    path('accounts/login/', views.user_login, name = 'login'),
    path('logout/', login_required(auth_views.LogoutView.as_view(template_name='changan/login.html')), name='logout'),
]