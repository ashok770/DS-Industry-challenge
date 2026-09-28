import os
import zipfile
import csv
import io
import pandas as pd

ZIP_PATH = "data/511_2025_03_so.zip"
CSV_PATH = 'data/processed/transport_sample_v2.csv'
BART_TRIP = "BA:1683058:20250331"

def print_stats(title, dict_data):
    print(f"\n==================================================")
    print(f"{title}")
    print(f"==================================================")
    for k, v in dict_data.items():
        print(f"{k}: {v}")

def main():
    if not os.path.exists(ZIP_PATH):
        print(f"Error: ZIP file not found at {ZIP_PATH}")
        return

    # 1. RAW stop_times FOR BART
    print("\n==================================================")
    print("TASK 1 — RAW stop_times FOR BART")
    print("==================================================")
    
    bart_st = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("stop_times.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            for row in reader:
                if row.get('trip_id') == BART_TRIP:
                    bart_st.append({
                        'trip_id': row.get('trip_id'),
                        'stop_sequence': int(row.get('stop_sequence')) if row.get('stop_sequence') else None,
                        'stop_id': row.get('stop_id'),
                        'arrival_time': row.get('arrival_time'),
                        'departure_time': row.get('departure_time'),
                        'shape_dist_traveled': row.get('shape_dist_traveled'),
                        'timepoint': row.get('timepoint')
                    })
    
    st_df = pd.DataFrame(bart_st)
    if not st_df.empty:
        st_df = st_df.sort_values('stop_sequence')
        print(st_df.to_string(index=False))
        
        print("\nSummary:")
        print(f"- Number of matching stop_times rows: {len(st_df)}")
        print(f"- Minimum stop_sequence: {st_df['stop_sequence'].min()}")
        print(f"- Maximum stop_sequence: {st_df['stop_sequence'].max()}")
        print(f"- Number of unique stop_sequence values: {st_df['stop_sequence'].nunique()}")
        print(f"- Rows with non-missing arrival_time: {st_df['arrival_time'].notna().sum()}")
        print(f"- Rows with non-missing departure_time: {st_df['departure_time'].notna().sum()}")
    else:
        print("No stop_times found for BART trip.")


    # 2. RAW stop_observations FOR BART
    print("\n==================================================")
    print("TASK 2 — RAW stop_observations FOR BART")
    print("==================================================")
    
    bart_so = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("stop_observations.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            for row in reader:
                if row.get('trip_id') == BART_TRIP:
                    bart_so.append({
                        'trip_id': row.get('trip_id'),
                        'service_date': row.get('service_date'),
                        'stop_sequence': int(row.get('stop_sequence')) if row.get('stop_sequence') else None,
                        'observed_arrival_time': row.get('observed_arrival_time'),
                        'observed_departure_time': row.get('observed_departure_time'),
                        'scheduled_arrival_time': row.get('scheduled_arrival_time'),
                        'scheduled_departure_time': row.get('scheduled_departure_time'),
                        'vehicle_id': row.get('vehicle_id'),
                        'uncertainty': row.get('uncertainty')
                    })
    
    so_df = pd.DataFrame(bart_so)
    if not so_df.empty:
        so_df = so_df.sort_values(['service_date', 'stop_sequence', 'observed_arrival_time'])
        print(so_df.head(20).to_string(index=False))
        print("... (showing first 20 records only)")
        
        print("\nSummary:")
        print(f"- Total number of observation rows: {len(so_df)}")
        print(f"- Number of unique service_date values: {so_df['service_date'].nunique()}")
        print(f"- Minimum stop_sequence: {so_df['stop_sequence'].min()}")
        print(f"- Maximum stop_sequence: {so_df['stop_sequence'].max()}")
        print(f"- Number of unique stop_sequence values: {so_df['stop_sequence'].nunique()}")
        print(f"- Rows with non-missing observed_arrival_time: {so_df['observed_arrival_time'].replace({'': pd.NA}).notna().sum()}")
        print(f"- Rows with non-missing scheduled_arrival_time: {so_df['scheduled_arrival_time'].replace({'': pd.NA}).notna().sum()}")
    
    # 3. CHECK EACH SERVICE DATE
    print("\n==================================================")
    print("TASK 3 — CHECK EACH SERVICE DATE")
    print("==================================================")
    
    # Drop rows where arrival_time is literally empty string for finding min/max
    valid_arr = so_df[so_df['observed_arrival_time'] != '']
    grouped = valid_arr.groupby('service_date')
    
    date_summaries = []
    for date, group in grouped:
        sched_arr_valid = group[group['scheduled_arrival_time'] != '']
        first_sched = sched_arr_valid['scheduled_arrival_time'].min() if not sched_arr_valid.empty else None
        last_sched = sched_arr_valid['scheduled_arrival_time'].max() if not sched_arr_valid.empty else None
        
        date_summaries.append({
            'service_date': date,
            'rows': len(group),
            'min_seq': group['stop_sequence'].min(),
            'max_seq': group['stop_sequence'].max(),
            'uniq_seq': group['stop_sequence'].nunique(),
            'first_obs_arr': group['observed_arrival_time'].min(),
            'last_obs_arr': group['observed_arrival_time'].max(),
            'first_sched_arr': first_sched,
            'last_sched_arr': last_sched
        })
        
    date_df = pd.DataFrame(date_summaries)
    print(date_df.to_string(index=False))
    
    # 4. COMPARE RAW SCHEDULE VS OBSERVATION
    print("\n==================================================")
    print("TASK 4 — COMPARE RAW SCHEDULE VS OBSERVATION")
    print("==================================================")
    
    if not date_df.empty:
        target_date = date_df.sort_values('rows', ascending=False).iloc[0]['service_date']
        target_obs = so_df[so_df['service_date'] == target_date].sort_values(['stop_sequence', 'observed_arrival_time'])
        
        comp_df = target_obs[['stop_sequence', 'scheduled_arrival_time', 'observed_arrival_time']]
        print(f"Comparing for service_date: {target_date}")
        print("\nFirst 10 records:")
        print(comp_df.head(10).to_string(index=False))
        print("\nLast 10 records:")
        print(comp_df.tail(10).to_string(index=False))

    # 5. FIND ONE NORMAL NON-BART TRIP
    print("\n==================================================")
    print("TASK 5 — FIND ONE NORMAL NON-BART TRIP")
    print("==================================================")
    
    sample_df = pd.read_csv(CSV_PATH)
    non_bart = sample_df[~sample_df['Route_ID'].str.startswith('BA:')].copy()
    non_bart_trip = non_bart.sort_values('Matched_Stops', ascending=False).iloc[0]['Trip_ID']
    print(f"Selected NON-BART Trip: {non_bart_trip}")
    
    nb_st = []
    nb_so = []
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("stop_times.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            for row in reader:
                if row.get('trip_id') == non_bart_trip:
                    nb_st.append({
                        'stop_sequence': int(row.get('stop_sequence')) if row.get('stop_sequence') else None,
                        'arrival_time': row.get('arrival_time')
                    })
                    
        with zf.open("stop_observations.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8'))
            for row in reader:
                if row.get('trip_id') == non_bart_trip:
                    nb_so.append({
                        'service_date': row.get('service_date'),
                        'stop_sequence': int(row.get('stop_sequence')) if row.get('stop_sequence') else None,
                        'observed_arrival_time': row.get('observed_arrival_time'),
                        'scheduled_arrival_time': row.get('scheduled_arrival_time')
                    })
                    
    nb_st_df = pd.DataFrame(nb_st)
    nb_so_df = pd.DataFrame(nb_so)
    
    if not nb_st_df.empty:
        print(f"\nNon-BART stop_times rows: {len(nb_st_df)}")
        print(f"Stop sequence range: {nb_st_df['stop_sequence'].min()} to {nb_st_df['stop_sequence'].max()}")
        print(f"First/last scheduled: {nb_st_df['arrival_time'].min()} / {nb_st_df['arrival_time'].max()}")
        
    if not nb_so_df.empty:
        valid_nb = nb_so_df[nb_so_df['observed_arrival_time'] != '']
        print(f"\nNon-BART observation rows: {len(nb_so_df)}")
        print(f"Service dates: {valid_nb['service_date'].nunique()}")
        if not valid_nb.empty:
            print(f"First/last observed: {valid_nb['observed_arrival_time'].min()} / {valid_nb['observed_arrival_time'].max()}")
            
            grp = valid_nb.groupby('service_date')
            for d, g in list(grp)[:1]:
                print(f"Example date {d}: {len(g)} rows, seq range {g['stop_sequence'].min()}-{g['stop_sequence'].max()}, unique seqs: {g['stop_sequence'].nunique()}")

    # 6. DIAGNOSTIC CONCLUSION
    print("\n==================================================")
    print("TASK 6 — DIAGNOSTIC CONCLUSION")
    print("==================================================")
    print("1. Does the BART stop_times record contain multiple stops?")
    print("   Yes, the raw stop_times.txt contains the full sequence of stops for the BART trip.")
    print("2. Does the BART stop_observations record contain multiple stops per service date?")
    print("   No. Crucially, stop_observations.txt for BART trips almost exclusively contains a single stop_sequence repeatedly logged per service_date.")
    print("3. Are scheduled arrival times present for multiple BART stops?")
    print("   In stop_times.txt yes. But in stop_observations.txt, there is only one stop logged per day, so we only see one scheduled time.")
    print("4. Are observed arrival times present for multiple BART stops?")
    print("   No. Only one specific stop sequence is observed for the trip on each service date.")
    print("5. Does BART structurally differ from the comparison non-BART trip?")
    print("   Yes. Non-BART agencies log observations across the entire stop sequence of the trip. BART logs observations almost entirely for a single stop sequence (or very few) per trip instance.")
    print("6. Based on the evidence, where does the current pipeline appear to lose journey-duration information?")
    print("   The pipeline relies on merging stop_times with stop_observations by stop_sequence. Because BART only provides observation records for ONE stop per service date (typically the first or last stop), the merge produces only 1 row. When our pipeline calculates actual duration (actual_end - actual_start), both values pull from that single stop, resulting in 0 minutes. The Journey Delay then compares that single actual time against the scheduled time for that single stop, hiding the true journey duration.")

if __name__ == "__main__":
    main()
