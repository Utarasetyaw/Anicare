from rest_framework.serializers import ModelSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Appointment
import six
from rest_framework.fields import ChoiceField

class PatientSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_patient')

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'address')

class ProfileUpdateSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'phone', 'address')

    def update(self, instance, validated):
        instance.email = validated["email"]
        instance.phone = validated["phone"]
        instance.address = validated["address"]

        instance.save()
        return instance

class DoctorSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_doctor')

class AdminSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff')

class RegisterPatientSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'is_patient')
        extra_kwargs = {'password': {'write_only':True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
                                            username    = validated_data['username'],
                                            email       = validated_data['email'],
                                            password    = validated_data['password'],
                                            first_name  = validated_data['first_name'],
                                            last_name   = validated_data['last_name'],
                                            is_patient  = True
                                            )

        return user

class RegisterDoctorSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'is_doctor')
        extra_kwargs = {'password': {'write_only':True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
                                        username    = validated_data['username'],
                                        email       = validated_data['email'],
                                        password    = validated_data['password'],
                                        first_name  = validated_data['first_name'],
                                        last_name   = validated_data['last_name'],
                                        is_doctor   = True
                                        )

        return user


class AccDoctorSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'acc_doctor')


class RegisterAdminSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'is_staff')
        extra_kwargs = {'password': {'write_only':True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
                                        username    = validated_data['username'],
                                        email       = validated_data['email'],
                                        password    = validated_data['password'],
                                        first_name  = validated_data['first_name'],
                                        last_name   = validated_data['last_name'],
                                        is_staff  = True
                                        )

        return user

class ChoiceDisplayField(ChoiceField):
    def __init__(self, *args, **kwargs):
        super(ChoiceDisplayField, self).__init__(*args, **kwargs)
        self.choice_strings_to_display = {
            six.text_type(key): value for key, value in self.choices.items()
        }

    def to_representation(self, value):
        if value in ('', None):
            return value
        return {
            'value': self.choice_strings_to_values.get(six.text_type(value), value),
            'display': self.choice_strings_to_display.get(six.text_type(value), value),
        }

class ChoiceModelSerializer(ModelSerializer):
    serializer_choice_field = ChoiceDisplayField

class AppointmentDetailsSerializer(ChoiceModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'id_doctor', 'id_patient', 'date', 'timeslot', 'status')

class AppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('id', 'id_doctor', 'id_patient', 'date', 'timeslot', 'status')

    def create(self, validated_data):
        appointment = Appointment.objects.create(
            id_doctor   = validated_data['id_doctor'],
            id_patient  = validated_data['id_patient'],
            date        = validated_data['date'],
            timeslot    = validated_data['timeslot'],
            status      = False
        )

        return appointment






