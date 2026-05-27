import logging

from api_rest.models import User
from api_rest.serializers import UserSerializer


logger = logging.getLogger(__name__)


def create_user_command(data):

    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        logger.info('User created: %s', serializer.data.get('user_nickname'))
        return serializer.data, True

    logger.warning('User creation failed: %s', serializer.errors)
    return serializer.errors, False



def update_user_command(user, data):

    serializer = UserSerializer(user, data=data)

    if serializer.is_valid():
        serializer.save()
        logger.info('User updated: %s', user.user_nickname)
        return serializer.data, True

    logger.warning('User update failed for %s: %s', user.user_nickname, serializer.errors)
    return serializer.errors, False



def delete_user_command(user):

    logger.info('User deleted: %s', user.user_nickname)
    user.delete()
