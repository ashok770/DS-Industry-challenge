import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


CSV_PATH = 'data/processed/transport_analysis.csv'


def main():

    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    df = pd.read_csv(CSV_PATH)

    print("=" * 60)
    print("RANDOM FOREST REGRESSION — BUS DELAY PREDICTION")
    print("=" * 60)

    print(f"Total rows: {len(df)}")

    # ---------------------------------------------------------
    # 1. Select features and target
    # ---------------------------------------------------------

    target = 'Journey_Delay_Minutes'

    features = [
        'Route_ID',
        'Route',
        'Route_Name',
        'Direction',
        'Scheduled_Start',
        'Scheduled_Duration_Minutes',
        'Number_of_Stops',
        'Distance'
    ]

    X = df[features].copy()
    y = df[target].copy()

    # ---------------------------------------------------------
    # 2. Remove rows with missing model inputs
    # ---------------------------------------------------------

    before = len(X)

    valid_mask = X.notna().all(axis=1) & y.notna()

    X = X[valid_mask]
    y = y[valid_mask]

    removed = before - len(X)

    print(f"\nRows removed because of missing model inputs: {removed}")
    print(f"Rows available for modelling: {len(X)}")

    # ---------------------------------------------------------
    # 3. Identify feature types
    # ---------------------------------------------------------

    categorical_features = [
        'Route_ID',
        'Route',
        'Route_Name',
        'Direction'
    ]

    numerical_features = [
        'Scheduled_Start',
        'Scheduled_Duration_Minutes',
        'Number_of_Stops',
        'Distance'
    ]

    # ---------------------------------------------------------
    # 4. Train/Test Split
    # ---------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    print("\nTrain/Test Split")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows:  {len(X_test)}")

    # ---------------------------------------------------------
    # 5. Preprocessing
    # ---------------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                'categorical',
                OneHotEncoder(
                    handle_unknown='ignore'
                ),
                categorical_features
            )
        ],
        remainder='passthrough'
    )

    # ---------------------------------------------------------
    # 6. Random Forest
    # ---------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        max_depth=None
    )

    pipeline = Pipeline(
        steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ]
    )

    # ---------------------------------------------------------
    # 7. Train
    # ---------------------------------------------------------

    print("\nTraining Random Forest...")

    pipeline.fit(X_train, y_train)

    print("Training completed.")

    # ---------------------------------------------------------
    # 8. Prediction
    # ---------------------------------------------------------

    y_pred = pipeline.predict(X_test)

    # ---------------------------------------------------------
    # 9. Evaluation
    # ---------------------------------------------------------

    mae = mean_absolute_error(y_test, y_pred)

    rmse = np.sqrt(
        mean_squared_error(y_test, y_pred)
    )

    r2 = r2_score(y_test, y_pred)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    print(f"MAE  : {mae:.3f} minutes")
    print(f"RMSE : {rmse:.3f} minutes")
    print(f"R²   : {r2:.3f}")

    # ---------------------------------------------------------
    # 10. Prediction examples
    # ---------------------------------------------------------

    results = pd.DataFrame({
        'Actual_Delay': y_test.values,
        'Predicted_Delay': y_pred
    })

    print("\nSample Predictions:")
    print(results.head(10).to_string(index=False))

    # ---------------------------------------------------------
    # 11. Feature importance
    # ---------------------------------------------------------

    feature_names = pipeline.named_steps[
        'preprocessor'
    ].get_feature_names_out()

    importances = pipeline.named_steps[
        'model'
    ].feature_importances_

    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    })

    importance_df = importance_df.sort_values(
        by='Importance',
        ascending=False
    )

    print("\nTop 20 Model Features:")
    print(
        importance_df.head(20).to_string(index=False)
    )

    # ---------------------------------------------------------
    # 12. Save feature importance
    # ---------------------------------------------------------

    output_path = (
        'data/processed/'
        'random_forest_feature_importance.csv'
    )

    importance_df.to_csv(
        output_path,
        index=False
    )

    print(f"\nFeature importance saved to:")
    print(output_path)


if __name__ == '__main__':
    main()