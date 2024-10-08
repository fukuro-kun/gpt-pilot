# Entwicklerdokumentation für GPT Pilot

## 1. Einführung

GPT Pilot ist ein KI-gestütztes Softwareentwicklungstool, das den Entwicklungsprozess automatisiert und verbessert. Es nutzt verschiedene KI-Agenten, um den gesamten Entwicklungszyklus von der Spezifikation bis zur Implementierung und Fehlerbehebung zu unterstützen.

### 1.1 Projektziele

- Generierung vollständiger, produktionsreifer Anwendungen
- Zusammenarbeit mit Entwicklern zur Sicherstellung hoher Codequalität
- Skalierbarkeit für verschiedene Projektgrößen

### 1.2 Hauptfunktionen

- KI-gesteuerte Projektplanung und Architekturentwurf
- Automatische Code-Generierung und -Implementierung
- Interaktive Fehlerbehebung und Problemlösung
- Dynamische Anpassung an Benutzeranforderungen

## 2. Systemarchitektur

GPT Pilot basiert auf einer modularen Architektur mit folgenden Hauptkomponenten:

### 2.1 Kernkomponenten

1. **Agents**: KI-Agenten für spezifische Entwicklungsaufgaben
2. **CLI**: Kommandozeilen-Schnittstelle
3. **Config**: Konfigurationsverwaltung
4. **DB**: Datenbankinteraktion (SQLAlchemy ORM)
5. **Disk**: Dateisystemoperationen
6. **LLM**: Integration von Language Models (aktuell OpenAI, Anthropic, Ollama)
7. **Log**: Logging-System
8. **Proc**: Prozess- und Befehlsausführung
9. **State**: Projekt-Zustandsverwaltung
10. **Telemetry**: Anonyme Datenerfassung (opt-out möglich)
11. **Templates**: Projekt-Vorlagen
12. **UI**: Benutzeroberflächen-Adapter (Konsole, VS Code)

### 2.2 Datenfluss

1. Benutzereingabe (Projektbeschreibung)
2. Spezifikationsverfeinerung (Specification Writer Agent)
3. Architekturentwurf (Architect Agent)
4. Aufgabenplanung (Tech Lead Agent)
5. Implementierungsplanung (Developer Agent)
6. Code-Generierung (Code Monkey Agent)
7. Code-Überprüfung (Reviewer Agent)
8. Problemlösung (Troubleshooter, Debugger Agents)
9. Dokumentation (Technical Writer Agent)

## 3. Hauptkomponenten im Detail

### 3.1 Agents (core/agents/)

Jeder Agent ist für einen spezifischen Aspekt des Entwicklungsprozesses zuständig:

- **Architect** (architect.py): Entwirft die Projektarchitektur
  - Wählt Technologien und Frameworks
  - Erstellt grundlegende Systemstruktur
- **Developer** (developer.py): Plant die Implementierung von Aufgaben
  - Bricht Aufgaben in umsetzbare Schritte herunter
  - Definiert Testanweisungen
- **CodeMonkey** (code_monkey.py): Implementiert tatsächlichen Code
  - Generiert Code basierend auf Entwicklervorgaben
  - Führt kleinere Code-Anpassungen durch
- **SpecWriter** (spec_writer.py): Verwaltet die Projektspezifikation
  - Verfeinert initiale Projektbeschreibungen
  - Aktualisiert Spezifikationen bei Änderungen
- **TechLead** (tech_lead.py): Verantwortlich für die Projektplanung
  - Erstellt Epics und Tasks
  - Priorisiert Entwicklungsaufgaben

Weitere wichtige Agents:
- **Orchestrator** (orchestrator.py): Koordiniert den gesamten Entwicklungsprozess
- **BugHunter** (bug_hunter.py): Identifiziert und analysiert Fehler
- **Troubleshooter** (troubleshooter.py): Löst komplexe Probleme
- **TechnicalWriter** (tech_writer.py): Erstellt Projektdokumentation

### 3.2 LLM Integration (core/llm/)

Aktuell unterstützte LLM-Provider:
- OpenAI (openai_client.py)
- Anthropic (anthropic_client.py)
- Ollama über (openai_client.py)

Hauptklassen:
- `BaseLLMClient` (base.py): Basisklasse für LLM-Clients
- `Convo` (convo.py): Verwaltet Konversationen mit LLMs

### 3.3 Konfiguration (core/config/)

