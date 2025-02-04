DG GSL_workflow_RRFS-SD GSL workflow for retrospective simulations based on EMC's workflow for RRFSv1 updated on July 2 2024 Build


rrfs-workflow/parm/FV3LAM_wflow.xml (dependencies for the process smoke task)
rrfs-workflow/scripts/exrrfs_run_fcst.sh (create dummy files for both ebb_dc options and used when RAVE is not available)
rrfs-workflow/scripts/exrrfs_run_prepstart.sh (smoke and dust cycling)
rrfs-workflow/scripts/exrrfs_process_smoke.sh (splitting of RAVE files, version < 2, replace interpolated files if older than 5 days, always replace the Smoke file)
rrfs-workflow/ush/generate_fire_emissions.py (handles two fire emission scenarios)
rrfs-workflow/ush/HWP_tools.py (handles restart files for different cycling configurations)
rrfs-workflow/ush/fire_emiss_tools.py (handles two fire emission scenarios)
rrfs-workflow/ush/interp_tools.py (handles two fire emission scenarios)


-## Disclaimer
-
-```
-The United States Department of Commerce (DOC) GitHub project code is
-provided on an "as is" basis and the user assumes responsibility for
-its use. DOC has relinquished control of the information and no longer
-has responsibility to protect the integrity, confidentiality, or
-availability of the information. Any claims against the Department of
-Commerce stemming from the use of its GitHub project will be governed
-by all applicable Federal law. Any reference to specific commercial
-products, processes, or services by service mark, trademark,
-manufacturer, or otherwise, does not constitute or imply their
-endorsement, recommendation or favoring by the Department of
-Commerce. The Department of Commerce seal and logo, or the seal and
-logo of a DOC bureau, shall not be used in any manner to imply
-endorsement of any commercial product or activity by DOC or the United
-States Government.
