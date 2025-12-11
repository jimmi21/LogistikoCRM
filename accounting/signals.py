# -*- coding: utf-8 -*-
"""
Signals for accounting app.

Handles ticket-call relationship cleanup.
"""
import logging
from django.db.models.signals import pre_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender='accounting.Ticket')
def cleanup_orphan_call_on_ticket_delete(sender, instance, **kwargs):
    """
    Όταν διαγράφεται Ticket, ενημέρωσε το VoIPCall ότι δεν έχει πλέον ticket.

    Χρησιμοποιούμε pre_delete γιατί στο post_delete το call μπορεί να έχει ήδη
    διαγραφεί (CASCADE).
    """
    if instance.call_id:
        try:
            # Ενημέρωση μόνο αν δεν διαγράφεται και η κλήση
            from accounting.models import VoIPCall
            call = VoIPCall.objects.filter(pk=instance.call_id).first()
            if call:
                # Σημειώνουμε για μετά (αποφυγή infinite loops)
                call._ticket_being_deleted = True
                call.ticket_created = False
                call.ticket_id = None
                call.save(update_fields=['ticket_created', 'ticket_id'])
                logger.info(f"Call {call.call_id}: ticket_created reset to False")
        except Exception as e:
            logger.warning(f"Could not update call on ticket delete: {e}")
