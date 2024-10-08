import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """Валидация никнейма пользователя."""

    if username == 'me':
        raise ValidationError('Выберите другой username')
    invalid_matches = set(re.findall(r'[^\w.@+-]', username))

    if invalid_matches:
        raise ValidationError(
            f'Недопустимые символы в никнейме: {"".join(invalid_matches)}'
        )
    return username
