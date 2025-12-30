from django.db.models import Sum
from .models import UtilizationRecord, Floor, EquipmentType
from .forms import UtilizationForm
from django.shortcuts import redirect, render, get_object_or_404
import json
import csv
from django.http import HttpResponse
from datetime import date

def dashboard(request):
    # ACTIVE RECORDS ONLY
    records = UtilizationRecord.objects.filter(end_date__isnull=True)

    # filter by floor if specified
    floor_filter = request.GET.get('floor')
    if floor_filter:
        records = records.filter(floor__name=floor_filter)

    # filter by equipment type if specified
    equipment_filter = request.GET.get('equipment')
    if equipment_filter:
        records = records.filter(equipment_type__name=equipment_filter)

    # calculate total daily cost with filtered list
    total_daily_cost = records.aggregate(Sum('daily_cost'))['daily_cost__sum'] or 0

    # calculate total daily cost for rentals
    rental_records = records.filter(ownership_type='RENTAL')
    rental_daily_cost = rental_records.aggregate(Sum('daily_cost'))['daily_cost__sum'] or 0

    # calculate total daily cost for owned equipment
    owned_records = records.filter(ownership_type='OWNED')
    owned_daily_cost = owned_records.aggregate(Sum('daily_cost'))['daily_cost__sum'] or 0

    total_items = records.count()
    owned_items = records.filter(ownership_type='OWNED').count()
    if total_items > 0:
        efficiency_score = (owned_items / total_items) * 100
    else:
        efficiency_score = 0

    floor_data = records.values('floor__name').annotate(total=Sum('daily_cost')).order_by('floor__name')

    chart_labels = []
    chart_data = []

    # populate lists for chart
    for item in floor_data:
        chart_labels.append(item['floor__name']) 
        chart_data.append(float(item['total'] or 0))

    # get all floors and equipment types for filter dropdowns
    all_floors = Floor.objects.all()
    all_equipment = EquipmentType.objects.all()

    # dynamic chart title based on filters
    chart_title = 'Cost Breakdown by Floor'
    if floor_filter and equipment_filter:
        chart_title = f'Cost Breakdown by Floor - {equipment_filter} on {floor_filter}'
    elif floor_filter:
        chart_title = f'Cost Breakdown by Floor - {floor_filter} Only'
    elif equipment_filter:
        chart_title = f'Cost Breakdown by Floor - {equipment_filter} Only'


    context = {
        'all_records': records,
        'all_floors': all_floors,
        'all_equipment': all_equipment,
        'current_filter': floor_filter,
        'current_equipment_filter': equipment_filter,
        'total_daily_cost': total_daily_cost,
        'rental_daily_cost': rental_daily_cost,
        'owned_daily_cost': owned_daily_cost,
        'efficiency_score': efficiency_score,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'chart_title': chart_title,
    }

    return render(request, 'inventory/dashboard.html', context)

# add record
def add_utilization(request):
    if request.method == "POST":
        form = UtilizationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UtilizationForm()

    context = {'form': form}
    return render(request, 'inventory/form.html', context)

# update record
def update_utilization(request, id):
    from .forms import FloorSegmentFormSet
    # get record or show 404 error
    record = get_object_or_404(UtilizationRecord, id=id)

    if request.method == 'POST':
        form = UtilizationForm(request.POST, instance=record)
        formset = FloorSegmentFormSet(request.POST, instance=record)

        if form.is_valid() and formset.is_valid():
            parent_start = form.cleaned_data['start_date']
            parent_end = form.cleaned_data['end_date']

            # collect all valid segments for overlap checking
            valid_segments = []

            for segment_form in formset:
                if segment_form.cleaned_data and not segment_form.cleaned_data.get('DELETE'):
                    seg_start = segment_form.cleaned_data.get('start_date')
                    seg_end = segment_form.cleaned_data.get('end_date')

                    # Check if segment start is before parent start
                    if seg_start and seg_start < parent_start:
                        segment_form.add_error('start_date',
                                               f"Start date cannot be before equipment utilization start date ({parent_start}).")

                    # check if segment end is after parent end (only if parent has an end date)
                    if parent_end and seg_end and seg_end > parent_end:
                        segment_form.add_error('end_date',
                                                 f"End date cannot be after equipment utilization end date ({parent_end}).")

                    # check if segment start is after segment end
                    if seg_start and seg_end and seg_start > seg_end:
                        segment_form.add_error('end_date',
                                                 "Segment end date cannot be before start date.")

                    # store valid segment for overlap checking
                    if seg_start:
                        valid_segments.append({
                            'form': segment_form,
                            'start': seg_start,
                            'end': seg_end
                        })

            # check for overlapping segments
            for i, seg1 in enumerate(valid_segments):
                for j, seg2 in enumerate(valid_segments):
                    if i >= j:  # Skip same segment and already checked pairs
                        continue

                    seg1_start = seg1['start']
                    seg1_end = seg1['end'] if seg1['end'] else date.today()  # use today if no end date
                    seg2_start = seg2['start']
                    seg2_end = seg2['end'] if seg2['end'] else date.today()

                    if seg1_start < seg2_end and seg2_start < seg1_end:
                        seg1['form'].add_error('start_date',
                            f"This floor segment overlaps with another segment. Equipment cannot be on multiple floors at the same time.")
                        seg2['form'].add_error('start_date',
                            f"This floor segment overlaps with another segment. Equipment cannot be on multiple floors at the same time.")
            if formset.is_valid():
                form.save()
                formset.save()
                return redirect('dashboard')
    else:
        form = UtilizationForm(instance=record)
        formset = FloorSegmentFormSet(instance=record)
    
    context = {
        'form': form,
        'formset': formset,
        'record': record
    }
    return render(request, 'inventory/form.html', context)

