from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(default="Nibrass ",max_length=30)
    last_name = models.CharField(default="Haider ",max_length=150)
    email = models.EmailField(default="user@gmail.com") # name that appears on screen (complementary username)
    birthday = models.DateField(auto_now=False, auto_now_add=False,null=True)


    """"@receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
            if created:
                    Profile.objects.create(user=instance)
            instance.profile.save()"""



class Restaurant(models.Model):
    CATEGORIES = (
        ("Rice", "Rice"),
        ("Fusi", "Fusion"),
        ("BBQ", "Barbecue"),
        ("Chin", "Chinese"),
        ("Medi","Mediterranean"),
        ("Crep","Creperie"),
        ("Hind","Hindu"),
        ("Japa","Japanese"),
        ("Ital","Italian"),
        ("Mexi","Mexican"),
        ("Peru", "Peruvian"),
        ("Russ","Russian"),
        ("Turk","Turkish"),
        ("Basq","Basque"),
        ("Vegy", "Vegetarian"),
        ("Afri","African"),
        ("Egyp","Egyptian"),
        ("Grek","Greek")
    )
    _d_categories = dict(CATEGORIES)
     
    restaurant_number = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=50)
    menu_description = models.TextField()
    price_average = models.DecimalField(max_digits=5, decimal_places=2)
    is_promot = models.BooleanField()
    rate = models.DecimalField(max_digits=3, decimal_places=1)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    featured_photo = models.ImageField(upload_to="res")
    category = models.CharField(max_length=5, choices=CATEGORIES)
    restaurant_capacity = models.PositiveIntegerField(max_length=3)
    
    def get_human_category(self):
        return self._d_categories[self.category]
        
    def __str__(self):
        return ('[**Promoted**]' if self.is_promot else '') + "[" + self.category + "] " \
                "[" + self.restaurant_number + "] " + self.name + " - " + self.menu_description + " (" + str(self.rate) + ")" \
                ": " + str(self.price_average) + u" €"


class Reservation(models.Model):

    SLOTS = (
        ("morning_first", "12h00"),
        ("morning_second", "13h00"),
        ("morning_third", "14h00"),
        ("morning_fourth", "15h00"),
        ("evening_first", "20h00"),
        ("evening_second", "21h00"),
        ("evening_third", "22h00"),
    )
    _d_slots = dict(SLOTS)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    id = models.AutoField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant)
    day = models.DateField(default=datetime.now)
    time_slot = models.CharField(max_length=15, choices=SLOTS)
    num_people = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def get_human_slot(self):
        return self._d_slots[self.time_slot]


class ViewedRestaurants(models.Model):
   id_vr = models.AutoField(primary_key=True)
   restaurant = models.ManyToManyField(Restaurant, through='RestaurantInsertDate')


class RestaurantInsertDate(models.Model):
    viewedrestaurants = models.ForeignKey(ViewedRestaurants, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']


class Review(models.Model):

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    number = models.CharField(max_length=8, default="")
    message = models.TextField()
    rating = models.IntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(5)])


