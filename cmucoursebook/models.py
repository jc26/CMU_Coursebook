from __future__ import unicode_literals
from django.db import models

# User class for built-in authentication module
from django.contrib.auth.models import User


class Course(models.Model):
    cid = models.CharField(max_length=5, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    start = models.CharField(max_length=5)  #start time
    end = models.CharField(max_length=5)    #end time

    # days is in COLON DELIMITED format with Monday = MN Tuesday = TU Wednesday = WD Thursday = TH Friday = FR
    # i.e. MN:WD:FR means Mondays, Wednesdays, and Fridays
    days = models.CharField(max_length=15)

    # these two fields are averaged over the most recent semester, either Fall or Spring
    # Summer semester is ignored
    # year 2017 is ignored
    hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    likes = models.IntegerField(default=0)


class Profile(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('FR', 'Freshman'),
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('GR', 'Graduate'),
    )
    user = models.ForeignKey(User, related_name="linked_user")
    major = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=2, choices=YEAR_IN_SCHOOL_CHOICES, default='FR')
    age = models.IntegerField(null=True, blank=True)
    from_city = models.CharField(max_length=50, null=True, blank=True)
    from_country = models.CharField(max_length=50, null=True, blank=True)
    bio = models.CharField(max_length=430, null=True, blank=True)
    # img = models.FileField(upload_to='cmucoursebook/static/image', null=True, blank=False)
    img = models.FileField(upload_to='cmucoursebook/static', null=True, blank=False)
    friends = models.ManyToManyField(User, related_name="friends")
    pending = models.IntegerField(default=0)
    pending_friends = models.ManyToManyField(User, related_name="pending_friends")
    curr = models.ManyToManyField(Course, related_name="current_courses")
    plan = models.ManyToManyField(Course, related_name="planned_courses")
    past = models.ManyToManyField(Course, related_name="past_courses")
    liked = models.ManyToManyField(Course, related_name="liked_courses")


class History(models.Model):
    semester = models.CharField(max_length=6)   #Fall, Spring, Summer
    year = models.CharField(max_length=4)
    instructor = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    cid = models.CharField(max_length=5)
    coursename = models.CharField(max_length=50)
    section = models.CharField(max_length=3)
    ctype = models.CharField(max_length=5)
    response = models.CharField(max_length=3)
    enrollment = models.CharField(max_length=3)
    resprate = models.DecimalField(max_digits=3, decimal_places=2)  # Response rate
    hours = models.DecimalField(max_digits=4, decimal_places=2)		#Time spent per week
    iisl = models.DecimalField(max_digits=3, decimal_places=2)		#Interest in student learning
    ecr = models.DecimalField(max_digits=3, decimal_places=2)		#Explain course requirements
    clg = models.DecimalField(max_digits=3, decimal_places=2)		#Clear learning goals
    ipfs = models.DecimalField(max_digits=3, decimal_places=2)		#Instructor provides Feedback to students
    ios = models.DecimalField(max_digits=3, decimal_places=2)		#Importance of subject
    esm = models.DecimalField(max_digits=3, decimal_places=2)		#Explains subject matter
    srs = models.DecimalField(max_digits=3, decimal_places=2)		#Show respect for students
    os = models.DecimalField(max_digits=3, decimal_places=2)		#Overall teaching
    oc = models.DecimalField(max_digits=3, decimal_places=2)		#Overall course


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comment_author")
    course = models.ForeignKey(Course, related_name="comment_course")
    difficulty = models.CharField(max_length=1)                     # 1 easy 2 medium 3 hard
    comment = models.CharField(max_length=800)
    skills = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)


class Skill(models.Model):
    user = models.ForeignKey(User, related_name="skill_author")
    course = models.ForeignKey(Course, related_name="skill_course")
    tag = models.CharField(max_length=20)
    count = models.IntegerField()


class Timeslot(models.Model):
    date = models.CharField(max_length=10, null=True, blank=True)
    start = models.CharField(max_length=5, null=True, blank=True)
    end = models.CharField(max_length=5, null=True, blank=True)


class Schedule(models.Model):
    course = models.ForeignKey(Course, related_name="schedule_course")
    timeslot = models.ManyToManyField(Timeslot, related_name="schedule_time")


class DataFile(models.Model):
    user = models.ForeignKey(User, related_name="updated_user")
    # csvfile = models.FileField(upload_to='cmucoursebook/static/files', null=True, blank=False)
    csvfile = models.FileField(upload_to='cmucoursebook/static', null=True, blank=False)
