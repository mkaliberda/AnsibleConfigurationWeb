from typing import Tuple
from django.http.response import HttpResponse
import yaml
import json

from django.forms import formset_factory, modelformset_factory
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic

from playbook_generator.file_config_parsers import ParserFactory
from playbook_generator.forms import FileUploadVarsPlaybookForm, PlaybookModeForm, StaticVarsValueModelForm
from playbook_generator.models import PlaybookServiceTypes, StaticVarsValue, ConfigUpload
from sites.models import Site
from utils import YamlLoader

class PlaybookHomeView(generic.RedirectView):
    pattern_name = 'playbook_generator:playbook_step_upload'

    def dispatch(self, request, *args, **kwargs):
        kwargs['service_type'] = PlaybookServiceTypes.NUTANIX.value
        return super().dispatch(request, *args, **kwargs)


class PlaybookSelectTagViewForm(generic.FormView):
    """
    turned off
    form uses in playbook_step_upload
    """
    template_name = 'step_form_select_tag.html'
    form_class = PlaybookModeForm
    uploaded_config = None

    def get_success_url(self):
        return reverse('playbook_generator:playbook_step_upload',
                       kwargs={'service_type': self.kwargs.get('service_type'),
                               'config_uuid': self.uploaded_config.uuid if self.uploaded_config else ''})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid:
            self.uploaded_config = ConfigUpload.objects.create(tag=request.POST.get('tags'))
            return redirect(to=self.get_success_url())
        else:
            return self.form_invalid(form)


class PlaybookUploadStepViewForm(generic.FormView):
    template_name = 'step_form_upload.html'
    form_class = FileUploadVarsPlaybookForm
    uploaded_config = None

    def get_success_url(self):
        return reverse('playbook_generator:playbook_step_review',
                       kwargs={'service_type': self.kwargs.get('service_type'),
                               'config_uuid': self.uploaded_config.uuid})

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get('service_type')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None, service_type=None):
        """Return an instance of the form to be used in this view."""
        if service_type is None:
            service_type = self.service_type
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs(), service_type=service_type)

    def post(self, request, *args, **kwargs):
        service_type = kwargs.get('service_type')
        form_class = self.get_form_class()
        form = self.get_form(form_class, service_type=service_type)
        file = request.FILES.get('uploaded_file')
        site_name = request.POST.get('site')

        if form.is_valid():
            parser_class = ParserFactory(event_type=service_type).parser_class(file_contents=file.read())
            parser_class.parse_file()

            if site_name:
                site = Site.objects.get(name=site_name, service_type=service_type)

            self.uploaded_config, created = ConfigUpload.objects.update_or_create(
              tag=request.POST.get('tags'),
              site=site,
              service_type=service_type,
              defaults={
                'parsed_data': parser_class.parsed_data,
              }
            )

            self.uploaded_config.config_json_file.save(
                f"upload_{int(timezone.now().timestamp())}.json",
                ContentFile(json.dumps(parser_class.get_json_dict(), indent=2))
            )
            yaml_loader = YamlLoader()
            json_name = self.uploaded_config.config_json_file.name.split('/')[-1]
            parsed_yaml = parser_class.get_yml_dict(json_path=f"/tmp/{json_name}")
            self.uploaded_config.config_yml_file.save(
                f"upload_{int(timezone.now().timestamp())}.yaml",
                ContentFile(yaml_loader.yaml_dump(parsed_yaml)),
            )
            self.uploaded_config.save()
            return redirect(to=self.get_success_url())
        else:
            return self.form_invalid(form)


class PlaybookReviewStepViewForm(generic.TemplateView):
    template_name = 'step_form_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.uploaded_config = get_object_or_404(ConfigUpload, uuid=kwargs.get("config_uuid"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        not_display_key = [
            'cluster_license', 'aos', 'hypervisor_iso', 'skip_hypervisor', 'hypervisor_version',
            'nos_package', 'is_imaging', 'witness_appliance_version', 'witness_address',
            'cluster_init_successful',
            'ipmi_user', 'ipmi_password', 'asset_tag', 'image_now', 'hypervisor', 'ipmi_configure_now', 'is_bare_metal',
            'vlan_ipmi_name', 'pulse_enabled', 'pulse_email_contact',
            'smtp_address', 'smtp_protocol', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_security_mode',
            'smtp_address_to', 'smtp_address_from', 'prism_central_ip', 'hypervisor_ip', 'cvm_ip', 'vlan_vm_id_hd'
        ]
        kwargs.update({ 'uploaded_config': self.uploaded_config, 'not_display_key': not_display_key })
        return super().get_context_data(**kwargs)


