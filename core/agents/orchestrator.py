from core.ui.translations import translate

import asyncio
from typing import List, Optional, Union

from core.agents.architect import Architect
from core.agents.base import BaseAgent
from core.agents.bug_hunter import BugHunter
from core.agents.code_monkey import CodeMonkey
from core.agents.developer import Developer
from core.agents.error_handler import ErrorHandler
from core.agents.executor import Executor
from core.agents.external_docs import ExternalDocumentation
from core.agents.human_input import HumanInput
from core.agents.importer import Importer
from core.agents.legacy_handler import LegacyHandler
from core.agents.problem_solver import ProblemSolver
from core.agents.response import AgentResponse, ResponseType
from core.agents.spec_writer import SpecWriter
from core.agents.task_completer import TaskCompleter
from core.agents.tech_lead import TechLead
from core.agents.tech_writer import TechnicalWriter
from core.agents.troubleshooter import Troubleshooter
from core.db.models.project_state import IterationStatus, TaskStatus
from core.log import get_logger
from core.telemetry import telemetry
from core.ui.base import ProjectStage

log = get_logger(__name__)


class Orchestrator(BaseAgent):
    """
    Hauptagent, der den Ablauf des Prozesses steuert.

    Basierend auf dem aktuellen Zustand des Projekts ruft der Orchestrator
    alle anderen Agenten auf. Er ist auch dafür verantwortlich zu bestimmen,
    wann jeder Schritt abgeschlossen ist und der Projektzustand in der Datenbank
    gespeichert werden muss.
    """

    agent_type = "orchestrator"
    display_name = "Orchestrator"

    async def run(self) -> bool:
        """
        Führt den Orchestrator-Agenten aus.

        :return: True, wenn der Orchestrator erfolgreich beendet wurde, False andernfalls.
        """
        response = None

        log.info(translate("starting_orchestrator"))

        self.executor = Executor(self.state_manager, self.ui)
        self.process_manager = self.executor.process_manager
        # self.chat = Chat() TODO

        await self.init_ui()
        await self.offline_changes_check()

        # TODO: Erwägen Sie, dies in zwei Schleifen umzugestalten; die äußere mit einer Iteration pro gespeichertem Schritt,
        # und die innere, die die Agenten für den aktuellen Schritt ausführt, bis sie fertig sind. Dies würde
        # handle_done() vereinfachen und uns ermöglichen, andere Verarbeitungen pro Schritt (z.B. Beschreiben von Dateien)
        # zwischen den Agentenausführungen durchzuführen.
        while True:
            await self.update_stats()

            agent = self.create_agent(response)

            # Falls der Agent eine Liste ist, führen Sie alle Agenten parallel aus.
            # Es kann nur ein Agententyp gleichzeitig parallel ausgeführt werden (vorerst). Siehe handle_parallel_responses().
            if isinstance(agent, list):
                tasks = [single_agent.run() for single_agent in agent]
                log.debug(
                    translate("running_multiple_agents",
                              agents=[a.__class__.__name__ for a in agent],
                              step=self.current_state.step_index)
                )
                responses = await asyncio.gather(*tasks)
                response = self.handle_parallel_responses(agent[0], responses)
            else:
                log.debug(translate("running_agent",
                                    agent=agent.__class__.__name__,
                                    step=self.current_state.step_index))
                response = await agent.run()

            if response.type == ResponseType.EXIT:
                log.debug(translate("agent_requested_exit", agent=agent.__class__.__name__))
                break

            if response.type == ResponseType.DONE:
                response = await self.handle_done(agent, response)
                continue

        # TODO: Änderungen an "next" zurücksetzen, damit sie nicht versehentlich gespeichert werden?
        return True

    def handle_parallel_responses(self, agent: BaseAgent, responses: List[AgentResponse]) -> AgentResponse:
        """
        Verarbeitet Antworten von Agenten, die parallel ausgeführt wurden.

        Diese Methode wird aufgerufen, wenn mehrere Agenten parallel ausgeführt werden,
        und sie sollte eine einzelne Antwort zurückgeben, die die kombinierten Antworten
        aller Agenten repräsentiert.

        :param agent: Der ursprüngliche Agent, der parallel ausgeführt wurde.
        :param responses: Liste der Antworten von allen Agenten.
        :return: Kombinierte Antwort.
        """
        response = AgentResponse.done(agent)
        if isinstance(agent, CodeMonkey):
            files = []
            for single_response in responses:
                if single_response.type == ResponseType.INPUT_REQUIRED:
                    files += single_response.data.get("files", [])
                    break
            if files:
                response = AgentResponse.input_required(agent, files)
            return response
        else:
            raise ValueError(translate("unhandled_parallel_agent_type", agent_type=agent.__class__.__name__))

    async def offline_changes_check(self):
        """
        Überprüft auf Änderungen außerhalb von Pythagora.

        Wenn es Änderungen gibt, fragt der Benutzer, ob er sie behalten möchte,
        und importiert sie bei Bedarf.
        """

        log.info(translate("checking_offline_changes"))
        modified_files = await self.state_manager.get_modified_files_with_content()

        if self.state_manager.workspace_is_empty():
            # HINWEIS: Dies wird derzeit bei einem neuen Projekt ausgelöst, wird aber
            # nichts tun, da keine Dateien in der Datenbank vorhanden sind.
            log.info(translate("empty_workspace_detected"))
            await self.state_manager.restore_files()
        elif modified_files:
            await self.send_message(translate("found_modified_files", count=len(modified_files)))
            await self.ui.send_modified_files(modified_files)
            hint = translate("keep_changes_hint")
            use_changes = await self.ask_question(
                question=translate("keep_changes_question"),
                buttons={
                    "yes": translate("yes_keep_changes"),
                    "no": translate("no_restore_state"),
                },
                buttons_only=True,
                hint=hint,
            )
            if use_changes.button == "yes":
                log.debug(translate("importing_offline_changes"))
                await self.import_files()
            else:
                log.debug(translate("restoring_last_state"))
                await self.state_manager.restore_files()

        log.info(translate("offline_changes_check_done"))

    async def handle_done(self, agent: BaseAgent, response: AgentResponse) -> AgentResponse:
        """
        Verarbeitet die DONE-Antwort vom Agenten und speichert den aktuellen Zustand in der Datenbank.

        Dies überprüft auch auf Dateien, die außerhalb von Pythagora erstellt oder geändert wurden,
        und importiert sie. Wenn eine der Dateien eine Eingabe vom Benutzer erfordert, wird die
        zurückgegebene Antwort den HumanInput-Agenten auslösen, um den Benutzer zur Eingabe aufzufordern.
        """
        n_epics = len(self.next_state.epics)
        n_finished_epics = n_epics - len(self.next_state.unfinished_epics)
        n_tasks = len(self.next_state.tasks)
        n_finished_tasks = n_tasks - len(self.next_state.unfinished_tasks)
        n_iterations = len(self.next_state.iterations)
        n_finished_iterations = n_iterations - len(self.next_state.unfinished_iterations)
        n_steps = len(self.next_state.steps)
        n_finished_steps = n_steps - len(self.next_state.unfinished_steps)

        log.debug(
            translate("agent_done_log",
                      agent=agent.__class__.__name__,
                      step=self.current_state.step_index,
                      finished_epics=n_finished_epics,
                      total_epics=n_epics,
                      finished_tasks=n_finished_tasks,
                      total_tasks=n_tasks,
                      finished_iterations=n_finished_iterations,
                      total_iterations=n_iterations,
                      finished_steps=n_finished_steps,
                      total_steps=n_steps)
        )
        await self.state_manager.commit()

        # Wenn es neue oder geänderte Dateien gibt, die außerhalb von Pythagora geändert wurden,
        # ist dies ein guter Zeitpunkt, um sie zum Projekt hinzuzufügen. Wenn eine von ihnen
        # INPUT_REQUIRED hat, werden wir zuerst den Benutzer bitten, die erforderliche Eingabe zu machen.
        import_files_response = await self.import_files()

        # Wenn einige der Dateien fehlende Metadaten/Beschreibungen haben, müssen diese ausgefüllt werden
        missing_descriptions = [file.path for file in self.current_state.files if not file.meta.get("description")]
        if missing_descriptions:
            log.debug(translate("files_missing_descriptions", files=', '.join(missing_descriptions)))
            return AgentResponse.describe_files(self)

        return import_files_response

    def create_agent(self, prev_response: Optional[AgentResponse]) -> Union[List[BaseAgent], BaseAgent]:
        state = self.current_state

        if prev_response:
            if prev_response.type in [ResponseType.CANCEL, ResponseType.ERROR]:
                return ErrorHandler(self.state_manager, self.ui, prev_response=prev_response)
            if prev_response.type == ResponseType.DESCRIBE_FILES:
                return CodeMonkey(self.state_manager, self.ui, prev_response=prev_response)
            if prev_response.type == ResponseType.INPUT_REQUIRED:
                # FIXME: HumanInput sollte die ganze Zeit aktiv sein und Chat/Unterbrechungen abfangen
                return HumanInput(self.state_manager, self.ui, prev_response=prev_response)
            if prev_response.type == ResponseType.IMPORT_PROJECT:
                return Importer(self.state_manager, self.ui, prev_response=prev_response)
            if prev_response.type == ResponseType.EXTERNAL_DOCS_REQUIRED:
                return ExternalDocumentation(self.state_manager, self.ui, prev_response=prev_response)
            if prev_response.type == ResponseType.UPDATE_SPECIFICATION:
                return SpecWriter(self.state_manager, self.ui, prev_response=prev_response)

        if not state.specification.description:
            if state.files:
                # Das Projekt wurde importiert, aber noch nicht analysiert
                return Importer(self.state_manager, self.ui)
            else:
                # Neues Projekt: Bitten Sie den Spec Writer, die Projektspezifikation zu verfeinern und zu speichern
                return SpecWriter(self.state_manager, self.ui, process_manager=self.process_manager)
        elif not state.specification.architecture:
            # Bitten Sie den Architekten, die Projektarchitektur zu entwerfen und Abhängigkeiten zu bestimmen
            return Architect(self.state_manager, self.ui, process_manager=self.process_manager)
        elif (
            not state.epics
            or not self.current_state.unfinished_tasks
            or (state.specification.templates and not state.files)
        ):
            # Bitten Sie den Tech Lead, das initiale Projekt oder Feature in Aufgaben aufzuteilen und Projekttemplates anzuwenden
            return TechLead(self.state_manager, self.ui, process_manager=self.process_manager)

        # Der aktuelle Aufgabenstatus muss überprüft werden, bevor Developer aufgerufen wird, da wir ihn
        # möglicherweise überspringen möchten, anstatt ihn aufzuschlüsseln
        current_task_status = state.current_task.get("status") if state.current_task else None
        if current_task_status:
            # Der Status der aktuellen Aufgabe wird zum ersten Mal gesetzt, nachdem die Aufgabe vom Benutzer überprüft wurde
            log.info(translate("current_task_status", status=current_task_status))
            if current_task_status == TaskStatus.REVIEWED:
                # Benutzer hat die Aufgabe überprüft, rufen Sie TechnicalWriter auf, um zu sehen, ob die Dokumentation aktualisiert werden muss
                return TechnicalWriter(self.state_manager, self.ui)
            elif current_task_status in [TaskStatus.DOCUMENTED, TaskStatus.SKIPPED]:
                # Aufgabe ist vollständig erledigt oder übersprungen, rufen Sie TaskCompleter auf, um sie als abgeschlossen zu markieren
                return TaskCompleter(self.state_manager, self.ui)

        if not state.steps and not state.iterations:
            # Bitten Sie den Developer, die aktuelle Aufgabe in ausführbare Schritte aufzuteilen
            return Developer(self.state_manager, self.ui)

        if state.current_step:
            # Führen Sie den nächsten Schritt in der Aufgabe aus
            # TODO: Dies kann in Zukunft parallelisiert werden
            return self.create_agent_for_step(state.current_step)

        if state.unfinished_iterations:
            current_iteration_status = state.current_iteration["status"]
            if current_iteration_status == IterationStatus.HUNTING_FOR_BUG:
                # Auslösen des Bug Hunters, um die Suche zu beginnen
                return BugHunter(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.START_PAIR_PROGRAMMING:
                # Pythagora kann das Problem nicht lösen, also beginnen wir mit Pair Programming
                return BugHunter(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.AWAITING_LOGGING:
                # Lassen Sie den Developer Logs implementieren, die für das Debugging benötigt werden
                return Developer(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.AWAITING_BUG_FIX:
                # Lassen Sie den Developer den Bug-Fix für das Debugging implementieren
                return Developer(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.IMPLEMENT_SOLUTION:
                # Lassen Sie den Developer die vom Benutzer angeforderte "Änderung" implementieren
                return Developer(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.AWAITING_USER_TEST:
                # Lassen Sie den Bug Hunter den Menschen bitten, den Bug-Fix zu testen
                return BugHunter(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.AWAITING_BUG_REPRODUCTION:
                # Lassen Sie den Bug Hunter den Menschen bitten, den Bug zu reproduzieren
                return BugHunter(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.FIND_SOLUTION:
                # Finden Sie eine Lösung für das Iterationsproblem
                return Troubleshooter(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.PROBLEM_SOLVER:
                # Rufen Sie den Problem Solver auf, wenn der Benutzer sagt "Ich stecke in einer Schleife fest"
                return ProblemSolver(self.state_manager, self.ui)
            elif current_iteration_status == IterationStatus.NEW_FEATURE_REQUESTED:
                # Rufen Sie Spec Writer auf, um die vom Benutzer angeforderte "Änderung" zur Projektspezifikation hinzuzufügen
                return SpecWriter(self.state_manager, self.ui)

        # Wir haben gerade die Aufgabe beendet, rufen Sie Troubleshooter auf, um den Benutzer um eine Überprüfung zu bitten
        return Troubleshooter(self.state_manager, self.ui)

    def create_agent_for_step(self, step: dict) -> Union[List[BaseAgent], BaseAgent]:
        step_type = step.get("type")
        if step_type == "save_file":
            steps = self.current_state.get_steps_of_type("save_file")
            parallel = []
            for step in steps:
                parallel.append(CodeMonkey(self.state_manager, self.ui, step=step))
            return parallel
        elif step_type == "command":
            return self.executor.for_step(step)
        elif step_type == "human_intervention":
            return HumanInput(self.state_manager, self.ui, step=step)
        elif step_type == "review_task":
            return LegacyHandler(self.state_manager, self.ui, data={"type": "review_task"})
        elif step_type == "create_readme":
            return TechnicalWriter(self.state_manager, self.ui)
        else:
            raise ValueError(translate("unknown_step_type", step_type=step_type))

    async def import_files(self) -> Optional[AgentResponse]:
        imported_files, removed_paths = await self.state_manager.import_files()
        if not imported_files and not removed_paths:
            return None

        if imported_files:
            log.info(translate("imported_files", files=', '.join(f.path for f in imported_files)))
        if removed_paths:
            log.info(translate("removed_files", files=', '.join(removed_paths)))

        input_required_files: list[dict[str, int]] = []
        for file in imported_files:
            for line in self.state_manager.get_input_required(file.content.content):
                input_required_files.append({"file": file.path, "line": line})

        if input_required_files:
            # Dies wird den HumanInput-Agenten auslösen, um den Benutzer aufzufordern, die erforderlichen Änderungen vorzunehmen
            # Wenn der Benutzer etwas ändert (die "erforderlichen Änderungen" entfernt), wird die Datei erneut importiert.
            return AgentResponse.input_required(self, input_required_files)

        # Speichern Sie die neu importierte Datei
        log.debug(translate("committing_imported_files", step=self.current_state.step_index))
        await self.state_manager.commit()
        return None

    async def init_ui(self):
        await self.ui.send_project_root(self.state_manager.get_full_project_root())
        await self.ui.loading_finished()

        if self.current_state.epics:
            await self.ui.send_project_stage(ProjectStage.CODING)
            if len(self.current_state.epics) > 2:
                # Wir möchten nur vorherige Features senden, d.h. das aktuelle und das initiale Projekt (erstes Epic) ausschließen
                await self.ui.send_features_list([e["description"] for e in self.current_state.epics[1:-1]])

        elif self.current_state.specification.description:
            await self.ui.send_project_stage(ProjectStage.ARCHITECTURE)
        else:
            await self.ui.send_project_stage(ProjectStage.DESCRIPTION)

        if self.current_state.specification.description:
            await self.ui.send_project_description(self.current_state.specification.description)

    async def update_stats(self):
        if self.current_state.steps and self.current_state.current_step:
            source = self.current_state.current_step.get("source")
            source_steps = self.current_state.get_last_iteration_steps()
            await self.ui.send_step_progress(
                source_steps.index(self.current_state.current_step) + 1,
                len(source_steps),
                self.current_state.current_step,
                source,
            )

        total_files = 0
        total_lines = 0
        for file in self.current_state.files:
            total_files += 1
            total_lines += len(file.content.content.splitlines())

        telemetry.set("num_files", total_files)
        telemetry.set("num_lines", total_lines)

        stats = telemetry.get_project_stats()
        await self.ui.send_project_stats(stats)
