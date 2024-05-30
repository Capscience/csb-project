# from django.shortcuts import render
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import connection
from project.models import Message
from django.urls import reverse

# Create your views here.


@login_required
def index(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, "index.html", {"users": users, "current": request.user})


@login_required
def messages_view(request, sender, receiver):
    sender = User.objects.get(id=sender)
    receiver = User.objects.get(id=receiver)
    messages = Message.objects.filter(
        Q(sender=sender) & Q(receiver=receiver)
        | Q(sender=receiver) & Q(receiver=sender)
    ).order_by("time")
    return render(
        request, "messages.html", {"messages": messages, "receiver": receiver}
    )


@login_required
def send_view(request, receiver):
    sender = request.user
    content = request.GET.get("message", "")
    sql = (
        "INSERT INTO project_message (sender_id, receiver_id, content, time) VALUES "
        f"('{sender.id}', '{receiver}', '{content}', datetime('now'));"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return redirect(reverse("messages", args=(sender.id, receiver)))


def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("index")
    else:
        # Return an 'invalid login' error message.
        return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")
