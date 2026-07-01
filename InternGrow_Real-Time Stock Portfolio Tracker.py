"""
Real-Time Stock Portfolio Tracker
==================================
Features:
- User-defined asset quantities (ticker -> shares held)
- Live market pricing fetched via the yfinance library (no hardcoded prices)
- Portfolio valuation: current value, cost basis, gain/loss, % allocation
- Daily summary exported to a structured, formula-driven Excel workbook

Requirements:
    pip install yfinance openpyxl

Usage:
    python portfolio_tracker.py
"""

import sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    sys.exit("Missing dependency. Install it with:\n    pip install yfinance")

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    sys.exit("Missing dependency. Install it with:\n    pip install openpyxl")


# ----------------------------------------------------------------------
# 1. User-defined holdings: ticker -> (shares, avg_cost_per_share)
#    Edit this dictionary (or wire it up to CLI/file input) with your
#    actual portfolio. avg_cost_per_share is what YOU paid, used to
#    calculate gain/loss - it is NOT a market price.
# ----------------------------------------------------------------------
HOLDINGS = {
    "AAPL": {"shares": 10, "avg_cost": 165.00},
    "MSFT": {"shares": 5,  "avg_cost": 310.00},
    "GOOGL": {"shares": 8, "avg_cost": 128.00},
    "TSLA": {"shares": 4,  "avg_cost": 220.00},
    "AMZN": {"shares": 6,  "avg_cost": 140.00},
}


def get_live_prices(tickers):
    """
    Fetch current market prices for a list of tickers using yfinance.
    Returns a dict: ticker -> {price, name, currency, day_change_pct}
    Falls back gracefully (None values) for any ticker that fails.
    """
    prices = {}
    data = yf.Tickers(" ".join(tickers))

    for ticker in tickers:
        try:
            info = data.tickers[ticker].fast_info
            price = info.get("last_price") if hasattr(info, "get") else info.last_price
            prev_close = info.get("previous_close") if hasattr(info, "get") else info.previous_close
            currency = info.get("currency") if hasattr(info, "get") else getattr(info, "currency", "USD")

            day_change_pct = None
            if price is not None and prev_close:
                day_change_pct = ((price - prev_close) / prev_close) * 100

            try:
                long_name = data.tickers[ticker].info.get("shortName", ticker)
            except Exception:
                long_name = ticker

            prices[ticker] = {
                "price": round(price, 2) if price is not None else None,
                "name": long_name,
                "currency": currency or "USD",
                "day_change_pct": round(day_change_pct, 2) if day_change_pct is not None else None,
            }
        except Exception as e:
            print(f"  Warning: could not fetch live price for {ticker} ({e})")
            prices[ticker] = {"price": None, "name": ticker, "currency": "USD", "day_change_pct": None}

    return prices


def build_portfolio_rows(holdings, live_prices):
    """Combine user holdings with live prices into row dicts for display/export."""
    rows = []
    for ticker, pos in holdings.items():
        market = live_prices.get(ticker, {})
        price = market.get("price")
        shares = pos["shares"]
        avg_cost = pos["avg_cost"]

        current_value = round(price * shares, 2) if price is not None else None
        cost_basis = round(avg_cost * shares, 2)
        gain_loss = round(current_value - cost_basis, 2) if current_value is not None else None
        gain_loss_pct = round((gain_loss / cost_basis) * 100, 2) if gain_loss is not None and cost_basis else None

        rows.append({
            "ticker": ticker,
            "name": market.get("name", ticker),
            "shares": shares,
            "avg_cost": avg_cost,
            "price": price,
            "currency": market.get("currency", "USD"),
            "day_change_pct": market.get("day_change_pct"),
            "current_value": current_value,
            "cost_basis": cost_basis,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
        })
    return rows


