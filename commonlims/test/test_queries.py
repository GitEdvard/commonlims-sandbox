import pytest
from sentry.testutils import TestCase
from commonlims.fixtures.models import GemstoneSample


class SubstanceTestCase(TestCase):
    def create_gemstone(self, *args, **kwargs):
        return self.create_substance(GemstoneSample, *args, **kwargs)

    def register_gemstone_type(self):
        return self.register_extensible(GemstoneSample)


class TestQueries(SubstanceTestCase):
    @pytest.mark.now
    def test_number_sql_calls(self):
        sample = self.create_gemstone()
        sample.color = 'red'
        sample.preciousness = 'high'
        sample.save()

        from django.db import connection
        from django.db import reset_queries
        from django.conf import settings
        fetched_sample = self.app.substances.get(name=sample.name)
        settings.DEBUG = True
        reset_queries()
        assert fetched_sample.color == 'red'
        from pprint import pprint
        print('queries:')
        pprint(connection.queries)
        assert len(connection.queries) == 0

        assert fetched_sample.color == 'red'
        assert len(connection.queries) == 0

    def test_environment_printout(self):
        from django.conf import settings
        print('debug: {}'.format(settings.DEBUG))
        assert False
