import pandas as pd
from data_loader import load_data
from model import train_model, predict_specific_date
from analytics import get_monthly_stats, get_yearly_analysis
from datetime import date

def test_system():
    print("1. Testing Data Loading...")
    df = load_data("GC=F", period="1y")
    if df.empty:
        print("❌ Data loading failed.")
        return
    print(f"✅ Data loaded: {len(df)} rows.")
    
    print("\n2. Testing Model Training...")
    try:
        model = train_model(df)
        print("✅ Model trained successfully.")
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        return

    print("\n3. Testing Prediction...")
    try:
        target_date = str(date.today())
        pred, low, high = predict_specific_date(model, target_date)
        print(f"✅ Prediction for {target_date}: {pred:.2f} (Range: {low:.2f} - {high:.2f})")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")

    print("\n4. Testing Analytics...")
    try:
        # Monthly
        stats, _ = get_monthly_stats(df, "January", date.today().year)
        if stats:
            print(f"✅ Monthly Stats (Jan {date.today().year}): {stats['trend']}")
        else:
            print(f"⚠️ No data for Jan {date.today().year} (Expected if early in year)")
            
        # Yearly
        res, summary = get_yearly_analysis(df, date.today().year - 1)
        if not res.empty:
            print(f"✅ Yearly Analysis ({date.today().year - 1}): Best Month - {summary['best_month']}")
        else:
            print("⚠️ No yearly data found.")
            
    except Exception as e:
        print(f"❌ Analytics failed: {e}")

if __name__ == "__main__":
    test_system()
