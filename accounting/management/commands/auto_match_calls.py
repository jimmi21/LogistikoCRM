# -*- coding: utf-8 -*-
"""
accounting/management/commands/auto_match_calls.py
Author: ddiplas
Version: 1.0
Description: Management command to auto-match VoIP calls to clients by phone number
"""
from django.core.management.base import BaseCommand, CommandError
from accounting.phone_utils import batch_auto_match_calls, normalize_phone
from accounting.models import VoIPCall, ClientProfile


class Command(BaseCommand):
    help = 'Auto-match VoIP calls to clients by phone number'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be matched without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each match',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Test phone normalization for a specific number',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        test_phone = options.get('phone')

        # Test phone normalization
        if test_phone:
            self.stdout.write(f"\nPhone normalization test:")
            self.stdout.write(f"  Input:      {test_phone}")
            self.stdout.write(f"  Normalized: {normalize_phone(test_phone)}")

            # Try to find matching client
            from accounting.phone_utils import find_client_by_phone
            client = find_client_by_phone(test_phone)
            if client:
                self.stdout.write(self.style.SUCCESS(
                    f"  Match:      {client.eponimia} (ID: {client.id})"
                ))
            else:
                self.stdout.write(self.style.WARNING("  Match:      No client found"))
            return

        # Get statistics before matching
        total_calls = VoIPCall.objects.count()
        unmatched_before = VoIPCall.objects.filter(client__isnull=True).count()
        matched_before = total_calls - unmatched_before

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Auto-matching VoIP Calls to Clients")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(f"\nBefore matching:")
        self.stdout.write(f"  Total calls:     {total_calls}")
        self.stdout.write(f"  Already matched: {matched_before}")
        self.stdout.write(f"  Unmatched:       {unmatched_before}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN MODE - No changes will be saved]\n"))

        if unmatched_before == 0:
            self.stdout.write(self.style.SUCCESS("\nAll calls are already matched!"))
            return

        # Perform matching
        self.stdout.write(f"\nProcessing {unmatched_before} unmatched calls...")
        stats = batch_auto_match_calls(dry_run=dry_run)

        # Show results
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("Results:")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"  Matched:     {stats['matched']}"))
        self.stdout.write(self.style.WARNING(f"  Still unmatched: {stats['unmatched']}"))

        if verbose and stats['details']:
            self.stdout.write(f"\nMatch details:")
            for detail in stats['details']:
                self.stdout.write(
                    f"  - Call #{detail['call_id']}: {detail['phone']} -> "
                    f"{detail['matched_client']} (ID: {detail['client_id']})"
                )

        if stats['matched'] > 0:
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"\n{stats['matched']} calls would be matched. "
                    f"Run without --dry-run to apply changes."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"\nSuccessfully matched {stats['matched']} calls to clients!"
                ))

        # Show remaining unmatched phones
        if stats['unmatched'] > 0 and verbose:
            unmatched_calls = VoIPCall.objects.filter(client__isnull=True).values_list(
                'phone_number', flat=True
            ).distinct()[:20]

            self.stdout.write(f"\nSample unmatched phone numbers (up to 20):")
            for phone in unmatched_calls:
                self.stdout.write(f"  - {phone}")

        self.stdout.write("")
