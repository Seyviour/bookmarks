from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

from common.decorators import ajax_required
from actions.utils import create_action

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.models import Action
# Create your views here.

def register(request): 
    if request.method == 'POST': 
        user_form = UserRegistrationForm(request.POST)
        print(user_form)
        if user_form.is_valid(): 
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request,
                            'account/register_done.html', 
                            {'new_user': new_user},)
    else: 
        user_form = UserRegistrationForm()
    return render(request, 
                    'account/register.html', 
                    {'user_form': user_form})

@login_required
def dashboard(request): 
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)

    if following_ids: 
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')[:10]\
                    .prefetch_related('target')[:10]
    print(actions)
    return render(request, 
                'account/dashboard.html',
                {'section': 'dashboard',
                'actions': actions})


@login_required
def edit(request): 
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid(): 
            user_form.save()
            profile_form.save()
            messages.success(request, 'profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    
    return render(request,
                    'account/edit.html',
                    {
                        'user_form': user_form,
                        'profile_form':profile_form
                    },)

@login_required
def user_detail(request, username): 
    user = get_object_or_404(User,
                            username=username,
                            is_active=True)
    return render(request,
                'account/user/detail.html',
                {'section': 'people',
                'user': user })

@login_required
def user_list(request): 
    users = User.objects.filter(is_active=True)
    #print(users)
    paginator = Paginator(users, 8)
    page = request.GET.get('page')

    try: 
        users_list = paginator.page(page)
    except PageNotAnInteger: 
        users_list = paginator.page(1)
    except EmptyPage: 
        users_list = paginator.page(paginator.num_pages)

    print(users_list)
    
    return render(request, 
                    'account/user/list.html',
                    {'section': 'pepole',
                    'users_list': users_list})

@ajax_required
@require_POST
def user_follow(request): 
    user_id = request.POST.get('id')
    action = request.POST.get('action')

    json_ok = JsonResponse({'status':'ok'})
    json_error = JsonResponse({'status':'error'})

    if user_id and action: 
        try: 
            user_to = User.objects.get(id=user_id)
            if action == 'follow': 
                Contact.objects.get_or_create(
                    user_from = request.user,
                    user_to = user_to
                )
                create_action(request.user, 'followed', user_to)
                return json_ok
            elif action == 'unfollow': 
                Contact.objects.filter(user_from=request.user,
                                         user_to=user_to).delete()
                return json_ok
            else: 
                raise("Invalid action on follow intent")
                return json_error
        
        except User.DoesNotExist:
            return json_error
    else: 
        return json_error






    




"""
def user_login(request): 
    if request.method == 'POST': 
        form = LoginForm(request.POST)
        if form.is_valid(): 
            cd = form.cleaned_data
            user = authenticate(request, 
                                username = cd['username'],
                                password = cd['password'], )
            if user is not None: 
                if user.is_active: 
                    login(request, user)
                    return HttpResponse('Authenticated Successfully')

                else: 
                    return HttpResponse('Disabled Account')
                
            else: 
                return HttpResponse('invalid login')
    
    elif request.method == 'GET': 
        form = LoginForm()
    
    return render(request, 'account/login.html', {'form': form})
"""

