from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("messages/<str:sender>/<str:receiver>/",
         views.messages_view, name="messages"),
    path("logout/", views.logout_view, name="logout"),
    path("send/<str:receiver>/", views.send_view, name="send"),
]
