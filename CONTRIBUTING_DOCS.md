#

# Documentation Style Guide

This guide defines documentation conventions for all Equilibria code to ensure clarity, scientific rigor, and extensibility.

## General Rules
- Use **NumPy-style docstrings** for all public **classes, methods, and functions**.
- Indent with **4 spaces**.
- Always include **units in square brackets**, e.g., `[kg/h]`, `[°C]`, `[kJ/h]`.
- Organize **assumptions by category** (Thermodynamic, Physical, Numerical).
- Use **blank lines** to visually separate major sections (`Parameters`, `Returns`, etc.).

---

## Required Sections (in order, when applicable)

### 1. Parameters

**Purpose:**  
Describes each input variable passed to the function or method.

**Structure:**
```text
parameter_name : type
    Description. [units]
```

**Example:**
```text
flow_rate : float
    Total mass flow rate. [kg/h]
```

---

### 2. Assumptions

**Purpose:**  
Outlines modeling and theoretical assumptions grouped by domain.

**Structure:**
```text
Thermodynamic:
    - Assumption 1
    - Assumption 2

Physical:
    - Assumption 1
    - Assumption 2

Numerical:
    - Assumption 1
    - Assumption 2
```

**Example:**
```text
Thermodynamic:
    - Ideal mixing (no excess enthalpy)
    - No pressure effects on properties

Physical:
    - Single-phase flow
    - Homogeneous composition

Numerical:
    - Mass fractions sum to 1.0 ± 1e-6
    - Pressure in range [0.1, 1000] kPa
```

---

### 3. Notes

**Purpose:**  
Highlights engineering simplifications or modeling constraints that are not formal assumptions.

**Structure:**
```text
- Note 1
- Note 2
```

**Example:**
```text
- Heat losses are not modeled
- Pressure assumed constant within unit operation
- No phase separation logic implemented
```

---

### 4. Returns

**Purpose:**  
Describes what the function returns and its units.

**Structure:**
```text
return_type
    Description. [units]
```

**Example:**
```text
float
    Total stream enthalpy. [kJ/h]
```

---

### 5. Raises

**Purpose:**  
Documents potential errors or exceptions raised by the function or method.

**Structure:**
```text
ErrorType
    Description of when/why it is raised.
```

**Example:**
```text
ValueError
    If mass fractions do not sum to 1.0 ± 1e-6.
```

---

### 6. Examples

**Purpose:**  
Provides a reproducible code example using triple angle brackets (`>>>`) in doctest format.

**Structure:**
```python
>>> Examples
--------
>>> object = ClassName(args)
>>> object.method()
>>> expected_output
```

**Example:**
```python
>>> stream = Stream("Feed", 100, 25, 101.3, {"Water": 1.0})
>>> stream.enthalpy()
104500.0  # [kJ/h]
```

---

## Optional Sections

### Notes

**Purpose:**  
Additional context, theoretical background, or calculation details.

**Structure:**
```text
- Note 1
- Note 2
```

**Example:**
```text
- Uses CoolProp enthalpy reference at 25°C and 1 atm.
```

---

### See Also

**Purpose:**  
Provides references to related functions or classes.

**Structure:**
```text
See Also
--------
related_function : brief description
```

**Example:**
```text
See Also
--------
Stream.component_flow_rate : Returns mass flow per component
```

---

## Full Docstring Example

```python
def enthalpy(self) -> float:
    """
    Calculate total stream enthalpy using CoolProp.

    Parameters
    ----------
    None

    Returns
    -------
    float
        Total stream enthalpy. [kJ/h]

    Assumptions
    -----------
    Thermodynamic:
        - Ideal mixing (no enthalpy of mixing)
    Physical:
        - No heat loss to surroundings
    Numerical:
        - Uses temperature in Kelvin and pressure in Pascals

    Raises
    ------
    ValueError
        If CoolProp fails for any component.

    Notes
    -----
    Converts units for compatibility with CoolProp.

    Examples
    --------
    >>> s = Stream("Feed", 100, 25, 101.3, {"Water": 1.0})
    >>> s.enthalpy()
    104500.0  # [kJ/h]
    """
```
