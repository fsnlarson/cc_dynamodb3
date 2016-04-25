import mock

from factories.hash_only_model import (
    HashOnlyModel,
    HashOnlyModelFactory,
)


def test_query_primary_index_model_hash_key_should_return():
    HashOnlyModelFactory.create_table()
    HashOnlyModelFactory(agency_subdomain='metzler')
    HashOnlyModelFactory(agency_subdomain='other')

    count = HashOnlyModel.query_count(agency_subdomain='metzler')
    assert count == 1
    query = list(HashOnlyModel.query(agency_subdomain='metzler'))
    assert query[0].agency_subdomain == 'metzler'


def test_query_secondary_index_model_hash_key_should_return():
    HashOnlyModelFactory.create_table()
    HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)
    HashOnlyModelFactory(agency_subdomain='other', external_id=123)

    count = HashOnlyModel.query_count(external_id=123,
                                      query_index='HashOnlyExternalId')
    assert count == 2
    query = list(HashOnlyModel.query(external_id=123,
                                     query_index='HashOnlyExternalId'))
    assert set([o.agency_subdomain for o in query]) == {'metzler', 'other'}


def test_primary_key_should_return():
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)

    assert obj.get_primary_key() == dict(agency_subdomain='metzler')


def test_update_item_then_get():
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)
    assert obj.external_id == 123
    obj.external_id = 124
    obj.save()
    assert obj.external_id == 124

    reloaded = HashOnlyModel.get(agency_subdomain='metzler')
    assert reloaded.external_id == 124


def test_non_field_set_on_item_then_get():
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)
    obj.non_field = 123
    obj.save()

    reloaded = HashOnlyModel.get(agency_subdomain='metzler')
    assert not reloaded.item.get('non_field')


def test_local_change_then_reload():
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)
    obj.external_id = 124

    reloaded = obj.reload()
    assert reloaded.external_id == 123


@mock.patch('cc_dynamodb3.models.log_data')
def test_has_changed_primary_key_save_logs(log_data_mock):
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)
    obj.agency_subdomain = 'other'
    assert obj.has_changed_primary_key()

    obj.save()
    assert log_data_mock.called
    called_with = log_data_mock.call_args_list[0]
    assert called_with[0][0] == 'save overwrite=True table=dev_hash_only'


def test_to_json():
    HashOnlyModelFactory.create_table()
    obj = HashOnlyModelFactory(agency_subdomain='metzler', external_id=123)

    json_data = obj.to_json()
    assert '"is_enabled": null' in json_data
    assert ('"updated": "%s"' % obj.updated.isoformat()) in json_data