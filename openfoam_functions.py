import subprocess
import os
import pandas as pd

def run_command(command, check_output=True):
    """Run a shell command and log its output."""
    source_openfoam = "source /opt/OpenFOAM/OpenFOAM-v2406/etc/bashrc"
    # source_openfoam = "source /opt/openfoam-dev/etc/bashrc"
    full_command = f"bash -c '{source_openfoam} && {command}'"
    print(f"Start command: {command}")
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    print(f"Finish command: {command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    if check_output:
        result.check_returncode()
    return result

def copy_file(local_path, container_path):
    """Copy a file."""
    copy_command = f"cp '{local_path}' '{container_path}'"
    result = subprocess.run(copy_command, shell=True, capture_output=True, text=True)
    print(f"Copy Command: {copy_command}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    result.check_returncode()

def create_directory_structure_in_container(case_dir):
    dirs = [
        case_dir,
        os.path.join(case_dir, 'constant'),
        os.path.join(case_dir, 'constant/triSurface'),
        os.path.join(case_dir, 'system'),
        os.path.join(case_dir, '0')
    ]
    for d in dirs:
        run_command(f"mkdir -p {d}")

def write_file(filepath, content):
    with open(filepath, 'w') as f:
        f.write(content)

def create_openfoam_control(case_dir, sim_end_time, time_step, write_interval, center_of_rotation):
    control_dict_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     pimpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         """ + str(sim_end_time) + """;

deltaT          """ + str(time_step) + """;

writeControl    adjustableRunTime;

writeInterval   """ + str(write_interval) + """;

purgeWrite      0;

writeFormat     ascii;

writePrecision  7;

writeCompression no;

timeFormat      general;

timePrecision   6;

runTimeModifiable yes;

adjustTimeStep  yes;

maxCo           1;

maxDeltaT       1;

functions
{
    forces
    {
        type forces;                   // Specifies the type of function
        libs (forces);      // Explicitly load the forces library
        writeControl writeTime;          // Controls when the forces are written
        patches ( fan );              // Specify the patches to apply the forces on
        // Field names
        p               p;
        U               U;
        rho             rhoInf;
        rhoInf  1.25;                 // Name of the density field (optional for compressible flows)
        log true;                       // Log the results
        CofR """ + center_of_rotation + """;                   // Center of rotation for moment calculations
    }

    forceCoeffs
    {
        type            forceCoeffs;           // Specifies the type of function
        libs            (forces);      // Explicitly load the forces library
        writeControl    writeTime;              // Controls when the coefficients are written
        patches         (fan);               // Specify the patches to apply the force coefficients on
        // Field names
        p               p;
        U               U;
        rho             rhoInf;

        rhoInf          1.25;                // Name of the density field (used for compressible flows)
        log             true;                  // Log the results
        liftDir         (0 0 -1);               // Direction for lift coefficient calculation
        dragDir         (0 1 0);               // Direction for drag coefficient calculation
        pitchAxis       (0 0 1);               // Axis about which the moment is calculated
        magUInf         1;                     // Freestream velocity magnitude
        lRef            1;                     // Reference length (used for calculating moment coefficient)
        Aref            1;                     // Reference area (used for calculating lift and drag coefficients)
        CofR """ + center_of_rotation + """;                   // Center of rotation for moment calculations
    }
    
}


// ************************************************************************* //
"""

    write_file("controlDict", control_dict_content)
    copy_file("controlDict", os.path.join(case_dir, 'system/controlDict'))
    os.remove("controlDict")

def create_openfoam_blockmesh(case_dir):
    block_mesh_dict_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   1;

vertices
(
    ( -6.0 -0.5 -0.1)
    (  0.5 -0.5 -0.1)
    (  0.5  5.0 -0.1)
    ( -6.0  5.0 -0.1)
    ( -6.0 -0.5 2.9)
    (  0.5 -0.5 2.9)
    (  0.5  5.0 2.9)
    ( -6.0  5.0 2.9)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (65 55 30) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    allBoundary
    {
        type patch;
        faces
        (
            (3 7 6 2)
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);


// ************************************************************************* //

"""

    write_file("blockMeshDict", block_mesh_dict_content)
    copy_file("blockMeshDict", os.path.join(case_dir, 'system/blockMeshDict'))
    os.remove("blockMeshDict")

def create_openfoam_createpatch(case_dir):
    create_patch_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      createPatchDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

pointSync false;

patches
(
    {
        //- Master side patch
        name            AMI1;
        patchInfo
        {
            type            cyclicAMI;
            matchTolerance  0.0001;
            neighbourPatch  AMI2;
            transform       noOrdering;
        }
        constructFrom patches;
        patches (AMI);
    }

    {
        //- Slave side patch
        name            AMI2;
        patchInfo
        {
            type            cyclicAMI;
            matchTolerance  0.0001;
            neighbourPatch  AMI1;
            transform       noOrdering;
        }
        constructFrom patches;
        patches (AMI_slave);
    }
);


// ************************************************************************* //
"""
    # Write the createPatchDict content to a file
    write_file("createPatchDict", create_patch_content)
    copy_file("createPatchDict", os.path.join(case_dir, 'system/createPatchDict'))
    os.remove("createPatchDict")

def create_openfoam_decomposepar(case_dir, number_of_subdomains):
    decompose_par_dict_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains """ + str(number_of_subdomains) + """;

method          hierarchical;


hierarchicalCoeffs
{
    n           (2 2 1); // The number of subdomains in the x, y, and z directions
    delta       0.001;
    order       xyz;
}

// ************************************************************************* //

"""
    write_file("decomposeParDict", decompose_par_dict_content)
    copy_file("decomposeParDict", os.path.join(case_dir, 'system/decomposeParDict'))
    os.remove("decomposeParDict")

def create_openfoam_fvschemes(case_dir):
    fv_schemes_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
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
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;

    div(phi,U)      Gauss linearUpwind grad(U);
    div(U)          Gauss linear;

    div(phi,k)      Gauss linearUpwind grad(U);
    div(phi,omega)  Gauss linearUpwind grad(U);

    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}


// ************************************************************************* //
"""
    write_file("fvSchemes", fv_schemes_content)
    copy_file("fvSchemes", os.path.join(case_dir, 'system/fvSchemes'))
    os.remove("fvSchemes")

def create_openfoam_fvsolution(case_dir):
    fv_solution_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
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
    "(p|pcorr)"
    {
        solver          GAMG;
        smoother        DICGaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }

    "(p|pcorr)Final"
    {
        $p;
        tolerance       1e-06;
        relTol          0;
    }

    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-06;
        relTol          0.1;
    }

    "(U|k|omega)Final"
    {
        $U;
        tolerance       1e-06;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor   yes;
    nOuterCorrectors    3;
    nCorrectors     1;
    nNonOrthogonalCorrectors 0;
}


// ************************************************************************* //
"""
    write_file("fvSolution", fv_solution_content)
    copy_file("fvSolution", os.path.join(case_dir, 'system/fvSolution'))
    os.remove("fvSolution")

def create_openfoam_relvelocity(case_dir):
    rel_velocity_content = """
// --------------------------------*- C++ -*-------------------------------- //
//
// File
//     OpenFOAM coded function object
//
// Description
//     Write relative rotational speed
//
// ------------------------------------------------------------------------- //

relVelocity
{
    type coded;
    name relVelocity;
    libs ( utilityFunctionObjects );

    writeControl writeTime;

    coeffs
    {
        // User input (duplicate of constant/dynamicMeshDict)
        // origin  (-3 2 2.6);
        // axis    (0 0 1);
        // omega   10;
        // zones   ( rotatingZone );

        #sinclude "../constant/dynamicMeshDict"
    }

    // Additional context for code execute/write
    codeContext
    {
        verbose true;
    }

    codeData
    #{
        vector origin;
        vector omega;
        wordRes zoneNames;
    #};

    codeRead
    #{
        const dictionary& coeffs = dict.optionalSubDict("coeffs");
        const dictionary& context = this->codeContext();

        origin = coeffs.get<vector>("origin");

        omega =
        (
            // speed
            (
                coeffs.found("rpm")
              ? degToRad(coeffs.get<scalar>("rpm") / 60.0)
              : coeffs.get<scalar>("omega")
            )
            // axis
          * normalised(coeffs.getOrDefault<vector>("axis", vector(0,0,1)))
        );

        if (!coeffs.readIfPresent("zones", zoneNames))
        {
            if (coeffs.found("cellZone"))
            {
                zoneNames.resize(1);
                coeffs.readEntry("cellZone", zoneNames[0]);
            }
        }

        if (context.getOrDefault<bool>("verbose", false))
        {
            Log<< "Relative velocity at origin " << origin << " ";
        }
    #};

    codeWrite
    #{
        const dictionary& context = this->codeContext();

        if (context.getOrDefault<bool>("verbose", false))
        {
            Log<< "Calculate relative velocity ";
        }

        const auto& cc = mesh().C();
        const auto& U = mesh().lookupObject<volVectorField>("U");

        auto trelVel = volVectorField::New
        (
            "relVelocity",
            mesh(),
            dimensionedVector(dimVelocity, Zero),
            fvPatchVectorField::zeroGradientType()
        );
        auto& relVel = trelVel.ref();
        auto& relVelField = relVel.primitiveFieldRef();

        if (zoneNames.empty())
        {
            for (label celli = 0; celli < mesh().nCells(); ++celli)
            {
                relVelField[celli] = U[celli] - (omega ^ (cc[celli] - origin));
            }
        }
        else
        {
            for (const label celli : mesh().cellZones().selection(zoneNames))
            {
                relVelField[celli] = U[celli] - (omega ^ (cc[celli] - origin));
            }
        }

        relVel.correctBoundaryConditions();
        relVel.write();
    #};
}


// ************************************************************************* //
"""
    write_file("relVelocity", rel_velocity_content)
    copy_file("relVelocity", os.path.join(case_dir, 'system/relVelocity'))
    os.remove("relVelocity") 

def create_openfoam_snappyhexmesh(case_dir, fine_mesh_level, course_mesh_level):
    snappy_hex_mesh_dict_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
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
{   AMI
    {
        file "AMI.stl";
        type triSurfaceMesh; 
        name AMI;
    }
    
    door
    {
        file "door.stl";
        type triSurfaceMesh; 
        name door;
    }
    fan
    {
        file "fan.stl";
        type triSurfaceMesh;
        name fan;
    }
    outlet
    {
        file "outlet.stl";
        type triSurfaceMesh; 
        name outlet;
    }
    room
    {
        file "room.stl";
        type triSurfaceMesh; 
        name room;
    }
    desk
    {
        file "desk.stl";
        type triSurfaceMesh;
        name desk;
    }
}

castellatedMeshControls
{
    maxLocalCells 100000;
    maxGlobalCells 8000000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 2;

    features
    (
        { file "AMI.eMesh"; level """ + str(fine_mesh_level) + """;} // Note: better: level 3
        { file "fan.eMesh"; level """ + str(fine_mesh_level) + """;} // Note: better: level 3
        { file "door.eMesh"; level """ + str(fine_mesh_level) + """;}
        { file "outlet.eMesh"; level """ + str(course_mesh_level) + """;}
        { file "room.eMesh"; level """ + str(course_mesh_level) + """;}
        { file "desk.eMesh"; level """ + str(course_mesh_level + 1) + """;}
    );

    refinementSurfaces
    {
        AMI
        {
            level (""" + str(fine_mesh_level) + " " + str(fine_mesh_level) + """); // Note: better: levels 3 3
            faceType boundary;
            cellZone rotatingZone;
            faceZone rotatingZone;
            cellZoneInside inside;
        }
        fan{ level (""" + str(fine_mesh_level) + " " + str(fine_mesh_level) + """);} // Note: better: levels 3 3
        door{ level (""" + str(course_mesh_level) + " " + str(course_mesh_level) + """);}
        outlet{ level (""" + str(course_mesh_level) + " " + str(course_mesh_level) + """);}
        room{ level (""" + str(course_mesh_level) + " " + str(course_mesh_level) + """);}
        desk{ level (""" + str(course_mesh_level + 1) + " " + str(course_mesh_level + 1) + """);}
    }

    resolveFeatureAngle 30;

    refinementRegions
    {
        // Note: for better mesh quality utilize this refinement region
        // AMI{ mode inside; levels ((1E15 3));}
    }

    locationInMesh (0.1001 0.001 0.0101);
    allowFreeStandingZoneFaces false;
}

snapControls
{
    nSmoothPatch 10;
    tolerance 2.0;
    nSolveIter 500;
    nRelaxIter 10;
    nFeatureSnapIter 10;
    implicitFeatureSnap true;
    explicitFeatureSnap true;
    multiRegionFeatureSnap true;
}

addLayersControls
{
    relativeSizes true;

    layers
    {
    }

    expansionRatio 1.0;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}

meshQualityControls
{
    maxNonOrtho 65;
    maxBoundarySkewness 4;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality -1;
    minArea -1;
    minTwist 0.01;
    minDeterminant 0.001;
    minFaceWeight 0.05;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 5;
    errorReduction 0.75;
    relaxed
    {
        maxNonOrtho 80;
    }
}

mergeTolerance 1e-6;


// ************************************************************************* //
"""
    write_file("snappyHexMeshDict", snappy_hex_mesh_dict_content)
    copy_file("snappyHexMeshDict", os.path.join(case_dir, 'system/snappyHexMeshDict'))
    os.remove("snappyHexMeshDict")

def create_openfoam_surfacefeatures(case_dir):
    surface_features_dict_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      surfaceFeatureExtractDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

AMI.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}

door.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}

fan.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}

outlet.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}

room.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}

desk.stl
{
    extractionMethod    extractFromSurface;
    includedAngle       150;
}


// ************************************************************************* //
"""
    write_file("surfaceFeatureExtractDict", surface_features_dict_content)
    copy_file("surfaceFeatureExtractDict", os.path.join(case_dir, 'system/surfaceFeatureExtractDict'))
    os.remove("surfaceFeatureExtractDict")

def create_openfoam_transportproperties(case_dir):
    transport_properties_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

nu              1e-05;


// ************************************************************************* //

"""
    write_file("transportProperties", transport_properties_content)
    copy_file("transportProperties", os.path.join(case_dir, 'constant/transportProperties'))
    os.remove("transportProperties")

def create_openfoam_dynamicmesh(case_dir, rotation_speed, center_of_rotation):
    dynamic_mesh_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dynamicFvMesh   dynamicMotionSolverFvMesh;

motionSolverLibs (fvMotionSolvers);

motionSolver    solidBody;

cellZone        rotatingZone;

solidBodyMotionFunction  rotatingMotion;

origin      """ + center_of_rotation + """;
axis        (0 0 1);
omega       """ + str(rotation_speed) + """;


// ************************************************************************* //
"""
    write_file("dynamicMeshDict", dynamic_mesh_content)
    copy_file("dynamicMeshDict", os.path.join(case_dir, 'constant/dynamicMeshDict'))
    os.remove("dynamicMeshDict") 

def create_openfoam_g(case_dir):
    g_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    object      g;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -2 0 0 0 0];
