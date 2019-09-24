from __future__ import absolute_import
import unittest
import pytest
from clims.models.pool import Pool
from clims.models.substance import Substance
from clims.services.substance import substances
from commonlims.utility.test_utils import create_organization
from commonlims.utility.test_utils import create_substance_type


@pytest.mark.django_db(transaction=False)
class TestPools(unittest.TestCase):
    def setUp(self):
        self.org = create_organization()
        self.gemstone_sample_type = create_substance_type(org=self.org)

    def test_create_pool__with_a_name(self):
        pool = Pool(name='edv')
        self.assertEqual('edv', pool.name)

    def test_create_pool__with_two_substances__number_parents_is_two(self):
        sub1 = substances.create(
            name='sub1', extensible_type=self.gemstone_sample_type,
            organization=self.org)
        sub2 = substances.create(
            name='sub2', extensible_type=self.gemstone_sample_type,
            organization=self.org)

        parents = [sub1, sub2]
        pool = Pool(name='edv')
        pool._wrapped.extensible_type = self.gemstone_sample_type
        pool._wrapped.organization = self.org
        pool._wrapped.save()
        pool._wrapped.parents.add(sub1)
        pool._wrapped.parents.add(sub2)
        self.assertEqual(2, len(pool._wrapped.parents.all()))
