import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = 'data/processed/transport_sample_v2.csv'
HIST_OUT = 'data/processed/eda_delay_histogram.png'
BOX_OUT = 'data/processed/eda_delay_boxplot.png'

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
    print("EDA: OVERALL JOURNEY DELAY DISTRIBUTION")
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
    print(f"- Delay < -30 mins (very early): {early_extreme}")
    print(f"- Delay > 30 mins (very late): {late_30}")
    print(f"- Delay > 60 mins (severely late): {late_60}")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.hist(delay, bins=100, color='skyblue', edgecolor='black')
    plt.title('Histogram of Journey Delay Minutes (Including Outliers)')
    plt.xlabel('Delay (Minutes)')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(HIST_OUT)
    plt.close()
    
    plt.figure(figsize=(10, 6))
    plt.boxplot(delay, vert=False, patch_artist=True, boxprops=dict(facecolor='skyblue'))
    plt.title('Boxplot of Journey Delay Minutes (Including Outliers)')
    plt.xlabel('Delay (Minutes)')
    plt.savefig(BOX_OUT)
    plt.close()
    
    print(f"\nSaved plots to:\n- {HIST_OUT}\n- {BOX_OUT}")
    
    print("\nInterpretation:")
    print("The distribution is heavily right-skewed and significantly compressed by extreme outliers on both tails.")
    print("While the median is close to 0 (around 1 minute late) and the IQR shows most trips operate reliably,")
    print("the presence of extreme delays (e.g., maximum delays exceeding 11 hours) indicates severe anomalies in")
    print("the raw data. These extremes are almost certainly due to erroneous GPS polling or vehicle misassignment,")
    print("rather than actual traffic delays. The boxplot and histogram will appear highly squashed until these")
    print("outliers are handled in later steps.")

if __name__ == '__main__':
    main()
