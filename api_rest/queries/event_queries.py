from api_rest.models import Event
from api_rest.serializers import EventSerializer



def get_all_events_query():

    events = Event.objects.all()

    return EventSerializer(events, many=True).data



def get_event_by_id_query(event_id):

    event = Event.objects.get(pk=event_id)

    return EventSerializer(event).data