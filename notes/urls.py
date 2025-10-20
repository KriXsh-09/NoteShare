from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
path('', views.index, name='index'),
path('home/', views.home, name='home'),
path('my_upload/', views.my_upload, name='my_upload'),
path('delete/<int:note_id>/', views.delete_note, name='delete'),
path('upload/', views.upload, name='upload'),
path('note/<int:note_id>/', views.view_note, name='view_note'),
path('search/', views.search_notes, name='search_notes'),
path('register/', views.register, name='register'),
path('login/', auth_views.LoginView.as_view(template_name='notes/login.html'), name='login'),
path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]