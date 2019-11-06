from __future__ import absolute_import
from clims.services.substance import SubstanceBase
from clims.services.extensible import TextField


class GemstoneSample(SubstanceBase):
    preciousness = TextField(prop_name="preciousness")  # TODO: Metaclass that sets prop_name
    color = TextField(prop_name="color")
