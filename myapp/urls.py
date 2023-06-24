from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('home/', views.home, name="home"),
    path('findflight', views.findflight, name="findflight"),
    path('bookings', views.bookings, name="bookings"),
    path('addfile', views.addfile, name="addfile"),
    path('adminpage',views.adminpage,name= "adminpage"),
    path('view_bookings',views.view_bookings, name="view_bookings"),
    path('cancellings', views.cancellings, name="cancellings"),
    path('seebookings', views.seebookings, name="seebookings"),
    path('signup/', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('adminsignin', views.adminsignin, name="admin_home"),
    path('success', views.success, name="success"),
    path('signout', views.signout, name="signout"),

]
