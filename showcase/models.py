"""Small, isolated data set for the interactive examples."""

from __future__ import annotations

from django.db import models


class Tag(models.Model):
    """A reusable tag identified by its label."""

    name: models.CharField[str, str] = models.CharField(
        max_length=100, unique=True
    )

    def __str__(self) -> str:
        """Return the label shown in the showcase."""
        return self.name


class Contact(models.Model):
    """A contact with a label composed from two fields."""

    first_name: models.CharField[str, str] = models.CharField(max_length=100)
    last_name: models.CharField[str, str] = models.CharField(max_length=100)

    def __str__(self) -> str:
        """Return the label shown in the showcase."""
        return f'{self.first_name} - {self.last_name}'


class Article(models.Model):
    """An independent selection for one showcase mode."""

    title: models.CharField[str, str] = models.CharField(
        max_length=100, unique=True
    )
    tags: models.ManyToManyField[Tag, models.Model] = models.ManyToManyField(
        Tag, blank=True
    )
    contacts: models.ManyToManyField[Contact, models.Model] = (
        models.ManyToManyField(Contact, blank=True)
    )

    def __str__(self) -> str:
        """Return the label shown in the showcase."""
        return self.title
