import os
import httpx
import base64
import time
from pydantic import BaseModel, Field
import structlog
from pymonad.either import Either, Left, Right

log = structlog.get_logger()

class SpotifyToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    expires_at: float = Field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Vérifie si le jeton a expiré."""
        return time.time() > self.expires_at + self.expires_in - 60  # Marge de 60s

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            raise ValueError("Spotify client_id et client_secret ne peuvent pas être vides.")
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: SpotifyToken | None = None
        self._search_cache = {}  # Cache simple en mémoire pour les recherches
        self._api_url = "https://api.spotify.com/v1"
        self._auth_url = "https://accounts.spotify.com/api/token"

    async def _get_token(self) -> Either[str, str]:
        """Récupère un jeton d'accès, le renouvelle si nécessaire."""
        if self._token and not self._token.is_expired():
            return Right(self._token.access_token)

        log.info("spotify.auth.request", message="Demande d'un nouveau jeton d'accès Spotify.")
        auth_header = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self._auth_url, headers=headers, data=data)
                response.raise_for_status()
                token_data = response.json()
                self._token = SpotifyToken(**token_data)
                log.info("spotify.auth.success", message="Nouveau jeton Spotify obtenu.")
                return Right(self._token.access_token)
            except httpx.HTTPStatusError as e:
                error_msg = f"Impossible de s'authentifier auprès de Spotify. Status: {e.response.status_code}"
                log.error("spotify.auth.error", error=error_msg, response=e.response.text)
                return Left(error_msg)

    async def search_track(self, query: str, limit: int = 5) -> Either[str, dict]:
        """Recherche une piste sur Spotify, en utilisant un cache."""
        cache_key = f"{query}:{limit}"
        if cache_key in self._search_cache:
            log.info("spotify.search.cache_hit", query=query)
            return Right(self._search_cache[cache_key])

        token_either = await self._get_token()
        if token_either.is_left():
            return Left(token_either.value)

        token = token_either.value
        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": query, "type": "track", "limit": limit}
        
        async with httpx.AsyncClient() as client:
            try:
                log.info("spotify.search.request", query=query, limit=limit)
                response = await client.get(f"{self._api_url}/search", headers=headers, params=params)
                response.raise_for_status()
                results = response.json()
                self._search_cache[cache_key] = results
                log.info("spotify.search.success", query=query)
                return Right(results)
            except httpx.HTTPStatusError as e:
                error_msg = f"Erreur de recherche Spotify. Status: {e.response.status_code}"
                log.error("spotify.search.error", error=error_msg, response=e.response.text)
                return Left(error_msg)