- `Config` (__init__.py): Zentrale Konfigurationsklasse
- Unterstützt verschiedene LLM-Provider und deren Einstellungen
- Verwaltet globale Projekt-Einstellungen

### 3.4 UI (core/ui/)

- `UIBase` (base.py): Basisklasse für UI-Adapter
- `ConsoleUI` (console.py): Konsolen-basierte Benutzeroberfläche
- `IPCClient` (ipc_client.py): Schnittstelle für VS Code-Erweiterung

## 4. Datenmodelle (core/db/models/)

Wichtige SQLAlchemy-Modelle:

- `Project` (project.py): Repräsentiert ein Projekt
  - Attribute: id, name, created_at, folder_name
  - Beziehungen: branches
- `Branch` (branch.py): Repräsentiert einen Projekt-Branch
  - Attribute: id, project_id, name
  - Beziehungen: project, states
- `ProjectState` (project_state.py): Repräsentiert einen Projektzustand
  - Attribute: id, branch_id, step_index, epics, tasks, steps, iterations
  - Beziehungen: branch, files, specification
- `Specification` (specification.py): Enthält die Projektspezifikation
  - Attribute: id, description, architecture, system_dependencies, package_dependencies
- `File` (file.py): Repräsentiert eine Projektdatei
  - Attribute: id, project_state_id, path
  - Beziehungen: project_state, content

## 5. Entwicklungsprozess

1. **Projektinitialisierung**
   - Benutzer gibt Projektbeschreibung ein
   - SpecWriter verfeinert die Spezifikation

2. **Architekturentwurf**
   - Architect wählt Technologien und erstellt Systemstruktur
   - TechLead plant initiale Epics und Tasks

3. **Implementierungsphase**
   - Developer bricht Tasks in Schritte herunter
   - CodeMonkey implementiert Code
   - Continuous Integration/Testing

4. **Überprüfung und Iteration**
   - Reviewer überprüft generierten Code
   - BugHunter und Troubleshooter beheben Probleme
   - Iterative Verbesserung und Erweiterung

5. **Dokumentation und Abschluss**
   - TechnicalWriter erstellt Projektdokumentation
   - Finale Tests und Benutzer-Feedback

## 6. Kernfunktionalitäten

### 6.1 Projekt-Zustandsverwaltung

- `StateManager` (core/state/state_manager.py) verwaltet Projektzustände
- Ermöglicht Versionierung und Rollback von Projektänderungen

### 6.2 Code-Generierung und -Modifikation

- CodeMonkey Agent generiert und modifiziert Code
- Nutzt LLM für kontextbezogene Code-Erstellung

### 6.3 Interaktive Problemlösung

- BugHunter und Troubleshooter Agents für Fehlerbehebung
- Interaktiver Prozess mit Benutzer-Feedback

### 6.4 Dynamische Aufgabenplanung

- TechLead passt Projektplan basierend auf Fortschritt und Feedback an
- Kontinuierliche Neubewertung und Priorisierung von Tasks

## 7. Entwicklerwerkzeuge und -praktiken

### 7.1 Logging und Debugging

- Zentrales Logging-System (core/log/__init__.py)
- Debug-Modus für detaillierte Ausführungsinformationen

### 7.2 Testing

- Unit-Tests für einzelne Komponenten
- Integrationstests für Agent-Interaktionen
- Mocking von LLM-Antworten für reproduzierbare Tests

### 7.3 Code-Stil und Konventionen

- PEP 8 für Python-Code-Stil
- Typisierung mit Python Type Hints
- Docstrings für alle Klassen und Methoden

## 8. Erweiterung und Anpassung

### 8.1 Hinzufügen neuer Agents

1. Neue Agent-Klasse in core/agents/ erstellen
2. Von BaseAgent erben und notwendige Methoden implementieren
3. Agent in Orchestrator integrieren

### 8.2 Unterstützung neuer LLM-Provider

1. Neuen Client in core/llm/ implementieren
2. BaseLLMClient erweitern
3. Konfiguration in Config-Klasse aktualisieren

### 8.3 Erweiterung der Projektvorlagen

1. Neue Vorlage in core/templates/ erstellen
2. Template-Klasse implementieren und in registry.py registrieren

## 9. Bekannte Einschränkungen und zukünftige Verbesserungen

- Aktuelle Abhängigkeit von externen LLM-Providern
- Begrenzte Unterstützung für große, komplexe Projekte
- Potenzial für Verbesserungen in der Code-Qualitätssicherung
- Möglichkeit zur Erweiterung der unterstützten Programmiersprachen und Frameworks

