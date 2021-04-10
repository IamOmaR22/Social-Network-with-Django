from django.db import models
from django.contrib.auth.models import User

from .utils import get_random_code # For slug field
from django.template.defaultfilters import slugify

from django.db.models import Q
# Create your models here.

class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)  # sender from Relationship model.
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))

        accepted = []
        for rel in qs:
            if rel.status == 'accepted':
                accepted.append(rel.receiver)
                accepted.append(rel.sender)
        print(accepted)

        available = [profile for profile in profiles if profile not in accepted] # List comprehension
        print(available)
        return available

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles

class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Every user will have only his own profile.
    bio = models.TextField(default='No bio ....', max_length=300)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='avatars/') # Create media_root folder within static_cdn. Put a avatar.png within media_root folder.
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ProfileManager()

    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def get_posts_no(self):
        return self.posts.all().count()  # posts is the related_name from author field of Post model. Also we can use modelname_set.

    def get_all_authors_posts(self):
        return self.posts.all()

    def get_likes_given_no(self):
        likes = self.like_set.all()  # modelname_set. relationship with post field of like model.
        total_liked = 0
        for item in likes:
            if item.value == 'Like':
                total_liked +=1
        return total_liked

    def get_likes_received_no(self):
        posts = self.posts.all()  # posts is the related_name of author field of Post model.
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count()
        return total_liked

    def __str__(self):
        # return f'{self.user.username}-{self.created}'
        return f'{self.user.username}-{self.created.strftime("%d-%m-%Y")}'

    def save(self, *args, **kwargs):  # For random slug field, created get_random_code function into utils.py file.
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name) + '' + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + '' + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
            to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)



STATUS_CHOICES = (   # for status field. 
    ('send', 'send'),
    ('accepted', 'accepted'),
)

class RelationshipManager(models.Manager):
    def invitations_received(self, receiver): # receiver is the ForeignKey field of Relationship model.
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs

    # Relationship.objects.invitations_received(myprofile)  # All the relationship received for this particular profile.


class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager() # Extends our existing manager.

    def __str__(self):
        return f'{self.sender}-{self.receiver}-{self.status}'

