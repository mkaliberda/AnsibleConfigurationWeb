"""ansible_conf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from sites.views import SitesListView, SitesCreateEditForm, SiteDeleteView


urlpatterns = [
    path('create/<str:service_type>/', SitesCreateEditForm.as_view(), name='site_create_form'),
    path('delete-confirm/<uuid:uuid>/', SiteDeleteView.as_view(), name='site_delete_confirm_form'),
    path('list/<str:service_type>/', SitesListView.as_view(), name='site_list_view'),
]
