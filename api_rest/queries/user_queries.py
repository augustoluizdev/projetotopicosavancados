from api_rest.models import User
from api_rest.serializers import UserSerializer



def get_all_users_query():

    users = User.objects.all()

    return UserSerializer(users, many=True).data



def get_user_by_nick_query(nick):

    user = User.objects.get(pk=nick)

    return UserSerializer(user).data