unload("python")
prepend_path("MODULEPATH","/ncrc/proj/epic/miniconda3/modulefiles/")
load("miniconda3")

unsetenv("PYTHONPATH")
setenv("SRW_ENV", "/gpfs/f6/drsa-fire3/proj-shared/Liam/envs/interpol_esmpy")
load("gaea_common")