class PlaybookInstructionStepViewForm(generic.TemplateView):
    template_name = 'step_instruction.html'

    def dispatch(self, request, *args, **kwargs):

        self.uploaded_config = get_object_or_404(ConfigUpload,
                                                 uuid=kwargs.get("config_uuid"))
        self.nodes_path = settings.CONFIGS_PATH.get(kwargs.get('service_type')).get(self.uploaded_config.tag)
        self.is_show_tags = self.uploaded_config.tag != ConfigUpload.DEPLOY
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'uploaded_config': self.uploaded_config, 'nodes_path': self.nodes_path, 'is_show_tags': self.is_show_tags })
        return super().get_context_data(**kwargs)


class PlaybookStaticVarsForm(generic.FormView):
    LOCATION_TYPE = "location"
    template_name = 'static_vars_form.html'
    form_class = modelformset_factory(StaticVarsValue, fields=('key', 'value',), can_delete=True)
    
    def get_success_url(self):
        return reverse(
            'playbook_generator:playbook_static_vars_form',
            kwargs={
                'service_type': self.kwargs.get('service_type'),
                'vars_type': self.vars_type,
            }
        )

    def get_form(self, form_class=None):
        super().get_form()
        self.is_common_location = self.kwargs.get('vars_type') == self.LOCATION_TYPE
        formset = self.get_form_class()
        form_qs = StaticVarsValue.objects.filter(
            service_type=self.kwargs.get('service_type'),
            is_common_location=self.is_common_location,
        )
        return formset(queryset=form_qs)

    def post(self, request, *args, **kwargs):
        self.is_common_location = kwargs.get('vars_type') == self.LOCATION_TYPE
        self.vars_type = kwargs.get('vars_type')
        formset = self.get_form_class()
        forms = formset(request.POST)
        for form in forms:
            if form.is_valid():
                if form.cleaned_data.get('key') and form.cleaned_data.get('value'):
                    if form.cleaned_data.get('DELETE') and form.cleaned_data.get('id'):
                        StaticVarsValue.objects.filter(
                            id=form.cleaned_data.get('id').id,
                            service_type=self.kwargs.get('service_type')
                        ).delete()
                    elif form.cleaned_data.get('id'):
                        StaticVarsValue.objects.update_or_create(
                            id=form.cleaned_data.get('id').id,
                            is_common_location=self.is_common_location,
                            defaults={'value': form.cleaned_data.get('value'), 'key': form.cleaned_data.get('key')}
                        )
                    else:
                        StaticVarsValue.objects.update_or_create(
                            key=form.cleaned_data.get('key'),
                            is_common_location=self.is_common_location,
                            service_type=self.kwargs.get('service_type'),
                            defaults={ 'value': form.cleaned_data.get('value') }
                        )
        return redirect(to=self.get_success_url())


