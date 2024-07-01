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
    # Flaw 2, broken access control:
    sender = User.objects.get(id=sender)
    # Simplest way to fix is to just add a check (best would be to change the
    # route to only accept one parameter, but this requires changes in multiple
    # places). Redirecting to index if sender is wrong is simpler, and has same
    # effect.
    #
    # if sender != request.user:
    #     return redirect("index")

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
    # FLAW 1, SQL injection:
    sql = (
        "INSERT INTO project_message (sender_id, receiver_id, content, time) VALUES "
        f"('{sender.id}', '{receiver}', '{content}', datetime('now'));"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return redirect(reverse("messages", args=(sender.id, receiver)))


# Fixed version. Both flaws 1 and 3 are fixed here.
# @login_required
# def send_view(request, receiver):
#     sender = request.user
#     content = request.POST.get("message", "")
#     receiver = User.objects.get(id=receiver)
#     message = Message(sender=sender, receiver=receiver, content=content)
#     message.save()
#     return redirect(reverse("messages", args=(sender.id, receiver.id)))


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
