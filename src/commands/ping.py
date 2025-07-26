import discord
from discord import app_commands

@app_commands.command(name="ping", description="Vérifie la latence du bot.")
async def ping(interaction: discord.Interaction):
    """Une commande simple qui répond avec la latence du bot."""
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Pong ! Latence : {latency} ms.")

async def setup(bot: discord.Client):
    """Fonction setup pour enregistrer la commande auprès du bot."""
    bot.tree.add_command(ping)
