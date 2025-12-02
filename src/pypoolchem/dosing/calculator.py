"""Dosing calculation functions for pool chemicals.

All formulas are derived from the TroubleFreePool PoolMath calculator.

Base formula for most chemicals:
    dose_oz = (target - current) * pool_gallons / multiplier

pH adjustment is more complex and depends on temperature, TA, and borates.
"""

from pydantic import BaseModel, Field

from pypoolchem.dosing.chemicals import (
    Chemical,
    ChemicalType,
    get_chemical,
)


class DosingResult(BaseModel, frozen=True):
    """Result of a dosing calculation.

    Attributes:
        chemical: The chemical to add.
        amount: Amount to add.
        unit: Unit of measurement.
        amount_volume: Amount in volume units (if different from weight).
        volume_unit: Volume unit (if applicable).
        notes: Additional notes or warnings.
    """

    chemical: Chemical
    amount: float = Field(description="Amount to add (weight)")
    unit: str = Field(description="Unit of measurement")
    amount_volume: float | None = Field(
        default=None,
        description="Amount in volume units",
    )
    volume_unit: str | None = Field(default=None, description="Volume unit")
    notes: str | None = Field(default=None, description="Additional notes")


def _calculate_ph_adjustment_factor(
    temperature_f: float,
    total_alkalinity: float,
) -> float:
    """Calculate the pH adjustment factor based on temperature and TA.

    Formula:
        temp = (temperature_f - 60) / 20
        adj = (192.1626 - 60.1221*temp + 6.0752*temp^2 - 0.1943*temp^3) * (TA + 13.91) / 114.6

    Args:
        temperature_f: Water temperature in Fahrenheit.
        total_alkalinity: Total alkalinity in ppm.

    Returns:
        pH adjustment factor.
    """
    # Normalize temperature
    temp = (temperature_f - 60) / 20

    # Calculate adjustment factor
    return (
        (192.1626 - 60.1221 * temp + 6.0752 * temp**2 - 0.1943 * temp**3)
        * (total_alkalinity + 13.91)
        / 114.6
    )


def _calculate_borate_correction(
    temperature_f: float,
    borates: float,
    ph_change: float,
) -> float:
    """Calculate the borate correction for pH adjustment.

    Formula:
        temp = (temperature_f - 60) / 20
        extra = (-5.476259 + 2.414292*temp - 0.355882*temp^2 + 0.01755*temp^3) * Borate * ph_change

    Args:
        temperature_f: Water temperature in Fahrenheit.
        borates: Borate level in ppm.
        ph_change: The desired pH change.

    Returns:
        Borate correction factor.
    """
    if borates <= 0:
        return 0.0

    temp = (temperature_f - 60) / 20

    return (
        (-5.476259 + 2.414292 * temp - 0.355882 * temp**2 + 0.01755 * temp**3) * borates * ph_change
    )


