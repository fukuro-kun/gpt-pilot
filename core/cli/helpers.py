# core/cli/helpers.py
import json
import os
import os.path
import sys
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from core.config import Config, LLMProvider, LocalIPCConfig, ProviderConfig, UIAdapter, get_config, loader
from core.config.env_importer import import_from_dotenv
from core.config.version import get_version
from core.db.session import SessionManager
from core.db.setup import run_migrations
from core.log import setup
from core.state.state_manager import StateManager
from core.ui.base import UIBase
from core.ui.console import PlainConsoleUI
from core.ui.ipc_client import IPCClientUI
from core.ui.virtual import VirtualUI
from core.ui.translations import translate

def parse_llm_endpoint(value: str) -> Optional[tuple[LLMProvider, str]]:
    """
    Parst die --llm-endpoint Kommandozeilenoption.

    Optionssyntax ist: --llm-endpoint <provider>:<url>

    :param value: Argumentwert.
    :return: Tuple mit LLM-Provider und URL, oder None, wenn die Option nicht angegeben wurde.
    """
    if not value:
        return None

    parts = value.split(":", 1)
    if len(parts) != 2:
        raise ArgumentTypeError(translate("invalid_llm_endpoint_format"))

    try:
        provider = LLMProvider(parts[0])
    except ValueError as err:
        raise ArgumentTypeError(f"Nicht unterstützter LLM-Provider: {err}")
    url = urlparse(parts[1])
    if url.scheme not in ("http", "https"):
        raise ArgumentTypeError(translate("invalid_llm_endpoint_url", url=parts[1]))

    return provider, url.geturl()


def parse_llm_key(value: str) -> Optional[tuple[LLMProvider, str]]:
    """
    Parst die --llm-key Kommandozeilenoption.

    Optionssyntax ist: --llm-key <provider>:<key>

    :param value: Argumentwert.
    :return: Tuple mit LLM-Provider und Schlüssel, oder None, wenn die Option nicht angegeben wurde.
    """
    if not value:
        return None

    parts = value.split(":", 1)
    if len(parts) != 2:
        raise ArgumentTypeError(translate("invalid_llm_key_format"))

    try:
        provider = LLMProvider(parts[0])
    except ValueError as err:
        raise ArgumentTypeError(f"Nicht unterstützter LLM-Provider: {err}")

    return provider, parts[1]


def parse_arguments() -> Namespace:
    """
    Parst Kommandozeilenargumente.

    Verfügbare Argumente:
        --help: Zeigt die Hilfemeldung an
        --config: Pfad zur Konfigurationsdatei
        --show-config: Gibt die Standardkonfiguration auf stdout aus
        --default-config: Gibt die Konfiguration auf stdout aus
        --level: Log-Level (debug,info,warning,error,critical)
        --database: Datenbank-URL
        --local-ipc-port: Lokaler IPC-Port für die Verbindung
        --local-ipc-host: Lokaler IPC-Host für die Verbindung
        --version: Zeigt die Version an und beendet
        --list: Listet alle Projekte auf
        --list-json: Listet alle Projekte im JSON-Format auf
        --project: Lädt ein bestimmtes Projekt
        --branch: Lädt einen bestimmten Branch
        --step: Lädt einen bestimmten Schritt in einem Projekt/Branch
        --llm-endpoint: Verwendet einen spezifischen API-Endpunkt für den angegebenen Provider
        --llm-key: Verwendet einen spezifischen LLM-Schlüssel für den angegebenen Provider
        --import-v0: Importiert Daten aus einer v0 (gpt-pilot) Datenbank mit dem angegebenen Pfad
        --email: E-Mail-Adresse des Benutzers, falls angegeben
        --extension-version: Version der VSCode-Erweiterung, falls verwendet
        --no-check: Deaktiviert die initiale LLM-API-Prüfung
    :return: Geparste Argumente als Objekt.
    """
    version = get_version()

    parser = ArgumentParser()
    parser.add_argument("--config", help=translate("config_help"), default="config.json")
    parser.add_argument("--show-config", help=translate("show_config_help"), action="store_true")
    parser.add_argument("--level", help=translate("level_help"), required=False)
    parser.add_argument("--database", help=translate("database_help"), required=False)
    parser.add_argument("--local-ipc-port", help=translate("local_ipc_port_help"), type=int, required=False)
    parser.add_argument("--local-ipc-host", help=translate("local_ipc_host_help"), default="localhost", required=False)
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("--list", help=translate("list_help"), action="store_true")
    parser.add_argument("--list-json", help=translate("list_json_help"), action="store_true")
    parser.add_argument("--project", help=translate("project_help"), type=UUID, required=False)
    parser.add_argument("--branch", help=translate("branch_help"), type=UUID, required=False)
    parser.add_argument("--step", help=translate("step_help"), type=int, required=False)
    parser.add_argument("--delete", help=translate("delete_help"), type=UUID, required=False)
    parser.add_argument(
        "--llm-endpoint",
        help=translate("llm_endpoint_help"),
        type=parse_llm_endpoint,
        action="append",
        required=False,
    )
    parser.add_argument(
        "--llm-key",
        help=translate("llm_key_help"),
        type=parse_llm_key,
        action="append",
        required=False,
    )
    parser.add_argument(
        "--import-v0",
        help=translate("import_v0_help"),
        required=False,
    )
    parser.add_argument("--email", help=translate("email_help"), required=False)
    parser.add_argument("--extension-version", help=translate("extension_version_help"), required=False)
    parser.add_argument("--no-check", help=translate("no_check_help"), action="store_true")
    return parser.parse_args()


