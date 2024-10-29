from .serializers import AvatarSerializer


def change_avatar(self, data):
    instance = self.get_instance()
    serializer = AvatarSerializer(instance, data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer
