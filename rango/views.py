from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from .models import Category, Page
from rango.forms import PageForm, CategoryForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


# Create your views here.


def index(request):
	# return HttpResponse("Rango says hey there world!<br /><a href='/rango/about'>About</a>")
	# context_dict={'boldmessage':"I am bold font from the context"}
	# return render(request,'rango/index.html',context_dict)
	category_list = Category.objects.all()
	page_list=Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list,'pages':page_list}

	visits=request.session.get('visits')
	if not visits:
		visits=1
	reset_last_visit_time=False

	last_visit=request.session.get('last_visit')
	if last_visit:
		last_visit_time=datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")
		if(datetime.now()-last_visit_time).seconds>2:
			visits+=1
			reset_last_visit_time=True

	else:
		reset_last_visit_time=True

	if reset_last_visit_time:
		request.session['last_visit']=str(datetime.now())
		request.session['visits']=visits

	context_dict['visits']=visits
	response=render(request,'rango/index.html',context_dict)

	return response




def about(request):
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0

# remember to include the visit data
	return render(request, 'rango/about.html', {'visits': count})
	# return render(request,'rango/about.html',{})


def category(request, category_name_slug):
	context_dict = {}
	category = Category.objects.get(slug=category_name_slug)
	pages = Page.objects.filter(category=category)
	context_dict['pages'] = pages
	context_dict['category'] = category
	return render(request, 'rango/category.html', context_dict)


def add_page(request, category_name_slug):
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
			return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	return render(request, 'rango/add_page.html', {'form': form, 'category': cat})


def add_category(request):
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)

			# Now call the index() view.
			# The user will be shown the homepage.
			return index(request)
		else:
			# The supplied form contained errors - just print them to the terminal.
			print form.errors
	else:
		# If the request was not a POST, display the form to enter details.
		form = CategoryForm()

	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})


# def register(request):
# 	if request.session.test_cookie_worked():
# 		print ">>>>>Test COOKIE WORKED"
# 		request.session.delete_test_cookie()
# 	# A boolean value for telling the template whether the registration was successful.
# 	# Set to False initially. Code changes value to True when registration succeeds.
# 	registered = False
# 	# If it's a HTTP POST, we're interested in processing form data.
# 	if request.method == 'POST':
# 		# Attempt to grab information from the raw form information.
# 		# Note that we make use of both UserForm and UserProfileForm.
# 		user_form = UserForm(data=request.POST)
# 		profile_form = UserProfileForm(data=request.POST)
#
# 		# If the two forms are valid...
# 		if user_form.is_valid() and profile_form.is_valid():
# 			# Save the user's form data to the database.
# 			user = user_form.save()
# 			# Now we hash the password with the set_password method.
# 			# Once hashed, we can update the user object.
# 			user.set_password(user.password)
# 			user.save()
# 			# Now sort out the UserProfile instance.
# 			# Since we need to set the user attribute ourselves, we set commit=False.
# 			# This delays saving the model until we're ready to avoid integrity problems.
# 			profile = profile_form.save(commit=False)
# 			profile.user = user
#
# 			# Did the user provide a profile picture?
# 			# If so, we need to get it from the input form and put it in the UserProfile model.
# 			if 'picture' in request.FILES:
# 				profile.picture = request.FILES['picture']
#
# 			# Now we save the UserProfile model instance.
# 			profile.save()
#
# 			# Update our variable to tell the template registration was successful.
# 			registered = True
#
# 		# Invalid form or forms - mistakes or something else?
# 		# Print problems to the terminal.
# 		# They'll also be shown to the user.
# 		else:
# 			print user_form.errors, profile_form.errors
#
# 		# Not a HTTP POST, so we render our form using two ModelForm instances.
# 		# These forms will be blank, ready for user input.
# 	else:
# 		user_form = UserForm()
# 		profile_form = UserProfileForm()
#
# 	# Render the template depending on the context
# 	return render(request, 'rango/register.html',
# 				  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


# def user_login(request):
# 	# If the request is a HTTP POST,try to pull out the relevant information
# 	if request.method == 'POST':
# 		# Gather the username and password provided by the user
# 		# This information is obtained from the login form.
# 		# we use request.POST.get('<variable>') as opposed to request.POST['<variable>']
# 		# because the request.POST.get('<variable>') returns None,if the value does not exist.
# 		# while the request.POST['<variable'>] will raise key error exception
# 		username = request.POST.get('username')
# 		password = request.POST.get('password')
#
# 		# Use Django's machinery to attempt to see if the username/password
# 		# combination is valid -a User object is returned if it is .
# 		user = authenticate(username=username, password=password)
#
# 		# If we have a User object,the details are correct
# 		# If None,no user with matching credentials was found
# 		if user:
# 			if user.is_active:
# 				login(request, user)
# 				return HttpResponseRedirect('/rango/')
# 			else:
# 				return HttpResponse('Your Rango account is disabled.')
# 		else:
# 			print "Invalid login details:{0}{1}".format(username, password)
# 			return HttpResponse("Invalid login details supplied.")
#
# 	else:
# 		return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
	return HttpResponse("since you're logged in ,you can see this text")

# @login_required
# def user_logout(request):
# 	logout(request)
# 	return  HttpResponseRedirect('/rango/')


