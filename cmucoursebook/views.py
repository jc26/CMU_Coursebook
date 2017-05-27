from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.core import serializers

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Imports the model in models.py
from cmucoursebook.models import *

# Used to create and manually log in a user
from cmucoursebook.forms import *

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

import csv, collections

# register page
@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    # Check the validity of the form data
    if not form.is_valid():
        return render(request, 'register.html', context)

    # Creates the new user and its empty profile
    new_user = User.objects.create_user(first_name=form.cleaned_data['firstname'],
                                        last_name=form.cleaned_data['lastname'],
                                        username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'])

    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    # Create a profile for the new user
    new_profile = Profile.objects.create(user=new_user)
    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)
    email_body = """
    Welcome to the CMU Course Book!
    Please click the link below to verify your email address and complete the registration of your account:
      http://%s%s
    """ % (request.get_host(), reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="zhouchep@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']

    return render(request, 'need_confirm.html', context)
    # return redirect(reverse('home'))

# wait to confirm
@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    context = {'user': user}
    return render(request, 'confirmed.html', context)


# the dashboard
@login_required
def home(request):
    the_profile = Profile.objects.get(user=request.user)
    courses = the_profile.curr.all()

    courses_as_list = []
    i = 1
    for course in courses:
        courses_as_list.append((course, i))
        i = i + 1

    monday = []
    tuesday = []
    wednesday = []
    thursday = []
    friday = []
    for course, index in courses_as_list:
        days = course.days.split(':')
        if 'MN' in days:
            monday.append((course, index))
        if 'TU' in days:
            tuesday.append((course, index))
        if 'WD' in days:
            wednesday.append((course, index))
        if 'TH' in days:
            thursday.append((course, index))
        if 'FR' in days:
            friday.append((course, index))

    # if user is super user
    formfile = FileForm()
    context = {'user':request.user, 'formfile':formfile, 'courses':courses,
        'monday':monday, 'tuesday':tuesday, 'wednesday':wednesday, 'thursday':thursday, 'friday':friday,
        'pending':the_profile.pending}
    return render(request, 'home.html', context)



@login_required
def profile(request, username):
    the_user = request.user
    the_profile = Profile.objects.get(user=request.user)

    try:
        c_user = User.objects.get(username=username)
        c_profile = Profile.objects.get(user=c_user)
    except User.DoesNotExist:
        c_user = None

    if c_user == request.user:
        formuser = UserForm()
        formprofile = ProfileForm()
        formimage= ImageForm()
    else:
        formuser = None
        formprofile = None
        formimage = None

    courses_curr = c_profile.curr.all()
    courses_past = c_profile.past.all()
    courses_plan = c_profile.plan.all()
    courses_like = c_profile.liked.all()


    pending = the_profile.pending

    isFriend = True
    try:
        the_profile.friends.get(username=username)
    except User.DoesNotExist:
        isFriend = False

    isPending = True
    try:
        c_profile.pending_friends.get(username=the_user.username)
    except User.DoesNotExist:
        isPending = False

    theyIsPending = True    # check to see if they waiting on you to accept/deny friendship
    try:
        the_profile.pending_friends.get(username=c_user.username)
    except User.DoesNotExist:
        theyIsPending = False


    context = {'cuser': c_user, 'profile': c_profile, 'user': the_user, 'formimage': formimage,
               'formuser': formuser, 'formprofile': formprofile, 'courses_curr': courses_curr,
               'courses_past': courses_past, 'courses_plan': courses_plan, 'courses_like': courses_like,
               'pending': pending, 'isFriend': isFriend, 'isPending': isPending, 'theyIsPending': theyIsPending}

    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'GET':
        return redirect(reverse('home'))

    the_user = request.user
    form_user = UserForm(request.POST, request.FILES, instance=the_user)
    form_user.save()

    the_profile = Profile.objects.get(user=the_user)
    form_profile = ProfileForm(request.POST, request.FILES, instance=the_profile)
    if form_profile.is_valid():
        form_profile.save()

    return redirect(reverse('profile', kwargs={'username':request.user.username}))


@login_required
def edit_image(request):
    if request.method == 'GET':
        return redirect(reverse('home'))

    the_user = request.user
    the_profile = Profile.objects.get(user=the_user)

    form_image = ImageForm(request.POST, request.FILES, instance=the_profile)
    if form_image.is_valid():
        form_image.content_type = form_image.cleaned_data['img'].content_type
        form_image.save()

    return redirect(reverse('profile', kwargs={'username': request.user.username}))

@login_required
def get_image(request, username):
    the_profile = get_object_or_404(Profile, user=User.objects.get(username=username))
    the_img = the_profile.img
    if not the_img:
        # the_img = open("cmucoursebook/static/image/default.jpg")
        # the_img = open("cmucoursebook/static/default.jpg")
        the_img = open("/home/ubuntu/Final_Sprint/cmucoursebook/static/default.jpg")
    img_type = "image/jpeg"
    return HttpResponse(the_img, content_type=img_type)


# search friends
@login_required
def friends(request):
    the_profile = Profile.objects.get(user=request.user)
    friends = the_profile.friends.all()
    pending_friends = the_profile.pending_friends.all()
    pending = the_profile.pending

    context = {'friends': friends, 'pending_friends': pending_friends, 'pending': pending}
    return render(request, 'friends.html', context)

# friendship request
@login_required
def request_friendship(request, username):
    # target_user
    try:
        target_user = User.objects.get(username=username)
        target_profile = Profile.objects.get(user=target_user)
    except:
        print("malformed input")
        return redirect(reverse('home'))

    # add current user to target user's pending friends
    target_profile.pending_friends.add(request.user)
    # increment their pending count by 1
    target_profile.pending = target_profile.pending_friends.all().count()
    target_profile.save()

    # assuming you can only request friendship on their profile page, this will redirect back to same page
    return redirect(reverse('profile', kwargs={'username': username}))

# friendship confirm
@login_required
def confirm_friendship(request, username):
    # current user
    the_user = request.user
    the_profile = Profile.objects.get(user=the_user)

    # target user
    try:
        target_user = User.objects.get(username=username)
        target_profile = Profile.objects.get(user=target_user)
    except:
        print("malformed input")
        return redirect(reverse('home'))

    # add target user to friends
    the_profile.friends.add(target_user)
    # remove target user from pending friends
    the_profile.pending_friends.remove(target_user)
    # decrement your pending count by 1
    the_profile.pending = the_profile.pending_friends.all().count()
    the_profile.save()
    # add you to target's friendlist
    target_profile.friends.add(the_user)

    # assuming you can only confirm/deny friendship on your friends plage, redirects back to friends page
    return redirect(reverse('friends'))

# friendship deny
@login_required
def deny_friendship(request, username):
    # current user
    the_profile = Profile.objects.get(user=request.user)

    # target user
    try:
        target_user = User.objects.get(username=username)
    except:
        print("malformed input")
        return redirect(reverse('home'))

    # remove target user from pending friends
    try:
        the_profile.pending_friends.remove(target_user)
    except:
        print("malformed input")
        return redirect(reverse('home'))

    # decrement your pending count by 1
    the_profile.pending = the_profile.pending_friends.all().count()
    the_profile.save()

    # assuming you can only confirm/deny friendship on your friends plage, redirects back to friends page
    return redirect(reverse('friends'))

# remove friend
@login_required
def remove_friend(request, username):
    the_user = request.user
    the_profile = Profile.objects.get(user=request.user)
    try:
        target_user = User.objects.get(username=username)
        target_profile = Profile.objects.get(user=target_user)

        the_profile.friends.remove(target_user)
        target_profile.friends.remove(the_user)
    except:
        print("malformed input, someone is trying to hack our web app, Sir!")
        return redirect(reverse('home'))

    # temporary redirect, need to redirect to their profile page (the place where the remove friend button is)
    return redirect(reverse('profile', kwargs={'username': username}))


# course detail
@login_required
def course_detail(request, cid):
    the_course = get_object_or_404(Course, cid=cid)
    the_user = request.user
    the_profile = Profile.objects.get(user=the_user)

    try:
        the_comments = Comment.objects.filter(course=the_course).order_by('-timestamp')
    except:
        the_comments = None

    try:
        my_comment = Comment.objects.get(course=the_course, user=request.user)
    except:
        my_comment = None

    added = False
    liked = False
    if the_profile.curr.filter(cid=cid).exists():
        added = True
    if the_profile.liked.filter(cid=cid).exists():
        liked = True

    context = {'user': the_user, 'course': the_course, 'added': added,
               'comments': the_comments, 'my_comment': my_comment, 'liked': liked,
               'pending': the_profile.pending}
    return render(request, 'course_detail.html', context)


# user add class
@login_required
def add_class(request, cid):
    the_user = request.user
    the_profile = Profile.objects.get(user=the_user)

    try:
        the_course = Course.objects.get(cid=cid)
    except:
        the_course = None

    if the_course:
        if the_profile.curr.filter(cid=cid).exists():
            print('This course is in your current schedule')
        else:
            the_profile.curr.add(the_course)

    return redirect(reverse('course-detail', kwargs={'cid': cid}))


# user add courses for curr/past/plan
@login_required
def add_courses(request):
    if request.GET:
        return redirect(reverse('home'))

    the_user = request.user
    cid = request.POST['cid']
    semester = request.POST['semester']

    try:
        the_course = Course.objects.get(cid=cid)
    except:
        print('This course id does not exist')
        return redirect(reverse('home'))

    the_profile = Profile.objects.get(user=the_user)
    if semester == 'Current':
        if the_profile.curr.filter(cid=cid).exists():
            print('This course is in your current schedule')
        else:
            the_profile.curr.add(the_course)
    elif semester == 'Past':
        if the_profile.past.filter(cid=cid).exists():
            print('This course is in your past schedule')
        else:
            the_profile.past.add(the_course)
    elif semester == 'Future':
        if the_profile.plan.filter(cid=cid).exists():
            print('This course is in your future schedule')
        else:
            the_profile.plan.add(the_course)
    else:
        print('Error semester, someone is trying to hack our web app, Sir!')

    return redirect(reverse('home'))


# delete course
@login_required
def delete_course(request):
    profile = Profile.objects.get(user=request.user)
    try:
        course = Course.objects.get(cid=request.POST['cid'])
        semester = request.POST['semester']
    except:
        print('malformed input!')
        return redirect(reverse('home'))

    if semester == 'curr':
        try:
            profile.curr.remove(course)
        except:
            print('This course is not in curr!')
            return redirect(reverse('home'))
    elif semester == 'past':
        try:
            profile.past.remove(course)
        except:
            print('This course is not in past!')
            return redirect(reverse('home'))
    elif semester == 'plan':
        try:
            profile.plan.remove(course)
        except:
            print('This course is not in plan!')
            return redirect(reverse('home'))

    goto = request.POST['page']     #either gonna be 'profile' or 'home'
    if goto == 'profile':
        return redirect(reverse(goto, kwargs={'username': request.user}))
    elif goto == 'course-detail':
        return redirect(reverse(goto, kwargs={'cid': request.POST['cid']}))
    else:
        return redirect(reverse('home'))


# search course
@login_required
def search(request):
    try:
        cid = request.POST['cid']
    except:
        return redirect(reverse('home'))

    num = Course.objects.filter(cid = cid).count()
    if num == 0:
        context = {'error': cid}
        return render(request, 'not_found.html', context)
    else:
        return redirect(reverse('course-detail', kwargs={'cid': cid}))


#search course with GET method
@login_required
def search2(request):
    try:
        cid = request.GET['cid']
    except:
        return redirect(reverse('home'))

    num = Course.objects.filter(cid = cid).count()
    if num == 0:
        context = {'error': cid}
        return render(request, 'not_found.html', context)
    else:
        return redirect(reverse('course-detail', kwargs={'cid': cid}))


# browse
@login_required
def browse(request):
    context = {}
    context['pending'] = Profile.objects.get(user=request.user).pending

    dept_list = []
    dept_list.append('All')
    for course in Course.objects.all():
        if course.department not in dept_list:
            dept_list.append(course.department)

    context['dept_list'] = dept_list

    # top 10
    rankby = ['liked', 'rating', 'workload(ascending)', 'workload(descending)']
    context['rankby'] = rankby

    if not request.GET:
        return render(request, 'browse.html', context)

    if 'department' in request.GET:
        try:
            selected_dept = request.GET['department']
        except:
            return redirect(reverse('home'))

        context['dept'] = selected_dept
        if selected_dept == 'All':
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(department=selected_dept)
    else:
        courses = None

    context['courses'] = courses

    if 'orderby' in request.GET:
        try:
            the_dept = request.GET['dept']
        except:
            the_dept = None

        if not the_dept or the_dept == 'All':
            the_courses = Course.objects.all()
        else:
            the_courses = Course.objects.filter(department=the_dept)

        if request.GET['orderby'] == 'liked':
            top5course = the_courses.order_by('-likes')[:5]
        elif request.GET['orderby'] == 'rating':
            top5course = the_courses.order_by('-rating')[:5]
        elif request.GET['orderby'] == 'workload(ascending)':
            top5course = the_courses.order_by('hours')[:5]
        elif request.GET['orderby'] == 'workload(descending)':
            top5course = the_courses.order_by('-hours')[:5]
        else:
            top5course = None
    else:
        top5course = None

    context['top5course'] = top5course

    return render(request, 'browse.html', context)

def search_users(request):
    try:
        key = request.GET['key']
        tag = request.GET['tag']
    except:
        print("malformed input, someone is trying to hack our web app, Sir!")
        return redirect(reverse('home'))

    context = {}
    user_list = []
    msg =""
    if tag == 'username':
        try:
            the_user = User.objects.get(username=key);
            user_list.append(the_user)
        except:
            msg = "Sorry, no such user"
    elif tag == 'firstname':
        user_list = User.objects.filter(first_name=key);
    elif tag == 'lastname':
        user_list = User.objects.filter(last_name=key);
    elif tag == 'email':
        user_list = User.objects.filter(email=key);
    else:
        msg = "Sorry, no such user"

    if not user_list:
        msg = "Sorry, no such user"

    context['user_list'] = user_list
    context['msg'] = msg
    return render(request, 'browse.html', context)

# get course data
# for course_detail.html trend plot
@login_required
def get_course_data(request):
    cid = request.GET['cid']
    data_type = request.GET['type']


    if data_type == 'difficulty':
        course = Course.objects.get(cid=cid)
        comments = Comment.objects.filter(course=course)

        easy = medium = hard = 0
        for comment in comments:
            difficulty = comment.difficulty
            if difficulty == '1':
                easy = easy + 1
            elif difficulty == '2':
                medium = medium + 1
            elif difficulty == '3':
                hard = hard + 1
            else: # just in case it's blank
                continue

        response = {'Easy': easy, 'Medium': medium, 'Hard': hard}
        return JsonResponse(response)

    else:
        response = collections.OrderedDict()
        visited = {}
        for record in History.objects.filter(cid=cid):
            if data_type == 'rating':
                data = record.oc
            else:   # data_type == 'hours'
                data = record.hours

            key = record.year + ' ' + record.semester
            if not visited.has_key(key):
                visited[key] = (data, 1)
            else:
                (prev_average, prev_count) = visited[key]
                new_count = prev_count + 1
                new_average = ((prev_average * prev_count) + data) / new_count
                visited[key] = (new_average, new_count)
        ordered_dict = collections.OrderedDict(sorted(visited.items()))

        for item in ordered_dict.items():
            (semester, data_tuple) = item
            (keep, trash) = data_tuple
            semester = "'" + semester[2:]
            response[semester] = float(keep)

        return JsonResponse(response)


# For faculty/super user, the can upload history data and course data
@login_required
def upload(request):

    the_user = request.user
    form_file = FileForm(request.POST, request.FILES, instance=the_user)

    if form_file.is_valid():
        form_file.content_type = form_file.cleaned_data['csvfile'].content_type
        form_file.save()
    else:
        print('bad file')
        return redirect(reverse('home'))

    iscourse = request.POST.get('datatype')
    content = csv.reader(request.FILES.get('csvfile'))

    new_courses = []
    try:
        # if it is course data
        if iscourse == 'True':
            for line in content:
                try:
                    the_course = Course.objects.get(cid=line[0])
                    the_course.name = line[1]
                    the_course.department = line[2]
                    the_course.description = line[3]
                    the_course.start = line[4]
                    the_course.end = line[5]
                    the_course.days = line[6]
                except:
                    the_course = Course(cid=line[0],
                                        name=line[1],
                                        department=line[2],
                                        description=line[3],
                                        start=line[4],
                                        end=line[5],
                                        days=line[6])
                the_course.save()
                new_courses.append(the_course)
        # if it is history data
        else:
            for line in content:
                new_history = History(semester=line[0],
                                      year=line[1],
                                      instructor=line[2],
                                      department=line[3],
                                      cid=line[4],
                                      coursename=line[5],
                                      section=line[6],
                                      ctype=line[7],
                                      response=line[8],
                                      enrollment=line[9],
                                      resprate=line[10],
                                      hours=line[11],
                                      iisl=line[12],
                                      ecr=line[13],
                                      clg=line[14],
                                      ipfs=line[15],
                                      ios=line[16],
                                      esm=line[17],
                                      srs=line[18],
                                      os=line[19],
                                      oc=line[20])
                new_history.save()
    except:
        print('upload data error!')

    #compute and store average hours/week and average overall rating
    def computeAvg(course, hset):
        count = 0
        total_hours = 0
        total_rating = 0
        for history in hset:
            count += 1
            total_hours = total_hours + history.hours
            total_rating = total_rating + history.oc
        hours = total_hours / count
        rating = total_rating / count
        course.hours = hours
        course.rating = rating
        course.save()

    # if both are present, populate 'hours' and 'ratings' field of models.Course
    if new_courses:
        for course in new_courses:
            i = 2016
            while True:
                fall_set = History.objects.filter(cid=course.cid, year=str(i), semester='Fall')
                spring_set = History.objects.filter(cid=course.cid, year=str(i), semester='Spring')
                if fall_set:
                    computeAvg(course, fall_set)
                    break
                elif spring_set:
                    computeAvg(course, spring_set)
                    break
                elif i < 2000:  # no previous data should be available on CMU SIO
                    break       # used to break out of inf loop
                else:
                    i -= 1

    return redirect(reverse('home'))


def add_comment(request, cid):
    the_course = get_object_or_404(Course, cid=cid)
    # the_course = Course.objects.get(cid=cid)
    form = CommentForm(request.POST)
    if not form.is_valid():
        raise Http404
    else:
        try:
            the_comment = Comment.objects.get(course=the_course, user=request.user)
            the_comment.delete()
        except:
            None
        the_comment = Comment(comment=request.POST['comment'],
                          skills=request.POST['skills'],
                          difficulty=request.POST['difficulty'],
                          user=request.user,
                          course=the_course)
        the_comment.save()
    return redirect(reverse('course-detail', kwargs={'cid': cid}))


def like_class(request, cid):
    the_user = request.user
    the_profile = Profile.objects.get(user=the_user)

    try:
        the_course = Course.objects.get(cid=cid)
    except:
        print('This course id does not exist')
        return redirect(reverse('home'))

    if the_course:
        if the_profile.liked.filter(cid=cid).exists():
            print('You have liked this course!')
        else:
            the_profile.liked.add(the_course)
            the_course.likes += 1
            the_course.save()

    return redirect(reverse('course-detail', kwargs={'cid': cid}))
