import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# Set random seed for reproducibility
RANDOM_STATE = 42

def train_dataset1():
    print("==================================================")
    print("TRAINING MODEL 1: 500 Person Gender Height Weight")
    print("==================================================")
    
    csv_path = 'ml/500_Person_Gender_Height_Weight_Index.csv'
    df = pd.read_csv(csv_path)
    
    # 1. Dataset overview
    n_rows, n_cols = df.shape
    print(f"Raw shape: {n_rows} rows, {n_cols} columns")
    
    # Check duplicates
    n_dupes = df.duplicated().sum()
    print(f"Duplicate records: {n_dupes}")
    # Remove exact duplicates for clean generalization
    df_clean = df.drop_duplicates().reset_index(drop=True)
    print(f"Clean shape after removing duplicates: {df_clean.shape}")
    
    # Class mapping based on notebook
    INDEX_LABELS = {
        0: 'Extremely Weak',
        1: 'Weak',
        2: 'Normal',
        3: 'Overweight',
        4: 'Obesity',
        5: 'Extreme Obesity'
    }
    
    # Class distribution
    print("\nClass distribution (Index):")
    dist = df_clean['Index'].value_counts().sort_index()
    for idx, count in dist.items():
        print(f"  Index {idx} ({INDEX_LABELS[idx]}): {count} ({count/len(df_clean)*100:.1f}%)")
        
    X = df_clean[['Gender', 'Height', 'Weight']]
    y = df_clean['Index']
    
    # Stratified Train-Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    
    # Preprocessing Pipeline (fitted ONLY on X_train to prevent data leakage)
    categorical_features = ['Gender']
    numerical_features = ['Height', 'Weight']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )
    
    # Models to compare
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=200, criterion='entropy', random_state=RANDOM_STATE),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    }
    
    comparison = {}
    best_pipe = None
    best_acc = 0.0
    best_name = ''
    
    for name, clf in models.items():
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', clf)
        ])
        # Cross validation on training data only
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring='accuracy')
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        comparison[name] = {
            'cv_mean_accuracy': float(cv_scores.mean()),
            'test_accuracy': float(acc),
            'test_f1_macro': float(f1_macro),
            'test_f1_weighted': float(f1_weighted)
        }
        print(f"\nModel: {name}")
        print(f"  5-fold CV Accuracy (Train): {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
        print(f"  Test Accuracy: {acc*100:.2f}%")
        print(f"  Test Macro F1: {f1_macro:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_pipe = pipe
            best_name = name

    # Detailed evaluation for Best Model (Random Forest or GB)
    # Using Random Forest as requested by user
    rf_pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=200, criterion='entropy', random_state=RANDOM_STATE))
    ])
    rf_pipe.fit(X_train, y_train)
    y_pred = rf_pipe.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    prec_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    unique_test_classes = sorted(y_test.unique())
    target_names = [f"Index {c} ({INDEX_LABELS[c]})" for c in unique_test_classes]
    clr = classification_report(y_test, y_pred, target_names=target_names, zero_division=0)
    
    print("\n--- FINAL TEST EVALUATION FOR RANDOM FOREST (DATASET 1) ---")
    print(f"Test Accuracy: {acc*100:.2f}%")
    print(f"Precision (Macro): {prec_macro:.4f}, Recall (Macro): {rec_macro:.4f}, F1 (Macro): {f1_macro:.4f}")
    print(f"Precision (Weighted): {prec_weighted:.4f}, Recall (Weighted): {rec_weighted:.4f}, F1 (Weighted): {f1_weighted:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:\n", clr)
    
    # Save the pipeline and artifacts
    os.makedirs('app/ml_artifacts', exist_ok=True)
    joblib.dump(rf_pipe, 'app/ml_artifacts/model_bmi_rf.joblib')
    
    results1 = {
        'dataset': '500_Person_Gender_Height_Weight_Index',
        'raw_rows': int(n_rows),
        'clean_rows': int(len(df_clean)),
        'duplicates_removed': int(n_dupes),
        'features': ['Gender', 'Height', 'Weight'],
        'target': 'Index',
        'classes': {int(k): v for k, v in INDEX_LABELS.items()},
        'class_distribution': {int(k): int(v) for k, v in dist.items()},
        'test_accuracy': float(acc),
        'test_precision_macro': float(prec_macro),
        'test_recall_macro': float(rec_macro),
        'test_f1_macro': float(f1_macro),
        'test_precision_weighted': float(prec_weighted),
        'test_recall_weighted': float(rec_weighted),
        'test_f1_weighted': float(f1_weighted),
        'confusion_matrix': cm.tolist(),
        'model_comparison': comparison
    }
    
    with open('app/ml_artifacts/metrics_dataset1.json', 'w') as f:
        json.dump(results1, f, indent=2)
        
    return results1

