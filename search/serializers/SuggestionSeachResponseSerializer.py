from rest_framework import serializers


class SuggestionSearchResponseSerializer(serializers.Serializer):
    suggestions = serializers.ListField(child=serializers.CharField())
