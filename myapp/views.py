from django.shortcuts import render
from decimal import Decimal

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Flight, Book
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import auth, messages
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from django.views.decorators.http import require_http_methods
def index(request):

    return render(request, 'myapp/index.html')

def home(request):
    if request.user.is_authenticated:
        return render(request, 'myapp/home.html')
    else:
        return render(request, 'myapp/signin.html')




@login_required(login_url='signin')
def findflight(request):
    context = {}
    all_flights = Flight.objects.all()
    context['all_flights'] = all_flights
    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        time_r = request.POST.get('time')

        date_obj = datetime.strptime(date_r, "%B %d, %Y").date()

        if time_r == 'midnight':
            time_obj = datetime.strptime('12 AM', "%I %p").time()
        elif time_r == 'noon':
            time_obj = datetime.strptime('12 PM', "%I %p").time()
        else:
            time_r_adjusted = time_r.replace('.', '')
            time_obj = datetime.strptime(time_r_adjusted, "%I %p").time()




        flight_list = Flight.objects.filter(source=source_r, dest=dest_r, date=date_obj, time=time_obj)

        if flight_list:
            return render(request, 'myapp/list.html', {'flight_list': flight_list})
        else:
            messages.error(request, "Sorry, no flights available")
            return redirect('findflight')
    else:
        source_airports = Flight.objects.values_list('source', flat=True).distinct()
        dest_airports = Flight.objects.values_list('dest', flat=True).distinct()
        date_choices = Flight.objects.values('date').distinct().order_by('date')
        time_choices = Flight.objects.values('time').distinct().order_by('time')
        context['source_airports'] = source_airports
        context['dest_airports'] = dest_airports
        context['date_choices'] = date_choices
        context['time_choices'] = time_choices

    return render(request, 'myapp/findflight.html',context)






@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('flight_id')
        seats_r = int(request.POST.get('no_seats'))
        flight = Flight.objects.get(id=id_r)
        if flight:
            if flight.rem > int(seats_r):
                name_r = flight.flight_name
                cost = int(seats_r) * flight.price
                source_r = flight.source
                dest_r = flight.dest
                nos_r = Decimal(flight.nos)
                price_r = flight.price
                date_r = flight.date
                time_r = flight.time
                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = flight.rem - seats_r
                Flight.objects.filter(id=id_r).update(rem=rem_r)
                book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, flight_name=name_r,
                                           source=source_r, flightid=id_r,
                                           dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                           status='BOOKED')
                print('------------book id-----------', book.id)
                # book.save()
                return render(request, 'myapp/bookings.html', locals())
            else:
                context["error"] = "Sorry select fewer number of seats"
                return render(request, 'myapp/findflight.html', context)

    else:
        return render(request, 'myapp/findflight.html')


@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('flight_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            flight = Flight.objects.get(id=book.flightid)
            rem_r = flight.rem + book.nos
            Flight.objects.filter(id=book.flightid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            return redirect('seebookings')
        except Book.DoesNotExist:
            context["error"] = "Sorry You have not booked that flight"
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findflight.html')


@login_required(login_url='signin')
def seebookings(request,new={}):
    context = {}
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)
    if book_list:
        return render(request, 'myapp/booklist.html', locals())
    else:
        return render(request, 'myapp/bookings_not_found.html')
def view_bookings(request):
    bookings = Book.objects.all()
    return render(request, 'myapp/view_bookings.html', {'bookings': bookings})

def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')

        if User.objects.filter(username=name_r).exists():
            error_message = "Username already exists. Please choose a different username."
            context["error_message"] = error_message
            return render(request, 'myapp/signup.html', context)

        user = User.objects.create_user(name_r, email_r, password_r)
        if user:
            login(request, user)
            return render(request, 'myapp/thank.html')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html',context)


def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            # username = request.session['username']
            context["user"] = name_r
            context["id"] = request.user.id
            return render(request, 'myapp/home.html', context)
            # return HttpResponseRedirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)

def adminsignin(request):
    context = {}

    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = auth.authenticate(request, username=name_r, password=password_r)

        if user is not None:
            if user.is_superuser:  # Check if the user is a superuser (admin)
                auth.login(request, user)
                return redirect('adminpage')
            else:
                context["error"] = "You don't have sufficient privileges to access the admin page."
        else:
            context["error"] = "Invalid credentials. Please provide valid username and password."

    return render(request, 'myapp/admin_home.html', context)

def adminpage(request):
    return render(request,'myapp/adminpage.html')


def addfile(request):
    if request.method == 'POST':
        flight_name = request.POST.get('flight_name')
        source = request.POST.get('source')
        dest = request.POST.get('dest')
        try:
            nos = Decimal(request.POST.get('nos'))
            rem = Decimal(request.POST.get('rem'))
            price = Decimal(request.POST.get('price'))
        except (InvalidOperation, TypeError, ValueError):
            error = 'Invalid decimal value provided.'
            return render(request, 'myapp/addfile.html', {'error': error})
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Create a new Flight object with the form data
        flight = Flight(
            flight_name=flight_name,
            source=source,
            dest=dest,
            nos=nos,
            rem=rem,
            price=price,
            date=date,
            time=time
        )
        flight.save()  # Save the flight object to the database
        messages.success(request, 'Flight added successfully.')
        # Redirect to a success page or perform any other necessary actions
        return redirect('addfile')  # Assuming you have a URL pattern named 'success'

    return render(request, 'myapp/addfile.html')


def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)
