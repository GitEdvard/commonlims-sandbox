from sentry.testutils import TestCase
from sentry_plugins.snpseq.plugin.models import Plate96
from sentry_plugins.snpseq.plugin.services.container import ContainerRepository


class TestContainers(TestCase):
    def setUp(self):
        self.register_extensible(Plate96)

    def test_create_plate96_container__number_of_rows_is_8(self):
        containers = ContainerRepository(self.organization)
        plate = containers.create_plate('myplate')

        # rows are located directly on the plate object!
        assert plate.rows == 8
