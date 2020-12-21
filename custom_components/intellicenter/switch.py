"""Pentair Intellicenter switches."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from . import PoolEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
):
    """Load a Pentair switch based on a config entry."""
    controller = hass.data[DOMAIN][entry.entry_id].controller

    switches = []

    for object in controller.model.objectList:
        if object.objtype == "BODY":
            switches.append(PoolBody(entry, controller, object))
        elif object.objtype == "CIRCUIT" and not object.isALight and object.isFeatured:
            switches.append(PoolCircuit(entry, controller, object))

    async_add_entities(switches)


class PoolCircuit(PoolEntity, SwitchEntity):
    """Representation of an pool circuit."""

    @property
    def is_on(self) -> bool:
        """Return the state of the circuit."""
        return self._poolObject.status == self._poolObject.onStatus

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self.requestChanges({"STATUS": self._poolObject.offStatus})

    def turn_on(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self.requestChanges({"STATUS": self._poolObject.onStatus})


class PoolBody(PoolCircuit):
    """Representation of a body of water."""

    def __init__(self, entry: ConfigEntry, controller, poolObject):
        """Initialize a Pool body from the underlying circuit."""
        super().__init__(entry, controller, poolObject)
        self._extraStateAttributes = ["VOL", "HEATER", "HTMODE"]

    @property
    def icon(self):
        """Return the icon for the entity."""
        return "mdi:pool"
