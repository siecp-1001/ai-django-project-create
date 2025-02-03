from rest_framework import serializers

class ProjectSpecificationSerializer(serializers.Serializer):
    project_name = serializers.CharField(max_length=100)
    app_name = serializers.CharField(max_length=100)
    models_spec = serializers.JSONField()
    endpoints_spec = serializers.JSONField()