from django.db import models

class ReprModel(models.Model):
    def __repr__(self):
        return (u'<%s[%d]: %s>' % (
            self.__class__.__name__,
            self.pk,
            self.name,
        )).encode('utf-8')

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Foo(ReprModel):
    name = models.CharField(max_length=50)


class Bar(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.ForeignKey(Foo)


class Spam(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.ManyToManyField(Foo)


class Egg(ReprModel):
    name = models.CharField(max_length=50)
    foo = models.OneToOneField(Foo)

