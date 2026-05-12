from api_rest.models import User
from api_rest.serializers import UserSerializer



def create_user_command(data):

    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors



def update_user_command(user, data):

    serializer = UserSerializer(user, data=data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data

    return serializer.errors



def delete_user_command(user):

    user.delete()