"""
URL configuration for project_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.views.generic.base import RedirectView
from projects import views as auth_views

app_name = 'projects'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/projects/', permanent=False), name='index'),
    path('signup/', auth_views.signup_view, name='signup'),
    path('login/', auth_views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.UserLogoutView.as_view(), name='logout'),    
    path('projects/', include('projects.urls', namespace='projects')),
]
