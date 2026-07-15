# Day modes

![](https://img.shields.io/github/v/release/ticstyle/Day-Modes?style=for-the-badge&color=blue)
![](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue?style=for-the-badge&logo=home-assistant)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/ticstyle/Day-Modes/pipeline.yml?branch=main&job=hassfest&label=Hassfest&style=for-the-badge)](https://github.com/ticstyle/Day-Modes/actions/workflows/pipeline.yml)
[![HACS Validation](https://img.shields.io/github/actions/workflow/status/ticstyle/Day-Modes/pipeline.yml?branch=main&job=hacs&label=HACS&style=for-the-badge)](https://github.com/ticstyle/Day-Modes/actions/workflows/pipeline.yml)
[![Ruff / Format](https://img.shields.io/github/actions/workflow/status/ticstyle/Day-Modes/pipeline.yml?branch=main&job=sync_and_format&label=Ruff%20%2F%20Format&style=for-the-badge)](https://github.com/ticstyle/Day-Modes/actions/workflows/pipeline.yml)
[![Mypy](https://img.shields.io/github/actions/workflow/status/ticstyle/Day-Modes/pipeline.yml?branch=main&job=mypy&label=Mypy&style=for-the-badge)](https://github.com/ticstyle/Day-Modes/actions/workflows/pipeline.yml)
![](https://img.shields.io/github/license/ticstyle/Day-Modes?style=for-the-badge)
![](https://img.shields.io/badge/dynamic/json?style=for-the-badge&color=41BDF5&logo=home-assistant&label=installs&url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.Day-Modes.total)
![](https://img.shields.io/github/issues/ticstyle/Day-Modes?style=for-the-badge&color=orange)

A modern Home Assistant custom integration that creates a dynamic device and sensor ecosystem to automatically track and cycle through custom day modes (Morning, Day, Evening, Night, Away) based on a personalized weekday schedule matrix, zone occupancy, and automated vacation sensing.

To add this integration, please add the custom repository `[https://github.com/ticstyle/Day-Modes](https://github.com/ticstyle/Day-Modes)` to HACS in your Home Assistant setup.

## 🌐 Supported Languages / Språk
The integration natively defaults to English for backend operations but includes full frontend translations for Swedish. Thanks to native State Translations, state values will display localized text (e.g., *Morgon*, *Dag*, *Borta*, *Semesterläge*) seamlessly in your UI while preserving standard raw values for backend tracking.

## ✨ Features
* **Device-Centric Architecture:** Instead of creating loose, disconnected entities, the integration generates a clean **Day modes** Device container grouping all relevant cycle state and configuration data together.
* **📅 Matrix Weekday Scheduling:** Configure unique time schedules for different days (e.g., separate weekday and weekend routines, or individual custom schedules for every single day) via a clean, unified flow.
* **🌴 Smart Vacation Mode & Time Delay:** Delay your Morning mode transition to a dedicated late-start time when you want a sleep-in. Fully automates via an optional Home Assistant calendar tracking system with native support for manual dashboard overrides.
* **🔄 Dynamic Calendar Sensors:** Exposes dedicated configuration entities that automatically adjust their states to show **today's active time boundaries**, making dashboard presentation effortless.
* **👥 Dynamic Presence Tracking:** Automatically forces an `away` state whenever your designated home zone becomes empty, and instantly restores the correct time-based operational mode the second someone returns.
* **⚙️ On-the-Fly Reconfiguration:** Built with a recursive multi-step Options Flow. Easily adjust your scheduled times, regroup weekdays, change your vacation calendar, or target a completely different zone at any point via the UI cogwheel.
* **100% Async Engine:** Uses Home Assistant's event-driven architecture to subscribe to precise state and time changes, ensuring zero unnecessary CPU polling cycles.

## 🚀 Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=Day-Modes&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `day_modes` folder from the [latest release](https://github.com/ticstyle/Day-Modes/releases/latest) to the `custom_components` folder inside your Home Assistant configuration directory.

## ⚙️ Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)]([https://my.home-assistant.io/redirect/config_flow_start/?domain=day_modes](https://my.home-assistant.io/redirect/config_flow_start/?domain=day_modes))

Add the integration via the Home Assistant User Interface. Go to **Settings -> Devices & Services -> Add Integration** and search for **Day modes**. 

During setup, you will select the active days for your baseline profile and optionally select an existing Home Assistant calendar to drive your vacation tracking. Any days left unselected will automatically cascade into custom follow-up setup steps until your entire week matrix is fully mapped.

## 📊 Available Entities
Once configured, the integration automatically registers a device named **Day modes** containing the following 8 entities:

| Entity ID | Name in UI | State Example | Description |
| :--- | :--- | :--- | :--- |
| `sensor.day_modes` | Current mode | `day` *(Dag)* | Core operational state tracking. Returns `morning`, `day`, `evening`, `night`, or `away`. |
| `sensor.day_modes_morning_time` | Morning start time | `06:00` | Displays the active start time threshold for Morning mode **today** (dynamically shifts if vacation mode is active). |
| `sensor.day_modes_day_time` | Day start time | `09:00` | Displays the active start time threshold for Day mode **today**. |
| `sensor.day_modes_evening_time` | Evening start time | `20:00` | Displays the active start time threshold for Evening mode **today**. |
| `sensor.day_modes_night_time` | Night start time | `23:00` | Displays the active start time threshold for Night mode **today**. |
| `sensor.day_modes_vacation_calendar` | Vacation calendar | `calendar.personal` | Displays the name of the tracked calendar or `Not Configured`. |
| `switch.day_modes_vacation_mode` | Vacation mode | `on` *(På)* | Controls whether the vacation mode time override is currently active. |
| `time.day_modes_vacation_morning_time` | Vacation morning time | `08:00` | An editable time selector to dynamically set your preferred vacation sleep-in time right from the UI. |

### Entity Attributes
The core state sensor (`sensor.day_modes`) explicitly exposes your entire configuration layout matrix within its metadata attributes:
* `tracked_zone`: The target zone entity being monitored (e.g., `zone.home`).
* `schedules`: A structured list containing all your configured profiles, including the assigned days and specific time variables for each group.

---

## 💡 Lovelace Dashboard Examples

### Example 1: Simple Status Card
Because all setup parameters for the current day are first-class entities, building a quick status layout is dead simple and no longer requires nested attribute lookups:

```yaml
type: markdown
title: "House Status"
content: >
  Current House Mode: **{{ states('sensor.day_modes') }}**
  
  {% if is_state('sensor.day_modes', 'away') %}
    🏠 The house is currently in eco-mode while everyone is out.
  {% else %}
    ⏰ Tonight's night mode schedule is set to trigger at {{ states('sensor.day_modes_night_time') }}.
  {% endif %}
```

### Example 2: Full Week Matrix Timetable Card
To render a beautiful, clean overview card that automatically displays all your distinct weekly profiles and schedules, use the structured data inside the core sensor attributes:

```yaml
type: markdown
content: |-
  📅 Day Mode Schedules
    {% set profiles = state_attr('sensor.day_modes', 'schedules') %}
    {% if profiles %}
      {% for p in profiles %}
        ### 🗓️ {{ p.days | join(', ') }}
        | 🌅 Morning | **{{ p.morning }}** |
        | ☀️ Day | **{{ p.day }}** |
        | 🌆 Evening | **{{ p.evening }}** |
        | 🌙 Night | **{{ p.night }}** |
        {% if not loop.last %}---{% endif %}
      {% endfor %}
    {% else %}
      No schedules configured.
    {% endif %}
```

### Example 3: Vacation Mode Controller Card
An elegant control station using standard Home Assistant cards to easily manage your holiday sleep-in offsets and keep an eye on automation bindings:

```yaml
type: entities
title: "🌴 Holiday & Vacation Control"
show_header_toggle: false
entities:
  - entity: switch.day_modes_vacation_mode
    name: "Activate Vacation Mode"
    icon: mdi:airplane
  - entity: time.day_modes_vacation_morning_time
    name: "Sleep-in Wake Up Time"
  - entity: sensor.day_modes_vacation_calendar
    name: "Monitored Calendar Source"
```
