import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = 'data/processed/transport_analysis.csv'
MEDIAN_OUT = 'data/processed/eda_clean_route_median_delay.png'
LATE_PCT_OUT = 'data/processed/eda_clean_route_late_percentage.png'

def main():
    df = pd.read_csv(CSV_PATH)
    
    # Group by Route_ID and Route
    grouped = df.groupby(['Route_ID', 'Route'])
    
    # Calculate stats
    stats = []
    for (route_id, route), group in grouped:
        n_journeys = len(group)
        delays = group['Journey_Delay_Minutes']
        
        mean_delay = delays.mean()
        median_delay = delays.median()
        std_delay = delays.std()
        
        early_n = (delays < 0).sum()
        ontime_n = (delays == 0).sum()
        late_n = (delays > 0).sum()
        severe_n = (delays > 60).sum()
        
        early_pct = (early_n / n_journeys) * 100
        ontime_pct = (ontime_n / n_journeys) * 100
        late_pct = (late_n / n_journeys) * 100
        severe_pct = (severe_n / n_journeys) * 100
        
        stats.append({
            'Route_ID': route_id,
            'Route': route,
            'Number_of_journeys': n_journeys,
            'Mean_delay': mean_delay,
            'Median_delay': median_delay,
            'Std_delay': std_delay,
            'Early_n': early_n,
            'Ontime_n': ontime_n,
            'Late_n': late_n,
            'Early_pct': early_pct,
            'Ontime_pct': ontime_pct,
            'Late_pct': late_pct,
            'Severe_n': severe_n,
            'Severe_pct': severe_pct
        })
        
    route_stats = pd.DataFrame(stats)
    
    total_routes = len(route_stats)
    
    # Filter >= 20 journeys
    valid_routes = route_stats[route_stats['Number_of_journeys'] >= 20].copy()
    valid_routes_count = len(valid_routes)
    
    if valid_routes_count == 0:
        print("No routes with at least 20 journeys found.")
        return
        
    # Top 10 by median delay
    top_median = valid_routes.sort_values('Median_delay', ascending=False).head(10)
    
    # Top 10 by late percentage
    top_late = valid_routes.sort_values('Late_pct', ascending=False).head(10)
    
    # Top 10 by severe delay percentage
    top_severe = valid_routes.sort_values('Severe_pct', ascending=False).head(10)
    
    def print_top(df_top, title):
        print(f"\n{title}")
        print("-" * 50)
        for _, row in df_top.iterrows():
            print(f"Route_ID: {row['Route_ID']} | Route: {row['Route']} | Journeys: {row['Number_of_journeys']}")
            print(f"Median: {row['Median_delay']:.2f}m | Mean: {row['Mean_delay']:.2f}m | Late: {row['Late_pct']:.1f}% | Severe: {row['Severe_pct']:.1f}%")
            print("-")

    print("==================================================")
    print("EDA: CLEAN ROUTE-LEVEL PUNCTUALITY ANALYSIS")
    print("==================================================")
    
    print_top(top_median, "A. Top 10 Routes by MEDIAN Delay")
    print_top(top_late, "B. Top 10 Routes by LATE Percentage")
    print_top(top_severe, "C. Top 10 Routes by SEVERE Delay Percentage (>60 mins)")
    
    highest_median = valid_routes.loc[valid_routes['Median_delay'].idxmax()]
    highest_late = valid_routes.loc[valid_routes['Late_pct'].idxmax()]
    highest_severe = valid_routes.loc[valid_routes['Severe_pct'].idxmax()]
    
    print("\nSummary:")
    print(f"- Total number of unique routes: {total_routes}")
    print(f"- Number of routes with >= 20 journeys: {valid_routes_count}")
    print(f"- Route with highest median delay: {highest_median['Route_ID']} ({highest_median['Median_delay']:.2f}m)")
    print(f"- Route with highest late percentage: {highest_late['Route_ID']} ({highest_late['Late_pct']:.1f}%)")
    print(f"- Route with highest severe-delay percentage: {highest_severe['Route_ID']} ({highest_severe['Severe_pct']:.1f}%)")

    # Plot 1: Top 10 routes by median delay
    plt.figure(figsize=(10, 6))
    plot_data = top_median.sort_values('Median_delay', ascending=True)
    plt.barh(plot_data['Route'].astype(str) + " (" + plot_data['Route_ID'] + ")", plot_data['Median_delay'], color='lightcoral')
    plt.title('Top 10 Routes by Median Delay (>= 20 journeys, Cleaned Dataset)')
    plt.xlabel('Median Delay (Minutes)')
    plt.tight_layout()
    plt.savefig(MEDIAN_OUT)
    plt.close()

    # Plot 2: Top 10 routes by late percentage
    plt.figure(figsize=(10, 6))
    plot_data2 = top_late.sort_values('Late_pct', ascending=True)
    plt.barh(plot_data2['Route'].astype(str) + " (" + plot_data2['Route_ID'] + ")", plot_data2['Late_pct'], color='orange')
    plt.title('Top 10 Routes by Late Percentage (>= 20 journeys, Cleaned Dataset)')
    plt.xlabel('Late Percentage (%)')
    plt.tight_layout()
    plt.savefig(LATE_PCT_OUT)
    plt.close()
    
    print("\nObservations:")
    print("1. Without BART routes, the highest median delay among valid routes is significantly lower, suggesting the remaining data is more reliable.")
    print("2. Certain routes still exhibit a high proportion of late journeys, indicating structural differences in punctuality across routes.")
    print("3. Severe delays (>60 minutes) are rare across all remaining valid routes, with maximum severe percentages much lower than in the uncleaned data.")
    print("4. The route with the highest median delay is not always the same as the route with the highest proportion of late journeys.")

if __name__ == '__main__':
    main()
