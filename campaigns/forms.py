# from django import forms

# from .models import (
#     Campaign,
#     EmailTemplate
# )


# class CampaignForm(forms.ModelForm):

#     scheduled_time = forms.DateTimeField(
#         required=False,
#         widget=forms.DateTimeInput(
#             attrs={
#                 'type': 'datetime-local',
#                 'class': 'form-control'
#             }
#         )
#     )

#     class Meta:

#         model = Campaign

#         fields = [
#             'subject',
#             'message',
#             'template',
#             'scheduled_time'
#             'is_ab_test',
# 'variant_a_subject',
# 'variant_b_subject',
# 'variant_a_message',
# 'variant_b_message',
#         ]

#         widgets = {

#             'subject': forms.TextInput(
#                 attrs={
#                     'class': 'form-control'
#                 }
#             ),

#             'message': forms.Textarea(
#                 attrs={
#                     'class': 'form-control',
#                     'rows': 6
#                 }
#             ),

#             'template': forms.Select(
#                 attrs={
#                     'class': 'form-select'
#                 }
#             )
#         }
# class HTMLImportForm(forms.Form):

#     name = forms.CharField(

#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control'
#             }
#         )
#     )

#     html_file = forms.FileField(

#         widget=forms.FileInput(
#             attrs={
#                 'class': 'form-control'
#             }
#         )
#     )


from django import forms
from .models import Campaign, EmailTemplate


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
            'scheduled_time',  # <--- Added the missing comma here!
            'is_ab_test',
            'variant_a_subject',
            'variant_b_subject',
            'variant_a_message',
            'variant_b_message',
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


class HTMLImportForm(forms.Form):

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    html_file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

class SpamCheckForm(forms.Form):

    content = forms.CharField(

        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 8
            }
        )
    )