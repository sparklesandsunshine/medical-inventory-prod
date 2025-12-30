from django.db import models
from datetime import date

class Floor(models.Model):
    name = models.CharField(max_length=50) # Name of the floor

    def __str__(self):
        return self.name
    
class EquipmentType(models.Model):
    CATEGORY_CHOICES = [
        # category choices for classification
        ("WOUND_CARE", "Wound Care"),
        ("BARIATRIC", "Bariatric"),
    ]
    name = models.CharField(max_length=100) # Name of the equipment type
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES) # Category of equipment (ie: wound care/bariatric)
    owned_quantity = models.PositiveIntegerField(default=0) # Quantity of owned equipment

    def __str__(self):
        return self.name

class UtilizationRecord(models.Model):
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE) # Link to catalog
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE) # Floor where equipment is utilized 
    start_date = models.DateField() # Start date of utilization
    end_date = models.DateField(null=True, blank=True) # End date of utilization (optional)
    daily_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Cost per day of utilization
    OWNERSHIP_CHOICES = [
        ("OWNED", "Owned"),
        ("RENTAL", "Rental"),
    ]

    ownership_type = models.CharField(max_length=10, choices=OWNERSHIP_CHOICES) # Owned or rental

    @property # calculates total days of utilization (can't store in db since it changes daily)
    def total_days(self):
        if not self.end_date:
            end = date.today()
        else:
            end = self.end_date
        delta = end - self.start_date
        return delta.days + 1 # inclusive of both start and end date
    
    @property # calculates days * daily rate to get total cost (ie: $45/day * 10 days = $450)
    def total_cost(self):
        return self.daily_cost * self.total_days
    

    def __str__(self):
        return f"{self.equipment_type.name} utilized on {self.floor.name} from {self.start_date} to {self.end_date if self.end_date else 'Present'}"
    
class FloorSegment(models.Model):
    # links to parent utilization record (foreign key)
    utilization_record = models.ForeignKey(
        UtilizationRecord,
        on_delete=models.CASCADE,
        related_name='segments'
    )
    
    # floor and date range for segment
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        end = self.end_date if self.end_date else 'Present'
        return f"Moved to {self.floor.name}: {self.start_date} to {end}"