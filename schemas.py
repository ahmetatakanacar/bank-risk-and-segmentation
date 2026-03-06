from pydantic import BaseModel, Field
from typing import Literal

class MusteriVerisi(BaseModel):
    Yas: int = Field(..., ge=18, le=100, description="Müşteri yaşı")
    Cinsiyet: Literal["E", "K"] = Field(..., description="E: Erkek, K: Kadın")
    Sehir: str = Field(..., description="Müşterinin yaşadığı şehir")
    Sehir_Tipi: str = Field(..., description="Şehrin ekonomik tipi")
    Ekonomik_Bolge_Seviyesi: float = Field(..., ge=0.0, le=1.0)
    Meslek: str
    Gelir_Tipi: str
    Egitim_Durumu: Literal["Lise", "Lisans", "Lisansustu"]
    Kart_Tipi: str
    Kredi_Karti_Limiti_TL: float = Field(..., gt=0)
    Toplam_Borc_TL: float = Field(..., ge=0)
    Limit_Kullanim_Orani: float = Field(..., ge=0.0, le=100.0)
    Son_Ay_Odenen_TL: float = Field(..., ge=0)
    Aylik_Odeme_Yuzdesi: float = Field(..., ge=0.0, le=100.0)
    Asgari_Odeme_Zorunlulugu: float = Field(..., ge=0, description="Aylık asgari ödeme zorunluluğu (TL)")