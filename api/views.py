from django.contrib.auth import login, get_user_model, models
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from knox.models import AuthToken

from knox.auth import TokenAuthentication
from .serializer.users import *
from .serializer.password import *
import pandas as pd
import numpy as np
from keras.models import load_model
model = load_model('Model.h5')

######################      Registration        ###################### 
class RegisterPatientAPI(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterPatientSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)


        if serializer.is_valid():
            user = serializer.save()

            return Response({
                    "status": "CREATED",
                    "code": status.HTTP_201_CREATED,
                    "message": "Patient account created",
                    "data": PatientSerializer(user, context=self.get_serializer_context()).data,
                    "token": AuthToken.objects.create(user)[1]
                }, status=status.HTTP_201_CREATED)
              
        return Response({
                "status": "BAD_REQUEST",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": f"{serializer.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterDoctorAPI(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterDoctorSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "status": "CREATED",
                "code": status.HTTP_201_CREATED,
                "message": "Doctor account created",
                "data": DoctorSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            }, status=status.HTTP_201_CREATED)

        return Response({
                "status": "BAD_REQUEST",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": f"{serializer.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)

class RegisterAdminAPI(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterAdminSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "status": "CREATED",
                "code": status.HTTP_201_CREATED,
                "message": "Admin account created",
                "data": AdminSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            }, status=status.HTTP_201_CREATED)
        return Response({
                "status": "BAD_REQUEST",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": f"{serializer.errors}"
            }, status=status.HTTP_400_BAD_REQUEST)

######################      Login        ################################ 
class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)


##################      Profile         ##################################

class Profile(UpdateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileUpdateSerializer

    def get(self, request, format=None):
        return Response({
            "status": "SUCCESS",
            "code": status.HTTP_200_OK,
            "message": "Profile retrieved successfully",
            "data": ProfileSerializer(request.user, context=self.get_serializer_context()).data
        }, status=status.HTTP_200_OK)

    
    def put(self, request, format=None):
        # Partial update of the data
        serializer = self.serializer_class(request.user, data=request.data, partial=True)

        if not any(key in request.data for key in ("email", "phone", "address")):
            return Response ({})
       
        if serializer.is_valid():
            self.perform_update(serializer)

            return Response({
                "status": "SUCCESS",
                "code": status.HTTP_200_OK,
                "message": "Profile updated successfully",
                "data": ProfileSerializer(request.user, context=self.get_serializer_context()).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "BAD_REQUEST",
            "code": status.HTTP_400_BAD_REQUEST,
            "message": f"{serializer.errors}",
            "data": []
        }, status = status.HTTP_400_BAD_REQUEST )


##################      Change Password        ##################################
class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = get_user_model()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {
                    "status": "BAD_REQUEST",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message" :{ 
                        "old_password": "Wrong password."
                        }
                    }, 
                    status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                "status": "SUCCESS",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": []
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


############################# Delete Account ##################################
class DeleteAccountView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user=request.user
        user.delete()

        return Response({
            "status": "SUCCESS",
            "code": status.HTTP_200_OK,
            "message": f"{request.user} has been deleted",
            "data": []
            })


class DeleteTargetAccountView(GenericAPIView):
    """
    Special Case for admin, have a permissions to delete patient/doctor/ another admin account
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user=request.user

        if 'id' not in request.data:
            return Response({
                    "status": "BAD_REQUEST",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "key 'id' not defined",
                    "data": []
            }, status = status.HTTP_400_BAD_REQUEST)


        if user.is_staff:
            target_user = get_user_model().objects.filter(id=request.data['id'])

            if target_user.exists():
                target_user.delete()

                return Response({
                    "status": "SUCCESS",
                    "code": status.HTTP_200_OK,
                    "message": f"{request.data['id']} has been deleted",
                    "data": []
                    })
            else:
                return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"User with Id {request.data['id']} doesnt exist",
                    "data": []
                    }, status = status.HTTP_404_NOT_FOUND)


        return Response({
                "status": "Failed",
                "code": status.HTTP_403_FORBIDDEN,
                "message": f"You dont have permission to access this API",
                "data": []
                }, status=status.HTTP_403_FORBIDDEN)


class AccDoctorView(UpdateAPIView):
    """
    Special Case for admin, have a permissions to verify / acc doctor
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user

        if 'id_doctor' not in request.data:
            return Response({
                    "status": "BAD_REQUEST",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "missing key 'id_doctor'",
                    "data": []
            }, status = status.HTTP_400_BAD_REQUEST)
            
        if 'acc_doctor' not in request.data:
            return Response({
                    "status": "BAD_REQUEST",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "missing key 'acc_doctor'",
                    "data": []
            }, status = status.HTTP_400_BAD_REQUEST)
        
        id_doctor = request.data['id_doctor']
        acc_value = request.data['acc_doctor']

        if user.is_staff:
            target_doctor = get_user_model().objects.filter(id=id_doctor)

            if target_doctor.exists():
                if target_doctor.values('is_doctor')[0]['is_doctor'] != True:
                    return Response({
                            "status": "Failed",
                            "code": status.HTTP_403_FORBIDDEN,
                            "message": f"User {id_doctor} is not a doctor.",
                            "data": []
                            }, status=status.HTTP_403_FORBIDDEN)

                else:
                    target_doctor.update(acc_doctor=acc_value)

                    return Response({
                        "status": "SUCCESS",
                        "code": status.HTTP_200_OK,
                        "message": f" Successfully assign acc {acc_value} to Doctor with Id {id_doctor} ",
                        "data": []
                    }, status=status.HTTP_200_OK)
                
            
            return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"Doctor with Id {id_doctor} doesnt exist",
                    "data": []
                    }, status = status.HTTP_404_NOT_FOUND)


