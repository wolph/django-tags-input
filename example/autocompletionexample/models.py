from __future__ import annotations

from typing import Any, ClassVar

from django.core import exceptions
from django.db import models


class ReprModel(models.Model):
    def __repr__(self) -> str:
        name: str = str(getattr(self, 'name', ''))
        pk: Any = self.pk or -1
        return f'<{self.__class__.__name__}[{pk}]: {name}>'

    def __str__(self) -> str:
        return str(getattr(self, 'name', ''))

    class Meta:
        abstract = True


class Foo(ReprModel):
    objects: ClassVar[models.Manager[Foo]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The foo name'
    )

    def full_clean(self, *args: Any, **kwargs: Any) -> None:
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'name': 'Test Error'})


class Bar(ReprModel):
    objects: ClassVar[models.Manager[Bar]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The bar name'
    )
    foo: models.ForeignKey[Foo, Foo] = models.ForeignKey(
        Foo, help_text='The foo object', on_delete=models.CASCADE
    )


class Spam(ReprModel):
    objects: ClassVar[models.Manager[Spam]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The spam name'
    )
    foo = models.ManyToManyField(Foo)

    def clean(self) -> None:
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'foo': 'Expected testing error'})


class FooExtraSpam(ReprModel):
    objects: ClassVar[models.Manager[FooExtraSpam]] = models.Manager()
    foo: models.ForeignKey[Foo, Foo] = models.ForeignKey(
        Foo, help_text='The foo object', on_delete=models.CASCADE
    )
    extra_spam: models.ForeignKey[ExtraSpam, ExtraSpam] = models.ForeignKey(
        'ExtraSpam',
        help_text='The extra spam object',
        on_delete=models.CASCADE,
    )


class ExtraSpam(ReprModel):
    objects: ClassVar[models.Manager[ExtraSpam]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The extra spam name'
    )
    foo = models.ManyToManyField(Foo, through=FooExtraSpam)


class Egg(ReprModel):
    objects: ClassVar[models.Manager[Egg]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The egg name'
    )
    name2: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='The egg 2nd name'
    )
    foo: models.OneToOneField[Foo, Foo] = models.OneToOneField(
        Foo, help_text='The foo object', on_delete=models.CASCADE
    )
