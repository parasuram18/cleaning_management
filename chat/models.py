from django.db import models

# Create your models here.

class rooms(models.Model):
    room_name = models.CharField(max_length=20)
    sender_id = models.CharField(max_length=10)
    receiver_id = models.CharField(max_length=10)

    class Meta:
        unique_together = ['sender_id', 'receiver_id']
    
    def __str__(self):
        return self.room_name

class messages(models.Model):
    room = models.ForeignKey(rooms, on_delete=models.DO_NOTHING)
    message = models.TextField()
    sender_id = models.CharField(max_length=10)
    reciever_id = models.CharField(max_length=10)
    time = models.DateTimeField(auto_now_add=True)