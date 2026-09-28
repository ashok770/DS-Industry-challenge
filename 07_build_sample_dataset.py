import os
import zipfile
import csv
import io
import pandas as pd

ZIP_PATH = "data/511_2025_03_so.zip"
OUTPUT_DIR = "data/processed"
PARQUET_OUT = os.path.join(OUTPUT_DIR, "transport_sample_v2.parquet")
CSV_OUT = os.path.join(OUTPUT_DIR, "transport_sample_v2.csv")

def time_to_minutes(time_str):
    """
    Converts GTFS time strings like 'HH:MM:SS' or '25:30:00' to total minutes since midnight.
    This safely handles times past midnight (e.g., 25:30 = 1530 minutes).
    Returns None if time_str is missing or invalid.
    """
    if not time_str or not isinstance(time_str, str):
        return None
    try:
        parts = time_str.split(':')
        if len(parts) >= 2:
            h = int(parts[0])
            m = int(parts[1])
            s = int(parts[2]) / 60 if len(parts) > 2 else 0
            return h * 60 + m + s
    except ValueError:
        pass
    return None

def main():
    if not os.path.exists(ZIP_PATH):
        print(f"Error: ZIP file not found at {ZIP_PATH}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("1. Loading routes and selecting candidate trips...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("routes.txt") as f:
            routes_df = pd.read_csv(f, usecols=['route_id', 'route_short_name', 'route_long_name'])
        
        with zf.open("trips.txt") as f:
            trips_df = pd.read_csv(f, usecols=['route_id', 'trip_id', 'direction_id'])
            
    candidate_trips_df = trips_df.sample(n=min(3000, len(trips_df)), random_state=42)
    candidate_trip_ids = set(candidate_trips_df['trip_id'].astype(str).tolist())
    
    print(f"Selected {len(candidate_trip_ids)} candidate trips.")

    print("2. Streaming stop_times.txt...")
    stop_times_filtered = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("stop_times.txt") as f:
            text_f = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.DictReader(text_f)
            for row in reader:
                if row.get('trip_id') in candidate_trip_ids:
                    stop_times_filtered.append({
                        'trip_id': row['trip_id'],
                        'stop_sequence': int(row['stop_sequence']) if row.get('stop_sequence') else None,
                        'scheduled_arrival_time': row.get('arrival_time'),
                        'scheduled_departure_time': row.get('departure_time'),
                        'shape_dist_traveled': float(row['shape_dist_traveled']) if row.get('shape_dist_traveled') else None
                    })
    
    st_df = pd.DataFrame(stop_times_filtered)
    print(f"Extracted {len(st_df)} stop_time records for candidate trips.")

    print("3. Streaming stop_observations.txt...")
    stop_obs_filtered = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        with zf.open("stop_observations.txt") as f:
            text_f = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.DictReader(text_f)
            for row in reader:
                if row.get('trip_id') in candidate_trip_ids:
                    stop_obs_filtered.append({
                        'trip_id': row['trip_id'],
                        'service_date': row.get('service_date'),
                        'stop_sequence': int(row['stop_sequence']) if row.get('stop_sequence') else None,
                        'observed_arrival_time': row.get('observed_arrival_time'),
                        'observed_departure_time': row.get('observed_departure_time'),
                        'vehicle_id': row.get('vehicle_id'),
                        'uncertainty': row.get('uncertainty'),
                        'scheduled_arrival_time_obs': row.get('scheduled_arrival_time'),
                        'scheduled_departure_time_obs': row.get('scheduled_departure_time')
                    })
    
    so_df = pd.DataFrame(stop_obs_filtered)
    print(f"Extracted {len(so_df)} stop_observation records for candidate trips.")

    print("4. Processing and deduplicating observations...")
    if st_df.empty or so_df.empty:
        print("No matching records found to process.")
        return

    # A. Check for raw duplicates in so_df (trip_id + service_date + stop_sequence)
    raw_obs_dups = so_df.duplicated(subset=['trip_id', 'service_date', 'stop_sequence']).sum()
    print(f"Found {raw_obs_dups} raw duplicate observations for (trip_id + service_date + stop_sequence).")

    # Drop missing observed_arrival_time
    so_df = so_df.dropna(subset=['observed_arrival_time'])
    
    # Parse observed arrival time to minutes for proper sorting
    so_df['obs_arr_min'] = so_df['observed_arrival_time'].apply(time_to_minutes)
    
    # Deduplicate observations: sort by obs_arr_min ascending and keep the first
    # This keeps the earliest valid observed arrival for the stop.
    so_df = so_df.sort_values(by=['trip_id', 'service_date', 'stop_sequence', 'obs_arr_min'])
    so_dedup = so_df.drop_duplicates(subset=['trip_id', 'service_date', 'stop_sequence'], keep='first')
    
    print(f"After deduplication, retained {len(so_dedup)} unique observation records.")

    print("5. Merging scheduled and observed data...")
    # Merge scheduled (stop_times) with deduplicated observations
    merged = pd.merge(st_df, so_dedup, on=['trip_id', 'stop_sequence'], how='inner')
    merged = merged.dropna(subset=['scheduled_arrival_time', 'observed_arrival_time'])
    
    merged['sched_arr_min'] = merged['scheduled_arrival_time'].apply(time_to_minutes)
    merged = merged.dropna(subset=['sched_arr_min', 'obs_arr_min'])

    print(f"Matched and time-parsed {len(merged)} stop-level records.")

    print("6. Aggregating to Journey Level...")
    journeys = []
    
    # Group by trip_id AND service_date to form unique journey instances
    grouped = merged.groupby(['trip_id', 'service_date'])
    for (trip_id, service_date), group in grouped:
        group = group.sort_values('stop_sequence')
        
        sched_start = group['sched_arr_min'].iloc[0]
        sched_end = group['sched_arr_min'].iloc[-1]
        
        actual_start = group['obs_arr_min'].iloc[0]
        actual_end = group['obs_arr_min'].iloc[-1]
        
        sched_duration = sched_end - sched_start
        actual_duration = actual_end - actual_start
        duration_diff = actual_duration - sched_duration
        
        # Journey Delay Logic: 
        # actual arrival time at the final matched stop minus scheduled arrival time at the final matched stop
        journey_delay = actual_end - sched_end
        
        matched_stops = len(group)
        
        # Distance logic: Max - Min of valid values
        dists = group['shape_dist_traveled'].dropna()
        if len(dists) >= 2:
            distance = dists.max() - dists.min()
        else:
            distance = None
            
        journeys.append({
            'Journey_ID': f"{trip_id}_{service_date}",
            'trip_id': trip_id, # Keep temporarily for joins
            'Service_Date': service_date,
            'Scheduled_Start': sched_start,
            'Scheduled_End': sched_end,
            'Actual_Start': actual_start,
            'Actual_End': actual_end,
            'Scheduled_Duration_Minutes': sched_duration,
            'Actual_Duration_Minutes': actual_duration,
            'Duration_Difference_Minutes': duration_diff,
            'Journey_Delay_Minutes': journey_delay,
            'Matched_Stops': matched_stops,
            'Distance': distance
        })
        
    journey_df = pd.DataFrame(journeys)
    
    # Get total Number_of_Stops scheduled for these trips
    total_stops = st_df.groupby('trip_id').size().reset_index(name='Number_of_Stops')
    total_stops['trip_id'] = total_stops['trip_id'].astype(str)
    
    journey_df['trip_id'] = journey_df['trip_id'].astype(str)
    journey_df = journey_df.merge(total_stops, on='trip_id', how='left')
    
    # Join Route info and direction
    candidate_trips_df['trip_id'] = candidate_trips_df['trip_id'].astype(str)
    journey_df = journey_df.merge(candidate_trips_df[['trip_id', 'route_id', 'direction_id']], on='trip_id', how='inner')
    
    routes_df['route_id'] = routes_df['route_id'].astype(str)
    journey_df['route_id'] = journey_df['route_id'].astype(str)
    journey_df = journey_df.merge(routes_df, on='route_id', how='inner')
    
    # Clean up and Rename
    journey_df = journey_df.rename(columns={
        'trip_id': 'Trip_ID',
        'route_id': 'Route_ID',
        'route_short_name': 'Route',
        'route_long_name': 'Route_Name',
        'direction_id': 'Direction'
    })
    
    col_order = [
        'Journey_ID', 'Trip_ID', 'Service_Date', 'Route_ID', 'Route', 'Route_Name', 'Direction',
        'Scheduled_Start', 'Scheduled_End', 'Actual_Start', 'Actual_End',
        'Scheduled_Duration_Minutes', 'Actual_Duration_Minutes', 
        'Duration_Difference_Minutes', 'Journey_Delay_Minutes',
        'Number_of_Stops', 'Matched_Stops', 'Distance'
    ]
    journey_df = journey_df[col_order]
    
    print("7. Performing Data Quality Checks...")
    
    # B. Duplicate final Journey_ID
    dup_journey_ids = journey_df['Journey_ID'].duplicated().sum()
    
    # C. Negative scheduled duration
    neg_sched_dur = (journey_df['Scheduled_Duration_Minutes'] < 0).sum()
    
    # D. Negative actual duration
    neg_act_dur = (journey_df['Actual_Duration_Minutes'] < 0).sum()
    
    # E. Duration > 1440 minutes
    large_sched_dur = (journey_df['Scheduled_Duration_Minutes'] > 1440).sum()
    large_act_dur = (journey_df['Actual_Duration_Minutes'] > 1440).sum()
    
    # F. Missing distance
    missing_dist = journey_df['Distance'].isnull().sum()
    
    # G. Missing Service_Date
    missing_service_date = journey_df['Service_Date'].isnull().sum()
    
    # H. Missing Journey_ID
    missing_journey_id = journey_df['Journey_ID'].isnull().sum()
    
    # I. Number of unique journey instances
    unique_journeys = journey_df['Journey_ID'].nunique()
    
    # J. Number of unique trip_ids
    unique_trips = journey_df['Trip_ID'].nunique()
    
    # K. Number of unique service dates
    unique_dates = journey_df['Service_Date'].nunique()
    
    # L. Number of unique routes
    unique_routes = journey_df['Route_ID'].nunique()
    
    print("\n============================================================")
    print("TRANSPORT SAMPLE DATASET v2 - QUALITY REPORT")
    print("============================================================")
    print(f"Candidate scheduled trips selected: {len(candidate_trip_ids)}")
    print(f"A. Duplicate raw observed (trip_id+date+stop): {raw_obs_dups}")
    print(f"B. Duplicate final Journey_ID count: {dup_journey_ids}")
    print(f"C. Negative scheduled duration count: {neg_sched_dur}")
    print(f"D. Negative actual duration count: {neg_act_dur}")
    print(f"E. Unusually large sched/actual duration (>1440 mins): {large_sched_dur} / {large_act_dur}")
    print(f"F. Missing distance count: {missing_dist}")
    print(f"G. Missing Service_Date count: {missing_service_date}")
    print(f"H. Missing Journey_ID count: {missing_journey_id}")
    print(f"I. Number of unique journey instances: {unique_journeys}")
    print(f"J. Number of unique trip_ids found: {unique_trips}")
    print(f"K. Number of unique service dates: {unique_dates}")
    print(f"L. Number of unique routes: {unique_routes}")
    
    print("\nMissing values by column:")
    print(journey_df.isnull().sum().to_string())

    print("\nSaving files...")
    journey_df.to_parquet(PARQUET_OUT, index=False)
    journey_df.to_csv(CSV_OUT, index=False)
    
    print(f"\nOutput:")
    print(f"{PARQUET_OUT}")
    print(f"{CSV_OUT}")

if __name__ == "__main__":
    main()
