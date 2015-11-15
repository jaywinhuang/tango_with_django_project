from django.shortcuts import render
from django.http import	HttpResponse
from rango.models import Category,Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango import bing_search
from django.shortcuts import redirect


# Create your views here.
def index(request):

    # request.session.set_test_cookie()
    #
    # category_list = Category.objects.order_by('-likes')[:5]
    #
    # page_list = Page.objects.order_by('-views')[:5]
    #
    # context_dict = {
    #     'categories':category_list,
    #     'boldmessage':"I am bold font from the context",
    #     'pages':page_list,
    # }
    #
    #
    # return render(request,'rango/index.html', context_dict)

    category_list = Category.objects.all()
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {
        'categories':category_list,
        'boldmessage':"I am bold font from the context",
        'pages':page_list,
    }

    visits = request.session.get('visits')
    if not visits:
        visits = 1

    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')

    if last_visit:

        last_visit_time = datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time ).seconds > 3:
            visits = visits + 1
            reset_last_visit_time = True
    else:

        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    return response


def category(request,category_name_slug):

    content_dict = {

    }

    try:
        category = Category.objects.get(slug=category_name_slug)
        content_dict['category_name'] = category.name
        content_dict['category_name_slug'] = category.slug

        pages = Page.objects.filter(category=category).order_by('-views')

        content_dict['pages'] = pages

        content_dict['category'] = category

    except Category.DoesNotExist:
        pass


    return render(request,'rango/category.html', content_dict)


@login_required
def add_category(request):

    if request.method == 'POST':

        form = CategoryForm(request.POST)

        if form.is_valid():

            form.save(commit=True)

            return index(request)

        else:
            print form.errors

    else:
        form = CategoryForm()

    return render(request,'rango/add_category.html',{'form':form})

@login_required
def add_page(request, category_name_slug):

    content_dict={}

    try:
        cat = Category.objects.get(slug=category_name_slug)

    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':

        form = PageForm(request.POST)

        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()

                return category(request,category_name_slug)
        else:
            print form.errors

    else:
        form = PageForm()

    content_dict = {'form':form,'category':cat}

    return render(request,'rango/add_page.html', content_dict)


def register(request):

    if request.session.test_cookie_worked():
        print ">>>Test cookie worked!"
        request.session.delete_test_cookie()

    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            user.set_password(user.password)
            user.save()

            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    content_dict = {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    }

    return render(request,'rango/register.html',content_dict)

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:

                login(request, user)
                return HttpResponseRedirect('/rango')

            else:
                return HttpResponse("Your Rango account is disabled. ")

        else:
            print "Invalid login details:{0},{1}".format(username,password)
            return HttpResponse("Your rango account is disabled.")

    else:
        return render(request,'rango/login.html',{})

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')

def about(request):

    return render(request,'rango/about.html',{})

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = bing_search.run_qurey(query)


    return render(request,'rango/search.html',{'result_list':result_list})

def track_url(request):
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes += 1
            cat.save()

    return HttpResponse(likes)

def get_category_list(max_results=0, start_with=''):
    cat_list = []
    if start_with:
        cat_list = Category.objects.filter(name__istartswith = start_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    cat_list = []
    start_with = ''
    if request.method == 'GET':
        start_with = request.GET['suggestion']

    cat_list = get_category_list(3,start_with)

    return render(request,'rango/category_list.html', {'cat_list':cat_list})









