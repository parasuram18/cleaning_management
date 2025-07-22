from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField


class IuMaster(models.Model):
    company_name = models.CharField(max_length=50, blank=True, null=True)
    domain_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'iu_master'

class IuMasterProfile(models.Model):
    iu_master = models.OneToOneField(IuMaster, related_name='Iudetails', on_delete=models.CASCADE)
    address = JSONField(default=dict, blank=True)
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=50)
    registration_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'iu_master_profile'

class RoleMaster(models.Model):
    role = models.CharField(max_length=15, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    
    class Meta:
        db_table = 'role_master'

class CustomUser(AbstractUser):
    username = None
    phonenumber = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = []
    class Meta:
        db_table = 'custom_user'
    def __str__(self):
        return str(self.phonenumber)
    def get_user_name(self):
        return f'{self.first_name if self.first_name else ""} {self.last_name if self.last_name else ""}'
class UserPersonalProfile(models.Model):
    user = models.OneToOneField(CustomUser, related_name='user_personal', on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = JSONField(default=dict, null=True, blank=True)
    is_married = models.BooleanField(default=None, null=True, blank=True)
    address = JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'user_personal_profile'


class RoleMapping(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.ForeignKey(RoleMaster, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'role_mapping'

class BlockMaster(models.Model):
    block_name = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'block_master'

class FloorMaster(models.Model):
    floor_number = models.CharField(max_length=20, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    block = models.ForeignKey(BlockMaster, on_delete=models.CASCADE, related_name='floor', null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'floor_master'

class RoomMaster(models.Model):
    room_number = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    floor = models.ForeignKey(FloorMaster, on_delete=models.CASCADE, related_name='room', null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'room_master'

class WorkSchedules(models.Model):
    ward_member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    room = models.ForeignKey(RoomMaster,  on_delete=models.CASCADE, related_name='schedules', null=True, blank=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'work_schedules'

from .models import WorkSchedules
from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save ,sender=WorkSchedules)
def send_to_live_dashboard(sender, instance, created, **kwargs):
    if created:
        channel = get_channel_layer()
        roomname = 'LiveDataDashboard'
        payload = {
            "id":instance.id,
            "user": instance.ward_member.get_user_name().title(),
            "block": instance.room.floor.block.block_name,
            "floor": instance.room.floor.floor_number,
            "room": instance.room.room_number,
            "date": str(instance.date),
            "session": instance.session
        }
        async_to_sync(channel.group_send)(
            roomname,
            {
                "type": "send_message",
                "task_data": [payload,],
            }
        )
        print("done...")
    else:
        print(f"task-{instance.id} updated" )
    if instance.is_active==False:
        print("---Task removed---")
