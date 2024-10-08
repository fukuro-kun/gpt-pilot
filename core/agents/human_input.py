from core.agents.base import BaseAgent
from core.agents.response import AgentResponse, ResponseType
from core.ui.translations import translate


class HumanInput(BaseAgent):
    agent_type = "human-input"
    display_name = translate("human_input_display_name")

    async def run(self) -> AgentResponse:
        if self.prev_response and self.prev_response.type == ResponseType.INPUT_REQUIRED:
            return await self.input_required(self.prev_response.data.get("files", []))

        return await self.human_intervention(self.step)

    async def human_intervention(self, step) -> AgentResponse:
        description = step["human_intervention_description"]

        await self.ask_question(
            translate("human_intervention_needed", description=description),
            buttons={"continue": translate("continue_button")},
            default="continue",
            buttons_only=True,
        )
        self.next_state.complete_step()
        return AgentResponse.done(self)

    async def input_required(self, files: list[dict]) -> AgentResponse:
        for item in files:
            file = item["file"]
            line = item["line"]

            # FIXME: this is an ugly hack, we shouldn't need to know how to get to VFS and
            # anyways the full path is only available for local vfs, so this is doubly wrong;
            # instead, we should just send the relative path to the extension and it should
            # figure out where its local files are and how to open it.
            full_path = self.state_manager.file_system.get_full_path(file)

            await self.send_message(translate("input_required_at", file=file, line=line))
            await self.ui.open_editor(full_path, line)
            await self.ask_question(
                translate("modify_file_instructions", file=file, line=line),
                buttons={"continue": translate("continue_button")},
                default="continue",
                buttons_only=True,
            )
        return AgentResponse.done(self)
