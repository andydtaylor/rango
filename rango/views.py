from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from datetime import datetime


# Create your views here.
from django.http import HttpResponse
from rango.models import *
from rango.helper_funcs import *
from rango.forms import CategoryForm, PageForm

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse

from rango.forms import UserForm, UserProfileForm

from django.contrib.auth.decorators import login_required

from django.contrib.auth import logout

from django.contrib.auth.models import User

from rango.bing_search import run_query

from django.contrib.auth.models import User

from django.shortcuts import redirect


def index(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # Query for categories - add the list to our context dictionary.
    category_list = get_5_categories()
    context_dict = {'categories': category_list}
        # Added this part for +pages exercise
    page_list = Page.objects.order_by('-views')[:5]
    context_dict['pages'] = page_list
    # End add

    #### NEW SESSION CODE ####

    response = render_to_response('rango/index.html', context_dict, context)

    # look for vists cookie and extract value if there
    visits = request.session.get('visits', 0)

    #Obtain current time for comparison purposes below
    current_visit_time = datetime.now()
    # Make text version of current time
    current_visit_time_text = datetime.strftime(current_visit_time, "%Y-%m-%d %H:%M:%S")

    # look for last visit cookie
    if request.session.get('last_visit'):
        last_visit = request.session.get('last_visit')
        # Parse last visit text into time data
        last_visit_time = datetime.strptime(last_visit, "%Y-%m-%d %H:%M:%S")

        # determine number of days elapsed
        if (current_visit_time - last_visit_time).days > 0:

            # increment cookie by 1
            request.session['visits'] = visits + 1
            # update last visit cookie
            request.session['last_visit'] = current_visit_time_text
    else:
    # create last visit cookie
        request.session['last_visit'] = current_visit_time_text
    return response


def about(request):
    #return HttpResponse("Rango says: Here is the about page. <a href= '/rango/'>Index</a>")
    if request.session.get('visits'):
        visit_count = request.session.get('visits')
    else:
        visit_count = 0

    about_context = RequestContext(request)
    about_dict = {'origin': "This is where it all began", 'visit_count': visit_count}
    return render_to_response('rango/about.html',about_dict, about_context)

def category(request, category_name_url):


    context = RequestContext(request)
    category_name = endecode(category_name_url)
    category_list = get_5_categories()

    context_dict = {'category_name': category_name, 'category_name_url': category_name_url, 'categories': category_list}

    try:

        category = Category.objects.get(name=category_name)
        context_dict['category'] = category

        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages

    except Category.DoesNotExist:
        pass


    if request.method == 'POST':
        if 'query' in request.POST:
            query = request.POST['query'].strip()
            print query

            if query:
                result_list = run_query(query)
                print result_list
                context_dict['result_list'] = result_list


    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)



def add_category(request):
    context = RequestContext(request)
    category_list = get_5_categories()

    if request.user.is_active and request.method == 'POST':

        #print request.method
        #print request.POST.copy()

        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors

    else:

        #print request.method
        #print request.GET.copy()
        form = CategoryForm
    context_dict = {'form': form, 'categories': category_list}


    return render_to_response('rango/add_category.html', context_dict, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    category_name = endecode(category_name_url)
    category_list = get_5_categories()
    context_dict = {'category_name_url': category_name_url, 'category_name': category_name, 'categories': category_list}

    if request.user.is_active and request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:

                return render_to_response( 'rango/add_page.html',
                                          context_dict,
                                          context)



            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            #print request
            #print category_name_url
            print category_name_url
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict['form'] = form

    return render_to_response( 'rango/add_page.html', context_dict, context)



def register(request):

    context = RequestContext(request)
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

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

    return render_to_response(
        'rango/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
        context)




def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            try:
                username = User.objects.get(username=username)
                print "Invalid login details: {0}, {1}".format(username, password)
                return HttpResponse("Invalid password details supplied.")
            except User.DoesNotExist:
                print "Invalid login details: {0}, {1}".format(username, password)
                return HttpResponse("Invalid login and password details supplied.")

    else:
        return render_to_response('rango/login.html', {}, context)


@login_required
def restricted(request):
    context = RequestContext(request)

    return render_to_response('rango/restricted.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')

@ login_required
def view_profile(request):
    # get basics
    context = RequestContext(request)
    # Augment with All category data
    category_list = get_5_categories()
    context_dict = {'categories': category_list}
    # Identify user (login required and User middleware)
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up

    return render_to_response('rango/profile.html', context_dict, context)

def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                thispage = Page.objects.get(id=page_id)
                thispage.views = thispage.views + 1
                thispage.save()
                url = thispage.url
            except:
                pass
    return redirect(url)



@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

def suggest_category(request):
    context = RequestContext(request)
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)
    return render_to_response('rango/category_list.html', {'categories': cat_list }, context)

@login_required
def auto_add_page(request):
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render_to_response('rango/page_list.html', context_dict, context)











