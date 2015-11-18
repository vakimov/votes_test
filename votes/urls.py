"""votes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required as _lr

from .views import (
    SignUpView, VotingListView, VotingAddView, VotingResultsView,
    VotingView, UsersVotingListView
)


urlpatterns = [
    url('^$', VotingListView.as_view(),
        name='vote_home'),
    url('^login/$',
        auth_views.login, {'template_name': 'votes/login.html'},
        name='votes_login'),
    url('^logout/$',
        auth_views.logout, {'template_name': 'votes/logout.html'},
        name='votes_logout'),
    url('^signup/$',
        SignUpView.as_view(),
        name='votes_signup'),
    url('^votings/$',
        _lr(UsersVotingListView.as_view()),
        name='votes_voting_list'),
    url('^votings/add/$',
        _lr(VotingAddView.as_view()),
        name='votes_voting_add'),
    url('^vote-for/(?P<slug>[-\w]+)/$',
        VotingView.as_view(),
        name='votes_voting'),
    url('^vote-for/(?P<slug>[-\w]+)/results/$',
        VotingResultsView.as_view(),
        name='votes_voting_results'),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
