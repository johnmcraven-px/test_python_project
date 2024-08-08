import subprocess
import os
import pandas as pd

# Define the Docker container name
DOCKER_CONTAINER_NAME = "openfoam_container_new"

def run_command(command, check_output=True):
    """Run a shell command and log its output."""
    source_openfoam = "source /opt/openfoam10/etc/bashrc"
    docker_command = f"docker exec -it {DOCKER_CONTAINER_NAME} bash -c '{source_openfoam} && {command}'"
    print(f'Start command: {command}')
    result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
    print(f"Command: {command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    if check_output:
        result.check_returncode()
    return result

def copy_file_to_container(local_path, container_path):
    """Copy a file from the host to the Docker container."""
    docker_copy_command = f"docker cp '{local_path}' '{DOCKER_CONTAINER_NAME}:{container_path}'"
    result = subprocess.run(docker_copy_command, shell=True, capture_output=True, text=True)
    print(f"Copy Command: {docker_copy_command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    result.check_returncode()

def create_directory_structure_in_container(case_dir):
    dirs = [
        case_dir,
        os.path.join(case_dir, 'constant'),
        os.path.join(case_dir, 'constant/polyMesh'),
        os.path.join(case_dir, 'constant/triSurface'),
        os.path.join(case_dir, 'system'),
        os.path.join(case_dir, '0')
    ]
    for d in dirs:
        run_command(f"mkdir -p {d}")

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def create_openfoam_case(case_dir, stl_file):
    create_directory_structure_in_container(case_dir)
    
    # Copy the STL file to the container
    copy_file_to_container(stl_file, os.path.join(case_dir, 'constant/triSurface/propeller.stl'))

    # Create system/controlDict
    control_dict_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        location    "system";
        object      controlDict;
    }
    application     simpleFoam;

    startFrom       startTime;

    startTime       0;

    stopAt          endTime;

    endTime         10; // Adjust this as needed

    deltaT          5; // Increase this to speed up the simulation, but ensure stability

    writeControl    timeStep;

    writeInterval   10; // Adjust this to write results less frequently

    purgeWrite      0;

    writeFormat     ascii;

    writePrecision  6;

    writeCompression off;

    timeFormat      general;

    timePrecision   6;

    runTimeModifiable true;

    functions
    {
    }


// ************************************************************************* //
"""
    write_file("controlDict", control_dict_content)
    copy_file_to_container("controlDict", os.path.join(case_dir, 'system/controlDict'))
    os.remove("controlDict")

    # Create system/fvSchemes
    fv_schemes_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss linearUpwind grad(k);
    div(phi,epsilon) Gauss linearUpwind grad(epsilon);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear orthogonal;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         orthogonal;
}

fluxRequired
{
    default         no;
    p;
    phi;
    rho;
}

CourantNo       10; // Increase as needed, but ensure stability


// ************************************************************************* //
"""
    write_file("fvSchemes", fv_schemes_content)
    copy_file_to_container("fvSchemes", os.path.join(case_dir, 'system/fvSchemes'))
    os.remove("fvSchemes")

    # Create system/fvSolution
    fv_solution_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        tolerance       1e-6;
        relTol          0.1;
        smoother        DIC;
        nPreSweeps      0;
        nPostSweeps     2;
        nFinestSweeps   2;
        cacheAgglomeration true;
        nCellsInCoarsestLevel 10;
        agglomerator    faceAreaPair;
        mergeLevels     1;
    }

    "(U|k|epsilon|omega)"
    {
        solver          PBiCG;
        preconditioner  DILU;
        smoother        DILU;
        tolerance       1e-5;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;

    residualControl
    {
        p_rgh           1e-2; // when you need dynamic pressure
        U               1e-4;
        T               1e-2;

        // possibly check turbulence fields
        "(k|epsilon|omega)" 1e-3;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
        "(k|epsilon|omega|R)" 0.7;
    }
}

