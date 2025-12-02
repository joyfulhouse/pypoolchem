"""Water chemistry data model."""

from pydantic import BaseModel, Field


class WaterChemistry(BaseModel, frozen=True):
    """Immutable representation of pool/spa water chemistry.

    All values are in ppm (parts per million) unless otherwise noted.

    Attributes:
        ph: Water pH level (0-14, typically 7.2-7.8 for pools).
        temperature_f: Water temperature in Fahrenheit (32-104°F typical).
        free_chlorine: Free available chlorine in ppm.
        combined_chlorine: Combined chlorine (chloramines) in ppm.
        total_alkalinity: Total alkalinity in ppm as CaCO3.
        calcium_hardness: Calcium hardness in ppm as CaCO3.
        cyanuric_acid: Cyanuric acid (stabilizer) in ppm.
        salt: Salt level in ppm (for SWG pools, typically 2700-3400).
        borates: Borate level in ppm (typically 30-50 if used).
        tds: Total dissolved solids in ppm.

    Example:
        >>> water = WaterChemistry(
        ...     ph=7.5,
        ...     temperature_f=84,
        ...     free_chlorine=3.0,
        ...     calcium_hardness=300,
        ...     total_alkalinity=80,
        ...     cyanuric_acid=50,
        ... )
    """

    ph: float = Field(ge=0, le=14, description="Water pH level")
    temperature_f: float = Field(ge=32, le=120, description="Water temperature in Fahrenheit")
    free_chlorine: float = Field(default=0, ge=0, description="Free chlorine in ppm")
    combined_chlorine: float = Field(
        default=0, ge=0, description="Combined chlorine (chloramines) in ppm"
    )
    total_alkalinity: float = Field(ge=0, description="Total alkalinity in ppm as CaCO3")
    calcium_hardness: float = Field(ge=0, description="Calcium hardness in ppm as CaCO3")
    cyanuric_acid: float = Field(default=0, ge=0, description="Cyanuric acid (stabilizer) in ppm")
    salt: float = Field(default=0, ge=0, description="Salt level in ppm")
    borates: float = Field(default=0, ge=0, description="Borate level in ppm")
    tds: float = Field(default=1000, ge=0, description="Total dissolved solids in ppm")

    @property
    def total_chlorine(self) -> float:
        """Calculate total chlorine (FC + CC)."""
        return self.free_chlorine + self.combined_chlorine

    @property
    def temperature_c(self) -> float:
        """Get temperature in Celsius."""
        return (self.temperature_f - 32) * 5 / 9
