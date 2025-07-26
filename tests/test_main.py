import pytest
from unittest.mock import patch, MagicMock
import discord # Importez discord pour pouvoir mocker ses erreurs

# Il est préférable d'importer le module que vous testez
from src import main as bot_main

@pytest.fixture
def mock_bot(mocker):
    """Fixture pour mocker le bot commands.Bot."""
    # Mocker la classe commands.Bot
    mock_bot_class = mocker.patch('discord.ext.commands.Bot')
    # Créer une instance mockée
    mock_instance = MagicMock()
    # Configurer la classe mockée pour retourner notre instance mockée
    mock_bot_class.return_value = mock_instance
    
    # Mocker également le chargement des commandes pour isoler le test de main
    mocker.patch('src.main.load_commands', new_callable=mocker.AsyncMock)
    
    return mock_instance

def test_main_starts_bot_with_token(mock_bot, monkeypatch):
    """
    Vérifie que la fonction main initialise et lance le bot
    avec le jeton provenant des variables d'environnement.
    """
    # Arrange: prépare l'environnement du test
    fake_token = "un_faux_jeton_pour_le_test"
    monkeypatch.setenv("DISCORD_BOT_TOKEN", fake_token)

    # Act: exécute la fonction à tester
    bot_main.main()

    # Assert: vérifie les résultats
    # 1. Vérifie que le bot a été lancé avec le bon jeton
    mock_bot.run.assert_called_once_with(fake_token)

def test_main_logs_error_on_login_failure(mock_bot, monkeypatch, caplog):
    """
    Vérifie qu'une erreur de type LoginFailure est correctement journalisée (loggée).
    """
    # Arrange
    fake_token = "un_jeton_invalide"
    monkeypatch.setenv("DISCORD_BOT_TOKEN", fake_token)

    # Simule une erreur de connexion de la part de la librairie discord.py
    mock_bot.run.side_effect = discord.errors.LoginFailure("Token invalide")

    # Act
    bot_main.main()

    # Assert
    # Vérifie que le message d'erreur attendu est bien présent dans les logs
    assert "bot.login_failure: Le token fourni est invalide." in caplog.text

def test_main_returns_if_token_is_missing(monkeypatch, caplog):
    """
    Vérifie que la fonction main retourne (s'arrête) si le jeton est manquant.
    """
    # Arrange
    # S'assure que la variable d'environnement n'est pas définie
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)

    # Act
    result = bot_main.main()

    # Assert
    assert "Le token du bot Discord est manquant" in caplog.text
    assert result is None # La fonction doit retourner None

