from django import forms

from .models import (
    Campaign,
    EmailTemplate
)


class CampaignForm(forms.ModelForm):

    scheduled_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )

    class Meta:

        model = Campaign

        fields = [
            'subject',
            'message',
            'template',
            'scheduled_time'
        ]

        widgets = {
            'subject': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6
                }
            ),

            'template': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            )
        }