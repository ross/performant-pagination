#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from django.core.paginator import Page


# we inherit from Page, even though it's a bit odd since we're so
# different, but if we don't some of the tools that use it will break,
# django-rest-framework for example. we do get a little bit from it though, in
# not having to implement some methods
class PerformantPage(Page):

    def __init__(self, paginator, object_list, prev_token, token, next_token):
        self.paginator = paginator
        self.object_list = object_list
        self.prev_token = prev_token
        self.token = token
        self.next_token = next_token

    def __repr__(self):
        return '<PerformantPage (%s, %s %s)>' % (self.prev_token, self.token,
                                                 self.next_token)

    def has_next(self):
        return self.next_token is not None

    def has_previous(self):
        return self.prev_token is not None

    def has_other_pages(self):
        return self.has_next() or self.has_previous()

    def next_page_number(self):
        return self.next_token

    def previous_page_number(self):
        return self.prev_token

    def start_index(self):
        return None

    def end_index(self):
        return None


class PerformantPaginator(object):

    def __init__(self, queryset, per_page=25, ordering=('pk',),
                 allow_count=False, allow_empty_first_page=True, orphans=0):
        '''As a general rule you should ensure there's an appropriate index for
        the fields provided in ordering.

        allow_count (default False) indicates whether or not to allow count
        queries that can be extremely expensive on large and fast changing
        datasets.

        allow_empty_first_page and orphans are currently ignored and only exist
        to allow dropping in place of Django's built-in pagination.
        '''
        self.queryset = queryset
        self.per_page = int(per_page)
        self.ordering = ordering
        self.allow_count = allow_count

        fields = []
        reverse_ordering = []
        for field in self.ordering:
            if field[0] == '-':
                field = field[1:]
                fields.append(field)
                reverse_ordering.append(field)
            else:
                fields.append(field)
                reverse_ordering.append('-{0}'.format(field))

        self._fields = fields
        self._reverse_ordering = reverse_ordering

    def __repr__(self):
        return '<PerformantPaginator (%d, %s %d)>' % (self.per_page,
                                                      self.ordering,
                                                      self.allow_count)

    def count(self):
        '''Counting the number of items is expensive, so by default it's not
        supported and None will be returned.'''
        return self.queryset.count() if self.allow_count else None

    def default_page_number(self):
        return None

    def validate_number(self, number):
        "Allows anything through since we"
        # TODO: could potentially make sure it's a valid value for our ordering
        return number

    def _object_to_token(self, obj):
        # TODO: more robust token creation, some sort of real serialization
        # that will escape seperators etc.
        token = []
        for field in self._fields:
            pieces = field.split('__')
            o = obj
            if len(pieces) > 1:
                # walk down relationships
                for piece in pieces[:-1]:
                    o = getattr(o, piece)
                field = pieces[-1]

            token.append(str(getattr(o, field)))

        return ':'.join(token)

    def _token_to_clause(self, token, rev=False):
        values = token.split(':')
        clause = {}
        # in the forward direction we want things that are greater than our
        # value, but if the ordering is -, we want less than. if rev=True we
        # fip it
        direction = ('lt', 'gt') if rev else ('gt', 'lt')
        for i, field in enumerate(self.ordering):
            if field[0] == '-':
                d = direction[1]
            else:
                d = direction[0]
            field = field.replace('-', '')
            # TODO: do we need to convert values to their appropriate type?
            clause['{0}__{1}'.format(field, d)] = values[i]
        return clause

    def page(self, token=None):
        # work around generics being integer specific with a default of 1,
        # again this is to deal with some pagination consumers that force our
        # hand
        if token == 1:
            token = None

        # get a queryset
        qs = self.queryset
        # if we have a truthy token, not includeing '', we'll need to offset
        if token:
            # we're paged in a bit, token will be the values of the final
            # object of the previous page, so we'll start with it
            qs = qs.filter(**self._token_to_clause(token))

        # apply our ordering
        qs = qs.order_by(*self.ordering)

        # get our object list, +1 to see if there's more to come
        object_list = list(qs[:self.per_page + 1])

        next_token = None
        # if there were more, then use
        if len(object_list) > self.per_page:
            # get rid of the extra
            object_list = object_list[:-1]
            # and now our last item's pk is the token for the next page
            next_token = self._object_to_token(object_list[-1])

        prev_token = None
        # if we have a truthy token, not including '', we'll check to see if
        # there's a prev
        if token:
            clause = self._token_to_clause(token, rev=True)
            qs = self.queryset.filter(**clause).only(*self._fields) \
                .order_by(*self._reverse_ordering)
            try:
                prev_token = self._object_to_token(qs[self.per_page - 1])
            except IndexError:
                # can't be none b/c some tooling will turn it in to 'None'
                prev_token = ''

        # return our page
        return PerformantPage(self, object_list, prev_token, token, next_token)
