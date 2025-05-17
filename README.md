<<<<<<< HEAD
# Billiard Ball Physics Simulation

A comprehensive billiard physics simulator that models realistic ball dynamics, collisions, and spin effects with an interactive visualization and analysis dashboard.

![Project Screenshot](https://via.placeholder.com/800x400?text=Billiard+Simulation+Screenshot)

## Features

- **Realistic Physics Engine**:
  - Elastic collisions between balls
  - Ball-cushion collisions with accurate rebound angles
  - Rolling and sliding friction modeling
  - Angular momentum and spin effects
  - Customizable physics parameters

- **Real-time Visualization**:
  - Interactive Pygame-based interface
  - Realistic ball movement and collision visualization
  - Shot placement and power controls
  - Slow-motion replay capabilities

- **Analysis Dashboard**:
  - Interactive Dash-based web dashboard
  - Real-time parameter adjustments
  - Ball trajectory analysis
  - Performance metrics and statistics
  - Shot outcome prediction

## Demo

https://github.com/yourusername/billiard-simulation/assets/demo.gif

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/billiard-simulation.git
cd billiard-simulation
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Simulation

To run the interactive simulation:
```bash
python main.py
```

### Running the Analysis Dashboard

To run only the analysis dashboard:
```bash
python dashboard.py
```

### Controls

- **Left Mouse Button**: Place the cue ball
- **Right Mouse Button**: Adjust shot power and direction
- **Space**: Execute shot
- **R**: Reset table
- **ESC**: Exit simulation

## Packaging with PyInstaller

The application can be packaged as a standalone executable using PyInstaller.

### Prerequisites
- PyInstaller: `pip install pyinstaller`
- All dependencies listed in requirements.txt

### Build Package
```bash
# Option 1: Use the provided batch file (Windows)
build_package.bat

# Option 2: Manual build using PyInstaller
pyinstaller --clean billiard_simulation.spec
```

### Run Packaged Application
After building, you'll find the executables in the `dist/billiard_simulation` directory:

- `billiard_simulation.exe` - Run the interactive visualization
- `billiard_dashboard.exe` - Run the analysis dashboard

You can also use the included `run_packaged_app.bat` batch file to choose which application to run.

## Project Structure

```
billiard-simulation/
│
├── main.py               # Main entry point for the simulation
├── billiard_app.py       # Application entry point for packaged versions
├── physics.py            # Physics engine implementation
├── visualization.py      # Pygame visualization components
├── dashboard.py          # Dash-based analysis dashboard
│
├── build_package.bat     # Windows batch file for building with PyInstaller
├── run_packaged_app.bat  # Batch file to run the packaged application
│
├── requirements.txt      # Python dependencies
├── billiard_simulation.spec  # PyInstaller specification file
│
└── README.md             # This file
```

## Development

### Adding New Features

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Roadmap

- [ ] Add multiplayer support
- [ ] Implement additional game modes (8-ball, 9-ball, etc.)
- [ ] Create machine learning model for shot prediction
- [ ] Enhance graphics with 3D rendering

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The physics equations are based on research by [relevant paper or author]
- Special thanks to [contributors]

## Contact

Your Name - [@yourusername](https://twitter.com/yourusername) - email@example.com

Project Link: [https://github.com/yourusername/billiard-simulation](https://github.com/yourusername/billiard-simulation)
=======
# billiard-simulation
>>>>>>> 350c1483d414098dfc409e134c33ca521e9bb166
