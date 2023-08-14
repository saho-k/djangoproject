from django.shortcuts import render, redirect, get_object_or_404


from . forms import CreateUserForm, LoginForm, ThoughtForm, UpdateUserForm, UpdateProfileForm, CommentForm


from django.contrib.auth.models import auth

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from . models import Thought, Profile


from django.contrib.auth.models import User


from django.core.mail import send_mail

from django.conf import settings

from django.db.models import Q

from django.shortcuts import get_object_or_404, render

 

def homepage(request):

    return render(request, 'journal/index.html')



def register(request):

    form = CreateUserForm()

    if request.method == 'POST':

        form = CreateUserForm(request.POST)

        if form.is_valid():

            current_user = form.save(commit=False)

            form.save()

            #send_mail("Welcome to Edenthought!", "Congratulations on creating your account", settings.DEFAULT_FROM_EMAIL, [current_user.email])


            profile = Profile.objects.create(user=current_user)



            messages.success(request, "User created!")

            return redirect('my-login')

    
    context = {'RegistrationForm': form}


    return render(request, 'journal/register.html', context)



def my_login(request):

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect('dashboard')


    context = {'LoginForm': form}

    return render(request, 'journal/my-login.html', context)





def user_logout(request):

    auth.logout(request)

    messages.success(request, "You were logged out securely!")

    return redirect("")





@login_required(login_url='my-login')
def dashboard(request):

    profile_pic = Profile.objects.get(user=request.user)

    context = {'profilePic': profile_pic}


    return render(request, 'journal/dashboard.html', context)





@login_required(login_url='my-login')
def create_thought(request):

    form = ThoughtForm()

    if request.method == 'POST':

        form = ThoughtForm(request.POST)

        if form.is_valid():

            thought = form.save(commit=False)

            thought.user = request.user

            thought.save()


            messages.success(request, "Thought created!")

            return redirect('my-thoughts')


    context = {'CreateThoughtForm': form}


    return render(request, 'journal/create-thought.html', context)





@login_required(login_url='my-login')
def my_thoughts(request):

    current_user = request.user.id

    thought = Thought.objects.all().filter(user=current_user)


    context = {'AllThoughts': thought}

    return render(request, 'journal/my-thoughts.html', context)



@login_required(login_url='my-login')
def update_thought(request, pk):


    try:

        thought = Thought.objects.get(id=pk, user=request.user)


    except:

        return redirect('my-thoughts')


    form = ThoughtForm(instance=thought)

    if request.method == 'POST':

        form = ThoughtForm(request.POST, instance=thought)

        if form.is_valid():

            form.save()


            messages.success(request, "Thought updated!")
            
            return redirect('my-thoughts')


    context = {'UpdateThought': form}

    return render(request, 'journal/update-thought.html', context)



@login_required(login_url='my-login')
def delete_thought(request, pk):

    try:

        thought = Thought.objects.get(id=pk, user=request.user)

    except:

        return redirect('my-thoughts')


    if request.method == 'POST':

        thought.delete()


        messages.success(request, "Thought deleted!")

        return redirect('my-thoughts')


    return render(request, 'journal/delete-thought.html')






@login_required(login_url='my-login')
def profile_management(request):

    form = UpdateUserForm(instance=request.user)


    profile = Profile.objects.get(user=request.user)


    form_2 = UpdateProfileForm(instance=profile)



    if request.method == 'POST':

        form = UpdateUserForm(request.POST, instance=request.user)

        form_2 = UpdateProfileForm(request.POST, request.FILES, instance=profile)


        if form.is_valid():

            form.save()


            messages.success(request, "Update success!")

            return redirect('dashboard')


        if form_2.is_valid():

            form_2.save()


            messages.success(request, "Update success!")

            return redirect('dashboard')



    context = {'UserUpdateForm': form, 'ProfileUpdateForm': form_2}


    return render(request, 'journal/profile-management.html', context)



@login_required(login_url='my-login')
def delete_account(request):

    if request.method == 'POST':

        deleteUser = User.objects.get(username=request.user)

        deleteUser.delete()


        messages.success(request, "Your account was deleted!")

        return redirect("")


    return render(request, 'journal/delete-account.html')


##### 검색 정보 추가 

def search_results(request):
    query = request.POST.get('q')
    
    if query:
        # 검색어와 일치하는 모든 생각을 찾습니다.
        results = Thought.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()
    else:
        results = []

    context = {
        'query': query,
        'search_results': results
    }

    return render(request, 'journal/search-results.html', context)




####  추가 상세페이지 

def thought_detail(request, pk):
    thought = get_object_or_404(Thought, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.thought = thought
            comment.save()
            return redirect('thought-detail', pk=thought.pk)
    else:
        form = CommentForm()
    return render(request, 'journal/thought-detail.html', {'thought': thought, 'form': form})




##### 댓글 

from django.http import HttpResponseNotAllowed, JsonResponse
 
def add_comment_to_thought(request, thought_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])  # 이 부분을 추가합니다.

    thought = get_object_or_404(Thought, pk=thought_id)
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.thought = thought
        comment.save()
        
        return JsonResponse({"success": True, "comment_text": comment.text})
    else:
        return JsonResponse({"success": False, "error": "Invalid form data."})