class ConfigsDetailsView(generic.TemplateView):
    template_name = 'config_details.html'

    def dispatch(self, request, *args, **kwargs):
        self.uploaded_config = get_object_or_404(ConfigUpload, uuid=kwargs.get("uuid"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        not_display_key = []
        kwargs.update({
            'uploaded_config': self.uploaded_config,
            'not_display_key': not_display_key,
        })
        return super().get_context_data(**kwargs)


class ConfigEditView(generic.TemplateView):
    template_name = 'config_edit.html'

    def get_success_url(self):
        return reverse(
            'playbook_generator:config_edit_view',
            kwargs={
                'service_type': self.kwargs.get('service_type'),
                'uuid': self.kwargs.get("uuid"),
            }
        )

    def dispatch(self, request, *args, **kwargs):
        self.uploaded_config = get_object_or_404(ConfigUpload, uuid=kwargs.get("uuid"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'uploaded_config': self.uploaded_config,
            'not_display_key': [],
        })
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        updated_parsed_data = {'nodes': {}}
        for c_key, c_value in self.uploaded_config.parsed_data.items():
            if c_key == 'nodes':
                for node_index, (node_key, node_value) in enumerate(c_value.items()):
                    if node_key == 'group':
                        updated_parsed_data['nodes']['group'] = 'nodes'
                    else:
                        updated_parsed_data['nodes'][node_key] = {}
                        for nv_key in node_value.keys():
                            updated_parsed_data['nodes'][node_key][nv_key] = request.POST.get(f"node{node_index}_{nv_key}")
            else:
                updeted_data = self.uploaded_config.parsed_data.get(c_key)
                updated_parsed_data[c_key] = { **updeted_data, 'value': request.POST.get(c_key)}
        self.uploaded_config.parsed_data = updated_parsed_data
        self.uploaded_config.save()
        return redirect(to=self.get_success_url())


class ConfigDeleteView(generic.DeleteView):
    template_name = 'components/form_delete_confirm.html'

    def get_success_url(self):
        self.success_url = reverse('playbook_generator:config_list_view',
                                   kwargs={'service_type': self.object.service_type})
        return super().get_success_url()

    def get_object(self, queryset=None):
        configObj = get_object_or_404(ConfigUpload, uuid=self.kwargs.get("uuid"))
        return configObj

    def get_context_data(self, **kwargs):
        not_display_key = []
        configObj = self.get_object()
        kwargs.update({
            'warning_text': f"Uploaded config for site {configObj.site.name} will be deleted. Are you sure?",
        })
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = ConfigUpload.objects.get(uuid=self.kwargs.get("uuid"))
        if request.POST.get('confirm_delete', None):
            self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


class ListConfigsView(generic.ListView):
    model = ConfigUpload
    queryset = ConfigUpload.objects.all()
    template_name = 'config_table.html'
    context_object_name = 'configs'

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(service_type=self.service_type)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)


class ListConfigsView(generic.ListView):
    model = ConfigUpload
    queryset = ConfigUpload.objects.all()
    template_name = 'config_table.html'
    context_object_name = 'configs'

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(service_type=self.service_type)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)


class ListConfigsView(generic.ListView):
    model = ConfigUpload
    queryset = ConfigUpload.objects.all()
    template_name = 'config_table.html'
    context_object_name = 'configs'

    def dispatch(self, request, *args, **kwargs):
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(service_type=self.service_type)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)

class CongigFileView(generic.View):
    JSON_FILE_TYPE = "JSON_FILE_TYPE"
    YAML_FILE_TYPE = "YAML_FILE_TYPE"
    file_type = JSON_FILE_TYPE

    def dispatch(self, request, *args, **kwargs):
        self.uploaded_config = get_object_or_404(ConfigUpload, uuid=kwargs.get("uuid"))
        self.service_type = kwargs.get("service_type")
        return super().dispatch(request, *args, **kwargs)

    # def get_queryset(self):
    #     return super().get_queryset().filter(service_type=self.service_type)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'service_type': self.service_type })
        return super().get_context_data(**kwargs)

    def get_yaml(self):
        parser_class = ParserFactory(event_type=self.service_type).parser_class(
            parsed_data=self.uploaded_config.parsed_data,
        )
        json_name = self.uploaded_config.config_json_file.name.split('/')[-1]
        yaml_loader = YamlLoader()
        parsed_yaml = parser_class.get_yml_dict(json_path=f"/tmp/{json_name}")
        file_name = f"upload_{int(timezone.now().timestamp())}.yaml"
        yaml_file = ContentFile(
            content=yaml_loader.yaml_dump(parsed_yaml),
        )
        
        self.uploaded_config.config_yml_file.save(file_name, yaml_file)
        response = HttpResponse(yaml_file, content_type='text/x-yaml')
        response["Content-Disposition"] = f"filename={file_name}"
        return response


    def get_json(self):
        parser_class = ParserFactory(event_type=self.service_type).parser_class(
            parsed_data=self.uploaded_config.parsed_data,
        )
        self.uploaded_config.config_json_file.save(
            f"upload_{int(timezone.now().timestamp())}.json",
            ContentFile(json.dumps(parser_class.get_json_dict(), indent=2))
        )
        return JsonResponse(parser_class.get_json_dict(), json_dumps_params={'indent': 2}, safe=False)

    def get(self, request, *args, **kwargs):
        if self.file_type == self.JSON_FILE_TYPE:
            return self.get_json()
        if self.file_type == self.YAML_FILE_TYPE:
            return self.get_yaml()
