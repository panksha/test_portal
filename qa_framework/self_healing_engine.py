"""
Self-Healing Locator Engine
Intercepts Selenium NoSuchElementException, tries fallback locator strategies
from the config.json repository, and heals the primary locator on success.
"""

import json
import os
import time
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
HEALING_LOG_PATH = os.path.join(REPORTS_DIR, "healing_log.json")

BY_MAP = {
    "id": By.ID,
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "name": By.NAME,
    "class": By.CLASS_NAME,
    "tag": By.TAG_NAME,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
}


def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def _load_healing_log():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if os.path.exists(HEALING_LOG_PATH):
        with open(HEALING_LOG_PATH, "r") as f:
            return json.load(f)
    return {"events": [], "total_heals": 0}


def _save_healing_log(log):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(HEALING_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def _log_heal_event(page: str, locator_key: str, failed_locator: dict, healed_locator: dict, attempts: int):
    """Record a self-healing event to the healing log JSON file."""
    log = _load_healing_log()
    event = {
        "timestamp": datetime.now().isoformat(),
        "page": page,
        "locator_key": locator_key,
        "failed_primary": failed_locator,
        "healed_with": healed_locator,
        "fallback_attempts": attempts,
        "status": "HEALED"
    }
    log["events"].append(event)
    log["total_heals"] = len(log["events"])
    _save_healing_log(log)

    # Console output for demo visibility
    print(f"\n{'='*60}")
    print(f"  [SELF-HEALING ENGINE] Locator failure detected!")
    print(f"  Page        : {page}")
    print(f"  Locator Key : {locator_key}")
    print(f"  Failed      : {failed_locator['by']}='{failed_locator['value']}'")
    print(f"  Healed With : {healed_locator['by']}='{healed_locator['value']}'")
    print(f"  Attempts    : {attempts}")
    print(f"  Status      : [HEALED] test continues successfully")
    print(f"{'='*60}\n")


def heal_locator(driver, page: str, locator_key: str, timeout: int = 10):
    """
    Attempt to find an element using primary locator; if it fails,
    try each fallback in sequence. On success, heal (promote) the
    working locator to primary in config.json.

    Args:
        driver: Selenium WebDriver instance
        page: Page name key in config (e.g., 'registration', 'forgot_password')
        locator_key: Locator key within the page (e.g., 'email', 'register_btn')
        timeout: WebDriverWait timeout in seconds

    Returns:
        WebElement if found

    Raises:
        NoSuchElementException if all strategies fail
    """
    config = _load_config()
    locator_repo = config.get("locators", {}).get(page, {}).get(locator_key)

    if not locator_repo:
        raise ValueError(f"Locator '{locator_key}' not found in config for page '{page}'")

    primary = locator_repo["primary"]
    fallbacks = locator_repo.get("fallbacks", [])

    # ── Try primary locator ──────────────────────────────────────────────────
    try:
        by = BY_MAP[primary["by"]]
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, primary["value"]))
        )
        return element
    except (NoSuchElementException, TimeoutException):
        logger.warning(f"[SelfHeal] Primary locator FAILED: {primary['by']}='{primary['value']}' for {page}.{locator_key}")

    # ── Try fallback strategies ──────────────────────────────────────────────
    for attempt, fallback in enumerate(fallbacks, start=1):
        try:
            by = BY_MAP[fallback["by"]]
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((by, fallback["value"]))
            )

            # ── Heal: Promote working fallback to primary ────────────────────
            _log_heal_event(
                page=page,
                locator_key=locator_key,
                failed_locator=primary,
                healed_locator=fallback,
                attempts=attempt
            )

            # Update config.json: old primary → new fallback, working fallback → new primary
            old_primary = dict(primary)
            config["locators"][page][locator_key]["primary"] = dict(fallback)
            # Add old primary back as a fallback (at the end) if not already there
            fallback_values = [f["value"] for f in fallbacks]
            if old_primary["value"] not in fallback_values:
                config["locators"][page][locator_key]["fallbacks"].append(old_primary)
            _save_config(config)

            return element

        except (NoSuchElementException, TimeoutException):
            logger.warning(f"[SelfHeal] Fallback {attempt} failed: {fallback['by']}='{fallback['value']}'")
            continue

    raise NoSuchElementException(
        f"[SelfHeal] ALL locator strategies exhausted for {page}.{locator_key}. "
        f"Tried: primary + {len(fallbacks)} fallbacks."
    )


def get_healing_summary():
    """Return a summary of all self-healing events."""
    log = _load_healing_log()
    return {
        "total_heals": log["total_heals"],
        "events": log["events"],
        "pages_affected": list(set(e["page"] for e in log["events"])),
        "locators_healed": list(set(f"{e['page']}.{e['locator_key']}" for e in log["events"]))
    }
