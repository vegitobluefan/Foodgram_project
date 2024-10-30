import base64

from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.response import Response


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def check_request(request, obj, model):
    return (
        request and request.user.is_authenticated
        and model.objects.filter(user=request.user, recipe=obj).exists())


def post_method(request, instance, serializer_class):
    serializer = serializer_class(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_method(request, instance, model):
    if not model.objects.filter(
        user=request.user, recipe=instance
    ).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    model.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
