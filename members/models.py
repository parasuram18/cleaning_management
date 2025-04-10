from django.db import models
from django.contrib.auth.models import AbstractUser

class IuMaster(models.Model):
    company_name = models.CharField(max_length=50, blank=True, null=True)
    domain_name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'iu_master'

class IuMasterProfile(models.Model):
    iu_master = models.ForeignKey(IuMaster, related_name='Iudetails', on_delete=models.CASCADE)
    address = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15)
    gst_number = models.CharField(max_length=50)
    registration_date = models.DateField(blank=True, null=True)
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
    phonenumber = models.CharField(max_length=20, blank=True, null=True)
    mail_id = models.EmailField(max_length=50, unique=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)

    class Meta:
        db_table = 'custom_user'

class UserPersonalProfile(models.Model):
    user = models.OneToOneField(CustomUser, related_name='user', on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='media/profile/')
    is_married = models.BooleanField(default=None, null=True, blank=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'user_personal_profile'

class RoleMapping(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.ForeignKey(RoleMaster, on_delete=models.CASCADE)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)

    class Meta:
        db_table = 'role_mapping'

class BlockMaster(models.Model):
    block_name = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'block_master'

class FloorMaster(models.Model):
    floor_number = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    block = models.ForeignKey(BlockMaster, on_delete=models.CASCADE, related_name='block', null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'floor_master'

class RoomMaster(models.Model):
    room_number = models.CharField(max_length=10, null=True, blank=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    floor = models.ForeignKey(FloorMaster, on_delete=models.CASCADE, related_name='floor', null=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)
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
    room = models.ForeignKey(RoomMaster,  on_delete=models.CASCADE, related_name='room', null=True, blank=True)
    iu_id = models.ForeignKey(IuMaster, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    modified_by = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'work_schedules'

 