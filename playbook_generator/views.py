from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.core.files.storage import FileSystemStorage

from playbook_generator.file_config_parsers import ParserFactory
from playbook_generator.forms import FileUploadVarsPlaybookForm
from playbook_generator.models import PlaybookServiceTypes
from playbook_generator.models import ConfigUpload


class PlaybookHomeView(generic.RedirectView):
    pattern_name = 'playbook_generator:playbook_step_upload'

    def dispatch(self, request, *args, **kwargs):
        kwargs['service_type'] = PlaybookServiceTypes.NUTANIX.value
        return super().dispatch(request, *args, **kwargs)


class PlaybookUploadStepViewForm(generic.FormView):
    template_name = 'step_form_upload.html'
    form_class = FileUploadVarsPlaybookForm

    def get_success_url(self):
        return reverse('playbook_generator:playbook_step_review',
                       kwargs={'service_type': self.kwargs.get('service_type'),
                               'config_uuid': self.config_upload.uuid})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        file = request.FILES.get('uploaded_file')
        service_type = kwargs.get('service_type')
        if form.is_valid():
            parser_class = ParserFactory(event_type=service_type).parser_class(file_contents=file.read())
            parser_class.parse_file()
            self.config_upload = ConfigUpload.objects.create(parsed_data=parser_class.parsed_data)
            return redirect(to=self.get_success_url())
        else:
            return self.form_invalid(form)


class PlaybookReviewStepViewForm(generic.TemplateView):
    uploaded_config = None
    template_name = 'step_form_review.html'

    def dispatch(self, request, *args, **kwargs):
        self.uploaded_config = get_object_or_404(ConfigUpload,
                                                 uuid=kwargs.get("config_uuid"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({'uploaded_config': self.uploaded_config})
        return super().get_context_data(**kwargs)
