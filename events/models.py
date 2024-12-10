import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import timedelta, now


class CustomUser(AbstractUser):
    """"""

    class Role(models.TextChoices):
        ORGANIZER = "organizer", _("Organizer")
        CHECKIN_STAFF = "checkin-staff", _("Check-in Staff")

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ORGANIZER)
    organizer = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="staff",
        verbose_name=_("Organizer"),
    )


class Event(models.Model):
    """"""

    event_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    organizer = models.ForeignKey(
        CustomUser,
        verbose_name=_("Organizer"),
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    staff = models.ManyToManyField(CustomUser, related_name="staffed_events", blank=True)
    name = models.CharField(_("Event name"), max_length=250)
    description = models.TextField(_("Event Description"))
    date = models.DateField(_("Date"), auto_now_add=False)
    image_url = models.ImageField(_("Event Image"), upload_to="event_images/")
    start_time = models.TimeField(
        _("Starting Time"), auto_now=False, auto_now_add=False
    )
    available_tickets = models.PositiveIntegerField(_("Available Tickets"))
    location = models.CharField(_("Avenue"), max_length=250)
    link = models.URLField(max_length=500)
    checked_in_count = models.PositiveIntegerField(_("Checked-In Count"), default=0)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    @property
    def is_sold_out(self):
        """"""

        return self.available_tickets <= 0

    @property
    def is_over(self):
        """"""
        return self.date < now().date()


class Booking(models.Model):
    """"""

    name = models.CharField(_("Name"), max_length=250)
    email = models.EmailField(_("Email"), max_length=250)
    event = models.ForeignKey(Event, verbose_name=_("Event"), on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email", "event"], name="unique_booking")
        ]

    def __str__(self):
        return f"{self.name} just booked a ticket to {self.event.name}"


class Ticket(models.Model):
    """"""

    booking_id = models.UUIDField()
    event = models.ForeignKey(
        Event, verbose_name=_("Event"), related_name="tickets", on_delete=models.CASCADE
    )
    is_checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"booking_id: {self.booking_id} / Event: {self.event.name}"


class ConfirmationToken(models.Model):
    """"""

    token = models.UUIDField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def is_expired(self):
        expiration_time = self.created_at + timedelta(days=1)
        return now() > expiration_time
