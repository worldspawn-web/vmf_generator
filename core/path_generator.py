import random
from typing import List
from vmf.brushes import Solid
from core.path_types import (
    PathPattern,
    PathSegment,
    SegmentDirection,
    create_pattern
)


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
        self.segment_length = 800  # Length of each segment
        self.max_blocks_per_row = 3  # Max blocks on same Y level
        self.block_types = ["medium", "large"]  # Which types to use
        self.randomize_sizes = True
        self.randomize_positions = True  # Randomize X positions
        self.grid_size = 32  # Grid size for snapping
        self.path_pattern = PathPattern.STRAIGHT  # Current pattern
        self.segments: List[PathSegment] = []  # Path segments

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

    def set_segment_length(self, length: float):
        """Sets the length of path segments."""
        self.segment_length = max(400, length)

    def set_path_pattern(self, pattern: PathPattern):
        """Sets the path pattern type."""
        self.path_pattern = pattern

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

    def generate_with_pattern(self) -> List[Solid]:
        """Generates blocks following a path pattern with corridors."""
        # Create segments based on pattern
        self.segments = create_pattern(
            self.path_pattern,
            self.block_count,
            self.segment_length,
            self.path_width
        )
        
        # Calculate positions for all segments
        current_pos = self.start_pos
        for segment in self.segments:
            segment.start_pos = current_pos
            segment.calculate_end_pos()
            current_pos = segment.end_pos
        
        solids = []
        
        # Generate blocks for each segment
        for seg_idx, segment in enumerate(self.segments):
            segment_solids = self._generate_segment_blocks(
                segment, solids, seg_idx
            )
            solids.extend(segment_solids)
        
        return solids

    def _generate_segment_blocks(
        self, segment: PathSegment, existing_solids: List[Solid], seg_idx: int
    ) -> List[Solid]:
        """Generate blocks for a single segment."""
        solids = []
        blocks_to_generate = segment.blocks
        blocks_generated = 0
        
        # Starting position for this segment
        sx, sy, sz = segment.start_pos
        ex, ey, ez = segment.end_pos
        
        # Calculate step along segment direction
        # block_size = (width, length, height) = (X, Y, Z)
        if segment.direction == SegmentDirection.FORWARD:
            progress_axis = 1  # Y axis
            fixed_axis = 0  # X axis (for random positioning)
            progress_size_idx = 1  # length (Y)
            fixed_size_idx = 0  # width (X)
            step_direction = 1
        elif segment.direction == SegmentDirection.RIGHT:
            progress_axis = 0  # X axis
            fixed_axis = 1  # Y axis
            progress_size_idx = 0  # width (X)
            fixed_size_idx = 1  # length (Y)
            step_direction = 1
        elif segment.direction == SegmentDirection.LEFT:
            progress_axis = 0  # X axis
            fixed_axis = 1  # Y axis
            progress_size_idx = 0  # width (X)
            fixed_size_idx = 1  # length (Y)
            step_direction = -1
        elif segment.direction == SegmentDirection.BACK:
            progress_axis = 1  # Y axis
            fixed_axis = 0  # X axis
            progress_size_idx = 1  # length (Y)
            fixed_size_idx = 0  # width (X)
            step_direction = -1
        else:
            return solids
        
        current_progress = [sx, sy, sz]
        current_row_blocks = 0
        blocks_in_current_row = 1 if seg_idx == 0 else random.randint(1, self.max_blocks_per_row)
        
        while blocks_generated < blocks_to_generate:
            # Select block size
            if self.randomize_sizes:
                block_type = random.choice(self.block_types)
            else:
                block_type = self.block_types[0]
            
            block_size = self.BLOCK_SIZES[block_type]
            
            # Calculate position
            block_pos = list(current_progress)
            
            # Add randomness to fixed axis within corridor
            if self.randomize_positions and blocks_generated > 0:
                half_width = segment.width / 2
                center = segment.start_pos[fixed_axis]
                offset_range = (segment.width - block_size[fixed_size_idx]) / 2
                block_pos[fixed_axis] = center + random.uniform(-offset_range, offset_range)
            
            # Snap to grid
            block_pos[0] = self.snap_to_grid(block_pos[0])
            block_pos[1] = self.snap_to_grid(block_pos[1])
            block_pos[2] = self.snap_to_grid(block_pos[2])
            
            block_tuple = tuple(block_pos)
            
            # Check corridor bounds and collisions
            if not segment.is_position_in_corridor(block_tuple, block_size):
                # Out of corridor, move to next row
                current_row_blocks = blocks_in_current_row
            else:
                # Check collision with existing blocks
                attempts = 0
                max_attempts = 100
                all_solids = existing_solids + solids
                
                collision = self._check_collision(block_tuple, block_size, all_solids)
                
                while collision and attempts < max_attempts:
                    # Try different position on fixed axis
                    half_width = segment.width / 2
                    center = segment.start_pos[fixed_axis]
                    offset_range = (segment.width - block_size[fixed_size_idx]) / 2
                    block_pos[fixed_axis] = center + random.uniform(-offset_range, offset_range)
                    block_pos[fixed_axis] = self.snap_to_grid(block_pos[fixed_axis])
                    
                    block_tuple = tuple(block_pos)
                    
                    # Recheck corridor and collision
                    if not segment.is_position_in_corridor(block_tuple, block_size):
                        break
                    collision = self._check_collision(block_tuple, block_size, all_solids)
                    attempts += 1
                
                if attempts >= max_attempts or not segment.is_position_in_corridor(block_tuple, block_size):
                    # Can't place, move to next row
                    current_row_blocks = blocks_in_current_row
                else:
                    # Successfully placed
                    solid = Solid(
                        id=len(existing_solids) + len(solids) + 10,
                        pos=block_tuple,
                        size=block_size,
                    )
                    solids.append(solid)
                    blocks_generated += 1
                    current_row_blocks += 1
            
            # Check if we should move to next row
            if current_row_blocks >= blocks_in_current_row:
                # Find max size in current row along progress axis
                if solids:
                    row_start_idx = len(solids) - current_row_blocks
                    max_size = max(
                        [s.size[progress_size_idx] for s in solids[row_start_idx:]],
                        default=0
                    )
                    current_progress[progress_axis] += (max_size + self.spacing) * step_direction
                else:
                    current_progress[progress_axis] += self.spacing * step_direction
                
                # Check if we've gone past segment end
                if step_direction > 0:
                    if current_progress[progress_axis] >= segment.end_pos[progress_axis]:
                        break
                else:
                    if current_progress[progress_axis] <= segment.end_pos[progress_axis]:
                        break
                
                # Next row
                blocks_in_current_row = random.randint(1, self.max_blocks_per_row)
                current_row_blocks = 0
        
        return solids

    def get_block_size_info(self) -> str:
        """Returns information about block sizes."""
        info_lines = []
        for name, size in self.BLOCK_SIZES.items():
            info_lines.append(f"{name}: {size[0]}x{size[1]}x{size[2]}")
        return "\n".join(info_lines)
