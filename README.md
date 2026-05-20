# Device Watchdog

Custom Integration für Home Assistant / HACS.

## Funktion

- Entitäten im Config Flow auswählen.
- Pro Entität konfigurierbare Überwachungszeit.
- Wenn innerhalb des Timeouts keine Zustandsänderung oder Aktualisierung eintritt, geht der Sammelalarm an.
- Fehlende Entitäten sind über das Attribut `failed_entities` auslesbar.

## Installation

1. Repository in deinen Home-Assistant-Ordner unter `custom_components/device_watchdog/` kopieren.
2. Home Assistant neu starten.
3. Integration über die UI hinzufügen.
4. Entitäten auswählen und Timeouts setzen.

## Nutzung

Der Alarm wird über folgende Entitäten sichtbar:

- `binary_sensor.device_watchdog`
- `sensor.device_watchdog_summary`

Das Attribut `failed_entities` enthält die betroffenen Entitäten.

## Beispiel Automation

```yaml
alias: Device Watchdog Alarm
trigger:
  - platform: state
    entity_id: binary_sensor.device_watchdog
    to: "on"
action:
  - service: notify.notify
    data:
      message: "Watchdog Alarm: {{ state_attr('binary_sensor.device_watchdog', 'failed_entities') }}"
```

## HACS

Diese Integration ist als Custom Integration für HACS vorgesehen.