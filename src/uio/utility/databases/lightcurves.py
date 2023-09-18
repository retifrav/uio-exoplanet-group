"""
Getting light curves data.
"""

import lightkurve
import re

from typing import Optional, Dict, List, Pattern

# apparently, one cannot set long/short threshold,
# hence this dictionary
#
# there are actually more authors available,
# but we are only interested in these
#
authors: Dict[str, Dict] = {
    "Kepler":
    {
        "mission": "Kepler",
        "cadence":
        {
            "long": 1800,
            "short": 60
        }
    },
    "K2":
    {
        "mission": "K2",
        "cadence":
        {
            "long": 1800,
            "short": 60
        }
    },
    "SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": 600,
            "short": 120,
            "fast": 20
        }
    },
    "TESS-SPOC":
    {
        "mission": "TESS",
        "cadence":
        {
            "long": 600
        }
    }
}
"""
Dictionary of authors, their cadence values and mapping to missions.
"""

missionSectorRegExes: Dict[str, Pattern] = {
    "Kepler": re.compile(
        r"^Kepler\s\w+\s(\d+)$"  # Kepler Quarter 15
    ),
    "K2": re.compile(
        r"^K2\s\w+\s(\d+)$"  # K2 Campaign 12
    ),
    "TESS": re.compile(
        r"^TESS\s\w+\s(\d+)$"  # TESS Sector 40
    )
}
"""
Dictionary of regular expressions for extracting sectors.
"""


def getLightCurveStats(
    starName: str,
    detailed: bool = True
) -> Dict[str, Dict]:
    """
    Gather statistics about available cadence values for a given star.

    If `detailed` is set to `False`, then function will skip collecting
    cadence values count by sectors, so resulting statistics will only
    contain total count of values.

    Example:

    ``` py
    from uio.utility.databases import lightcurves

    stats = lightcurves.getLightCurveStats("Kepler-114")
    if not stats:
        raise ValueError("Didn't find any results for this star")
    #print(stats)
    ```
    """
    stats: Dict[str, Dict] = {}

    lghtcrvs = lightkurve.search_lightcurve(
        starName,
        author=tuple(authors.keys())
    )
    if len(lghtcrvs) != 0:
        tbl = lghtcrvs.table.to_pandas()[["author", "exptime", "mission"]]
        # print(tbl)

        for author, group in (tbl.groupby("author")):
            if author not in authors:
                raise ValueError(f"Unknown author: {author}")
            mission = authors[author]["mission"]
            if not stats.get(mission):
                stats[mission] = {}
            for cadence in ["long", "short", "fast"]:
                if cadence in authors[author]["cadence"]:
                    stats[mission][cadence] = {}
                    cadenceValue = authors[author]["cadence"][cadence]
                    # perhaps both of these should be normalized to int first
                    cadences = group.query("exptime == @cadenceValue")

                    # total count
                    stats[mission][cadence]["total"] = len(cadences)

                    if detailed:
                        # count by sectors
                        stats[mission][cadence]["by-sectors"] = {}
                        for m in cadences["mission"]:
                            sectorMatch = re.search(
                                missionSectorRegExes[mission],
                                m
                            )
                            if not sectorMatch:
                                raise ValueError(
                                    " ".join((
                                        "Couldn't extract sector from",
                                        f"this mission value: {m}"
                                    ))
                                )
                            sector = sectorMatch.group(1)
                            try:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector] += 1
                            except KeyError:
                                stats[mission][cadence][
                                    "by-sectors"
                                ][sector] = 1
    return stats


def getLightCurveIDs(
    starName: str
) -> Dict[str, List[str]]:
    """
    Based on available cadence values statistics for a given star,
    get names of missions and cadences. For instance, in order to pass
    them to `altaipony.lcio.from_mast()`.

    Example:

    ``` py
    from uio.utility.databases import lightcurves
    from altaipony.lcio import from_mast

    starName = "LTT 1445 A"
    lightCurveIDs = {}

    try:
        lightCurveIDs = lightcurves.getLightCurveIDs(starName)
    except ValueError as ex:
        print(f"Failed to get light curves missons and cadences. {ex}")
        raise
    if not lightCurveIDs:
        raise ValueError("Didn't find any results for this star")
    #print(lightCurveIDs)

    for m in lightCurveIDs.keys():
        #print(f"Mission: {m}")
        for c in lightCurveIDs[m]:
            #print(f"- {c}")
            flc = from_mast(
                starName,
                mode="LC",
                cadence=c,
                mission=m
            )
            #print(flc)
    ```
    """
    lightCurveIDs: Dict[str, List[str]] = {}

    stats: Dict[str, Dict] = getLightCurveStats(
        starName,
        detailed=False
    )
    if not stats:
        raise ValueError("Didn't find any results for this star")

    # the order matters, it goes from most important to least important,
    # and in fact long cadence is so not important that it is discarded
    # if there is fast or short cadence available
    cadencePriority = ["fast", "short", "long"]

    for m in stats.keys():
        lightCurveIDs[m] = []
        priorityThreshold = 0
        for cp in cadencePriority:
            # if there is already fast or short cadence in the list,
            # don't take long cadence
            if any(lightCurveIDs[m]) and priorityThreshold > 1:
                break
            if cp in stats[m]:
                # print(f"Count [{cp}]: {stats[m][cp]['total']}")
                totalCnt = stats[m][cp].get("total")
                if totalCnt and totalCnt != 0:
                    lightCurveIDs[m].append(cp)
                # else:
                #     print(
                #         " ".join((
                #             f"[WARNING] The [{cp}] cadence count",
                #             f"in [{m}] is 0 (or missing)"
                #         ))
                #     )
            priorityThreshold += 1

    return lightCurveIDs
