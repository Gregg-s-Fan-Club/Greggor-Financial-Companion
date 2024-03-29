from datetime import datetime
from django.utils import timezone
import pytz
from django.conf import settings
from financial_companion.helpers import send_monthly_newsletter_email
from django_q.models import Schedule


def create_monthly_newsletter_scheduler() -> None:
    """Creates a scheduler object for the monthly newsletter"""
    schedulers: Schedule = Schedule.objects.filter(name="Monthly Newsletter")
    if (len(schedulers) == 0):
        date_time_str: str = f'{timezone.now().month + 1}-01-{timezone.now().year}'
        date_object: datetime = datetime.strptime(
            date_time_str, '%m-%d-%Y').replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

        scheduler: Schedule = Schedule.objects.create(
            name="Monthly Newsletter",
            func='financial_companion.helpers.tasks.send_monthly_newsletter_email',
            minutes=1,
            repeats=-1,
            schedule_type=Schedule.MONTHLY,
            next_run=date_object)
