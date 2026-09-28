import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = 'data/processed/transport_analysis.csv'

SCATTER_OUT = 'data/processed/eda_scheduled_vs_actual_duration.png'
DIFF_OUT = 'data/processed/eda_duration_difference.png'


def main():

    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    df = pd.read_csv(CSV_PATH)

    scheduled = df['Scheduled_Duration_Minutes']
    actual = df['Actual_Duration_Minutes']
    difference = df['Duration_Difference_Minutes']

    # ---------------------------------------------------------
    # Basic statistics
    # ---------------------------------------------------------

    longer = (difference > 0).sum()
    shorter = (difference < 0).sum()
    same = (difference == 0).sum()

    negative_actual = (actual < 0).sum()

    print("=" * 60)
    print("EDA: SCHEDULED VS ACTUAL JOURNEY DURATION")
    print("=" * 60)

    print(f"Total journeys: {len(df)}")

    print("\nScheduled Duration")
    print(f"Mean:   {scheduled.mean():.2f} minutes")
    print(f"Median: {scheduled.median():.2f} minutes")

    print("\nActual Duration")
    print(f"Mean:   {actual.mean():.2f} minutes")
    print(f"Median: {actual.median():.2f} minutes")

    print("\nDuration Difference")
    print(f"Mean:   {difference.mean():.2f} minutes")
    print(f"Median: {difference.median():.2f} minutes")

    print("\nJourney Duration Comparison")

    print(
        f"Longer than scheduled: "
        f"{longer} ({longer / len(df) * 100:.2f}%)"
    )

    print(
        f"Shorter than scheduled: "
        f"{shorter} ({shorter / len(df) * 100:.2f}%)"
    )

    print(
        f"Same as scheduled: "
        f"{same} ({same / len(df) * 100:.2f}%)"
    )

    print("\nData Quality Check")

    print(
        f"Negative actual-duration journeys: "
        f"{negative_actual}"
    )

    # ---------------------------------------------------------
    # Visualization 1
    # Scheduled vs Actual Duration
    # ---------------------------------------------------------

    plt.figure(figsize=(8, 6))

    plt.scatter(
        scheduled,
        actual,
        alpha=0.4
    )

    # Reference line: actual = scheduled
    min_value = min(scheduled.min(), actual.min())
    max_value = max(scheduled.max(), actual.max())

    plt.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle='--'
    )

    plt.title('Scheduled Duration vs Actual Duration')
    plt.xlabel('Scheduled Duration (minutes)')
    plt.ylabel('Actual Duration (minutes)')

    plt.tight_layout()
    plt.savefig(SCATTER_OUT)
    plt.close()

    # ---------------------------------------------------------
    # Visualization 2
    # Duration Difference
    # ---------------------------------------------------------

    plt.figure(figsize=(8, 5))

    plt.hist(
        difference,
        bins=50
    )

    plt.axvline(
        0,
        linestyle='--'
    )

    plt.title('Distribution of Duration Difference')
    plt.xlabel(
        'Actual Duration - Scheduled Duration (minutes)'
    )
    plt.ylabel('Number of Journeys')

    plt.tight_layout()
    plt.savefig(DIFF_OUT)
    plt.close()

    print("\nSaved plots:")
    print(f"- {SCATTER_OUT}")
    print(f"- {DIFF_OUT}")

    # ---------------------------------------------------------
    # Observations
    # ---------------------------------------------------------

    print("\nObservations:")

    print(
        "1. The comparison shows how actual journey duration "
        "differs from the scheduled duration."
    )

    print(
        "2. A positive duration difference means the journey "
        "took longer than scheduled."
    )

    print(
        "3. A negative duration difference means the journey "
        "took less time than scheduled."
    )

    print(
        "4. Negative actual-duration records indicate "
        "data-quality issues and should be investigated."
    )


if __name__ == '__main__':
    main()