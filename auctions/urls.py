from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('create/', views.create_auction, name='create_auction'),
    path('bid/<int:auction_id>/', views.place_bid, name='place_bid'),
    path('profile/', views.profile_view, name='profile'),
    path("logout/", views.logout_view, name="logout"),
    path("bookmark/<int:auction_id>/", views.toggle_bookmark, name="toggle_bookmark"),


]



