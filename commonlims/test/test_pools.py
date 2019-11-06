import pytest
from sentry.testutils import TestCase
from sentry_plugins.snpseq.plugin.models import Pool
from sentry_plugins.snpseq.plugin.models import RmlSample
from clims.services.substance import SubstanceBase
from clims.services.application import ioc


class TestPools(TestCase):
    def setUp(self):
        self.register_extensible(Pool)
        self.register_extensible(RmlSample)

    def test_instantiate_pool__with_access_of_internal_variables__pool_parents_listable(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()
        sample3 = RmlSample(name='sample3', organization=self.organization)
        sample3.save()

        # Act
        pool1 = Pool(name='pool1', organization=self.organization)
        pool1.save()
        pool1._archetype.parents.add(sample1._wrapped_version)
        pool1._archetype.parents.add(sample2._wrapped_version)
        pool1._archetype.parents.add(sample3._wrapped_version)
        pool1.save()

        # Assert
        expected_parents = {'sample1', 'sample2', 'sample3'}
        assert expected_parents == {p.name for p in pool1.parents}

    def test_create_pool__with_constructor_call__pool_parents_listable(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()
        sample3 = RmlSample(name='sample3', organization=self.organization)
        sample3.save()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[sample1, sample2, sample3])
        pool1.save()

        # Assert
        expected_parents = {'sample1', 'sample2', 'sample3'}
        assert expected_parents == {p.name for p in pool1.parents}

    def test_update_sample__with_no_parents(self):
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        sample1.special_info_sequencing = 'some text'
        sample1.save()

    def test_update_pool__with_parent__fetched_object_from_db_ok(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[sample1])
        pool1.save()
        pool1.volume = 10
        pool1.save()

        # Assert
        fetched = self.app.substances.get(name='pool1')
        expected_parents = {'sample1'}
        assert expected_parents == {p.name for p in fetched.parents}
        assert 10 == fetched.volume

    def test_instantiate_substance__with_already_created_sample__property_retained(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.custom_seq_primer = 'xxx'
        sample1.save()

        # Act
        sample2 = SubstanceBase(_wrapped_version=sample1._wrapped_version)

        # Assert
        props = {k: prop.value for k, prop in sample2.properties.items()}
        assert props['custom_seq_primer'] == 'xxx'

    def test_instantiate_substance__with_both_created_sample_and_parents__exception(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.custom_seq_primer = 'xxx'
        sample1.save()

        # Act
        # Assert
        with pytest.raises(AssertionError):
            SubstanceBase(_wrapped_version=sample1._wrapped_version, parents=[sample1])

    def test_create_pool__from_depth_1_samples__depth_of_pool_is_2(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[sample1, sample2])
        pool1.save()

        # Assert
        assert sample1.depth == 1
        assert sample2.depth == 1
        assert pool1.depth == 2

    def test_create_pool__from_samples_with_different_depths__depth_of_pool_is_based_on_highest(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1._archetype.depth = 4
        sample1.save()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[sample1, sample2])
        pool1.save()

        # Assert
        assert sample1.depth == 4
        assert sample2.depth == 1
        assert pool1.depth == 5

    def test_create_pool__from_two_samples__origins_of_pool_are_the_samples(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[sample1, sample2])
        pool1.save()

        # Assert
        assert len(pool1.origins) == 2
        assert set(pool1.origins) == {sample1.id, sample2.id}

    @pytest.mark.now
    def test_create_pool__from_two_aliqouts__origins_of_pool_are_original_samples(self):
        # Arrange
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()
        aliquot1 = sample1.create_child()
        sample2 = RmlSample(name='sample2', organization=self.organization)
        sample2.save()
        aliquot2 = sample2.create_child()

        # Act
        pool1 = Pool(
            name='pool1', organization=self.organization, parents=[aliquot1, aliquot2])
        pool1.save()

        # Assert
        assert len(pool1.origins) == 2
        assert set(pool1.origins) == {sample1.id, sample2.id}

    def test_fetch_sample__origins_is_ok(self):
        sample1 = RmlSample(name='sample1', organization=self.organization)
        sample1.save()

        fetched = ioc.app.substances.get_by_name('sample1')

        assert len(fetched.origins) == 1
