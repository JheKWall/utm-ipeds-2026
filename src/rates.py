"""The five disposition measures defined in the design spec, section 4.

Each is a share of the entering first-time full-time cohort at the 8-year status
point. Kept as pure functions with no database or file access so they can be tested
directly.
"""

# The four IPEDS Outcome Measures dispositions. Mutually exclusive; they sum to the
# adjusted cohort.
DISPOSITIONS = ("awarded", "still_enrolled", "enrolled_elsewhere", "unknown")


def disposition_rates(counts: dict) -> dict:
    """Convert raw Outcome Measures counts into the five reported rates.

    Args:
        counts: keys 'cohort' plus the four names in DISPOSITIONS.

    Returns:
        The five rates as proportions (0..1).

    Raises:
        ValueError: if the cohort is not positive, or if the four dispositions do
            not sum to it -- which means a source variable has been mis-mapped.

    Note on naming: 'unknown_outcome_rate' is deliberately NOT called a dropout
    rate. It is a residual that also absorbs students who enrolled somewhere the
    National Student Clearinghouse does not cover.
    """
    cohort = counts["cohort"]
    if cohort <= 0:
        raise ValueError(f"cohort must be positive, got {cohort}")

    total = sum(counts[d] for d in DISPOSITIONS)
    if total != cohort:
        raise ValueError(f"dispositions do not sum to cohort: {total} != {cohort}")

    return {
        "completion_rate": counts["awarded"] / cohort,
        "still_enrolled_rate": counts["still_enrolled"] / cohort,
        "transfer_out_rate": counts["enrolled_elsewhere"] / cohort,
        "unknown_outcome_rate": counts["unknown"] / cohort,
        # Reported alongside completion because transferring out is mission success
        # for a community college, not failure (spec section 8.1).
        "completion_or_transfer_rate": (
            counts["awarded"] + counts["enrolled_elsewhere"]
        ) / cohort,
    }
