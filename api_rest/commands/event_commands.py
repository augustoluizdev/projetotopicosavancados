from api_rest.serializers import EventSerializer



def create_event_command(data):

    serializer = EventSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors



def update_event_command(event, data):

    serializer = EventSerializer(event, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors



def delete_event_command(event):

    event.delete()
