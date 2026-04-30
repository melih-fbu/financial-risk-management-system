from datetime import date

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.metals import MetalPrice, SimulationResult
from app.models.transaction import Transaction


class RiskCalculator:
    @staticmethod
    def calculate_daily_returns(prices: pd.Series) -> pd.Series:
        """
        Günlük getirileri hesaplar: (Bugünkü Fiyat / Dünkü Fiyat) - 1
        """
        return prices.pct_change().dropna()

    @staticmethod
    def calculate_historical_var(prices: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Geçmişe dayalı VaR (Historical Value at Risk) hesaplar.
        %95 güven düzeyi için en kötü %5'lik dilimi bulur.
        """
        returns = RiskCalculator.calculate_daily_returns(prices)
        if len(returns) < 2:
            return 0.0

        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(returns, var_percentile)
        return abs(float(var_value))

    @staticmethod
    def calculate_sharpe_ratio(prices: pd.Series, risk_free_rate: float = 0.02) -> float:
        returns = RiskCalculator.calculate_daily_returns(prices)
        if len(returns) < 2:
            return 0.0

        mean_return_annual = returns.mean() * 252
        std_return_annual = returns.std() * np.sqrt(252)
        if std_return_annual == 0 or np.isnan(std_return_annual):
            return 0.0

        sharpe_ratio = (mean_return_annual - risk_free_rate) / std_return_annual
        return float(sharpe_ratio)

    @staticmethod
    def calculate_max_drawdown(prices: pd.Series) -> float:
        clean_prices = prices.dropna()
        if len(clean_prices) < 2:
            return 0.0

        cumulative_max = clean_prices.cummax()
        drawdowns = (clean_prices - cumulative_max) / cumulative_max
        return float(drawdowns.min() * 100)

    @staticmethod
    def calculate_volatility(prices: pd.Series) -> float:
        returns = RiskCalculator.calculate_daily_returns(prices)
        if len(returns) < 2:
            return 0.0

        volatility = returns.std() * np.sqrt(252)
        return float(volatility * 100)

    @staticmethod
    def monte_carlo_simulation(prices: pd.Series, days: int = 30, simulations: int = 1000):
        clean_prices = prices.dropna()
        returns = RiskCalculator.calculate_daily_returns(clean_prices)

        if len(clean_prices) < 2 or len(returns) < 2:
            latest_price = float(clean_prices.iloc[-1]) if len(clean_prices) > 0 else 0.0
            fallback_path = [[latest_price] * (days + 1)]
            return {
                "mean_price": latest_price,
                "worst_case": latest_price,
                "best_case": latest_price,
                "all_simulations": fallback_path,
            }

        last_price = float(clean_prices.iloc[-1])
        mean_return = float(returns.mean())
        std_return = float(returns.std())

        all_paths = []
        final_prices = []

        for _ in range(simulations):
            random_returns = np.random.normal(mean_return, std_return, days)
            price_path = [last_price]

            for simulated_return in random_returns:
                next_price = price_path[-1] * (1 + simulated_return)
                price_path.append(float(next_price))

            all_paths.append(price_path)
            final_prices.append(price_path[-1])

        return {
            "mean_price": float(np.mean(final_prices)),
            "worst_case": float(np.percentile(final_prices, 5)),
            "best_case": float(np.percentile(final_prices, 95)),
            "all_simulations": all_paths,
        }

    @staticmethod
    def _find_price_entry(db: Session, metal_type: str, target_date: date):
        return (
            db.query(MetalPrice)
            .filter(
                MetalPrice.metal_type == metal_type,
                MetalPrice.date <= target_date,
            )
            .order_by(MetalPrice.date.desc())
            .first()
        )

    @staticmethod
    def _get_price_series(db: Session, metal_type: str) -> pd.Series:
        all_prices = (
            db.query(MetalPrice)
            .filter(MetalPrice.metal_type == metal_type)
            .order_by(MetalPrice.date.asc())
            .all()
        )
        return pd.Series([price.price_try for price in all_prices if price.price_try is not None])

    @staticmethod
    def _calculate_metal_position(
        db: Session,
        metal_type: str,
        initial_amount: float,
        start_date: date,
        end_date: date,
    ):
        start_price_entry = RiskCalculator._find_price_entry(db, metal_type, start_date)
        if not start_price_entry:
            return {"error": f"{start_date} tarihinde {metal_type} için fiyat bulunamadı."}

        end_price_entry = RiskCalculator._find_price_entry(db, metal_type, end_date)
        if not end_price_entry:
            return {"error": f"{end_date} tarihinde {metal_type} için fiyat bulunamadı."}

        price_series = RiskCalculator._get_price_series(db, metal_type)
        var_ratio_95 = RiskCalculator.calculate_historical_var(price_series, 0.95) if len(price_series) >= 2 else 0.0

        units_bought = initial_amount / start_price_entry.price_try
        final_amount = units_bought * end_price_entry.price_try
        profit_loss = final_amount - initial_amount

        return {
            "metal_type": metal_type,
            "initial_amount": float(initial_amount),
            "start_date": start_price_entry.date.isoformat(),
            "end_date": end_price_entry.date.isoformat(),
            "start_price_try": float(start_price_entry.price_try),
            "end_price_try": float(end_price_entry.price_try),
            "final_amount": float(final_amount),
            "profit_loss": float(profit_loss),
            "var_ratio_95": float(var_ratio_95),
            "var_95": float(var_ratio_95 * initial_amount),
        }

    @staticmethod
    def simulate_portfolio(db: Session, user_name: str, metal_type: str, initial_amount: float, start_date: date):
        """
        Belirli bir tarihte yapılan yatırımın güncel durumunu ve riskini simüle eder.
        """
        start_price_entry = RiskCalculator._find_price_entry(db, metal_type, start_date)
        if not start_price_entry:
            return {"error": f"{start_date} tarihinde {metal_type} için fiyat bulunamadı."}

        latest_price_entry = (
            db.query(MetalPrice)
            .filter(MetalPrice.metal_type == metal_type)
            .order_by(MetalPrice.date.desc())
            .first()
        )
        if not latest_price_entry:
            return {"error": f"{metal_type} için veritabanında hiç fiyat bulunamadı."}

        price_series = RiskCalculator._get_price_series(db, metal_type)
        if len(price_series) < 2:
            var_95 = 0.0
        else:
            var_95 = RiskCalculator.calculate_historical_var(price_series, 0.95)

        units_bought = initial_amount / start_price_entry.price_try
        final_amount = units_bought * latest_price_entry.price_try
        profit_loss = final_amount - initial_amount

        new_simulation = SimulationResult(
            user_name=user_name,
            metal_type=metal_type,
            initial_amount=initial_amount,
            final_amount=final_amount,
            profit_loss=profit_loss,
            var_95=var_95,
            start_date=start_date,
            end_date=latest_price_entry.date,
        )
        db.add(new_simulation)
        db.commit()
        db.refresh(new_simulation)

        return new_simulation

    @staticmethod
    def compare_metals(db: Session, initial_amount: float, start_date: date, end_date: date):
        if start_date > end_date:
            return {"error": "Başlangıç tarihi bitiş tarihinden büyük olamaz."}

        results = {}
        for metal_type in ["XAU", "XAG"]:
            position = RiskCalculator._calculate_metal_position(
                db=db,
                metal_type=metal_type,
                initial_amount=initial_amount,
                start_date=start_date,
                end_date=end_date,
            )
            if "error" in position:
                return position
            results[metal_type] = position

        better_metal = max(results.values(), key=lambda item: item["final_amount"])
        return {
            "initial_amount": float(initial_amount),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "results": results,
            "better_metal": better_metal["metal_type"],
        }

    @staticmethod
    def calculate_portfolio_risk(db: Session, customer_id: int):
        buy_transactions = (
            db.query(Transaction)
            .filter(
                Transaction.customer_id == customer_id,
                Transaction.transaction_type == "BUY",
            )
            .order_by(Transaction.date.asc(), Transaction.id.asc())
            .all()
        )

        if not buy_transactions:
            return {
                "customer_id": customer_id,
                "total_investment": 0.0,
                "current_value": 0.0,
                "profit_loss": 0.0,
                "var_95": 0.0,
                "buy_transaction_count": 0,
                "positions": [],
            }

        positions = []
        total_investment = 0.0
        current_value = 0.0
        total_var_95 = 0.0

        for transaction in buy_transactions:
            latest_price_entry = (
                db.query(MetalPrice)
                .filter(MetalPrice.metal_type == transaction.metal_type)
                .order_by(MetalPrice.date.desc())
                .first()
            )
            if not latest_price_entry:
                continue

            position = RiskCalculator._calculate_metal_position(
                db=db,
                metal_type=transaction.metal_type,
                initial_amount=transaction.amount_try,
                start_date=transaction.date,
                end_date=latest_price_entry.date,
            )
            if "error" in position:
                continue

            positions.append(
                {
                    "transaction_id": transaction.id,
                    "metal_type": transaction.metal_type,
                    "initial_amount": float(transaction.amount_try),
                    "final_amount": float(position["final_amount"]),
                    "profit_loss": float(position["profit_loss"]),
                    "var_95": float(position["var_95"]),
                    "start_date": transaction.date.isoformat(),
                    "end_date": position["end_date"],
                }
            )

            total_investment += float(transaction.amount_try)
            current_value += float(position["final_amount"])
            total_var_95 += float(position["var_95"])

        return {
            "customer_id": customer_id,
            "total_investment": float(total_investment),
            "current_value": float(current_value),
            "profit_loss": float(current_value - total_investment),
            "var_95": float(total_var_95),
            "buy_transaction_count": len(positions),
            "positions": positions,
        }
