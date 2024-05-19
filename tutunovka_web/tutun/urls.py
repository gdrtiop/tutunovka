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
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/<str:stat>', views.profile, name='profile'),
    path('new_route', views.create_route, name='new_route'),
    path('save_route/<int:pk>', views.save_route, name='save_route'),
    path('route_detail/<int:route_id>/', views.route_detail, name='route_detail'),
    path('editing_route/<int:route_id>/', views.editing_route, name='editing_route'),
    path('update_note/<int:note_id>/', views.update_note, name='update_note'),
    path('complaints/', views.complaints, name='complaints'),
    path('create_complaint', views.create_complaint, name='create_complaint'),
    path('complaint_answer/<int:complaint_id>', views.complaint_answer, name='complaint_answer'),
    path('public_routes/', views.PublicRoutesPage.as_view(), name='public_routes'),
    path('public_routes/tags/<str:tag>/', views.PublicRoutesTagsPage.as_view(), name='public_routes_by_tags'),
    path('public_routes_search/', views.PublicRoutesSearchResults.as_view(), name='search_results_public'),
    path('public_routes_search/', views.PublicRoutesSearchResults.as_view(), name='search_results_public'),
    path('public_route_detail/<int:route_id>/', views.public_route_detail, name='public_route_detail'),
    path('post_route/<int:id>/', views.post_route, name='post_route'),
    path('get_tg_bot_token/', views.get_tg_token, name='tg_token'),
    path('get_tg_bot_token/', views.get_tg_token, name='tg_token'),
    path('api_yn_map/', views.yandex_maps, name='api_yn_map'),
]
