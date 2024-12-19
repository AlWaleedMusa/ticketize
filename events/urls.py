from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("event/add/", views.add_event, name="add_event"),
    path("event/details/<str:pk>/", views.event_detail, name="event_detail"),
    path("event/delete/<str:pk>/", views.delete_event, name="event_delete"),
    path("event/book/<str:event_id>/", views.book_event, name="book_event"),
    path("event/staff/<str:event_id>/", views.add_staff, name="add_staff"),
    path("confirm/", views.confirm_email, name="confirm_email"),
    path("scan-qr/<str:event_id>", views.qr_code_scanner, name="scan_qr"),
    path("process-qr-code/", views.process_qr_code, name="process_qr_code"),
]
