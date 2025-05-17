"""
Billiard Simulation Application
Main entry point for the packaged application
"""
import sys
import os
import argparse

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='Billiard Physics Simulation')
    parser.add_argument('--dashboard', action='store_true', help='Run the dashboard instead of the visualization')
    args = parser.parse_args()
    
    if args.dashboard:
        # Run the dashboard
        print("Starting Billiard Dashboard...")
        from dashboard import app
        app.run_server(debug=False, host='127.0.0.1')
    else:
        # Run the visualization
        print("Starting Billiard Simulation...")
        import pygame
        from physics import BilliardTable, PhysicsEngine
        from visualization import BilliardVisualizer
        
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
