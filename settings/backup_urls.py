# -*- coding: utf-8 -*-
"""
Backup API URLs for inclusion in accounting/urls.py
"""
from django.urls import path
from .api_views import (
    BackupSettingsAPIView,
    BackupListAPIView,
    BackupCreateAPIView,
    BackupDownloadAPIView,
    BackupRestoreAPIView,
    BackupUploadRestoreAPIView,
)

urlpatterns = [
    path('settings/', BackupSettingsAPIView.as_view(), name='backup_settings_api'),
    path('list/', BackupListAPIView.as_view(), name='backup_list_api'),
    path('create/', BackupCreateAPIView.as_view(), name='backup_create_api'),
    path('<int:pk>/download/', BackupDownloadAPIView.as_view(), name='backup_download_api'),
    path('<int:pk>/restore/', BackupRestoreAPIView.as_view(), name='backup_restore_api'),
    path('upload-restore/', BackupUploadRestoreAPIView.as_view(), name='backup_upload_restore_api'),
]
