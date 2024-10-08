from uuid import uuid4

from core.agents.base import BaseAgent
from core.agents.convo import AgentConvo
from core.agents.response import AgentResponse, ResponseType
from core.db.models import Complexity
from core.llm.parser import JSONParser
from core.log import get_logger
from core.telemetry import telemetry
from core.templates.example_project import EXAMPLE_PROJECT_DESCRIPTION

log = get_logger(__name__)

MAX_PROJECT_LINES = 10000


class Importer(BaseAgent):
    agent_type = "importer"
    display_name = "Project Analyist"

    async def run(self) -> AgentResponse:
        if self.prev_response and self.prev_response.type == ResponseType.IMPORT_PROJECT:
            # Called by SpecWriter to start the import process
            await self.start_import_process()
            return AgentResponse.describe_files(self)

        await self.analyze_project()
        return AgentResponse.done(self)

    async def start_import_process(self):
        # TODO: Send a signal to the UI to copy the project files to workspace
        project_root = self.state_manager.get_full_project_root()
        await self.ui.import_project(project_root)
        await self.send_message(
            translate("experimental_feature_warning", max_lines=MAX_PROJECT_LINES)
        )

        await self.ask_question(
            translate("copy_files_instruction", project_root=project_root),
            allow_empty=False,
            buttons={
                "continue": "Fortfahren",
            },
            buttons_only=True,
            default="continue",
        )

        imported_files, _ = await self.state_manager.import_files()
        imported_lines = sum(len(f.content.content.splitlines()) for f in imported_files)
        if imported_lines > MAX_PROJECT_LINES:
            await self.send_message(
                translate("project_size_warning", loc=imported_lines)
            )
        await self.state_manager.commit()

    async def analyze_project(self):
        llm = self.get_llm(stream_output=True)

        self.send_message(translate("inspecting_files"))

        convo = AgentConvo(self).template("get_entrypoints")
        llm_response = await llm(convo, parser=JSONParser())
        relevant_files = [f for f in self.current_state.files if f.path in llm_response]

        self.send_message(translate("analyzing_project"))

        convo = AgentConvo(self).template(
            "analyze_project", relevant_files=relevant_files, example_spec=EXAMPLE_PROJECT_DESCRIPTION
        )
        llm_response = await llm(convo)

        spec = self.current_state.specification.clone()
        spec.description = llm_response
        self.next_state.specification = spec
        self.next_state.epics = [
            {
                "id": uuid4().hex,
                "name": "Import project",
                "description": "Import an existing project into Pythagora",
                "tasks": [],
                "completed": True,
                "test_instructions": None,
                "source": "app",
                "summary": None,
                "complexity": Complexity.HARD if len(self.current_state.files) > 5 else Complexity.SIMPLE,
            }
        ]

        n_lines = sum(len(f.content.content.splitlines()) for f in self.current_state.files)
        await telemetry.trace_code_event(
            "existing-project",
            {
                "num_files": len(self.current_state.files),
                "num_lines": n_lines,
                "description": llm_response,
            },
        )