// ************************************************************************* //
"""
    write_file("fvSolution", fv_solution_content)
    copy_file_to_container("fvSolution", os.path.join(case_dir, 'system/fvSolution'))
    os.remove("fvSolution")

    # Create system/blockMeshDict
    block_mesh_dict_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    (5 0 -2.5)           // 0
    (3.535 3.535 -2.5)   // 1
    (0 5 -2.5)           // 2
    (-3.535 3.535 -2.5)  // 3
    (-5 0 -2.5)          // 4
    (-3.535 -3.535 -2.5) // 5
    (0 -5 -2.5)          // 6
    (3.535 -3.535 -2.5)  // 7
    (5 0 2.5)            // 8
    (3.535 3.535 2.5)    // 9
    (0 5 2.5)            // 10
    (-3.535 3.535 2.5)   // 11
    (-5 0 2.5)           // 12
    (-3.535 -3.535 2.5)  // 13
    (0 -5 2.5)           // 14
    (3.535 -3.535 2.5)   // 15
    (0 0 -2.5)           // 16 center bottom
    (0 0 2.5)            // 17 center top
);

blocks
(
    hex (16 0 1 2 17 8 9 10) (100 100 1) simpleGrading (1 1 1)
    hex (16 2 3 4 17 10 11 12) (100 100 1) simpleGrading (1 1 1)
    hex (16 4 5 6 17 12 13 14) (100 100 1) simpleGrading (1 1 1)
    hex (16 6 7 0 17 14 15 8) (100 100 1) simpleGrading (1 1 1)
);

edges
(
    arc 0 1 (4.265 1.765 -2.5)
    arc 1 2 (1.765 4.265 -2.5)
    arc 2 3 (-1.765 4.265 -2.5)
    arc 3 4 (-4.265 1.765 -2.5)
    arc 4 5 (-4.265 -1.765 -2.5)
    arc 5 6 (-1.765 -4.265 -2.5)
    arc 6 7 (1.765 -4.265 -2.5)
    arc 7 0 (4.265 -1.765 -2.5)
    
    arc 8 9 (4.265 1.765 2.5)
    arc 9 10 (1.765 4.265 2.5)
    arc 10 11 (-1.765 4.265 2.5)
    arc 11 12 (-4.265 1.765 2.5)
    arc 12 13 (-4.265 -1.765 2.5)
    arc 13 14 (-1.765 -4.265 2.5)
    arc 14 15 (1.765 -4.265 2.5)
    arc 15 8 (4.265 -1.765 2.5)
);

boundary
(
    walls
    {
        type wall;
        faces
        (
            (0 1 9 8)
            (1 2 10 9)
            (2 3 11 10)
            (3 4 12 11)
            (4 5 13 12)
            (5 6 14 13)
            (6 7 15 14)
            (7 0 8 15)
        );
    }
    bottom
    {
        type wall;
        faces
        (
            (16 0 1 2)
            (16 2 3 4)
            (16 4 5 6)
            (16 6 7 0)
        );
    }
    top
    {
        type wall;
        faces
        (
            (17 8 9 10)
            (17 10 11 12)
            (17 12 13 14)
            (17 14 15 8)
        );
    }
);

mergePatchPairs
(
);

// ************************************************************************* //
"""
    write_file("blockMeshDict", block_mesh_dict_content)
    copy_file_to_container("blockMeshDict", os.path.join(case_dir, 'system/blockMeshDict'))
    os.remove("blockMeshDict")

    create_patch_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      createPatchDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

pointSync true;

patches
(
    {
        name inlet;
        patchInfo
        {
            type patch;
        }
        constructFrom patches;
        patches
        (
            bottom
        );
        faces
        (
            (16 0 8 17)
        );
    }
    {
        name outlet;
        patchInfo
        {
            type patch;
        }
        constructFrom patches;
        patches
        (
            top
        );
        faces
        (
            (16 6 14 17)
        );
    }
);

// ************************************************************************* //
"""
    # Write the createPatchDict content to a file
    write_file("createPatchDict", create_patch_content)
    copy_file_to_container("createPatchDict", os.path.join(case_dir, 'system/createPatchDict'))
    os.remove("createPatchDict")

    # Create system/surfaceFeaturesDict
    surface_features_dict_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      surfaceFeaturesDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

propeller
{
    surfaces ("propeller.stl");
    includedAngle 120;
    
}

// ************************************************************************* //
"""
    write_file("surfaceFeaturesDict", surface_features_dict_content)
    copy_file_to_container("surfaceFeaturesDict", os.path.join(case_dir, 'system/surfaceFeaturesDict'))
    os.remove("surfaceFeaturesDict")

    # Create system/snappyHexMeshDict
    snappy_hex_mesh_dict_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

