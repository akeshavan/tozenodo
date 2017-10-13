import tozenodo as tz

zenodo_deps = tz.get_depositions()

assert len([d for d in zenodo_deps if d["title"] == "Data Manifest"]) == 0, "You already have a deposition for a data manifest"

metadata = tz.create_deposition_metadata("Data Manifest",
    "dataset",
    "Data manifest for all data uploaded to zenodo by the tozenodo python package.",
    [{"name": "Keshavan, Anisha", "affiliation": "University of Washington"}])

manifest_dep = tz.create_empty_deposition()

tz.update_deposition_metadata(manifest_dep["id"], metadata)
