"""Block shape definitions and management."""

import json
import os
from typing import List, Tuple, Dict
from enum import Enum
from dataclasses import dataclass


class ShapeType(Enum):
    """Predefined shape types."""

    SQUARE = "square"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    CIRCLE = "circle"
    PARALLELOGRAM = "parallelogram"
    TRAPEZOID = "trapezoid"
    PENTAGON = "pentagon"
    RHOMBUS = "rhombus"
    HEXAGON = "hexagon"
    OCTAGON = "octagon"
    OVAL = "oval"
    ELLIPSE = "ellipse"
    CUSTOM = "custom"


SHAPE_DISPLAY_NAMES = {
    ShapeType.SQUARE: "Square",
    ShapeType.RECTANGLE: "Rectangle",
    ShapeType.TRIANGLE: "Triangle",
    ShapeType.CIRCLE: "Circle",
    ShapeType.PARALLELOGRAM: "Parallelogram",
    ShapeType.TRAPEZOID: "Trapezoid",
    ShapeType.PENTAGON: "Pentagon",
    ShapeType.RHOMBUS: "Rhombus",
    ShapeType.HEXAGON: "Hexagon",
    ShapeType.OCTAGON: "Octagon",
    ShapeType.OVAL: "Oval",
    ShapeType.ELLIPSE: "Ellipse",
    ShapeType.CUSTOM: "Custom",
}


@dataclass
class BlockShape:
    """
    Represents a block shape configuration.

    Attributes:
        shape_type: Type of shape
        name: Display name (for custom shapes)
        enabled: Whether this shape is enabled for generation
        vertices: List of vertices for custom shapes (normalized 0-1)
        size_multiplier: Size multiplier (width, length)
    """

    shape_type: ShapeType
    name: str
    enabled: bool = False
    vertices: List[Tuple[float, float]] = None
    size_multiplier: Tuple[float, float] = (1.0, 1.0)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "shape_type": self.shape_type.value,
            "name": self.name,
            "enabled": self.enabled,
            "vertices": self.vertices,
            "size_multiplier": self.size_multiplier,
        }

    @staticmethod
    def from_dict(data: dict) -> "BlockShape":
        """Create from dictionary."""
        return BlockShape(
            shape_type=ShapeType(data["shape_type"]),
            name=data["name"],
            enabled=data.get("enabled", False),
            vertices=data.get("vertices"),
            size_multiplier=tuple(data.get("size_multiplier", (1.0, 1.0))),
        )


class ShapeManager:
    """Manages block shapes and their configurations."""

    def __init__(self, config_path: str = "block_shapes.json"):
        """
        Initialize shape manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.shapes: List[BlockShape] = []
        self._initialize_default_shapes()

        # Load config or save default if doesn't exist
        if os.path.exists(config_path):
            self.load_config()
        else:
            self.save_config()

    def _initialize_default_shapes(self):
        """Initialize default predefined shapes."""
        # Square (enabled by default)
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.SQUARE,
                name=SHAPE_DISPLAY_NAMES[ShapeType.SQUARE],
                size_multiplier=(1.0, 1.0),
                enabled=True,
            )
        )

        # Rectangle (enabled by default)
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.RECTANGLE,
                name=SHAPE_DISPLAY_NAMES[ShapeType.RECTANGLE],
                size_multiplier=(1.0, 2.0),
                enabled=True,
            )
        )

        # Triangle (approximated with 3 vertices)
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.TRIANGLE,
                name=SHAPE_DISPLAY_NAMES[ShapeType.TRIANGLE],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Circle (approximated with octagon)
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.CIRCLE,
                name=SHAPE_DISPLAY_NAMES[ShapeType.CIRCLE],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Parallelogram
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.PARALLELOGRAM,
                name=SHAPE_DISPLAY_NAMES[ShapeType.PARALLELOGRAM],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Trapezoid
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.TRAPEZOID,
                name=SHAPE_DISPLAY_NAMES[ShapeType.TRAPEZOID],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Pentagon
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.PENTAGON,
                name=SHAPE_DISPLAY_NAMES[ShapeType.PENTAGON],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Rhombus
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.RHOMBUS,
                name=SHAPE_DISPLAY_NAMES[ShapeType.RHOMBUS],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Hexagon
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.HEXAGON,
                name=SHAPE_DISPLAY_NAMES[ShapeType.HEXAGON],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Octagon
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.OCTAGON,
                name=SHAPE_DISPLAY_NAMES[ShapeType.OCTAGON],
                size_multiplier=(1.0, 1.0),
            )
        )

        # Oval
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.OVAL,
                name=SHAPE_DISPLAY_NAMES[ShapeType.OVAL],
                size_multiplier=(1.0, 1.5),
            )
        )

        # Ellipse
        self.shapes.append(
            BlockShape(
                shape_type=ShapeType.ELLIPSE,
                name=SHAPE_DISPLAY_NAMES[ShapeType.ELLIPSE],
                size_multiplier=(1.5, 1.0),
            )
        )

    def add_custom_shape(self, name: str, vertices: List[Tuple[float, float]]):
        """Add a custom shape."""
        shape = BlockShape(
            shape_type=ShapeType.CUSTOM,
            name=name,
            vertices=vertices,
            enabled=False,
            probability=0.0,
        )
        self.shapes.append(shape)
        self.save_config()

    def remove_custom_shape(self, name: str):
        """Remove a custom shape by name."""
        self.shapes = [
            s
            for s in self.shapes
            if not (s.shape_type == ShapeType.CUSTOM and s.name == name)
        ]
        self.save_config()

    def get_custom_shapes(self) -> List[BlockShape]:
        """Get all custom shapes."""
        return [s for s in self.shapes if s.shape_type == ShapeType.CUSTOM]

    def get_enabled_shapes(self) -> List[BlockShape]:
        """Get all enabled shapes."""
        return [s for s in self.shapes if s.enabled]

    def save_config(self):
        """Save configuration to file."""
        data = {"shapes": [s.to_dict() for s in self.shapes]}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update existing shapes and add custom ones
            loaded_shapes = {s["shape_type"]: s for s in data.get("shapes", [])}

            # Update predefined shapes
            for shape in self.shapes:
                key = shape.shape_type.value
                if key in loaded_shapes:
                    loaded = loaded_shapes[key]
                    shape.enabled = loaded.get("enabled", False)

            # Add custom shapes
            for shape_data in data.get("shapes", []):
                if shape_data["shape_type"] == ShapeType.CUSTOM.value:
                    shape = BlockShape.from_dict(shape_data)
                    if shape.name not in [s.name for s in self.shapes]:
                        self.shapes.append(shape)

        except Exception as e:
            print(f"Error loading shape config: {e}")
