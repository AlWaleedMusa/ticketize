from django import forms

from .models import Event, Booking


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        exclude = (
            "organizer",
            "link",
            "checked_in_count",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image_url"].widget.attrs.update({"class": "px-4"})


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        exclude = ("event",)
        widgets = {
            "email": forms.EmailInput(attrs={"type": "email"}),
        }
