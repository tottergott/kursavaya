from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('decks/new/', views.deck_create_view, name='deck_create'),
    path('decks/demo/', views.create_demo_deck_view, name='create_demo_deck'),
    path('decks/<int:pk>/', views.deck_detail_view, name='deck_detail'),
    path('decks/<int:pk>/edit/', views.deck_edit_view, name='deck_edit'),
    path('decks/<int:pk>/delete/', views.deck_delete_view, name='deck_delete'),
    path('decks/<int:pk>/study/', views.deck_study_view, name='deck_study'),
    path('cards/<int:pk>/edit/', views.card_edit_view, name='card_edit'),
    path('cards/<int:pk>/delete/', views.card_delete_view, name='card_delete'),
    path('stats/', views.stats_view, name='stats'),
]

