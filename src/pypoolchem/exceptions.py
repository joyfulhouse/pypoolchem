"""Custom exceptions for pypoolchem."""


class PyPoolChemError(Exception):
    """Base exception for all pypoolchem errors."""


class ValidationError(PyPoolChemError):
    """Raised when input validation fails."""


class CalculationError(PyPoolChemError):
    """Raised when a calculation cannot be performed."""


class ChemicalNotFoundError(PyPoolChemError):
    """Raised when a chemical type is not found."""
