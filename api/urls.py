from knox import views as knox_views
from django.urls import path
from .views import *

urlpatterns = [
    path('register/patient/', RegisterPatientAPI.as_view(), name="patient registration"),
    path('register/doctor/', RegisterDoctorAPI.as_view(), name="doctor registration"),
    path('register/admin/', RegisterAdminAPI.as_view(), name="admin registration"),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('profile/', Profile.as_view(), name='test'),
    path('password/', ChangePasswordView.as_view(), name='change password'),
    path('delete/', DeleteAccountView.as_view(), name='delete account'),
    path('admin/delete-user/', DeleteTargetAccountView.as_view(), name='delete specific account'),
    path('admin/acc-doctor/', AccDoctorView.as_view(), name='acc doctor'),
    path('appointment/', AppointmentView.as_view(), name="Get and Create Appointment"),
    path('appointment/status/', ChangeStatusAppointmentView.as_view(), name="Get and Create Appointment"),
    path('chat/', Chatbot.as_view(), name="Get and set AI")
]