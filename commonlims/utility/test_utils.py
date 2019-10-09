from __future__ import absolute_import
from sentry.models.organization import Organization
from clims.models.plugin_registration import PluginRegistration
from clims.models.extensible import ExtensiblePropertyType
from clims.services.application import ApplicationService


def create_organization_new(self, name=None, owner=None, **kwargs):
    org = Organization.objects.create(name=name, **kwargs)
    if owner:
        self.create_member(
            organization=org,
            user=owner,
            role='owner',
        )
    return org


def create_plugin(org=None):
    plugin, _ = PluginRegistration.objects.get_or_create(
        name='tests_utils.create_plugin', version='1.0.0', organization=org)
    return plugin


def create_substance_type_for_sample(type_name=None, org=None, plugin=None, properties=None):
    properties = properties or [
        dict(name='concentration', raw_type=ExtensiblePropertyType.FLOAT, display_name='Concentration'),
    ]
    plugin = plugin or create_plugin()
    app = ApplicationService()
    substance_type = app.extensibles._register_model(type_name, org, plugin, property_types=properties)

    return substance_type
