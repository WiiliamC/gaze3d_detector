# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

`pye3d` is a Python library implementing a 3D eye model for gaze tracking. It uses a two-sphere model (eyeball and pupil) to estimate 3D gaze direction from 2D pupil ellipses detected in eye images. The library includes C++ extensions (Cython) for performance-critical operations.

## Build System

This project uses **scikit-build** to build C++ extensions. The build process involves:
- CMake (for C++ compilation)
- Cython (for Python-C++ bindings)
- Eigen3 (C++ linear algebra library, required dependency)

### Installing Dependencies

**Using Conda (recommended):**
```bash
conda env create --file conda-env.yml
conda activate pye3d-conda
```

**Manual setup:**
```bash
# Install Eigen3 (required C++ dependency)
conda install -c conda-forge eigen

# Or on Ubuntu/Debian:
sudo apt-get install libeigen3-dev
```

### Building and Installing

```bash
# Editable install (development)
pip install -e ".[testing]"

# Production install
pip install .

# Build with custom Eigen3 location
Eigen3_DIR=/path/to/eigen pip install .
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_package.py

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov

# Run with legacy sklearn model testing (optional)
pytest --legacy-model-location /path/to/models
```

## Linting and Code Quality

This project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run individual tools
black pye3d/ tests/
flake8 pye3d/ tests/
isort --profile black pye3d/ tests/
```

**Configuration files:**
- `.flake8` - Flake8 settings (max line length: 88, compatible with Black)
- `pyproject.toml` - Black configuration
- `.pre-commit-config.yaml` - Pre-commit hooks

## Architecture

### High-Level Structure

```
pye3d/
├── detector_3d.py          # Main API: Detector3D class
├── camera.py               # CameraModel for camera parameters
├── observation.py          # Observation and storage classes
├── kalman.py               # Kalman filter for temporal smoothing
├── refraction.py           # Refraction correction models
├── eye_model/              # Two-sphere eye model implementation
│   ├── abstract.py         # Abstract base class
│   ├── base.py             # Synchronous TwoSphereModel
│   └── asynchronous.py     # Async TwoSphereModelAsync (background processing)
├── geometry/               # Geometric primitives and operations
│   ├── primitives.py       # Circle, Ellipse, Sphere, Line, Conic
│   ├── projections.py      # 3D-to-2D projection functions
│   ├── intersections.py    # Geometric intersection calculations
│   └── utilities.py        # Coordinate conversions (cart2sph, sph2cart)
└── cpp/                    # C++ extensions (Cython)
    ├── pupil_detection_3d.pyx   # 3D pupil detection algorithms
    ├── projections.pyx          # Fast projection functions
    ├── refraction_correction.pyx # Refraction correction
    └── *.h                      # C++ headers (Eigen3-based)
```

### Core Algorithm Flow

1. **Input**: 2D pupil ellipse from a pupil detector (e.g., `pupil-detectors`)
2. **Observation**: Convert to `Observation` object with ellipse parameters
3. **Model Update**: Add observation to three models:
   - Short-term model (10 observations, high confidence threshold)
   - Long-term model (binned storage, 30 observations)
   - Ultra-long-term model (600 observations, 60s forget time)
4. **Sphere Center Estimation**: Estimate eyeball center from accumulated observations
5. **Pupil Circle Prediction**: Predict 3D pupil circle using model estimates
6. **Kalman Filtering**: Apply temporal smoothing to predictions
7. **Refraction Correction**: Apply optical correction for corneal refraction
8. **Output**: 3D gaze direction (phi, theta), sphere center, pupil diameter

### Key Classes

- **`Detector3D`** (`detector_3d.py:89`): Main API class. Configurable thresholds, supports blocking and asynchronous modes.
- **`TwoSphereModel`** (`eye_model/base.py`): Core model implementing sphere center estimation and pupil prediction.
- **`Observation`** (`observation.py`): Encapsulates a single 2D pupil detection with timestamp and confidence.
- **`CameraModel`** (`camera.py`): Simple focal length and resolution container.
- **Geometric Primitives** (`geometry/primitives.py`): `Circle`, `Ellipse`, `Sphere` with projection/unprojection methods.

### C++ Extensions

Performance-critical code is implemented in C++ and exposed via Cython:
- `pupil_detection_3d`: Edge detection and sphere search algorithms
- `projections`: Fast 3D-to-2D projections using Eigen3
- `refraction_correction`: Optical refraction calculations

The C++ code uses **Eigen3** for linear algebra. Headers are in `pye3d/cpp/*.h`.

## Important Implementation Notes

- **Coordinate system**: Camera is at origin, looking down negative Z-axis. Image plane is at z = -focal_length.
- **Threading**: `TwoSphereModelAsync` runs model updates in a background thread. Use `DetectorMode.asynchronous` for non-blocking operation.
- **Model freezing**: `is_long_term_model_frozen` pauses model updates (useful during calibration).
- **Confidence thresholds**: Three tiers (swirski=0.7, kalman=0.98, short/long term=0.8/0.98) control data quality acceptance.
- **Refraction correction**: Uses precomputed lookup tables (msgpack format) or optional sklearn models.

## Common Development Tasks

**Add a new geometric primitive:**
1. Add class to `geometry/primitives.py` (follow `Primitive` abstract base)
2. Implement `__slots__` for memory efficiency
3. Add projection methods to `geometry/projections.py`

**Modify C++ extension:**
1. Edit `.pyx` or `.h` files in `pye3d/cpp/`
2. Rebuild with `pip install -e .`
3. Run tests to verify

**Update refraction models:**
- Models are stored as msgpack in `pye3d/refraction_models/`
- Legacy sklearn models require `joblib` and `scikit-learn` extras

## Documentation

- Full docs: https://pye3d-detector.readthedocs.io
- Build locally: `tox -e docs` (requires `sphinx`, `furo` theme)
- Source: `docs/` directory (RST format)

## References

- Swirski and Dodgson, 2013: "A fully-automatic temporal approach to single camera glint-free 3D eye model fitting"
- Dierkes, Kassner, and Bulling, 2019: "A fast approach to refraction-aware eye-model fitting and gaze prediction"
