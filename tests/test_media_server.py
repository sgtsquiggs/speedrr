import httpx
import pytest

from helpers.config import IgnoreStreamConfig, MediaServerConfig
from modules.media_server import PlexServer, TautulliServer


# 8.8.8.8 stands in for a remote stream. RFC 5737 documentation ranges
# (203.0.113.0/24 and friends) look like better placeholders but are wrong here:
# Python's ipaddress module classifies them as private, so process_session()
# would ignore them as local. No network traffic occurs -- the address is only
# ever parsed.
def plex_session(session_id="s1", bandwidth=5000, state="playing", address="8.8.8.8"):
    return {
        "title": "Some Movie",
        "Session": {"id": session_id, "bandwidth": bandwidth},
        "Player": {"state": state, "address": address},
    }


def plex_payload(*sessions):
    return {
        "MediaContainer": {
            "size": len(sessions),
            "Metadata": list(sessions),
        }
    }


@pytest.fixture
def plex(speedrr_config, plex_server_config, make_media_server_module):
    return PlexServer(speedrr_config, plex_server_config, make_media_server_module(speedrr_config))


def test_plex_returns_zero_when_no_sessions(httpx_mock, plex):
    httpx_mock.add_response(json={"MediaContainer": {"size": 0}})

    assert plex.get_bandwidth() == 0


def test_plex_sums_remote_session_bandwidth(httpx_mock, plex):
    httpx_mock.add_response(
        json=plex_payload(
            plex_session(session_id="a", bandwidth=4000),
            plex_session(session_id="b", bandwidth=1500),
        )
    )

    assert plex.get_bandwidth() == 5500


def test_plex_ignores_private_addresses_when_local_is_ignored(httpx_mock, plex):
    httpx_mock.add_response(
        json=plex_payload(
            plex_session(session_id="a", bandwidth=4000, address="192.168.1.50"),
            plex_session(session_id="b", bandwidth=1500, address="8.8.8.8"),
        )
    )

    assert plex.get_bandwidth() == 1500


def test_plex_treats_the_literal_lan_address_as_local(httpx_mock, plex):
    # Regression guard: Plex reports "lan" where an IP is expected, and
    # ipaddress.ip_address("lan") raises. The code special-cases it.
    httpx_mock.add_response(json=plex_payload(plex_session(bandwidth=9000, address="lan")))

    assert plex.get_bandwidth() == 0


def test_plex_raises_on_a_payload_without_a_mediacontainer(httpx_mock, plex):
    httpx_mock.add_response(json={"error": "bad token"})

    with pytest.raises(Exception, match="Error from Plex"):
        plex.get_bandwidth()


def test_plex_raises_for_http_errors(httpx_mock, plex):
    httpx_mock.add_response(status_code=401)

    with pytest.raises(httpx.HTTPStatusError):
        plex.get_bandwidth()


def test_ip_networks_extend_what_counts_as_local(
    httpx_mock, speedrr_config, make_media_server_module
):
    config = MediaServerConfig(
        type="plex",
        url="http://plex:32400",
        https_verify=False,
        bandwidth_multiplier=1.0,
        update_interval=5,
        ignore_streams=IgnoreStreamConfig(
            local=False,
            ip_networks=("203.0.113.0/24",),
            paused_after=300,
        ),
        token="token123",
    )
    server = PlexServer(speedrr_config, config, make_media_server_module(speedrr_config))
    httpx_mock.add_response(json=plex_payload(plex_session(bandwidth=7000, address="203.0.113.5")))

    assert server.get_bandwidth() == 0


def test_tautulli_sums_session_bandwidth(httpx_mock, speedrr_config, make_media_server_module):
    config = MediaServerConfig(
        type="tautulli",
        url="http://tautulli:8181",
        https_verify=False,
        bandwidth_multiplier=1.0,
        update_interval=5,
        ignore_streams=IgnoreStreamConfig(local=True, ip_networks=None, paused_after=300),
        api_key="key123",
    )
    server = TautulliServer(speedrr_config, config, make_media_server_module(speedrr_config))
    httpx_mock.add_response(
        json={
            "response": {
                "result": "success",
                "data": {
                    "sessions": [
                        {
                            "session_id": "a",
                            "bandwidth": 3000,
                            "state": "playing",
                            "ip_address": "8.8.8.8",
                            "full_title": "Show",
                        }
                    ]
                },
            }
        }
    )

    assert server.get_bandwidth() == 3000


def test_tautulli_raises_when_the_api_reports_failure(
    httpx_mock, speedrr_config, make_media_server_module
):
    config = MediaServerConfig(
        type="tautulli",
        url="http://tautulli:8181",
        https_verify=False,
        bandwidth_multiplier=1.0,
        update_interval=5,
        ignore_streams=IgnoreStreamConfig(local=True, ip_networks=None, paused_after=300),
        api_key="key123",
    )
    server = TautulliServer(speedrr_config, config, make_media_server_module(speedrr_config))
    httpx_mock.add_response(json={"response": {"result": "error", "message": "invalid apikey"}})

    with pytest.raises(Exception, match="Error from Tautulli"):
        server.get_bandwidth()
