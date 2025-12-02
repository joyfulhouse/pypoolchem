"""Target ranges for pool chemistry parameters."""

from pydantic import BaseModel, Field

from pypoolchem.models.pool import PoolType


class ParameterRange(BaseModel, frozen=True):
    """A range for a water chemistry parameter.

    Attributes:
        minimum: Minimum acceptable value.
        target: Ideal target value.
        maximum: Maximum acceptable value.
    """

    minimum: float
    target: float
    maximum: float

    def is_in_range(self, value: float) -> bool:
        """Check if a value is within the acceptable range."""
        return self.minimum <= value <= self.maximum

    def is_low(self, value: float) -> bool:
        """Check if a value is below the minimum."""
        return value < self.minimum

    def is_high(self, value: float) -> bool:
        """Check if a value is above the maximum."""
        return value > self.maximum


class TargetRanges(BaseModel, frozen=True):
    """Target ranges for all pool chemistry parameters.

    These ranges vary by pool type (traditional, SWG, spa).

    Attributes:
        ph: pH range (typically 7.2-7.8).
        free_chlorine_min_factor: Minimum FC as factor of CYA.
        free_chlorine_target_factor: Target FC as factor of CYA.
        total_alkalinity: TA range in ppm.
        calcium_hardness: CH range in ppm.
        cyanuric_acid: CYA range in ppm.
        salt: Salt range in ppm (for SWG pools).
        borates: Borate range in ppm (optional).
        csi: CSI/LSI range.
    """

    ph: ParameterRange
    total_alkalinity: ParameterRange
    calcium_hardness: ParameterRange
    cyanuric_acid: ParameterRange
    salt: ParameterRange | None = None
    borates: ParameterRange | None = None
    csi: ParameterRange = Field(default=ParameterRange(minimum=-0.3, target=0.0, maximum=0.3))

    # FC/CYA factors for calculating chlorine targets
    fc_min_factor: float = Field(
        default=0.075,
        description="Minimum FC as multiplier of CYA",
    )
    fc_target_factor: float = Field(
        default=0.10,
        description="Target FC as multiplier of CYA",
    )


# Predefined target ranges for different pool types
TRADITIONAL_POOL_TARGETS = TargetRanges(
    ph=ParameterRange(minimum=7.2, target=7.5, maximum=7.8),
    total_alkalinity=ParameterRange(minimum=80, target=100, maximum=120),
    calcium_hardness=ParameterRange(minimum=200, target=300, maximum=400),
    cyanuric_acid=ParameterRange(minimum=30, target=50, maximum=80),
    fc_min_factor=0.075,
    fc_target_factor=0.10,
)

SWG_POOL_TARGETS = TargetRanges(
    ph=ParameterRange(minimum=7.4, target=7.6, maximum=7.8),
    total_alkalinity=ParameterRange(minimum=50, target=70, maximum=90),
    calcium_hardness=ParameterRange(minimum=200, target=350, maximum=450),
    cyanuric_acid=ParameterRange(minimum=60, target=70, maximum=90),
    salt=ParameterRange(minimum=2700, target=3200, maximum=3400),
    fc_min_factor=0.045,
    fc_target_factor=0.075,
)

SPA_TARGETS = TargetRanges(
    ph=ParameterRange(minimum=7.4, target=7.6, maximum=7.8),
    total_alkalinity=ParameterRange(minimum=50, target=60, maximum=80),
    calcium_hardness=ParameterRange(minimum=120, target=150, maximum=200),
    cyanuric_acid=ParameterRange(minimum=20, target=30, maximum=40),
    fc_min_factor=0.075,
    fc_target_factor=0.10,
)


def get_target_ranges(pool_type: PoolType) -> TargetRanges:
    """Get target ranges for a specific pool type.

    Args:
        pool_type: The type of pool.

    Returns:
        TargetRanges for the specified pool type.

    Example:
        >>> targets = get_target_ranges(PoolType.SWG)
        >>> print(f"Target pH: {targets.ph.target}")
        Target pH: 7.6
    """
    match pool_type:
        case PoolType.TRADITIONAL:
            return TRADITIONAL_POOL_TARGETS
        case PoolType.SWG:
            return SWG_POOL_TARGETS
        case PoolType.SPA:
            return SPA_TARGETS