## 10. Beitrag zum Projekt

- Fork des Repositories
- Feature-Branches für neue Funktionen oder Bugfixes
- Umfassende Tests für alle Änderungen
- Pull Requests mit klarer Beschreibung der Änderungen
- Code-Reviews durch Kernentwickler

## 11. Ressourcen und Links

- Projekt-Repository: [GitHub-Link]
- Dokumentation: [Docs-Link]
- Issue-Tracker: [Issues-Link]
- Community-Forum: [Forum-Link]

## 12. Detaillierte Komponenten-Analyse

### 12.1 Agents - Erweiterte Funktionalität

#### Orchestrator (core/agents/orchestrator.py)
Der Orchestrator ist das Herzstück des Entwicklungsprozesses. Hier ein Beispiel für seine Hauptschleife:

```python
class Orchestrator(BaseAgent):
    async def run(self) -> bool:
        while True:
            await self.update_stats()
            agent = self.create_agent(response)

            if isinstance(agent, list):
                tasks = [single_agent.run() for single_agent in agent]
                responses = await asyncio.gather(*tasks)
                response = self.handle_parallel_responses(agent[0], responses)
            else:
                response = await agent.run()

            if response.type == ResponseType.EXIT:
                break
            if response.type == ResponseType.DONE:
                response = await self.handle_done(agent, response)

        return True

    def create_agent(self, prev_response: Optional[AgentResponse]) -> Union[List[BaseAgent], BaseAgent]:
        state = self.current_state
        if prev_response:
            # Logik zur Auswahl des nächsten Agenten basierend auf der vorherigen Antwort
        elif not state.specification.description:
            return SpecWriter(self.state_manager, self.ui, process_manager=self.process_manager)
        elif not state.specification.architecture:
            return Architect(self.state_manager, self.ui, process_manager=self.process_manager)
        elif not state.epics or not self.current_state.unfinished_tasks:
            return TechLead(self.state_manager, self.ui, process_manager=self.process_manager)
        # Weitere Bedingungen...
```

#### Developer (core/agents/developer.py)
Der Developer-Agent ist verantwortlich für die Aufschlüsselung von Tasks in konkrete Implementierungsschritte:

```python
class Developer(RelevantFilesMixin, BaseAgent):
    async def breakdown_current_task(self) -> AgentResponse:
        current_task = self.current_state.current_task

        await self.send_message("Thinking about how to implement this task ...")

        llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME, stream_output=True)
        convo = AgentConvo(self).template(
            "breakdown",
            task=current_task,
            iteration=None,
            current_task_index=current_task_index,
            docs=self.current_state.docs,
        )
        response: str = await llm(convo)

        await self.get_relevant_files(None, response)

        # Aktualisieren des Task-Status und Aufschlüsselung in Schritte
        self.next_state.tasks[current_task_index] = {
            **current_task,
            "instructions": response,
        }
        self.next_state.flag_tasks_as_modified()

        # Parsing der Schritte
        llm = self.get_llm(PARSE_TASK_AGENT_NAME)
        convo.assistant(response).template("parse_task").require_schema(TaskSteps)
        parsed_steps: TaskSteps = await llm(convo, parser=JSONParser(TaskSteps), temperature=0)

        self.set_next_steps(parsed_steps, source)
        return AgentResponse.done(self)
```

### 12.2 LLM-Integration - Erweitertes Beispiel

Die LLM-Integration ist zentral für die Funktionsweise von GPT Pilot. Hier ein detaillierteres Beispiel der BaseLLMClient-Klasse:

