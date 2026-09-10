# pyrefly: ignore [missing-import]
from django.contrib import admin
from .models import ChildProfile, NavigationLog, AlertWord

admin.site.register(ChildProfile)
admin.site.register(NavigationLog)
admin.site.register(AlertWord)