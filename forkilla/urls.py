from django.conf.urls import url
from django.contrib.auth.views import login, logout

from . import views

listOfAddresses = ["161.116.56.65","161.116.56.165"]
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^restaurants/$', views.restaurants, name='restaurants'),
    url(r'^restaurants/(?P<city>.*)/$', views.restaurants, name='restaurants'),
    url(r'^restaurant/(?P<restaurant_number>.*)/$', views.details, name='details'),
    url(r'^reservation/$', views.reservation, name='reservation'),
    url(r'^restaurants/(?P<city>.*)/(?P<category>.*)$', views.restaurants,name = 'restaurants'),
    url(r'^reservation/checkout/$', views.checkout, name='checkout'),
    url(r'^reservation_list/$', views.reservation_list, name='reservation_list'),
    url(r'^review/(?P<restaurant_number>.*)', views.review, name='review'),
    url(r'^cancellation/(?P<id>.*)/$', views.cancellation, name='cancellation'),
    url(r'^accounts/login/$',  login, name='login'),
    url(r'^accounts/logout/$',  logout,  {'next_page': '/'}, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^comparator$', views.comparator, name='comparator'),
    url(r'^advancedSearch/$', views.advancedSearch, name='advancedSearch'),
]

