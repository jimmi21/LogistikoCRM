# accounting/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import MonthlyObligation

class MonthlyObligationAdminForm(forms.ModelForm):
    """Custom form για το Admin με έλεγχο duplicates"""
    
    class Meta:
        model = MonthlyObligation
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Μόνο για νέες εγγραφές
        if not self.instance.pk:
            client = cleaned_data.get('client')
            obligation_type = cleaned_data.get('obligation_type')
            year = cleaned_data.get('year')
            month = cleaned_data.get('month')
            
            if all([client, obligation_type, year, month]):
                exists = MonthlyObligation.objects.filter(
                    client=client,
                    obligation_type=obligation_type,
                    year=year,
                    month=month
                ).exists()
                
                if exists:
                    raise ValidationError({
                        '__all__': [
                            f'⚠️ Υπάρχει ήδη υποχρέωση "{obligation_type}" '
                            f'για τον πελάτη "{client}" '
                            f'για {month}/{year}!'
                        ]
                    })
        
        return cleaned_data