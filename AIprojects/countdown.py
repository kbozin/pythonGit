import calendar
import datetime


def get_future_date():
    while True:
        s = input("Enter a future date (YYYY-MM-DD): ").strip()
        try:
            dt = datetime.date.fromisoformat(s)
        except Exception:
            print("Invalid format. Please use YYYY-MM-DD.")
            continue
        today = datetime.date.today()
        if dt <= today:
            if dt == today:
                print("The date you entered is today; please enter a future date.")
            else:
                print("The date is in the past; please enter a future date.")
            continue
        return today, dt


def diff_ymd(today, future):
    y1, m1, d1 = today.year, today.month, today.day
    y2, m2, d2 = future.year, future.month, future.day
    # Borrow days if necessary
    if d2 < d1:
        m2 -= 1
        if m2 == 0:
            m2 = 12
            y2 -= 1
        days_in_prev_month = calendar.monthrange(y2, m2)[1]
        days = d2 + days_in_prev_month - d1
    else:
        days = d2 - d1
    # Borrow months if necessary
    if m2 < m1:
        m2 += 12
        y2 -= 1
    months = m2 - m1
    years = y2 - y1
    return years, months, days


def plural(n, word):
    return f"{n} {word}" + ("s" if n != 1 else "")


def format_parts(parts):
    if not parts:
        return "0 days"
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return parts[0] + " and " + parts[1]
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def main():
    today, future = get_future_date()
    years, months, days = diff_ymd(today, future)
    parts = []
    if years:
        parts.append(plural(years, "year"))
    if months:
        parts.append(plural(months, "month"))
    if days:
        parts.append(plural(days, "day"))
    desc = format_parts(parts)
    print(f"The future date {future.isoformat()} is {desc} from today.")


if __name__ == "__main__":
    main()