def print_portfolio_summary(rows):
    total_value = sum(r["current_value"] for r in rows if r["current_value"] is not None)

    print("\n" + "=" * 90)
    print(f" PORTFOLIO SUMMARY — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 90)
    header = f"{'Ticker':<8}{'Price':>10}{'Day %':>9}{'Shares':>9}{'Value':>14}{'Gain/Loss':>14}{'Alloc %':>10}"
    print(header)
    print("-" * 90)

    for r in rows:
        if r["price"] is None:
            print(f"{r['ticker']:<8}{'N/A':>10}")
            continue
        alloc_pct = round((r["current_value"] / total_value) * 100, 2) if total_value else 0
        day_chg = f"{r['day_change_pct']:+.2f}%" if r["day_change_pct"] is not None else "N/A"
        gain_str = f"{r['gain_loss']:+,.2f}"
        print(f"{r['ticker']:<8}{r['price']:>10,.2f}{day_chg:>9}{r['shares']:>9}"
              f"{r['current_value']:>14,.2f}{gain_str:>14}{alloc_pct:>9.2f}%")

    print("-" * 90)
    print(f"{'TOTAL':<8}{'':>10}{'':>9}{'':>9}{total_value:>14,.2f}")
    print("=" * 90)


def export_to_excel(rows, filepath):
    """Export a structured, formula-driven daily summary to Excel via openpyxl."""
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Portfolio Summary"

    bold_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", start_color="1F4E78")
    input_font = Font(color="0000FF")          # blue = hardcoded inputs
    calc_font = Font(color="000000")           # black = formulas
    total_fill = PatternFill("solid", start_color="D9E1F2")
    thin = Side(style="thin", color="B7B7B7")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center")

    # --- Title ---
    sheet.merge_cells("A1:J1")
    sheet["A1"] = f"Portfolio Daily Summary — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    sheet["A1"].font = Font(bold=True, size=14)

    # --- Header row ---
    headers = ["Ticker", "Name", "Shares", "Avg Cost", "Live Price",
               "Currency", "Day Chg %", "Current Value", "Cost Basis",
               "Gain/Loss", "Gain/Loss %", "Allocation %"]
    header_row = 3
    for col, title in enumerate(headers, start=1):
        cell = sheet.cell(row=header_row, column=col, value=title)
        cell.font = bold_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    first_data_row = header_row + 1
    n = len(rows)
    last_data_row = first_data_row + n - 1

    for i, r in enumerate(rows):
        row_num = first_data_row + i

        sheet.cell(row=row_num, column=1, value=r["ticker"]).font = input_font
        sheet.cell(row=row_num, column=2, value=r["name"])
        sheet.cell(row=row_num, column=3, value=r["shares"]).font = input_font
        sheet.cell(row=row_num, column=4, value=r["avg_cost"]).font = input_font
        sheet.cell(row=row_num, column=5, value=r["price"] if r["price"] is not None else "N/A").font = input_font
        sheet.cell(row=row_num, column=6, value=r["currency"])
        sheet.cell(row=row_num, column=7,
                    value=(r["day_change_pct"] / 100) if r["day_change_pct"] is not None else "N/A")

        # Formulas (calculated in Excel, not hardcoded from Python)
        col_shares = f"C{row_num}"
        col_avgcost = f"D{row_num}"
        col_price = f"E{row_num}"

        current_value_cell = sheet.cell(row=row_num, column=8, value=f"=IFERROR({col_price}*{col_shares},\"N/A\")")
        cost_basis_cell = sheet.cell(row=row_num, column=9, value=f"={col_avgcost}*{col_shares}")
        gain_loss_cell = sheet.cell(row=row_num, column=10, value=f"=IFERROR(H{row_num}-I{row_num},\"N/A\")")
        gain_pct_cell = sheet.cell(row=row_num, column=11,
                                     value=f"=IFERROR(J{row_num}/I{row_num},\"N/A\")")
        alloc_cell = sheet.cell(row=row_num, column=12,
                                  value=f"=IFERROR(H{row_num}/H${last_data_row + 2},\"N/A\")")

        for c in (current_value_cell, cost_basis_cell, gain_loss_cell, gain_pct_cell, alloc_cell):
            c.font = calc_font

        # Number formats
        sheet.cell(row=row_num, column=4).number_format = '$#,##0.00'
        sheet.cell(row=row_num, column=5).number_format = '$#,##0.00'
        sheet.cell(row=row_num, column=7).number_format = '0.00%;(0.00%);-'
        sheet.cell(row=row_num, column=8).number_format = '$#,##0.00'
        sheet.cell(row=row_num, column=9).number_format = '$#,##0.00'
        sheet.cell(row=row_num, column=10).number_format = '$#,##0.00;($#,##0.00);-'
        sheet.cell(row=row_num, column=11).number_format = '0.00%;(0.00%);-'
        sheet.cell(row=row_num, column=12).number_format = '0.00%'

        for col in range(1, 13):
            sheet.cell(row=row_num, column=col).border = border

    # --- Totals row ---
    total_row = last_data_row + 2
    sheet.cell(row=total_row, column=1, value="TOTAL").font = Font(bold=True)
    sheet.cell(row=total_row, column=1).fill = total_fill

    total_value_cell = sheet.cell(row=total_row, column=8, value=f"=SUM(H{first_data_row}:H{last_data_row})")
    total_cost_cell = sheet.cell(row=total_row, column=9, value=f"=SUM(I{first_data_row}:I{last_data_row})")
    total_gain_cell = sheet.cell(row=total_row, column=10, value=f"=H{total_row}-I{total_row}")
    total_gain_pct_cell = sheet.cell(row=total_row, column=11, value=f"=IFERROR(J{total_row}/I{total_row},\"N/A\")")
    total_alloc_cell = sheet.cell(row=total_row, column=12, value=f"=SUM(L{first_data_row}:L{last_data_row})")

    for c in (total_value_cell, total_cost_cell, total_gain_cell, total_gain_pct_cell, total_alloc_cell):
        c.font = Font(bold=True)
        c.fill = total_fill

    sheet.cell(row=total_row, column=8).number_format = '$#,##0.00'
    sheet.cell(row=total_row, column=9).number_format = '$#,##0.00'
    sheet.cell(row=total_row, column=10).number_format = '$#,##0.00;($#,##0.00);-'
    sheet.cell(row=total_row, column=11).number_format = '0.00%;(0.00%);-'
    sheet.cell(row=total_row, column=12).number_format = '0.00%'

    for col in range(1, 13):
        sheet.cell(row=total_row, column=col).border = border

    # --- Column widths & font ---
    widths = [10, 24, 9, 11, 12, 10, 11, 15, 14, 14, 12, 12]
    for i, w in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(i)].width = w

    for row in sheet.iter_rows(min_row=1, max_row=total_row, min_col=1, max_col=12):
        for cell in row:
            if cell.font.name != "Arial":
                cell.font = Font(
                    name="Arial",
                    bold=cell.font.bold,
                    color=cell.font.color,
                    size=14 if cell.row == 1 else 11,
                )

    wb.save(filepath)
    print(f"\nExcel summary saved to: {filepath}")


def main():
    tickers = list(HOLDINGS.keys())
    print(f"Fetching live prices for: {', '.join(tickers)} ...")
    live_prices = get_live_prices(tickers)

    rows = build_portfolio_rows(HOLDINGS, live_prices)
    print_portfolio_summary(rows)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = f"portfolio_summary_{date_str}.xlsx"
    export_to_excel(rows, filepath)


if __name__ == "__main__":
    main()