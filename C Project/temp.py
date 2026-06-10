"""
================================================================================
DESIGN AND SIMULATION OF AN AI-BASED FERMENTATION MONITORING SYSTEM 
FOR BEER FERMENTATION
Professional Industrial-Grade Brewery Monitoring Platform
Version: 7.9.0 - Enterprise Edition (ALL PAGES RESTORED)

MODIFICATIONS:
1. RESTORED ALL navigation pages (Virtual Sensors, Live Monitoring, Fermentation Analytics, 
   Alert Center, Quality Control, Batch Reports, Historical Archive, System Settings)
2. All pages fully functional
3. Yeast activity follows real fermentation kinetics
4. Empty box removed between beer card and AI alerts

Author: SKOL Brewery Advanced Automation
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import json
from io import BytesIO
import time
import warnings
warnings.filterwarnings('ignore')

# Machine Learning Libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler

# =================================================================================
# 1. PAGE CONFIGURATION
# =================================================================================
st.set_page_config(
    page_title="AI-Based Fermentation Monitoring System for Beer Fermentation",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================================================================================
# 2. BEER FERMENTATION PROFILES
# =================================================================================

BEER_FERMENTATION_PROFILES = {
    "Virunga Silver": {
        "name": "Virunga Silver",
        "brand": "Virunga",
        "type": "Premium Lager",
        "grain_type": "Wheat",
        "color": "#f59e0b",
        "default_grain_amount_kg": 4200,
        "grain_amount_min": 2200,
        "grain_amount_max": 6500,
        "fermentation_days": 10,
        "requires_sugar": True,
        "requires_yeast_nutrients": True,
        "profile": {
            "temperature": {"min": 8.0, "max": 12.0, "optimal": 10.0, "critical_high": 13.0, "critical_low": 7.0},
            "ph": {"min": 4.1, "max": 4.6, "optimal": 4.4, "critical_high": 4.8, "critical_low": 3.9},
            "sugar": {"min": 0.0, "max": 13.0, "optimal_start": 12.5, "optimal_end": 2.5},
            "yeast_activity": {"min": 0, "max": 98, "optimal_peak": 88, "optimal_range": [75, 92]},
            "pressure": {"min": 0.5, "max": 2.0, "optimal": 1.1},
            "co2": {"min": 2.2, "max": 3.2, "optimal": 2.7},
            "abv_target": 4.5, "abv_range": {"min": 4.3, "max": 4.7},
            "density_target": 1.006, "gravity_og": 1.038, "gravity_fg": 1.006,
            "quality_threshold": 87,
            "yeast_strain": "Saccharomyces pastorianus"
        },
        "warnings": {
            "temp_high": {
                "message": "🌡️ ALERT: Temperature at {value}°C EXCEEDS Virunga Silver maximum of 12°C!",
                "risk": "High risk of off-flavors (esters) and fusel alcohols",
                "action": "⚠️ IMMEDIATE ACTION: Increase cooling rate by 50%. Target: 10°C"
            },
            "temp_low": {
                "message": "🌡️ ALERT: Temperature at {value}°C BELOW Virunga Silver minimum of 8°C!",
                "risk": "Yeast dormancy risk - fermentation may stop completely",
                "action": "⚠️ IMMEDIATE ACTION: Reduce cooling or add heat. Target: 10°C"
            },
            "yeast_low_growth": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected growth curve!",
                "risk": "Slow fermentation start - extended lag phase",
                "action": "Add yeast nutrients and oxygenate. Check viability"
            },
            "yeast_low_peak": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected peak activity!",
                "risk": "Incomplete fermentation - potential stuck fermentation",
                "action": "Add yeast energizer and monitor gravity closely"
            },
            "yeast_low_decline": {
                "message": "🌀 Yeast activity at {value}% is declining FASTER than expected!",
                "risk": "Premature yeast flocculation - incomplete attenuation",
                "action": "Consider yeast nutrient addition. Monitor sugar levels"
            },
            "ph_high": {
                "message": "🔬 pH at {value} exceeds Virunga Silver maximum of 4.6!",
                "risk": "Potential bacterial contamination",
                "action": "Add food-grade lactic acid to lower pH to 4.4"
            },
            "ph_low": {
                "message": "🔬 pH at {value} below Virunga Silver minimum of 4.1!",
                "risk": "Excessive acidity - stuck fermentation risk",
                "action": "Add calcium carbonate to raise pH to 4.4"
            },
            "sugar_high": {
                "message": "🍬 Sugar at {value}°Bx higher than expected for Virunga Silver!",
                "risk": "Stuck fermentation - yeast unable to consume sugar",
                "action": "Add yeast nutrients and check viability"
            },
            "abv_low": {
                "message": "🍺 ABV at {value}% below target for Virunga Silver (4.5%)!",
                "risk": "Low alcohol content - incomplete fermentation",
                "action": "Check yeast health. Consider extending fermentation"
            }
        }
    },
    "Skol Malt": {
        "name": "Skol Malt",
        "brand": "Skol",
        "type": "Malt Beer",
        "grain_type": "Wheat",
        "color": "#34d399",
        "default_grain_amount_kg": 4500,
        "grain_amount_min": 2500,
        "grain_amount_max": 7000,
        "fermentation_days": 12,
        "requires_sugar": True,
        "requires_yeast_nutrients": True,
        "profile": {
            "temperature": {"min": 12.0, "max": 16.0, "optimal": 14.0, "critical_high": 17.5, "critical_low": 10.5},
            "ph": {"min": 3.8, "max": 4.3, "optimal": 4.0, "critical_high": 4.5, "critical_low": 3.6},
            "sugar": {"min": 0.0, "max": 17.0, "optimal_start": 16.5, "optimal_end": 3.0},
            "yeast_activity": {"min": 0, "max": 95, "optimal_peak": 85, "optimal_range": [70, 90]},
            "pressure": {"min": 0.5, "max": 2.2, "optimal": 1.2},
            "co2": {"min": 2.1, "max": 3.1, "optimal": 2.6},
            "abv_target": 6.5, "abv_range": {"min": 6.3, "max": 6.7},
            "density_target": 1.010, "gravity_og": 1.056, "gravity_fg": 1.010,
            "quality_threshold": 85,
            "yeast_strain": "Saccharomyces cerevisiae"
        },
        "warnings": {
            "temp_high": {
                "message": "🌡️ ALERT: Temperature at {value}°C EXCEEDS Skol Malt maximum of 16°C!",
                "risk": "Fusel alcohol production - harsh flavors",
                "action": "⚠️ IMMEDIATE ACTION: Activate emergency cooling. Target: 14°C"
            },
            "temp_low": {
                "message": "🌡️ ALERT: Temperature at {value}°C BELOW Skol Malt minimum of 12°C!",
                "risk": "Slow fermentation - extended lag phase",
                "action": "⚠️ IMMEDIATE ACTION: Increase temperature to 14°C"
            },
            "yeast_low_growth": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected growth curve!",
                "risk": "Poor yeast propagation - slow start",
                "action": "Oxygenate and add yeast nutrients"
            },
            "yeast_low_peak": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected peak!",
                "risk": "Insufficient yeast for complete fermentation",
                "action": "Add yeast energizer and monitor closely"
            },
            "yeast_low_decline": {
                "message": "🌀 Yeast activity at {value}% is declining TOO FAST!",
                "risk": "Premature flocculation - high residual sugar",
                "action": "Add yeast nutrients to maintain activity"
            },
            "ph_high": {
                "message": "🔬 pH at {value} exceeds Skol Malt maximum of 4.3!",
                "risk": "Diacetyl production risk",
                "action": "Add phosphoric acid to reduce pH to 4.0"
            },
            "ph_low": {
                "message": "🔬 pH at {value} below Skol Malt minimum of 3.8!",
                "risk": "Excessive tartness - yeast stress",
                "action": "Add calcium carbonate. Target pH: 4.0"
            },
            "sugar_high": {
                "message": "🍬 Sugar at {value}°Bx higher than expected for Skol Malt!",
                "risk": "Incomplete fermentation - yeast overwhelmed",
                "action": "Add yeast nutrients and extend fermentation"
            },
            "abv_low": {
                "message": "🍺 ABV at {value}% below target for Skol Malt (6.5%)!",
                "risk": "Low alcohol - not meeting specifications",
                "action": "Check yeast viability. Consider adding simple sugars"
            }
        }
    },
    "Skol Lager": {
        "name": "Skol Lager",
        "brand": "Skol",
        "type": "Lager",
        "grain_type": "Rice",
        "color": "#38bdf8",
        "default_grain_amount_kg": 5000,
        "grain_amount_min": 3000,
        "grain_amount_max": 8000,
        "fermentation_days": 14,
        "requires_sugar": False,
        "requires_yeast_nutrients": False,
        "profile": {
            "temperature": {"min": 10.0, "max": 14.0, "optimal": 12.0, "critical_high": 15.0, "critical_low": 9.0},
            "ph": {"min": 4.0, "max": 4.5, "optimal": 4.2, "critical_high": 4.7, "critical_low": 3.8},
            "sugar": {"min": 0.0, "max": 15.0, "optimal_start": 14.0, "optimal_end": 2.0},
            "yeast_activity": {"min": 0, "max": 95, "optimal_peak": 85, "optimal_range": [70, 90]},
            "pressure": {"min": 0.5, "max": 2.2, "optimal": 1.2},
            "co2": {"min": 2.0, "max": 3.0, "optimal": 2.5},
            "abv_target": 5.0, "abv_range": {"min": 4.8, "max": 5.2},
            "density_target": 1.008, "gravity_og": 1.044, "gravity_fg": 1.008,
            "quality_threshold": 85,
            "yeast_strain": "Saccharomyces pastorianus"
        },
        "warnings": {
            "temp_high": {
                "message": "🌡️ ALERT: Temperature at {value}°C EXCEEDS Skol Lager maximum of 14°C!",
                "risk": "Ester production - fruity off-flavors",
                "action": "⚠️ IMMEDIATE ACTION: Increase cooling. Target: 12°C"
            },
            "temp_low": {
                "message": "🌡️ ALERT: Temperature at {value}°C BELOW Skol Lager minimum of 10°C!",
                "risk": "Extended lag phase - slow start",
                "action": "⚠️ IMMEDIATE ACTION: Reduce cooling. Allow warming to 12°C"
            },
            "yeast_low_growth": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected growth!",
                "risk": "Slow propagation - extended lag",
                "action": "Monitor closely. Consider nutrient addition"
            },
            "yeast_low_peak": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected peak!",
                "risk": "Insufficient yeast activity",
                "action": "Check viability. Add yeast nutrients if needed"
            },
            "yeast_low_decline": {
                "message": "🌀 Yeast activity at {value}% is declining TOO FAST!",
                "risk": "Early flocculation - incomplete fermentation",
                "action": "Monitor gravity. Consider yeast nutrient"
            },
            "ph_high": {
                "message": "🔬 pH at {value} exceeds Skol Lager maximum of 4.5!",
                "risk": "Contamination susceptibility",
                "action": "Add lactic acid to adjust pH to 4.2"
            },
            "ph_low": {
                "message": "🔬 pH at {value} below Skol Lager minimum of 4.0!",
                "risk": "Harsh acidity - yeast stress",
                "action": "Add calcium carbonate. Target: 4.2"
            },
            "sugar_high": {
                "message": "🍬 No sugar addition required - Skol Lager uses malt sugars!",
                "risk": "Monitor maltose conversion only",
                "action": "No action needed - sugars come from malt"
            },
            "abv_low": {
                "message": "🍺 ABV at {value}% below target for Skol Lager (5.0%)!",
                "risk": "Not meeting brand specification",
                "action": "Monitor gravity. Consider extending fermentation"
            }
        }
    },
    "Skol Gatanu": {
        "name": "Skol Gatanu",
        "brand": "Skol",
        "type": "Lager",
        "grain_type": "Rice",
        "color": "#38bdf8",
        "default_grain_amount_kg": 5200,
        "grain_amount_min": 3200,
        "grain_amount_max": 8200,
        "fermentation_days": 14,
        "requires_sugar": False,
        "requires_yeast_nutrients": False,
        "profile": {
            "temperature": {"min": 10.0, "max": 14.0, "optimal": 12.0, "critical_high": 15.0, "critical_low": 9.0},
            "ph": {"min": 4.0, "max": 4.5, "optimal": 4.2, "critical_high": 4.7, "critical_low": 3.8},
            "sugar": {"min": 0.0, "max": 15.0, "optimal_start": 14.0, "optimal_end": 2.0},
            "yeast_activity": {"min": 0, "max": 95, "optimal_peak": 85, "optimal_range": [70, 90]},
            "pressure": {"min": 0.5, "max": 2.2, "optimal": 1.2},
            "co2": {"min": 2.0, "max": 3.0, "optimal": 2.5},
            "abv_target": 5.0, "abv_range": {"min": 4.8, "max": 5.2},
            "density_target": 1.008, "gravity_og": 1.044, "gravity_fg": 1.008,
            "quality_threshold": 85,
            "yeast_strain": "Saccharomyces pastorianus"
        },
        "warnings": {
            "temp_high": {
                "message": "🌡️ ALERT: Temperature at {value}°C EXCEEDS Skol Gatanu maximum of 14°C!",
                "risk": "Off-flavor development",
                "action": "⚠️ IMMEDIATE ACTION: Adjust cooling. Target: 12°C"
            },
            "temp_low": {
                "message": "🌡️ ALERT: Temperature at {value}°C BELOW Skol Gatanu minimum of 10°C!",
                "risk": "Slow fermentation - extended time",
                "action": "⚠️ IMMEDIATE ACTION: Increase temperature to 12°C"
            },
            "yeast_low_growth": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected growth!",
                "risk": "Insufficient yeast propagation",
                "action": "Monitor viability. Consider nutrient addition"
            },
            "yeast_low_peak": {
                "message": "🌀 Yeast activity at {value}% is BELOW expected peak!",
                "risk": "Incomplete attenuation risk",
                "action": "Add yeast nutrients and monitor gravity"
            },
            "yeast_low_decline": {
                "message": "🌀 Yeast activity at {value}% is declining TOO FAST!",
                "risk": "Premature settling - high residual sugar",
                "action": "Rouse yeast. Consider nutrient addition"
            },
            "ph_high": {
                "message": "🔬 pH at {value} exceeds Skol Gatanu maximum of 4.5!",
                "risk": "Elevated pH - monitor for contamination",
                "action": "Add acid to correct pH to 4.2"
            },
            "ph_low": {
                "message": "🔬 pH at {value} below Skol Gatanu minimum of 4.0!",
                "risk": "Depressed pH - acid shock to yeast",
                "action": "Add base to normalize pH to 4.2"
            },
            "sugar_high": {
                "message": "🍬 No sugar addition required - Skol Gatanu uses malt sugars!",
                "risk": "Monitor maltose conversion only",
                "action": "No action needed"
            },
            "abv_low": {
                "message": "🍺 ABV at {value}% below target for Skol Gatanu (5.0%)!",
                "risk": "Below specification - quality issue",
                "action": "Check fermentation efficiency"
            }
        }
    }
}

# =================================================================================
# 3. WATER QUALITY STANDARDS
# =================================================================================
WATER_QUALITY_STANDARDS = {
    "max_turbidity": 0.30,
    "optimal_turbidity": 0.10,
    "warning_turbidity": 0.25,
}

# =================================================================================
# 4. DYNAMIC SETTINGS MANAGEMENT
# =================================================================================
DEFAULT_SETTINGS = {
    "fermentation_limits": {
        "temperature": {"min": 8.0, "max": 25.0, "warning_tolerance": 1.5, "critical_tolerance": 2.5},
        "ph": {"min": 3.5, "max": 5.0, "warning_tolerance": 0.2, "critical_tolerance": 0.4},
        "sugar": {"min": 0.0, "max": 20.0, "warning_tolerance": 1.0, "critical_tolerance": 2.0},
        "yeast_activity": {"min": 0, "max": 100, "warning_tolerance": 10, "critical_tolerance": 20},
        "pressure": {"min": 0.3, "max": 2.8, "warning_tolerance": 0.3, "critical_tolerance": 0.5},
        "co2": {"min": 1.5, "max": 3.5, "warning_tolerance": 0.3, "critical_tolerance": 0.5},
        "alcohol": {"min": 0.0, "max": 8.0, "warning_tolerance": 0.3, "critical_tolerance": 0.5}
    },
    "water_quality_limits": {"turbidity": {"min": 0.0, "max": 0.5, "warning_tolerance": 0.05, "critical_tolerance": 0.1}},
    "prediction_limits": {
        "quality_thresholds": {"excellent": 90, "good": 80, "warning": 70, "critical": 60},
        "risk_thresholds": {"low": 25, "medium": 50, "high": 75},
        "confidence_threshold": 70
    },
    "alert_config": {"enable_alerts": True, "auto_correct": False, "notification_frequency": 60, "log_retention_days": 30}
}

# =================================================================================
# 5. ML ENGINE
# =================================================================================
class QualityPredictionEngine:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.is_trained = False
        self.model_metrics = {}
        
    def generate_training_data(self, n_samples=2000):
        np.random.seed(42)
        temperature = np.random.normal(12, 2, n_samples)
        temperature = np.clip(temperature, 8, 24)
        ph = np.random.normal(4.2, 0.2, n_samples)
        ph = np.clip(ph, 3.8, 4.8)
        sugar = np.random.uniform(0, 18, n_samples)
        yeast = np.random.uniform(0, 98, n_samples)
        co2 = np.random.uniform(1.8, 3.2, n_samples)
        pressure = np.random.uniform(0.5, 2.5, n_samples)
        duration = np.random.uniform(24, 400, n_samples)
        gravity = np.random.uniform(1.002, 1.060, n_samples)
        
        optimal_temp, optimal_ph, optimal_yeast = 12, 4.2, 85
        temp_quality = 100 - np.abs(temperature - optimal_temp) * 6
        ph_quality = 100 - np.abs(ph - optimal_ph) * 20
        yeast_quality = yeast * 0.85 + 15
        attenuation = ((18 - sugar) / 18) * 100
        interaction = (temperature - optimal_temp) * (ph - optimal_ph) * 40
        quality = (temp_quality * 0.3 + ph_quality * 0.2 + yeast_quality * 0.25 + 
                   attenuation * 0.25 - np.abs(interaction) * 0.05)
        quality = np.clip(quality, 45, 100)
        
        return pd.DataFrame({
            'temperature': temperature, 'ph': ph, 'sugar': sugar,
            'yeast_activity': yeast, 'co2': co2, 'pressure': pressure,
            'fermentation_duration': duration, 'specific_gravity': gravity,
            'quality_score': quality
        })
    
    def train_model(self):
        with st.spinner("🤖 Training Advanced AI Model..."):
            data = self.generate_training_data()
            features = ['temperature', 'ph', 'sugar', 'yeast_activity', 'co2', 'pressure', 
                       'fermentation_duration', 'specific_gravity']
            X, y = data[features], data['quality_score']
            X_scaled = self.scaler.fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            self.model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            self.model_metrics = {'r2_score': r2_score(y_test, y_pred), 'rmse': np.sqrt(mean_squared_error(y_test, y_pred)), 'mae': np.mean(np.abs(y_test - y_pred))}
            self.feature_importance = dict(zip(features, self.model.feature_importances_))
            self.is_trained = True
            
    def predict_quality(self, parameters):
        if not self.is_trained:
            self.train_model()
        features = ['temperature', 'ph', 'sugar', 'yeast_activity', 'co2', 'pressure', 
                   'fermentation_duration', 'specific_gravity']
        input_df = pd.DataFrame([{k: parameters.get(k, 0) for k in features}])
        input_scaled = self.scaler.transform(input_df)
        quality_score = self.model.predict(input_scaled)[0]
        predictions = [self.model.predict(input_scaled) for _ in range(20)]
        confidence = min(99, max(75, 100 - (np.std(predictions) * 2.5)))
        
        if quality_score >= 92:
            grade = "Excellent"
        elif quality_score >= 85:
            grade = "Very Good"
        elif quality_score >= 78:
            grade = "Good"
        elif quality_score >= 70:
            grade = "Fair"
        elif quality_score >= 60:
            grade = "Poor"
        else:
            grade = "Critical"
            
        return {'quality_score': round(quality_score, 1), 'grade': grade, 'confidence': round(confidence, 1), 'metrics': self.model_metrics}
    
    def predict_abv(self, sugar_consumed, initial_sugar, yeast_activity):
        base_abv = (sugar_consumed * 0.13) if initial_sugar > 0 else 0
        return round(base_abv * min(1, yeast_activity / 85), 2)
    
    def predict_contamination_risk(self, parameters, turbidity):
        risk_score = 0
        ph = parameters.get('ph', 4.2)
        optimal_ph = parameters.get('optimal_ph', 4.2)
        ph_deviation = abs(ph - optimal_ph)
        
        if ph_deviation > 0.3:
            risk_score += min(35, ph_deviation * 45)
        elif ph_deviation > 0.15:
            risk_score += min(20, ph_deviation * 35)
        
        if turbidity > WATER_QUALITY_STANDARDS["max_turbidity"]:
            risk_score += 25
        elif turbidity > WATER_QUALITY_STANDARDS["warning_turbidity"]:
            risk_score += 10
        
        temp = parameters.get('temperature', 12)
        optimal_temp = parameters.get('optimal_temp', 12)
        temp_deviation = abs(temp - optimal_temp)
        if temp_deviation > 2:
            risk_score += min(20, temp_deviation * 5)
        
        return ("Low" if risk_score < 20 else "Medium" if risk_score < 40 else "High", min(80, risk_score))
    
    def predict_success_probability(self, parameters):
        factors = []
        temp = parameters.get('temperature', 12)
        factors.append(0.97 if abs(temp - parameters.get('optimal_temp', 12)) <= 1.5 else 0.80)
        ph = parameters.get('ph', 4.2)
        factors.append(0.97 if abs(ph - parameters.get('optimal_ph', 4.2)) <= 0.2 else 0.82)
        yeast = parameters.get('yeast_activity', 85)
        factors.append(0.98 if yeast >= 75 else (0.70 if yeast < 60 else 0.90))
        return round(np.prod(factors) * 100, 1)

ml_engine = QualityPredictionEngine()

# =================================================================================
# 6. SMOOTH FERMENTATION KINETICS FUNCTIONS
# =================================================================================

def get_beer_profile(beer_name):
    return BEER_FERMENTATION_PROFILES.get(beer_name, BEER_FERMENTATION_PROFILES["Skol Lager"])

def calculate_expected_sugar_at_day(day, beer_profile):
    initial_sugar = beer_profile['profile']['sugar']['optimal_start']
    final_sugar = beer_profile['profile']['sugar']['optimal_end']
    fermentation_days = beer_profile['fermentation_days']
    
    if day <= 0:
        return initial_sugar
    if day >= fermentation_days:
        return final_sugar
    
    midpoint = fermentation_days * 0.5
    k = 0.6
    fraction_remaining = 1 / (1 + np.exp(k * (day - midpoint)))
    sugar = final_sugar + (initial_sugar - final_sugar) * fraction_remaining
    return max(final_sugar, min(initial_sugar, sugar))

def calculate_expected_abv_at_day(day, beer_profile):
    target_abv = beer_profile['profile']['abv_target']
    fermentation_days = beer_profile['fermentation_days']
    
    if day <= 0:
        return 0.0
    if day >= fermentation_days:
        return target_abv
    
    midpoint = fermentation_days * 0.55
    k = 0.55
    abv = target_abv / (1 + np.exp(-k * (day - midpoint)))
    return max(0.0, min(target_abv, abv))

def calculate_expected_yeast_at_day(day, beer_profile):
    optimal_peak = beer_profile['profile']['yeast_activity']['optimal_peak']
    fermentation_days = beer_profile['fermentation_days']
    
    if day <= 0:
        return 75.0
    
    if day >= fermentation_days:
        return max(25.0, optimal_peak * 0.3)
    
    growth_end = min(3, fermentation_days * 0.25)
    peak_end = min(5, fermentation_days * 0.4)
    
    if day <= growth_end:
        fraction = day / growth_end
        activity = 75 + (optimal_peak - 75) * fraction
    elif day <= peak_end:
        activity = optimal_peak
    else:
        decay_start = peak_end
        decay_constant = 0.2
        activity = optimal_peak * np.exp(-decay_constant * (day - decay_start))
    
    variation = 1 + (random.random() - 0.5) * 0.04
    activity = activity * variation
    
    return max(20.0, min(optimal_peak + 3, activity))

def calculate_expected_temperature_at_day(day, beer_profile):
    optimal_temp = beer_profile['profile']['temperature']['optimal']
    fermentation_days = beer_profile['fermentation_days']
    
    if day <= 0:
        return optimal_temp
    if day >= fermentation_days:
        return optimal_temp - 1.0
    
    phase1_end = fermentation_days * 0.3
    if day <= phase1_end:
        fraction = day / phase1_end
        return optimal_temp + fraction * 0.6
    
    phase2_end = fermentation_days * 0.7
    if day <= phase2_end:
        return optimal_temp + 0.6
    
    fraction = (day - phase2_end) / (fermentation_days - phase2_end)
    return optimal_temp + 0.6 - fraction * 1.6

def calculate_expected_ph_at_day(day, beer_profile):
    optimal_ph = beer_profile['profile']['ph']['optimal']
    min_ph = beer_profile['profile']['ph']['min']
    fermentation_days = beer_profile['fermentation_days']
    
    if day <= 0:
        return optimal_ph
    if day >= fermentation_days:
        return min_ph
    
    fraction = min(1.0, day / fermentation_days)
    ph_decrease = (optimal_ph - min_ph) * (1 - np.exp(-2.5 * fraction))
    return optimal_ph - ph_decrease

def reset_beer_fermentation(beer_name):
    new_profile = get_beer_profile(beer_name)
    
    st.session_state.fermentation_data.update({
        'beer_type': beer_name,
        'grain_type': new_profile['grain_type'],
        'grain_amount_kg': new_profile['default_grain_amount_kg'],
        'temperature': new_profile['profile']['temperature']['optimal'],
        'ph': new_profile['profile']['ph']['optimal'],
        'sugar': new_profile['profile']['sugar']['optimal_start'],
        'specific_gravity': new_profile['profile']['gravity_og'],
        'alcohol': 0.0,
        'progress': 0,
        'stage': "Active Fermentation",
        'start_time': datetime.now(),
        'expected_completion': datetime.now() + timedelta(days=new_profile['fermentation_days']),
        'yeast_deviation': 0,
        'sugar_deviation': 0,
        'temp_deviation': 0,
        'ph_deviation': 0,
        'fermentation_days': new_profile['fermentation_days'],
        'simulation_day': 0,
        'batch_id': f"FER-{datetime.now().strftime('%y%m%d')}-{random.randint(100,999)}",
        'water_turbidity': 0.30
    })
    
    add_alert_to_center(f"🔄 Fermentation reset to Day 1 - New batch: {beer_name} ({new_profile['fermentation_days']}-day profile)", "low", "info")

def sync_parameters_with_day(day_number, beer_profile):
    data = st.session_state.fermentation_data
    fermentation_days = beer_profile['fermentation_days']
    
    expected_sugar = calculate_expected_sugar_at_day(day_number, beer_profile)
    sugar_deviation = data.get('sugar_deviation', 0)
    if beer_profile['requires_sugar']:
        data['sugar'] = max(beer_profile['profile']['sugar']['min'], 
                           min(beer_profile['profile']['sugar']['max'], 
                           expected_sugar + sugar_deviation))
    else:
        data['sugar'] = expected_sugar
    
    if day_number <= 0:
        data['alcohol'] = 0.0
    elif day_number >= fermentation_days:
        data['alcohol'] = beer_profile['profile']['abv_target']
    else:
        data['alcohol'] = calculate_expected_abv_at_day(day_number, beer_profile)
    
    expected_yeast = calculate_expected_yeast_at_day(day_number, beer_profile)
    yeast_deviation = data.get('yeast_deviation', 0)
    data['yeast_activity'] = max(beer_profile['profile']['yeast_activity']['min'], 
                                min(beer_profile['profile']['yeast_activity']['max'], 
                                expected_yeast + yeast_deviation))
    
    expected_temp = calculate_expected_temperature_at_day(day_number, beer_profile)
    temp_deviation = data.get('temp_deviation', 0)
    data['temperature'] = max(beer_profile['profile']['temperature']['min'], 
                             min(beer_profile['profile']['temperature']['max'], 
                             expected_temp + temp_deviation))
    
    expected_ph = calculate_expected_ph_at_day(day_number, beer_profile)
    ph_deviation = data.get('ph_deviation', 0)
    data['ph'] = max(beer_profile['profile']['ph']['min'], 
                    min(beer_profile['profile']['ph']['max'], 
                    expected_ph + ph_deviation))
    
    initial_sugar = beer_profile['profile']['sugar']['optimal_start']
    sugar_consumed = max(0, initial_sugar - data['sugar']) if beer_profile['requires_sugar'] else initial_sugar - data['sugar']
    data['progress'] = min(100.0, (sugar_consumed / initial_sugar) * 100) if initial_sugar > 0 else 0
    
    data['co2'] = 1.0 + (data['yeast_activity'] / 100) * 2.0
    data['pressure'] = 0.5 + (data['co2'] - 1.0) * 0.5
    
    temp_score = max(0, 100 - abs(data['temperature'] - beer_profile['profile']['temperature']['optimal']) * 12)
    ph_score = max(0, 100 - abs(data['ph'] - beer_profile['profile']['ph']['optimal']) * 25)
    attenuation_score = (sugar_consumed / initial_sugar) * 100 if initial_sugar > 0 else 0
    yeast_score = data['yeast_activity'] * 0.9
    
    data['quality_score'] = max(0, min(100, int(
        temp_score * 0.30 + 
        ph_score * 0.25 + 
        attenuation_score * 0.25 + 
        yeast_score * 0.20
    )))
    
    expected_abv = calculate_expected_abv_at_day(day_number, beer_profile)
    abv_ratio = data['alcohol'] / expected_abv if expected_abv > 0 else 1.0
    data['success_probability'] = max(0, min(100, 100 * abv_ratio))
    
    data['health_score'] = int((temp_score * 0.3 + ph_score * 0.3 + data['yeast_activity'] * 0.4))
    data['health_score'] = max(0, min(100, data['health_score']))
    
    params = {
        'ph': data['ph'],
        'optimal_ph': beer_profile['profile']['ph']['optimal'],
        'temperature': data['temperature'],
        'optimal_temp': beer_profile['profile']['temperature']['optimal']
    }
    turbidity = data.get('water_turbidity', 0.30)
    risk_level, risk_score = ml_engine.predict_contamination_risk(params, turbidity)
    data['contamination_risk'] = risk_score
    
    expected_progress = min(100, (day_number / fermentation_days) * 100) if day_number > 0 else data['progress']
    data['process_efficiency'] = min(100, max(0, (data['progress'] / max(1, expected_progress)) * 100))
    
    if data['quality_score'] >= 85 and data['contamination_risk'] < 25:
        data['product_stability'] = "Stable"
    elif data['quality_score'] >= 70 and data['contamination_risk'] < 45:
        data['product_stability'] = "Moderately Stable"
    else:
        data['product_stability'] = "Unstable"
    
    if data['progress'] >= 90:
        data['stage'] = "Maturation"
    elif data['progress'] >= 60:
        data['stage'] = "Conditioning"
    else:
        data['stage'] = "Active Fermentation"
    
    data['last_update'] = datetime.now()
    data['simulation_day'] = day_number
    
    return {
        "day": day_number, "progress": data['progress'], "alcohol": data['alcohol'],
        "sugar": data['sugar'], "temperature": data['temperature'], "ph": data['ph'],
        "yeast": data['yeast_activity'], "quality": data['quality_score'],
        "success": data['success_probability'], "risk": data['contamination_risk']
    }

# =================================================================================
# 7. SESSION STATE INITIALIZATION
# =================================================================================

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    default_beer = "Skol Lager"
    default_profile = get_beer_profile(default_beer)
    
    st.session_state.fermentation_data = {
        'temperature': default_profile['profile']['temperature']['optimal'],
        'ph': default_profile['profile']['ph']['optimal'],
        'sugar': default_profile['profile']['sugar']['optimal_start'],
        'alcohol': 0.0,
        'co2': 0.5,
        'yeast_activity': 85,
        'pressure': 0.8,
        'tank_level': 95,
        'specific_gravity': default_profile['profile']['gravity_og'],
        'turbidity': 0.30,
        'dissolved_oxygen': 8.5,
        'last_update': datetime.now(),
        'batch_id': f"FER-{datetime.now().strftime('%y%m%d')}-{random.randint(100,999)}",
        'beer_type': default_beer,
        'stage': "Active Fermentation",
        'progress': 0,
        'quality_score': 85,
        'ai_confidence': 90,
        'contamination_risk': 12,
        'flavor_score': 85,
        'aroma_score': 82,
        'clarity_score': 90,
        'fermentation_rate': 0.8,
        'product_stability': "Stable",
        'process_efficiency': 85,
        'health_score': 88,
        'consistency_score': 90,
        'grain_type': default_profile['grain_type'],
        'grain_amount_kg': default_profile['default_grain_amount_kg'],
        'water_turbidity': 0.30,
        'start_time': datetime.now(),
        'expected_completion': datetime.now() + timedelta(days=default_profile['fermentation_days']),
        'simulation_day': 0,
        'success_probability': 85,
        'yeast_deviation': 0,
        'sugar_deviation': 0,
        'temp_deviation': 0,
        'ph_deviation': 0,
        'fermentation_days': default_profile['fermentation_days']
    }
    
    now = datetime.now()
    st.session_state.historical_data = []
    for i in range(60):
        st.session_state.historical_data.append({
            'timestamp': now - timedelta(minutes=60-i),
            'temperature': default_profile['profile']['temperature']['optimal'] + random.uniform(-0.2, 0.3),
            'ph': default_profile['profile']['ph']['optimal'] + random.uniform(-0.03, 0.03),
            'sugar': default_profile['profile']['sugar']['optimal_start'] - (i * 0.15),
            'alcohol': i * 0.08,
            'quality': 85 + (i * 0.25),
            'co2': 0.5 + (i * 0.05),
            'yeast': 75 + (i * 0.25),
            'pressure': 0.8 + (i * 0.025),
            'health': 85 + (i * 0.15)
        })
    
    st.session_state.alerts = [
        {"type": "info", "message": "AI Fermentation Intelligence System Online", "time": datetime.now().strftime('%H:%M:%S'), "severity": "low"},
        {"type": "success", "message": f"{default_beer} fermentation profile loaded - Day 1", "time": datetime.now().strftime('%H:%M:%S'), "severity": "low"},
        {"type": "success", "message": f"Expected completion: {(datetime.now() + timedelta(days=default_profile['fermentation_days'])).strftime('%Y-%m-%d')}", "time": datetime.now().strftime('%H:%M:%S'), "severity": "low"}
    ]
    
    st.session_state.batch_history = [
        {"id": "FER-260520-01", "beer": "Skol Lager", "abv": 5.0, "quality": 94, "status": "Completed", 
         "date": "2026-05-20", "efficiency": 92, "grain_type": "Rice", "grain_amount": 5000, "duration_days": 14},
        {"id": "FER-260515-02", "beer": "Skol Malt", "abv": 6.4, "quality": 91, "status": "Completed", 
         "date": "2026-05-15", "efficiency": 89, "grain_type": "Wheat", "grain_amount": 4500, "duration_days": 12},
        {"id": "FER-260510-03", "beer": "Virunga Silver", "abv": 4.5, "quality": 93, "status": "Completed", 
         "date": "2026-05-10", "efficiency": 91, "grain_type": "Wheat", "grain_amount": 4200, "duration_days": 10},
        {"id": "FER-260505-04", "beer": "Skol Gatanu", "abv": 5.1, "quality": 90, "status": "Completed", 
         "date": "2026-05-05", "efficiency": 88, "grain_type": "Rice", "grain_amount": 5200, "duration_days": 14},
    ]
    
    st.session_state.settings = DEFAULT_SETTINGS.copy()
    st.session_state.simulation_mode = False

# =================================================================================
# 8. HELPER FUNCTIONS
# =================================================================================

def add_alert_to_center(message, severity, alert_type="warning"):
    st.session_state.alerts.insert(0, {
        "type": alert_type,
        "message": message,
        "time": datetime.now().strftime('%H:%M:%S'),
        "severity": severity
    })
    if len(st.session_state.alerts) > 50:
        st.session_state.alerts = st.session_state.alerts[:50]

def ai_update_with_inputs(temp, ph, yeast, sugar, grain_amount=None):
    data = st.session_state.fermentation_data
    beer_profile = get_beer_profile(data['beer_type'])
    current_day = data.get('simulation_day', 0)
    
    expected_yeast = calculate_expected_yeast_at_day(current_day, beer_profile)
    expected_sugar = calculate_expected_sugar_at_day(current_day, beer_profile)
    expected_temp = calculate_expected_temperature_at_day(current_day, beer_profile)
    expected_ph = calculate_expected_ph_at_day(current_day, beer_profile)
    
    data['yeast_deviation'] = yeast - expected_yeast
    data['sugar_deviation'] = sugar - expected_sugar if beer_profile['requires_sugar'] else 0
    data['temp_deviation'] = temp - expected_temp
    data['ph_deviation'] = ph - expected_ph
    
    if grain_amount is not None:
        data['grain_amount_kg'] = grain_amount
    
    sync_parameters_with_day(current_day, beer_profile)
    
    st.session_state.historical_data.append({
        'timestamp': datetime.now(), 'temperature': data['temperature'], 'ph': data['ph'],
        'sugar': data['sugar'], 'alcohol': data['alcohol'], 'quality': data['quality_score'],
        'co2': data['co2'], 'yeast': data['yeast_activity'], 'pressure': data['pressure'],
        'health': data['health_score']
    })
    
    if len(st.session_state.historical_data) > 200:
        st.session_state.historical_data = st.session_state.historical_data[-200:]

def generate_report(report_type="batch"):
    data = st.session_state.fermentation_data
    beer_profile = get_beer_profile(data['beer_type'])
    elapsed = (datetime.now() - data['start_time']).total_seconds() / 3600
    remaining_days = max(0, beer_profile['fermentation_days'] - (elapsed / 24))
    
    return {
        "report_type": report_type,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "batch_info": {
            "batch_id": data['batch_id'], "beer_type": data['beer_type'],
            "grain_type": data.get('grain_type', 'Unknown'), "grain_amount_kg": data.get('grain_amount_kg', 0),
            "remaining_days": round(remaining_days, 1), "completion_percentage": data['progress'],
            "fermentation_profile": f"{beer_profile['fermentation_days']} days - {beer_profile['type']}"
        },
        "quality_metrics": {
            "overall_quality_score": data['quality_score'], "health_score": data['health_score'],
            "flavor_score": data.get('flavor_score', 85), "aroma_score": data.get('aroma_score', 82),
            "clarity_score": data.get('clarity_score', 90)
        },
        "water_quality": {
            "turbidity_ntu": data.get('water_turbidity', 0), "max_allowed": WATER_QUALITY_STANDARDS["max_turbidity"],
            "optimal": WATER_QUALITY_STANDARDS["optimal_turbidity"],
            "status": "Optimal" if data.get('water_turbidity', 0) <= WATER_QUALITY_STANDARDS["optimal_turbidity"] else "Acceptable"
        },
        "fermentation_parameters": {
            "temperature": {"current": data['temperature'], "target": beer_profile['profile']['temperature']['optimal']},
            "ph": {"current": data['ph'], "target": beer_profile['profile']['ph']['optimal']},
            "sugar": {"current": data['sugar'], "target": beer_profile['profile']['sugar']['optimal_start']},
            "alcohol": {"current": data['alcohol'], "target": beer_profile['profile']['abv_target']},
            "yeast": {"current": data['yeast_activity'], "target": beer_profile['profile']['yeast_activity']['optimal_peak']},
            "co2": data['co2'], "pressure": data['pressure']
        },
        "risk_assessment": {
            "contamination_risk": data['contamination_risk'], "process_stability": data.get('product_stability', 'Stable'),
            "success_probability": data.get('success_probability', 85)
        },
        "predictions": {
            "expected_final_abv": round(data['alcohol'] + (beer_profile['profile']['abv_target'] - data['alcohol']) * 0.3, 1),
            "expected_yield_l": round(data.get('grain_amount_kg', 5000) * 19.5, 0),
            "quality_trajectory": "Improving" if data['quality_score'] > 80 else "Stable"
        }
    }

def export_to_excel(report):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([report['batch_info']]).to_excel(writer, sheet_name='Batch Info', index=False)
        pd.DataFrame([report['quality_metrics']]).to_excel(writer, sheet_name='Quality Metrics', index=False)
        pd.DataFrame([report['water_quality']]).to_excel(writer, sheet_name='Water Quality', index=False)
        pd.DataFrame([report['fermentation_parameters']]).to_excel(writer, sheet_name='Parameters', index=False)
        pd.DataFrame([report['risk_assessment']]).to_excel(writer, sheet_name='Risk Assessment', index=False)
        pd.DataFrame([report['predictions']]).to_excel(writer, sheet_name='Predictions', index=False)
    return output.getvalue()

# =================================================================================
# 9. PROFESSIONAL CSS
# =================================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f141e 0%, #0a0e16 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid #1f2937;
    }
    
    .dashboard-card {
        background: rgba(17, 24, 39, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid #374151;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    
    .beer-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 12px 16px;
        text-align: center;
        border: 1px solid #3b82f6;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .beer-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px -5px rgba(59, 130, 246, 0.3);
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #3b82f6;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.2);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    
    .status-excellent { background: linear-gradient(135deg, #059669, #10b981); color: white; }
    .status-verygood { background: linear-gradient(135deg, #3b82f6, #60a5fa); color: white; }
    .status-good { background: linear-gradient(135deg, #8b5cf6, #a78bfa); color: white; }
    .status-warning { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }
    .status-critical { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; }
    
    .alert-critical {
        background: linear-gradient(135deg, #7f1a1a 0%, #991b1b 100%);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        animation: pulse 1.5s infinite;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .ai-alert-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 2px solid #8b5cf6;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.2);
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981, #34d399);
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0f172a;
        border-radius: 16px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 24px;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
    }
    
    h1, h2, h3, h4, h5 {
        background: linear-gradient(135deg, #f1f5f9, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.6rem; margin-top: 1rem; margin-bottom: 0.75rem; }
    h3 { font-size: 1.3rem; margin-bottom: 0.5rem; }
    
    [data-testid="stMetric"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 16px;
    }
    
    [data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-weight: 500;
    }
    
    [data-testid="stMetric"] .stMetricValue {
        color: #e2e8f0 !important;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; box-shadow: 0 0 15px #ef4444; }
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #3b82f6;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #3b82f6, #4f46e5);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4);
    }
    
    .risk-meter {
        background: #0f172a;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #1f2937;
    }
    
    .quality-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border-radius: 16px;
        padding: 16px;
        margin: 8px;
        text-align: center;
    }
    
    [data-testid="stInfo"] {
        background: #1e3a5f;
        color: #93c5fd;
        border-radius: 12px;
    }
    [data-testid="stSuccess"] {
        background: #064e3b;
        color: #34d399;
        border-radius: 12px;
    }
    [data-testid="stWarning"] {
        background: #78350f;
        color: #fcd34d;
        border-radius: 12px;
    }
    [data-testid="stError"] {
        background: #7f1a1a;
        color: #fca5a5;
        border-radius: 12px;
    }
    
    .report-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }
    
    .trend-chart {
        background: #1e293b;
        border-radius: 16px;
        padding: 16px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =================================================================================
# 10. SIDEBAR NAVIGATION - ALL PAGES INCLUDED
# =================================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 48px;">🍺</div>
        <h3 style="color: #e2e8f0; margin: 0;">Fermentation Monitor</h3>
        <p style="color: #f59e0b; font-size: 0.85rem;">AI-Powered System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    nav_page = st.radio("NAVIGATION", [
        "🏭 Main Dashboard", 
        "🎛️ Virtual Sensors", 
        "📊 Live Monitoring", 
        "📈 Fermentation Analytics", 
        "🚨 Alert Center", 
        "🛡️ Quality Control", 
        "📋 Batch Reports", 
        "📚 Historical Archive", 
        "⚙️ System Settings"
    ], index=0)
    
    st.markdown("---")
    
    st.subheader("🍺 Beer Selection")
    beer_options = ["Virunga Silver", "Skol Malt", "Skol Lager", "Skol Gatanu"]
    selected_beer = st.selectbox("Select Beer Type", beer_options, 
                                   index=beer_options.index(st.session_state.fermentation_data.get('beer_type', "Skol Lager")))
    
    if selected_beer != st.session_state.fermentation_data.get('beer_type'):
        reset_beer_fermentation(selected_beer)
        st.rerun()
    
    current_profile = get_beer_profile(selected_beer)
    
    st.info(f"""
    🍺 **{selected_beer}**  
    Type: {current_profile['type']}  
    Temp Range: {current_profile['profile']['temperature']['min']}°C - {current_profile['profile']['temperature']['max']}°C
    Duration: {current_profile['fermentation_days']} days  
    Target ABV: {current_profile['profile']['abv_target']}%
    """)
    
    grain_min, grain_max = current_profile['grain_amount_min'], current_profile['grain_amount_max']
    current_grain = st.session_state.fermentation_data.get('grain_amount_kg', current_profile['default_grain_amount_kg'])
    new_grain = st.slider(f"🌾 {current_profile['grain_type']} Amount (kg)", 
                          min_value=grain_min, max_value=grain_max, 
                          value=current_grain, step=100)
    if new_grain != current_grain:
        st.session_state.fermentation_data['grain_amount_kg'] = new_grain
        st.rerun()
    
    elapsed = (datetime.now() - st.session_state.fermentation_data['start_time']).total_seconds() / 3600
    total_days = current_profile['fermentation_days']
    progress_pct = min(1.0, elapsed / (total_days * 24))
    st.progress(progress_pct)
    st.caption(f"Day {min(total_days, int(elapsed/24)+1)} of {total_days}")
    
    st.markdown("---")
    
    st.subheader("🎛️ Process Controls")
    limits = st.session_state.settings['fermentation_limits']
    
    t = st.slider("Temperature (°C)", 
                  min_value=float(limits['temperature']['min']), 
                  max_value=float(limits['temperature']['max']), 
                  value=float(st.session_state.fermentation_data['temperature']), 
                  step=0.1)
    
    p = st.slider("pH", 
                  min_value=float(limits['ph']['min']), 
                  max_value=float(limits['ph']['max']), 
                  value=float(st.session_state.fermentation_data['ph']), 
                  step=0.05)
    
    y = st.slider("Yeast Activity (%)", 
                  min_value=int(limits['yeast_activity']['min']), 
                  max_value=int(limits['yeast_activity']['max']), 
                  value=int(st.session_state.fermentation_data['yeast_activity']), 
                  step=1)
    
    if current_profile['requires_sugar']:
        s = st.slider("Sugar Content (°Bx)", 
                      min_value=float(limits['sugar']['min']), 
                      max_value=float(limits['sugar']['max']), 
                      value=float(st.session_state.fermentation_data['sugar']), 
                      step=0.1)
    else:
        s = st.session_state.fermentation_data['sugar']
        st.info("ℹ️ This beer type does not require sugar addition")
    
    if st.button("⚡ Apply Parameters", use_container_width=True, type="primary"):
        with st.spinner("Updating fermentation parameters..."):
            old_temp = st.session_state.fermentation_data['temperature']
            old_ph = st.session_state.fermentation_data['ph']
            old_yeast = st.session_state.fermentation_data['yeast_activity']
            
            ai_update_with_inputs(t, p, y, s, new_grain)
            
            if t > current_profile['profile']['temperature']['max']:
                add_alert_to_center(f"⚠️ Temperature set to {t}°C which exceeds {selected_beer} maximum!", "critical", "error")
            elif t < current_profile['profile']['temperature']['min']:
                add_alert_to_center(f"⚠️ Temperature set to {t}°C which is below {selected_beer} minimum!", "warning", "warning")
            
            if abs(t - old_temp) > 1.5:
                add_alert_to_center(f"Temperature changed from {old_temp:.1f}°C to {t:.1f}°C", "low", "info")
            if abs(p - old_ph) > 0.2:
                add_alert_to_center(f"pH changed from {old_ph:.2f} to {p:.2f}", "low", "info")
            if abs(y - old_yeast) > 10:
                add_alert_to_center(f"Yeast activity adjusted from {old_yeast:.0f}% to {y:.0f}%", "low", "info")
            
            st.success("✅ Parameters applied successfully!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    st.subheader("🎮 Fermentation Preview")
    sim_day = st.slider("Preview Day", 0, current_profile['fermentation_days'], 
                        st.session_state.fermentation_data.get('simulation_day', 0), 1)
    if sim_day != st.session_state.fermentation_data.get('simulation_day', 0):
        sync_parameters_with_day(sim_day, current_profile)
        st.rerun()

# =================================================================================
# 11. MAIN DASHBOARD (FULLY FUNCTIONAL)
# =================================================================================

data = st.session_state.fermentation_data
current_beer = data['beer_type']
current_profile = get_beer_profile(current_beer)
sim_day = data.get('simulation_day', 0)
total_days = current_profile['fermentation_days']

if sim_day > 0:
    st.info(f"🎮 **Simulation Mode:** Viewing Day {sim_day} of {total_days} | {data['progress']:.0f}% Complete")
else:
    elapsed_days = (datetime.now() - data['start_time']).total_seconds() / 3600 / 24
    current_day_display = min(total_days, int(elapsed_days) + 1)
    st.info(f"📅 **Fermentation Day {current_day_display} of {total_days}** | Target ABV: {current_profile['profile']['abv_target']}%")

if nav_page == "🏭 Main Dashboard":
    st.title("🍺 DESIGN AND SIMULATION OF AN AI-BASED FERMENTATION MONITORING SYSTEM FOR BEER FERMENTATION")
    st.caption("AI-Powered Brewery Monitoring | Real-Time Quality Control | Industry-Standard Profiles")
    
    # Beer Card
    st.markdown(f"""
    <div class="beer-card">
        <div style="font-size: 1rem; font-weight: 600; color: #e2e8f0;">🍺 {current_beer}</div>
        <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 4px;">
            {current_profile['type']} | Temp: {current_profile['profile']['temperature']['min']}°C-{current_profile['profile']['temperature']['max']}°C | 
            {current_profile['fermentation_days']} days | ABV: {current_profile['profile']['abv_target']}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI PREDICTIVE ALERTS
    st.markdown('<div class="ai-alert-box">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Smart Recommendations")
    st.markdown("---")
    
    current_display_day = sim_day if sim_day > 0 else min(total_days, int((datetime.now() - data['start_time']).total_seconds() / 3600 / 24) + 1)
    
    expected_sugar = calculate_expected_sugar_at_day(current_display_day, current_profile)
    expected_abv = calculate_expected_abv_at_day(current_display_day, current_profile)
    expected_yeast = calculate_expected_yeast_at_day(current_display_day, current_profile)
    
    ai_alerts = []
    ai_recommendations = []
    
    # TEMPERATURE WARNINGS
    temp_current = data['temperature']
    temp_min = current_profile['profile']['temperature']['min']
    temp_max = current_profile['profile']['temperature']['max']
    
    if temp_current > temp_max:
        alert_data = current_profile['warnings']['temp_high']
        alert_msg = alert_data['message'].format(value=temp_current)
        ai_alerts.append({"severity": "critical", "title": f"🚨 HIGH TEMPERATURE ALERT", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "critical", "error")
    elif temp_current < temp_min:
        alert_data = current_profile['warnings']['temp_low']
        alert_msg = alert_data['message'].format(value=temp_current)
        ai_alerts.append({"severity": "warning", "title": f"⚠️ LOW TEMPERATURE ALERT", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "warning", "warning")
    else:
        if temp_current > temp_max - 0.5:
            alert_msg = f"🌡️ Temperature at {temp_current:.1f}°C approaching {current_beer} maximum!"
            ai_alerts.append({"severity": "warning", "title": "⚠️ TEMPERATURE WARNING", 
                             "message": alert_msg,
                             "risk": "Risk of off-flavors if temperature continues to rise",
                             "action": f"Increase cooling to maintain below {temp_max}°C"})
            ai_recommendations.append(f"Increase cooling rate")
            add_alert_to_center(alert_msg, "warning", "warning")
        elif temp_current < temp_min + 0.5:
            alert_msg = f"🌡️ Temperature at {temp_current:.1f}°C approaching {current_beer} minimum!"
            ai_alerts.append({"severity": "warning", "title": "⚠️ TEMPERATURE WARNING", 
                             "message": alert_msg,
                             "risk": "Risk of yeast dormancy",
                             "action": f"Reduce cooling to maintain above {temp_min}°C"})
            ai_recommendations.append(f"Reduce cooling")
            add_alert_to_center(alert_msg, "warning", "warning")
    
    # YEAST WARNINGS - Based on fermentation phase
    yeast_current = data['yeast_activity']
    yeast_expected = expected_yeast
    yeast_deviation = yeast_current - yeast_expected
    
    if current_display_day <= 3:
        phase = "growth"
    elif current_display_day <= 5:
        phase = "peak"
    else:
        phase = "decline"
    
    if yeast_deviation < -8:
        if phase == "growth":
            alert_data = current_profile['warnings']['yeast_low_growth']
            alert_msg = alert_data['message'].format(value=yeast_current)
            ai_alerts.append({"severity": "critical", "title": "🌀 LOW YEAST ACTIVITY - Growth Phase", 
                             "message": alert_msg,
                             "risk": alert_data['risk'],
                             "action": alert_data['action']})
            ai_recommendations.append(alert_data['action'])
            add_alert_to_center(alert_msg, "critical", "error")
        elif phase == "peak":
            alert_data = current_profile['warnings']['yeast_low_peak']
            alert_msg = alert_data['message'].format(value=yeast_current)
            ai_alerts.append({"severity": "critical", "title": "🌀 LOW YEAST ACTIVITY - Peak Phase", 
                             "message": alert_msg,
                             "risk": alert_data['risk'],
                             "action": alert_data['action']})
            ai_recommendations.append(alert_data['action'])
            add_alert_to_center(alert_msg, "critical", "error")
        else:
            alert_data = current_profile['warnings']['yeast_low_decline']
            alert_msg = alert_data['message'].format(value=yeast_current)
            ai_alerts.append({"severity": "warning", "title": "🌀 RAPID YEAST DECLINE", 
                             "message": alert_msg,
                             "risk": alert_data['risk'],
                             "action": alert_data['action']})
            ai_recommendations.append(alert_data['action'])
            add_alert_to_center(alert_msg, "warning", "warning")
    
    # pH alerts
    if data['ph'] > current_profile['profile']['ph']['max']:
        alert_data = current_profile['warnings']['ph_high']
        alert_msg = alert_data['message'].format(value=data['ph'], max=current_profile['profile']['ph']['max'])
        ai_alerts.append({"severity": "critical", "title": "HIGH pH ALERT", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "critical", "error")
    elif data['ph'] < current_profile['profile']['ph']['min']:
        alert_data = current_profile['warnings']['ph_low']
        alert_msg = alert_data['message'].format(value=data['ph'], min=current_profile['profile']['ph']['min'])
        ai_alerts.append({"severity": "warning", "title": "LOW pH ALERT", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "warning", "warning")
    
    # Sugar alerts
    if current_profile['requires_sugar'] and data['sugar'] > expected_sugar * 1.15 and current_display_day > 2:
        alert_data = current_profile['warnings']['sugar_high']
        alert_msg = alert_data['message'].format(value=data['sugar'])
        ai_alerts.append({"severity": "warning", "title": "STUCK FERMENTATION", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "warning", "warning")
    
    # Low alcohol production
    if data['alcohol'] < expected_abv * 0.75 and current_display_day > 3:
        alert_data = current_profile['warnings']['abv_low']
        alert_msg = alert_data['message'].format(value=data['alcohol'])
        ai_alerts.append({"severity": "warning", "title": "LOW ALCOHOL PRODUCTION", 
                         "message": alert_msg,
                         "risk": alert_data['risk'],
                         "action": alert_data['action']})
        ai_recommendations.append(alert_data['action'])
        add_alert_to_center(alert_msg, "warning", "warning")
    
    critical_count = len([a for a in ai_alerts if a['severity'] == 'critical'])
    
    if critical_count > 0:
        st.error(f"### 🚨 {critical_count} CRITICAL ALERT(S) DETECTED")
        st.caption("Immediate operator intervention required")
    elif len(ai_alerts) > 0:
        st.warning(f"### ⚠️ CORRECTIVE ACTIONS RECOMMENDED")
        st.caption("Parameter deviations detected - follow recommendations below")
    else:
        st.success(f"### ✅ OPTIMAL FERMENTATION PROGRESSION")
        st.caption(f"All parameters within optimal ranges for {current_beer}")
    
    if ai_alerts:
        for alert in ai_alerts[:4]:
            if alert['severity'] == 'critical':
                st.markdown(f"""
                <div class="alert-critical">
                    <strong>🔴 {alert['title']}</strong><br>
                    📊 {alert['message']}<br>
                    ⚠️ <strong>Risk:</strong> {alert.get('risk', 'Monitor closely')}<br>
                    🛠️ <strong>Action:</strong> {alert['action']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>🟠 {alert['title']}</strong><br>
                    📊 {alert['message']}<br>
                    ⚠️ <strong>Risk:</strong> {alert.get('risk', 'Monitor closely')}<br>
                    🛠️ <strong>Action:</strong> {alert['action']}
                </div>
                """, unsafe_allow_html=True)
    
    if ai_recommendations:
        st.markdown("#### 🛠️ Smart Recommendations")
        for rec in ai_recommendations[:4]:
            st.markdown(f"- {rec}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quality_score_val = data['quality_score']
        if quality_score_val >= 92:
            health_color = "status-excellent"
            health_text = "Excellent"
        elif quality_score_val >= 85:
            health_color = "status-verygood"
            health_text = "Very Good"
        elif quality_score_val >= 78:
            health_color = "status-good"
            health_text = "Good"
        elif quality_score_val >= 70:
            health_color = "status-warning"
            health_text = "Fair"
        else:
            health_color = "status-critical"
            health_text = "Critical"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">QUALITY SCORE</div>
            <div class="kpi-value">{quality_score_val:.1f}%</div>
            <span class="status-badge {health_color}">{health_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        health_score_val = data['health_score']
        if health_score_val >= 85:
            health_color = "status-excellent"
            health_text = "Excellent"
        elif health_score_val >= 70:
            health_color = "status-good"
            health_text = "Good"
        else:
            health_color = "status-warning"
            health_text = "Warning"
        
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">FERMENTATION HEALTH</div>
            <div class="kpi-value">{health_score_val}%</div>
            <span class="status-badge {health_color}">{health_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risk_val = data['contamination_risk']
        risk_color = "status-critical" if risk_val > 40 else "status-warning" if risk_val > 20 else "status-excellent"
        risk_text = 'High' if risk_val > 40 else 'Medium' if risk_val > 20 else 'Low'
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">CONTAMINATION RISK</div>
            <div class="kpi-value">{risk_val:.0f}%</div>
            <span class="status-badge {risk_color}">{risk_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">CURRENT ABV</div>
            <div class="kpi-value">{data['alcohol']:.1f}%</div>
            <span class="status-badge status-good">Target: {current_profile['profile']['abv_target']}%</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress
    display_day = sim_day if sim_day > 0 else min(total_days, int((datetime.now() - data['start_time']).total_seconds() / 3600 / 24) + 1)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.progress(data['progress']/100, text=f"Overall Completion: {data['progress']:.1f}%")
    with col2:
        st.metric("📅 Day", f"{display_day} / {total_days}")
    with col3:
        remaining_days = max(0, total_days - display_day)
        st.metric("⏳ Remaining", f"{remaining_days} days")
    
    # Stage
    stage_emojis = {"Active Fermentation": "⚡", "Conditioning": "🌡️", "Maturation": "🍺", "Complete": "✅"}
    stage_emoji = stage_emojis.get(data['stage'], "🔄")
    stage_colors = {"Active Fermentation": "#f59e0b", "Conditioning": "#3b82f6", "Maturation": "#10b981", "Complete": "#34d399"}
    stage_color = stage_colors.get(data['stage'], "#94a3b8")
    st.markdown(f"""
    <div style="background: {stage_color}20; border-left: 4px solid {stage_color}; 
                padding: 12px 16px; border-radius: 12px; margin: 15px 0;">
        <strong>{stage_emoji} Current Stage:</strong> {data['stage']}
    </div>
    """, unsafe_allow_html=True)
    
    # Fermentation Trends
    st.markdown("### 📈 Fermentation Trends")
    st.caption("Real-time fermentation progress tracking with smooth transitions")
    
    trend_days = list(range(1, min(display_day + 1, total_days + 1)))
    
    sugar_trend = []
    alcohol_trend = []
    temp_trend = []
    yeast_trend = []
    
    for day in trend_days:
        sugar_trend.append(calculate_expected_sugar_at_day(day, current_profile))
        alcohol_trend.append(calculate_expected_abv_at_day(day, current_profile))
        temp_trend.append(calculate_expected_temperature_at_day(day, current_profile))
        yeast_trend.append(calculate_expected_yeast_at_day(day, current_profile))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if current_profile['requires_sugar']:
            fig_sugar = go.Figure()
            fig_sugar.add_trace(go.Scatter(x=trend_days, y=sugar_trend, mode='lines+markers', 
                                          name='Expected Sugar', line=dict(color='#f59e0b', width=3), 
                                          fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.1)'))
            fig_sugar.add_trace(go.Scatter(x=[display_day], y=[data['sugar']], mode='markers', 
                                          name='Current', marker=dict(size=14, color='#ef4444', symbol='circle')))
            fig_sugar.update_layout(title="🍬 Sugar Content (°Bx)", xaxis_title="Day", yaxis_title="°Bx", 
                                   template="plotly_dark", height=320, font=dict(color='#e2e8f0'))
            st.plotly_chart(fig_sugar, use_container_width=True)
        else:
            st.info("📊 Sugar monitoring is passive for this beer type (no sugar addition required)")
        
        fig_yeast = go.Figure()
        fig_yeast.add_trace(go.Scatter(x=trend_days, y=yeast_trend, mode='lines+markers', 
                                      name='Expected Yeast', line=dict(color='#ec4899', width=3), 
                                      fill='tozeroy', fillcolor='rgba(236, 72, 153, 0.1)'))
        fig_yeast.add_trace(go.Scatter(x=[display_day], y=[data['yeast_activity']], mode='markers', 
                                      name='Current', marker=dict(size=14, color='#ef4444', symbol='circle')))
        fig_yeast.update_layout(title="🌀 Yeast Activity (%) - Growth → Peak → Decline", xaxis_title="Day", yaxis_title="%", 
                               template="plotly_dark", height=320, font=dict(color='#e2e8f0'))
        fig_yeast.add_hrect(y0=current_profile['profile']['yeast_activity']['optimal_range'][0], 
                           y1=current_profile['profile']['yeast_activity']['optimal_range'][1],
                           fillcolor="green", opacity=0.2, line_width=0,
                           annotation_text="Optimal Range", annotation_position="top left")
        st.plotly_chart(fig_yeast, use_container_width=True)
    
    with col2:
        fig_alcohol = go.Figure()
        fig_alcohol.add_trace(go.Scatter(x=trend_days, y=alcohol_trend, mode='lines+markers', 
                                        name='Expected Alcohol', line=dict(color='#34d399', width=3), 
                                        fill='tozeroy', fillcolor='rgba(52, 211, 153, 0.1)'))
        fig_alcohol.add_trace(go.Scatter(x=[display_day], y=[data['alcohol']], mode='markers', 
                                        name='Current', marker=dict(size=14, color='#ef4444', symbol='circle')))
        fig_alcohol.update_layout(title="🍺 Alcohol (% ABV)", xaxis_title="Day", yaxis_title="% ABV", 
                                 template="plotly_dark", height=320, font=dict(color='#e2e8f0'))
        fig_alcohol.add_hline(y=current_profile['profile']['abv_target'], line_dash="dash", 
                             line_color="green", annotation_text="Target")
        st.plotly_chart(fig_alcohol, use_container_width=True)
        
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=trend_days, y=temp_trend, mode='lines+markers', 
                                     name='Expected Temperature', line=dict(color='#ef4444', width=3), 
                                     fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.1)'))
        fig_temp.add_trace(go.Scatter(x=[display_day], y=[data['temperature']], mode='markers', 
                                     name='Current', marker=dict(size=14, color='#ef4444', symbol='circle')))
        fig_temp.update_layout(title="🌡️ Temperature (°C)", xaxis_title="Day", yaxis_title="°C", 
                              template="plotly_dark", height=320, font=dict(color='#e2e8f0'))
        fig_temp.add_hrect(y0=current_profile['profile']['temperature']['min'], 
                          y1=current_profile['profile']['temperature']['max'],
                          fillcolor="green", opacity=0.2, line_width=0,
                          annotation_text=f"Optimal Range: {current_profile['profile']['temperature']['min']}°C-{current_profile['profile']['temperature']['max']}°C", 
                          annotation_position="top left")
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Quality Control Dashboard
    st.markdown("### 🛡️ Quality Control Dashboard")
    
    quality_score = data['quality_score']
    if quality_score >= 92:
        quality_grade = "Excellent"
        quality_color = "#10b981"
    elif quality_score >= 85:
        quality_grade = "Very Good"
        quality_color = "#3b82f6"
    elif quality_score >= 78:
        quality_grade = "Good"
        quality_color = "#8b5cf6"
    elif quality_score >= 70:
        quality_grade = "Fair"
        quality_color = "#f59e0b"
    else:
        quality_grade = "Poor"
        quality_color = "#ef4444"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig_quality = go.Figure(go.Indicator(
            mode="gauge+number+delta", 
            value=quality_score, 
            title={'text': "Quality Score", 'font': {'color': '#e2e8f0', 'size': 14}}, 
            delta={'reference': 85}, 
            gauge={
                'axis': {'range': [0, 100]}, 
                'bar': {'color': quality_color}, 
                'steps': [
                    {'range': [0, 60], 'color': '#7f1a1a'}, 
                    {'range': [60, 70], 'color': '#78350f'}, 
                    {'range': [70, 78], 'color': '#b45309'},
                    {'range': [78, 85], 'color': '#6d28d9'},
                    {'range': [85, 92], 'color': '#1d4ed8'},
                    {'range': [92, 100], 'color': '#065f46'}
                ], 
                'threshold': {'value': 85, 'line': {'color': "white", 'width': 2}}
            }))
        fig_quality.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'})
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div class="kpi-label">QUALITY GRADE</div>
            <div style="font-size: 2rem; font-weight: 700; color: {quality_color};">{quality_grade}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div class="kpi-label">SUCCESS PROBABILITY</div>
            <div style="font-size: 2rem; font-weight: 700; color: #34d399;">{data.get('success_probability', 85):.1f}%</div>
            <div style="font-size: 0.8rem;">Target: {current_profile['profile']['abv_target']}% ABV</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_color_val = "#ef4444" if data['contamination_risk'] > 35 else "#f59e0b" if data['contamination_risk'] > 15 else "#10b981"
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div class="kpi-label">CONTAMINATION RISK</div>
            <div style="font-size: 2rem; font-weight: 700; color: {risk_color_val};">{data['contamination_risk']:.0f}%</div>
            <div style="margin-top: 10px;">Based on pH + Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Current Parameters
    st.markdown("### 🎯 Current Parameters")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Temperature", f"{data['temperature']:.1f}°C", 
                f"Optimal: {current_profile['profile']['temperature']['optimal']}°C")
    col2.metric("🔬 pH", f"{data['ph']:.2f}", 
                f"Target: {current_profile['profile']['ph']['optimal']}")
    col3.metric("🍬 Sugar", f"{data['sugar']:.1f}°Bx", 
                f"Initial: {current_profile['profile']['sugar']['optimal_start']}°Bx" if current_profile['requires_sugar'] else "Malt-derived")
    col4.metric("🍺 Alcohol", f"{data['alcohol']:.2f}%", 
                f"Target: {current_profile['profile']['abv_target']}%")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("🌀 Yeast", f"{data['yeast_activity']:.0f}%", 
                f"Strain: {current_profile['profile']['yeast_strain'].split()[-1]}")
    col6.metric("💨 CO2", f"{data['co2']:.2f} vol", 
                f"Target: {current_profile['profile']['co2']['optimal']}")
    col7.metric("🎛️ Pressure", f"{data['pressure']:.2f} bar")
    col8.metric("💧 Turbidity", f"{data.get('water_turbidity', 0.30):.2f} NTU", 
                f"Optimal: {WATER_QUALITY_STANDARDS['optimal_turbidity']:.2f}")
    
    if data.get('yeast_deviation', 0) != 0 or data.get('temp_deviation', 0) != 0:
        st.info(f"""
        📊 **User Adjustments Active:** 
        Yeast {data['yeast_deviation']:+.1f}% | 
        Temperature {data['temp_deviation']:+.1f}°C | 
        pH {data['ph_deviation']:+.2f}
        """)
    
    st.info(f"**Batch ID:** {data['batch_id']} | **Grain Used:** {data.get('grain_amount_kg', 0):,} kg of {data.get('grain_type', 'Unknown')} | **Process Efficiency:** {data['process_efficiency']:.0f}%")

# =================================================================================
# 12. VIRTUAL SENSORS PAGE
# =================================================================================

elif nav_page == "🎛️ Virtual Sensors":
    st.header("🎛️ AI-Powered Virtual Sensors")
    st.caption(f"Real-time sensor monitoring for {current_beer} fermentation")
    
    sensors = {
        "🌡️ Temperature Sensor": {"value": data['temperature'], "unit": "°C", 
                                   "target": current_profile['profile']['temperature']['optimal'],
                                   "min": current_profile['profile']['temperature']['min'],
                                   "max": current_profile['profile']['temperature']['max'],
                                   "icon": "🌡️", "color": "#ef4444"},
        "🔬 pH Sensor": {"value": data['ph'], "unit": "", 
                        "target": current_profile['profile']['ph']['optimal'],
                        "min": current_profile['profile']['ph']['min'],
                        "max": current_profile['profile']['ph']['max'],
                        "icon": "🔬", "color": "#10b981"},
        "🍬 Sugar Sensor": {"value": data['sugar'], "unit": "°Bx", 
                           "target": current_profile['profile']['sugar']['optimal_start'],
                           "min": current_profile['profile']['sugar']['min'],
                           "max": current_profile['profile']['sugar']['max'],
                           "icon": "🍬", "color": "#f59e0b"},
        "🍺 Alcohol Sensor": {"value": data['alcohol'], "unit": "% ABV", 
                              "target": current_profile['profile']['abv_target'],
                              "min": 0, "max": 8, "icon": "🍺", "color": "#34d399"},
        "🌀 Yeast Sensor": {"value": data['yeast_activity'], "unit": "%", 
                            "target": current_profile['profile']['yeast_activity']['optimal_peak'],
                            "min": 0, "max": 100, "icon": "🌀", "color": "#ec4899"},
        "💨 CO2 Sensor": {"value": data['co2'], "unit": "vol", 
                          "target": current_profile['profile']['co2']['optimal'],
                          "min": 1.5, "max": 3.5, "icon": "💨", "color": "#a78bfa"}
    }
    
    col1, col2 = st.columns(2)
    sensor_items = list(sensors.items())
    
    for i, (name, sensor) in enumerate(sensor_items):
        with col1 if i % 2 == 0 else col2:
            if name == "🍬 Sugar Sensor" and not current_profile['requires_sugar']:
                continue
            st.markdown(f"""
            <div class="dashboard-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <div style="font-size: 1rem; font-weight: 600;">{name}</div>
                    </div>
                    <div style="font-size: 1.5rem;">{sensor['icon']}</div>
                </div>
                <div style="margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span style="font-size: 2rem; font-weight: 700; color: {sensor['color']};">{sensor['value']:.1f}</span>
                            <span style="font-size: 0.9rem;"> {sensor['unit']}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 0.7rem;">Target: {sensor['target']} {sensor['unit']}</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="background: #334155; border-radius: 8px; height: 6px;">
                            <div style="background: {sensor['color']}; width: {min(100, max(0, (sensor['value'] - sensor['min']) / (sensor['max'] - sensor['min']) * 100))}%; height: 100%; border-radius: 8px;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📊 Sensor Performance")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Sensor Accuracy", "98.5%", "+0.2%")
    with col2:
        st.metric("🤖 AI Confidence", f"{data.get('ai_confidence', 90)}%", "Stable")
    with col3:
        st.metric("📡 Active Sensors", "6/6", "Online")
    with col4:
        st.metric("⚡ Refresh Rate", "1.2s", "Real-time")

# =================================================================================
# 13. LIVE MONITORING PAGE
# =================================================================================

elif nav_page == "📊 Live Monitoring":
    st.header("📊 Live Monitoring")
    if sim_day > 0:
        st.warning(f"🔮 Simulation Mode: Day {sim_day}")
    if st.session_state.historical_data:
        df = pd.DataFrame(st.session_state.historical_data[-30:])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], name='Temperature', line=dict(color='#ef4444')))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sugar'], name='Sugar', line=dict(color='#f59e0b')))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['alcohol'], name='Alcohol', line=dict(color='#34d399')))
        fig.update_layout(title="Real-Time Parameters", template="plotly_dark", height=450, font=dict(color='#e2e8f0'))
        st.plotly_chart(fig, use_container_width=True)

# =================================================================================
# 14. FERMENTATION ANALYTICS PAGE
# =================================================================================

elif nav_page == "📈 Fermentation Analytics":
    st.header("📈 Fermentation Analytics")
    if st.session_state.historical_data:
        df = pd.DataFrame(st.session_state.historical_data)
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.line(df, x='timestamp', y='temperature', title="Temperature Profile", template="plotly_dark")
            fig1.update_layout(font=dict(color='#e2e8f0'))
            st.plotly_chart(fig1, use_container_width=True)
            fig2 = px.line(df, x='timestamp', y='sugar', title="Sugar Attenuation", template="plotly_dark")
            fig2.update_layout(font=dict(color='#e2e8f0'))
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = px.line(df, x='timestamp', y='ph', title="pH Evolution", template="plotly_dark")
            fig3.update_layout(font=dict(color='#e2e8f0'))
            st.plotly_chart(fig3, use_container_width=True)
            fig4 = px.line(df, x='timestamp', y='alcohol', title="Alcohol Accumulation", template="plotly_dark")
            fig4.update_layout(font=dict(color='#e2e8f0'))
            st.plotly_chart(fig4, use_container_width=True)

# =================================================================================
# 15. ALERT CENTER PAGE
# =================================================================================

elif nav_page == "🚨 Alert Center":
    st.header("🚨 Alert Center")
    st.caption("All system alerts and deviation warnings")
    
    if st.session_state.alerts:
        critical_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'critical']
        warning_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'warning']
        info_alerts = [a for a in st.session_state.alerts if a.get('severity') == 'low']
        
        if critical_alerts:
            st.markdown("### 🔴 Critical Alerts")
            for a in critical_alerts[:10]:
                st.error(f"**[{a['time']}]** {a['message']}")
        
        if warning_alerts:
            st.markdown("### 🟠 Warning Alerts")
            for a in warning_alerts[:20]:
                st.warning(f"**[{a['time']}]** {a['message']}")
        
        if info_alerts:
            st.markdown("### 🔵 Info Alerts")
            for a in info_alerts[:10]:
                st.info(f"**[{a['time']}]** {a['message']}")
        
        if st.button("🗑️ Clear All Alerts", use_container_width=True):
            st.session_state.alerts = []
            st.rerun()
    else:
        st.success("✅ No active alerts. All systems operating normally.")

# =================================================================================
# 16. QUALITY CONTROL PAGE
# =================================================================================

elif nav_page == "🛡️ Quality Control":
    st.header("🛡️ Quality Control Dashboard")
    st.caption("Comprehensive quality analysis with radar chart and detailed metrics")
    
    current_display_day = sim_day if sim_day > 0 else min(total_days, int((datetime.now() - data['start_time']).total_seconds() / 3600 / 24) + 1)
    
    # Quality Overview Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="quality-card">
            <div style="font-size: 0.7rem; color: #94a3b8;">OVERALL</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38bdf8;">{data['quality_score']:.0f}</div>
            <div style="font-size: 0.7rem;">/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="quality-card">
            <div style="font-size: 0.7rem; color: #94a3b8;">FLAVOR</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">{data.get('flavor_score', 85)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="quality-card">
            <div style="font-size: 0.7rem; color: #94a3b8;">AROMA</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #f59e0b;">{data.get('aroma_score', 82)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="quality-card">
            <div style="font-size: 0.7rem; color: #94a3b8;">CLARITY</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #8b5cf6;">{data.get('clarity_score', 90)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="quality-card">
            <div style="font-size: 0.7rem; color: #94a3b8;">HEALTH</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ec4899;">{data['health_score']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Radar Chart
    categories = ['Temperature', 'pH', 'Yeast Activity', 'Sugar Profile', 'CO2 Level', 'Alcohol Progress']
    
    temp_score = max(0, 100 - abs(data['temperature'] - current_profile['profile']['temperature']['optimal']) * 12)
    ph_score = max(0, 100 - abs(data['ph'] - current_profile['profile']['ph']['optimal']) * 22)
    yeast_score = data['yeast_activity']
    expected_sugar_val = calculate_expected_sugar_at_day(current_display_day, current_profile)
    sugar_score = max(0, 100 - abs(data['sugar'] - expected_sugar_val) * 7)
    co2_score = max(0, 100 - abs(data['co2'] - current_profile['profile']['co2']['optimal']) * 28)
    alcohol_score = (data['alcohol'] / current_profile['profile']['abv_target']) * 100 if current_profile['profile']['abv_target'] > 0 else 0
    
    values = [temp_score, ph_score, yeast_score, sugar_score, co2_score, min(100, alcohol_score)]
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            marker=dict(color='#38bdf8', size=8),
            line=dict(color='#3b82f6', width=2),
            fillcolor='rgba(56, 189, 248, 0.2)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color='#94a3b8'),
                angularaxis=dict(color='#94a3b8', tickfont=dict(size=10))
            ),
            title="Quality Dimensions Radar Chart",
            template="plotly_dark",
            height=450,
            font=dict(color='#e2e8f0')
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        quality_score = data['quality_score']
        if quality_score >= 92:
            grade, grade_color, grade_icon = "EXCELLENT", "#10b981", "🏆"
        elif quality_score >= 85:
            grade, grade_color, grade_icon = "VERY GOOD", "#3b82f6", "👍"
        elif quality_score >= 78:
            grade, grade_color, grade_icon = "GOOD", "#8b5cf6", "✓"
        elif quality_score >= 70:
            grade, grade_color, grade_icon = "FAIR", "#f59e0b", "⚠️"
        else:
            grade, grade_color, grade_icon = "POOR", "#ef4444", "🔴"
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=quality_score,
            title={'text': "Quality Score", 'font': {'color': '#e2e8f0', 'size': 14}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
                'bar': {'color': grade_color},
                'steps': [
                    {'range': [0, 60], 'color': '#7f1a1a'},
                    {'range': [60, 70], 'color': '#78350f'},
                    {'range': [70, 78], 'color': '#b45309'},
                    {'range': [78, 85], 'color': '#6d28d9'},
                    {'range': [85, 92], 'color': '#1d4ed8'},
                    {'range': [92, 100], 'color': '#065f46'}
                ],
                'threshold': {'value': 85, 'line': {'color': "white", 'width': 2}}
            }
        ))
        fig_gauge.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'})
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 10px;">
            <span class="status-badge" style="background: {grade_color};">
                {grade_icon} Grade: {grade}
            </span>
        </div>
        """, unsafe_allow_html=True)

# =================================================================================
# 17. BATCH REPORTS PAGE
# =================================================================================

elif nav_page == "📋 Batch Reports":
    st.header("📋 Batch Reports Dashboard")
    st.caption("Comprehensive batch analysis with export capabilities")
    
    with st.spinner("Generating comprehensive batch report..."):
        report = generate_report("batch")
    
    quality_score = report['quality_metrics']['overall_quality_score']
    if quality_score >= 92:
        grade_text, grade_color, grade_icon = "EXCELLENT", "#10b981", "🏆"
    elif quality_score >= 85:
        grade_text, grade_color, grade_icon = "VERY GOOD", "#3b82f6", "👍"
    elif quality_score >= 78:
        grade_text, grade_color, grade_icon = "GOOD", "#8b5cf6", "✓"
    elif quality_score >= 70:
        grade_text, grade_color, grade_icon = "FAIR", "#f59e0b", "⚠️"
    else:
        grade_text, grade_color, grade_icon = "POOR", "#ef4444", "🔴"
    
    st.markdown(f"""
    <div class="report-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 1.5rem; font-weight: bold;">🍺 {report['batch_info']['beer_type']}</div>
                <div style="color: #94a3b8;">Batch ID: <strong>{report['batch_info']['batch_id']}</strong> | {report['generated_at']}</div>
            </div>
            <div>
                <span class="status-badge" style="background: {grade_color};">{grade_icon} {grade_text} ({quality_score})</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Batch Info", "🔬 Parameters", "⚠️ Risk & Predictions", "📎 Export"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Batch Information")
            st.dataframe(pd.DataFrame(list(report['batch_info'].items()), columns=["Parameter", "Value"]), 
                        use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Quality Metrics")
            st.dataframe(pd.DataFrame(list(report['quality_metrics'].items()), columns=["Metric", "Value"]), 
                        use_container_width=True, hide_index=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Fermentation Parameters")
            params_list = []
            for key, value in report['fermentation_parameters'].items():
                if isinstance(value, dict):
                    params_list.append({"Parameter": key.upper(), "Current": value.get('current', 'N/A'), "Target": value.get('target', 'N/A')})
                else:
                    params_list.append({"Parameter": key.upper(), "Current": value, "Target": "N/A"})
            st.dataframe(pd.DataFrame(params_list), use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Water Quality")
            st.dataframe(pd.DataFrame(list(report['water_quality'].items()), columns=["Parameter", "Value"]), 
                        use_container_width=True, hide_index=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Risk Assessment")
            st.dataframe(pd.DataFrame(list(report['risk_assessment'].items()), columns=["Factor", "Value"]), 
                        use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Predictions")
            st.dataframe(pd.DataFrame(list(report['predictions'].items()), columns=["Prediction", "Value"]), 
                        use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader("Export Options")
        if st.button("📄 Export to Excel", use_container_width=True):
            excel_data = export_to_excel(report)
            st.download_button("⬇️ Download Report", data=excel_data, 
                              file_name=f"batch_report_{report['batch_info']['batch_id']}.xlsx", 
                              use_container_width=True)

# =================================================================================
# 18. HISTORICAL ARCHIVE PAGE
# =================================================================================

elif nav_page == "📚 Historical Archive":
    st.header("📚 Historical Archive")
    st.caption("Batch history with filtering and search capabilities")
    
    if st.session_state.batch_history:
        df_history = pd.DataFrame(st.session_state.batch_history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            beer_filter = st.selectbox("Filter by Beer", ["All"] + list(df_history['beer'].unique()))
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(df_history['status'].unique()))
        with col3:
            sort_by = st.selectbox("Sort by", ["date", "quality", "abv", "efficiency"])
        
        filtered_df = df_history.copy()
        if beer_filter != "All":
            filtered_df = filtered_df[filtered_df['beer'] == beer_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False)
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        st.subheader("📈 Historical Quality Trend")
        fig = px.line(df_history, x='date', y='quality', color='beer', 
                      title="Batch Quality Over Time", template="plotly_dark", markers=True)
        fig.add_hline(y=85, line_dash="dash", line_color="green", annotation_text="Quality Target")
        fig.update_layout(font=dict(color='#e2e8f0'), height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📊 Historical Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Batches", len(df_history))
        with col2:
            st.metric("Average Quality", f"{df_history['quality'].mean():.0f}")
        with col3:
            st.metric("Average ABV", f"{df_history['abv'].mean():.1f}%")
        with col4:
            st.metric("Average Efficiency", f"{df_history['efficiency'].mean():.0f}%")
    else:
        st.info("No historical batches available yet")

# =================================================================================
# 19. SYSTEM SETTINGS PAGE
# =================================================================================

elif nav_page == "⚙️ System Settings":
    st.header("⚙️ System Settings")
    st.caption("Configure fermentation parameter limits - These limits apply to Process Controls")
    
    st.markdown("### 🔧 Fermentation Parameter Limits")
    st.info("ℹ️ These min/max values will be used in the Process Controls sliders on the sidebar.")
    
    limits = st.session_state.settings['fermentation_limits']
    
    with st.expander("🌡️ TEMPERATURE", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min Temperature (°C)", value=float(limits['temperature']['min']), step=0.5, key="temp_min")
        with col2:
            new_max = st.number_input("Max Temperature (°C)", value=float(limits['temperature']['max']), step=0.5, key="temp_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (°C)", value=float(limits['temperature']['warning_tolerance']), step=0.1, key="temp_warn")
        limits['temperature']['min'] = new_min
        limits['temperature']['max'] = new_max
        limits['temperature']['warning_tolerance'] = new_warning
    
    with st.expander("🔬 pH", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min pH", value=float(limits['ph']['min']), step=0.1, key="ph_min")
        with col2:
            new_max = st.number_input("Max pH", value=float(limits['ph']['max']), step=0.1, key="ph_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance", value=float(limits['ph']['warning_tolerance']), step=0.05, key="ph_warn")
        limits['ph']['min'] = new_min
        limits['ph']['max'] = new_max
        limits['ph']['warning_tolerance'] = new_warning
    
    with st.expander("🍬 Sugar", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min Sugar (°Bx)", value=float(limits['sugar']['min']), step=0.5, key="sugar_min")
        with col2:
            new_max = st.number_input("Max Sugar (°Bx)", value=float(limits['sugar']['max']), step=0.5, key="sugar_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (°Bx)", value=float(limits['sugar']['warning_tolerance']), step=0.2, key="sugar_warn")
        limits['sugar']['min'] = new_min
        limits['sugar']['max'] = new_max
        limits['sugar']['warning_tolerance'] = new_warning
    
    with st.expander("🌀 Yeast Activity", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min Yeast (%)", value=int(limits['yeast_activity']['min']), step=5, key="yeast_min")
        with col2:
            new_max = st.number_input("Max Yeast (%)", value=int(limits['yeast_activity']['max']), step=5, key="yeast_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (%)", value=int(limits['yeast_activity']['warning_tolerance']), step=2, key="yeast_warn")
        limits['yeast_activity']['min'] = new_min
        limits['yeast_activity']['max'] = new_max
        limits['yeast_activity']['warning_tolerance'] = new_warning
    
    with st.expander("🎛️ Pressure", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min Pressure (bar)", value=float(limits['pressure']['min']), step=0.1, key="pressure_min")
        with col2:
            new_max = st.number_input("Max Pressure (bar)", value=float(limits['pressure']['max']), step=0.1, key="pressure_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (bar)", value=float(limits['pressure']['warning_tolerance']), step=0.1, key="pressure_warn")
        limits['pressure']['min'] = new_min
        limits['pressure']['max'] = new_max
        limits['pressure']['warning_tolerance'] = new_warning
    
    with st.expander("💨 CO2", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min CO2 (vol)", value=float(limits['co2']['min']), step=0.1, key="co2_min")
        with col2:
            new_max = st.number_input("Max CO2 (vol)", value=float(limits['co2']['max']), step=0.1, key="co2_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (vol)", value=float(limits['co2']['warning_tolerance']), step=0.1, key="co2_warn")
        limits['co2']['min'] = new_min
        limits['co2']['max'] = new_max
        limits['co2']['warning_tolerance'] = new_warning
    
    with st.expander("🍺 Alcohol", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input("Min Alcohol (%)", value=float(limits['alcohol']['min']), step=0.5, key="alcohol_min")
        with col2:
            new_max = st.number_input("Max Alcohol (%)", value=float(limits['alcohol']['max']), step=0.5, key="alcohol_max")
        with col3:
            new_warning = st.number_input("Warning Tolerance (%)", value=float(limits['alcohol']['warning_tolerance']), step=0.1, key="alcohol_warn")
        limits['alcohol']['min'] = new_min
        limits['alcohol']['max'] = new_max
        limits['alcohol']['warning_tolerance'] = new_warning
    
    # Turbidity Settings
    st.markdown("---")
    st.markdown("### 💧 Water Quality Settings")
    st.info("ℹ️ Configure turbidity limits for water quality monitoring")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        WATER_QUALITY_STANDARDS["optimal_turbidity"] = st.number_input(
            "Optimal Turbidity (NTU)", 
            value=WATER_QUALITY_STANDARDS["optimal_turbidity"], 
            step=0.01, 
            format="%.2f",
            key="optimal_turbidity"
        )
    with col2:
        WATER_QUALITY_STANDARDS["warning_turbidity"] = st.number_input(
            "Warning Turbidity (NTU)", 
            value=WATER_QUALITY_STANDARDS["warning_turbidity"], 
            step=0.01, 
            format="%.2f",
            key="warning_turbidity"
        )
    with col3:
        WATER_QUALITY_STANDARDS["max_turbidity"] = st.number_input(
            "Maximum Turbidity (NTU)", 
            value=WATER_QUALITY_STANDARDS["max_turbidity"], 
            step=0.01, 
            format="%.2f",
            key="max_turbidity"
        )
    
    st.caption(f"Current water turbidity: {st.session_state.fermentation_data.get('water_turbidity', 0.30):.2f} NTU")
    
    if st.button("💾 Save All Settings", use_container_width=True, type="primary"):
        st.session_state.settings['fermentation_limits'] = limits
        st.success("✅ All fermentation limits and water quality settings saved successfully!")

# =================================================================================
# FOOTER
# =================================================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.75rem;">
    DESIGN AND SIMULATION OF AN AI-BASED FERMENTATION MONITORING SYSTEM FOR BEER FERMENTATION | 
    {current_beer} | {current_profile['fermentation_days']}-Day Profile | Batch: {data['batch_id']}
</div>
""", unsafe_allow_html=True)