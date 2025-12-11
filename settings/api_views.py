# -*- coding: utf-8 -*-
"""
API views for Backup functionality.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.http import FileResponse

from .models import BackupSettings, BackupHistory
from .backup_utils import create_backup, restore_backup, get_backup_list


class HasBackupPermission:
    """Custom permission mixin for backup operations."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True


class BackupSettingsAPIView(APIView):
    """API για ρυθμίσεις backup."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Επιστρέφει τις ρυθμίσεις backup."""
        settings_obj = BackupSettings.get_settings()
        return Response({
            'backup_path': settings_obj.backup_path,
            'include_media': settings_obj.include_media,
            'max_backups': settings_obj.max_backups,
        })

    def patch(self, request):
        """Ενημερώνει τις ρυθμίσεις backup."""
        if not request.user.has_perm('settings.change_backupsettings'):
            return Response({'error': 'Permission denied'}, status=403)

        settings_obj = BackupSettings.get_settings()

        if 'backup_path' in request.data:
            settings_obj.backup_path = request.data['backup_path']
        if 'include_media' in request.data:
            settings_obj.include_media = request.data['include_media']
        if 'max_backups' in request.data:
            settings_obj.max_backups = request.data['max_backups']

        settings_obj.save()
        return Response({'status': 'updated'})


class BackupListAPIView(APIView):
    """API για λίστα backups."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Επιστρέφει λίστα με τα διαθέσιμα backups."""
        backups = BackupHistory.objects.all().values(
            'id', 'filename', 'file_size', 'includes_db', 'includes_media',
            'created_at', 'notes', 'restored_at'
        )

        backup_list = []
        for backup in backups:
            backup_obj = BackupHistory.objects.get(pk=backup['id'])
            backup['file_size_display'] = backup_obj.file_size_display()
            backup['file_exists'] = backup_obj.file_exists()
            backup['created_at'] = backup['created_at'].isoformat()
            if backup['restored_at']:
                backup['restored_at'] = backup['restored_at'].isoformat()
            backup_list.append(backup)

        return Response(backup_list)


class BackupCreateAPIView(APIView):
    """API για δημιουργία backup."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Δημιουργεί νέο backup."""
        if not request.user.has_perm('settings.can_create_backup'):
            return Response({'error': 'Permission denied'}, status=403)

        notes = request.data.get('notes', '')
        include_media = request.data.get('include_media', True)

        try:
            backup = create_backup(
                user=request.user,
                include_media=include_media,
                notes=notes
            )
            return Response({
                'status': 'success',
                'backup': {
                    'id': backup.id,
                    'filename': backup.filename,
                    'file_size': backup.file_size,
                    'file_size_display': backup.file_size_display(),
                }
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class BackupDownloadAPIView(APIView):
    """API για download backup."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Download backup file."""
        if not request.user.has_perm('settings.can_download_backup'):
            return Response({'error': 'Permission denied'}, status=403)

        try:
            backup = BackupHistory.objects.get(pk=pk)
            if backup.file_exists():
                return FileResponse(
                    open(backup.file_path, 'rb'),
                    as_attachment=True,
                    filename=backup.filename
                )
            return Response({'error': 'File not found'}, status=404)
        except BackupHistory.DoesNotExist:
            return Response({'error': 'Backup not found'}, status=404)


class BackupRestoreAPIView(APIView):
    """API για restore backup."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Restore backup."""
        if not request.user.has_perm('settings.can_restore_backup'):
            return Response({'error': 'Permission denied'}, status=403)

        mode = request.data.get('mode', 'replace')
        if mode not in ['replace', 'merge']:
            return Response({'error': 'Invalid mode'}, status=400)

        try:
            success = restore_backup(pk, user=request.user, mode=mode)
            if success:
                return Response({'status': 'success', 'mode': mode})
            return Response({'error': 'Restore failed'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class BackupUploadRestoreAPIView(APIView):
    """API για upload και restore από εξωτερικό αρχείο."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        """Upload και restore backup."""
        if not request.user.has_perm('settings.can_restore_backup'):
            return Response({'error': 'Permission denied'}, status=403)

        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)

        mode = request.data.get('mode', 'replace')
        uploaded_file = request.FILES['file']

        # Αποθήκευση uploaded αρχείου
        import os
        import tempfile
        from django.utils import timezone

        settings_obj = BackupSettings.get_settings()
        backup_dir = settings_obj.get_backup_dir()
        os.makedirs(backup_dir, exist_ok=True)

        filename = f'uploaded_{timezone.now().strftime("%Y%m%d_%H%M%S")}.zip'
        file_path = os.path.join(backup_dir, filename)

        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Δημιουργία record
        backup = BackupHistory.objects.create(
            filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            includes_db=True,
            includes_media=True,
            created_by=request.user,
            notes='Uploaded backup'
        )

        # Restore
        try:
            success = restore_backup(backup.id, user=request.user, mode=mode)
            if success:
                return Response({'status': 'success', 'backup_id': backup.id})
            return Response({'error': 'Restore failed'}, status=500)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