class AppointmentView(GenericAPIView):
    """
    Get and Create appointment
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        if request.user.is_patient:
            queryset = Appointment.get_appointment_patient(request.user.id)

            if queryset.exists():
                return Response({
                    "status": "SUCCESS",
                    "code": status.HTTP_200_OK,
                    "message": f"Successfully retrieve appointment data",
                    "data": [queryset.values()]
                    })
            else:
                return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"Current user doesnt have appointment",
                    "data": []
                    }, status = status.HTTP_404_NOT_FOUND)

        
        elif request.user.is_doctor:
            queryset = Appointment.get_appointment_doctor(request.user.id)

            if queryset.exists():
                return Response({
                    "status": "SUCCESS",
                    "code": status.HTTP_200_OK,
                    "message": f"Successfully retrieve appointment data",
                    "data": [queryset.values()]
                    })
            else:
                return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"Current user doesnt have appointment",
                    "data": []
                    }, status = status.HTTP_404_NOT_FOUND)

            

    def post(self, request, format=None):

        if request.user.is_patient:
            id_patient = request.user.id
            id_doctor = request.data['id_doctor']
    

            request.data['id_patient'] = id_patient
            doctor = get_user_model().objects.filter(id=id_doctor)
            print(doctor.exists())
            
            if doctor.exists():
                if doctor.values('acc_doctor')[0]['acc_doctor'] != True:
                    return Response({
                            "status": "Failed",
                            "code": status.HTTP_403_FORBIDDEN,
                            "message": f"The Doctor Id {id_doctor} is unverified.",
                            "data": []
                            }, status=status.HTTP_403_FORBIDDEN)

                else:

                    serializer = AppointmentSerializer(data=request.data)

                    if serializer.is_valid():
                        appointment = serializer.save()

                        return Response({
                                "status": "SUCCESS",
                                "code": status.HTTP_201_CREATED,
                                "message": "Appointment created",
                                "data": AppointmentDetailsSerializer(appointment, context=self.get_serializer_context()).data
                            }, status=status.HTTP_201_CREATED)
            
                
                    return Response({
                            "status": "BAD_REQUEST",
                            "code": status.HTTP_400_BAD_REQUEST,
                            "message": f"{serializer.errors}"
                        }, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"Doctor with Id {id_doctor} doesnt exist",
                    "data": []
                    }, status = status.HTTP_404_NOT_FOUND)


class Chatbot(GenericAPIView):
    "Get and set AI"
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):

        if request.user.is_patient:
            id_patient = request.user.id
            request.data['id_patient'] = id_patient
            item1 = request.data['input1']
            item2 = request.data['input2']
            item3 = request.data['input3']
            item4 = request.data['input4']
            item5 = request.data['input5']
            item6 = request.data['input6']
            item7 = request.data['input7']
            item8 = request.data['input8']
            item9 = request.data['input9']
            item10 = request.data['input10']

            item = {
                'Tidak mau makan': [item1],
                'Luka/lepuh pada daerah mulut' : [item2],
                'luka/lepuh pada daerah keempat kakinya' : [item3],
                'Suhu Sapi' : [item4],
                'Lama Demam' : [item5],
                'Gemetaran' : [item6],
                'hewan lebih senang berbaring' : [item7],
                'Mengalami salah satu gejala Menggeretakkan gigi/ menggosokkan mulut/ leleran mulut' : [item8],
                'terjadi penurunan produksi susu' : [item9],
                'nafas cepat' : [item10],
                }
            data = pd.DataFrame(item)
            y_pred = model.predict(data)
            y_pred = np.argmax(y_pred, axis=-1)
        return Response({
                "status": "SUCCESS",
                "code": status.HTTP_200_OK,
                "message": f" Successfully diagnosa ",
                "data": y_pred
            }, status=status.HTTP_200_OK)

class ChangeStatusAppointmentView(UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        id_appointment = request.data['id_appointment']

        if not user.is_doctor :
            return Response({
                            "status": "FORBIDDEN",
                            "code": status.HTTP_403_FORBIDDEN,
                            "message": f"You dont have permissions to use this feature.",
                            "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        
        if not user.acc_doctor:
            return Response({
                            "status": "FORBIDDEN",
                            "code": status.HTTP_403_FORBIDDEN,
                            "message": f"You need to be verified to access this feature. Please Contact the admin",
                            "data": []
            }, status=status.HTTP_403_FORBIDDEN)

        check_appointment = Appointment.objects.filter(id=id_appointment, id_doctor=user.id)

        if not check_appointment.exists():
            return Response({
                    "status": "NOT_FOUND",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": f"Appointment with Id {id_appointment} doesnt exist",
                    "data": []
            }, status = status.HTTP_404_NOT_FOUND)
        else:
            check_appointment.update(status=True)

            return Response({
                "status": "SUCCESS",
                "code": status.HTTP_200_OK,
                "message": f" Successfully assign Appointment with Id {id_appointment} ",
                "data": []
            }, status=status.HTTP_200_OK)