```python
class BaseLLMClient:
    def __init__(self, config: LLMConfig, stream_handler: Optional[Callable] = None, error_handler: Optional[Callable] = None):
        self.config = config
        self.stream_handler = stream_handler
        self.error_handler = error_handler

    async def __call__(self, convo: Convo, temperature: Optional[float] = None, parser: Optional[Callable] = None, max_retries: int = 3, json_mode: bool = False) -> Tuple[Any, LLMRequestLog]:
        request_log = LLMRequestLog(
            provider=self.provider,
            model=self.config.model,
            temperature=temperature or self.config.temperature,
            prompts=convo.prompt_log,
        )

        remaining_retries = max_retries
        while True:
            if remaining_retries == 0:
                raise APIError("Maximum retries reached")

            remaining_retries -= 1
            try:
                response, prompt_tokens, completion_tokens = await self._make_request(convo, temperature, json_mode)

                request_log.prompt_tokens += prompt_tokens
                request_log.completion_tokens += completion_tokens

                if parser:
                    try:
                        parsed_response = parser(response)
                        return parsed_response, request_log
                    except ValueError as err:
                        convo.assistant(response)
                        convo.user(f"Error parsing response: {err}. Please output your response EXACTLY as requested.")
                        continue
                else:
                    return response, request_log

            except Exception as e:
                # Fehlerbehandlung...

    async def _make_request(self, convo: Convo, temperature: Optional[float], json_mode: bool) -> tuple[str, int, int]:
        raise NotImplementedError()
```

### 12.3 Datenbank-Modelle - Erweiterte Beziehungen

Die Datenbankmodelle in GPT Pilot sind komplex und stark miteinander verknüpft. Hier ein erweitertes Beispiel für das `ProjectState`-Modell:

```python
class ProjectState(Base):
    __tablename__ = "project_states"
    __table_args__ = (
        UniqueConstraint("prev_state_id"),
        UniqueConstraint("branch_id", "step_index"),
        {"sqlite_autoincrement": True},
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    branch_id: Mapped[UUID] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"))
    prev_state_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("project_states.id", ondelete="CASCADE"))
    specification_id: Mapped[int] = mapped_column(ForeignKey("specifications.id"))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    step_index: Mapped[int] = mapped_column(default=1, server_default="1")
    epics: Mapped[list[dict]] = mapped_column(default=list)
    tasks: Mapped[list[dict]] = mapped_column(default=list)
    steps: Mapped[list[dict]] = mapped_column(default=list)
    iterations: Mapped[list[dict]] = mapped_column(default=list)
    relevant_files: Mapped[Optional[list[str]]] = mapped_column(default=None)
    modified_files: Mapped[dict] = mapped_column(default=dict)
    docs: Mapped[Optional[list[dict]]] = mapped_column(default=None)
    run_command: Mapped[Optional[str]] = mapped_column()
    action: Mapped[Optional[str]] = mapped_column()

    branch: Mapped["Branch"] = relationship(back_populates="states", lazy="selectin")
    prev_state: Mapped[Optional["ProjectState"]] = relationship(
        back_populates="next_state",
        remote_side=[id],
        single_parent=True,
        lazy="raise",
        cascade="delete",
    )
    next_state: Mapped[Optional["ProjectState"]] = relationship(back_populates="prev_state", lazy="raise")
    files: Mapped[list["File"]] = relationship(
        back_populates="project_state",
        lazy="selectin",
        cascade="all,delete-orphan",
    )
    specification: Mapped["Specification"] = relationship(back_populates="project_states", lazy="selectin")
    llm_requests: Mapped[list["LLMRequest"]] = relationship(back_populates="project_state", cascade="all", lazy="raise")
    user_inputs: Mapped[list["UserInput"]] = relationship(back_populates="project_state", cascade="all", lazy="raise")
    exec_logs: Mapped[list["ExecLog"]] = relationship(back_populates="project_state", cascade="all", lazy="raise")

    @property
    def unfinished_steps(self) -> list[dict]:
        return [step for step in self.steps if not step.get("completed")]

    @property
    def current_step(self) -> Optional[dict]:
        li = self.unfinished_steps
        return li[0] if li else None

    # Weitere Eigenschaften und Methoden...
```

### 12.4 Konfigurationsmanagement

Die Konfiguration in GPT Pilot wird über die `Config`-Klasse in `core/config/__init__.py` verwaltet. Hier ein erweitertes Beispiel:

```python
class Config(_StrictModel):
    llm: dict[LLMProvider, ProviderConfig] = Field(
        default={
            LLMProvider.OPENAI: ProviderConfig(),
            LLMProvider.ANTHROPIC: ProviderConfig(),
        }
    )
    agent: dict[str, AgentLLMConfig] = Field(
        default={
            DEFAULT_AGENT_NAME: AgentLLMConfig(),
            CHECK_LOGS_AGENT_NAME: AgentLLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-3-5-sonnet-20240620",
                temperature=0.5,
            ),
            CODE_MONKEY_AGENT_NAME: AgentLLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4-0125-preview",
                temperature=0.0,
            ),
            # Weitere Agent-Konfigurationen...
        }
    )
    prompt: PromptConfig = PromptConfig()
    log: LogConfig = LogConfig()
    db: DBConfig = DBConfig()
    ui: UIConfig = PlainUIConfig()
    fs: FileSystemConfig = FileSystemConfig()

    def llm_for_agent(self, agent_name: str = "default") -> LLMConfig:
        agent_name = agent_name if agent_name in self.agent else "default"
        agent_config = self.agent[agent_name]
        provider_config = self.llm[agent_config.provider]
        return LLMConfig.from_provider_and_agent_configs(provider_config, agent_config)

    def all_llms(self) -> list[LLMConfig]:
        return [self.llm_for_agent(agent) for agent in self.agent]
```

