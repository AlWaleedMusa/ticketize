from django.contrib import admin

from .models import CustomUser, Event, Booking, Ticket, ConfirmationToken

admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(Booking)
admin.site.register(Ticket)
admin.site.register(ConfirmationToken)
