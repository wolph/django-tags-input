from django.db import models
from django.core import exceptions

class ReprModel(models.Model):
    def __repr__(self):
        return (u'<%s[%d]: %s>' % (
            self.__class__.__name__,
            self.pk or -1,
            self.name,
        )).encode('utf-8')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class Foo(ReprModel):
    name = models.CharField(max_length=50)

    def full_clean(self):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError('Test Error')


class Bar(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.ForeignKey(Foo)


class Spam(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.ManyToManyField(Foo)

    def clean(self):
        # We want everything tested, also calling a clean method
        raise exceptions.ValidationError('Test Error')


class FooExtraSpam(ReprModel):
    foo = models.ForeignKey(Foo)
    extra_spam = models.ForeignKey('ExtraSpam')


class ExtraSpam(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.ManyToManyField(Foo, through=FooExtraSpam)


class Egg(ReprModel):
    name = models.CharField(max_length=50)
    name2 = models.CharField(max_length=50)
    foo = models.OneToOneField(Foo)

