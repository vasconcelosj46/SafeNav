# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import NavigationLog

class NavigationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationLog
        fields = ['url', 'title', 'timestamp', 'category']