value           (0 0 -9.81);


// ************************************************************************* //
"""
    write_file("g", g_content)
    copy_file("g", os.path.join(case_dir, 'constant/g'))
    os.remove("g") 

def create_openfoam_turbulenceproperties(case_dir):
    turbulence_properties_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType      RAS;

RAS
{
    RASModel        kOmegaSST;

    turbulence      on;

    printCoeffs     on;
}


// ************************************************************************* //

"""
    write_file("turbulenceProperties", turbulence_properties_content)
    copy_file("turbulenceProperties", os.path.join(case_dir, 'constant/turbulenceProperties'))
    os.remove("turbulenceProperties")

def create_openfoam_initial_condition_u(case_dir):
    u_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    AMI1
    {
        type            cyclicAMI;
        value           uniform (0 0 0);
    }

    AMI2
    {
        type            cyclicAMI;
        value           uniform (0 0 0);
    }

    fan
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }

    door
    {
        type            fixedValue;
        value           uniform (-0.1 0 0);
    }

    outlet
    {
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
    }

    room
    {
        type            noSlip;
    }

    desk
    {
        type            noSlip;
    }
}


// ************************************************************************* //
"""
    write_file("U", u_content)
    copy_file("U", os.path.join(case_dir, '0/U'))
    os.remove("U")

def create_openfoam_initial_condition_p(case_dir):
    p_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    AMI1
    {
        type            cyclicAMI;
        value           uniform 0;
    }

    AMI2
    {
        type            cyclicAMI;
        value           uniform 0;
    }

    fan
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }

    door
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }

    room
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }

    desk
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
}


// ************************************************************************* //
"""
    write_file("p", p_content)
    copy_file("p", os.path.join(case_dir, '0/p'))
    os.remove("p")

