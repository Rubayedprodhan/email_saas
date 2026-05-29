from django.urls import reverse_lazy
from .models import MediaFile
from django.shortcuts import redirect,get_object_or_404,render
import json
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import ListView,CreateView,FormView, TemplateView
from django.utils.timezone import now
from .utils import render_email_template
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import EmailBlock
from django.views.generic import ListView,CreateView
from django.db.models import Count,Q
from django.http import HttpResponse
from contacts.models import Contact
from .utils import render_email_template
from .models import Campaign,EmailTrack,ClickTrack,EmailTemplate
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import SavedSection,EmailBlockHistory
from .forms import CampaignForm, HTMLImportForm.
from django.http import JsonResponse

from .ai import optimize_subject_line, check_spam_score
from .tasks import send_campaign_email

from .forms import SpamCheckForm


class CampaignListView(
    LoginRequiredMixin,
    ListView
):

    model = Campaign

    template_name = 'campaigns/list.html'

    def get_queryset(self):

        campaigns = Campaign.objects.filter(
            user=self.request.user
        ).annotate(

            total_sent=Count(
                'emailtrack'
            ),

            total_opened=Count(
                'emailtrack',
                filter=Q(
                    emailtrack__opened=True
                )
            ),

            total_failed=Count(
                'emailtrack',
                filter=Q(
                    emailtrack__status='failed'
                )
            )
        )

        return campaigns

class CampaignCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Campaign

    form_class = CampaignForm

    template_name = 'campaigns/create.html'

    success_url = reverse_lazy(
        'campaign_list'
    )

    def get_form(self, form_class=None):

        form = super().get_form(form_class)

        form.fields['template'].queryset = (
            EmailTemplate.objects.filter(
                user=self.request.user
            )
        )

        return form

    def form_valid(self, form):

        campaign = form.save(
            commit=False
        )

        campaign.user = self.request.user

        contacts = Contact.objects.filter(
            user=self.request.user,
            is_subscribed=True
        )

        email_list = [
            contact.email
            for contact in contacts
        ]

        domain = (
            f"http://"
            f"{self.request.get_host()}"
        )

        if campaign.scheduled_time:

            campaign.status = 'scheduled'

            campaign.save()

            send_campaign_email.apply_async(
                args=[
                    campaign.id,
                    campaign.subject,
                    campaign.message,
                    email_list,
                    domain
                ],
                eta=campaign.scheduled_time
            )

        else:

            campaign.status = 'sent'

            campaign.save()

            send_campaign_email.delay(
                campaign.id,
                campaign.subject,
                campaign.message,
                email_list,
                domain
            )

        return redirect(
            'campaign_list'
        )


class EmailTemplateListView(
    LoginRequiredMixin,
    ListView
):

    model = EmailTemplate

    template_name = (
        'campaigns/template_list.html'
    )

    def get_queryset(self):

        return EmailTemplate.objects.filter(
            user=self.request.user
        )


class EmailTemplateCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = EmailTemplate

    fields = (
        'name',
        'html_content'
    )

    template_name = (
        'campaigns/template_create.html'
    )

    success_url = reverse_lazy(
        'template_list'
    )

    def get_form(self, form_class=None):

        form = super().get_form(form_class)

        form.fields['name'].widget.attrs.update({
            'class': 'form-control'
        })

        form.fields['html_content'].widget.attrs.update({
            'class': 'form-control',
            'rows': 12
        })

        return form

    def form_valid(
        self,
        form
    ):

        form.instance.user = (
            self.request.user
        )

        return super().form_valid(form)


def email_open_tracking(
    request,
    track_id
):

    try:

        track = EmailTrack.objects.get(
            id=track_id
        )

        if not track.opened:

            track.opened = True

            track.opened_at = now()

            track.save()

    except EmailTrack.DoesNotExist:
        pass

    pixel = (
        b'\x47\x49\x46\x38\x39\x61'
        b'\x01\x00\x01\x00\x80\x00'
        b'\x00\x00\x00\x00\xff\xff'
        b'\xff\x21\xf9\x04\x01\x00'
        b'\x00\x00\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02\x44\x01\x00'
        b'\x3b'
    )

    return HttpResponse(
        pixel,
        content_type='image/gif'
    )


def click_tracking(
    request,
    track_id
):

    track = get_object_or_404(
        ClickTrack,
        id=track_id
    )

    return HttpResponseRedirect(
        track.original_url
    )

class MediaUploadView(
    LoginRequiredMixin,
    CreateView
):

    model = MediaFile

    fields = ['file']

    template_name = (
        'campaigns/media_upload.html'
    )

    success_url = reverse_lazy(
        'media_upload'
    )

    def form_valid(self, form):

        form.instance.user = (
            self.request.user
        )

        return super().form_valid(form)



class MediaListView(
    LoginRequiredMixin,
    ListView
):

    model = MediaFile

    template_name = (
        'campaigns/media_list.html'
    )

    def get_queryset(self):

        return MediaFile.objects.filter(
            user=self.request.user
        )



class EmailBlockCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = EmailBlock

    fields = [
        'block_type',
        'content',
        'sort_order'
    ]

    template_name = (
        'campaigns/block_create.html'
    )

    def form_valid(self, form):

        template = EmailTemplate.objects.get(
            id=self.kwargs['template_id'],
            user=self.request.user
        )

        form.instance.template = template

        return super().form_valid(form)

    def get_success_url(self):

        return reverse_lazy(
            'template_builder',
            kwargs={
                'template_id':
                self.kwargs['template_id']
            }
        )




