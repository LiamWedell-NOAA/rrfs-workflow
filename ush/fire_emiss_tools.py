import os
import numpy as np
import xarray as xr
from datetime import datetime
from netCDF4 import Dataset
import interp_tools as i_tools

#Compute average FRP from raw RAVE for the previous 24 hours

#Compute average FRP from raw RAVE for the previous 24 hours
def FRP_ebb1(ebb_dcycle, fcst_dates, cols, rows, intp_dir, rave_to_intp, veg_map, tgt_area, beta, fg_to_ug, to_s):
    base_array = np.zeros((cols*rows))
    frp_daily = base_array
    ebb_smoke_total = []
    ebb_smoke_hr = []
    frp_avg_hr = []

    try:
        ef_map = xr.open_dataset(veg_map)
        emiss_factor = ef_map.emiss_factor.values
        target_area = tgt_area.values
    except (FileNotFoundError, IOError, OSError, RuntimeError, ValueError, TypeError, KeyError, IndexError, MemoryError) as e:
        print(f"Error loading vegetation map: {e}")
        return np.zeros((cols, rows)), np.zeros((cols, rows))

    num_files = 0
    for cycle in fcst_dates:
        try:
            file_path = os.path.join(intp_dir, f'{rave_to_intp}{cycle}00_{cycle}59.nc')
            if os.path.exists(file_path):
                try:
                    with xr.open_dataset(file_path) as nc:
                        open_fre = nc.FRE[0, :, :].values
                        open_frp = nc.frp_avg_hr[0, :, :].values
                        num_files += 1
                        if ebb_dcycle == 1:
                            print('Processing emissions for ebb_dcyc 1')
                            print(file_path)
                            frp_avg_hr.append(open_frp)
                            ebb_hourly = (open_fre * emiss_factor * beta * fg_to_ug) / (target_area * to_s)
                            ebb_smoke_total.append(np.where(open_frp > 0, ebb_hourly, 0))
                except (FileNotFoundError, IOError, OSError, RuntimeError, ValueError, TypeError, KeyError, IndexError, MemoryError) as e:
                    print(f"Error processing NetCDF file {file_path}: {e}")
                    frp_avg_hr.append(np.zeros((cols, rows)))
                    ebb_smoke_total.append(np.zeros((cols, rows)))
            else:
                frp_avg_hr.append(np.zeros((cols, rows)))
                ebb_smoke_total.append(np.zeros((cols, rows)))
        except Exception as e:
            print(f"Error processing cycle {cycle}: {e}")
            frp_avg_hr.append(np.zeros((cols, rows)))
            ebb_smoke_total.append(np.zeros((cols, rows)))

    if num_files > 0:
        frp_avg_reshaped = np.stack(frp_avg_hr, axis=0)
        ebb_total_reshaped = np.stack(ebb_smoke_total, axis=0)
    else:
        frp_avg_reshaped = np.zeros((24, cols, rows))
        ebb_total_reshaped = np.zeros((24, cols, rows))
    return(frp_avg_reshaped, ebb_total_reshaped)