def train_dataset2():
    print("\n==================================================")
    print("TRAINING MODEL 2: Obesity Lifestyle Dataset (UCI)")
    print("==================================================")
    
    csv_path = 'ml/ObesityDataSet_raw_and_data_sinthetic.csv'
    df = pd.read_csv(csv_path)
    
    n_rows, n_cols = df.shape
    print(f"Raw shape: {n_rows} rows, {n_cols} columns")
    
    n_dupes = df.duplicated().sum()
    print(f"Duplicate records: {n_dupes}")
    df_clean = df.drop_duplicates().reset_index(drop=True)
    print(f"Clean shape after removing duplicates: {df_clean.shape}")
    
    target_col = 'NObeyesdad'
    feature_cols = [c for c in df_clean.columns if c != target_col]
    
    # Analyze synthetic data prevalence
    # Synthetic samples generated via SMOTE have non-integer ages and other continuous floats
    non_int_ages = (df_clean['Age'] != df_clean['Age'].round()).sum()
    print(f"Synthetic records indicator (fractional ages): {non_int_ages} / {len(df_clean)} ({non_int_ages/len(df_clean)*100:.1f}%)")
    
    print("\nClass distribution (NObeyesdad):")
    dist = df_clean[target_col].value_counts()
    for cat, count in dist.items():
        print(f"  {cat}: {count} ({count/len(df_clean)*100:.1f}%)")
        
    X = df_clean[feature_cols]
    y = df_clean[target_col]
    
    # Train-test split (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain set: {len(X_train)} samples, Test set: {len(X_test)} samples")
    
    # Identify numerical and categorical columns
    num_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object']).columns.tolist()
    
    print(f"Numerical features ({len(num_cols)}): {num_cols}")
    print(f"Categorical features ({len(cat_cols)}): {cat_cols}")
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
        ]
    )
    
    rf_pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE))
    ])
    
    # Cross validation on training data
    cv_scores = cross_val_score(rf_pipe, X_train, y_train, cv=5, scoring='accuracy')
    print(f"5-fold CV Accuracy (Train): {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
    
    rf_pipe.fit(X_train, y_train)
    y_pred = rf_pipe.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
    rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
    prec_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    clr = classification_report(y_test, y_pred, zero_division=0)
    
    print("\n--- FINAL TEST EVALUATION FOR RANDOM FOREST (DATASET 2) ---")
    print(f"Test Accuracy: {acc*100:.2f}%")
    print(f"Precision (Macro): {prec_macro:.4f}, Recall (Macro): {rec_macro:.4f}, F1 (Macro): {f1_macro:.4f}")
    print(f"Precision (Weighted): {prec_weighted:.4f}, Recall (Weighted): {rec_weighted:.4f}, F1 (Weighted): {f1_weighted:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:\n", clr)
    
    joblib.dump(rf_pipe, 'app/ml_artifacts/model_lifestyle_rf.joblib')
    
    results2 = {
        'dataset': 'ObesityDataSet_raw_and_data_sinthetic',
        'raw_rows': int(n_rows),
        'clean_rows': int(len(df_clean)),
        'duplicates_removed': int(n_dupes),
        'synthetic_fractional_age_count': int(non_int_ages),
        'synthetic_fractional_age_pct': float(non_int_ages/len(df_clean)*100),
        'features': feature_cols,
        'numerical_features': num_cols,
        'categorical_features': cat_cols,
        'target': target_col,
        'classes': sorted(y.unique().tolist()),
        'class_distribution': {str(k): int(v) for k, v in dist.items()},
        'test_accuracy': float(acc),
        'test_precision_macro': float(prec_macro),
        'test_recall_macro': float(rec_macro),
        'test_f1_macro': float(f1_macro),
        'test_precision_weighted': float(prec_weighted),
        'test_recall_weighted': float(rec_weighted),
        'test_f1_weighted': float(f1_weighted),
        'confusion_matrix': cm.tolist(),
        'classes_in_confusion_matrix': sorted(y_test.unique().tolist())
    }
    
    with open('app/ml_artifacts/metrics_dataset2.json', 'w') as f:
        json.dump(results2, f, indent=2)
        
    return results2

if __name__ == '__main__':
    train_dataset1()
    train_dataset2()
