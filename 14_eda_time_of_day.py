import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = 'data/processed/transport_analysis.csv'
MEDIAN_OUT = 'data/processed/eda_time_median_delay.png'
LATE_PCT_OUT = 'data/processed/eda_time_late_percentage.png'

# Define time-of-day categories
TIME_BUCKETS = {
    'Morning': (5, 10),       # 05:00–10:59 -> hours 5-10
    'Afternoon': (11, 15),    # 11:00–15:59 -> hours 11-15
    'Evening': (16, 20),      # 16:00–20:59 -> hours 16-20
    'Night': (21, 23),        # 21:00–23:59 -> hours 21-23
    # Night also covers 0-4, handled separately
}

def assign_period(hour):
    # hour is in 0-23 range
    if 5 <= hour <= 10:
        return 'Morning'
    if 11 <= hour <= 15:
        return 'Afternoon'
    if 16 <= hour <= 20:
        return 'Evening'
    # Night includes 21-23 and 0-4
    return 'Night'

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return
    df = pd.read_csv(CSV_PATH)

    # Convert Scheduled_Start (minutes since midnight) to hour
    df['Scheduled_Hour'] = (df['Scheduled_Start'] // 60) % 24
    df['TimePeriod'] = df['Scheduled_Hour'].apply(assign_period)

    # Prepare aggregation
    periods = ['Morning', 'Afternoon', 'Evening', 'Night']
    rows = []
    for period in periods:
        sub = df[df['TimePeriod'] == period]
        n = len(sub)
        if n == 0:
            # Guard against empty period (should not happen)
            rows.append({
                'Period': period,
                'Journeys': 0,
                'MeanDelay': None,
                'MedianDelay': None,
                'StdDelay': None,
                'EarlyPct': None,
                'OnTimePct': None,
                'LatePct': None,
                'SevereCount': 0,
                'SeverePct': None,
            })
            continue
        delay = sub['Journey_Delay_Minutes']
        mean = delay.mean()
        median = delay.median()
        std = delay.std()
        early = (delay < 0).sum()
        ontime = (delay == 0).sum()
        late = (delay > 0).sum()
        severe = (delay > 60).sum()
        rows.append({
            'Period': period,
            'Journeys': n,
            'MeanDelay': mean,
            'MedianDelay': median,
            'StdDelay': std,
            'EarlyPct': (early / n) * 100,
            'OnTimePct': (ontime / n) * 100,
            'LatePct': (late / n) * 100,
            'SevereCount': severe,
            'SeverePct': (severe / n) * 100,
        })
    summary = pd.DataFrame(rows)
    # Print table sorted chronologically as defined above
    print("==================================================")
    print("EDA: JOURNEY DELAY BY TIME OF DAY (CLEANED DATASET)")
    print("==================================================")
    print(summary[['Period', 'Journeys', 'MeanDelay', 'MedianDelay', 'StdDelay',
                   'EarlyPct', 'OnTimePct', 'LatePct', 'SevereCount', 'SeverePct']].to_string(index=False))

    # Identify extreme periods
    highest_median = summary.loc[summary['MedianDelay'].idxmax()]['Period']
    highest_mean = summary.loc[summary['MeanDelay'].idxmax()]['Period']
    highest_late_pct = summary.loc[summary['LatePct'].idxmax()]['Period']
    highest_severe_pct = summary.loc[summary['SeverePct'].idxmax()]['Period']
    print("\nExtremes:")
    print(f"Period with highest median delay: {highest_median}")
    print(f"Period with highest mean delay: {highest_mean}")
    print(f"Period with highest late percentage: {highest_late_pct}")
    print(f"Period with highest severe‑delay percentage: {highest_severe_pct}")

    # Plot median delay bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(summary['Period'], summary['MedianDelay'], color='steelblue')
    plt.title('Median Journey Delay by Time of Day')
    plt.ylabel('Median Delay (minutes)')
    plt.xlabel('Time Period')
    plt.tight_layout()
    plt.savefig(MEDIAN_OUT)
    plt.close()

    # Plot late percentage bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(summary['Period'], summary['LatePct'], color='seagreen')
    plt.title('Late Journey Percentage by Time of Day')
    plt.ylabel('Late Percentage (%)')
    plt.xlabel('Time Period')
    plt.tight_layout()
    plt.savefig(LATE_PCT_OUT)
    plt.close()

    print("\nSaved plots to:")
    print(f"- {MEDIAN_OUT}")
    print(f"- {LATE_PCT_OUT}")

    print("\nObservations:")
    print("1. The median delay differs across periods, with the highest measured median delay occurring in the period identified above.")
    print("2. Late‑journey percentages vary, highlighting when trips are most frequently delayed.")
    print("3. Severe delays (>60 min) remain relatively rare in all periods, but one period shows the highest proportion.")
    print("4. Early‑arrival percentages are also provided, showing that some periods have a notable share of journeys arriving ahead of schedule.")

if __name__ == '__main__':
    main()
