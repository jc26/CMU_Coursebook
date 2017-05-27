from django.conf.urls import url
from django.contrib.auth import views as auth_views
from cmucoursebook import views
from forms import CustomLoginForm

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^profile/(?P<username>[\w.@+-]+)$', views.profile, name='profile'),
    url(r'^edit-profile$', views.edit_profile, name="edit-profile"),
    url(r'^edit-image', views.edit_image, name="edit-image"),
    url(r'^get-image/(?P<username>[\w.@+-]+)$', views.get_image, name="get-image"),
    #
    url(r'^browse$',views.browse, name='browse'),
    url(r'^search$',views.search, name='search'),
    url(r'^search2$',views.search2, name='search2'),
    url(r'^course-detail/(?P<cid>(\d+))$',views.course_detail, name='course-detail'),
    url(r'^course-detail/get-course-data$', views.get_course_data, name="get-course-data"),
    url(r'^search-users$',views.search_users, name='search-users'),
    #
    url(r'^add-class/(?P<cid>(\d+))$',views.add_class, name='add-class'),
    url(r'^like-class/(?P<cid>(\d+))$',views.like_class, name='like-class'),
    url(r'^add-courses/',views.add_courses, name='add-courses'),
    url(r'^delete-course/',views.delete_course, name='delete-course'),
    #
    url(r'^friends$',views.friends, name='friends'),
    url(r'^request-friendship/(?P<username>[\w.@+-]+)$',views.request_friendship, name='request-friendship'),
    url(r'^confirm-friendship/(?P<username>[\w.@+-]+)$',views.confirm_friendship, name='confirm-friendship'),
    url(r'^deny-friendship/(?P<username>[\w.@+-]+)$',views.deny_friendship, name='deny-friendship'),
    url(r'^remove-friend/(?P<username>[\w.@+-]+)$',views.remove_friend, name='remove-friend'),
    #
    url(r'^login$', auth_views.login, {'template_name':'login.html', 'authentication_form': CustomLoginForm}, name='login'),
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$',
        views.confirm_registration, name='confirm'),
    url(r'^upload',views.upload, name='upload'),
    url(r'^add-comment/(\d+)$',views.add_comment, name='add-comment'),
]
