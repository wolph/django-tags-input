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


class SimpleName(ReprModel):
    objects: ClassVar[models.Manager[SimpleName]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='Help text of the name'
    )


class DoubleName(ReprModel):
    objects: ClassVar[models.Manager[DoubleName]] = models.Manager()
    name_a: models.CharField[str, str] = models.CharField(max_length=50)
    name_b: models.CharField[str, str] = models.CharField(max_length=50)

    @property
    def name(self) -> str:
        return f'{self.name_a}/{self.name_b}'

    @name.setter
    def name(self, value: str) -> None:
        pass


class ErrorName(ReprModel):
    objects: ClassVar[models.Manager[ErrorName]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(
        max_length=50, help_text='Impossible to save name'
    )

    def full_clean(self, *args: Any, **kwargs: Any) -> None:
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'name': 'Test Error'})


class ForeignKeyToSimpleName(ReprModel):
    objects: ClassVar[models.Manager[ForeignKeyToSimpleName]] = (
        models.Manager()
    )
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_name: models.ForeignKey[SimpleName, SimpleName] = models.ForeignKey(
        SimpleName, on_delete=models.CASCADE
    )


class ManyToManyToSimpleName(ReprModel):
    objects: ClassVar[models.Manager[ManyToManyToSimpleName]] = (
        models.Manager()
    )
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(
        SimpleName,
        verbose_name='Verbose simple names',
        help_text='Missing items will be auto-created',
    )


class ManyToManyToDoubleName(ReprModel):
    objects: ClassVar[models.Manager[ManyToManyToDoubleName]] = (
        models.Manager()
    )
    name: models.CharField[str, str] = models.CharField(max_length=50)
    double_names = models.ManyToManyField(
        DoubleName,
        verbose_name='Verbose double names',
        help_text='Double names help',
    )


class ManyToManyToError(ReprModel):
    objects: ClassVar[models.Manager[ManyToManyToError]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(
        SimpleName,
        verbose_name='Verbose simple names',
        help_text='Impossible to save',
    )

    def clean(self) -> None:
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError(
            {'simple_names': 'Expected testing error'}
        )


class ThroughModel(ReprModel):
    objects: ClassVar[models.Manager[ThroughModel]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_name: models.ForeignKey[SimpleName, SimpleName] = models.ForeignKey(
        SimpleName, on_delete=models.CASCADE
    )
    many_to_many_through: models.ForeignKey[
        ManyToManyThrough, ManyToManyThrough
    ] = models.ForeignKey('ManyToManyThrough', on_delete=models.CASCADE)


class ManyToManyThrough(ReprModel):
    objects: ClassVar[models.Manager[ManyToManyThrough]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(SimpleName, through=ThroughModel)


class InlineModel(ReprModel):
    objects: ClassVar[models.Manager[InlineModel]] = models.Manager()
    name: models.CharField[str, str] = models.CharField(max_length=50)
    simple_name: models.ForeignKey[SimpleName, SimpleName] = models.ForeignKey(
        SimpleName, on_delete=models.CASCADE
    )
    simple_names = models.ManyToManyField(ManyToManyToSimpleName)
    double_names = models.ManyToManyField(ManyToManyToDoubleName)
