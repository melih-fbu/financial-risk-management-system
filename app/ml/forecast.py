import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from app.risk.calculator import RiskCalculator


class MetalForecaster:
    @staticmethod
    def _build_features(prices: pd.Series, window_size: int = 5):
        clean_prices = prices.dropna().reset_index(drop=True)
        if len(clean_prices) <= window_size:
            return None, None, clean_prices

        rows = []
        targets = []

        for index in range(window_size, len(clean_prices)):
            window = clean_prices.iloc[index - window_size:index]
            rows.append(window.tolist())
            targets.append(float(clean_prices.iloc[index]))

        return np.array(rows), np.array(targets), clean_prices

    @staticmethod
    def predict_future_prices(prices: pd.Series, days_ahead: int = 7, window_size: int = 5):
        clean_prices = prices.dropna().reset_index(drop=True)
        requested_days = days_ahead
        effective_days = min(days_ahead, 3)
        warning = None

        if requested_days > 3:
            warning = "3 günden fazla tahmin için Monte Carlo simülasyonunu kullanın"

        if len(clean_prices) < 30:
            confidence = "low"
        elif len(clean_prices) < 100:
            confidence = "medium"
        else:
            confidence = "high"

        latest_price = float(clean_prices.iloc[-1]) if len(clean_prices) else 0.0
        recent_window = clean_prices.iloc[-window_size:].tolist() if len(clean_prices) >= window_size else []

        if len(clean_prices) <= window_size:
            fallback_predictions = [
                {"day": day, "predicted_price": latest_price}
                for day in range(1, effective_days + 1)
            ]
            return {
                "last_price": latest_price,
                "days_ahead": effective_days,
                "requested_days_ahead": requested_days,
                "training_points": int(len(clean_prices)),
                "predicted_prices": fallback_predictions,
                "mean_predicted_price": latest_price,
                "trend": "stable",
                "confidence": confidence,
                "warning": warning,
            }

        predicted_prices = []

        for horizon in range(1, effective_days + 1):
            feature_rows = []
            target_rows = []

            for index in range(window_size, len(clean_prices) - horizon + 1):
                window = clean_prices.iloc[index - window_size:index]
                target = clean_prices.iloc[index + horizon - 1]
                feature_rows.append(window.tolist())
                target_rows.append(float(target))

            if not feature_rows:
                predicted_prices.append({"day": horizon, "predicted_price": latest_price})
                continue

            model = LinearRegression()
            model.fit(np.array(feature_rows), np.array(target_rows))
            next_price = float(model.predict([recent_window])[0])
            predicted_prices.append({"day": horizon, "predicted_price": next_price})

        mean_predicted_price = float(np.mean([item["predicted_price"] for item in predicted_prices]))

        if predicted_prices[-1]["predicted_price"] > latest_price:
            trend = "up"
        elif predicted_prices[-1]["predicted_price"] < latest_price:
            trend = "down"
        else:
            trend = "stable"

        return {
            "last_price": latest_price,
            "days_ahead": effective_days,
            "requested_days_ahead": requested_days,
            "training_points": int(len(clean_prices)),
            "predicted_prices": predicted_prices,
            "mean_predicted_price": mean_predicted_price,
            "trend": trend,
            "confidence": confidence,
            "warning": warning,
        }

    @staticmethod
    def calculate_risk_score(prices: pd.Series) -> dict:
        clean_prices = prices.dropna()
        if len(clean_prices) < 2:
            return {
                "risk_score": 0.0,
                "risk_level": "low",
                "risk_label": "Düşük Risk",
            }

        volatility = RiskCalculator.calculate_volatility(clean_prices)
        var_95 = RiskCalculator.calculate_historical_var(clean_prices, 0.95)
        max_drawdown = abs(RiskCalculator.calculate_max_drawdown(clean_prices))
        sharpe_ratio = RiskCalculator.calculate_sharpe_ratio(clean_prices)

        volatility_score = min(max(volatility / 40 * 100, 0), 100)
        var_score = min(max(var_95 / 0.10 * 100, 0), 100)
        drawdown_score = min(max(max_drawdown / 50 * 100, 0), 100)
        sharpe_clamped = min(max(sharpe_ratio, -1), 3)
        sharpe_score = ((3 - sharpe_clamped) / 4) * 100

        risk_score = (
            volatility_score * 0.30
            + var_score * 0.30
            + drawdown_score * 0.25
            + sharpe_score * 0.15
        )

        if risk_score < 35:
            risk_level = "low"
            risk_label = "Düşük Risk"
        elif risk_score < 65:
            risk_level = "medium"
            risk_label = "Orta Risk"
        else:
            risk_level = "high"
            risk_label = "Yüksek Risk"

        return {
            "risk_score": float(round(risk_score, 2)),
            "risk_level": risk_level,
            "risk_label": risk_label,
        }

    @staticmethod
    def classify_volatility(prices: pd.Series) -> dict:
        volatility_pct = RiskCalculator.calculate_volatility(prices)

        if volatility_pct < 10:
            volatility_class = "stable"
            volatility_label = "Stabil"
        elif volatility_pct <= 20:
            volatility_class = "normal"
            volatility_label = "Normal"
        else:
            volatility_class = "high"
            volatility_label = "Yüksek Volatilite"

        return {
            "volatility_pct": float(round(volatility_pct, 2)),
            "volatility_class": volatility_class,
            "volatility_label": volatility_label,
        }

    @staticmethod
    def generate_signal(prices: pd.Series) -> dict:
        clean_prices = prices.dropna()
        current_price = float(clean_prices.iloc[-1]) if len(clean_prices) else 0.0
        moving_average_20 = float(clean_prices.tail(20).mean()) if len(clean_prices) else 0.0
        var_95 = RiskCalculator.calculate_historical_var(clean_prices, 0.95) if len(clean_prices) >= 2 else 0.0

        if len(clean_prices) >= 2 and clean_prices.iloc[-1] > clean_prices.iloc[-2]:
            trend = "up"
        elif len(clean_prices) >= 2 and clean_prices.iloc[-1] < clean_prices.iloc[-2]:
            trend = "down"
        else:
            trend = "stable"

        signal = "HOLD"
        signal_strength = "medium"
        reasoning = "Fiyat ve hareketli ortalama dengede."

        if trend == "up" and var_95 < 0.02:
            signal = "STRONG BUY"
            signal_strength = "high"
            reasoning = "Trend yukarı ve VaR düşük olduğu için güçlü alım sinyali oluştu."
        elif trend == "down" and var_95 > 0.04:
            signal = "STRONG SELL"
            signal_strength = "high"
            reasoning = "Trend aşağı ve VaR yüksek olduğu için güçlü satış sinyali oluştu."
        elif current_price > moving_average_20:
            signal = "BUY"
            signal_strength = "medium"
            reasoning = "Güncel fiyat 20 günlük hareketli ortalamanın üzerinde."
        elif current_price < moving_average_20:
            signal = "SELL"
            signal_strength = "medium"
            reasoning = "Güncel fiyat 20 günlük hareketli ortalamanın altında."

        return {
            "signal": signal,
            "signal_strength": signal_strength,
            "current_price": current_price,
            "moving_average_20": moving_average_20,
            "reasoning": reasoning,
        }
