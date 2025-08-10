import yfinance as yf

def get_taux_conversion():
    devises = {
        "PLN": "EURPLN=X", 
        "SEK": "EURSEK=X",
        "GBP": "EURGBP=X",
        "USD": "EURUSD=X",
        "EUR": None 
    }

    taux_conversion = {}
    for code_iso, ticker in devises.items():
        if ticker is None:
            taux_conversion[code_iso] = 1.0
        else:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                taux = data["Close"].iloc[0]
                taux_conversion[code_iso] = taux
            else:
                taux_conversion[code_iso] = None

    return taux_conversion