def calculate_chlorine_dose(
    current_fc: float,
    target_fc: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BLEACH_12_5,
) -> DosingResult:
    """Calculate chlorine dose to reach target FC.

    Args:
        current_fc: Current free chlorine in ppm.
        target_fc: Target free chlorine in ppm.
        pool_gallons: Pool volume in US gallons.
        chemical_type: Type of chlorine to use.

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_chlorine_dose(2.0, 5.0, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(chemical_type)
    fc_change = target_fc - current_fc

    if fc_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="FC is already at or above target",
        )

    # For bleach, use the formula: (FC_change * gallons) / multiplier
    # The multiplier for bleach is based on concentration
    amount = (fc_change * pool_gallons) / chemical.multiplier

    # Calculate volume if applicable
    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups" if chemical.unit == "oz" else chemical.unit

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
    )


def calculate_ph_dose(
    current_ph: float,
    target_ph: float,
    pool_gallons: float,
    total_alkalinity: float,
    temperature_f: float = 80,
    borates: float = 0,
    *,
    raise_ph: bool | None = None,
    chemical_type: ChemicalType | None = None,
) -> DosingResult:
    """Calculate pH adjustment dose.

    pH adjustment is complex because it depends on temperature, TA, and borates.
    The function automatically determines whether to raise or lower pH.

    Args:
        current_ph: Current pH level.
        target_ph: Target pH level.
        pool_gallons: Pool volume in US gallons.
        total_alkalinity: Total alkalinity in ppm.
        temperature_f: Water temperature in Fahrenheit.
        borates: Borate level in ppm (affects pH buffering).
        raise_ph: Force raising (True) or lowering (False) pH.
        chemical_type: Specific chemical to use (auto-selected if None).

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_ph_dose(7.8, 7.5, 15000, 80)
        >>> print(f"Add {result.amount:.1f} {result.unit} of {result.chemical.name}")
    """
    ph_change = target_ph - current_ph

    # Determine direction
    if raise_ph is None:
        raise_ph = ph_change > 0

    # Select default chemical if not specified
    if chemical_type is None:
        chemical_type = ChemicalType.SODA_ASH if raise_ph else ChemicalType.MURIATIC_ACID_31_45

    chemical = get_chemical(chemical_type)

    if abs(ph_change) < 0.01:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="pH is already at target",
        )

    # Calculate adjustment factor
    adj = _calculate_ph_adjustment_factor(temperature_f, total_alkalinity)

    # Calculate base delta
    delta = ph_change * adj

    # Calculate borate correction
    extra = _calculate_borate_correction(temperature_f, borates, ph_change)

    # Calculate dose based on chemical
    if raise_ph:
        # Raising pH with soda ash or borax
        amount = (delta / chemical.multiplier) + (extra / chemical.multiplier)
        amount = abs(amount)
    else:
        # Lowering pH with acid
        # Acid multipliers are positive, but delta is negative
        amount = (delta / -chemical.multiplier) + (extra / -chemical.multiplier)
        amount = abs(amount)

    # Scale by pool volume (the formulas above are for 10,000 gallons)
    amount = amount * pool_gallons / 10000

    # Calculate volume if applicable
    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups" if chemical.unit == "oz" else chemical.unit

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
    )


def calculate_alkalinity_dose(
    current_ta: float,
    target_ta: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BAKING_SODA,
) -> DosingResult:
    """Calculate alkalinity adjustment dose.

    Args:
        current_ta: Current total alkalinity in ppm.
        target_ta: Target total alkalinity in ppm.
        pool_gallons: Pool volume in US gallons.
        chemical_type: Chemical to use (default: baking soda).

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_alkalinity_dose(60, 80, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(chemical_type)
    ta_change = target_ta - current_ta

    if ta_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="TA is already at or above target. Lower TA with acid + aeration.",
        )

    amount = (ta_change * pool_gallons) / chemical.multiplier

    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups"

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
    )


def calculate_calcium_dose(
    current_ch: float,
    target_ch: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.CALCIUM_CHLORIDE_DIHYDRATE,
) -> DosingResult:
    """Calculate calcium hardness adjustment dose.

    Args:
        current_ch: Current calcium hardness in ppm.
        target_ch: Target calcium hardness in ppm.
        pool_gallons: Pool volume in US gallons.
        chemical_type: Chemical to use (default: calcium chloride dihydrate/flake).

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_calcium_dose(200, 300, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(chemical_type)
    ch_change = target_ch - current_ch

    if ch_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="CH is already at or above target. Lower CH with water replacement.",
        )

    amount = (ch_change * pool_gallons) / chemical.multiplier

    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups"

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
    )


def calculate_cya_dose(
    current_cya: float,
    target_cya: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.CYA_GRANULAR,
) -> DosingResult:
    """Calculate cyanuric acid (stabilizer) dose.

    Args:
        current_cya: Current CYA level in ppm.
        target_cya: Target CYA level in ppm.
        pool_gallons: Pool volume in US gallons.
        chemical_type: Chemical to use (default: granular CYA).

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_cya_dose(30, 50, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(chemical_type)
    cya_change = target_cya - current_cya

    if cya_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="CYA is already at or above target. Lower CYA with water replacement.",
        )

    amount = (cya_change * pool_gallons) / chemical.multiplier

    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups"

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
    )


