from django.shortcuts import render
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView
from django.contrib.auth.models import User
# Create your views here.

def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None ,instance=profile)
    confirm = False

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }
    return render(request, 'profiles/myprofile.html', context)


def invites_received_view(request):  # Others user when send me a request.
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitations_received(profile)  # Geeting all the invitations for this particular profile.

    context = {
        'qs': qs,
    }
    return render(request, 'profiles/my_invites.html', context)



def invite_profiles_list_view(request): # The list of the profiles whom I can send invites.
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {
        'qs': qs,
    }
    return render(request, 'profiles/to_invite_list.html', context)



# def profiles_list_view(request): # All the profiles.
#     user = request.user
#     qs = Profile.objects.get_all_profiles(user)

#     context = {
#         'qs': qs,
#     }
#     return render(request, 'profiles/profile_list.html', context)



class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'qs' # Also we can use object_list as context instead of qs by default.

    def get_queryset(self): # Override the get_queryset method because of we can get what we want.
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs): # This method allows us to provide some additional context to the template. 
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)   # Grab this user. This should give us each time a user.
        profile = Profile.objects.get(user=user) # Grab the profile once we get the user.
        
        rel_r = Relationship.objects.filter(sender=profile)   # Relationship receiver where we are going to simply query relationships by the sender equal to our profile. Here we are storing relationships where we invited other users to friends. 
        rel_s = Relationship.objects.filter(receiver=profile)  # Relationship sender where we are going to simply query relationships by the receiver equal to our profile.        
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user) # receiver is relate to the user.
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context['rel_receiver'] = rel_receiver 
        context['rel_sender'] = rel_sender 
        
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        return context