castellatedMesh true;
snap            true;
addLayers       false;
geometry
{   
    propeller.stl
    {
        type            triSurfaceMesh;
        name            propeller;
    }
}

castellatedMeshControls
{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 10;
    nCellsBetweenLevels 3;

    features
    (
        {
            file "propeller.eMesh";
            level 1;
        }
    );

    refinementSurfaces
    {
        propeller
        {
            level (2 2);
            regions
            {
                propellerPatch
                {
                    name propeller;
                    type wall;
                }
            }
        }
    }

    resolveFeatureAngle 30;

    refinementRegions
    {
        propellerZone
        {
            mode inside;
            levels ((1e15 2));
        }
    }

    locationInMesh (0 0 0);  // Ensure this point is inside your mesh
    allowFreeStandingZoneFaces true;
}

snapControls
{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
}

addLayersControls
{
    relativeSizes true;
    layers { }

    expansionRatio 1.0;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 60;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedianAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}

meshQualityControls
{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minFlatness 0.5;
    minVol 1e-13;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.05;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
    minTetQuality 1e-15;
}

mergeTolerance 1E-6;

zones
{
    propellerZone
    {
        type cellZone;
        name propellerZone;
    }
}

// ************************************************************************* //
"""
    write_file("snappyHexMeshDict", snappy_hex_mesh_dict_content)
    copy_file_to_container("snappyHexMeshDict", os.path.join(case_dir, 'system/snappyHexMeshDict'))
    os.remove("snappyHexMeshDict")

    # Create constant/MRFProperties
    rotating_frame_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      MRFProperties;
    }

    MRFZones
    (
        propellerZone
        {
            cellZone    propellerZone; // Name of the cell zone from snappyHexMeshDict
            active      yes;
            nonRotatingPatches ();
            origin      (0 0 0); // Center of rotation, adjust as necessary
            axis        (0 0 1); // Axis of rotation
            omega       30; // Rotational speed in rad/s
        }
    );

    // ************************************************************************* //

"""
    write_file("MRFProperties", rotating_frame_content)
    copy_file_to_container("MRFProperties", os.path.join(case_dir, 'constant/MRFProperties'))
    os.remove("MRFProperties")

    # Create constant/transportProperties
    transport_properties_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      transportProperties;
    }

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    transportModel  Newtonian;

    nu              [0 2 -1 0 0 0 0] 1.5e-5;

    // ************************************************************************* //

