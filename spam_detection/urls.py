from django.urls import path
from . import views

app_name = 'spam_detection'

#Determine URL patterns for all the views.
urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('check-spam/', views.check_spam, name='check_spam'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('blacklist/', views.blacklist, name='blacklist'),
    path('whitelist/', views.whitelist, name='whitelist'),
    path('metrics/', views.evaluation_metrics, name='metrics'),
]
