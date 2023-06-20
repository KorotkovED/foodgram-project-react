from typing import Any
from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as get_


class HexColorField(models.CharField):
    """Класс поля цветов"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault('max_length', 7)
        super().__init__(*args, **kwargs)
        self.validators.append(
            validators.RegexValidator(
                regex=r'#([a-fA-F0-9]{6})',
                message=get_('Введите корректное значение HEX-кода!')
            )
        )
