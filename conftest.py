from __future__ import absolute_import
import pytest

pytest_plugins = [
    'sentry.utils.pytest.sentry',
]

with open("/home/edeng655-local/source/commonlims-sandbox/.skiptests") as f:
    # Extra skips should be of the format <class_name>.<function_name>, as that
    # is the format pytest reports by default in the failure report
    extra_skips = {line.strip() for line in f.readlines()}


def pytest_configure(config):
    import warnings
    # XXX(dcramer): Riak throws a UserWarning re:OpenSSL which isnt important
    # to tests
    # XXX(dramer): Kombu throws a warning due to transaction.commit_manually
    # being used
    warnings.filterwarnings('error', '', Warning, r'^(?!(|kombu|raven|riak|sentry))')


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        try:
            cls_and_name = "{}.{}".format(item.cls.__name__, item.name)
            if cls_and_name in extra_skips:
                mark = pytest.mark.skip(reason="Is in .skiptests...")
                item.add_marker(mark)
        except AttributeError:
            pass
