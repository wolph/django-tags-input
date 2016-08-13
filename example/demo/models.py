from django.db import models
from django.core import exceptions


class ReprModel(models.Model):

    def __repr__(self):
        return '<%s[%d]: %s>' % (
            self.__class__.__name__,
            self.pk or -1,
            self.name,
        )

    # Either unicode or str is used depending on the Python version
    def __unicode__(self):  # pragma: no cover
        return self.name

    def __str__(self):  # pragma: no cover
        return self.name

    class Meta:
        abstract = True


class SimpleName(ReprModel):
    name = models.CharField(max_length=50, help_text='Help text of the name')


class DoubleName(ReprModel):
    name_a = models.CharField(max_length=50)
    name_b = models.CharField(max_length=50)

    @property
    def name(self):
        return '%s/%s' % (self.name_a, self.name_b)


class ErrorName(ReprModel):
    name = models.CharField(max_length=50, help_text='Impossible to save name')

    def full_clean(self, *args, **kwargs):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'name': 'Test Error'})


class ForeignKeyToSimpleName(ReprModel):
    name = models.CharField(max_length=50)
    simple_name = models.ForeignKey(SimpleName)


class ManyToManyToSimpleName(ReprModel):
    name = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(
        SimpleName,
        verbose_name='Verbose simple names',
        help_text='Missing items will be auto-created')


class ManyToManyToDoubleName(ReprModel):
    name = models.CharField(max_length=50)
    double_names = models.ManyToManyField(
        DoubleName,
        verbose_name='Verbose double names',
        help_text='Double names help')


class ManyToManyToError(ReprModel):
    name = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(
        SimpleName,
        verbose_name='Verbose simple names',
        help_text='Impossible to save')

    def clean(self):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError(
            {'simple_names': 'Expected testing error'})


class ThroughModel(ReprModel):
    name = models.CharField(max_length=50)
    simple_name = models.ForeignKey(SimpleName)
    many_to_many_through = models.ForeignKey('ManyToManyThrough')


class ManyToManyThrough(ReprModel):
    name = models.CharField(max_length=50)
    simple_names = models.ManyToManyField(SimpleName, through=ThroughModel)


class InlineModel(ReprModel):
    name = models.CharField(max_length=50)
    simple_name = models.ForeignKey(SimpleName)
    simple_names = models.ManyToManyField(ManyToManyToSimpleName)
    double_names = models.ManyToManyField(ManyToManyToDoubleName)

