import pandas as pd
import os

INPUT_CSV = 'data/processed/transport_sample_v2.csv'
OUTPUT_CSV = 'data/processed/transport_analysis.csv'

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return
        
    df = pd.read_csv(INPUT_CSV)
    
    orig_journeys = len(df)
    orig_routes = df['Route_ID'].nunique()
    
    # Identify BART journeys
    is_bart = df['Route_ID'].astype(str).str.startswith('BA:')
    bart_count = is_bart.sum()
    
    # Filter out BART journeys
    analysis_df = df[~is_bart].copy()
    
    final_journeys = len(analysis_df)
    final_routes = analysis_df['Route_ID'].nunique()
    final_dates = analysis_df['Service_Date'].nunique()
    
    dup_journey_ids = analysis_df['Journey_ID'].duplicated().sum()
    missing_vals = analysis_df.isnull().sum()
    
    print(f"Original number of journeys: {orig_journeys}")
    print(f"BART journeys excluded: {bart_count}")
    print(f"Final number of journeys: {final_journeys}")
    print(f"Original number of routes: {orig_routes}")
    print(f"Final number of routes: {final_routes}")
    print(f"Number of remaining service dates: {final_dates}")
    
    print("\nMissing values by column in final dataset:")
    print(missing_vals.to_string())
    
    print(f"\nDuplicate Journey_ID count in final dataset: {dup_journey_ids}")
    
    analysis_df.to_csv(OUTPUT_CSV, index=False)
    
    print("\nAnalysis dataset created successfully.")

if __name__ == '__main__':
    main()