class TemplateBuilderView(
    LoginRequiredMixin,
    ListView
):

    model = EmailBlock

    template_name = (
        'campaigns/template_builder.html'
    )

    def get_queryset(self):

        template = EmailTemplate.objects.get(

            id=self.kwargs['template_id'],

            user=self.request.user
        )

        return template.blocks.all()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        context['template_id'] = (
            self.kwargs['template_id']
        )

        return context



class EmailPreviewView(
    LoginRequiredMixin,
    TemplateView
):

    template_name = (
        'campaigns/email_preview.html'
    )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        template = EmailTemplate.objects.get(

            id=self.kwargs['template_id'],

            user=self.request.user
        )

        html_content = render_email_template(
            template
        )

        context['html_content'] = (
            html_content
        )

        return context
    

def update_block_order(
    request
):

    if request.method == 'POST':

        data = json.loads(
            request.body
        )

        order = data.get(
            'order',
            []
        )

        for index, block_id in enumerate(order):

            EmailBlock.objects.filter(
                id=block_id
            ).update(
                sort_order=index
            )

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({
        'status': 'failed'
    })



@csrf_exempt
def update_block_content(
    request,
    block_id
):

    if request.method == 'POST':

        data = json.loads(
            request.body
        )

        content = data.get(
            'content'
        )

        block = EmailBlock.objects.get(
            id=block_id
        )

        EmailBlockHistory.objects.create(

    block=block,

    content=block.content,

    action_type='update'
)

        block.save()

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({
        'status': 'failed'
    })

def template_preview_api(
    request,
    template_id
):

    template = EmailTemplate.objects.get(

        id=template_id,

        user=request.user
    )

    html = render_email_template(
        template
    )

    return JsonResponse({
        'html': html
    })


def duplicate_block(
    request,
    block_id
):

    block = get_object_or_404(
        EmailBlock,
        id=block_id
    )

    EmailBlock.objects.create(

        template=block.template,

        block_type=block.block_type,

        content=block.content,

        sort_order=block.sort_order + 1
    )

    return redirect(
        'template_builder',
        template_id=block.template.id
    )



def export_template_html(
    request,
    template_id
):

    template = EmailTemplate.objects.get(

        id=template_id,

        user=request.user
    )

    html = render_email_template(
        template
    )

    response = HttpResponse(
        html,
        content_type='text/html'
    )

    response[
        'Content-Disposition'
    ] = (

        f'attachment; '
        f'filename="{template.name}.html"'
    )

    return response

class ImportHTMLTemplateView(
    LoginRequiredMixin,
    View
):

    template_name = (
        'campaigns/import_template.html'
    )

    def get(
        self,
        request
    ):

        form = HTMLImportForm()

        return render(request,self.template_name,{'form': form})

    def post(
        self,
        request
    ):

        form = HTMLImportForm(

            request.POST,

            request.FILES
        )

        if form.is_valid():

            html_file = request.FILES[
                'html_file'
            ]

            html_content = (
                html_file.read()
                .decode('utf-8')
            )

            template = EmailTemplate.objects.create(

                user=request.user,

                name=form.cleaned_data[
                    'name'
                ],

                html_content=html_content
            )

            return redirect(
                'template_builder',
                template_id=template.id
            )

        return render(

            request,

            self.template_name,

            {
                'form': form
            }
        )


def save_section(
    request,
    block_id
):

    block = get_object_or_404(

        EmailBlock,

        id=block_id
    )

    SavedSection.objects.create(

        user=request.user,

        name=f"{block.block_type} section",

        block_type=block.block_type,

        content=block.content
    )

    return redirect(

        'template_builder',

        template_id=block.template.id
    )


def add_saved_section(
    request,
    template_id,
    section_id
):

    template = EmailTemplate.objects.get(

        id=template_id,

        user=request.user
    )

    section = SavedSection.objects.get(

        id=section_id,

        user=request.user
    )

    EmailBlock.objects.create(

        template=template,

        block_type=section.block_type,

        content=section.content,

        sort_order=template.blocks.count()
    )

    return redirect(
        'template_builder',
        template_id=template.id
    )


class SavedSectionListView(
    LoginRequiredMixin,
    ListView
):

    model = SavedSection

    template_name = (
        'campaigns/saved_sections.html'
    )

    def get_queryset(self):

        return SavedSection.objects.filter(
            user=self.request.user
        )


def undo_block_change(
    request,
    block_id
):

    block = EmailBlock.objects.get(
        id=block_id
    )

    history = block.history.filter(

        action_type='update'

    ).order_by('-created_at').first()

    if history:

        current_content = block.content

        block.content = history.content

        block.save()

        history.content = current_content

        history.save()

    return JsonResponse({
        'status': 'success'
    })


def redo_block_change(
    request,
    block_id
):

    block = EmailBlock.objects.get(
        id=block_id
    )

    history = block.history.filter(

        action_type='update'

    ).order_by('-created_at').first()

    if history:

        current_content = block.content

        block.content = history.content

        block.save()

        history.content = current_content

        history.save()

    return JsonResponse({
        'status': 'success'
    })


class ABTestResultView(LoginRequiredMixin, TemplateView):

    template_name = "campaigns/ab_results.html"

    def get_context_data(self, **kwargs):

        campaign = Campaign.objects.get(
            id=self.kwargs['campaign_id']
        )

        context = super().get_context_data(**kwargs)

        context["campaign"] = campaign

        context["results"] = ABTestResult.objects.filter(
            campaign=campaign
        )

        return context

def ai_optimize_subject(
    request
):

    subject = request.POST.get(
        'subject'
    )

    optimized = optimize_subject_line(
        subject
    )

    return JsonResponse({

        'optimized_subject':
        optimized
    })