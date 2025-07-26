import pytest
import httpx
from respx import MockRouter
from pymonad.either import Left, Right
from assertpy import assert_that

from src.clients.spotify import SpotifyClient, SpotifyToken

@pytest.fixture
def spotify_client():
    """Fixture pour un client Spotify avec des identifiants factices."""
    return SpotifyClient(client_id="test_id", client_secret="test_secret")

@pytest.mark.asyncio
async def test_get_token_success(spotify_client: SpotifyClient, respx_mock: MockRouter):
    """Teste la récupération réussie d'un jeton d'accès."""
    respx_mock.post("https://accounts.spotify.com/api/token").mock(
        return_value=httpx.Response(200, json={"access_token": "new_fake_token", "expires_in": 3600})
    )
    result = await spotify_client._get_token()
    assert result.is_right()
    assert result.value == "new_fake_token"

@pytest.mark.asyncio
async def test_get_token_failure(spotify_client: SpotifyClient, respx_mock: MockRouter):
    """Teste l'échec de la récupération d'un jeton d'accès."""
    respx_mock.post("https://accounts.spotify.com/api/token").mock(return_value=httpx.Response(401))
    result = await spotify_client._get_token()
    assert result.is_left()
    result.either(
        lambda err: assert_that("Impossible de s'authentifier" in err),
        lambda _: pytest.fail("Expected Left, got Right")
    )

@pytest.mark.asyncio
async def test_search_track_success(spotify_client: SpotifyClient, respx_mock: MockRouter):
    """Teste une recherche de piste réussie."""
    respx_mock.post("https://accounts.spotify.com/api/token").mock(
        return_value=httpx.Response(200, json={"access_token": "fake_token", "expires_in": 3600})
    )
    search_response = {"tracks": {"items": [{"name": "Bohemian Rhapsody"}]}}
    respx_mock.get("https://api.spotify.com/v1/search").mock(
        return_value=httpx.Response(200, json=search_response)
    )
    result = await spotify_client.search_track("Queen")
    assert result.is_right()
    assert result.value == search_response

@pytest.mark.asyncio
async def test_search_handles_api_error(spotify_client: SpotifyClient, respx_mock: MockRouter):
    """Teste la gestion d'une erreur 500 de l'API de recherche."""
    respx_mock.post("https://accounts.spotify.com/api/token").mock(
        return_value=httpx.Response(200, json={"access_token": "fake_token", "expires_in": 3600})
    )
    respx_mock.get("https://api.spotify.com/v1/search").mock(return_value=httpx.Response(500))
    result = await spotify_client.search_track("query")
    assert result.is_left()
    result.either(
        lambda err: assert_that("Erreur de recherche Spotify" in err),
        lambda _: pytest.fail("Expected Left, got Right")
    )

@pytest.mark.asyncio
async def test_search_uses_cache(spotify_client: SpotifyClient, respx_mock: MockRouter):
    """Teste que le cache de recherche est utilisé pour les requêtes identiques."""
    respx_mock.post("https://accounts.spotify.com/api/token").mock(
        return_value=httpx.Response(200, json={"access_token": "fake_token", "expires_in": 3600})
    )
    search_api = respx_mock.get("https://api.spotify.com/v1/search").mock(
        return_value=httpx.Response(200, json={"tracks": {"items": []}})
    )
    await spotify_client.search_track("query")
    await spotify_client.search_track("query")
    assert search_api.call_count == 1
