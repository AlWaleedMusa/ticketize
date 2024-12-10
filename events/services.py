import qrcode
import uuid
import os

from django.core.mail import send_mail
from django.db.models import F
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.template.loader import render_to_string

from PIL import Image
from email.mime.image import MIMEImage
from io import BytesIO

from .models import Ticket, ConfirmationToken


def resize_image(image):
    """
    Resize the uploaded image to a smaller size to avoid large files being uploaded.
    """
    img = Image.open(image)
    img.thumbnail((800, 800))  # Resize image to fit within a 800x800 box

    # Save resized image to an in-memory file
    img_io = BytesIO()
    img.save(img_io, format="JPEG", quality=85)
    img_io.seek(0)

    # Create a new InMemoryUploadedFile instance
    image_file = InMemoryUploadedFile(
        img_io, None, image.name, "image/jpeg", img_io.getbuffer().nbytes, None
    )

    return image_file


def generate_send_qr(booking_id, email, event):
    # Generate the QR code
    generated_qr = qrcode.make(booking_id)

    buffer = BytesIO()
    generated_qr.save(buffer, format="PNG")
    buffer.seek(0)

    # Path to your logo file (e.g., stored in your static files directory)
    logo_path = os.path.join(settings.STATIC_ROOT, "images", "logo.png")
    with open(logo_path, "rb") as logo_file:
        logo_data = logo_file.read()

    # Email content
    subject = f"Your QR Ticket for the Event '{event.name}'"
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    html_content = render_to_string("events/emails/qr_email.html", {"event": event})
    plain_text_content = f"Your QR Ticket\n\nThank you for registering for the event {event.name}! Please find your QR code attached. Present this code at the event for check-in.\n\nIf you have any questions, contact us at example.com"

    # Create the email
    email_obj = EmailMultiAlternatives(
        subject, plain_text_content, from_email, to_email
    )
    email_obj.attach_alternative(html_content, "text/html")

    # Attach the QR code as an inline image
    qr_image = MIMEImage(buffer.read(), _subtype="png")
    qr_image.add_header("Content-ID", "<qr_code>")
    qr_image.add_header("Content-Disposition", "inline", filename="qr_code.png")
    email_obj.attach(qr_image)

    # Attach the brand logo as an inline image
    logo_image = MIMEImage(logo_data, _subtype="png")
    logo_image.add_header("Content-ID", "<logo>")
    logo_image.add_header("Content-Disposition", "inline", filename="logo.png")
    email_obj.attach(logo_image)

    # Send the email
    email_obj.send()

    buffer.close()


def process_booking(event):
    """ """

    with transaction.atomic():
        if event.is_sold_out:
            raise ValueError("No tickets available for this event.")

        # Save the booking and decrement tickets
        # booking = form.save(commit=False)
        # booking.event = event
        event.available_tickets = F("available_tickets") - 1
        event.save()
        # booking.save()

    # Generate confirmation and QR code
    booking_id = uuid.uuid4()
    return booking_id


def save_ticket(booking_id, event):
    """"""

    ticket = Ticket.objects.create(booking_id=booking_id, event=event)
    ticket.save()


def validate_ticket(qr_code_data, event_id):
    """"""

    try:
        uuid.UUID(qr_code_data)

        with transaction.atomic():
            ticket = Ticket.objects.select_related("event").get(
                booking_id=qr_code_data, event__event_id=event_id
            )
            if ticket and ticket.is_checked_in:
                raise ValueError("This ticket has already been used for check-in.")

            ticket.is_checked_in = True  # Mark as checked in
            ticket.save(update_fields=["is_checked_in"])

            event = ticket.event
            event.checked_in_count = F("checked_in_count") + 1
            event.save(update_fields=["checked_in_count"])

        return ticket
    except ValueError:
        raise Http404("Invalid confirmation ID format.")
    except Ticket.DoesNotExist:
        raise Http404("Ticket with the provided confirmation ID does not exist.")
    except Exception:
        raise Http404("ticket might be used already")


def send_confirmation_email(request, email, generated_token):
    """"""

    confirmation_link = request.build_absolute_uri(f"/confirm/?token={generated_token}")

    send_mail(
        "Confirm booking",
        f"Please click on the link to confirm your booking: {confirmation_link}",
        settings.EMAIL_HOST_USER,
        [email],
    )


def email_staff_password(email, random_password):
    """"""

    send_mail(
        "Staff Password",
        f"Your password is: {random_password}",
        settings.EMAIL_HOST_USER,
        [email],
    )
