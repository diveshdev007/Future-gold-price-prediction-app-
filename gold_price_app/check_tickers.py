import yfinance as yf

def check_tickers():
    print("Checking GC=F (Gold Futures)...")
    gc = yf.download("GC=F", period="5d")
    print(gc['Close'].tail())

    print("\nChecking SI=F (Silver Futures)...")
    si = yf.download("SI=F", period="5d")
    print(si['Close'].tail())
    
    print("\nChecking GLD (SPDR Gold Shares)...")
    gld = yf.download("GLD", period="5d")
    print(gld['Close'].tail())

if __name__ == "__main__":
    check_tickers()
