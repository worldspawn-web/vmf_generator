import sys
import io

# Encoding setup for console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from core.path_generator import PathGenerator
from vmf.writer import VMFWriter


def test_generation():
    """Test generation of a simple path."""
    print("=" * 50)
    print("Test generation of VMF file")
    print("=" * 50)

    # Create generator
    generator = PathGenerator()
    generator.set_start_position(0, 0, 0)
    generator.set_block_count(5)
    generator.set_spacing(200)
    generator.set_randomize(True)

    print("\nGeneration parameters:")
    print("  Start position: (0, 0, 0)")
    print("  Block count: 5")
    print("  Distance: 200 units")
    print("  Randomization: Yes")

    # Generate
    print("\nGenerating blocks...")
    solids = generator.generate_straight_line()
    print(f"✅ Generated {len(solids)} blocks")

    # Print block information
    print("\nBlock information:")
    for i, solid in enumerate(solids):
        print(f"  Block {i+1}: position={solid.pos}, size={solid.size}")

    # Create VMF writer
    writer = VMFWriter()
    for solid in solids:
        writer.add_solid(solid)

    # Save
    output_file = "test_output.vmf"
    print(f"\nSaving to {output_file}...")
    writer.save(output_file)
    print("✅ File successfully saved!")

    # Check file size
    import os

    file_size = os.path.getsize(output_file)
    print(f"📁 File size: {file_size} bytes")

    print("\n" + "=" * 50)
    print("✅ Test completed successfully!")
    print("=" * 50)
    print(f"\nYou can open the file '{output_file}' in Hammer Editor!")


if __name__ == "__main__":
    test_generation()
