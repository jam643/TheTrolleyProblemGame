<div style="text-align: center;">
    <img src="images/TrolleyProblemBanner.gif" width="1000">
</div>


![License](https://shields.io/badge/license-Apache%202-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jam643/)


## About This Project

## Gameplay Mode

<img src="images/gameplay.gif" width="800">

## Sandbox Mode

The game conceals an underlying framework of tunable path tracking controllers, customizable vehicle dynamics models, spline-based path generation, etc. These modules can be  

### Path Tracking Controllers

Users can tune (in realtime) and experiment with several path tracking controllers of varying complexity. See below video for example: 

<img src="images/path_trackers.gif" width="800">

Brief comparison of the various path tracking controllers implemented:

|                        | **Description**                                                                                               | **Model Used**                  | **Robustness**                                                        | **Stability**                                                                           | **Linearity**                     |
| ---------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | --------------------------------- |
| **Pure Pursuit**       | Geometric method that follows a look-ahead point on the path based on vehicle speed                           | Kinematic, simple bicycle model | Less robust to dynamic changes, struggles with sharp turns            | Generally stable but can lose stability in sharp turns, high speeds, or small lookahead | Non-linear                        |
| **Stanley Controller** | Minimizes cross-track error and heading error through a proportional control strategy                         | Kinematic, bicycle model        | Robust to small disturbances, but may oscillate in certain conditions | Lyapunov stable, particularly for straight paths                                        | Non-linear                        |
| **Kinematic LQR**      | Uses linear quadratic regulator to minimize deviations in position and velocity using a kinematic model       | Kinematic, linearized model     | Moderately robust with careful tuning                                 | Stable within the Region of Attraction (ROA)                                            | Linearized around operating point |
| **Dynamic LQR**        | Uses linear quadratic regulator to minimize deviations including dynamic effects like forces and acceleration | Dynamic, linearized model       | Highly robust, especially in dynamic and high-speed environments      | Stable within the Region of Attraction (ROA)                                            | Linearized around operating point |


User can also click the `Docs` button to go to a Jupyter Notebook page containing derivations of some of the control strategies as well as sample code calling the controllers:

<img src="images/path_tracker_docs.gif" width="800">

### Vehicle Model


### Path Generation



## Setup
First time only:
```bash
pip install --user pipenv
pip install --user pipenv-shebang
pipenv sync
pipenv run ipykernel_setup
```
Start game:
```bash
./TheTrolleyProblemGame.py
```