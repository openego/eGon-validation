from egon_validation.rules.base import SqlRule, Severity
from egon_validation.rules.registry import register

# Germany's official area in km²
GERMANY_TOTAL_AREA_KM2 = 357386.0

@register(
    task="germanyAreaComparison",
    table="boundaries.vg250_krs",
    rule_id="GERMANY_TOTAL_AREA_CHECK",
    geom_column="geometry",
    expected_area_km2=GERMANY_TOTAL_AREA_KM2,
    tolerance=0.01,  # 1% tolerance
)
class GermanyAreaAggregationValidation(SqlRule):
    """Validates that the sum of all Kreise geometries equals Germany's total area.

    This rule checks if the accumulated area of all polygons in the boundaries.vg250_krs
    table (German counties/Kreise) sums up to the expected total area of Germany.

    Args:
        rule_id: Unique identifier for this rule instance
        task: Task identifier (e.g., "validation-test")
        table: Full table name including schema (e.g., "boundaries.vg250_krs")
        geom_column: Name of the geometry column (default: "geometry")
        expected_area_km2: Expected total area in km² (default: 357386 km²)
        tolerance: Relative tolerance for comparison (default: 0.01 = 1%)
    """

    def get_query(self, ctx):
        geom_column = self.params.get("geom_column", "geometry")

        # Use ST_Transform to EPSG:3035 (ETRS89-LAEA) for accurate area calculation
        # Then convert to km² by dividing by 1,000,000
        return f"""
        SELECT
            COUNT(*) as total_kreise,
            SUM(ST_Area(ST_Transform({geom_column}, 3035))) / 1000000.0 as total_area_km2,
            MIN(ST_Area(ST_Transform({geom_column}, 3035))) / 1000000.0 as min_area_km2,
            MAX(ST_Area(ST_Transform({geom_column}, 3035))) / 1000000.0 as max_area_km2
        FROM {self.table}
        WHERE {geom_column} IS NOT NULL
        """

    def postprocess(self, row, ctx):
        total_kreise = int(row.get("total_kreise") or 0)
        total_area_km2 = float(row.get("total_area_km2") or 0.0)
        min_area_km2 = float(row.get("min_area_km2") or 0.0)
        max_area_km2 = float(row.get("max_area_km2") or 0.0)

        expected_area_km2 = float(self.params.get("expected_area_km2", GERMANY_TOTAL_AREA_KM2))
        tolerance = float(self.params.get("tolerance", 0.01))

        # Calculate relative difference
        if expected_area_km2 > 0:
            rel_diff = abs(total_area_km2 - expected_area_km2) / expected_area_km2
        else:
            rel_diff = 1.0 if total_area_km2 > 0 else 0.0

        ok = rel_diff <= tolerance

        if ok:
            message = (
                f"Total area of {total_kreise} Kreise: {total_area_km2:.2f} km2 "
                f"(expected: {expected_area_km2:.2f} km2, diff: {rel_diff*100:.2f}%, "
                f"tolerance: {tolerance*100:.1f}%). "
                f"Min Kreis: {min_area_km2:.2f} km2, Max Kreis: {max_area_km2:.2f} km2"
            )
        else:
            message = (
                f"Total area mismatch! Calculated: {total_area_km2:.2f} km2, "
                f"Expected: {expected_area_km2:.2f} km2, Difference: {rel_diff*100:.2f}% "
                f"(exceeds tolerance of {tolerance*100:.1f}%). "
                f"Kreise count: {total_kreise}"
            )

        return self.create_result(
            success=ok,
            observed=total_area_km2,
            expected=expected_area_km2,
            message=message,
            column=self.params.get("geom_column", "geometry"),
            severity=Severity.ERROR if not ok else Severity.INFO,
        )