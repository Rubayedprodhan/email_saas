from django.urls import path

from .views import (
    CampaignListView,
    CampaignCreateView,
    EmailTemplateListView,
    EmailTemplateCreateView,
    email_open_tracking,
    click_tracking,
    MediaUploadView,
    MediaListView,
    EmailBlockCreateView,
    TemplateBuilderView,
    EmailPreviewView,
    update_block_order,
    update_block_content,
    template_preview_api,
    duplicate_block,
    export_template_html,
    ImportHTMLTemplateView,
    save_section,
    add_saved_section,
    SavedSectionListView,
    undo_block_change,
    redo_block_change,
    ai_optimize_subject

)

urlpatterns = [

    path('',CampaignListView.as_view(),name='campaign_list'),

    path('create/',CampaignCreateView.as_view(),name='campaign_create'),

    path('templates/',EmailTemplateListView.as_view(),name='template_list'),

    path('templates/create/',EmailTemplateCreateView.as_view(),name='template_create'),

    path('track/<int:track_id>/',email_open_tracking,name='email_tracking'),

    path('click/<int:track_id>/',click_tracking,name='click_tracking'),
    path('media/upload/',MediaUploadView.as_view(),name='media_upload'),

    path('media/',MediaListView.as_view(),name='media_list'),
    path('templates/<int:template_id>/builder/',TemplateBuilderView.as_view(),name='template_builder'),

    path('templates/<int:template_id>/blocks/create/',EmailBlockCreateView.as_view(),name='block_create'),
    path('templates/<int:template_id>/preview/',EmailPreviewView.as_view(),name='email_preview'),
    path('blocks/update-order/',update_block_order,name='update_block_order'),
    path('blocks/<int:block_id>/update/',update_block_content, name='update_block_content'),
    path('templates/<int:template_id>/preview-api/',template_preview_api,name='template_preview_api'),
    path('blocks/<int:block_id>/duplicate/',duplicate_block,name='duplicate_block'),
    path('templates/<int:template_id>/export/',export_template_html,name='export_template_html'),
    path('templates/import/',ImportHTMLTemplateView.as_view(),name='import_template'),
    path('blocks/<int:block_id>/save-section/', save_section,name='save_section'),
    path('templates/<int:template_id>/add-section/<int:section_id>/',add_saved_section,name='add_saved_section'),

    path('saved-sections/',SavedSectionListView.as_view(), name='saved_sections'),

    path('blocks/<int:block_id>/undo/', undo_block_change , name='undo_block_change'),
    path('blocks/<int:block_id>/redo/',redo_block_change, name='redo_block_change'),
    path('ai/optimize-subject/',ai_optimize_subject,name='ai_optimize_subject'),

]