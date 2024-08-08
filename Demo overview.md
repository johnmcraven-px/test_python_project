# PXH Demo - NYC Hackers!

## Overview

In this demo, we showcase several new components developed by PhysicsX, highlighting our advancements in data handling, application platform development, and job orchestration. The demo focuses on a simulation workflow that demonstrates the generation, running, tracking, visualization, and data management of simulations. 

### Key Components

1. **New Data Labeling and Handling Scheme** Embed tagging for experiment tracking.
   
1. **Application Platform** Enables quick development of React applications.

2. **Argo for Job Orchestration** Set up and run multiple jobs and sweeps from the UI.

## Simulation Workflow

The targeted application in this demo is a comprehensive simulation workflow. Below are the steps involved:

1. **Generate CAD** Based on a set of input parameters.
   
1. **Output STL Files** Generate STL files required for simulations.
   
1. **Generate Simulations** Create simulations based on STL geometry and additional parameters (e.g., mesh).
   
2. **Run Simulations** Use Docker containers managed by Argo to execute simulations.
   
1. **Visualize Data** Visualize the results of the simulations.
   
1. **Data Management** Manage all data, including simulation run history, in the background.

## Open Source Toolset

To enable scaling and experimentation without the need for licenses, we utilize a complete set of open-source tools. However, each component can be swapped out for licensed alternatives if needed.

### Tools Used

- **Blender** For CAD generation. <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Blender_logo_no_text.svg/2048px-Blender_logo_no_text.svg.png" alt="Blender Logo" width="100"/>
  
- **OpenFOAM** For running simulations. <img src="https://upload.wikimedia.org/wikipedia/commons/4/48/OpenFOAM_logo.svg" alt="OpenFOAM Logo" width="200"/>
  
- **Docker** To run and manage images.<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Docker_%28container_engine%29_logo.png/800px-Docker_%28container_engine%29_logo.png" alt="Docker Logo" width="200"/>
  
- **ParaView** For visualizing output. <img src="https://www.paraview.org/wp-content/uploads/2022/10/paraview.png" alt="ParaView Logo" width="100"/>
  
- **Python** Used throughout the workflow for various functions. <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/800px-Python-logo-notext.svg.png" alt="Python Logo" width="100"/>

## Conclusion

This demo showcases how using open-source tools can be effectively used to build scalable and experimental workflows. The modular nature of our platform allows for easy integration of licensed components, making it adaptable to various needs and preferences.
