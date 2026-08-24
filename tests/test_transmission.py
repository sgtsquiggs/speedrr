import pytest

from clients.transmission import TransmissionClient
from helpers.config import ClientConfig


def client_config(url):
    return ClientConfig(
        type="transmission",
        url=url,
        username="user",
        password="pass",
        https_verify=False,
    )


def test_rejects_an_unknown_url_scheme(speedrr_config):
    with pytest.raises(ValueError, match="Unknown url scheme"):
        TransmissionClient(speedrr_config, client_config("ftp://host:9091"))


def test_rejects_a_url_with_no_hostname(speedrr_config):
    with pytest.raises(ValueError, match="Missing hostname"):
        TransmissionClient(speedrr_config, client_config("http://"))
