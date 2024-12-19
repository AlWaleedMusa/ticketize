import json
import uuid

from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.db.models import Q
from django.db import transaction
from django.db.models import F



from .models import Event, CustomUser, Ticket, ConfirmationToken, Booking
from .forms import EventForm, BookingForm, AddStaffForm
from .permissions import roles_required
from .services import (
    process_booking,
    save_ticket,
    validate_ticket,
    send_confirmation_email,
    resize_image,
    generate_send_qr,
    email_staff_password,
)

def landing(request):
    """"""
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "events/landing.html")


@roles_required(["organizer", "checkin-staff"])
def home(request):
    """"""

    if request.user.role == CustomUser.Role.CHECKIN_STAFF:
        events = (
            Event.objects.prefetch_related("staff")
            .filter(staff=request.user)
            .order_by("date")
        )
        context = {"events": events}
        return render(request, "events/checkin_staff_home.html", context)

    events = (
        Event.objects.prefetch_related("organizer")
        .filter(organizer=request.user)
        .order_by("date")
    )

    context = {"events": events}
    return render(request, "events/home.html", context)

def about(request):
    """"""

    return render(request, "events/about.html")

@roles_required(["organizer"])
def add_event(request):
    """"""

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.organizer = request.user

            if "image_url" in request.FILES:
                obj.image_url = resize_image(request.FILES["image_url"])

            event_link = request.build_absolute_uri(
                reverse("event_detail", args=[obj.event_id])
            )

            obj.link = event_link
            obj.save()

            return redirect("home")
    else:
        form = EventForm()

    context = {"form": form}
    return render(request, "events/forms/add_event_form.html", context)


def event_detail(request, pk):
    """"""

    event = get_object_or_404(Event.objects.prefetch_related("organizer"), event_id=pk)
    return render(request, "events/event_detail.html", {"event": event})


@roles_required(["organizer"])
def delete_event(request, pk):
    """"""

    event = Event.objects.filter(organizer=request.user, event_id=pk).first()

    if event:
        if request.method == "POST":
            event.delete()
            return redirect("home")
        return render(request, "includes/confirm_delete.html", {"event": event})
    else:
        return render(request, "events/forbidden.html")


def book_event(request, event_id):
    """"""

    event = get_object_or_404(Event, event_id=event_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]

            # Check if the user already has a booking for this event
            if Booking.objects.filter(event=event, email=email).exists():
                messages.error(request, "You are already booked for this event.")
                return redirect("event_detail", pk=event_id)

            try:
                # Create a new booking
                Booking.objects.create(name=name, email=email, event=event)

                # Generate token for confirmation
                generated_token = uuid.uuid4()
                ConfirmationToken.objects.create(
                    token=generated_token, event=event, email=email
                )

                # Send confirmation email
                send_confirmation_email(request, email, generated_token)

                return render(request, "events/booking_step_one.html", {"event": event})

            except Exception as e:
                # Handle any unforeseen exceptions
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect("event_detail", pk=event_id)

    else:
        form = BookingForm()

    context = {"form": form}
    return render(request, "events/forms/booking_form.html", context)


@roles_required(["organizer"])
def add_staff(request, event_id):
    """"""

    event = Event.objects.filter(organizer=request.user, event_id=event_id).first()

    if not event:
        return render(request, "events/forbidden.html")

    if request.method == "POST":
        form = AddStaffForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]

            try:
                random_password = uuid.uuid4().hex[:10]
                print(random_password)
                user = CustomUser.objects.create(
                    email=email,
                    username=name,
                    role=CustomUser.Role.CHECKIN_STAFF,
                    organizer=request.user,
                )
                user.set_password(random_password)
                user.save()
                event.staff.add(user)
                email_staff_password(email, random_password)
                messages.success(request, f"{name} added as a Staff")
                return redirect("home")
            except IntegrityError:
                messages.error(request, f"{name} already is a Staff")
                return redirect("home")
    else:
        form = AddStaffForm()

    return render(request, "events/forms/add_staff_form.html", {"form": form})


def confirm_email(request):
    """"""

    token_param = request.GET.get("token")

    try:
        # Ensure the token is valid UUID
        token = get_object_or_404(ConfirmationToken, token=uuid.UUID(token_param))
    except ValueError:
        messages.error(request, "Invalid token format.")
        return redirect("home")

    event = token.event
    email = token.email

    if token.is_expired():
        messages.error(request, "This token is expired")
        return redirect("home")

    if not token.is_confirmed:
        token.is_confirmed = True
        token.save(update_fields=["is_confirmed"])

        try:
            booking_id = process_booking(event)

            # generate a ticket
            save_ticket(booking_id, event)
            generate_send_qr(booking_id, email, event)

            with transaction.atomic():
                event.confirmed_tickets = F("confirmed_tickets") + 1
                event.save(update_fields=["confirmed_tickets"])

            return render(request, "events/booking_step_two.html")
        except Exception as e:
            return HttpResponse(str(e))

    else:
        return render(request, "events/already_confirmed.html")


@roles_required(["organizer", "checkin-staff"])
def qr_code_scanner(request, event_id):
    """"""

    event = Event.objects.filter(
        Q(organizer=request.user) | Q(staff=request.user), event_id=event_id
    ).first()

    if not event:
        return render(request, "events/forbidden.html")

    return render(request, "events/scanner.html", {"event_id": event_id})


@roles_required(["organizer", "checkin-staff"])
def process_qr_code(request):
    """"""

    if request.method == "POST":
        data = json.loads(request.body)
        qr_code_data = data.get("qr_code", "")
        event_id = data.get("event_id", "")

        try:
            ticket = validate_ticket(qr_code_data, event_id)
            if ticket:
                messages.success(request, "Access granted")
                return JsonResponse(
                    {"redirect_url": reverse("scan_qr"), "status": "success"}
                )
        except Exception as e:
            messages.error(request, f"Access denied: {str(e)}")
            return JsonResponse(
                {
                    "redirect_url": reverse("scan_qr", kwargs={"event_id": event_id}),
                    "status": "error",
                }
            )
