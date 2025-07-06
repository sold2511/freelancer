from django.db.models import *
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    
    phone = CharField(max_length=20,unique=True)
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )
    tagline = CharField(max_length=100)
    bio = TextField()
    website = URLField(blank=True)
    profile_pic = ImageField(upload_to="profile/",blank=True )
    role = CharField(max_length=20, choices=ROLE_CHOICES)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone', 'role','password']
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_freelancer(self):
        print('checking freelancer')
        if(hasattr(self, 'freelancer')):
            print(self.freelancer)
            return self.freelancer
        return None

    def get_business(self):
        if(hasattr(self, 'business')):
            return self.business
        return None