"""
URL configuration for tutun project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from tutun_app import views
from tutun_app.views import UserRegisterView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('me-my', views.memy_page, name='me-my'),
    path('new_route', views.create_route, name='new_route'),
    path('route_detail/<int:route_id>/', views.route_detail, name='route_detail'),
]
