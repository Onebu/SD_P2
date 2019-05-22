from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Restaurant,Reservation,ViewedRestaurants,Review,RestaurantInsertDate
from .forms import ReservationForm, ReviewForm ,CancellationForm, LoginForm,searchForm
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User,Group
from rest_framework import viewsets
from .serializers import RestaurantSerializer
import datetime
from rest_framework.permissions import BasePermission


def index(request):
    #return HttpResponse("Hello, world. You're at the forkilla home.")
    restaurants_by_city = Restaurant.objects.filter(is_promot="True")
    context = {'restaurants':restaurants_by_city,'promoted': True}
    return render(request, 'forkilla/restaurants.html', context)


def restaurants(request,city="",category=""):
    viewedrestaurants = _check_session(request)
    promoted = False
    res = request.GET.get("rest")
    if res:
        restaurants_by_city = Restaurant.objects.filter(name__iexact=res)
    elif city:
        restaurants_by_city = Restaurant.objects.filter(city__iexact = city)
        if category:

            restaurants_by_city = restaurants_by_city.filter(category__iexact = category)
    else:
        restaurants_by_city = Restaurant.objects.filter(is_promot="True")
        promoted = True
    restaurants_by_city = restaurants_by_city.order_by('category')
    categories = Restaurant.objects.order_by().values('category').distinct()
    cities = Restaurant.objects.order_by().values('city').distinct()
    context ={
        'city':city,
        'category':category,
        'restaurants':restaurants_by_city,
        'viewedrestaurants': viewedrestaurants,
        'promoted':promoted,
        'categories': categories,
        'cities': cities
    }
    return render(request,'forkilla/restaurants.html',context)


def details(request,restaurant_number=""):
    viewedrestaurants = _check_session(request)
    restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
    lastviewed = RestaurantInsertDate(viewedrestaurants=viewedrestaurants, restaurant=restaurant)
    msg = Review.objects.filter(number=restaurant_number).all()
    categories = Restaurant.objects.order_by().values('category').distinct()
    cities = Restaurant.objects.order_by().values('city').distinct()
    lastviewed.save()
    context = {
        'restaurant': restaurant,
        'viewedrestaurants': viewedrestaurants,
        'msg': msg,
        'city': restaurant.city,
        'category': restaurant.category,
        'categories': categories,
        'cities': cities,
    }
    return render(request, 'forkilla/details.html', context)


def _check_session(request):

    if "viewedrestaurants" not in request.session:
        viewedrestaurants = ViewedRestaurants()
        viewedrestaurants.save()
        request.session["viewedrestaurants"] = viewedrestaurants.id_vr
    else:
        viewedrestaurants = ViewedRestaurants.objects.get(id_vr=request.session["viewedrestaurants"])
    return viewedrestaurants


@login_required
def reservation(request):
    viewedrestaurants = _check_session(request)
    try:
        if request.method == "POST":
            form = ReservationForm(request.POST)
            if form.is_valid():
                resv = form.save(commit=False)
                restaurant_number = request.session["reserved_restaurant"]
                resv.restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
                if (resv.restaurant.restaurant_capacity - form.cleaned_data[
                    'num_people'] < 0 or resv.restaurant.restaurant_capacity < form.cleaned_data['num_people']):
                    request.session["result"] = form.errors
                else:
                    resv.restaurant.restaurant_capacity = resv.restaurant.restaurant_capacity - form.cleaned_data[
                        'num_people']
                    resv.user = request.user
                    print(resv.restaurant.restaurant_capacity)
                    Restaurant.objects.get(
                        restaurant_number=restaurant_number).restaurant_capacity = resv.restaurant.restaurant_capacity
                    resv.save()
                    request.session["num"] = form.cleaned_data['num_people']
                    request.session["reservation"] = resv.id
                    request.session["result"] = "OK"


            else:
                request.session["result"] = form.errors
            return HttpResponseRedirect(reverse('checkout'))

        elif request.method == "GET":
            restaurant_number = request.GET["reservation"]
            restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
            request.session["reserved_restaurant"] = restaurant_number

            form = ReservationForm()
            form.initial['user'] = request.user
            context = {
                'restaurant': restaurant,
                'viewedrestaurants': viewedrestaurants,
                'form': form
            }
    except Restaurant.DoesNotExist:
        return HttpResponse("Restaurant Does not exists")
    return render(request, 'forkilla/reservation.html', context)

