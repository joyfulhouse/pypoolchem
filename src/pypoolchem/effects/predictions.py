"""Predict chemistry effects of adding chemicals to pool water.

Given a chemical addition, calculate the expected change in water chemistry.
This allows users to see what will happen before actually adding chemicals.
"""

from pypoolchem.dosing.chemicals import ChemicalType, get_chemical
from pypoolchem.models.water import WaterChemistry


def predict_effect(
    water: WaterChemistry,
    chemical_type: ChemicalType,
    amount_oz: float,
    pool_gallons: float,
) -> WaterChemistry:
    """Predict water chemistry after adding a chemical.

    Uses the chemical's effect multipliers to calculate the expected
    changes to each water parameter.

    Formula for each effect:
        new_value = current_value + (amount_oz / pool_gallons) * multiplier

    Args:
        water: Current water chemistry.
        chemical_type: Type of chemical to add.
        amount_oz: Amount of chemical in ounces.
        pool_gallons: Pool volume in US gallons.

    Returns:
        New WaterChemistry with predicted values.

    Example:
        >>> water = WaterChemistry(
        ...     ph=7.5, temperature_f=84, free_chlorine=2.0,
        ...     calcium_hardness=300, total_alkalinity=80, cyanuric_acid=50
        ... )
        >>> new_water = predict_effect(water, ChemicalType.TRICHLOR, 8, 15000)
        >>> print(f"New FC: {new_water.free_chlorine:.1f}")
        >>> print(f"New CYA: {new_water.cyanuric_acid:.1f}")
    """
    chemical = get_chemical(chemical_type)

    # Start with current values
    new_fc = water.free_chlorine
    new_cc = water.combined_chlorine
    new_ph = water.ph
    new_ta = water.total_alkalinity
    new_ch = water.calcium_hardness
    new_cya = water.cyanuric_acid
    new_salt = water.salt
    new_borates = water.borates

    # Calculate effect multiplier
    effect_factor = amount_oz / pool_gallons

    # Apply primary effect
    match chemical.affects:
        case "free_chlorine":
            new_fc += effect_factor * chemical.multiplier
        case "ph":
            # pH effects are more complex - simplified linear approximation
            new_ph += effect_factor * chemical.multiplier / 100
        case "total_alkalinity":
            new_ta += effect_factor * chemical.multiplier
        case "calcium_hardness":
            new_ch += effect_factor * chemical.multiplier
        case "cyanuric_acid":
            new_cya += effect_factor * chemical.multiplier
        case "salt":
            new_salt += effect_factor * chemical.multiplier
        case "borates":
            new_borates += effect_factor * chemical.multiplier

    # Apply secondary effects
    for param, multiplier in chemical.secondary_effects.items():
        match param:
            case "free_chlorine":
                new_fc += effect_factor * multiplier
            case "ph":
                new_ph += effect_factor * multiplier / 100
            case "total_alkalinity":
                # Negative multiplier means it lowers TA
                new_ta += effect_factor * multiplier
            case "calcium_hardness":
                new_ch += effect_factor * multiplier
            case "cyanuric_acid":
                new_cya += effect_factor * multiplier
            case "salt":
                new_salt += effect_factor * multiplier
            case "borates":
                new_borates += effect_factor * multiplier

    # Clamp values to reasonable ranges
    new_fc = max(0, new_fc)
    new_cc = max(0, new_cc)
    new_ph = max(0, min(14, new_ph))
    new_ta = max(0, new_ta)
    new_ch = max(0, new_ch)
    new_cya = max(0, new_cya)
    new_salt = max(0, new_salt)
    new_borates = max(0, new_borates)

    return WaterChemistry(
        ph=round(new_ph, 2),
        temperature_f=water.temperature_f,
        free_chlorine=round(new_fc, 1),
        combined_chlorine=round(new_cc, 1),
        total_alkalinity=round(new_ta, 0),
        calcium_hardness=round(new_ch, 0),
        cyanuric_acid=round(new_cya, 0),
        salt=round(new_salt, 0),
        borates=round(new_borates, 0),
        tds=water.tds,
    )


def predict_multiple_effects(
    water: WaterChemistry,
    additions: list[tuple[ChemicalType, float]],
    pool_gallons: float,
) -> WaterChemistry:
    """Predict water chemistry after adding multiple chemicals.

    Applies each chemical addition in sequence.

    Args:
        water: Current water chemistry.
        additions: List of (chemical_type, amount_oz) tuples.
        pool_gallons: Pool volume in US gallons.

    Returns:
        New WaterChemistry with predicted values after all additions.

    Example:
        >>> water = WaterChemistry(
        ...     ph=7.8, temperature_f=84, free_chlorine=2.0,
        ...     calcium_hardness=300, total_alkalinity=80, cyanuric_acid=50
        ... )
        >>> additions = [
        ...     (ChemicalType.MURIATIC_ACID_31_45, 16),
        ...     (ChemicalType.BLEACH_12_5, 64),
        ... ]
        >>> new_water = predict_multiple_effects(water, additions, 15000)
    """
    current = water

    for chemical_type, amount_oz in additions:
        current = predict_effect(current, chemical_type, amount_oz, pool_gallons)

    return current
