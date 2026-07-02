# Day modes

![](https://img.shields.io/github/v/release/ticstyle/Day-Modes?style=for-the-badge&color=blue)
![](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue?style=for-the-badge&logo=home-assistant)
![](https://img.shields.io/github/license/ticstyle/Day-Modes?style=for-the-badge)
![](https://img.shields.io/github/downloads/ticstyle/Day-Modes/total?style=for-the-badge&color=green)
![](https://img.shields.io/github/issues/ticstyle/Day-Modes?style=for-the-badge&color=orange)

A modern Home Assistant custom integration that creates a dynamic sensor to automatically track and cycle through custom day modes (Morning, Day, Evening, Night, Away) based on your personalized schedule and zone occupancy.

To add this integration, please add the custom repository `https://github.com/ticstyle/Day-Modes` to HACS in your Home Assistant setup.

## 🌐 Supported Languages / Språk
The integration natively defaults to English for the core backend but includes full frontend translations for Swedish. The Config Flow, Options Flow, and entity configurations will seamlessly match your user interface language.

## ✨ Features
* **Dynamic Presence Tracking:** Automatically forces an `away` state whenever your designated home zone becomes empty, and instantly restores the correct time-based operational mode the second someone returns.
* **On-the-Fly Reconfiguration:** Built with a full Options Flow. Easily change your scheduled morning, day, evening, or night times, or target a completely different zone at any point without needing to delete and recreate the entity.
* **Rich Metadata Attributes:** Every sensor exposes its active time thresholds and tracked zone directly inside its state attributes, making it incredibly clean to cross-reference configuration states inside advanced templates.
* **100% Async Engine:** Uses Home Assistant's event-driven architecture to subscribe to precise time changes and state triggers, ensuring zero unnecessary CPU polling cycles or blocking calls.

## 🚀 Installation

[![](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ticstyle&repository=Day-Modes&category=Integration)

Via [HACS](https://hacs.xyz/) or manually copy the `day_modes` folder from the [latest release](https://github.com/ticstyle/Day-Modes/releases/latest) to the `custom_components` folder inside your Home Assistant configuration directory.

## ⚙️ Configuration

[![](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=day_modes)

Add the integration via the Home Assistant User Interface. Go to **Settings -> Devices & Services -> Add Integration** and search for **Day modes**.

## 📊 Available Entities
Regardless of your tracked zone name, the integration locks the primary state entity to a predictable, clean identity:

| Entity ID | Name in UI | State Example | Description |
| :--- | :--- | :--- | :--- |
| `sensor.day_modes` | Day modes | `day` | Operational state tracking. Returns `morning`, `day`, `evening`, `night`, or `away`. |

### Entity Attributes
The generated sensor explicitly exposes your active settings within its state attributes for easy UI mapping:
* `tracked_zone`: The target zone entity being monitored (e.g., `zone.home`).
* `morning_time`: Configured timestamp for the start of morning mode (e.g., `06:00:00`).
* `day_time`: Configured timestamp for the start of day mode (e.g., `09:00:00`).
* `evening_time`: Configured timestamp for the start of evening mode (e.g., `20:00:00`).
* `night_time`: Configured timestamp for the start of night mode (e.g., `23:00:00`).

## 💡 Lovelace Dashboard Example
Since the states are native string values, you can use standard entity cards, conditional cards, or clean markdown blocks to adapt your dashboard experience based on the house operational state:

```yaml
type: markdown
title: "House Status"
content: >
  Current House Mode: **{{ states('sensor.day_modes') | capitalize }}**
  
  {% if is_state('sensor.day_modes', 'away') %}
    🏠 The house is currently in eco-mode while everyone is out.
  {% else %}
    ⏰ Tonight's night mode schedule is set to trigger at {{ state_attr('sensor.day_modes', 'night_time') }}.
  {% endif %}