def calculate_salt_dose(
    current_salt: float,
    target_salt: float,
    pool_gallons: float,
) -> DosingResult:
    """Calculate salt dose for SWG pools.

    Args:
        current_salt: Current salt level in ppm.
        target_salt: Target salt level in ppm.
        pool_gallons: Pool volume in US gallons.

    Returns:
        DosingResult with amount to add in lbs.

    Example:
        >>> result = calculate_salt_dose(2800, 3200, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(ChemicalType.POOL_SALT)
    salt_change = target_salt - current_salt

    if salt_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit="lbs",
            notes="Salt is already at or above target. Lower salt with water replacement.",
        )

    amount_oz = (salt_change * pool_gallons) / chemical.multiplier
    amount_lbs = amount_oz / 16  # Convert oz to lbs

    return DosingResult(
        chemical=chemical,
        amount=round(amount_lbs, 1),
        unit="lbs",
        notes=f"Approximately {round(amount_oz, 1)} oz",
    )


def calculate_borate_dose(
    current_borates: float,
    target_borates: float,
    pool_gallons: float,
    chemical_type: ChemicalType = ChemicalType.BORAX_BORATE,
) -> DosingResult:
    """Calculate borate dose.

    Note: Boric acid and sodium tetraborate pentahydrate require
    muriatic acid to neutralize the pH effect.

    Args:
        current_borates: Current borate level in ppm.
        target_borates: Target borate level in ppm.
        pool_gallons: Pool volume in US gallons.
        chemical_type: Chemical to use (default: borax).

    Returns:
        DosingResult with amount to add.

    Example:
        >>> result = calculate_borate_dose(0, 30, 15000)
        >>> print(f"Add {result.amount:.1f} {result.unit}")
    """
    chemical = get_chemical(chemical_type)
    borate_change = target_borates - current_borates

    if borate_change <= 0:
        return DosingResult(
            chemical=chemical,
            amount=0,
            unit=chemical.unit,
            notes="Borates already at or above target.",
        )

    amount = (borate_change * pool_gallons) / chemical.multiplier

    # Add note about acid requirement for certain products
    notes = None
    if chemical_type == ChemicalType.BORIC_ACID:
        acid_oz = amount * 0.624
        notes = f"Requires {acid_oz:.1f} fl oz muriatic acid (31.45%) to neutralize"
    elif chemical_type == ChemicalType.SODIUM_TETRABORATE_PENTAHYDRATE:
        acid_oz = amount * 0.4765
        notes = f"Requires {acid_oz:.1f} fl oz muriatic acid (31.45%) to neutralize"

    amount_volume = None
    volume_unit = None
    if chemical.volume_factor:
        amount_volume = amount * chemical.volume_factor
        volume_unit = "cups"

    return DosingResult(
        chemical=chemical,
        amount=round(amount, 2),
        unit=chemical.unit,
        amount_volume=round(amount_volume, 2) if amount_volume else None,
        volume_unit=volume_unit,
        notes=notes,
    )


def calculate_water_replacement(
    current_value: float,
    target_value: float,
    fill_water_value: float = 0,
) -> float:
    """Calculate percentage of water to replace to reach target.

    Used for lowering CYA, CH, or Salt which can only be reduced by dilution.

    Formula:
        For CYA/Salt (fill water assumed 0):
            replacement_% = 100 - (target / current) * 100

        For CH (fill water has some CH):
            replacement_% = 100 - ((target - fill) / (current - fill)) * 100

    Args:
        current_value: Current level in ppm.
        target_value: Target level in ppm.
        fill_water_value: Level in fill water (default 0).

    Returns:
        Percentage of water to replace.

    Example:
        >>> calculate_water_replacement(80, 50)  # CYA from 80 to 50
        37.5
    """
    if current_value <= target_value:
        return 0.0

    if fill_water_value == 0:
        # Simple formula for CYA/Salt
        return 100 - (target_value / current_value) * 100
    # Formula for CH with fill water
    if current_value <= fill_water_value:
        return 0.0
    return 100 - ((target_value - fill_water_value) / (current_value - fill_water_value)) * 100
