import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import structlog
import asyncio
import importlib
import pkgutil

def setup_logging():
    """Configure la journalisation structurée pour s'intégrer avec le logging standard."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

async def load_commands(bot):
    """Charge dynamiquement toutes les commandes du package 'commands'."""
    log = structlog.get_logger()
    commands_package = 'src.commands'
    for _, name, _ in pkgutil.iter_modules([commands_package.replace('.', '/')]):
        try:
            module = importlib.import_module(f'{commands_package}.{name}')
            if hasattr(module, 'setup'):
                await module.setup(bot)
                log.info("command.load.success", command=name)
            else:
                log.warn("command.load.no_setup", command=name)
        except Exception as e:
            log.error("command.load.error", command=name, error=str(e))

def main():
    """
    Point d'entrée principal pour démarrer le bot.
    """
    setup_logging()
    log = structlog.get_logger()

    load_dotenv()
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    if not BOT_TOKEN or BOT_TOKEN == "VOTRE_TOKEN_DISCORD_ICI":
        log.error("Le token du bot Discord est manquant ou n'a pas été configuré.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        log.info("bot.ready", user=str(bot.user), user_id=bot.user.id)
        await load_commands(bot)
        # Synchronisation des commandes slash
        try:
            synced = await bot.tree.sync()
            log.info("command.sync.success", count=len(synced))
        except Exception as e:
            log.error("command.sync.error", error=str(e))
        print(f'Connecté en tant que {bot.user}')

    @bot.event
    async def on_disconnect():
        log.warn("bot.disconnect", reason="Le bot a été déconnecté de Discord.")

    @bot.event
    async def on_resumed():
        log.info("bot.resumed", message="Le bot a repris sa session avec Discord.")

    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Gestionnaire d'erreurs global pour les commandes slash."""
        log.error(
            "app_command.error",
            command_name=interaction.command.name if interaction.command else "unknown",
            error=str(error),
            user_id=interaction.user.id,
            guild_id=interaction.guild.id if interaction.guild else "DM"
        )
        
        # Message générique pour l'utilisateur
        error_message = "Une erreur est survenue lors de l'exécution de la commande."
        if interaction.response.is_done():
            await interaction.followup.send(error_message, ephemeral=True)
        else:
            await interaction.response.send_message(error_message, ephemeral=True)

    try:
        log.info("bot.start", message="Démarrage du bot...")
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        log.error("bot.login_failure: Le token fourni est invalide.", exc_info=True)
    except Exception as e:
        log.critical("bot.critical_error", error=str(e), exc_info=True)

if __name__ == "__main__":
    main()
