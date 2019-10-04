from __future__ import absolute_import
from sentry.models.organization import Organization
from clims.models.plugin_registration import PluginRegistration
from clims.models.extensible import ExtensiblePropertyType
from uuid import uuid4
# from clims.services.substance import substances
from clims.services.extensible import extensibles


def create_organization():
    org = Organization.objects.get(name='lab')
    return org


def create_plugin(org=None):
    org = org or create_organization()
    plugin, _ = PluginRegistration.objects.get_or_create(
        name='tests_utils.create_plugin', version='1.0.0', organization=org)
    return plugin


def create_gemstone_substance_type(org=None, plugin=None, properties=None):
    properties = properties or [
        dict(name='color', raw_type=ExtensiblePropertyType.STRING, display_name='Col.'),
        dict(name='preciousness', raw_type=ExtensiblePropertyType.STRING, display_name='Prec.'),
        dict(name='payload', raw_type=ExtensiblePropertyType.JSON, display_name='Payload'),
    ]
    plugin = plugin or create_plugin()
    substance_type = extensibles._register_model('GemstoneSample', org, plugin, property_types=properties)
    # substance_type = extensibles.register('GemstoneSample', org, plugin, properties=properties)

    return substance_type
