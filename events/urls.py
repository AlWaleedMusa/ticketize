from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("event/add/", views.add_event, name="add_event"),
    path("event/details/<str:pk>/", views.event_detail, name="event_detail"),
    path("event/delete/<str:pk>/", views.delete_event, name="event_delete"),
    path("event/book/<str:event_id>/", views.book_event, name="book_event"),
    path("event/staff/<str:event_id>/", views.add_staff, name="add_staff"),
    path("confirm/", views.confirm_email, name="confirm_email"),
    path("scan-qr/<str:event_id>", views.qr_code_scanner, name="scan_qr"),
    path("process-qr-code/", views.process_qr_code, name="process_qr_code"),
    path("scan-qr/entry_granted/", views.entry_granted, name="entry_granted"),
    path("scan-qr/entry_denied/", views.entry_denied, name="entry_denied"),
]
