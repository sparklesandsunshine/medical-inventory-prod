from django import forms
from .models import FloorSegment, UtilizationRecord

class UtilizationForm(forms.ModelForm):
    class Meta:
        model = UtilizationRecord
        fields = [
            "equipment_type",
            "floor",
            "ownership_type",
            "start_date",
            "end_date",
            "daily_cost"
        ]

        labels = {
            'start_date': 'Utilization Start Date',
            'end_date': 'Utilization End Date',
        }
    
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class FloorSegmentForm(forms.ModelForm):
    class Meta:
        model = FloorSegment
        fields = [
            "floor",
            "start_date",
            "end_date"
        ]

        labels = {
            'start_date': 'Moved to floor on',
            'end_date': 'Moved off floor on (leave blank if here)',
        }

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
# floor movement/transfer
FloorSegmentFormSet = forms.inlineformset_factory(
    UtilizationRecord,
    FloorSegment,
    form=FloorSegmentForm,
    fields=('floor', 'start_date', 'end_date'),
    extra=1,
    can_delete=True,
)