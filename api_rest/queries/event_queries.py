from django.core.cache import cache

from api_rest.models import Event
from api_rest.serializers import EventSerializer


EVENT_LIST_CACHE_KEY = 'events:list'
EVENT_ITEM_CACHE_KEY = 'events:item:{id}'


def get_event_item_cache_key(event_id):
    return EVENT_ITEM_CACHE_KEY.format(id=event_id)


def get_all_events_query():
    cached_events = cache.get(EVENT_LIST_CACHE_KEY)
    if cached_events is not None:
        return cached_events

    events = Event.objects.all().order_by('date')
    event_data = EventSerializer(events, many=True).data
    cache.set(EVENT_LIST_CACHE_KEY, event_data)
    return event_data


def get_event_by_id_query(event_id):
    cache_key = get_event_item_cache_key(event_id)
    cached_event = cache.get(cache_key)
    if cached_event is not None:
        return cached_event

    event = Event.objects.get(pk=event_id)
    event_data = EventSerializer(event).data
    cache.set(cache_key, event_data)
    return event_data


def invalidate_event_list_cache():
    cache.delete(EVENT_LIST_CACHE_KEY)


def invalidate_event_item_cache(event_id):
    cache.delete(get_event_item_cache_key(event_id))
