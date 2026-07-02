# Day modes

![](https://img.shields.io/github/v/release/ticstyle/Day-Modes?style=for-the-badge&color=blue)
![](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue?style=for-the-badge&logo=home-assistant)
![](https://img.shields.io/github/license/ticstyle/Day-Modes?style=for-the-badge)
![](https://img.shields.io/github/downloads/ticstyle/Day-Modes/total?style=for-the-badge&color=green)
![](https://img.shields.io/github/issues/ticstyle/Day-Modes?style=for-the-badge&color=orange)

A modern Home Assistant custom integration that creates a dynamic device and sensor ecosystem to automatically track and cycle through custom day modes (Morning, Day, Evening, Night, Away) based on your personalized schedule and zone occupancy.

To add this integration, please add the custom repository `https://github.com/ticstyle/Day-Modes` to HACS in your Home Assistant setup.

## 🌐 Supported Languages / Språk
The integration natively defaults to English for backend operations but includes full frontend translations for Swedish. Thanks to native State Translations, state values will display localized text (e.g., *Morgon*, *Dag*, *Borta*) seamlessly in your UI while preserving standard raw values for backend tracking.

## ✨ Features
* **Device-Centric Architecture:** Instead of creating loose, disconnected entities, the integration generates a clean **Day modes** Device container grouping all relevant cycle state and configuration data together.
* **Granular Configuration Sensors:** Exposes 4 dedicated configuration entities showing your active time boundaries, making dashboard presentation effortless without advanced template coding.
* **Dynamic Presence Tracking:** Automatically forces an `away` state whenever your designated home zone becomes empty, and instantly restores the correct time-based operational mode the second someone returns.
* **On-the-Fly Reconfiguration:** Built with a full Options Flow. Easily adjust your scheduled times using a clean `HH:MM` interface or target a completely different zone at any point via the UI cogwheel.
* **100% Async Engine:** Uses Home Assistant's event-driven architecture to subscribe to precise state and time changes, ensuring zero unnecessary CPU polling cycles.

## 🚀 Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=Day-Modes&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `day_modes` folder from the [latest release](https://github.com/ticstyle/Day-Modes/releases/latest) to the `custom_components` folder inside your Home Assistant configuration directory.

## ⚙️ Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=day_modes)

Add the integration via the Home Assistant User Interface. Go to **Settings -> Devices & Services -> Add Integration** and search for **Day modes**.

## 📊 Available Entities
Once configured, the integration automatically registers a device named **Day modes** containing the following 5 entities:

| Entity ID | Name in UI | State Example | Description |
| :--- | :--- | :--- | :--- |
| `sensor.day_modes` | Current mode | `day` *(Dag)* | Core operational state tracking. Returns `morning`, `day`, `evening`, `night`, or `away`. |
| `sensor.day_modes_morning_time` | Morning start time | `06:00` | Displays the currently configured start time for Morning mode. |
| `sensor.day_modes_day_time` | Day start time | `09:00` | Displays the currently configured start time for Day mode. |
| `sensor.day_modes_evening_time` | Evening start time | `20:00` | Displays the currently configured start time for Evening mode. |
| `sensor.day_modes_night_time` | Night start time | `23:00` | Displays the currently configured start time for Night mode. |

### Entity Attributes
The core state sensor (`sensor.day_modes`) also explicitly exposes your configuration matrix within its metadata attributes for backwards compatibility:
* `tracked_zone`: The target zone entity being monitored (e.g., `zone.home`).
* `morning_time`: Active string configuration for morning start (e.g., `06:00`).
* `day_time`: Active string configuration for day start (e.g., `09:00`).
* `evening_time`: Active string configuration for evening start (e.g., `20:00`).
* `night_time`: Active string configuration for night start (e.g., `23:00`).

## 💡 Lovelace Dashboard Example
Because all setup parameters are now first-class entities, building an informative dashboard summary layout is dead simple and no longer requires nested attribute lookups:

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