def create_openfoam_initial_condition_nut(case_dir):
    nut_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 1e-5;

boundaryField
{
    AMI1
    {
        type            cyclicAMI;
        value           uniform 1e-5;
    }

    AMI2
    {
        type            cyclicAMI;
        value           uniform 1e-5;
    }

    fan
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }

    door
    {
        type            zeroGradient;
    }

    outlet
    {
        type            zeroGradient;
    }

    room
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }

    desk
    {
        type            nutkWallFunction;
        value           uniform 1e-5;
    }
}


// ************************************************************************* //
"""
    write_file("nut", nut_content)
    copy_file("nut", os.path.join(case_dir, '0/nut'))
    os.remove("nut")

def create_openfoam_initial_condition_k(case_dir):
    k_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0.00341;

boundaryField
{
    AMI1
    {
        type            cyclicAMI;
        value           uniform 0.00341;
    }

    AMI2
    {
        type            cyclicAMI;
        value           uniform 0.00341;
    }

    fan
    {
        type            kqRWallFunction;
        value           uniform 0.00341;
    }

    door
    {
        type            turbulentIntensityKineticEnergyInlet;
        intensity       0.05;
        value           uniform 0.00341;
    }

    outlet
    {
        type            zeroGradient;
    }

    room
    {
        type            kqRWallFunction;
        value           uniform 0.00341;
    }

    desk
    {
        type            kqRWallFunction;
        value           uniform 0.00341;
    }
}


// ************************************************************************* //
"""
    write_file("k", k_content)
    copy_file("k", os.path.join(case_dir, '0/k'))
    os.remove("k")

