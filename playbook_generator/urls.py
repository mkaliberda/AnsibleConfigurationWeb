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
from playbook_generator.views import (PlaybookHomeView, PlaybookSelectTagViewForm, PlaybookUploadStepViewForm,
                                      PlaybookReviewStepViewForm, PlaybookInstructionStepViewForm, PlaybookStaticVarsForm,
                                      ListConfigsView, ConfigsDetailsView, ConfigDeleteView, ConfigEditView,
                                      CongigFileView)


urlpatterns = [
    path('', PlaybookHomeView.as_view(), name='playbook_home_view'),
    # path('playbook-form/<str:service_type>/step/select_tag/',
    #      PlaybookSelectTagViewForm.as_view(), name='playbook_step_select_tag'),
    path('playbook-form/<str:service_type>/step/upload/',
        PlaybookUploadStepViewForm.as_view(), name='playbook_step_upload'),
    path('playbook-form/<str:service_type>/step/review/<uuid:config_uuid>/',
        PlaybookReviewStepViewForm.as_view(), name='playbook_step_review'),
    path('playbook-form/<str:service_type>/step/instruction/<uuid:config_uuid>/',
        PlaybookInstructionStepViewForm.as_view(), name='playbook_step_instruction'),
    path('playbook-static-vars-form/<str:service_type>/<str:vars_type>/',
        PlaybookStaticVarsForm.as_view(), name='playbook_static_vars_form'),
    path('configs/<str:service_type>/',
        ListConfigsView.as_view(), name='config_list_view'),
    path('config-details/<str:service_type>/<uuid:uuid>/',
        ConfigsDetailsView.as_view(), name='config_details_view'),
    path('config-confirm-delete/<str:service_type>/<uuid:uuid>/',
        ConfigDeleteView.as_view(), name='config_delete_confirm_view',),
    path('config-edit/<str:service_type>/<uuid:uuid>/',
        ConfigEditView.as_view(), name='config_edit_view',),
    path('config-file-json/<str:service_type>/<uuid:uuid>/',
        CongigFileView.as_view(file_type=CongigFileView.JSON_FILE_TYPE), name='config_json_file_view',),
    path('config-file-yaml/<str:service_type>/<uuid:uuid>/',
        CongigFileView.as_view(file_type=CongigFileView.YAML_FILE_TYPE), name='config_yaml_file_view',),
]
