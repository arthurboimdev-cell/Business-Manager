import re


class TransactionUtils:
    """Utility class for transaction calculations"""

    @staticmethod
    def calculate_summary(transactions):
        """
        Calculate totals, balance, sold units, and average price.

        Args:
            transactions (list[dict]): List of transactions from DB.

        Returns:
            dict: {
                "total_income": float,
                "total_expense": float,
                "balance": float,
                "total_sold_units": int,
                "avg_price_per_unit": float
            }
        """
        total_income = 0
        total_expense = 0
        total_sold_units = 0
        total_income_sum = 0

        for t in transactions:
            t_type = t['transaction_type']
            t_total = float(t['total'])
            if t_type == 'income':
                total_income += t_total
                total_sold_units += t['quantity']
                total_income_sum += t_total
            else:
                total_expense += t_total

        balance = total_income - total_expense
        avg_price_per_unit = total_income_sum / total_sold_units if total_sold_units > 0 else 0

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "total_sold_units": total_sold_units,
            "avg_price_per_unit": avg_price_per_unit
        }

    @staticmethod
    def filter_by_month(transactions, year, month):
        """Return only transactions from a specific month"""
        return [t for t in transactions if t['transaction_date'].startswith(f"{year}-{month:02d}")]

    @staticmethod
    def filter_by_quarter(transactions, year, quarter):
        """Return transactions from a specific quarter (1-4)"""
        month_ranges = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
        start, end = month_ranges[quarter]
        return [t for t in transactions if t['transaction_date'].startswith(f"{year}-") and start <= int(t['transaction_date'][5:7]) <= end]

    @staticmethod
    def filter_by_year(transactions, year):
        """Return only transactions from a specific year"""
        return [t for t in transactions if t['transaction_date'].startswith(f"{year}-")]

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize user text:
        - Strip leading/trailing spaces
        - Collapse multiple spaces into one
        - Remove tabs/newlines
        """
        if not text:
            return ""

        # Replace tabs/newlines with space
        text = re.sub(r"[\t\n\r]+", " ", text)

        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @staticmethod
    def calculate_monthly_breakdown(transactions, year):
        """
        Groups transactions by month for a specific year.
        Returns a dict: {1: {'income': 0, 'expense': 0}, ...}
        """
        breakdown = {m: {'income': 0.0, 'expense': 0.0} for m in range(1, 13)}
        
        for t in transactions:
            # Date format expected: YYYY-MM-DD
            date_str = str(t['transaction_date'])
            if not date_str.startswith(str(year)):
                continue
                
            try:
                # Extract month (YYYY-MM-DD) -> index 5:7
                month = int(date_str.split('-')[1])
                amount = float(t['total'])
                t_type = t['transaction_type']
                
                if t_type == 'income':
                    breakdown[month]['income'] += amount
                else:
                    breakdown[month]['expense'] += amount
            except (ValueError, IndexError):
                continue
                
        return breakdown
