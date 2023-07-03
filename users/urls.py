from django.urls import path,include
from . import views

urlpatterns = [
    path('all/', views.ProfileListView.as_view(), name='profile-list-view'),
    path('follow/', views.follow_unfollow_profile, name='follow-unfollow-view'),
    path('relative/', views.relative_unrelative_profile, name='relative-unrelative-view'),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail-view'),
    path('public-profile/<str:username>/', views.public_profile, name='public-profile'),
    
]