# Copyright 2026 CoChem Project Family. All rights reserved.
# Apache License 2.0
"""
Spectral Database API Interface for SDBS and NIST WebBook.
Strictly adheres to Anti-Spoofing Directives: never returns synthetic or mocked spectra.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def fetch_sdbs(inchi_key: str) -> Dict[str, Any]:
    """
    Fetch experimental IR/NMR spectrum from SDBS for a given InChIKey.
    Raises NotImplementedError if active web connector is unconfigured.
    """
    if not inchi_key or not isinstance(inchi_key, str):
        raise ValueError("Invalid InChIKey supplied to fetch_sdbs")
    
    logger.info(f"Querying SDBS for InChIKey: {inchi_key}")
    # SDBS does not provide a public REST API without active session scrapers or credentials.
    raise NotImplementedError(
        f"[MISSING DATA] Direct SDBS programmatic API access is not configured for InChIKey '{inchi_key}'. "
        "Provide authenticated repository credentials or use local empirical reference libraries."
    )

def fetch_nist(inchi_key: str) -> Dict[str, Any]:
    """
    Fetch experimental mass spectrometry / IR data from NIST Chemistry WebBook.
    """
    if not inchi_key or not isinstance(inchi_key, str):
        raise ValueError("Invalid InChIKey supplied to fetch_nist")
        
    logger.info(f"Querying NIST WebBook for InChIKey: {inchi_key}")
    raise NotImplementedError(
        f"[MISSING DATA] NIST WebBook connector requires configured network endpoint for InChIKey '{inchi_key}'."
    )
