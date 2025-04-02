#!/bin/sh
#
# FIX_RRFS locaitons at different HPC platforms
#
if [[ -d /lfs/h2 ]] ; then
    PLATFORM=wcoss2
    FIX_RRFS_LOCATION="/lfs/h2/emc/lam/noscrub/emc.lam/FIX_RRFS"
elif [[ -d /scratch1 ]] ; then
    PLATFORM=hera
    FIX_RRFS_LOCATION="/scratch1/BMC/acomp/rrfs-sd_tools/fix"
elif [[ -d /jetmon ]] ; then
    PLATFORM=jet
    FIX_RRFS_LOCATION="/lfs4/BMC/nrtrr/FIX_RRFS"
elif [[ -d /work ]]; then
    FIX_RRFS_LOCATION="/work/noaa/rtrr/FIX_RRFS"
    hoststr=$(hostname)
    if [[ "$hoststr" == "hercules"* ]]; then                                                                                                                           
      PLATFORM=hercules
    else
      PLATFORM=orion
    fi
elif [[ -d /gpfs ]]; then
    PLATFORM=gaea
    FIX_RRFS_LOCATION="/gpfs/f6/drsa-fire3/proj-shared/Liam/fix/rrfs-sd"
else
    PLATFORM=unknown
    FIX_RRFS_LOCATION="/this/is/an/unknown/platform"
fi
