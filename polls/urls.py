from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.ShowView.as_view(), name='show'),
    path('<int:post_id>/comment/', views.comment, name='comment'),
    path('photos', views.photos, name='photos'),
    path('info', views.info, name='info'),
    path('search/<str:title>', views.search, name='search'),
    path('categories/<str:category>', views.categories, name='categories'),
]