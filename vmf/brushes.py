from typing import List, Tuple


class Vertex:
    """3D point in space."""

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        # For plane, we need parentheses, for vertices_plus, we don't
        return f"({self.x} {self.y} {self.z})"

    def to_vertex_string(self) -> str:
        """Returns coordinates WITHOUT parentheses for vertices_plus."""
        return f"{self.x} {self.y} {self.z}"


class Side:
    """Side of a brush (face)."""

    def __init__(
        self,
        id: int,
        plane: List[Vertex],
        material: str = "TOOLS/TOOLSNODRAW",
        vertices: List[Vertex] = None,
    ):
        self.id = id
        self.plane = plane  # 3 points, defining the plane
        self.vertices = (
            vertices if vertices else plane
        )  # All vertices of the face (usually 4)
        self.material = material
        self.uaxis = "[1 0 0 0] 0.25"
        self.vaxis = "[0 -1 0 0] 0.25"
        self.rotation = 0
        self.lightmapscale = 16
        self.smoothing_groups = 0

    def to_vmf(self) -> str:
        """Converts side to VMF format."""
        # Form vertices_plus section (WITHOUT parentheses!)
        vertices_vmf = "\n".join(
            f'\t\t\t"v" "{v.to_vertex_string()}"' for v in self.vertices
        )

        return f"""	side
	{{
		"id" "{self.id}"
		"plane" "{self.plane[0]} {self.plane[1]} {self.plane[2]}"
		vertices_plus
		{{
{vertices_vmf}
		}}
		"material" "{self.material}"
		"uaxis" "{self.uaxis}"
		"vaxis" "{self.vaxis}"
		"rotation" "{self.rotation}"
		"lightmapscale" "{self.lightmapscale}"
		"smoothing_groups" "{self.smoothing_groups}"
	}}"""


class Solid:
    """Brush (solid block)."""

    def __init__(
        self,
        id: int,
        pos: Tuple[float, float, float],
        size: Tuple[float, float, float] = (128, 128, 32),
    ):
        self.id = id
        self.pos = pos
        self.size = size
        self.sides: List[Side] = []
        self._create_box()

    def _create_box(self):
        """Creates a standard box brush."""
        x, y, z = self.pos
        w, l, h = self.size

        # Minimum and maximum coordinates
        x_min, y_min, z_min = x, y, z
        x_max, y_max, z_max = x + w, y + l, z + h

        side_id = self.id * 10

        # 6 sides of the cube
        # Top (players walk on this side) - Z max
        self.sides.append(
            Side(
                side_id + 1,
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                ],
                "DEV/DEV_MEASUREGENERIC01B",  # Видимая текстура
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_min, y_min, z_max),
                ],
            )
        )

        # Bottom - Z min
        self.sides.append(
            Side(
                side_id + 2,
                [
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_max, z_min),
                ],
                "TOOLS/TOOLSNODRAW",
                [
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_max, z_min),
                    Vertex(x_min, y_max, z_min),
                ],
            )
        )

        # North (+Y)
        self.sides.append(
            Side(
                side_id + 3,
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                    Vertex(x_max, y_max, z_min),
                ],
                "TOOLS/TOOLSNODRAW",
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                    Vertex(x_max, y_max, z_min),
                    Vertex(x_max, y_max, z_max),
                ],
            )
        )

        # South (-Y)
        self.sides.append(
            Side(
                side_id + 4,
                [
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_min, y_min, z_min),
                ],
                "TOOLS/TOOLSNODRAW",
                [
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_min, y_min, z_max),
                ],
            )
        )

        # East (+X)
        self.sides.append(
            Side(
                side_id + 5,
                [
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_max, y_min, z_min),
                ],
                "TOOLS/TOOLSNODRAW",
                [
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_max, z_min),
                ],
            )
        )

        # West (-X)
        self.sides.append(
            Side(
                side_id + 6,
                [
                    Vertex(x_min, y_min, z_max),
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                ],
                "TOOLS/TOOLSNODRAW",
                [
                    Vertex(x_min, y_min, z_max),
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                    Vertex(x_min, y_min, z_min),
                ],
            )
        )

    def to_vmf(self) -> str:
        """Converts solid to VMF format."""
        sides_vmf = "\n".join(side.to_vmf() for side in self.sides)
        return f"""solid
{{
	"id" "{self.id}"
{sides_vmf}
	editor
	{{
		"color" "0 180 0"
		"visgroupshown" "1"
		"visgroupautoshown" "1"
	}}
}}"""
