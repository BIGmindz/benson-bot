#!/usr/bin/env python3
"""
Check current portfolio status
"""

from paper_portfolio import PaperTradingPortfolio
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

portfolio = PaperTradingPortfolio(config)
status = portfolio.get_portfolio_summary()

print("📊 Current Portfolio Status:")
print(status)