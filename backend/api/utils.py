from rest_framework import status
from rest_framework.response import Response


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
