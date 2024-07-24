from django.apps import apps
from django.conf import settings

from axis.core import technology

__author__ = "Autumn Valenta"
__date__ = "10-16-14 12:57 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]


class FilehandlingConfig(technology.TechnologyAppConfig):
    """Filehandling technology configuration."""

    name = "axis.filehandling"

    HASHID_FILE_HANDLING_SALT = f"filehandling.CustomerDocument{settings.HASHID_FIELD_SALT}"

    # Import
    @property
    def rater_organization_factory(self):
        return apps.get_app_config("company").rater_organization_factory

    # Exports
    @property
    def customer_document_factory(self):
        dotted_path = ".tests.factories.customer_document_factory"
        return self._get_dotted_path_function(dotted_path)

    @property
    def store_document_to_model_instance(self):
        dotted_path = ".utils.store_document_to_model_instance"
        return self._get_dotted_path_function(dotted_path)

    DOCUSIGN_SANDBOX_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAuoESqDjCwGQfffN2VIvpvm1gqFQVEM5y/HhGlTAjVqbgcu5u
rVr1NzuQ9YlzAP72HpaCiBD8c6k/Prj2oT41TWi17u9XGAJVxum+HC1PNU4KvBOX
uH147iqk3ESlc1z6qAib8vBqS2VAr3gJPQFKmYU3biE/OFTWZEc3Rt/PcqW4ekld
oLPCREXwHxum7K1+E5Z33xbGXpoX1CpMDPFX03vMnLNEB+p074JQhNO1IHKQahoH
m5AiKlQKf8/jNdLcrl4geqE+UkgF47GjhLzAHKkHI/oiV8Myeot/jEkCTF6wbAmR
aarR2Mm5IE9zhlnC6Ri5DZx/mczdmzIXP/wHTQIDAQABAoIBABYI7+peImxWp/3a
iO1+RlSQWa4pmP+OVLmNgFFaCaLQPo51qy/iIjyvVfYckjDY7r04bR2kXB9SLL29
Xq44SlXl/DDJqFGW3QmOTj7H/6a9nLkR24gZkvMYqLe5iI6zuo2lzr8KNpTH1rek
h/rkLysqOR1S4kRGibn5TAeco8bYp9fGbUG9kixjuMKkK7DjAlfsmM2Ki4cBCTcj
wxnySBAil4MD+RmydNLOJXxJpxiICQvUFhXvaapUM1bgF8VEjUsxe5PLwoHHvIU0
PdgFcMfmdkAi6wVxD+745od1rXZ6HYHkae+dra3YKRfs9hJA01NEMOESISt3oWNN
ow1NZAECgYEA5volad0nCYazUZCFu35B13abbgmjLOFWTGdLxAggTaDgy1D4LJYh
EgCkaAkc/ZVeeQKgIS17H4xTXVuRNTfODXt2d7YzoAwOSCs0FhuU+jCW4sphq5Mr
spk8hZe+yU75TATVNzEr1PFnRo89iK9Dtplc+Z/ZvLeMkfF5z8p9zk0CgYEAzrWG
333C4VeUXeAefQB/tkD4gGxNcZCvzSOBUjyDec03ItVzm4FoGbmSWgEU7muZWIIN
wbr31F8wZVx4HsnNk7qABF+LZa/qx2B0MbiHMmu3N1dGkFibr57kZo1pj09Wg8di
g0hpY3pzPsFnrjrv6IkDUovpxECu5KTCe8xdnQECgYAR7pm4/lJpiuuhCXdYdxTl
hW/LuzPP6C6q/9oB/h+D51mMb1zVGVK38xTQfuShS1dqTang6YcFi/9s4A8F8q8s
nMk1wg9//W+earxAeyO1yM/uC4hJqcNaukrYlE9bkaYJINbs0gR1I8jA0Z4VXoYD
RyTQvHhLDnT7X6P1XeMmgQKBgFhbxBFYgqsscqFGIgIw6maPkyniIaB/xoYbvTXX
5CN2kzDyqP457LPCXUrX14iqudvZi+PZ9gHzxo4tXrNac+PH/tzfsoh/EA61rjVq
uW/WF3Uye1lMZxBFDUDBBfRaZ5Lg8b1IgLQjLYwPxC/3xYFSv/bTE9PuClR2ESQ2
EXYBAoGBALKVnuV+O3U6pVd/LCd4YzDZQtAhRXIckrXhpDGq76ZK7ZPi2X7+Asdl
UR92dkkQCI+ZqvgTr6yks4118Dimw3xTPp/wOiQU9Ke+D4598O57fCF5hHmKff0E
CYWkqNCdF3fmAzg3Fp4fG0/WN5NHeESpM0c+OxQHMYfvqk0jxzLE
-----END RSA PRIVATE KEY-----"""

    DOCUSIGN_SECURE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxRE5Z5mxRLAtdYzCUwQ1h4m7an54rWNtT/zAeOMLRt/kver+
0h9N40klhqA1bgdUXTBhU9QpLymQIV7ts/XnfoEuMGsfMG+Q3cmNhbjW2+VZQeyi
/VYlbvmwM0sR9r9gXJUUcD//RrA9D9HOS800E5zTNsAkDzx4KjLOFdXfDjZA6WFQ
DUqm7eydWMUDLSf/TMXQBf6OE6/yVaiqI4c4GX+SOxu3+6g/CBRgdnC2Q8lE1bt7
sRExHBCGQXzh2VvOF+J5zrPC6u6E0v64kpwidzHmiLg9Mn/HXyNjS9UZXmquPAim
NYF30b3DPpfG98Y0ZEMJQbCZUpIkXIIFDuJMlQIDAQABAoIBAAC7kf68R+LH05Nx
T4j8JgV3/KC7vE/LY9en9UCTJN1BmIR1lYxLHitZ1UWNM5r8yf0tYIntla2di5yk
JrbEPkpuc9vYOh3K/GXmtEZVVpnWCMvsSPraJs96fC45+Y90913AwXpdXTdHu80N
lvpvK+IQHjTrkqFqic6BBoUhmMULwEGzikBpiS0uS5kO27riXYfyWQ3pjSfBTFX5
mCXngxX61AzimIIveWrl6gzfbNfY/AmjZ6QUGTLdgw2QdXKJXgSo1jT696+0M6Oa
gYGSpoj6mBOWU7rOKxgLFWZR0XaDPXzOqGTeaqJGJrVKryAh8v/tijEFZT/c2/xY
fxV4p0ECgYEA5T8+HNkkiBxJT/YphTCOesFXpJflZ5sPBaDoiynih8eohrwurIml
g9crn+Hm2idlw9X7Yl8rL03VpDH8+P81tHgEhT5XV1qz2YPMLfHoKT+conodSw8y
acTGlqhqXmsyf73QG5SB6oJfwWzpzBPdDeGKw24rPOvY9ZW8bie1S1ECgYEA3BCc
a6MJfEVpDO0o2PXYd/WrdFmACiIAb2VTx0AKm9dbvbN6dtaJoIjP8SHfQhWQzQok
UH6l+n1JU8wSoh2VO5D16Nle3yBH94Is0q/yi/4DhbSHWgJ9cxfmUJehlztSzAkZ
gxJQRX4rmKRw9Md3MdinVmWj5Q9occzrT369lAUCgYEAsjfxTLIO8XW0FOLVMoMm
MQ5/2ShxIpNsIT8PqaidQFuai2xeiKnVr+ImOvx+4JgCSDXhYX+E7hh/f0+RT+3v
zWYEdaWadwG/kdkhcZJ/nxmh5roybbjZw1pD3Ln/P3ns31wsHlTcjvheAtxuAcZr
crAllXrfSFQ97eZDgAuEqJECgYATNrgRhcicOwsy/7njR4PA5Yg0vmO5fsJ+91/b
M7I5bRIre/IjUhPuGkPdj9GIWY2s+Ue2Z3hiaHHwiQ7PbLnM25k83U21OYJPD+SN
+KK6qlDwaZSvvSvq0plfS/3l0F4oRlsd4Il1p9ByoVjjZk734SyrFHC83R2HYhbh
d/VhaQKBgFdhUuoQwVi5fNWh4mBJGIzJYsUPGCEz6DP+HpD06xNAm6rXCp1qt0U4
ejNTKc+a6iNnAnASb15NorPXu4+QKhjp918/28QGOkRYMz2nCFVHTRd4aFkU2Yu8
vJtwPuRdsIljKYYy2KvrPnPJ86hjJseAG7AY1eQCOw1lFQlfQXEG
-----END RSA PRIVATE KEY-----"""
