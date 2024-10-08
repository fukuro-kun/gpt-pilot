from core.agents.base import BaseAgent
from core.agents.convo import AgentConvo
from core.agents.response import AgentResponse
from core.db.models.project_state import TaskStatus
from core.log import get_logger
from core.ui.base import success_source
from core.ui.translations import translate

log = get_logger(__name__)


class TechnicalWriter(BaseAgent):
    agent_type = "tech-writer"
    display_name = translate("tech_writer_display_name")

    async def run(self) -> AgentResponse:
        """
        Führt den TechnicalWriter-Agenten aus.

        :return: AgentResponse
        """
        n_tasks = len(self.current_state.tasks)
        # Die aktuelle Aufgabe gilt zu diesem Zeitpunkt noch als "unbeendet", aber für die Zwecke dieses Agenten
        # wollen wir sie als "beendet" betrachten, weshalb wir 1 von der Gesamtzahl der unbeendeten Aufgaben abziehen
        n_unfinished = len(self.current_state.unfinished_tasks) - 1

        if n_unfinished in [n_tasks // 2, 1]:
            # Halbzeit des anfänglichen Projekts und bei der letzten Aufgabe
            await self.send_congratulations()
            await self.create_readme()

        self.next_state.action = translate("create_readme_action")
        self.next_state.set_current_task_status(TaskStatus.DOCUMENTED)
        return AgentResponse.done(self)

    async def send_congratulations(self):
        """
        Sendet Glückwünsche und Projektstatistiken an den Benutzer.
        """
        n_tasks = len(self.current_state.tasks)
        if not n_tasks:
            log.warning(translate("no_tasks_found"))
            return

        n_unfinished = len(self.current_state.unfinished_tasks) - 1
        n_finished = n_tasks - n_unfinished
        pct_finished = int(n_finished / n_tasks * 100)
        n_files = len(self.current_state.files)
        n_lines = sum(len(f.content.content.splitlines()) for f in self.current_state.files)
        await self.ui.send_message(
            "\n\n".join(
                [
                    translate("congratulations_message", pct_finished=pct_finished),
                    translate("project_stats", n_files=n_files, n_lines=n_lines),
                    translate("creating_documentation"),
                ]
            ),
            source=success_source,
        )

    async def create_readme(self):
        """
        Erstellt die README.md-Datei für das Projekt.
        """
        await self.send_message(translate("creating_readme"))

        llm = self.get_llm(stream_output=True)
        convo = AgentConvo(self).template("create_readme")
        llm_response: str = await llm(convo)
        await self.state_manager.save_file("README.md", llm_response)
