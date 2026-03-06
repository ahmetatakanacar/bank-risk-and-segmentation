import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data.csv")

df.drop(["Musteri_ID", "Musteri_Adi", "Plaka_Kodu"], axis=1, inplace=True)
df.drop_duplicates(inplace = True)

df["Gecikme_Gun_Sayisi"].value_counts()
df["Risk"] = (df["Gecikme_Gun_Sayisi"] > 0).astype(int)
df["Risk"].value_counts()

df.drop(["Musteri_Skoru", "Hesap_Aktif"], axis=1, inplace = True)

plt.figure(figsize = (10, 7))
sns.heatmap(df.corr(numeric_only = True), annot = True)

plt.figure(figsize = (10, 6))
sns.countplot(data = df, x = "Egitim_Durumu", hue = "Risk", palette = "Set2")
plt.title("Eğitim Durumuna Göre Müşteri Dağılımı ve Risk Durumu")
plt.xlabel("Eğitim Durumu")
plt.ylabel("Müşteri Sayısı")
#plt.show()

plt.figure(figsize = (10, 6))
sns.boxplot(data = df, x = "Risk", y = "Limit_Kullanim_Orani")
plt.title("Risk Durumuna Göre Limit Kullanım Oranı")
plt.xlabel("0: Risksiz | 1: Riskli")
plt.ylabel("Limit Kullanım Oranı")
#plt.show()

plt.figure(figsize = (10, 6))
sns.kdeplot(data = df, x = "Yas", hue = "Risk", fill = True, common_norm = False, palette = "Set2")
plt.title("Risk Durumuna Göre Yaş Yoğunluğu")
plt.xlabel("Yaş")
plt.ylabel("Yoğunluk")
#plt.show()

plt.figure(figsize = (10, 6))
sns.scatterplot(
    data = df, x = "Yas", y = "Aylik_Odeme_Yuzdesi",
    hue = "Risk", palette = "Set1", alpha = 0.6
)
plt.title("Yaş vs Aylık Ödeme Yüzdesi (Risk Dağılımı)")
plt.xlabel("Yaş")
plt.ylabel("Aylık Ödeme Yüzdesi")
#plt.show()

df.drop("Gecikme_Gun_Sayisi", axis = 1, inplace = True)

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate

X = df.drop("Risk", axis = 1)
y = df["Risk"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42, stratify = y)

education      = ["Egitim_Durumu"]
education_rank = [["Lise", "Lisans", "Lisansustu"]]
categoric_cols = ["Cinsiyet", "Sehir_Tipi", "Meslek", "Gelir_Tipi", "Kart_Tipi"]
city           = ["Sehir"]
numeric_cols   = [col for col in X.columns if col not in education + categoric_cols + city]

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
import category_encoders as ce

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("ordinal", OrdinalEncoder(categories=education_rank), education),
        ("onehot", OneHotEncoder(drop="first", sparse_output=False), categoric_cols),
        ("target", ce.TargetEncoder(), city),
    ]
)

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

master_pipeline = ImbPipeline([
    ("preprocessor", preprocessor),
    ("smote", SMOTE(random_state=42)),
    ("classifier", XGBClassifier(random_state=42, eval_metric="logloss")),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = cross_validate(
    master_pipeline,
    X_train, y_train,
    cv=cv,
    scoring=["f1", "precision", "recall", "roc_auc"],
    return_train_score=True,
    n_jobs=-1,
)

print("\n" + "="*60)
print("CROSS-VALIDATION SONUÇLARI")
print("="*60)
print(f"\n  {'Metrik':<14} {'Ort':>7}  {'Std':>7}  {'Min':>7}  {'Max':>7}")
print(f"  {'-'*50}")

for label, key in [
    ("F1 Score",  "test_f1"),
    ("Precision", "test_precision"),
    ("Recall",    "test_recall"),
    ("ROC-AUC",   "test_roc_auc"),
]:
    s = cv_results[key]
    print(f"  {label:<14} {s.mean():>7.4f}  {s.std():>7.4f}  "
          f"{s.min():>7.4f}  {s.max():>7.4f}")

print(f"\n  Fold bazında F1 skorları:")
for i, score in enumerate(cv_results["test_f1"], 1):
    bar = "|" * int(score * 30)
    print(f"    Fold {i}: {score:.4f}  {bar}")

print(f"\n  Overfit Kontrolü:")
print(f"  {'Metrik':<14} {'Train Ort':>10}  {'Val Ort':>8}  {'Fark':>6}  {'Durum':>10}")
print(f"  {'-'*55}")
for label, train_key, test_key in [
    ("F1 Score",  "train_f1",       "test_f1"),
    ("ROC-AUC",   "train_roc_auc",  "test_roc_auc"),
]:
    train_mean = cv_results[train_key].mean()
    test_mean  = cv_results[test_key].mean()
    diff       = train_mean - test_mean
    durum      = "Overfit" if diff > 0.05 else "Normal"
    print(f"  {label:<14} {train_mean:>10.4f} {test_mean:>8.4f}  "
          f"{diff:>6.4f}  {durum:>10}")

print("="*60)

from sklearn.model_selection import RandomizedSearchCV

param_grid = {
    "classifier__n_estimators":[100, 200, 300],
    "classifier__learning_rate":[0.01, 0.05, 0.1, 0.2],
    "classifier__max_depth":[3, 5, 7, 9],
    "classifier__subsample":[0.7, 0.8, 1.0],
    "classifier__colsample_bytree":[0.7, 0.8, 1.0],
}

random_search = RandomizedSearchCV(
    estimator=master_pipeline,
    param_distributions=param_grid,
    n_iter=10,
    scoring="f1",
    cv=3,
    verbose=2,
    random_state=42,
    n_jobs=-1,
)

random_search.fit(X_train, y_train)
print("\nEn iyi parametreler:", random_search.best_params_)

best_model     = random_search.best_estimator_
y_pred_tuned   = best_model.predict(X_test)

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
print(classification_report(y_test, y_pred_tuned))
print("Accuracy:", accuracy_score(y_test, y_pred_tuned))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred_tuned))

import joblib
joblib.dump(best_model, "bank_risk_pipeline.pkl")
print("\nModel kaydedildi: bank_risk_pipeline.pkl")