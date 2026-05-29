from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_page),
    path('create/', views.create_article),
    path('articles/', views.list_articles),
    path('comment/<int:article_id>/', views.add_comment),
    path('comments/<int:article_id>/', views.get_comments),
    path('', include('django_prometheus.urls')),
]