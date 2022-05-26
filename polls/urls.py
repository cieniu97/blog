from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('photos', views.photos, name='photos'),
    path('info', views.info, name='info'),
    path('search/<str:title>', views.search, name='search'),
    path('categories/<str:category>', views.categories, name='categories'),
    path('register', views.register, name='register'),
    path('user/register', views.storeUser, name='storeUser'),
    path('login', views.login, name='login'),
    path('user/login', views.loginUser, name='loginUser'),
    path('logout', views.logout, name='logout'),
    path('<int:pk>/', views.ShowView.as_view(), name='show'),
    path('<int:post_id>/comment/', views.storeComment, name='storeComment'),

]