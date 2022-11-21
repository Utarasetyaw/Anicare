from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    acc_doctor = models.BooleanField(default=False)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)



class Appointment(models.Model):
    """Contains info about appointment"""

    class Meta:
        unique_together = ('id_doctor', 'date', 'timeslot')

    TIMESLOT_LIST = (
        (0, '09:00 – 09:30'),
        (1, '10:00 – 10:30'),
        (2, '11:00 – 11:30'),
        (3, '12:00 – 12:30'),
        (4, '13:00 – 13:30'),
        (5, '14:00 – 14:30'),
        (6, '15:00 – 15:30'),
        (7, '16:00 – 16:30'),
        (8, '17:00 – 17:30'),
    )

    id = models.AutoField(primary_key=True),
    id_doctor = models.IntegerField(null=False)
    id_patient = models.ForeignKey(CustomUser,on_delete = models.CASCADE)
    date = models.DateField(help_text="YYYY-MM-DD")
    timeslot = models.IntegerField(choices=TIMESLOT_LIST)
    status  = models.BooleanField(default=False)

    @property
    def time(self):
        return self.TIMESLOT_LIST[self.timeslot][1]
    
    @classmethod
    def get_appointment_patient(cls, id):
        return cls.objects.filter(id_patient=id)

    @classmethod
    def get_appointment_doctor(cls, id):
        return cls.objects.filter(id_doctor=id)


