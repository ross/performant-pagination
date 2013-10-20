#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models


class SimpleModel(models.Model):
    name = models.CharField(max_length=32, db_index=True)

    def __unicode__(self):
        return '{0}: {1}'.format(self.pk, self.name)
