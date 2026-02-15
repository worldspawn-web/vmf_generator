import random
from typing import List
from vmf.brushes import Solid


class PathGenerator:
    """Generator of straight paths from blocks."""

    # Predefined block sizes (width, length, height)
    BLOCK_SIZES = {
        "small": (64, 64, 32),
        "medium": (96, 96, 32),
        "large": (128, 128, 32),
        "long": (128, 256, 32),
        "wide": (192, 128, 32),
    }

    def __init__(self):
        self.start_pos = (0, 0, 0)
        self.block_count = 10
        self.spacing = 150  # Distance between blocks on Y
        self.path_width = 512  # Width of generation zone (X axis)
        self.max_blocks_per_row = 3  # Max blocks on same Y level
        self.block_types = ["medium", "large"]  # Which types to use
        self.randomize_sizes = True
        self.randomize_positions = True  # Randomize X positions
        self.grid_size = 32  # Grid size for snapping

    def set_start_position(self, x: float, y: float, z: float):
        """Sets the start position."""
        self.start_pos = (x, y, z)

    def set_block_count(self, count: int):
        """Sets the number of blocks."""
        self.block_count = max(1, count)

    def set_spacing(self, spacing: float):
        """Sets the distance between blocks."""
        self.spacing = max(50, spacing)

    def set_block_types(self, types: List[str]):
        """Sets the types of blocks for generation."""
        valid_types = [t for t in types if t in self.BLOCK_SIZES]
        if valid_types:
            self.block_types = valid_types

    def set_randomize(self, randomize: bool):
        """Enables/disables randomization of sizes."""
        self.randomize_sizes = randomize

    def set_path_width(self, width: float):
        """Sets the width of generation zone."""
        self.path_width = max(128, width)

    def set_randomize_positions(self, randomize: bool):
        """Enables/disables randomization of X positions."""
        self.randomize_positions = randomize

    def set_max_blocks_per_row(self, max_blocks: int):
        """Sets the maximum number of blocks per row (Y level)."""
        self.max_blocks_per_row = max(1, min(max_blocks, 10))

    def set_grid_size(self, grid_size: int):
        """Sets the grid size for snapping."""
        self.grid_size = grid_size

    def snap_to_grid(self, value: float) -> float:
        """Snaps value to the nearest grid point."""
        return round(value / self.grid_size) * self.grid_size

    def _check_collision(
        self, pos: tuple, size: tuple, existing_solids: List[Solid]
    ) -> bool:
        """
        Check if a block at given position/size collides with existing blocks.
        Uses AABB (Axis-Aligned Bounding Box) collision detection.
        
        Args:
            pos: (x, y, z) position of new block
            size: (width, length, height) size of new block
            existing_solids: list of already placed blocks
            
        Returns:
            True if collision detected, False otherwise
        """
        x1, y1, z1 = pos
        w1, l1, h1 = size
        
        for solid in existing_solids:
            x2, y2, z2 = solid.pos
            w2, l2, h2 = solid.size
            
            # AABB collision check on all 3 axes
            collision_x = x1 < (x2 + w2) and (x1 + w1) > x2
            collision_y = y1 < (y2 + l2) and (y1 + l1) > y2
            collision_z = z1 < (z2 + h2) and (z1 + h1) > z2
            
            if collision_x and collision_y and collision_z:
                return True
                
        return False

    def generate_straight_line(self) -> List[Solid]:
        """Generates a straight line from blocks without collisions."""
        solids = []
        x, y, z = self.start_pos
        
        current_y = y  # Track actual Y position
        blocks_generated = 0
        current_row_blocks = 0
        blocks_in_current_row = 1  # First row always has 1 block (spawn)

        while blocks_generated < self.block_count:
            # Select the block size
            if self.randomize_sizes:
                block_type = random.choice(self.block_types)
            else:
                block_type = self.block_types[0]

            block_size = self.BLOCK_SIZES[block_type]

            # Calculate X position
            if self.randomize_positions and blocks_generated > 0:
                # Random position within path_width
                x_range = (self.path_width - block_size[0]) / 2
                block_x = x + random.uniform(-x_range, x_range)
            else:
                # Center the block on X (for first block)
                block_x = x - block_size[0] / 2
            
            block_z = z
            block_y = current_y

            # Snap to grid BEFORE collision check
            block_x = self.snap_to_grid(block_x)
            block_y = self.snap_to_grid(block_y)
            block_z = self.snap_to_grid(block_z)
            
            # Check for collisions and adjust position if needed
            attempts = 0
            max_attempts = 100
            collision = self._check_collision(
                (block_x, block_y, block_z), block_size, solids
            )
            
            while collision and attempts < max_attempts:
                # Try different X position
                x_range = (self.path_width - block_size[0]) / 2
                block_x = x + random.uniform(-x_range, x_range)
                block_x = self.snap_to_grid(block_x)
                
                collision = self._check_collision(
                    (block_x, block_y, block_z), block_size, solids
                )
                attempts += 1
            
            if attempts >= max_attempts:
                # Can't place block in current row, move to next row
                current_row_blocks = blocks_in_current_row
            else:
                # Successfully placed block
                solid = Solid(
                    id=blocks_generated + 10,
                    pos=(block_x, block_y, block_z),
                    size=block_size,
                )
                solids.append(solid)
                blocks_generated += 1
                current_row_blocks += 1

            # Check if we should move to next row
            if current_row_blocks >= blocks_in_current_row:
                # Find the tallest block in current row to calculate next Y
                row_start_idx = len(solids) - current_row_blocks
                max_length = max(
                    [s.size[1] for s in solids[row_start_idx:]],
                    default=0
                )
                current_y += max_length + self.spacing
                
                # Randomize blocks for next row (1 to max_blocks_per_row)
                if blocks_generated > 0:
                    blocks_in_current_row = random.randint(1, self.max_blocks_per_row)
                current_row_blocks = 0

        return solids

    def get_block_size_info(self) -> str:
        """Returns information about block sizes."""
        info_lines = []
        for name, size in self.BLOCK_SIZES.items():
            info_lines.append(f"{name}: {size[0]}x{size[1]}x{size[2]}")
        return "\n".join(info_lines)