## 13. Fortgeschrittene Konzepte und Techniken

### 13.1 Asynchrone Programmierung

GPT Pilot macht extensiven Gebrauch von asynchroner Programmierung. Hier ein Beispiel für die asynchrone Verarbeitung von LLM-Anfragen:

```python
async def process_llm_requests(requests: List[str], llm: BaseLLMClient):
    async def process_request(request: str):
        convo = Convo().user(request)
        response, _ = await llm(convo)
        return response

    tasks = [process_request(req) for req in requests]
    responses = await asyncio.gather(*tasks)
    return responses
```

### 13.2 Zustandsmanagement

Das Zustandsmanagement ist kritisch für die Funktionalität von GPT Pilot. Die `StateManager`-Klasse in `core/state/state_manager.py` ist dafür verantwortlich:

```python
class StateManager:
    async def commit(self) -> ProjectState:
        if self.next_state is None:
            raise ValueError("No state to commit.")

        await self.commit_with_retry()

        self.current_state = self.next_state
        self.current_session.add(self.next_state)
        self.next_state = await self.current_state.create_next_state()

        for f in self.current_state.files:
            await f.awaitable_attrs.content

        telemetry.inc("num_steps")

        return self.current_state

    async def import_files(self) -> tuple[list[File], list[File]]:
        known_files = {file.path: file for file in self.current_state.files}
        files_in_workspace = set()
        imported_files = []
        removed_files = []

        for path in self.file_system.list():
            files_in_workspace.add(path)
            content = self.file_system.read(path)
            saved_file = known_files.get(path)

            if saved_file and saved_file.content.content == content:
                continue

            hash = self.file_system.hash_string(content)
            file_content = await FileContent.store(self.current_session, hash, content)
            file = self.next_state.save_file(path, file_content, external=True)
            imported_files.append(file)

        for path, file in known_files.items():
            if path not in files_in_workspace:
                next_state_file = self.next_state.get_file_by_path(path)
                self.next_state.files.remove(next_state_file)
                removed_files.append(file.path)

        return imported_files, removed_files
```

### 13.3 Prompt-Engineering

Effektives Prompt-Engineering ist entscheidend für die Leistung von GPT Pilot. Hier ein Beispiel für einen komplexen Prompt aus `core/agents/spec_writer.py`:

```python
ANALYZE_SPEC_PROMPT = """
You are a seasoned software architect tasked with refining and expanding a project specification. The user has provided an initial description, but it may lack detail or clarity. Your job is to analyze this description and generate a more comprehensive specification.

Initial Project Description:
{spec}

Please provide a detailed analysis and expansion of this project description, considering the following aspects:
1. Core Functionality: What are the main features and capabilities of the proposed system?
2. User Interface: What type of interface (CLI, GUI, Web, etc.) would be most appropriate, and why?
3. Data Management: What kind of data will the system handle, and how should it be stored?
4. Integration Requirements: Are there any external systems or APIs that need to be integrated?
5. Performance Considerations: Are there any specific performance requirements or potential bottlenecks?
6. Security Concerns: What security measures should be implemented?
7. Scalability: How might the system need to scale in the future?
8. Potential Challenges: What are the main technical or logistical challenges in implementing this project?

Please structure your response as a detailed project specification, expanding on the initial description while maintaining its original intent. Add any additional features or considerations that you believe would enhance the project.

Refined Project Specification:
"""

async def analyze_spec(self, spec: str) -> str:
    llm = self.get_llm(SPEC_WRITER_AGENT_NAME, stream_output=True)
    convo = AgentConvo(self).template(ANALYZE_SPEC_PROMPT, spec=spec)
    response: str = await llm(convo)
    return response.strip()
```

## 14. Leistungsoptimierung und Skalierung

