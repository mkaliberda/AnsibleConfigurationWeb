import yaml
import json

from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic

from playbook_generator.file_config_parsers import ParserFactory
from playbook_generator.forms import FileUploadVarsPlaybookForm, PlaybookModeForm
from playbook_generator.models import PlaybookServiceTypes
from playbook_generator.models import ConfigUpload


class PlaybookHomeView(generic.RedirectView):
    pattern_name = 'playbook_generator:playbook_step_select_tag'

    def dispatch(self, request, *args, **kwargs):
        kwargs['service_type'] = PlaybookServiceTypes.NUTANIX.value
        return super().dispatch(request, *args, **kwargs)


class PlaybookSelectTagViewForm(generic.FormView):
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
        self.uploaded_config = get_object_or_404(ConfigUpload, uuid=kwargs.get("config_uuid"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        file = request.FILES.get('uploaded_file')
        service_type = kwargs.get('service_type')
        if form.is_valid():
            parser_class = ParserFactory(event_type=service_type).parser_class(file_contents=file.read())
            parser_class.parse_file()
            # define a custom representer for strings
            def quoted_presenter(dumper, data):
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

            yaml.add_representer(str, quoted_presenter)

            self.uploaded_config.parsed_data=parser_class.parsed_data
            self.uploaded_config.config_json_file.save(
                f"upload_{int(timezone.now().timestamp())}.json",
                ContentFile(json.dumps(parser_class.get_json_dict(), indent=2))
            )
            self.uploaded_config.config_yml_file.save(
                f"upload_{int(timezone.now().timestamp())}.yaml",
                ContentFile(yaml.dump(
                    parser_class.get_yml_dict(self.uploaded_config.config_json_file.path),
                    default_flow_style=False, sort_keys=False, encoding='utf-8')
                )
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
            'smtp_address_to', 'smtp_address_from', 'prism_central_ip',
        ]
        kwargs.update({ 'uploaded_config': self.uploaded_config, 'not_display_key': not_display_key })
        return super().get_context_data(**kwargs)


class PlaybookInstructionStepViewForm(generic.TemplateView):
    template_name = 'step_instruction.html'

    def dispatch(self, request, *args, **kwargs):
        self.nodes_path = settings.STATIC_NODES_CONFIG_PATH
        self.uploaded_config = get_object_or_404(ConfigUpload,
                                                 uuid=kwargs.get("config_uuid"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({ 'uploaded_config': self.uploaded_config, 'nodes_path': self.nodes_path })
        return super().get_context_data(**kwargs)
