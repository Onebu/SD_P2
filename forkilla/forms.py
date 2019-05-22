from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation,Review,Restaurant


class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation
        fields = ["day", "time_slot", "num_people"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['message', 'rating', 'number']


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('username','password')


class CancellationForm(forms.ModelForm):

    class Meta:
        model = Reservation

        fields = ["id"]


class searchForm(forms.ModelForm):

    class Meta:
        model = Restaurant
        fields = ['city','category']