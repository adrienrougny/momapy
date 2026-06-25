"""Shared CellDesigner format constants.

Format-level constants needed by both the CellDesigner reader and writer:
the CellDesigner XML namespace, the special-character decoding table, and
the link-anchor position-code mapping. Keeping them here (rather than in
``_reading_parsing``) lets the writer share them without importing from a
reading module.

Internal module (underscore filename): its module-level contents are
public-named but the module itself is not part of the public API.
"""

CD_NAMESPACE = "http://www.sbml.org/2001/ns/celldesigner"
"""The CellDesigner extension XML namespace."""

TEXT_TO_CHARACTER = {
    "_underscore_": "_",
    "_br_": "\n",
    "_BR_": "\n",
    "_plus_": "+",
    "_minus_": "-",
    "_slash_": "/",
    "_space_": " ",
    "_Alpha_": "Α",
    "_alpha_": "α",
    "_Beta_": "Β",
    "_beta_": "β",
    "_Gamma_": "Γ",
    "_gamma_": "γ",
    "_Delta_": "Δ",
    "_delta_": "δ",
    "_Epsilon_": "Ε",
    "_epsilon_": "ε",
    "_Zeta_": "Ζ",
    "_zeta_": "ζ",
    "_Eta_": "Η",
    "_eta_": "η",
    "_Theta_": "Θ",
    "_theta_": "θ",
    "_Iota_": "Ι",
    "_iota_": "ι",
    "_Kappa_": "Κ",
    "_kappa_": "κ",
    "_Lambda_": "Λ",
    "_lambda_": "λ",
    "_Mu_": "Μ",
    "_mu_": "μ",
    "_Nu_": "Ν",
    "_nu_": "ν",
    "_Xi_": "Ξ",
    "_xi_": "ξ",
    "_Omicron_": "Ο",
    "_omicron_": "ο",
    "_Pi_": "Π",
    "_pi_": "π",
    "_Rho_": "Ρ",
    "_rho_": "ρ",
    "_Sigma_": "Σ",
    "_sigma_": "σ",
    "_Tau_": "Τ",
    "_tau_": "τ",
    "_Upsilon_": "Υ",
    "_upsilon_": "υ",
    "_Phi_": "Φ",
    "_phi_": "φ",
    "_Chi_": "Χ",
    "_chi_": "χ",
    "_Psi_": "Ψ",
    "_psi_": "ψ",
    "_Omega_": "Ω",
    "_omega_": "ω",
}
"""Mapping from CellDesigner escape sequences to their characters."""

LINK_ANCHOR_POSITION_TO_ANCHOR_NAME: dict[str, str] = {
    "NW": "north_west",
    "NNW": "north_north_west",
    "N": "north",
    "NNE": "north_north_east",
    "NE": "north_east",
    "ENE": "east_north_east",
    "E": "east",
    "ESE": "east_south_east",
    "SE": "south_east",
    "SSE": "south_south_east",
    "S": "south",
    "SSW": "south_south_west",
    "SW": "south_west",
    "WSW": "west_south_west",
    "W": "west",
    "WNW": "west_north_west",
}
"""Mapping from CellDesigner link-anchor position codes to momapy anchor names."""
