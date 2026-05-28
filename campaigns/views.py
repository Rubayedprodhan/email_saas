from django.urls import reverse_lazy

from django.shortcuts import (
    redirect,
    get_object_or_404
)

from django.http import (
    HttpResponse,
    HttpResponseRedirect
)

from django.utils.timezone import now

from django.contrib.auth.mixins import (
    LoginRequiredMixin
)

from django.views.generic import (
    ListView,
    CreateView
)

from django.db.models import (
    Count,
    Q
)

from contacts.models import Contact

from .models import (
    Campaign,
    EmailTrack,
    ClickTrack,
    EmailTemplate
)

from .forms import CampaignForm

from .tasks import send_campaign_email


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

    fields = [
        'name',
        'html_content'
    ]

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