def create_openfoam_initial_condition_omega(case_dir):
    omega_content = """
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2406                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      omega;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 -1 0 0 0 0];

internalField   uniform 0.1;

boundaryField
{
    AMI1
    {
        type            cyclicAMI;
        value           uniform 0.1;
    }

    AMI2
    {
        type            cyclicAMI;
        value           uniform 0.1;
    }

    fan
    {
        type            omegaWallFunction;
        value           uniform 0.1;
    }

    door
    {
        type            turbulentMixingLengthFrequencyInlet;
        mixingLength    1.2;
        value           uniform 0.1;
    }

    outlet
    {
        type            zeroGradient;
    }

    room
    {
        type            omegaWallFunction;
        value           uniform 0.1;
    }

    desk
    {
        type            omegaWallFunction;
        value           uniform 0.1;
    }
}


// ************************************************************************* //
"""
    write_file("omega", omega_content)
    copy_file("omega", os.path.join(case_dir, '0/omega'))
    os.remove("omega")

def create_openfoam_case(case_dir, number_of_subdomains, sim_end_time, fine_mesh_level, course_mesh_level, rotation_speed, time_step, write_interval, center_of_rotation):

    create_openfoam_control(case_dir, sim_end_time, time_step, write_interval, center_of_rotation)
    create_openfoam_blockmesh(case_dir)
    create_openfoam_createpatch(case_dir)
    create_openfoam_decomposepar(case_dir, number_of_subdomains)
    create_openfoam_fvschemes(case_dir)
    create_openfoam_fvsolution(case_dir)
    create_openfoam_relvelocity(case_dir)
    create_openfoam_snappyhexmesh(case_dir, fine_mesh_level, course_mesh_level)
    create_openfoam_surfacefeatures(case_dir)
    create_openfoam_transportproperties(case_dir)
    create_openfoam_dynamicmesh(case_dir, rotation_speed, center_of_rotation)
    create_openfoam_g(case_dir)
    create_openfoam_turbulenceproperties(case_dir)
    

