from datetime import date, datetime, timedelta
from decimal import Decimal

from src.domain.entities.bondholder import BondHolder


class AnalyticsService:
    INTERVAL_THRESHOLDS = [
        (30, timedelta(days=5)),
        (90, timedelta(days=15)),
        (180, timedelta(weeks=2)),
        (365, timedelta(weeks=4)),
    ]
    DEFAULT_INTERVAL = timedelta(days=30)

    def get_equity_history(
        self, bondholder_data: list[tuple[BondHolder, Decimal]]
    ) -> list[tuple[date, Decimal]]:
        bh_face_value = {bh.id: fv for bh, fv in bondholder_data}
        bondholders = [bh for bh, _ in bondholder_data]
        
        sorted_bhs = sorted(bondholders, key=lambda x: x.purchase_date)
        
        first_date = sorted_bhs[0].purchase_date
        last_date = datetime.now().date()

        timeline = self._determine_time_interval(first_date, last_date)
        points = self._find_timeline_points(first_date, last_date, timeline)
        
        history_equity: list[tuple[date, Decimal]] = []
        current_equity = Decimal(0)
        bh_index = 0
        
        for date_point in points:
            while bh_index < len(sorted_bhs) and sorted_bhs[bh_index].purchase_date <= date_point:
                bh = sorted_bhs[bh_index]
                current_equity += bh.quantity * bh_face_value[bh.id]
                bh_index += 1

            history_equity.append((date_point, current_equity))
        return history_equity

    def _determine_time_interval(self, first_date: date, last_date: date) -> timedelta:
        days = (last_date - first_date).days
        for threshold, interval in self.INTERVAL_THRESHOLDS:
            if days <= threshold:
                return interval
        return self.DEFAULT_INTERVAL

    def _find_timeline_points(
        self, first_date: date, last_date: date, interval: timedelta
    ) -> list[date]:
        points = []
        current_date = first_date
        while current_date <= last_date:
            points.append(current_date)
            current_date += interval
        if points[-1] != last_date:
            points.append(last_date)
        return points
