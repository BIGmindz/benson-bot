#!/usr/bin/env python3
"""
Loss Analysis Tool - Analyze trading losses and risk management
"""

import json

# Analyze losses from the latest 4-hour session
with open('rapid_training_results_rapid_training_1758024233.json', 'r') as f:
    data = json.load(f)

trades = data.get('trade_history', [])
total_trades = len(trades)
losses = []
wins = []

print('📊 LOSS ANALYSIS - 4-Hour Session')
print('='*50)

for i, trade in enumerate(trades):
    profit = trade.get('profit', 0)
    if profit < 0:
        losses.append({
            'trade_num': i+1,
            'symbol': trade.get('symbol', 'N/A'),
            'profit': profit,
            'confidence': trade.get('confidence', 0),
            'position_size': trade.get('position_size', 0)
        })
    elif profit > 0:
        wins.append(profit)

print(f'Total Trades: {total_trades}')
print(f'Losing Trades: {len(losses)}')
print(f'Winning Trades: {len(wins)}')
print(f'Win Rate: {len(wins)/total_trades*100:.1f}%')
print(f'Loss Rate: {len(losses)/total_trades*100:.1f}%')

if losses:
    total_losses = sum(l['profit'] for l in losses)
    avg_loss = total_losses / len(losses)
    max_loss = min(l['profit'] for l in losses)
    
    print(f'\n💸 LOSS METRICS:')
    print(f'Total Losses: ${total_losses:.2f}')
    print(f'Average Loss: ${avg_loss:.2f}')
    print(f'Largest Loss: ${max_loss:.2f}')
    
    # Worst losses
    worst_losses = sorted(losses, key=lambda x: x['profit'])[:5]
    print(f'\n🔴 TOP 5 WORST LOSSES:')
    for loss in worst_losses:
        print(f'  Trade #{loss["trade_num"]}: {loss["symbol"]} - ${loss["profit"]:.2f} (Conf: {loss["confidence"]:.1f}%, Size: {loss["position_size"]*100:.1f}%)')

    # Loss by confidence analysis
    high_conf_losses = [l for l in losses if l['confidence'] >= 80]
    medium_conf_losses = [l for l in losses if 60 <= l['confidence'] < 80]
    low_conf_losses = [l for l in losses if l['confidence'] < 60]
    
    print(f'\n📈 LOSS BY CONFIDENCE:')
    print(f'High Confidence (≥80%): {len(high_conf_losses)} losses, ${sum(l["profit"] for l in high_conf_losses):.2f}')
    print(f'Medium Confidence (60-79%): {len(medium_conf_losses)} losses, ${sum(l["profit"] for l in medium_conf_losses):.2f}')
    print(f'Low Confidence (<60%): {len(low_conf_losses)} losses, ${sum(l["profit"] for l in low_conf_losses):.2f}')

if wins:
    total_wins = sum(wins)
    avg_win = total_wins / len(wins)
    max_win = max(wins)
    
    print(f'\n💰 WIN METRICS:')
    print(f'Total Wins: ${total_wins:.2f}')
    print(f'Average Win: ${avg_win:.2f}')
    print(f'Largest Win: ${max_win:.2f}')
    
    if losses:
        print(f'Win/Loss Ratio: {avg_win/abs(avg_loss):.2f}:1')
        print(f'Total P&L: ${total_wins + total_losses:.2f}')

# Risk management analysis
print(f'\n⚖️ RISK MANAGEMENT:')
large_losses = [l for l in losses if l['profit'] < -2.0]  # Losses > $2
print(f'Large Losses (>$2): {len(large_losses)}')

if large_losses:
    print('Large Loss Details:')
    for loss in large_losses:
        print(f'  ${loss["profit"]:.2f} - {loss["symbol"]} (Conf: {loss["confidence"]:.1f}%)')

# Position sizing effectiveness
small_pos_losses = [l for l in losses if l['position_size'] < 0.1]  # <10% positions
large_pos_losses = [l for l in losses if l['position_size'] >= 0.1]  # ≥10% positions

print(f'\nPosition Size Analysis:')
print(f'Small Position Losses (<10%): {len(small_pos_losses)}, Total: ${sum(l["profit"] for l in small_pos_losses):.2f}')
print(f'Large Position Losses (≥10%): {len(large_pos_losses)}, Total: ${sum(l["profit"] for l in large_pos_losses):.2f}')