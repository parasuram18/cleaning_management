from django.shortcuts import render

# Create your views here.
def room_page(request, sender, receiver):
    if request.method == 'GET':
        room_name = f'chat_room_{min(sender, receiver)}_{max(sender, receiver)}'
        context = {
            'room_name':room_name,
            'sender':sender,
            'receiver':receiver
            }
        return render(request, 'chat_room.html',context)