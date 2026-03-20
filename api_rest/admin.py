from django.contrib import admin

# Aqui registramos os modelos no admin do Django.

from .models import User

admin.site.register(User)

from .models import Event

admin.site.register(Event)