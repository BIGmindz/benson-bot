#!/usr/bin/env python3

import pandas as pd
from datetime import datetime, timedelta

# Read the signals file
df = pd.read_csv('benson_signals.csv')

# Convert timestamp to datetime
df['ts_utc'] = pd.to_datetime(df['ts_utc'])

# Filter for the 30-minute session (23:46 to 00:16 local, which is 03:46 to 04:16 UTC)
session_start = datetime(2025, 9, 17, 3, 46, 0)  # UTC time
session_end = datetime(2025, 9, 17, 4, 16, 0)

session_signals = df[(df['ts_utc'] >= session_start) & (df['ts_utc'] <= session_end)]

print('📊 30-MINUTE TRADING SESSION RESULTS')
print('=' * 60)
print(f'Session: 23:46 - 00:16 Local Time (03:46 - 04:16 UTC)')
print(f'Total Signals Generated: {len(session_signals)}')
print()

if len(session_signals) > 0:
    # Count signals by symbol
    signal_counts = session_signals['symbol'].value_counts()
    print('📈 SIGNALS BY SYMBOL:')
    for symbol, count in signal_counts.items():
        print(f'   {symbol}: {count} signals')

    print()

    # Count signal types
    signal_types = session_signals['signal'].value_counts()
    print('📊 SIGNAL TYPES:')
    for signal_type, count in signal_types.items():
        print(f'   {signal_type}: {count} signals')

    print()

    # Show RSI analysis
    print('📉 RSI ANALYSIS:')
    print(f'   Lowest RSI: {session_signals["rsi"].min():.1f}')
    print(f'   Highest RSI: {session_signals["rsi"].max():.1f}') 
    print(f'   Average RSI: {session_signals["rsi"].mean():.1f}')

    # Count how many were BUY signals (should have triggered trades)
    buy_signals = session_signals[session_signals['signal'] == 'BUY']
    print(f'   BUY Signals (attempted trades): {len(buy_signals)}')
    
    if len(buy_signals) > 0:
        print()
        print('🎯 TOP BUY SIGNALS (First 15):')
        for i, (_, row) in enumerate(buy_signals.head(15).iterrows()):
            time_str = row['ts_utc'].strftime('%H:%M:%S')
            price = float(row['price'])
            rsi = float(row['rsi'])
            print(f'   {i+1:2d}. {time_str} | {row["symbol"]:8s} | RSI {rsi:5.1f} | ${price:8.2f}')
    
    # Show some sample data
    print()
    print('📋 FIRST 10 SIGNALS:')
    sample = session_signals.head(10)
    for _, row in sample.iterrows():
        time_str = row['ts_utc'].strftime('%H:%M:%S')
        price = float(row['price'])
        rsi = float(row['rsi'])
        print(f'   {time_str} | {row["symbol"]:8s} | {row["signal"]:4s} | RSI {rsi:5.1f} | ${price:8.2f}')

else:
    print('❌ No signals found in this time range')
    print('Checking recent data...')
    recent_signals = df.tail(10)
    print('\n🔍 LAST 10 SIGNALS FROM FILE:')
    for _, row in recent_signals.iterrows():
        time_str = row['ts_utc'].strftime('%m-%d %H:%M:%S')
        price = float(row['price'])  
        rsi = float(row['rsi'])
        print(f'   {time_str} | {row["symbol"]:8s} | {row["signal"]:4s} | RSI {rsi:5.1f} | ${price:8.2f}')