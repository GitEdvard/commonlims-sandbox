from sentry.testutils import TestCase
from clims.models.container import Container


class TestContainer(TestCase):
    def test_create_same_container_twice__exception(self):
        c = Container(name='c1')
        c.save()
        c2 = Container(name='c1')
        c2.save()
