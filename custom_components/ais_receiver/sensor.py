"""Sensors for AIS receiver."""

from pyais.constants import NavigationStatus

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MMSIS, DOMAIN

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="course", name="course", entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="heading", name="heading", entity_registry_enabled_default=False
    ),
    SensorEntityDescription(
        key="speed",
        name="speed",
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
    ),
    SensorEntityDescription(
        key="status",
        name="status",
        device_class=SensorDeviceClass.ENUM,
        options={status.name for status in NavigationStatus},
    ),
    SensorEntityDescription(
        key="turn", name="turn", entity_registry_enabled_default=False
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up device tracker for AIS receiver."""

    async_add_entities(
        AisReceiverSensorEntity(mmsi, description)
        for mmsi in entry.data[CONF_MMSIS]
        for description in SENSORS
    )


class AisReceiverSensorEntity(SensorEntity):
    """Represent a tracked device."""

    _attr_should_poll = False

    def __init__(self, mmsi: str, description: SensorEntityDescription) -> None:
        """Set up AIS receiver tracker entity."""
        self.entity_description = description
        self._mmsi = mmsi
        self._attr_unique_id = f"ais_mmsi_{mmsi}_{description.key}"
        self._attr_name = f"{mmsi} {description.key}"
        self._attr_extra_state_attributes = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mmsi)}, name=mmsi, serial_number=mmsi
        )

    async def async_update_data_from_msg(self, event: Event) -> None:
        """Update data from received message."""
        msg = event.data
        if (
            msg.get("msg_type") in [1, 2, 3]
            and (value := msg.get(self.entity_description.key)) is not None
        ):
            if self.entity_description.key == "speed":
                value = value / 10
            if self.entity_description.key == "status":
                value = NavigationStatus(value).name
            self._attr_native_value = value

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
