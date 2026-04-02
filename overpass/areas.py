from dataclasses import dataclass, field


@dataclass
class Area:
    """Defines an OSM administrative area to query."""

    name: str
    filters: dict = field(default_factory=dict)
    admin_level: int = 7
    # When True, build_query uses area["name"=...]["admin_level"=...] instead
    # of bbox, which is more precise for areas with complex polygon boundaries
    # (e.g. Tokyo wards that share edges with many neighbours).
    use_area_query: bool = False
    # (south, west, north, east)
    bbox: tuple[float, float, float, float] | None = None
    # Areas that must be co-fetched for correct bbox-dedup.  For example, 新北市
    # geographically surrounds 臺北市, so querying NWT alone would pull in TPE
    # entities via the overlapping bbox.  Listing 臺北市 here ensures it is
    # fetched alongside NWT and participates in the dedup pass, so the results
    # for each area are clean.  Companions are transparent to callers: they do
    # not appear in the dict returned by batch_fetch unless the caller already
    # requested them.
    companions: list["Area"] = field(default_factory=list)

    @property
    def bbox_area(self) -> float:
        """Geographic area of bbox in degrees² (for dedup priority)."""
        if self.bbox is None:
            return float("inf")
        s, w, n, e = self.bbox
        return (n - s) * (e - w)


def resolve_area(
    name_input: str,
    aliases: dict[str, str],
    city_lookup: dict[str, "Area"],
) -> "Area":
    """Resolve a free-form name string to an Area.

    Resolution order:
      1. Alias table lookup (uppercased key).
      2. Direct city lookup by canonical name.
      3. Fallback: bare Area with the raw name (Nominatim will handle it).
    """
    key = name_input.upper()
    resolved_name = aliases.get(key, name_input)
    if resolved_name in city_lookup:
        return city_lookup[resolved_name]
    return Area(name=resolved_name)


__all__ = ["Area", "resolve_area"]
