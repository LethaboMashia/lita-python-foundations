"LITA - DAY 1: Bytecode Autopsy"
import dis

def get_vat_rate():
    return 0.15

def make_pilot_quote(monthly_rate):
    def quote(months):
        return monthly_rate * months 
    return quote

def total_invoices(invoices):
    total = 0
    for amount in invoices:
        total = total + amount
    return total  

if __name__ == "__main__":
    print("===1. get_vat_rate ===")
    dis.dis(get_vat_rate)

    print("\n=== 2a. make_pilot_quote (outer) ===")
    dis.dis(make_pilot_quote)

    creative_tier_quote = make_pilot_quote(3500)
    print("\n=== 2b. make_pilot_quote (inner, captured  ) ===")
    dis.dis(creative_tier_quote)

    print("\n=== 3. total-invoices ===")
    dis.dis(total_invoices)