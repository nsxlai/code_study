from pytest import mark


@mark.xfail(reason='testing in DEV only')
def test_environment_is_qa(app_config):
    base_url = app_config.base_url
    port = app_config.app_port
    assert base_url == 'https://myqa-env.com'
    assert port == 80


def test_environment_is_dev(app_config):
    base_url = app_config.base_url
    port = app_config.app_port
    assert base_url == 'https://mydev-env.com'
    assert port == 8080


@mark.skip(reason='bad result due to env variable')
def test_environment_is_staging(app_config):
    base_url = app_config.base_url
    assert base_url == 'staging'


@mark.skip(reason='work in progress')
def test_work_in_progress():
    assert False