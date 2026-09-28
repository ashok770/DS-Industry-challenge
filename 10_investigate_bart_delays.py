import pandas as pd

CSV_PATH = 'data/processed/transport_sample_v2.csv'

def get_stats(df):
    n = len(df)
    if n == 0:
        return {}
    
    delays = df['Journey_Delay_Minutes']
    late_pct = (delays > 0).sum() / n * 100
    severe_pct = (delays > 60).sum() / n * 100
    
    return {
        'Number of journeys': n,
        'Number of unique routes': df['Route_ID'].nunique(),
        'Mean delay': delays.mean(),
        'Median delay': delays.median(),
        'Minimum delay': delays.min(),
        'Maximum delay': delays.max(),
        'Percentage late (>0)': late_pct,
        'Percentage severe (>60m)': severe_pct
    }

def print_stats(stats_dict):
    for k, v in stats_dict.items():
        if 'Percentage' in k:
            print(f"  {k}: {v:.1f}%")
        elif 'delay' in k:
            print(f"  {k}: {v:.2f} mins")
        else:
            print(f"  {k}: {v}")

def main():
    df = pd.read_csv(CSV_PATH)
    
    is_bart = df['Route_ID'].str.startswith('BA:')
    bart_df = df[is_bart]
    non_bart_df = df[~is_bart]
    
    print("==================================================")
    print("TASK 1 & 2: BART vs NON-BART COMPARISON")
    print("==================================================")
    print("\n--- BART Journeys ---")
    bart_stats = get_stats(bart_df)
    print_stats(bart_stats)
    
    print("\n--- NON-BART Journeys ---")
    non_bart_stats = get_stats(non_bart_df)
    print_stats(non_bart_stats)
    
    print("\n==================================================")
    print("TASK 3 & 4: SAMPLE OF 5 TARGET BART ROUTES")
    print("==================================================")
    target_routes = ['BA:Green-N', 'BA:Green-S', 'BA:Red-N', 'BA:Blue-N', 'BA:Blue-S']
    
    cols = ['Journey_ID', 'Trip_ID', 'Service_Date', 'Scheduled_Start', 'Scheduled_End',
            'Actual_Start', 'Actual_End', 'Scheduled_Duration_Minutes', 'Actual_Duration_Minutes',
            'Duration_Difference_Minutes', 'Journey_Delay_Minutes', 'Number_of_Stops']
            
    for r in target_routes:
        route_df = bart_df[bart_df['Route_ID'] == r]
        sample = route_df.sort_values('Journey_Delay_Minutes', ascending=False).head(5)[cols]
        print(f"\nRoute: {r}")
        print("-" * 50)
        print(sample.to_string(index=False))
        
        # TASK 4 diagnostic observation
        median_sched = route_df['Scheduled_Duration_Minutes'].median()
        median_act = route_df['Actual_Duration_Minutes'].median()
        median_diff = route_df['Duration_Difference_Minutes'].median()
        median_delay = route_df['Journey_Delay_Minutes'].median()
        print(f"\n[Observation for {r}]: Median Sched Dur: {median_sched:.2f}m | Median Act Dur: {median_act:.2f}m | Median Diff: {median_diff:.2f}m | Median Delay: {median_delay:.2f}m")
    
    print("\n==================================================")
    print("TASK 5: SUSPICIOUS PATTERNS AMONG BART JOURNEYS")
    print("==================================================")
    cond1 = (bart_df['Actual_Duration_Minutes'] > 2 * bart_df['Scheduled_Duration_Minutes']).sum()
    cond2 = (bart_df['Journey_Delay_Minutes'] > 60).sum()
    cond3 = (bart_df['Actual_Duration_Minutes'] > 120).sum()
    cond4 = (bart_df['Scheduled_Duration_Minutes'] <= 0).sum()
    cond5 = (bart_df['Actual_Duration_Minutes'] <= 0).sum()
    
    print(f"1. Actual duration > 2x scheduled duration: {cond1}")
    print(f"2. Journey delay > 60 minutes: {cond2}")
    print(f"3. Actual duration > 120 minutes: {cond3}")
    print(f"4. Scheduled duration <= 0: {cond4}")
    print(f"5. Actual duration <= 0: {cond5}")
    
    print("\n==================================================")
    print("TASK 6: MEDIAN DURATION COMPARISON")
    print("==================================================")
    print(f"{'Metric':<30} | {'BART':<10} | {'Non-BART':<10}")
    print("-" * 55)
    print(f"{'Median scheduled duration':<30} | {bart_df['Scheduled_Duration_Minutes'].median():<10.2f} | {non_bart_df['Scheduled_Duration_Minutes'].median():<10.2f}")
    print(f"{'Median actual duration':<30} | {bart_df['Actual_Duration_Minutes'].median():<10.2f} | {non_bart_df['Actual_Duration_Minutes'].median():<10.2f}")
    print(f"{'Median duration diff':<30} | {bart_df['Duration_Difference_Minutes'].median():<10.2f} | {non_bart_df['Duration_Difference_Minutes'].median():<10.2f}")
    print(f"{'Median journey delay':<30} | {bart_df['Journey_Delay_Minutes'].median():<10.2f} | {non_bart_df['Journey_Delay_Minutes'].median():<10.2f}")
    
    print("\n==================================================")
    print("TASK 7: DIAGNOSTIC CONCLUSION")
    print("==================================================")
    print("The median scheduled duration and actual duration for BART trips are fairly similar (difference is minimal).")
    print("However, the overall Journey Delay is massive for BART compared to non-BART trips.")
    print("This shows a systematic difference where BART actual timestamps are consistently shifted relative to the scheduled timestamps by roughly an hour.")
    print("Since the duration of the trips themselves is normal, this is consistent with a possible timestamp/matching issue (e.g. a time-zone offset error or systematic polling delay specifically for BART feeds) rather than genuine operational traffic delays.")

if __name__ == '__main__':
    main()
