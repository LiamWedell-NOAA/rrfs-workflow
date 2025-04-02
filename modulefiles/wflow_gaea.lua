help([[
This module loads python environement for running the RRFS workflow on
the NOAA RDHPC machine Gaea
]])

whatis([===[Loads libraries needed for running the RRFS workflow on Gaea ]===])

prepend_path("MODULEPATH","/ncrc/proj/epic/rocoto/modulefiles")
load("rocoto")

prepend_path("MODULEPATH", "/ncrc/proj/epic/spack-stack/c6/spack-stack-1.5.1/envs/gsi-addon/install/modulefiles/Core")
load("stack-intel/2023.2.0")
load("stack-cray-mpich/8.1.29")
load("cmake/3.23.1")
load("crtm/2.4.0")

prepend_path("MODULEPATH","/ncrc/proj/epic/miniconda3/modulefiles")
load(pathJoin("miniconda3", os.getenv("miniconda3_ver") or "4.12.0"))

if mode() == "load" then
   LmodMsgRaw([===[Please do the following to activate conda:
       > conda activate workflow_tools
]===])
end
