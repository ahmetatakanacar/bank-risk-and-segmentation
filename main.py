from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
from schemas import MusteriVerisi

app = FastAPI(
    title="Banka Risk Analizi API",
    description="XGBoost tabanlı kredi risk tahmin servisi — predict_proba + feature importance destekli.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load("bank_risk_pipeline.pkl")
    print("✅ Model başarıyla yüklendi!")
except Exception as e:
    model = None
    print(f"❌ Model yüklenemedi: {e}")

try:
    fi_df = pd.read_csv("feature_importance.csv")
    print("✅ Feature importance yüklendi!")
except Exception:
    fi_df = None

@app.get("/")
def ana_sayfa():
    return {
        "mesaj": "Banka Risk Analizi API v2.0 — Aktif",
        "endpoints": {
            "POST /tahmin-et": "Risk tahmini (0/1 + olasılık skoru)",
            "GET  /feature-importance": "Modelin özellik önem sıralaması",
            "GET  /model-info": "Model bilgileri",
        }
    }

@app.post("/tahmin-et")
def risk_tahmini_yap(musteri: MusteriVerisi):
    if model is None:
        raise HTTPException(status_code=503, detail="Model yüklü değil.")

    try:
        df = pd.DataFrame([musteri.model_dump()])

        tahmin         = model.predict(df)
        risk_kodu      = int(tahmin[0])
        aciklama       = "Riskli Müşteri! Gecikme ihtimali yüksek." if risk_kodu == 1 else "Risksiz Müşteri. Kredi onaylanabilir."

        return {
            "durum":       "Başarılı",
            "tahmin_kodu": risk_kodu,
            "karar":       aciklama,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tahmin hatası: {str(e)}")

@app.get("/feature-importance")
def ozellik_onemleri(top_n: int = Query(default=15, ge=1, le=50)):
    """
    Modelin hangi özelliklere ne kadar ağırlık verdiğini döndürür.
    """
    if fi_df is None:
        if model is None:
            raise HTTPException(status_code=503, detail="Model ve feature importance dosyası bulunamadı.")
        try:
            importances = model.named_steps["classifier"].feature_importances_
            return {"mesaj": "feature_importance.csv bulunamadı, canlı hesaplandı",
                    "importances": importances[:top_n].tolist()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    top = fi_df.head(top_n)
    return {
        "top_n": top_n,
        "ozellikler": [
            {"sira": i+1, "ozellik": row["feature"], "onem": round(row["importance"], 6)}
            for i, row in top.iterrows()
        ]
    }

@app.get("/model-info")
def model_bilgileri():
    """
    Modelin pipeline yapısını ve parametrelerini döndürür.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model yüklü değil.")
    try:
        params = model.named_steps["classifier"].get_params()
        return {
            "model_tipi":    "XGBoost + SMOTE Pipeline",
            "adimlar":       list(model.named_steps.keys()),
            "xgb_params": {
                "n_estimators":     params.get("n_estimators"),
                "learning_rate":    params.get("learning_rate"),
                "max_depth":        params.get("max_depth"),
                "subsample":        params.get("subsample"),
                "colsample_bytree": params.get("colsample_bytree"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))