#Compute average FRP from raw RAVE for the previous 24 hours 
def averaging_FRP_24(fcst_dates, cols, rows, intp_dir, rave_to_intp, veg_map, tgt_area, beta, fg_to_ug):
    # There are two situations here.
    #   1) there is only on fire detection whithin 24 hours so FRP is divided by 2 
    #   2) There are more than one fire detection so the average FRP is stimated
    # ebb_smoke is always divided by the number of times a fire is detected within 24 hours window
    base_array = np.zeros((cols*rows))
    frp_daily = base_array
    ebb_smoke_total = []
    cldfrac_daily = []

    try:
        ef_map = xr.open_dataset(veg_map)
        emiss_factor = ef_map.emiss_factor.values
        target_area = tgt_area.values
    except (FileNotFoundError, IOError,OSError,RuntimeError,ValueError, TypeError, KeyError, IndexError, MemoryError) as e:
        print(f"Error loading vegetation map: {e}")
        return np.zeros((cols, rows)), np.zeros((cols, rows))

    num_files = 0
    for cycle in fcst_dates:
        try:
            file_path = os.path.join(intp_dir, f'{rave_to_intp}{cycle}00_{cycle}59.nc')

            if os.path.exists(file_path):
                try:
                    with xr.open_dataset(file_path) as nc:
                        open_fre = nc.FRE[0, :, :].values
                        open_frp = nc.frp_avg_hr[0, :, :].values
                        open_cldfrac = nc.Cloud_Fraction[0, :, :].values

                        ebb_hourly = open_fre * emiss_factor * beta * fg_to_ug / target_area
                        ebb_smoke_total.append(np.where(open_frp > 0, ebb_hourly, 0).ravel())

                        frp_daily += np.where(open_frp > 0, open_frp, 0).ravel()
                        cldfrac_daily += np.where(open_frp > 0, open_cldfrac, 0).ravel()

                        num_files += 1
                except (FileNotFoundError, IOError,OSError,RuntimeError,ValueError, TypeError, KeyError, IndexError, MemoryError) as e:
                    print(f"Error processing NetCDF file {file_path}: {e}")
        except Exception as e:
            print(f"Error processing cycle {cycle}: {e}")

    if num_files > 0:
        summed_array = np.sum(np.array(ebb_smoke_total), axis=0)
        num_zeros = len(ebb_smoke_total) - np.sum([arr == 0 for arr in ebb_smoke_total], axis=0)
        safe_zero_count = np.where(num_zeros == 0, 1, num_zeros)

        result_array = [summed_array[i] / 2 if safe_zero_count[i] == 1 else summed_array[i] / safe_zero_count[i] for i in range(len(safe_zero_count))]
        result_array = np.array(result_array)
        result_array[num_zeros == 0] = summed_array[num_zeros == 0]
        ebb_total = result_array.reshape(cols, rows)
        ebb_total_reshaped = ebb_total / 3600

        temp_frp = [frp_daily[i] / 2 if safe_zero_count[i] == 1 else frp_daily[i] / safe_zero_count[i] for i in range(len(safe_zero_count))]
        temp_frp = np.array(temp_frp)
        temp_frp[num_zeros == 0] = frp_daily[num_zeros == 0]
        frp_avg_reshaped = temp_frp.reshape(cols, rows)
  
        #cldfrac_daily 
        tmp_cldfrac = [cldfrac_daily [i] / 2 if safe_zero_count[i] == 1 else cldfrac_daily[i] / safe_zero_count[i] for i in range(len(safe_zero_count))]
        tmp_cldfrac = np.array(tmp_cldfrac)
        tmp_cldfrac[num_zeros == 0] = cldfrac_daily[num_zeros == 0]
        cldfrac_avg_reshaped = tmp_cldfrac.reshape(cols, rows)
        
    else:
        frp_avg_reshaped = np.zeros((cols, rows))
        ebb_total_reshaped = np.zeros((cols, rows))
        cldfrac_avg_reshaped = np.zeros((cols, rows))

    return(frp_avg_reshaped, ebb_total_reshaped, cldfrac_avg_reshaped)