def load_config(args: Namespace) -> Optional[Config]:
    """
    Lädt die Pythagora JSON-Konfigurationsdatei und wendet Kommandozeilenargumente an.

    :param args: Kommandozeilenargumente (mindestens `config` muss vorhanden sein).
    :return: Konfigurationsobjekt oder None, wenn die Konfiguration nicht geladen werden konnte.
    """
    if not os.path.isfile(args.config):
        imported = import_from_dotenv(args.config)
        if not imported:
            print(f"Konfigurationsdatei nicht gefunden: {args.config}; verwende Standard", file=sys.stderr)
            return get_config()

    try:
        config = loader.load(args.config)
    except ValueError as err:
        print(f"Fehler beim Parsen der Konfigurationsdatei {args.config}: {err}", file=sys.stderr)
        return None

    if args.level:
        config.log.level = args.level.upper()

    if args.database:
        config.db.url = args.database

    if args.local_ipc_port:
        config.ui = LocalIPCConfig(port=args.local_ipc_port, host=args.local_ipc_host)

    if args.llm_endpoint:
        for provider, endpoint in args.llm_endpoint:
            if provider not in config.llm:
                config.llm[provider] = ProviderConfig()
            config.llm[provider].base_url = endpoint

    if args.llm_key:
        for provider, key in args.llm_key:
            if provider not in config.llm:
                config.llm[provider] = ProviderConfig()
            config.llm[provider].api_key = key

    try:
        Config.model_validate(config)
    except ValueError as err:
        print(f"Konfigurationsfehler: {err}", file=sys.stderr)
        return None

    return config


async def list_projects_json(db: SessionManager):
    """
    Listet alle Projekte in der Datenbank im JSON-Format auf.
    """
    sm = StateManager(db)
    projects = await sm.list_projects()

    data = []
    for project in projects:
        last_updated = None
        p = {
            "name": project.name,
            "id": project.id.hex,
            "branches": [],
        }
        for branch in project.branches:
            b = {
                "name": branch.name,
                "id": branch.id.hex,
                "steps": [],
            }
            for state in branch.states:
                if not last_updated or state.created_at > last_updated:
                    last_updated = state.created_at
                s = {
                    "name": state.action or f"Schritt #{state.step_index}",
                    "step": state.step_index,
                }
                b["steps"].append(s)
            if b["steps"]:
                b["steps"][-1]["name"] = translate("latest_step")
            p["branches"].append(b)
        p["updated_at"] = last_updated.isoformat() if last_updated else None
        data.append(p)

    print(json.dumps(data, indent=2))


async def list_projects(db: SessionManager):
    """
    Listet alle Projekte in der Datenbank auf.
    """
    sm = StateManager(db)
    projects = await sm.list_projects()

    print(translate("available_projects", count=len(projects)))
    for project in projects:
        print(f"* {project.name} ({project.id})")
        for branch in project.branches:
            last_step = max(state.step_index for state in branch.states)
            print(translate("branch_info", name=branch.name, id=branch.id, last_step=last_step))


async def load_project(
    sm: StateManager,
    project_id: Optional[UUID] = None,
    branch_id: Optional[UUID] = None,
    step_index: Optional[int] = None,
) -> bool:
    """
    Lädt ein Projekt aus der Datenbank.

    :param sm: State Manager.
    :param project_id: Projekt-ID (optional, lädt den letzten Schritt im Hauptbranch).
    :param branch_id: Branch-ID (optional, lädt den letzten Schritt im Branch).
    :param step_index: Schritt-Index (optional, lädt den Zustand beim angegebenen Schritt).
    :return: True, wenn das Projekt erfolgreich geladen wurde, False sonst.
    """
    step_txt = f" {translate('step')} {step_index}" if step_index else ""

    if branch_id:
        project_state = await sm.load_project(branch_id=branch_id, step_index=step_index)
        if project_state:
            return True
        else:
            print(translate("branch_not_found", branch_id=branch_id, step_txt=step_txt), file=sys.stderr)
            return False

    elif project_id:
        project_state = await sm.load_project(project_id=project_id, step_index=step_index)
        if project_state:
            return True
        else:
            print(translate("project_not_found", project_id=project_id, step_txt=step_txt), file=sys.stderr)
            return False

    return False


async def delete_project(db: SessionManager, project_id: UUID) -> bool:
    """
    Löscht ein Projekt aus der Datenbank.

    :param sm: State Manager.
    :param project_id: Projekt-ID.
    :return: True, wenn das Projekt gelöscht wurde, False sonst.
    """

    sm = StateManager(db)
    return await sm.delete_project(project_id)


def show_config():
    """
    Gibt die aktuelle Konfiguration auf stdout aus.
    """
    cfg = get_config()
    print(cfg.model_dump_json(indent=2))


def init() -> tuple[UIBase, SessionManager, Namespace]:
    """
    Initialisiert die Anwendung.

    Lädt die Konfiguration, richtet Logging und UI ein, initialisiert die Datenbank
    und führt Datenbankmigrationen durch.

    :return: Tuple mit UI, DB-Sitzungsmanager, Dateimanager und Kommandozeilenargumenten.
    """
    args = parse_arguments()
    config = load_config(args)
    if not config:
        return (None, None, args)

    setup(config.log, force=True)

    if config.ui.type == UIAdapter.IPC_CLIENT:
        ui = IPCClientUI(config.ui)
    elif config.ui.type == UIAdapter.VIRTUAL:
        ui = VirtualUI(config.ui.inputs)
    else:
        ui = PlainConsoleUI()

    run_migrations(config.db)
    db = SessionManager(config.db)

    return (ui, db, args)


__all__ = ["parse_arguments", "load_config", "list_projects_json", "list_projects", "load_project", "init"]
