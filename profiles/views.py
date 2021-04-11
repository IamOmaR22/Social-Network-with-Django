from django.shortcuts import render
from .models import Profile, Relationship
from .forms import ProfileModelForm
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



def profiles_list_view(request): # All the profiles.
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {
        'qs': qs,
    }
    return render(request, 'profiles/profile_list.html', context)


def invite_profiles_list_view(request): # The list of the profiles whom I can send invites.
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {
        'qs': qs,
    }
    return render(request, 'profiles/to_invite_list.html', context)