### 14.1 Caching-Strategien

GPT Pilot implementiert verschiedene Caching-Strategien zur Optimierung der Leistung. Hier ein Beispiel für einen In-Memory-Cache:

```python
class InMemoryCache(BaseCache):
    def __init__(self):
        self._cache = {}

    def lookup(self, prompt: str, llm_string: str) -> Optional[str]:
        return self._cache.get((prompt, llm_string))

    def update(self, prompt: str, llm_string: str, return_val: str) -> None:
        self._cache[(prompt, llm_string)] = return_val

# Verwendung
cache = InMemoryCache()
llm_with_cache = CustomLLM(cache=cache)
```

### 14.2 Parallelisierung von Aufgaben

Für rechenintensive Aufgaben nutzt GPT Pilot Parallelisierung:

```python
async def parallel_code_generation(tasks: List[dict], llm: BaseLLMClient):
    async def generate_code(task: dict):
        convo = Convo().template("code_generation", task=task)
        code, _ = await llm(convo)
        return task['id'], code

    code_tasks = [generate_code(task) for task in tasks]
    results = await asyncio.gather(*code_tasks)
    return dict(results)
```

## 15. Sicherheit und Fehlerbehandlung

### 15.1 Sichere Handhabung von Benutzereingaben

GPT Pilot implementiert strenge Validierung und Bereinigung von Benutzereingaben:

```python
def sanitize_input(input: str) -> str:
    # Entfernen potenziell gefährlicher Zeichen
    sanitized = re.sub(r'[;<>&`|]', '', input)
    # Escape von Shellzeichen
    sanitized = shlex.quote(sanitized)
    return sanitized

