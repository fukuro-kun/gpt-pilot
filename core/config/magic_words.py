# core/config/magic_words.py
from typing import Dict, List
from core.config import get_config

PROBLEM_IDENTIFIED = "PROBLEM_IDENTIFIED"
ADD_LOGS = "ADD_LOGS"
THINKING_LOGS: Dict[str, List[str]] = {
    "en": [
        "Pythagora is crunching the numbers...",
        "Pythagora is deep in thought...",
        "Pythagora is analyzing your request...",
        "Pythagora is brewing up a solution...",
        "Pythagora is putting the pieces together...",
        "Pythagora is working its magic...",
        "Pythagora is crafting the perfect response...",
        "Pythagora is decoding your query...",
        "Pythagora is on the case...",
        "Pythagora is computing an answer...",
        "Pythagora is sorting through the data...",
        "Pythagora is gathering insights...",
        "Pythagora is making connections...",
        "Pythagora is tuning the algorithms...",
        "Pythagora is piecing together the puzzle...",
        "Pythagora is scanning the possibilities...",
        "Pythagora is engineering a response...",
        "Pythagora is building the answer...",
        "Pythagora is mapping out a solution...",
        "Pythagora is figuring this out for you...",
        "Pythagora is thinking hard right now...",
        "Pythagora is working for you, so relax!",
        "Pythagora might take some time to figure this out...",
    ],
    "de": [
        "Pythagora kaut gerade die Zahlen durch...",
        "Pythagora ist in tiefes Nachdenken versunken...",
        "Pythagora analysiert Ihre Anfrage...",
        "Pythagora braut eine Lösung...",
        "Pythagora setzt die Teile zusammen...",
        "Pythagora lässt seine Magie wirken...",
        "Pythagora erstellt die perfekte Antwort...",
        "Pythagora entschlüsselt Ihre Anfrage...",
        "Pythagora ist an der Sache dran...",
        "Pythagora berechnet eine Antwort...",
        "Pythagora sortiert die Daten...",
        "Pythagora sammelt Erkenntnisse...",
        "Pythagora stellt Verbindungen her...",
        "Pythagora stimmt die Algorithmen ab...",
        "Pythagora setzt das Puzzle zusammen...",
        "Pythagora scannt die Möglichkeiten...",
        "Pythagora konstruiert eine Antwort...",
        "Pythagora baut die Antwort auf...",
        "Pythagora zeichnet eine Lösung...",
        "Pythagora findet das für Sie heraus...",
        "Pythagora denkt gerade angestrengt nach...",
        "Pythagora arbeitet für Sie, also entspannen Sie sich!",
        "Pythagora braucht vielleicht etwas Zeit, um das herauszufinden...",
    ]
}

def get_thinking_logs() -> List[str]:
    config = get_config()
    lang = getattr(config, 'language', 'en')
    return THINKING_LOGS.get(lang, THINKING_LOGS['en'])