"""
    write_file("transportProperties", transport_properties_content)
    copy_file_to_container("transportProperties", os.path.join(case_dir, 'constant/transportProperties'))
    os.remove("transportProperties")

    # Create constant/thermophysicalProperties
    thermophysical_properties_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        location    "constant";
        object      thermophysicalProperties;
    }

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    thermoType
    {
        type            hePsiThermo;
        mixture         pureMixture;
        transport       sutherland;
        thermo          hConst;
        equationOfState perfectGas;
        specie          specie;
        energy          sensibleInternalEnergy;
    }

    mixture
    {
        specie
        {
            nMoles          1;
            molWeight       28.97;
        }
        equationOfState
        {
            R               287.058;
        }
        thermodynamics
        {
            Cp              1005;
            Hf              0;
        }
        transport
        {
            mu              1.8e-05;
            Pr              0.7;
        }
    }

    // ************************************************************************* //

"""
    write_file("thermophysicalProperties", thermophysical_properties_content)
    copy_file_to_container("thermophysicalProperties", os.path.join(case_dir, 'constant/thermophysicalProperties'))
    os.remove("thermophysicalProperties")

    # Create constant/physicalProperties
    physical_properties_content = """
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        location    "system";
        object      snappyHexMeshDict;
    }
    castellatedMesh true;
    snap true;
    addLayers false;
    viscosityModel Newtonian;
    nu [0 2 -1 0 0 0 0] 1.5e-5;

    transport
    {
        nu [0 2 -1 0 0 0 0] 1.5e-5;
    }


    geometry
    {
        propeller.stl
        {
            type triSurfaceMesh;
            name propeller;
        }
    }

    castellatedMeshControls
    {
        maxLocalCells 1000000;
        maxGlobalCells 2000000;
        minRefinementCells 10;
        nCellsBetweenLevels 3;

        features
        (
            {
                file "propeller.eMesh";
                level 2;
            }
        );

        refinementSurfaces
        {
            propeller
            {
                level (4 4);
            }
        }

        resolveFeatureAngle 30;
    }

    snapControls
    {
        nSmoothPatch 3;
        tolerance 2.0;
        nSolveIter 30;
        nRelaxIter 5;
    }

    addLayersControls
    {
        relativeSizes true;
        layers
        {
            propeller
            {
                nSurfaceLayers 1;
            }
        }
        expansionRatio 1.0;
        finalLayerThickness 0.3;
        minThickness 0.25;
        nGrow 0;
        featureAngle 30;
        nRelaxIter 3;
        nSmoothSurfaceNormals 1;
        nSmoothNormals 3;
        nSmoothThickness 10;
        maxFaceThicknessRatio 0.5;
        maxThicknessToMedialRatio 0.3;
        minMedianAxisAngle 130;
        maxSkewness 4.0;
        maxBoundarySkewness 20;
        nBufferCellsNoExtrude 0;
        nLayerIter 50;
    }

    meshQualityControls
    {
        maxNonOrtho 65;
        maxBoundarySkewness 20;
        maxInternalSkewness 4;
        maxConcave 80;
        minFlatness 0.5;
        minVol 1e-13;
        minTetQuality 1e-9;
        minArea -1;
        minTwist 0.02;
        minDeterminant 0.001;
        minFaceWeight 0.02;
        minVolRatio 0.01;
        minTriangleTwist -1;
        nSmoothScale 4;
        errorReduction 0.75;
    }

    writeFlags (scalarLevels layerSets layerFields);

    mergeTolerance 1e-6;

"""
    write_file("physicalProperties", physical_properties_content)
    copy_file_to_container("physicalProperties", os.path.join(case_dir, 'constant/physicalProperties'))
    os.remove("physicalProperties")

    # Create constant/momentumTransport
    momentum_transport_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      momentumTransport;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel Newtonian;
nu              nu [ 0 2 -1 0 0 0 0 ] 1e-05;
simulationType RAS;

RAS
{
    model           kEpsilon;
    turbulence      on;
    printCoeffs     on;
}

// ************************************************************************* //
"""
    write_file("momentumTransport", momentum_transport_content)
    copy_file_to_container("momentumTransport", os.path.join(case_dir, 'constant/momentumTransport'))
    os.remove("momentumTransport")

    # Create 0/U
    u_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            noSlip;
    }
    bottom
    {
        type            noSlip;
    }
    top
    {
        type            slip;
    }
    propeller
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }
}

// ************************************************************************* //
"""
    write_file("U", u_content)
    copy_file_to_container("U", os.path.join(case_dir, '0/U'))
    os.remove("U")

    # Create 0/p
    p_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            zeroGradient;
    }
    bottom
    {
        type            zeroGradient;
    }
    top
    {
        type            zeroGradient;
    }
    propeller
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""
    write_file("p", p_content)
    copy_file_to_container("p", os.path.join(case_dir, '0/p'))
    os.remove("p")

    # Create 0/nut
    nut_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      nut;
}

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-5;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 1e-5;
    }
    outlet
    {
        type            calculated;
        value           uniform 1e-5;
    }
    walls
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }
    bottom
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }
    top
    {
        type            calculated;
        value           uniform 1e-5;
    }
    propeller
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }
}

// ************************************************************************* //
"""
    write_file("nut", nut_content)
    copy_file_to_container("nut", os.path.join(case_dir, '0/nut'))
    os.remove("nut")

    # Create 0/k
    k_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      k;
}

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.01;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.01;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }
    bottom
    {
        type            kqRWallFunction;
        value           uniform 0.01;
    }
    top
    {
        type            zeroGradient;
    }
    propeller
    {
        type            kqRWallFunction;
        value           uniform 0.005;
    }
}

// ************************************************************************* //
"""
    write_file("k", k_content)
    copy_file_to_container("k", os.path.join(case_dir, '0/k'))
    os.remove("k")

    # Create 0/epsilon
    epsilon_content = """
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      epsilon;
}

dimensions      [0 2 -3 0 0 0 0];

internalField   uniform 0.01;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.01;
    }
    outlet
    {
        type            zeroGradient;
    }
    walls
    {
        type            epsilonWallFunction;
        value           uniform 0.01;
    }
    bottom
    {
        type            epsilonWallFunction;
        value           uniform 0.01;
    }
    top
    {
        type            zeroGradient;
    }
    propeller
    {
        type            epsilonWallFunction;
        value           uniform 0.1;
    }
}

// ************************************************************************* //
"""
    write_file("epsilon", epsilon_content)
    copy_file_to_container("epsilon", os.path.join(case_dir, '0/epsilon'))
    os.remove("epsilon")

