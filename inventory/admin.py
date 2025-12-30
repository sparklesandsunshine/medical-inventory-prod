from django.contrib import admin
from .models import EquipmentType, Floor, UtilizationRecord, FloorSegment

admin.site.register(EquipmentType)
admin.site.register(Floor)

# view floor segments as a table inline within utilization record admin
class FloorSegmentInline(admin.TabularInline):
    model = FloorSegment
    extra = 1

# custom admin for UtilizationRecord
@admin.register(UtilizationRecord)
class UtilizationRecordAdmin(admin.ModelAdmin):
    list_display = ('equipment_type', 'floor', 'ownership_type', 'start_date', 'end_date', 'daily_cost', 'total_cost')
    list_filter = ('floor', 'ownership_type','equipment_type',)
    search_fields = ('equipment_type__name', 'floor__name')
    ordering = ('-id',)
    inlines = [FloorSegmentInline]