from django.db import models
from django.core import exceptions


class ReprModel(models.Model):

    def __repr__(self):
        return '<%s[%d]: %s>' % (
            self.__class__.__name__,
            self.pk or -1,
            self.name,
        )

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Foo(ReprModel):
    name = models.CharField(max_length=50, help_text='The foo name')

    def full_clean(self, *args, **kwargs):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'name': 'Test Error'})


class Bar(ReprModel):
    name = models.CharField(max_length=50, help_text='The bar name')
    foo = models.ForeignKey(Foo, help_text='The foo object')


class Spam(ReprModel):
    name = models.CharField(max_length=50, help_text='The spam name')
    foo = models.ManyToManyField(Foo, help_text='The foo objects')

    def clean(self):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError({'foo': 'Test Error'})


class FooExtraSpam(ReprModel):
    foo = models.ForeignKey(Foo, help_text='The foo object')
    extra_spam = models.ForeignKey(
        'ExtraSpam', help_text='The extra spam object')


class ExtraSpam(ReprModel):
    name = models.CharField(max_length=50, help_text='The extra spam name')
    foo = models.ManyToManyField(
        Foo, through=FooExtraSpam, help_text='The foo objects')


class Egg(ReprModel):
    name = models.CharField(max_length=50, help_text='The egg name')
    name2 = models.CharField(max_length=50, help_text='The egg 2nd name')
    foo = models.OneToOneField(Foo, help_text='The foo object')

