"""Device tracker for AIS receiver."""

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MMSIS, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up device tracker for AIS receiver."""

    async_add_entities(
        AisReceiverTrackerEntity(mmsi) for mmsi in entry.data[CONF_MMSIS]
    )


class AisReceiverTrackerEntity(TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, mmsi: str) -> None:
        """Set up AIS receiver tracker entity."""
        self._mmsi = mmsi
        self._attr_unique_id = f"ais_mmsi_{mmsi}"
        self._attr_name = mmsi
        self._attr_icon = "mdi:ferry"
        self._attr_extra_state_attributes = {}

        self.latitude: float | None = None
        self.longitude: float | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(identifiers={(DOMAIN, self._mmsi)})

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.GPS

    async def async_update_data_from_msg(self, event: Event) -> None:
        """Update data from received message."""
        msg = event.data
        if msg.get("msg_type") in [1, 2, 3]:
            self.latitude = msg.get("lat")
            self.longitude = msg.get("lon")

        if msg.get("msg_type") == 5:
            self._attr_extra_state_attributes["shipname"] = msg.get("shipname")
            self._attr_extra_state_attributes["callsign"] = msg.get("callsign")

        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register for updates."""
        self.async_on_remove(
            self.hass.bus.async_listen(
                f"{DOMAIN}_{self._mmsi}", self.async_update_data_from_msg
            )
        )