def extract_forces_data(case_dir):
    forces_file = os.path.join(case_dir, 'postProcessing/forces/0/forces.dat')
    
    if not os.path.exists(forces_file):
        print(f"Error: The file {forces_file} does not exist.")
        return None
    
    forces_data = pd.read_csv(forces_file, delim_whitespace=True, skiprows=4)
    return forces_data

def decompose_mesh():
    """Decompose the mesh for parallel processing."""
    return_code, stdout, stderr = run_command('decomposePar')
    if return_code != 0:
        print("Error during decomposePar")
        print(stderr.decode('utf-8'))
    else:
        print("decomposePar completed successfully")
        print(stdout.decode('utf-8'))

def run_parallel_simulation(num_processors):
    """Run the OpenFOAM simulation in parallel."""
    command = f'mpirun -np {num_processors} simpleFoam -parallel'
    return_code, stdout, stderr = run_command(command)
    if return_code != 0:
        print("Error during parallel simulation")
        print(stderr.decode('utf-8'))
    else:
        print("Parallel simulation completed successfully")
        print(stdout.decode('utf-8'))

def reconstruct_results():
    """Reconstruct the results from the parallel simulation."""
    return_code, stdout, stderr = run_command('reconstructPar')
    if return_code != 0:
        print("Error during reconstructPar")
        print(stderr.decode('utf-8'))
    else:
        print("reconstructPar completed successfully")
        print(stdout.decode('utf-8'))

def main():
    # Set the case directory inside Docker
    case_dir = "/home/openfoam/case"  # Directory inside Docker container
    run_command(f"cd {case_dir} && rm -rf ./*")
    stl_file = os.path.expanduser("./output/propeller.stl")  # STL file on the host
    stl_file_in_container = os.path.join(case_dir, "constant/triSurface/propeller.stl")

    # Check if STL file exists
    if not os.path.exists(stl_file):
        raise FileNotFoundError(f"STL file {stl_file} not found")

    # Setup the OpenFOAM case
    create_openfoam_case(case_dir, stl_file)

    # Run OpenFOAM commands inside Docker container
    run_command(f"cd {case_dir} && blockMesh")
    run_command(f"cd {case_dir} && createPatch -overwrite")
    run_command(f"cd {case_dir} && surfaceFeatures")
    

    # Check if .eMesh file was created
    run_command(f"ls {case_dir}/constant/triSurface")

    run_command(f"cd {case_dir} && snappyHexMesh -overwrite")
    
    # Run simpleFoam and capture log output
    # run_command(f"cd {case_dir} && simpleFoam &> log.simpleFoam", check_output=False)
    run_command(f"cd {case_dir} && simpleFoam &> log.simpleFoam", check_output=False)


    # Print log output
    # log_output = run_command(f"cd {case_dir} && tail -n 50 log.simpleFoam", check_output=False)
    # print(f"Log Output:\n{log_output.stdout}")
    # Decompose the mesh for parallel processing
    # run in parallel mode
    decompose_mesh()

    # Run the simulation in parallel
    num_processors = 2  # Adjust this based on your available hardware
    run_parallel_simulation(num_processors)

    # Reconstruct the results from the parallel simulation
    reconstruct_results()

    # # Extract forces data
    # forces_data = extract_forces_data(case_dir)
    
    # if forces_data is not None:
    #     print(forces_data.head())
        
    #     # Save forces data to CSV for further analysis
    #     forces_data.to_csv(os.path.join(case_dir, 'forces_data.csv'), index=False)
    # else:
    #     print("Failed to extract forces data.")

if __name__ == "__main__":
    main()
