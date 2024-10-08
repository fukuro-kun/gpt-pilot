## Telemetrie in Pythagora

Bei Pythagora sind wir bestrebt, Ihre Erfahrung und die Gesamtqualität unserer Software zu verbessern. Um dies zu erreichen, sammeln wir anonyme Telemetriedaten, die uns helfen zu verstehen, wie das Tool genutzt wird und Bereiche für Verbesserungen zu identifizieren.

### Was wir sammeln

Die Telemetriedaten, die wir sammeln, umfassen:

- **Gesamtlaufzeit**: Die Gesamtzeit, in der Pythagora aktiv und in Betrieb war.
- **Ausgeführte Befehle**: Wie viele Befehle während einer Sitzung ausgeführt wurden.
- **Entwicklungsschritte**: Die Anzahl der durchgeführten Entwicklungsschritte.
- **LLM-Anfragen**: Die Anzahl der getätigten LLM-Anfragen.
- **Benutzereingaben**: Die Anzahl der Male, die Sie Eingaben für das Tool gemacht haben.
- **Betriebssystem**: Das von Ihnen verwendete Betriebssystem (und Linux-Distribution, falls zutreffend).
- **Python-Version**: Die von Ihnen verwendete Python-Version.
- **GPT Pilot-Version**: Die von Ihnen verwendete Pythagora-Version.
- **LLM-Modell**: Das/die für die Sitzung verwendete(n) LLM-Modell(e).
- **Zeit**: Wie lange es gedauert hat, ein Projekt zu generieren.
- **Anfängliche Eingabeaufforderung**: App-Beschreibung, die zur Erstellung der App verwendet wurde (nach dem Specification Writer Agent).
- **Architektur**: Von Pythagora für die App entworfene Architektur.
- **Dokumentation**: Pythagora-Dokumentation, die während der Erstellung der App verwendet wurde.
- **Benutzer-E-Mail**: Benutzer-E-Mail (bei Verwendung der Pythagora VSCode-Erweiterung oder wenn bei der Ausführung von Pythagora über die Befehlszeile explizit angegeben).
- **Pythagora-Aufgaben/Schritte**: Informationen über die Entwicklungsaufgaben und -schritte, die Pythagora während der Codierung der App durchführt.

Alle Datenpunkte sind in [core.telemetry:Telemetry.clear_data()](../core/telemetry/__init__.py) aufgelistet.

### Wie wir diese Daten verwenden

Wir verwenden diese Daten, um:

- Die Leistung und Zuverlässigkeit von Pythagora zu überwachen.
- Nutzungsmuster zu verstehen, um unsere Entwicklung und Priorisierung von Funktionen zu leiten.
- Häufige Arbeitsabläufe zu identifizieren und die Benutzererfahrung zu verbessern.
- Die Skalierbarkeit und Effizienz unserer Sprachmodellinteraktionen sicherzustellen.

### Ihre Privatsphäre

Ihre Privatsphäre ist uns wichtig. Die gesammelten Daten dienen ausschließlich der internen Analyse und werden nicht an Dritte weitergegeben. Es werden keine personenbezogenen Informationen gesammelt, und die Telemetriedaten sind vollständig anonymisiert. Wir halten uns an bewährte Praktiken der Datensicherheit, um diese Informationen zu schützen.

### Opt-out

Wir glauben an Transparenz und Kontrolle. Wenn Sie es vorziehen, keine Telemetriedaten zu senden, können Sie dies jederzeit deaktivieren, indem Sie `telemetry.enabled` in Ihrer `~/.gpt-pilot/config.json` Konfigurationsdatei auf `false` setzen.

Nachdem Sie diese Einstellung aktualisiert haben, wird Pythagora keine Telemetriedaten mehr von Ihrem Gerät sammeln.

### Fragen und Feedback
Wenn Sie Fragen zu unseren Telemetriepraktiken haben oder Feedback geben möchten, öffnen Sie bitte ein Issue in unserem Repository. Wir freuen uns darauf, mit Ihnen in Kontakt zu treten.

Vielen Dank, dass Sie Pythagora unterstützen und uns helfen, es für alle zu verbessern.
