"""Pool configuration data model."""

from enum import StrEnum

from pydantic import BaseModel, Field


class PoolType(StrEnum):
    """Type of pool for determining target ranges."""

    TRADITIONAL = "traditional"  # Standard chlorine pool
    SWG = "swg"  # Salt water generator pool
    SPA = "spa"  # Hot tub / spa


class PoolSurface(StrEnum):
    """Pool surface material (affects calcium hardness targets)."""

    PLASTER = "plaster"
    VINYL = "vinyl"
    FIBERGLASS = "fiberglass"
    PAINTED = "painted"
    PEBBLE = "pebble"  # PebbleTec or similar


class Pool(BaseModel, frozen=True):
    """Pool configuration and dimensions.

    Attributes:
        name: Optional name for the pool.
        volume_gallons: Pool volume in US gallons.
        pool_type: Type of pool (traditional, SWG, spa).
        surface: Pool surface material.
        has_heater: Whether pool has a heater.
        has_swg: Whether pool has a salt water generator.

    Example:
        >>> pool = Pool(
        ...     name="Backyard Pool",
        ...     volume_gallons=15000,
        ...     pool_type=PoolType.SWG,
        ...     surface=PoolSurface.PLASTER,
        ... )
    """

    name: str | None = Field(default=None, description="Pool name")
    volume_gallons: float = Field(gt=0, description="Pool volume in US gallons")
    pool_type: PoolType = Field(default=PoolType.TRADITIONAL, description="Type of pool")
    surface: PoolSurface = Field(default=PoolSurface.PLASTER, description="Pool surface material")
    has_heater: bool = Field(default=False, description="Whether pool has a heater")
    has_swg: bool = Field(default=False, description="Whether pool has a salt water generator")

    @property
    def volume_liters(self) -> float:
        """Get volume in liters."""
        return self.volume_gallons * 3.78541