def create_openfoam_initial_conditions(case_dir):
    run_command(f"cd {case_dir} && mkdir 0")
    create_openfoam_initial_condition_u(case_dir)
    create_openfoam_initial_condition_p(case_dir)
    create_openfoam_initial_condition_nut(case_dir)
    create_openfoam_initial_condition_k(case_dir)
    create_openfoam_initial_condition_omega(case_dir)

# post processing on forces
def extract_forces_data(forces_file):
    forces_df = pd.read_csv(forces_file, sep='\s+', comment='#', header=None)

    # Inspect the first few rows to understand the structure
    print(forces_df.head())

    # Update the column names based on the structure of your forces.dat file
    forces_df.columns = ['Time', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz', 'Vx', 'Vy', 'Vz']

    # Extract thrust (assuming it's the force in the x-direction)
    thrust = forces_df['Fx']

    # Define propeller angular velocity (rad/s)
    angular_velocity = 100.0  # Adjust according to your simulation setup

    # Convert the torque column to numeric, forcing errors to NaN
    torque = pd.to_numeric(forces_df['Mx'], errors='coerce')

    # Replace NaN values with 0 (or handle them as needed)
    torque.fillna(0, inplace=True)

    # Calculate power (Power = Torque * Angular Velocity)
    power = torque * angular_velocity

    # Save results to a CSV file
    results_df = pd.DataFrame({'Time': forces_df['Time'], 'Thrust': thrust, 'Power': power})
    results_df.to_csv('thrust_power.csv', index=False)

    print("Thrust and power data saved to thrust_power.csv")
    return results_df