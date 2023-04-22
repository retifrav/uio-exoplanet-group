"""
Getting data from various databases
via [TAP](https://www.ivoa.net/documents/TAP/) interface.
"""

# what is available for importing from __init__.py
# __all__ = [
#     "services",
#     "queryService",
#     ...
# ]

import pyvo

from typing import Optional, Dict, List

services: Dict[str, Dict] = {
    "NASA":
    {
        # case-sensitive URL
        "endpoint": "https://exoplanetarchive.ipac.caltech.edu/TAP",
        "parameters-that-are-strings":
        [
            "st_metratio",
            "st_spectype"
        ],
        "parameters-that-have-errors":
        [
            "period",
            "pl_massj",
            "pl_orbper",
            "pl_orbsmax",
            "pl_radj",
            "semi_major_axis"
        ]
    },
    "PADC":
    {
        "endpoint": "http://voparis-tap-planeto.obspm.fr/tap"
    },
    "GAIA":
    {
        "endpoint": "https://gea.esac.esa.int/tap-server/tap"
    }
}
"""
Dictionary of the most common TAP services.
"""

mappings: Dict[str, Dict] = {
    "NASA-to-PADC":
    {
        "planets":
        {
            "ima_flag": "ima_flag",
            "pl_massj": "mass",
            "pl_massjerr1": "mass_error_max",
            "pl_massjerr2": "mass_error_min",
            "pl_massjlim": "pl_massjlim",
            "pl_name": "granule_uid",
            "pl_orbeccen": "eccentricity",
            "pl_orbincl": "inclination",
            "pl_orbper": "period",
            "pl_orbpererr1": "period_error_max",
            "pl_orbpererr2": "period_error_min",
            "pl_orbperlim": "pl_orbperlim",
            "pl_orbsmax": "semi_major_axis",
            "pl_orbsmaxerr1": "semi_major_axis_error_max",
            "pl_orbsmaxerr2": "semi_major_axis_error_min",
            "pl_orbsmaxlim": "pl_orbsmaxlim",
            "pl_radj": "radius",
            "pl_radjerr1": "radius_error_max",
            "pl_radjerr2": "radius_error_min",
            "pl_radjlim": "pl_radjlim",
            "rv_flag": "rv_flag",
            "tran_flag": "tran_flag",
            "ttv_flag": "ttv_flag"
        },
        "stars":
        {
            "cb_flag": "cb_flag",
            "hostname": "star_name",
            "ra": "ra",
            "st_age": "star_age",
            "st_lum": "st_lum",
            "st_mass": "star_mass",
            "st_met": "star_metallicity",
            "st_metratio": "st_metratio",
            "st_rad": "star_radius",
            "st_rotp": "st_rotp",
            "st_spectype": "star_spec_type",
            "st_teff": "star_teff",
            "sy_dist": "sy_dist",
            "sy_pnum": "sy_pnum",
            "sy_snum": "sy_snum"
        }
    }
}
"""
Mapping tables columns between different databases.
"""


def getServiceEndpoint(tapServiceName: str) -> Optional[str]:
    """
    Example:

    ``` py
    from uio.utility.databases import tap

    tapServiceEndpoint = tap.getServiceEndpoint("PADC")
    if tapServiceEndpoint is None:
        raise SystemError("No endpoint for such TAP service in the list")
    print(tapServiceEndpoint)
    ```
    """
    tapService = services.get(tapServiceName)
    if tapService:
        tapServiceEndpoint = tapService.get("endpoint")
        if tapServiceEndpoint:
            return tapServiceEndpoint
        else:
            f"[ERROR] {tapServiceName} has no registered endpoint"
            return None
    else:
        print(
            f"[ERROR] There is no TAP service under the name {tapServiceName}"
        )
        return None


def queryService(
    tapEndpoint: str,
    adqlQuery: str
) -> Optional[pyvo.dal.tap.TAPResults]:
    """
    Example:

    ``` py
    from uio.utility.databases import tap

    tbl = tap.queryService(
        "http://voparis-tap-planeto.obspm.fr/tap",
        " ".join((
            "SELECT star_name, granule_uid, mass, radius, period, semi_major_axis",
            "FROM exoplanet.epn_core",
            "WHERE star_name = 'Kepler-107'",
            "ORDER BY granule_uid"
        ))
    ).to_table().to_pandas()
    #print(tbl)
    ```
    """
    tapService = pyvo.dal.TAPService(tapEndpoint)
    results = tapService.search(adqlQuery)
    if len(results):
        return results
    else:
        return None
