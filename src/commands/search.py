import os
import discord
from discord import app_commands
import structlog
from pymonad.either import Either

from src.clients.spotify import SpotifyClient

log = structlog.get_logger()

# Initialisation du client Spotify
spotify_client = SpotifyClient(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
)

@app_commands.command(name="search", description="Recherche un morceau sur Spotify.")
async def search(interaction: discord.Interaction, query: str):
    """Exécute la recherche et affiche les résultats."""
    await interaction.response.defer(thinking=True)

    search_result: Either[str, dict] = await spotify_client.search_track(query)

    if search_result.is_left():
        error_message = search_result.value
        log.error("search.command.error", error=error_message)
        await interaction.followup.send(f"Une erreur est survenue lors de la recherche : {error_message}", ephemeral=True)
        return

    results = search_result.value
    if not results.get('tracks') or not results['tracks']['items']:
        await interaction.followup.send("Aucun résultat trouvé.", ephemeral=True)
        return

    # Créer un embed pour afficher les résultats
    embed = discord.Embed(
        title=f"Résultats de la recherche pour '{query}'",
        color=discord.Color.green()
    )

    for i, item in enumerate(results['tracks']['items'][:5], 1):
        track_name = item['name']
        artist_name = ', '.join(artist['name'] for artist in item['artists'])
        track_url = item['external_urls']['spotify']
        embed.add_field(
            name=f"{i}. {track_name} - {artist_name}",
            value=f"[Écouter sur Spotify]({track_url})",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)


async def setup(bot: discord.Client):
    """Enregistre la commande auprès du bot."""
    bot.tree.add_command(search)