@login_required
def cancellation(request, id=""):
    viewedrestaurants = _check_session(request)
    id = id
    if(request.method=="POST"):

        form = request.POST
        if Reservation.objects.get(id=id):
            Reservation.objects.get(id=id).delete()
            request.session["result"] = "Z"
        else:
            request.session["result"] = form.errors
        return HttpResponseRedirect(reverse('checkout'))

    else:
        form = CancellationForm()
        form.initial['id'] = id
        resv = Reservation.objects.get(id=id)
        context = {
            'form': form,
            'resv': resv
        }
        return render(request, 'forkilla/cancellation.html', context)
@login_required
def checkout(request):
    result = request.session['result']
    if result == "OK":
        restaurant = Restaurant.objects.get(restaurant_number=request.session['reserved_restaurant'])
        context = {
            'restaurant':restaurant,
            'num_people':request.session["num"],
            'checkout': result
        }
    elif result == "Y":
        restaurant = Restaurant.objects.get(restaurant_number=request.session['reserved_restaurant'])
        context = {
            'restaurant':restaurant,
            'checkout': result,
            'rate': request.session["rating"]
        }
    elif result == "Z":
        context = { 'Z': 1}
    else:
        context = {
            'failed':1
        }
    return render(request, 'forkilla/checkout.html', context)

@login_required
def review(request, restaurant_number=""):
    viewedrestaurants = _check_session(request)
    r = restaurant_number
    if(request.method=="POST"):
        #form = ReviewForm(request.POST)
        #print(request.POST)
        form = request.POST
        message = form["message"]
        number = form["number"]
        rating = form["rating"]
        restaurant = Restaurant.objects.get(restaurant_number=number)
        review = Review(user = request.user,number = number,message =message,rating = rating)
        review.save()
        review.restaurant = restaurant
        review.restaurant.rate = review.rating
        review.restaurant.save()
        review.save()

        msg = Review.objects.filter(number=number).all()
        context = {
            'restaurant': restaurant,
            'msg': msg
        }
        return render(request, 'forkilla/details.html', context)

    else:
        form = ReviewForm()
        form.initial['number'] = r
        form.initial['user'] = request.user
        context = {
            'form': form,
        }
        return render(request, 'forkilla/review.html', context)



def advancedSearch(request):
    viewedrestaurants = _check_session(request)
    if(request.method=="POST"):
        form = request.POST
        city = form["city"]
        category = form["category"]
        if city:
            restaurants_by_city = Restaurant.objects.filter(city__iexact=city)
            if category:
                restaurants_by_city = restaurants_by_city.filter(category__iexact=category)
        else:
            restaurants_by_city = Restaurant.objects.filter(is_promot="True")
        context= {
            'restaurants':restaurants_by_city
        }
        return render(request, 'forkilla/restaurants.html', context)

    else:
        form = searchForm()
        context = {
            'form': form,
        }
        return render(request, 'forkilla/advancedSearch.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth.login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        form = LoginForm()
        return render(request, 'forkilla/login.html', {'form':form})

@login_required(login_url='login')
def reservation_list(request):
    now = datetime.datetime.now()
    past = Reservation.objects.filter(user=request.user).filter(day__lte=now).order_by('day')
    future = Reservation.objects.filter(user=request.user).filter(day__gt=now).order_by('day')
    context = {
        'past': past,
        'future': future
    }
    return render(request, 'forkilla/reservation_list.html', context)


def comparator(request):
    restaurants = Restaurant.objects.all()
    categories = Restaurant.objects.order_by().values('category').distinct()
    cities = Restaurant.objects.order_by().values('city').distinct()
    context = {
        'user' : request.user,
        'restaurants' : restaurants,
        'categories' : categories,
        'cities' : cities,
    }
    return render(request, "forkilla/comparator.html", context)

# Error Pages
def server_error(request):
    return render(request, 'errors/500.html')


def not_found(request):
    return render(request, 'errors/404.html')


class RestaurantEditPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'DELETE':
            group = request.user.groups.filter(name="Commercial")
            if group and 'Commercial' == group[0].name:
                return True
            return False
        return True

    def has_object_permission(self, request, view, obj):
        return True


class RestaurantViewSet(viewsets.ModelViewSet):
            """
            API endpoint that allows Restaurants to be viewed or edited.
            """
            queryset = Restaurant.objects.all().order_by('category')
            serializer_class = RestaurantSerializer
            permission_classes = (RestaurantEditPermission,)

            def get_queryset(self):
                queryset = Restaurant.objects.all()
                city = self.request.query_params.get('city', None)
                category = self.request.query_params.get('category', None)
                price_average = self.request.query_params.get('price_average', None)

                if category is not None:
                    queryset = queryset.filter(category=category)

                if city is not None:
                    queryset = queryset.filter(city=city)

                if price_average is not None:
                    queryset = queryset.filter(price_average__lte=price_average).order_by('price_average')

                return queryset