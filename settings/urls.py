from django.urls import path
from .api_views import (
    BackupSettingsAPIView,
    BackupListAPIView,
    BackupCreateAPIView,
    BackupDownloadAPIView,
    BackupRestoreAPIView,
    BackupUploadRestoreAPIView,
)

app_name = 'settings'

urlpatterns = [
    # Backup API
    path('api/backup/settings/', BackupSettingsAPIView.as_view(), name='backup_settings_api'),
    path('api/backup/list/', BackupListAPIView.as_view(), name='backup_list_api'),
    path('api/backup/create/', BackupCreateAPIView.as_view(), name='backup_create_api'),
    path('api/backup/<int:pk>/download/', BackupDownloadAPIView.as_view(), name='backup_download_api'),
    path('api/backup/<int:pk>/restore/', BackupRestoreAPIView.as_view(), name='backup_restore_api'),
    path('api/backup/upload-restore/', BackupUploadRestoreAPIView.as_view(), name='backup_upload_restore_api'),
]