#
#
#

from __future__ import absolute_import, print_function, unicode_literals

from django.core.paginator import Page, PageNotAnInteger
from django.test import TestCase
from performant_pagination.pagination import PerformantPaginator
from performant_pagination.tests.models import RelatedModel, SimpleModel


class TestBasicPagination(TestCase):
    maxDiff = None

    def setUp(self):
        SimpleModel.objects.bulk_create(
            [SimpleModel(name='object {0}'.format(i)) for i in range(33)]
        )

    def test_page_1_work_around(self):
        objects = SimpleModel.objects.order_by('pk')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all())
        self.assertTrue(paginator)
        # first page
        page = paginator.page(1)
        self.assertTrue(page)
        self.assertIsInstance(page, Page)

        # make sure we got the first page
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(str(objects[24].pk), page.next_token)
        self.assertEquals(None, page.prev_token)

    def test_allow_count(self):
        objects = SimpleModel.objects.order_by('pk')

        # defaults, no count
        paginator = PerformantPaginator(SimpleModel.objects.all())
        self.assertTrue(paginator)
        self.assertEquals(None, paginator.count())

        # allow_count
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        allow_count=True)
        self.assertTrue(paginator)
        self.assertEquals(len(objects), paginator.count())

    def test_default_page_number(self):
        paginator = PerformantPaginator(None)
        self.assertEquals(None, paginator.default_page_number())

    def test_validate_number(self):
        paginator = PerformantPaginator(None)
        # things that are valid
        for number in (None, '', 42, 1, -1, 'something'):
            self.assertEquals(number, paginator.validate_number(number))
        # things that are not
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a:b')
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a:b:c')
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a:b:')

        paginator = PerformantPaginator(None, ordering=('name', 'sub_name',
                                                        'third'))
        # things that are valid
        self.assertEquals(None, paginator.validate_number(None))
        self.assertEquals('a:b:c', paginator.validate_number('a:b:c'))
        self.assertEquals('', paginator.validate_number(''))
        # things that are not
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a')
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('a:b')


    def test_has_other_pages(self):
        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all())
        self.assertTrue(paginator)
        page = paginator.page()
        self.assertTrue(page.has_other_pages())
        while page.has_next():
            self.assertTrue(page.has_other_pages())
            page = paginator.page(page.next_page_number())

        # per_page > total count so no next/prev
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        per_page=999)
        self.assertTrue(paginator)
        page = paginator.page()
        self.assertFalse(page.has_other_pages())

    def test_basic(self):
        objects = SimpleModel.objects.order_by('pk')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all())
        self.assertTrue(paginator)
        self.assertTrue(str(paginator))
        # first page
        page = paginator.page()
        self.assertTrue(page)
        self.assertTrue(str(page))

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(str(objects[24].pk), page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals(str(objects[24].pk), page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[25:]), list(page))
        # and the expected next tokens
        self.assertEquals(str(objects[24].pk), page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())

    def test_reversed(self):
        objects = SimpleModel.objects.order_by('-pk')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        ordering=('-pk',))
        self.assertTrue(paginator)
        # first page
        page = paginator.page()
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(str(objects[24].pk), page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals(str(objects[24].pk), page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[25:]), list(page))
        # and the expected next tokens
        self.assertEquals(str(objects[24].pk), page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())

    def test_non_pk(self):
        objects = SimpleModel.objects.order_by('name')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        ordering=('name',))
        self.assertTrue(paginator)
        # first page
        page = paginator.page()
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(objects[24].name, page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals(objects[24].name, page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[25:]), list(page))
        # and the expected next tokens
        self.assertEquals(objects[24].name, page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())

    def test_compound(self):
        objects = SimpleModel.objects.order_by('pk', 'name')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        ordering=('pk', 'name'))
        self.assertTrue(paginator)
        # first page
        page = paginator.page()
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        obj = objects[24]
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name), page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name),
                          page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[25:]), list(page))
        # and the expected next tokens
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name), page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())

    # test_compound, reversed
    def test_reversed_compound(self):
        objects = SimpleModel.objects.order_by('-pk', '-name')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        ordering=('-pk', '-name'))
        self.assertTrue(paginator)
        # first page
        page = paginator.page()
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        obj = objects[24]
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name), page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name),
                          page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[25:]), list(page))
        # and the expected next tokens
        self.assertEquals('{0}:{1}'.format(obj.pk, obj.name), page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())

    def test_page_sizes(self):
        objects = SimpleModel.objects.order_by('pk')

        # defaults
        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        per_page=11)
        self.assertTrue(paginator)
        # first page
        page = paginator.page()
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[:11]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(str(objects[10].pk), page.next_token)
        self.assertEquals(None, page.prev_token)

        # check the page's methods
        self.assertFalse(page.has_previous())
        self.assertEquals(None, page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals(str(objects[10].pk), page.next_page_number())

        # these guys are not applicable/implemented with our system
        self.assertFalse(page.start_index())
        self.assertFalse(page.end_index())

        # now lets check the 2nd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[11:22]), list(page))
        # and the expected next tokens
        self.assertEquals(str(objects[10].pk), page.token)
        self.assertEquals(str(objects[21].pk), page.next_token)
        self.assertEquals('', page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals('', page.previous_page_number())
        self.assertTrue(page.has_next())
        self.assertEquals(str(objects[21].pk), page.next_page_number())

        # and finally the 3rd page
        page = paginator.page(page.next_page_number())
        self.assertTrue(page)

        # make sure we got the expected data
        self.assertEquals(list(objects[22:]), list(page))
        # and the expected next tokens
        self.assertEquals(str(objects[21].pk), page.token)
        self.assertEquals(None, page.next_token)
        self.assertEquals(str(objects[10].pk), page.prev_token)

        # check the page's methods
        self.assertTrue(page.has_previous())
        self.assertEquals(str(objects[10].pk), page.previous_page_number())
        self.assertFalse(page.has_next())
        self.assertEquals(None, page.next_page_number())


class TestLarger(TestCase):

    def setUp(self):
        SimpleModel.objects.bulk_create(
            [SimpleModel(name='object {0}'.format(i)) for i in range(333)]
        )

    def test_larger(self):
        objects = list(SimpleModel.objects.order_by('pk'))

        paginator = PerformantPaginator(SimpleModel.objects.all(),
                                        per_page=50)

        page = paginator.page()
        self.assertFalse(page.previous_page_number())
        off = 0
        while page.has_next():
            self.assertEquals(50, len(page))
            self.assertEquals(list(objects[off:off + 50]), list(page))
            page = paginator.page(page.next_page_number())
            off += 50

        # last page
        self.assertTrue(page.previous_page_number() is not None)
        self.assertEquals(33, len(page))
        self.assertEquals(list(objects[off:off + 33]), list(page))
        self.assertEquals(None, page.next_page_number())

        # now let's go backwards
        page = paginator.page(page.previous_page_number())
        while page.has_previous():
            off -= 50
            self.assertEquals(50, len(page))
            self.assertEquals(list(objects[off:off + 50]), list(page))
            page = paginator.page(page.previous_page_number())


class TestRelationships(TestCase):

    def setUp(self):
        SimpleModel.objects.bulk_create(
            [SimpleModel(name='object {0}'.format(i)) for i in range(27)]
        )
        relateds = []
        for simple in SimpleModel.objects.all():
            relateds.extend(
                [RelatedModel(number=i, simple=simple) for i in range(5)]
            )
        RelatedModel.objects.bulk_create(relateds)

    def test_related_order(self):
        objects = RelatedModel.objects.order_by('simple__name')

        # defaults
        paginator = PerformantPaginator(RelatedModel.objects.all(),
                                        ordering=('simple__name',))
        self.assertTrue(paginator)
        self.assertTrue(str(paginator))
        # first page
        page = paginator.page()
        self.assertTrue(page)
        self.assertTrue(str(page))

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals(str(objects[24].simple.name), page.next_token)
        self.assertEquals(None, page.prev_token)

    def test_related_compound(self):
        objects = RelatedModel.objects.order_by('simple__name', '-pk')

        # defaults
        paginator = PerformantPaginator(RelatedModel.objects.all(),
                                        ordering=('simple__name', '-pk'))
        self.assertTrue(paginator)
        self.assertTrue(str(paginator))
        # first page
        page = paginator.page()
        self.assertTrue(page)
        self.assertTrue(str(page))

        # make sure we got the expected data
        self.assertEquals(list(objects[:25]), list(page))
        # and the expected next tokens
        self.assertEquals(None, page.token)
        self.assertEquals('{0}:{1}'.format(objects[24].simple.name,
                                           objects[24].pk), page.next_token)
        self.assertEquals(None, page.prev_token)
