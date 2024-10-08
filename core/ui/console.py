# core/ui/console.py
from typing import Optional, List, Dict
import random

from prompt_toolkit.shortcuts import PromptSession

from core.log import get_logger
from core.ui.base import ProjectStage, UIBase, UIClosedError, UISource, UserInput, empty_list
from core.ui.translations import translate
from core.config.magic_words import get_thinking_logs

log = get_logger(__name__)


class PlainConsoleUI(UIBase):
    """
    UI adapter for plain (no color) console output.
    """

    async def start(self) -> bool:
        log.debug("Starting console UI")
        return True

    async def stop(self):
        log.debug("Stopping console UI")

    async def send_stream_chunk(
        self, chunk: Optional[str], *, source: Optional[UISource] = None, project_state_id: Optional[str] = None
    ):
        if chunk is None:
            # end of stream
            print("", flush=True)
        else:
            print(chunk, end="", flush=True)

    async def send_message(
        self, message: str, *, source: Optional[UISource] = None, project_state_id: Optional[str] = None
    ):
        if source:
            print(f"[{source}] {message}")
        else:
            print(message)

    async def send_key_expired(self, message: Optional[str] = None):
        if message:
            await self.send_message(message)

    async def send_app_finished(
        self,
        app_id: Optional[str] = None,
        app_name: Optional[str] = None,
        folder_name: Optional[str] = None,
    ):
        pass

    async def send_feature_finished(
        self,
        app_id: Optional[str] = None,
        app_name: Optional[str] = None,
        folder_name: Optional[str] = None,
    ):
        pass

    async def ask_question(
        self,
        question: str,
        *,
        buttons: Optional[dict[str, str]] = None,
        default: Optional[str] = None,
        buttons_only: bool = False,
        allow_empty: bool = False,
        hint: Optional[str] = None,
        initial_text: Optional[str] = None,
        source: Optional[UISource] = None,
        project_state_id: Optional[str] = None,
    ) -> UserInput:
        if source:
            print(f"[{source}] {translate(question)}")
        else:
            print(f"{translate(question)}")

        if buttons:
            for k, v in buttons.items():
                default_str = " (Standard)" if k == default else ""
                print(f"  [{k}]: {v}{default_str}")

        session = PromptSession("> ")

        while True:
            try:
                choice = await session.prompt_async(default=initial_text or "")
                choice = choice.strip()
            except KeyboardInterrupt:
                raise UIClosedError()
            if not choice and default:
                choice = default
            if buttons and choice in buttons:
                return UserInput(button=choice, text=None)
            if buttons_only:
                print(translate("please_choose_option"))
                continue
            if choice or allow_empty:
                return UserInput(button=None, text=choice)
            print(translate("provide_valid_input"))

    async def send_project_stage(self, stage: ProjectStage):
        pass

    async def send_epics_and_tasks(
        self,
        epics: List[Dict] = empty_list(),
        tasks: List[Dict] = empty_list(),
    ):
        pass

    async def send_task_progress(
        self,
        index: int,
        n_tasks: int,
        description: str,
        source: str,
        status: str,
        source_index: int = 1,
        tasks: List[Dict] = empty_list(),
    ):
        pass

    async def send_step_progress(
        self,
        index: int,
        n_steps: int,
        step: dict,
        task_source: str,
    ):
        pass

    async def send_modified_files(
        self,
        modified_files: List[Dict[str, str]],
    ):
        pass

    async def send_data_about_logs(
        self,
        data_about_logs: dict,
    ):
        pass

    async def send_run_command(self, run_command: str):
        pass

    async def open_editor(self, file: str, line: Optional[int] = None):
        pass

    async def send_project_root(self, path: str):
        pass

    async def send_project_stats(self, stats: dict):
        pass

    async def send_test_instructions(self, test_instructions: str):
        pass

    async def send_file_status(self, file_path: str, file_status: str):
        pass

    async def send_bug_hunter_status(self, status: str, num_cycles: int):
        pass

    async def generate_diff(
        self, file_path: str, file_old: str, file_new: str, n_new_lines: int = 0, n_del_lines: int = 0
    ):
        pass

    async def stop_app(self):
        pass

    async def close_diff(self):
        pass

    async def loading_finished(self):
        pass

    async def send_project_description(self, description: str):
        pass

    async def send_features_list(self, features: list[str]):
        pass

    async def import_project(self, project_dir: str):
        pass

    async def start_important_stream(self, path: str):
        thinking_logs = get_thinking_logs()
        thinking_message = random.choice(thinking_logs)
        print(thinking_message)


__all__ = ["PlainConsoleUI"]
