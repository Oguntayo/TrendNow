from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages as msg
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import User, Message, Comment
from .forms import MessageForm, UserForm, MyUserCreationForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            msg.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            msg.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'trends/login_register.html', context)

# Create your views here.


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'trends/login_register.html', {'form': form})


def home(request):
    form = MessageForm()
    if request.GET.get('q') != None and request.GET.get('q') != '':
        q = request.GET.get('q')
        search = Message.objects.filter(
            Q(recipient__username__icontains=q) |
            Q(name__icontains=q) |
            Q(body__icontains=q)
        )

    else:
        search = ''

    message = Message.objects.all()
    user = User.objects.all()
    q = ''
    if q != '':
        comment = Comment.objects.filter(Q(message__name__icontains=q))[0:3]
    else:
        comment = Comment.objects.all()
    context = {'search': search, 'messages': message,
               'users': user, 'comments': comment, 'form': form}
    return render(request, 'trends/home.html', context)


@login_required(login_url='login')
def createMessage(request):
    form = MessageForm()
    if request.method == 'POST':
        comments = Message.objects.create(
            recipient=request.user,
            name=request.POST.get('name'),
            body=request.POST.get('body')
        )
        return redirect('home')

    context = {'form': form}
    return render(request, 'trends/message_form.html', context)


@login_required(login_url='login')
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    pg = 'update'
    form = MessageForm(instance=message)
    if request.user != message.recipient:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.name = request.POST.get('name')

        message.body = request.POST.get('body')
        message.save()
        return redirect('home')

    context = {'form': form, 'page': pg}
    return render(request, 'trends/update_form.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.recipient:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'trends/delete.html', {'obj': message.name})


def room(request):

    if request.method == 'POST':
        message = Message.objects.get(id=request.POST.get('messageid'))
        comments = Comment.objects.create(
            user=request.user,
            message=message,
            comment=request.POST.get('comment')
        )

        comment = message.comment_set.all()

        return redirect('home')

    return redirect('home')


@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'trends/delete.html', {'obj': comment})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'trends/update_user.html', {'form': form})


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.message_set.all()
    room_messages = user.comment_set.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages}
    return render(request, 'trends/profile.html', context)
