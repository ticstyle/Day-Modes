"""Constants for the Day modes integration."""

DOMAIN = "day_modes"

# Configuration keys
CONF_HOME_ZONE = "home_zone"
CONF_MORNING_TIME = "morning_time"
CONF_DAY_TIME = "day_time"
CONF_EVENING_TIME = "evening_time"
CONF_NIGHT_TIME = "night_time"
CONF_SCHEDULES = "schedules"
CONF_VACATION_CALENDAR = "vacation_calendar"
CONF_VACATION_MORNING_TIME = "vacation_morning_time"

# Default values
DEFAULT_NAME = "Day Mode"
DEFAULT_ZONE = "zone.home"
DEFAULT_MORNING_TIME = "06:00"
DEFAULT_DAY_TIME = "09:00"
DEFAULT_EVENING_TIME = "20:00"
DEFAULT_NIGHT_TIME = "23:00"
DEFAULT_VACATION_MORNING_TIME = "08:00"

# Modes
MODE_AWAY = "away"
MODE_MORNING = "morning"
MODE_DAY = "day"
MODE_EVENING = "evening"
MODE_NIGHT = "night"

# Clean string mapping for internal weekday evaluations
WEEKDAYS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}
