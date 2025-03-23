from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('staff_dash/',views.staff_dashboard,name='staff_dash'),

    path('logout/', views.user_logout, name='logout'),
    path('add_voter/', views.add_voter, name='add_voter'),
    path('create_session/', views.create_session, name='create_session'),
    path('add_candidate/', views.add_candidate, name='add_candidate'),
    path('add_constituency/', views.add_constituency, name='add_constituency'),
    path('vote/<int:session_id>/', views.voting_interface, name='voting_interface'),
    path('submit-vote/<int:candidate_id>/', views.submit_vote, name='submit_vote'),


    path('scan/<int:session_id>/', views.scan_biometric, name='scan_biometric'),
    path('validate_fingerprint/<int:voter_id>/', views.validate_fingerprint, name='validate_fingerprint'),
    path('validate_retina/<int:voter_id>/', views.validate_retina, name='validate_retina'),



    path('session/<int:session_id>/', views.session_details, name='session_details'),

]
