from typing import List
from vmf.brushes import Solid


class VMFWriter:
    """Class for writing VMF files."""

    def __init__(self):
        self.solids: List[Solid] = []
        self.version_info = 400
        self.editor_version = 400
        self.map_version = 1

    def add_solid(self, solid: Solid):
        """Adds solid (brush) to the map."""
        self.solids.append(solid)

    def clear(self):
        """Clears all solids."""
        self.solids = []

    def save(self, filepath: str):
        """Saves VMF file."""
        vmf_content = self._generate_vmf()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(vmf_content)

    def _generate_vmf(self) -> str:
        """Generates full VMF content."""
        # Generate solids and add indentation (tab) to each line
        solids_list = []
        for solid in self.solids:
            solid_text = solid.to_vmf()
            # Add tab to each non-empty line
            indented = "\n".join(
                "\t" + line if line.strip() else line for line in solid_text.split("\n")
            )
            solids_list.append(indented)
        solids_vmf = "\n".join(solids_list)

        vmf = f"""versioninfo
{{
	"editorversion" "{self.editor_version}"
	"editorbuild" "8456"
	"mapversion" "{self.map_version}"
	"formatversion" "100"
	"prefab" "0"
}}
visgroups
{{
}}
viewsettings
{{
	"bSnapToGrid" "1"
	"bShowGrid" "1"
	"bShowLogicalGrid" "0"
	"nGridSpacing" "64"
	"bShow3DGrid" "0"
}}
world
{{
	"id" "1"
	"mapversion" "1"
	"classname" "worldspawn"
	"skyname" "sky_day01_01"
	"maxpropscreenwidth" "-1"
	"detailvbsp" "detail.vbsp"
	"detailmaterial" "detail/detailsprites"
{solids_vmf}
}}
entity
{{
	"id" "2"
	"classname" "info_player_start"
	"angles" "0 0 0"
	"origin" "0 0 64"
	editor
	{{
		"color" "0 255 0"
		"visgroupshown" "1"
		"visgroupautoshown" "1"
		"logicalpos" "[0 0]"
	}}
}}
cameras
{{
	"activecamera" "-1"
}}
cordon
{{
	"mins" "(-1024 -1024 -1024)"
	"maxs" "(1024 1024 1024)"
	"active" "0"
}}
"""
        return vmf
