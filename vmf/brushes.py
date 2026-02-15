from typing import List, Tuple
import math


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
        uaxis: str = None,
        vaxis: str = None,
    ):
        self.id = id
        self.plane = plane  # 3 points, defining the plane
        self.vertices = (
            vertices if vertices else plane
        )  # All vertices of the face (usually 4)
        self.material = material
        self.uaxis = uaxis if uaxis else "[1 0 0 0] 0.25"
        self.vaxis = vaxis if vaxis else "[0 -1 0 0] 0.25"
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
        rotation_z: float = 0.0
    ):
        """
        Creates a box brush.
        
        Args:
            id: Unique ID
            pos: Position (x, y, z) - bottom-left corner
            size: Size (width, length, height)
            rotation_z: Rotation around Z axis in degrees (default 0)
        """
        self.id = id
        self.pos = pos
        self.size = size
        self.rotation_z = rotation_z
        self.sides: List[Side] = []
        self._create_box()
        
        # Apply rotation if needed
        if self.rotation_z != 0:
            self._rotate_z(self.rotation_z)

    def _create_box(self):
        """Creates a standard box brush."""
        x, y, z = self.pos
        w, l, h = self.size

        # Minimum and maximum coordinates
        x_min, y_min, z_min = x, y, z
        x_max, y_max, z_max = x + w, y + l, z + h

        side_id = self.id * 10

        # 6 sides of the cube - vertices MUST be counter-clockwise from outside!
        # Top (players walk on this side) - Z max, looking from above
        self.sides.append(
            Side(
                side_id + 1,
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_min, y_min, z_max),
                ],
                "[1 0 0 0] 0.25",
                "[0 -1 0 0] 0.25",
            )
        )

        # Bottom - Z min, looking from below
        self.sides.append(
            Side(
                side_id + 2,
                [
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_max, z_min),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_max, z_min),
                    Vertex(x_min, y_max, z_min),
                ],
                "[1 0 0 0] 0.25",
                "[0 -1 0 0] 0.25",
            )
        )

        # West (-X), looking from outside (west side)
        self.sides.append(
            Side(
                side_id + 3,
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_min, z_max),
                    Vertex(x_min, y_min, z_min),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_min, z_max),
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_min, y_max, z_min),
                ],
                "[0 1 0 0] 0.25",
                "[0 0 -1 0] 0.25",
            )
        )

        # East (+X), looking from outside (east side)
        self.sides.append(
            Side(
                side_id + 4,
                [
                    Vertex(x_max, y_max, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_min, z_max),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_max, y_max, z_min),
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_max, y_min, z_max),
                    Vertex(x_max, y_max, z_max),
                ],
                "[0 1 0 0] 0.25",
                "[0 0 -1 0] 0.25",
            )
        )

        # North (+Y), looking from outside (north side)
        self.sides.append(
            Side(
                side_id + 5,
                [
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_max, y_max, z_max),
                    Vertex(x_min, y_max, z_max),
                    Vertex(x_min, y_max, z_min),
                    Vertex(x_max, y_max, z_min),
                ],
                "[1 0 0 0] 0.25",
                "[0 0 -1 0] 0.25",
            )
        )

        # South (-Y), looking from outside (south side)
        self.sides.append(
            Side(
                side_id + 6,
                [
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_min, y_min, z_max),
                ],
                "DEV/DEV_MEASUREGENERIC01B",
                [
                    Vertex(x_max, y_min, z_min),
                    Vertex(x_min, y_min, z_min),
                    Vertex(x_min, y_min, z_max),
                    Vertex(x_max, y_min, z_max),
                ],
                "[1 0 0 0] 0.25",
                "[0 0 -1 0] 0.25",
            )
        )

    def _rotate_z(self, angle_degrees: float):
        """
        Rotate all vertices around Z axis (top-down rotation).
        Rotates around the center of the block.
        
        Args:
            angle_degrees: Rotation angle in degrees
        """
        # Convert to radians
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Calculate center of the block (before rotation)
        x, y, z = self.pos
        w, l, h = self.size
        center_x = x + w / 2
        center_y = y + l / 2
        
        # Rotate all vertices in all sides
        for side in self.sides:
            # Rotate plane vertices
            for vertex in side.plane:
                self._rotate_vertex(vertex, center_x, center_y, cos_a, sin_a)
            
            # Rotate all vertices (for vertices_plus)
            if side.vertices:
                for vertex in side.vertices:
                    self._rotate_vertex(vertex, center_x, center_y, cos_a, sin_a)
    
    def _rotate_vertex(
        self, vertex: Vertex, center_x: float, center_y: float,
        cos_a: float, sin_a: float
    ):
        """Rotate a single vertex around center point."""
        # Translate to origin
        dx = vertex.x - center_x
        dy = vertex.y - center_y
        
        # Rotate
        new_x = dx * cos_a - dy * sin_a
        new_y = dx * sin_a + dy * cos_a
        
        # Translate back
        vertex.x = new_x + center_x
        vertex.y = new_y + center_y
    
    def get_rotated_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get axis-aligned bounding box (AABB) of the rotated block.
        Returns (min_x, min_y, max_x, max_y) for collision detection.
        """
        if not self.sides or not self.sides[0].vertices:
            # Fallback to original bounds
            x, y, _ = self.pos
            w, l, _ = self.size
            return (x, y, x + w, y + l)
        
        # Get all vertices from first side (top) which has all corners
        vertices = self.sides[0].vertices
        
        x_coords = [v.x for v in vertices]
        y_coords = [v.y for v in vertices]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

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
