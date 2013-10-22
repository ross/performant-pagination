#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models


class SimpleModel(models.Model):
    name = models.CharField(max_length=32, db_index=True)

    def __unicode__(self):
        return '{0}: {1}'.format(self.pk, self.name)


class RelatedModel(models.Model):
    number = models.IntegerField()
    simple = models.ForeignKey(SimpleModel, related_name='related_models')

    def __unicode__(self):
        return '{0}: {1}'.format(self.pk, self.number)

    class Meta(object):
        unique_together = (('simple', 'number'),)