# delete record
def delete_utilization(request, id):
    record = get_object_or_404(UtilizationRecord, id=id)
    if request.method == 'POST':
        record.delete()
        return redirect('dashboard')
    
    context = {
        'record': record
    }
    return render(request, 'inventory/delete_confirm.html', context)

# historical data
def history(request):
    # INACTIVE RECORDS ONLY
    records = UtilizationRecord.objects.filter(end_date__isnull=False)

    # filter by floor if specified
    floor_filter = request.GET.get('floor')
    if floor_filter:
        records = records.filter(floor__name=floor_filter)

    # filter by equipment type if specified
    equipment_filter = request.GET.get('equipment')
    if equipment_filter:
        records = records.filter(equipment_type__name=equipment_filter)

    # filter by date range if specified
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if from_date and to_date:
        records = records.filter(end_date__range=[from_date, to_date])
    elif from_date:
        records = records.filter(end_date__gte=from_date)
    elif to_date:
        records = records.filter(end_date__lte=to_date)

    #ownership filter
    ownership_filter = request.GET.get('ownership')
    if ownership_filter:
        records = records.filter(ownership_type=ownership_filter)
    
    # calculate total history cost and count before sorting
    total_history_cost = sum(record.total_cost for record in records)
    total_records = records.count()

    #preparing chart data
    floor_chart_data = {}
    for record in records:
        floor_name = record.floor.name
        if floor_name not in floor_chart_data:
            floor_chart_data[floor_name] = 0
        floor_chart_data[floor_name] += float(record.total_cost)

    #convert to list
    chart_labels = list(floor_chart_data.keys())
    chart_data = list(floor_chart_data.values())



    # sort
    sort_by = request.GET.get('sort', '-end_date') # newest first (default)

    # handle sorting by total_cost (property, not database field)
    if sort_by in ['total_cost', '-total_cost']:
        records = list(records)  # convert to list to sort in Python
        records = sorted(records, key=lambda x: x.total_cost, reverse=(sort_by == '-total_cost'))
    else:
        records = records.order_by(sort_by)

    # get all floors/equipment types for filter dropdowns
    all_floors = Floor.objects.all()
    all_equipment = EquipmentType.objects.all()

    context = {
        'all_records': records,
        'all_floors': all_floors,
        'all_equipment': all_equipment,
        'current_filter': floor_filter,
        'current_equipment_filter': equipment_filter,
        'from_date': from_date,
        'to_date': to_date,
        'ownership_filter': ownership_filter,
        'sort_by': sort_by,
        'total_history_cost': total_history_cost,
        'total_records': total_records,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request,'inventory/history.html', context)

# export to csv
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Equipment Name', 'Floor', 'Ownership', 'Status', 'Daily Cost', 'Total Days', 'Total Cost'])
    
    # ACTIVE RECORDS ONLY
    records = UtilizationRecord.objects.filter(end_date__isnull=True)

    # filter by floor if specified
    floor_filter = request.GET.get('floor')
    if floor_filter:
        records = records.filter(floor__name=floor_filter)

    # filter by equipment type if specified
    equipment_filter = request.GET.get('equipment')
    if equipment_filter:
        records = records.filter(equipment_type__name=equipment_filter)

    for record in records:
        status = 'Active' if not record.end_date else 'Inactive'
        writer.writerow([
            record.equipment_type.name,
            record.floor.name,
            record.ownership_type,
            status,
            f"{record.daily_cost:.2f}",
            record.total_days,
            f"{record.total_cost:.2f}"
        ])

    return response