from datetime import date

from django import forms

from .models import Event, Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div


class EventForm(forms.ModelForm):
    """"""

    class Meta:
        model = Event
        exclude = (
            "organizer",
            "link",
            "checked_in_count",
            "staff",
            "confirmed_tickets",
            "status",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "min": date.today()}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("name", css_class="w-full p-1"),
            ),
            Row(
                Column("description", css_class="w-full sm:w-1/2 p-1"),
            ),
            Row(
                Column("date", css_class="w-full sm:w-1/3 p-1"),
                Column("start_time", css_class="w-full sm:w-1/3 p-1"),
            ),
            Row(
                Column("image_url", css_class="w-full sm:w-1/2 px-2"),
            ),
            Row(
                Column("location", css_class="w-full sm:w-1/2 p-1"),
                Column("available_tickets", css_class="w-1/4 p-1"),
            ),
            Div(
                Submit(
                    "submit",
                    (
                        "Create Event"
                        if self.request.resolver_match.url_name == "add_event"
                        else "Update Event"
                    ),
                    css_class="w-full sm:w-1/4 text-white bg-[#FFA300] border focus:outline-none font-medium rounded-lg text-sm px-4 py-3 cursor-pointer",
                ),
                css_class="flex justify-start",
            ),
        )


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        exclude = ("event",)
        widgets = {
            "email": forms.EmailInput(attrs={"type": "email"}),
        }


class AddStaffForm(forms.ModelForm):
    """"""

    name = forms.CharField(label="Name")
    email = forms.EmailField(label="Email")

    class Meta:
        model = Event
        fields = ("name", "email")
