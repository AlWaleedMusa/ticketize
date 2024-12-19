from http import HTTPStatus
from datetime import datetime
import json

from django.test import TestCase, Client
from django.core import mail
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from events.models import Event, CustomUser, Booking, ConfirmationToken, Ticket


class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="user@gmail.com", password="testpassword"
        )

    def test_send_mail(self):
        # Send an email and check the outbox
        self.user.email_user("Test Subject", "Test Message")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")
        self.assertEqual(mail.outbox[0].body, "Test Message")
        self.assertEqual(mail.outbox[0].to, ["user@gmail.com"])


class EventTestCase(TestCase):
    def setUp(self):
        # Set up user, event, and client
        self.user = CustomUser.objects.create_user(
            username="testuser", email="user@gmail.com", password="testpassword"
        )
        self.event = Event.objects.create(
            name="Test Event",
            description="Test Description",
            date=datetime.now().date(),
            start_time=datetime.now().time(),
            location="Test Location",
            available_tickets=50,
            organizer=self.user,
        )
        self.client = Client()
        self.client.login(
            username="testuser", password="testpassword", role=CustomUser.Role.ORGANIZER
        )

    def test_add_event(self):
        # Test adding a new event
        response = self.client.post(
            reverse("add_event"),
            {
                "name": "Test Event 1",
                "description": "Test Description",
                "date": "2020-01-02",
                "start_time": "10:00:00",
                "location": "Test Location",
                "available_tickets": 50,
            },
        )

        event = Event.objects.get(name="Test Event 1")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(event.name, "Test Event 1")
        self.assertEqual(event.organizer, self.user)
        self.assertIsNotNone(event.link)
        self.assertIsNotNone(event.image_url)

    def test_delete_event(self):
        # Test event deletion
        self.assertEqual(Event.objects.count(), 1)

        response = self.client.post(
            reverse("event_delete", args=[self.event.event_id]), follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Event.objects.count(), 0)

    def test_event_details(self):
        # Test event details page
        response = self.client.get(reverse("event_detail", args=[self.event.event_id]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context["event"], self.event)
        self.assertEqual(self.event.organizer, self.user)

    def test_book_event(self):
        # Test event booking and confirmation
        response = self.client.post(
            reverse("book_event", args=[self.event.event_id]),
            {"name": "Test User", "email": "user@gmail.com"},
        )
        booking = Booking.objects.get(name="Test User")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.event, self.event)
        self.assertEqual(booking.email, "user@gmail.com")
        self.assertEqual(booking.name, "Test User")
        self.assertEqual(ConfirmationToken.objects.count(), 1)

        token = ConfirmationToken.objects.first()
        self.assertFalse(token.is_expired())

        # Confirm email and check token confirmation
        response = self.client.get(reverse("confirm_email"), {"token": token.token})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        token.refresh_from_db()
        self.assertTrue(token.is_confirmed)

        # Verify ticket creation and check-in status
        ticket = Ticket.objects.first()
        self.assertEqual(ticket.event, self.event)
        self.assertEqual(ticket.is_checked_in, False)
        self.assertEqual(self.event.checked_in_count, 0)

        # Check-in ticket
        response = self.client.get(reverse("scan_qr", args=[self.event.event_id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Validate ticket check-in
        response = self.client.post(
            reverse("process_qr_code"),
            data=json.dumps(
                {
                    "qr_code": str(ticket.booking_id),
                    "event_id": str(self.event.event_id),
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Ticket.objects.first().is_checked_in, True)
        self.event.refresh_from_db()
        self.assertEqual(self.event.checked_in_count, 1)