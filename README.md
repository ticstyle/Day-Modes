# Day Modes

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![version](https://img.shields.io/github/v/release/ticstyle/Day-Modes?include_prereleases&style=for-the-badge)](https://github.com/ticstyle/Day-Modes/releases)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badgelink.svg?redirect=hacs_repository&repository=ticstyle%2FDay-Modes&category=integration)](https://my.home-assistant.io/redirect/hacs_repository/?repository=ticstyle%2FDay-Modes&category=integration)
[![Open your Home Assistant instance and start a pin to a specific config flow.](https://my.home-assistant.io/badgelink.svg?redirect=config_flow&domain=day_modes)](https://my.home-assistant.io/redirect/config_flow/?domain=day_modes)

A modern, dynamic, and calendar-aware Home Assistant custom integration that automatically tracks and cycles through custom day modes based on occupancy and time matrices configured individually per weekday.

---

## ✨ Features

*   **📅 Matrix Weekday Scheduling:** Configure unique time schedules for different days (e.g., separate weekday and weekend routines, or individual custom schedules for every single day).
*   **👥 Zone Occupancy Aware:** Automatically switches to an `Away` mode whenever the configured zone becomes empty, and instantly restores the correct calendar mode when someone returns.
*   **🔄 Dynamic Time Sensors:** Automatically exposes 4 individual time sensors (`Morning`, `Day`, `Evening`, `Night`) that change their states dynamically to reflect the active rules for the current day.
*   **⚙️ 100% Native UI Configuration:** Fully managed via Home Assistant's Config Flow and Options Flow. Change your schedules anytime via the UI without touch restrictions or manual YAML updates.

---

## 🚀 Installation via HACS

You can add this repository directly to your HACS instance by clicking the button below:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badgelink.svg?redirect=hacs_repository&repository=ticstyle%2FDay-Modes&category=integration)](https://my.home-assistant.io/redirect/hacs_repository/?repository=ticstyle%2FDay-Modes&category=integration)

### Manual Steps:
1.  Navigate to **HACS** in your Home Assistant sidebar.
2.  Click on **Integrations**.
3.  Click the **three dots** in the top-right corner and select **Custom repositories**.
4.  Paste your repository URL (`https://github.com/ticstyle/Day-Modes`) into the **Repository** field.
5.  Select **Integration** as the Category and click **Add**.
6.  Click on the newly added **Day Modes** integration and click **Download** (Make sure to enable *Show beta versions* if you want to test the multi-day matrix pre-releases).
7.  **Restart Home Assistant** to load the integration components.

---

## 🛠️ Configuration

Once installed, you can start the configuration flow directly by clicking this button:

[![Open your Home Assistant instance and start a pin to a specific config flow.](https://my.home-assistant.io/badgelink.svg?redirect=config_flow&domain=day_modes)](https://my.home-assistant.io/redirect/config_flow/?domain=day_modes)

### Manual Steps:
1.  Go to **Settings** -> **Devices & Services** in Home Assistant.
2.  Click **Add Integration** in the bottom right corner.
3.  Search for **Day Modes** and select it.
4.  Follow the dynamic multi-step wizard:
    *   Select your **Tracked Zone** (e.g., `zone.home`).
    *   Set your times and select which days the profile should apply to using the multi-select checkbox block.
    *   Unchecked days will automatically cascade into custom follow-up setup steps until your entire week matrix is fully mapped.

> 💡 **Tip:** To adjust your times or change weekday groups in the future, simply click the **Configure (cogwheel)** button on the integration entry page. Stored configurations will be fully pre-populated automatically!

---

## 📊 Dashboard Markdown Card

The integration automatically publishes your entire multi-day matrix layout inside the attributes of `sensor.day_modes`. You can render a beautiful, clean, and automated timetable card anywhere on your Lovelace dashboard using the native Markdown card.

### Dashboard YAML:
```yaml
type: markdown
title: 📅 Day Modes Schedules
content: >
  {% set profiles = state_attr('sensor.day_modes', 'schedules') %}
  {% if profiles %}
    {% for p in profiles %}
      ### 🗓️ {{ p.days | join(', ') }}
      | Mode | Start Time |
      | :--- | :--- |
      | 🌅 Morning | **{{ p.morning }}** |
      | ☀️ Day | **{{ p.day }}** |
      | 🌆 Evening | **{{ p.evening }}** |
      | 🌙 Night | **{{ p.night }}** |
      {% if not loop.last %}---{% endif %}
    {% endfor %}
  {% else %}
    No schedules configured.
  {% endif %}