# Verwendung
user_input = get_user_input()
safe_input = sanitize_input(user_input)
```

### 15.2 Fehlerbehandlung und Wiederherstellung

GPT Pilot implementiert robuste Fehlerbehandlung und Wiederherstellungsmechanismen:

```python
class ErrorHandler:
    @staticmethod
    async def handle_llm_error(error: Exception, state_manager: StateManager):
        if isinstance(error, APIError):
            await state_manager.rollback()
            # Benachrichtigung an den Benutzer
            await notify_user("LLM API Error occurred. Rolling back to last stable state.")
        elif isinstance(error, TimeoutError):
            # Wiederholungslogik
            retry_count = 0
            while retry_count < 3:
                try:
                    # Wiederholen der Operation
                    break
                except TimeoutError:
                    retry_count += 1
            if retry_count == 3:
                await state_manager.rollback()
                await notify_user("Repeated timeouts occurred. Please check your connection.")
        else:
            # Unerwarteter Fehler
            log_error(error)
            await state_manager.rollback()
            await notify_user("An unexpected error occurred. The system has been rolled back.")


            ## Projektstruktur

            ```
            gpt-pilot/
            ├── core/
            │   ├── agents/                 # Verschiedene KI-Agenten für spezifische Aufgaben
            │   │   ├── architect.py        # Entwurf der Projektarchitektur
            │   │   ├── base.py             # Basisklasse für Agenten
            │   │   ├── bug_hunter.py       # Fehlersuche und -behebung
            │   │   ├── code_monkey.py      # Code-Implementierung
            │   │   ├── developer.py        # Allgemeine Entwicklungsaufgaben
            │   │   ├── error_handler.py    # Fehlerbehandlung
            │   │   ├── executor.py         # Befehlsausführung
            │   │   ├── external_docs.py    # Verwaltung externer Dokumentation
            │   │   ├── human_input.py      # Behandlung von Benutzereingaben
            │   │   ├── importer.py         # Import von bestehenden Projekten
            │   │   ├── legacy_handler.py   # Behandlung von Legacy-Code
            │   │   ├── orchestrator.py     # Koordination aller Agenten
            │   │   ├── problem_solver.py   # Lösung komplexer Probleme
            │   │   ├── spec_writer.py      # Erstellung von Projektspezifikationen
            │   │   ├── task_completer.py   # Abschluss von Aufgaben
            │   │   ├── tech_lead.py        # Technische Leitung und Planung
            │   │   ├── tech_writer.py      # Technische Dokumentation
            │   │   └── troubleshooter.py   # Fehlerbehebung und Problemlösung
            │   ├── cli/                    # Kommandozeilen-Interface
            │   │   ├── helpers.py          # Hilfsfunktionen für CLI
            │   │   └── main.py             # Haupteinstiegspunkt für CLI
            │   ├── config/                 # Konfigurationsverwaltung
            │   │   ├── env_importer.py     # Import von Umgebungsvariablen
            │   │   ├── magic_words.py      # Spezielle Schlüsselwörter
            │   │   ├── user_settings.py    # Benutzerspezifische Einstellungen
            │   │   └── version.py          # Versionsverwaltung
            │   ├── db/                     # Datenbankoperationen
            │   │   ├── migrations/         # Datenbankmigrationen
            │   │   ├── models/             # Datenbankmodelle
            │   │   ├── session.py          # Datenbanksitzungsverwaltung
            │   │   ├── setup.py            # Datenbankeinrichtung
            │   │   └── v0importer.py       # Importer für ältere Datenbankversionen
            │   ├── disk/                   # Dateisystemoperationen
            │   │   ├── ignore.py           # Ignorieren bestimmter Dateien/Ordner
            │   │   └── vfs.py              # Virtuelles Dateisystem
            │   ├── llm/                    # LLM-Integration
            │   │   ├── anthropic_client.py # Anthropic API-Client
            │   │   ├── azure_client.py     # Azure OpenAI API-Client
            │   │   ├── base.py             # Basis-LLM-Client
            │   │   ├── convo.py            # Konversationsmanagement
            │   │   ├── groq_client.py      # Groq API-Client
            │   │   ├── openai_client.py    # OpenAI API-Client
            │   │   ├── parser.py           # Parsing von LLM-Antworten
            │   │   ├── prompt.py           # Prompt-Verwaltung
            │   │   └── request_log.py      # Logging von LLM-Anfragen
            │   ├── log/                    # Logging-Funktionalität
            │   │   └── __init__.py         # Logging-Konfiguration
            │   ├── proc/                   # Prozessverwaltung
            │   │   ├── exec_log.py         # Logging von Befehlsausführungen
            │   │   └── process_manager.py  # Verwaltung von Subprozessen
            │   ├── state/                  # Zustandsverwaltung
            │   │   └── state_manager.py    # Verwaltung des Projektzustands
            │   ├── telemetry/              # Telemetrie und Datenerfassung
            │   │   └── __init__.py         # Telemetrie-Implementierung
            │   ├── templates/              # Projekttemplates
            │   │   ├── base.py             # Basis-Templateklasse
            │   │   ├── example_project.py  # Beispielprojekt-Template
            │   │   ├── javascript_react.py # React-Projekt-Template
            │   │   ├── node_express_mongoose.py # Node.js-Express-MongoDB-Template
            │   │   ├── react_express.py    # React-Express-Template
            │   │   ├── registry.py         # Template-Registry
            │   │   └── render.py           # Template-Rendering
            │   └── ui/                     # Benutzeroberflächen
            │       ├── base.py             # Basis-UI-Klasse
            │       ├── console.py          # Konsolen-UI
            │       ├── ipc_client.py       # IPC-Client für VSCode-Erweiterung
            │       └── virtual.py          # Virtuelles UI für Tests
            ├── docs/
            │   └── TELEMETRY.md            # Dokumentation zur Telemetrie-Funktionalität
            ├── tests/
            │   ├── agents/                 # Tests für Agent-Komponenten
            │   ├── cli/                    # Tests für CLI-Komponenten
            │   ├── config/                 # Tests für Konfigurationskomponenten
            │   ├── db/                     # Tests für Datenbankkomponenten
            │   ├── disk/                   # Tests für Dateisystemkomponenten
            │   ├── integration/            # Integrationstests
            │   ├── llm/                    # Tests für LLM-Komponenten
            │   ├── log/                    # Tests für Logging-Komponenten
            │   ├── proc/                   # Tests für Prozessverwaltungskomponenten
            │   ├── state/                  # Tests für Zustandsverwaltungskomponenten
            │   ├── telemetry/              # Tests für Telemetrie-Komponenten
            │   ├── templates/              # Tests für Template-Komponenten
            │   └── ui/                     # Tests für UI-Komponenten
            ├── .gitignore                  # Git-Ignore-Datei
            ├── LICENSE                     # Lizenzinformationen
            ├── main.py                     # Haupteinstiegspunkt der Anwendung
            ├── pyproject.toml              # Python-Projektdatei
            ├── README.md                   # Projektbeschreibung und Dokumentation
            └── requirements.txt            # Python-Abhängigkeiten
            ```