def averaging_FRP_dc4(fcst_dates, cols, rows, intp_dir, rave_to_intp, veg_map, tgt_area, beta, fg_to_ug):
    time_blocks = 4  # 6-hourly blocks
    # Initialize arrays for data and count of actual data points per block
    frp_blocks = [np.zeros((cols, rows)) for _ in range(time_blocks)]
    cldfrac_blocks = [np.zeros((cols, rows)) for _ in range(time_blocks)]
    ebb_smoke_blocks = [[] for _ in range(time_blocks)]
    data_count_blocks = [np.zeros((cols, rows)) for _ in range(time_blocks)]

    ef_map = xr.open_dataset(veg_map)
    emiss_factor = ef_map.emiss_factor.values.reshape(cols, rows)
    target_area = tgt_area.values.reshape(cols, rows)
    # Determine the start datetime for the forecast period
    forecast_start = datetime.strptime(fcst_dates[0], "%Y%m%d%H")
    
    for cycle in fcst_dates:
        # Parse hour from cycle
        try:
            hour = int(cycle[8:10])
            cycle_datetime = datetime.strptime(cycle, "%Y%m%d%H")
            print('PRINTING HOUR',hour)
        except ValueError:
            print(f"Invalid cycle format: {cycle}")
            continue
                # Calculate elapsed hours from forecast start
        elapsed_hours = int((cycle_datetime - forecast_start).total_seconds() / 3600)
        block_index = (elapsed_hours // 6) % time_blocks 

        file_path = os.path.join(intp_dir, f'{rave_to_intp}{cycle}00_{cycle}59.nc')

        if os.path.exists(file_path):
            with xr.open_dataset(file_path) as nc:
                open_fre = nc.FRE[0, :, :].values
                open_frp = nc.frp_avg_hr[0, :, :].values
                open_cldfrac = nc.Cloud_Fraction[0, :, :].values

                ebb_hourly = open_fre * emiss_factor * beta * fg_to_ug / target_area
                ebb_smoke_blocks[block_index].append(np.where(open_frp > 0, ebb_hourly, 0))
                frp_blocks[block_index] += np.where(open_frp > 0, open_frp, 0)
                cldfrac_blocks[block_index] += np.where(open_frp > 0, open_cldfrac, 0)
                data_count_blocks[block_index] += 1

    results = []
    for block in range(time_blocks):
        if np.any(data_count_blocks[block]):

            summed_array = np.sum(np.stack(ebb_smoke_blocks[block]), axis=0)
            # Count the total number of zeros

            non_zero_count = np.sum(np.stack(ebb_smoke_blocks[block]) != 0, axis=0)
            safe_zero_count = np.maximum(non_zero_count, 1)  # Avoid division by zero

            #Estimate ebb rate
            result_array = np.where(safe_zero_count == 1, summed_array / 2, summed_array / safe_zero_count).reshape(cols, rows)
            result_array = np.array(result_array)
            ebb_total =result_array.reshape(cols, rows)
            ebb_total_reshaped = ebb_total / 3600

            #Estimate frp avg  
            temp_frp=np.where(safe_zero_count == 1, frp_blocks[block]  / 2,  frp_blocks[block]  / safe_zero_count).reshape(cols, rows)
            temp_frp=np.array(temp_frp)

            # Cloud_Fraction
            temp_cldfrac =np.where(safe_zero_count == 1, cldfrac_blocks[block]  / 2, cldfrac_blocks[block]  / safe_zero_count).reshape(cols, rows)
            temp_cldfrac = np.array(temp_cldfrac)

            results.append((temp_frp,ebb_total_reshaped, temp_cldfrac))
        else:
            results.append((np.zeros((cols, rows)), np.zeros((cols, rows)), np.zeros((cols, rows))))

    time_blocks = 1  # Daily blocks
        # Stack the FRP and EBB results from all blocks along a new time dimension
    frp_avg_reshaped_dc4 = np.stack([res[0] for res in results], axis=0)
    ebb_tot_reshaped_dc4 = np.stack([res[1] for res in results], axis=0)
    cldfrac_avg_reshaped_dc4 = np.stack([res[2] for res in results], axis=0)

    print('Merged FRP shape:', frp_avg_reshaped_dc4.shape)
    print('Merged EBB shape:', ebb_tot_reshaped_dc4.shape)


    return(frp_avg_reshaped_dc4, ebb_tot_reshaped_dc4, cldfrac_avg_reshaped_dc4)

def estimate_fire_duration(intp_avail_hours, intp_dir, fcst_dates, current_day, cols, rows, rave_to_intp):
    # There are two steps here.
    #   1) First day simulation no RAVE from previous 24 hours available (fire age is set to zero)
    #   2) previus files are present (estimate fire age as the difference between the date of the current cycle and the date whe the fire was last observed whiting 24 hours)
    t_fire = np.zeros((cols, rows))

    for date_str in fcst_dates:
        try:
            date_file = int(date_str[:10])
            print('Date processing for fire duration', date_file)
            file_path = os.path.join(intp_dir, f'{rave_to_intp}{date_str}00_{date_str}59.nc')

            if os.path.exists(file_path):
                try:
                    with xr.open_dataset(file_path) as open_intp:
                        FRP = open_intp.frp_avg_hr[0, :, :].values
                        dates_filtered = np.where(FRP > 0, date_file, 0)
                        t_fire = np.maximum(t_fire, dates_filtered)
                except (FileNotFoundError, IOError, OSError,RuntimeError,ValueError, TypeError, KeyError, IndexError, MemoryError) as e:
                    print(f"Error processing NetCDF file {file_path}: {e}")
        except Exception as e:
            print(f"Error processing date {date_str}: {e}")

    t_fire_flattened = t_fire.flatten()
    t_fire_flattened = [int(i) if i != 0 else 0 for i in t_fire_flattened]

    try:
        fcst_t = datetime.strptime(current_day, '%Y%m%d%H')
        hr_ends = [datetime.strptime(str(hr), '%Y%m%d%H') if hr != 0 else 0 for hr in t_fire_flattened]
        te = [(fcst_t - i).total_seconds() / 3600 if i != 0 else 0 for i in hr_ends]
    except ValueError as e:
        print(f"Error processing forecast time {current_day}: {e}")
        te = np.zeros((rows, cols))

    return(te)


       # Repeat the same values across 4 time frames
       # fire_dur = np.repeat(te_array[np.newaxis, :, :], repeats=4, axis=0)
def save_fire_dur(cols, rows, te):
    fire_dur = np.array(te).reshape(cols, rows)
    return(fire_dur)

def produce_emiss_24hr_file(ebb_dcycle, frp_reshaped, intp_dir, current_day, tgt_latt, tgt_lont, ebb_smoke_reshaped, cols, rows):
    file_path = os.path.join(intp_dir, f'SMOKE_RRFS_data_{current_day}00.nc')
    with Dataset(file_path, 'w') as fout:
        i_tools.create_emiss_file(fout, cols, rows)
        i_tools.Store_latlon_by_Level(fout, 'geolat', tgt_latt, 'cell center latitude', 'degrees_north', '2D', '-9999.f', '1.f')
        i_tools.Store_latlon_by_Level(fout, 'geolon', tgt_lont, 'cell center longitude', 'degrees_east', '2D', '-9999.f', '1.f')

        i_tools.Store_by_Level(fout,'frp_avg_hr','mean Fire Radiative Power','MW','3D','0.f','1.f')
        fout.variables['frp_avg_hr'][:, :, :] = frp_reshaped
        i_tools.Store_by_Level(fout,'ebb_smoke_hr','EBB emissions','ug m-2 s-1','3D','0.f','1.f')
        fout.variables['ebb_smoke_hr'][:, :, :] = ebb_smoke_reshaped
'''
def prepare_arrays(frp_avg_reshaped, ebb_tot_reshaped, fire_dur,  xarr_hwp, xarr_totprcp, hwp_alpha, **kwargs):
    if hwp_alpha != 0:
        try:
            frp_avg_dc4 = kwargs['frp_avg_reshaped_dc4']
            ebb_tot_dc4 = kwargs['ebb_tot_reshaped_dc4']
            xarr_hwp_dc4 = kwargs['xarr_hwp_dc4']
        except KeyError as e:
            raise ValueError(f"Missing required argument for hwp_alpha != 0: {e}")
    totprcp_input   =  np.repeat(xarr_totprcp[np.newaxis, :, :], repeats=5, axis=0)
    fire_dur_input  =  np.repeat(fire_dur[np.newaxis, :, :], repeats=5, axis=0)

    if hwp_alpha == 0:
        frp_avg_input   =  np.repeat(frp_avg_reshaped[np.newaxis, :, :], repeats=5, axis=0)
        ebb_tot_input   =  np.repeat(ebb_tot_reshaped[np.newaxis, :, :], repeats=5, axis=0)
        hwp_input       =  np.repeat(xarr_hwp[np.newaxis, :, :], repeats=5, axis=0)
    else:
        frp_avg_input   =  np.concatenate([frp_avg_dc4, frp_avg_reshaped[np.newaxis, :, :]], axis=0)
        ebb_tot_input   =  np.concatenate([ebb_tot_dc4, ebb_tot_reshaped[np.newaxis, :, :]], axis=0) 
        hwp_input       =  np.concatenate([xarr_hwp_dc4, xarr_hwp[np.newaxis, :, :]], axis=0) 
 
    print("frpd:", frp_avg_input.shape)
    print("ebb:", ebb_tot_input.shape)
    print("totprcp:", totprcp_input.shape)
    print("hwp:", hwp_input.shape)
    print("fire_dur:", fire_dur_input.shape)
    return(frp_avg_input,ebb_tot_input,totprcp_input,hwp_input,fire_dur_input)
'''

def prepare_arrays(frp_avg_reshaped, ebb_tot_reshaped, fire_dur,  xarr_hwp, xarr_totprcp,frp_avg_reshaped_dc4, ebb_tot_reshaped_dc4,xarr_hwp_dc4,cldfrac_avg_reshaped_dc4,cldfrac_avg_reshaped):
    print(xarr_totprcp.shape, fire_dur.shape, frp_avg_reshaped_dc4.shape, frp_avg_reshaped.shape, ebb_tot_reshaped_dc4.shape, ebb_tot_reshaped.shape, xarr_hwp_dc4.shape, xarr_hwp.shape,cldfrac_avg_reshaped_dc4.shape,cldfrac_avg_reshaped.shape)
    totprcp_input   =  np.repeat(xarr_totprcp.values[np.newaxis, :, :], repeats=5, axis=0)
    fire_dur_input  =  np.repeat(fire_dur[np.newaxis, :, :], repeats=5, axis=0)
    frp_avg_input   =  np.concatenate([frp_avg_reshaped_dc4, frp_avg_reshaped[np.newaxis, :, :]], axis=0)
    ebb_tot_input   =  np.concatenate([ebb_tot_reshaped_dc4, ebb_tot_reshaped[np.newaxis, :, :]], axis=0)
    hwp_input       =  np.concatenate([xarr_hwp_dc4, xarr_hwp.values[np.newaxis, :, :]], axis=0)
    cldfrac_input   =  np.concatenate([cldfrac_avg_reshaped_dc4, cldfrac_avg_reshaped[np.newaxis, :, :]], axis=0)
    print("frpd:", frp_avg_input.shape, type(frp_avg_input))
    print("ebb:", ebb_tot_input.shape, type(ebb_tot_input))
    print("totprcp:", totprcp_input.shape, type(totprcp_input))
    print("hwp:", hwp_input.shape,type(hwp_input))
    print("fire_dur:", fire_dur_input.shape, type(fire_dur_input))
    print("cldfrac:", cldfrac_input.shape, type(cldfrac_input))

    #da = xr.DataArray(
    #totprcp_input,
    #dims=["time", "lat", "lon"],
    #coords={
    #    "time": np.arange(totprcp_input.shape[0]),
    #    "lat": np.arange(totprcp_input.shape[1]),
    #    "lon": np.arange(totprcp_input.shape[2])
    #},
    #name="totprcp"
    #)  

    # Save to NetCDF
    #da.to_netcdf("/scratch1/BMC/acomp/Johana/for_Ravan/test_HWP/test_2025042221/RRFS_NA_3km/totprcp_test.nc")
    return(frp_avg_input,ebb_tot_input,totprcp_input,hwp_input,fire_dur_input,cldfrac_input)


def produce_emiss_file(frp_avg_input,ebb_tot_input,totprcp_input,hwp_input,fire_dur_input, intp_dir, current_day, tgt_latt, tgt_lont, cols, rows, cldfrac_input):
    # Ensure arrays are not negative or NaN
    frp_avg_reshaped = np.clip(frp_avg_input, 0, None)
    frp_avg_reshaped = np.nan_to_num(frp_avg_input)

    ebb_tot_reshaped = np.clip(ebb_tot_input, 0, None)
    ebb_tot_reshaped = np.nan_to_num(ebb_tot_reshaped)

    fire_age = np.clip(fire_dur_input, 0, None)
    fire_age = np.nan_to_num(fire_age)

    cldfrac = np.clip(cldfrac_input, 0, None)
    cldfrac = np.nan_to_num(cldfrac) 

    # Filter HWP Prcp arrays to be non-negative and replace NaNs
    #filtered_hwp = hwp_input#.where(frp_avg_reshaped  > 0, 0).fillna(0)
    #filtered_prcp = totprcp_input#.where(frp_avg_reshaped > 0, 0).fillna(0)

    # Filter based on ebb_rate
    ebb_rate_threshold = 0  # Define an appropriate threshold if needed
    mask = (ebb_tot_reshaped > ebb_rate_threshold)
    mask_age = (fire_age  > 1)

    filtered_hwp = np.where(mask, hwp_input, 0)#filtered_hwp.where(mask, 0).fillna(0)
    filtered_prcp = np.where(mask_age, totprcp_input, 0) #filtered_prcp.where(mask, 0).fillna(0)
    frp_avg_reshaped = frp_avg_reshaped * mask
    filtered_clfrac = cldfrac * mask

    ebb_tot_reshaped = ebb_tot_reshaped * mask
    #fire_age = fire_age * mask

    print(frp_avg_reshaped.shape, ebb_tot_reshaped.shape, fire_age.shape, filtered_hwp.shape, filtered_prcp.shape)
    # Produce emiss file
    file_path = os.path.join(intp_dir, f'SMOKE_RRFS_data_{current_day}00.nc')
    
    try:
        with Dataset(file_path, 'w') as fout:
          i_tools.create_emiss_file(fout, cols, rows)
          i_tools.Store_latlon_by_Level(fout, 'geolat', tgt_latt, 'cell center latitude', 'degrees_north', '2D', '-9999.f', '1.f')
          i_tools.Store_latlon_by_Level(fout, 'geolon', tgt_lont, 'cell center longitude', 'degrees_east', '2D', '-9999.f', '1.f')

          print('Storing different variables')
          i_tools.Store_by_Level(fout,'frp_davg','Daily mean Fire Radiative Power','MW','3D','0.f','1.f')
          fout.variables['frp_davg'][:, :, :] = frp_avg_reshaped
          i_tools.Store_by_Level(fout,'ebb_rate','Total EBB emission','ug m-2 s-1','3D','0.f','1.f')
          fout.variables['ebb_rate'][:, :, :] = ebb_tot_reshaped
          i_tools.Store_by_Level(fout,'fire_end_hr','Hours since fire was last detected','hrs','3D','0.f','1.f')
          fout.variables['fire_end_hr'][:, :, :] = fire_age
          i_tools.Store_by_Level(fout,'hwp_davg','Daily mean Hourly Wildfire Potential', 'none','3D','0.f','1.f')
          fout.variables['hwp_davg'][:, :, :] = filtered_hwp
          i_tools.Store_by_Level(fout,'totprcp_24hrs','Sum of precipitation', 'm', '3D', '0.f','1.f')
          fout.variables['totprcp_24hrs'][:, :, :] = filtered_prcp
          i_tools.Store_by_Level(fout,'Cloud_Fraction','Cloud_Fraction', '%', '3D', '0.f','1.f')
          fout.variables['Cloud_Fraction'][:, :, :] = filtered_clfrac


        print("Emissions file created successfully")
        return "Emissions file created successfully"

    except (OSError, IOError) as e:
        print(f"Error creating or writing to NetCDF file {file_path}: {e}")
        return f"Error creating or writing to NetCDF file {file_path}: {e}"

    return "Emissions file created successfully"

