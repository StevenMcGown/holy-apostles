from datetime import datetime, timedelta
from reportlab.lib.units import inch
import calendar as cal  # Avoid naming conflicts by aliasing the module
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Google Calendar API Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Register fonts
pdfmetrics.registerFont(TTFont('ComicNeue', 'fonts/Comic_Neue/ComicNeue-Regular.ttf'))
pdfmetrics.registerFont(TTFont('kells_sd', 'fonts/Kells-SD/Kells_SD.ttf'))

# Define custom styles
styles = getSampleStyleSheet()

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['BodyText'],
    fontName='Times-Roman',  # Body text uses Times New Roman
    fontSize=10,
    leading=10,  # Adjust line spacing
    spaceBefore=0,
    spaceAfter=0
)

class TitleWithImage(Flowable):
    """A custom Flowable to combine an image and text overlay."""
    def __init__(self, image_path, church_name, month_year, page_width):
        super().__init__()
        self.image_path = image_path
        self.church_name = church_name
        self.month_year = month_year
        self.page_width = page_width
        self.width = 8.5 * inch  # Adjust to fit the page
        self.height = 2 * inch  # Banner height

    def draw(self):
        """Draw the centered image and overlay text."""
        # Center the image horizontally
        # image_x = (self.page_width - self.width) / 2
        image_x = -79
        self.canv.drawImage(self.image_path, image_x, -10, width=self.width, height=self.height)

        # Overlay text
        self.canv.setFont("kells_sd", 24)
        self.canv.setFillColor(colors.black)  # Set text color to black
        self.canv.drawCentredString(230, self.height - 110, self.church_name)
        print(self.page_width)
        self.canv.setFont("kells_sd", 22)
        self.canv.drawCentredString(230, self.height - 135, self.month_year)

def list_calendars():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    calendars_result = service.calendarList().list().execute()
    return calendars_result.get('items', [])

def get_calendar_id_by_index(calendars, index):
    try:
        return calendars[index]['id'], calendars[index]['summary']
    except IndexError:
        raise ValueError(f"Invalid selection. Please choose a valid number from 1 to {len(calendars)}.")

def get_next_month_events(calendar_id='primary'):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    today = datetime.utcnow()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    start_of_next_month = next_month.isoformat() + 'Z'
    end_of_next_month = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)
    end_of_next_month = end_of_next_month.isoformat() + 'Z'

    print(f"Fetching events for next month from calendar '{calendar_id}' ({start_of_next_month} to {end_of_next_month})...")
    events_result = service.events().list(
        calendarId=calendar_id, timeMin=start_of_next_month, timeMax=end_of_next_month, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Sort events by start time
    sorted_events = sorted(events, key=lambda x: x['start'].get('dateTime', x['start'].get('date')))
    return sorted_events

def format_time_to_12hr_simple(time_str):
    """Convert time from 'HH:MM' (24-hour format) to 'H AM/PM'."""
    if 'T' in time_str:  # Check if a time exists in the format
        time_obj = datetime.fromisoformat(time_str).time()
        if time_obj.minute == 0:
            return time_obj.strftime("%I %p").lstrip('0')  # Omit minutes if they are 0
        return time_obj.strftime("%I:%M %p").lstrip('0')  # Include minutes otherwise
    return ''  # Return empty string if no time

def create_calendar_pdf(events):
    today = datetime.utcnow()
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    year, month = next_month.year, next_month.month
    days_in_month = cal.monthrange(year, month)[1]
    first_weekday = cal.monthrange(year, month)[0]

    events_by_day = {day: [] for day in range(1, days_in_month + 1)}
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_date = datetime.fromisoformat(start[:10])
        if event_date.month == month:
            event_time = format_time_to_12hr_simple(start)
            event_summary = f"{event_time} {event['summary']}" if event_time else event['summary']
            events_by_day[event_date.day].append(event_summary)

    pdf_path = "Next_Month_Calendar.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    page_width, _ = letter

    # Add custom title with image
    title_with_image = TitleWithImage(
        image_path="frame.jpg",  # Replace with your image path
        church_name="Holy Apostles Orthodox Church",
        month_year=f"{cal.month_name[month]} {year}",
        page_width=page_width
    )

    data = [["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
    current_day = 1
    week = [""] * 7
    for day_idx in range(first_weekday):
        week[day_idx] = ""

    while current_day <= days_in_month:
        for day_idx in range(first_weekday, 7):
            if current_day > days_in_month:
                break

            day_content = f"<b>{current_day}</b>"
            for event in events_by_day[current_day]:
                day_content += f"<br/>{event}"
            day_paragraph = Paragraph(day_content, body_style)
            week[day_idx] = day_paragraph
            current_day += 1
        data.append(week)
        week = [""] * 7
        first_weekday = 0

    if any(day != "" for day in week):
        data.append(week)

    table = Table(data, colWidths=[1.2 * inch] * 7, rowHeights=[0.25 * inch] + [1 * inch] * (len(data) - 1))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))

    elements = [
        title_with_image,
        Spacer(1, 12),
        table,
    ]

    doc.build(elements)
    print(f"PDF saved as '{pdf_path}'")

if __name__ == "__main__":
    calendars = list_calendars()
    print("\nSelect a calendar by entering its number:")
    for i, calendar in enumerate(calendars):
        print(f"{i + 1}. {calendar['summary']}")

    try:
        choice = int(input("\nEnter the number of the calendar: ")) - 1
        calendar_id, calendar_name = get_calendar_id_by_index(calendars

, choice)
        events = get_next_month_events(calendar_id)
        create_calendar_pdf(events)
    except ValueError as e:
        print(e)