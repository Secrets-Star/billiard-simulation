import sys
import numpy as np
from physics import Ball, BilliardTable, PhysicsEngine
from visualization import BilliardVisualizer

def main():
    """Main entry point for the billiard simulation."""
    # Create the billiard table with default parameters
    table = BilliardTable(
        length=2.7,  # meters
        width=1.35,  # meters
        cushion_elasticity=0.7,
        friction=0.03
    )
    
    # Create the physics engine
    physics_engine = PhysicsEngine(table)
    
    # Set up a standard rack of balls
    physics_engine.setup_rack()
    
    # Create the visualizer
    visualizer = BilliardVisualizer(physics_engine)
    
    # Run the visualization
    visualizer.run()

if __name__ == "__main__":
    main()
