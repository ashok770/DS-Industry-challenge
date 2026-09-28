import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = 'data/processed/transport_analysis.csv'
HIST_OUT = 'data/processed/eda_clean_delay_histogram.png'
BOX_OUT = 'data/processed/eda_clean_delay_boxplot.png'

def main():
    df = pd.read_csv(CSV_PATH)
    delay = df['Journey_Delay_Minutes']
    
    n_journeys = len(delay)
    mean_val = delay.mean()
    median_val = delay.median()
    std_val = delay.std()
    min_val = delay.min()
    max_val = delay.max()
    p25 = delay.quantile(0.25)
    p75 = delay.quantile(0.75)
    
    early_n = (delay < 0).sum()
    ontime_n = (delay == 0).sum()
    late_n = (delay > 0).sum()
    
    early_pct = (early_n / n_journeys) * 100
    ontime_pct = (ontime_n / n_journeys) * 100
    late_pct = (late_n / n_journeys) * 100
    
    early_extreme = (delay < -30).sum()
    late_30 = (delay > 30).sum()
    late_60 = (delay > 60).sum()
    
    print("==================================================")
    print("EDA: CLEAN OVERALL JOURNEY DELAY DISTRIBUTION")
    print("==================================================")
    print(f"1. Number of journeys: {n_journeys}")
    print(f"2. Mean delay: {mean_val:.2f} mins")
    print(f"3. Median delay: {median_val:.2f} mins")
    print(f"4. Standard deviation: {std_val:.2f} mins")
    print(f"5. Minimum delay: {min_val:.2f} mins")
    print(f"6. Maximum delay: {max_val:.2f} mins")
    print(f"7. 25th percentile: {p25:.2f} mins")
    print(f"8. 75th percentile: {p75:.2f} mins")
    
    print("\nDelay Categories:")
    print(f"9. Early (< 0): {early_n} ({early_pct:.1f}%)")
    print(f"10. On-Time (== 0): {ontime_n} ({ontime_pct:.1f}%)")
    print(f"11. Late (> 0): {late_n} ({late_pct:.1f}%)")
    
    print("\nExtremes:")
    print(f"12. Delay < -30 mins: {early_extreme}")
    print(f"13. Delay > 30 mins: {late_30}")
    print(f"14. Delay > 60 mins: {late_60}")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.hist(delay, bins=100, color='lightgreen', edgecolor='black')
    plt.title('Histogram of Journey Delay Minutes (Cleaned Dataset)')
    plt.xlabel('Delay (Minutes)')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(HIST_OUT)
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.boxplot(delay, vert=False, patch_artist=True, boxprops=dict(facecolor='lightgreen'))
    plt.title('Boxplot of Journey Delay Minutes (Cleaned Dataset)')
    plt.xlabel('Delay (Minutes)')
    plt.savefig(BOX_OUT)
    plt.close()
    
    print(f"\nSaved plots to:\n- {HIST_OUT}\n- {BOX_OUT}")
    
    print("\nInterpretation:")
    print("With BART removed, the distribution is much more centered, showing a median delay of roughly 1 minute.")
    print("The extreme right-tail skew has been significantly reduced, though some severe outliers (>10 hours late) still exist.")
    print("The majority of trips operate within a narrow band of punctuality, slightly favoring late arrivals over early arrivals.")

if __name__ == '__main__':
    main()
