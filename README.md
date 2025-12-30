# Medical Equipment Inventory Tracker
A Django-based web app for tracking medical equipment utilization across hospital floors.

## Screenshots

### Active Dashboard
![Active Dashboard](screenshots/active%20dashboard.png)

### Historical Data Dashboard
![Historical Dashboard](screenshots/Historical%20dashboard.png)

### Historical Data Table with Filters
![Historical Table](screenshots/Historical%20Table.png)

### Add Equipment Form
![Add Equipment Form](screenshots/add%20equipment%20form.png)

## Features
- **Dashboard** View equipment with daily cost breakdown by floor
- **Historical Data Tab** Analyzes past equipment usage with filtering
- Date range filters
- Floor/equipment type filters
- Ownership filters (rented/owned)
- Sortable by date, equipment name, and total cost
- Interactive chart
- Floor Segment tracking for patients that move between floors
- CSV export option
- Responsive design

## Stack
-  **Backend**: Django 5.2.9
- **Frontend**: Bootstrap 5, chart.js
- **SQLite**: (development)

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd med-portfolio-prod
2. Create and Activate a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
3. install dependencies
    pip install -r requirements.txt
4. Create .env file in project root:
    SECRET_KEY=your-secret-key-here
    DEBUG=True
5. Run migrations:
    python manage.py makemigrations
    python manage.py migrate
6. Create superuser (optional):
    python manage.py createsuperuser
7. Run development sever:
    python manage.py runserver
8. http://127.0.0.1:8000/inventory/dashboard/

## Structure
med-portfolio-prod/
├── config/              # Project settings
├── inventory/           # Main app
│   ├── models.py       # Database models
│   ├── views.py        # View logic
│   ├── forms.py        # Form definitions
│   ├── templates/      # HTML templates
│   └── admin.py        # Admin configuration
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── .env

## Future Considerations
- User authentication/permissions
- Advanced analytics and reporting

## License
This project is for educational purposes.



