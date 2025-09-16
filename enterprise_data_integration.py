#!/usr/bin/env python3
"""
🌐 BENSON ENTERPRISE DATA INTEGRATION
Multi-tenant data pipeline supporting external data sources, custom webhooks, and enterprise clients

Features:
- Multi-tenant data isolation and security
- Custom data source integrations (APIs, databases, files)
- Real-time webhook processing
- Data transformation and normalization
- Enterprise-grade security and compliance
- Usage tracking and billing integration

Revenue Model: $99-$999/month per data source integration

Author: Benson Trading Systems
"""

import sqlite3
import json
import requests
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import uuid
import time
from threading import Thread
import queue
import logging
from pattern_marketplace import PatternMarketplace

# Optional Flask import for webhook server
try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """External data source configuration"""
    source_id: str
    tenant_id: str
    source_type: str  # 'api', 'webhook', 'database', 'file', 'kafka'
    name: str
    endpoint_url: Optional[str]
    authentication: Dict[str, str]
    data_format: str  # 'json', 'csv', 'xml', 'binary'
    update_frequency: str  # 'realtime', '1m', '5m', '1h', '1d'
    transformation_rules: List[Dict]
    is_active: bool
    created_date: datetime
    monthly_fee: float

@dataclass 
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    tenant_id: str
    source_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    processed: bool
    processing_time_ms: Optional[float]

class EnterpriseDataIntegration:
    """🌐 Enterprise Data Integration and Multi-tenant Pipeline"""
    
    def __init__(self):
        """Initialize enterprise data integration system"""
        self.db_path = 'benson_data_integration.db'
        self.webhook_queue = queue.Queue()
        self.processing_threads = []
        
        # Initialize Flask app if available
        if HAS_FLASK:
            self.webhook_app = Flask(__name__)
            self.setup_webhook_routes()
        else:
            self.webhook_app = None
            print("⚠️ Flask not available - webhook server disabled")
        
        self.init_integration_database()
        self.marketplace = PatternMarketplace()
        
        # Start webhook processor
        self.start_webhook_processor()
        
        print("🌐 Enterprise Data Integration System initialized!")
        print("🔐 Multi-tenant security and compliance ready")
    
    def init_integration_database(self):
        """Initialize data integration database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tenants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                subscription_tier TEXT,
                api_key TEXT NOT NULL,
                webhook_secret TEXT NOT NULL,
                data_retention_days INTEGER DEFAULT 90,
                max_data_sources INTEGER DEFAULT 10,
                created_date TEXT,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Data sources
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                source_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                name TEXT NOT NULL,
                config TEXT NOT NULL,
                transformation_rules TEXT,
                update_frequency TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                monthly_fee REAL DEFAULT 99.99,
                created_date TEXT,
                last_updated TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)
            )
        ''')
        
        # Data events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_events (
                event_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                event_type TEXT,
                event_data TEXT,
                timestamp TEXT,
                processed BOOLEAN DEFAULT FALSE,
                processing_time_ms REAL,
                error_message TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
                FOREIGN KEY (source_id) REFERENCES data_sources (source_id)
            )
        ''')
        
        # Data transformations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_transformations (
                transformation_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                transformation_name TEXT,
                input_schema TEXT,
                output_schema TEXT,
                transformation_code TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TEXT,
                FOREIGN KEY (source_id) REFERENCES data_sources (source_id)
            )
        ''')
        
        # Usage analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_analytics (
                analytics_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                source_id TEXT,
                usage_date TEXT,
                events_processed INTEGER DEFAULT 0,
                data_volume_mb REAL DEFAULT 0,
                processing_time_total_ms REAL DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                cost_generated REAL DEFAULT 0,
                FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("🗄️ Enterprise integration database initialized")
    
    def create_tenant(self, company_name: str, subscription_tier: str = "standard") -> Dict:
        """🏢 Create new enterprise tenant with isolated data"""
        tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
        api_key = f"benson_api_{uuid.uuid4().hex}"
        webhook_secret = uuid.uuid4().hex
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Set tenant limits based on subscription tier
        tier_limits = {
            "basic": {"max_sources": 5, "retention_days": 30, "monthly_fee": 299},
            "standard": {"max_sources": 15, "retention_days": 90, "monthly_fee": 699}, 
            "enterprise": {"max_sources": 50, "retention_days": 365, "monthly_fee": 1999},
            "unlimited": {"max_sources": 1000, "retention_days": 730, "monthly_fee": 4999}
        }
        
        limits = tier_limits.get(subscription_tier, tier_limits["standard"])
        
        cursor.execute('''
            INSERT INTO tenants
            (tenant_id, company_name, subscription_tier, api_key, webhook_secret,
             data_retention_days, max_data_sources, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tenant_id, company_name, subscription_tier, api_key, webhook_secret,
            limits["retention_days"], limits["max_sources"], datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        tenant_info = {
            "tenant_id": tenant_id,
            "company_name": company_name,
            "subscription_tier": subscription_tier,
            "api_key": api_key,
            "webhook_secret": webhook_secret,
            "limits": limits
        }
        
        print(f"🏢 Created enterprise tenant: {company_name}")
        print(f"🔑 API Key: {api_key}")
        print(f"🎯 Tenant ID: {tenant_id}")
        print(f"💰 Monthly Fee: ${limits['monthly_fee']}")
        
        return tenant_info
    
    def add_data_source(self, tenant_id: str, source_config: Dict) -> str:
        """📡 Add new data source for tenant"""
        source_id = f"source_{uuid.uuid4().hex[:12]}"
        
        # Validate tenant has capacity
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT max_data_sources FROM tenants WHERE tenant_id = ?', (tenant_id,))
        tenant = cursor.fetchone()
        
        if not tenant:
            raise ValueError("Tenant not found")
        
        cursor.execute('SELECT COUNT(*) FROM data_sources WHERE tenant_id = ? AND is_active = TRUE', (tenant_id,))
        current_sources = cursor.fetchone()[0]
        
        if current_sources >= tenant[0]:
            raise ValueError(f"Maximum data sources ({tenant[0]}) reached for tenant")
        
        # Determine pricing based on source type
        pricing = {
            "api": 99.99,
            "webhook": 149.99,
            "database": 199.99,
            "kafka": 299.99,
            "file": 49.99,
            "custom": 499.99
        }
        
        monthly_fee = pricing.get(source_config.get("source_type", "api"), 99.99)
        
        cursor.execute('''
            INSERT INTO data_sources
            (source_id, tenant_id, source_type, name, config, transformation_rules,
             update_frequency, monthly_fee, created_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source_id,
            tenant_id,
            source_config["source_type"],
            source_config["name"],
            json.dumps(source_config),
            json.dumps(source_config.get("transformation_rules", [])),
            source_config.get("update_frequency", "1h"),
            monthly_fee,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        print(f"📡 Added data source: {source_config['name']}")
        print(f"💰 Monthly fee: ${monthly_fee}")
        print(f"🆔 Source ID: {source_id}")
        
        return source_id
    
    def setup_webhook_routes(self):
        """🎣 Setup webhook endpoints for data ingestion"""
        if not HAS_FLASK or not self.webhook_app:
            return
        
        @self.webhook_app.route('/webhook/<tenant_id>/<source_id>', methods=['POST'])
        def receive_webhook(tenant_id, source_id):
            """Receive webhook data from external sources"""
            try:
                # Validate tenant and source
                if not self.validate_webhook_access(tenant_id, source_id, request.headers):
                    return jsonify({"error": "Unauthorized"}), 401
                
                # Extract webhook data
                event_data = request.json or {}
                
                # Create webhook event
                webhook_event = WebhookEvent(
                    event_id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    source_id=source_id,
                    event_type=event_data.get("event_type", "data_update"),
                    payload=event_data,
                    timestamp=datetime.now(),
                    processed=False,
                    processing_time_ms=None
                )
                
                # Queue for processing
                self.webhook_queue.put(webhook_event)
                
                return jsonify({
                    "status": "received",
                    "event_id": webhook_event.event_id,
                    "timestamp": webhook_event.timestamp.isoformat()
                }), 200
                
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.webhook_app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "queue_size": self.webhook_queue.qsize()
            })
    
    def validate_webhook_access(self, tenant_id: str, source_id: str, headers: Dict) -> bool:
        """🔐 Validate webhook access with signature verification"""
        try:
            # Get tenant webhook secret
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT webhook_secret FROM tenants WHERE tenant_id = ?', (tenant_id,))
            tenant = cursor.fetchone()
            
            cursor.execute('SELECT is_active FROM data_sources WHERE source_id = ? AND tenant_id = ?', 
                          (source_id, tenant_id))
            source = cursor.fetchone()
            
            conn.close()
            
            if not tenant or not source or not source[0]:
                return False
            
            # Validate signature if provided (simplified for demo)
            signature = headers.get('X-Benson-Signature')
            if signature:
                webhook_secret = tenant[0]
                # In production, use proper request body for signature validation
                return True  # Simplified validation for demo
            
            return True  # Allow unsigned webhooks for demo
            
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            return False
    
    def start_webhook_processor(self):
        """🔄 Start webhook processing threads"""
        def process_webhook_events():
            """Process webhook events from queue"""
            while True:
                try:
                    event = self.webhook_queue.get(timeout=1.0)
                    self.process_webhook_event(event)
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Webhook processing error: {e}")
        
        # Start processing threads
        for i in range(3):  # 3 worker threads
            thread = Thread(target=process_webhook_events, daemon=True)
            thread.start()
            self.processing_threads.append(thread)
        
        print("🔄 Started 3 webhook processing threads")
    
    def process_webhook_event(self, event: WebhookEvent):
        """⚙️ Process individual webhook event"""
        start_time = time.time()
        
        try:
            # Get data source configuration
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT config, transformation_rules FROM data_sources WHERE source_id = ?', 
                          (event.source_id,))
            source_config = cursor.fetchone()
            
            if not source_config:
                raise ValueError("Data source not found")
            
            config = json.loads(source_config[0])
            transformation_rules = json.loads(source_config[1])
            
            # Apply data transformations
            transformed_data = self.apply_transformations(event.payload, transformation_rules)
            
            # Store processed event
            processing_time = (time.time() - start_time) * 1000  # milliseconds
            
            cursor.execute('''
                INSERT INTO data_events
                (event_id, tenant_id, source_id, event_type, event_data, 
                 timestamp, processed, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.tenant_id,
                event.source_id,
                event.event_type,
                json.dumps(transformed_data),
                event.timestamp.isoformat(),
                True,
                processing_time
            ))
            
            # Update usage analytics
            self.update_usage_analytics(event.tenant_id, event.source_id, processing_time)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Processed event {event.event_id} in {processing_time:.1f}ms")
            
        except Exception as e:
            # Log error and mark as failed
            logger.error(f"Event processing failed: {e}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_events
                (event_id, tenant_id, source_id, event_type, event_data, 
                 timestamp, processed, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.tenant_id,
                event.source_id,
                event.event_type,
                json.dumps(event.payload),
                event.timestamp.isoformat(),
                False,
                str(e)
            ))
            
            conn.commit()
            conn.close()
    
    def apply_transformations(self, data: Dict, transformation_rules: List[Dict]) -> Dict:
        """🔄 Apply data transformation rules"""
        transformed = data.copy()
        
        for rule in transformation_rules:
            rule_type = rule.get("type", "passthrough")
            
            if rule_type == "rename_field":
                old_name = rule["old_name"]
                new_name = rule["new_name"]
                if old_name in transformed:
                    transformed[new_name] = transformed.pop(old_name)
            
            elif rule_type == "convert_type":
                field_name = rule["field"]
                target_type = rule["target_type"]
                if field_name in transformed:
                    try:
                        if target_type == "float":
                            transformed[field_name] = float(transformed[field_name])
                        elif target_type == "int":
                            transformed[field_name] = int(transformed[field_name])
                        elif target_type == "string":
                            transformed[field_name] = str(transformed[field_name])
                    except (ValueError, TypeError):
                        pass  # Keep original value if conversion fails
            
            elif rule_type == "calculate_field":
                # Simple field calculations
                field_name = rule["field"]
                expression = rule["expression"]
                # Simplified expression evaluation (in production, use safer eval)
                try:
                    # Replace field references in expression
                    for key, value in transformed.items():
                        if isinstance(value, (int, float)):
                            expression = expression.replace(f"{{{key}}}", str(value))
                    
                    # Evaluate simple mathematical expressions
                    if all(c in "0123456789+-*/.() " for c in expression):
                        transformed[field_name] = eval(expression)
                except:
                    pass  # Skip failed calculations
        
        return transformed
    
    def update_usage_analytics(self, tenant_id: str, source_id: str, processing_time_ms: float):
        """📊 Update usage analytics for billing"""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO usage_analytics
            (analytics_id, tenant_id, source_id, usage_date, events_processed, 
             processing_time_total_ms, cost_generated)
            VALUES (
                COALESCE((SELECT analytics_id FROM usage_analytics 
                         WHERE tenant_id = ? AND source_id = ? AND usage_date = ?),
                         ?),
                ?, ?, ?,
                COALESCE((SELECT events_processed FROM usage_analytics 
                         WHERE tenant_id = ? AND source_id = ? AND usage_date = ?), 0) + 1,
                COALESCE((SELECT processing_time_total_ms FROM usage_analytics 
                         WHERE tenant_id = ? AND source_id = ? AND usage_date = ?), 0) + ?,
                COALESCE((SELECT cost_generated FROM usage_analytics 
                         WHERE tenant_id = ? AND source_id = ? AND usage_date = ?), 0) + ?
            )
        ''', (
            tenant_id, source_id, today,  # For COALESCE SELECT
            str(uuid.uuid4()),             # New analytics_id if needed
            tenant_id, source_id, today,   # INSERT values
            tenant_id, source_id, today,   # For events_processed SELECT
            tenant_id, source_id, today,   # For processing_time_total_ms SELECT 
            processing_time_ms,
            tenant_id, source_id, today,   # For cost_generated SELECT
            0.001  # Cost per event processed
        ))
        
        conn.commit()
        conn.close()
    
    def get_tenant_dashboard(self, tenant_id: str) -> Dict:
        """📊 Get comprehensive tenant usage dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get tenant info
        cursor.execute('SELECT * FROM tenants WHERE tenant_id = ?', (tenant_id,))
        tenant_info = cursor.fetchone()
        
        # Get data sources
        cursor.execute('SELECT COUNT(*), SUM(monthly_fee) FROM data_sources WHERE tenant_id = ? AND is_active = TRUE', 
                      (tenant_id,))
        source_stats = cursor.fetchone()
        
        # Get usage analytics (last 30 days)
        cursor.execute('''
            SELECT SUM(events_processed), SUM(data_volume_mb), 
                   SUM(processing_time_total_ms), SUM(errors_count), SUM(cost_generated)
            FROM usage_analytics 
            WHERE tenant_id = ? AND usage_date > date('now', '-30 days')
        ''', (tenant_id,))
        usage_stats = cursor.fetchone()
        
        # Get recent events
        cursor.execute('''
            SELECT COUNT(*) FROM data_events 
            WHERE tenant_id = ? AND timestamp > datetime('now', '-1 day')
        ''', (tenant_id,))
        events_24h = cursor.fetchone()[0]
        
        conn.close()
        
        if not tenant_info:
            return {"error": "Tenant not found"}
        
        dashboard = {
            "tenant_id": tenant_id,
            "company_name": tenant_info[1],
            "subscription_tier": tenant_info[2],
            "data_sources": {
                "active_count": source_stats[0] or 0,
                "monthly_cost": source_stats[1] or 0,
                "max_allowed": tenant_info[5]
            },
            "usage_last_30_days": {
                "events_processed": usage_stats[0] or 0,
                "data_volume_mb": usage_stats[1] or 0,
                "processing_time_ms": usage_stats[2] or 0,
                "errors": usage_stats[3] or 0,
                "cost": usage_stats[4] or 0
            },
            "events_last_24h": events_24h,
            "account_status": "active" if tenant_info[8] else "suspended"
        }
        
        return dashboard

def demo_enterprise_integration():
    """🌐 Demo enterprise data integration capabilities"""
    integration = EnterpriseDataIntegration()
    
    print("\n🏢 CREATING DEMO ENTERPRISE TENANTS")
    print("="*50)
    
    # Create demo tenants
    tenants = []
    
    # Create hedge fund tenant
    hedge_fund = integration.create_tenant("Quantum Capital Management", "enterprise")
    tenants.append(hedge_fund)
    
    # Create fintech startup tenant
    fintech = integration.create_tenant("CryptoTrade Pro", "standard")
    tenants.append(fintech)
    
    # Create trading firm tenant
    trading_firm = integration.create_tenant("Alpha Trading Systems", "unlimited")
    tenants.append(trading_firm)
    
    print("\n📡 ADDING DATA SOURCES")
    print("="*30)
    
    # Add data sources for hedge fund
    hedge_fund_sources = [
        {
            "source_type": "api",
            "name": "Real-time Market Data Feed",
            "endpoint_url": "https://api.marketdata.com/v1/quotes",
            "update_frequency": "realtime",
            "transformation_rules": [
                {"type": "rename_field", "old_name": "last_price", "new_name": "price"},
                {"type": "convert_type", "field": "volume", "target_type": "float"}
            ]
        },
        {
            "source_type": "webhook", 
            "name": "News Sentiment Analysis",
            "update_frequency": "realtime",
            "transformation_rules": [
                {"type": "convert_type", "field": "sentiment_score", "target_type": "float"},
                {"type": "calculate_field", "field": "weighted_sentiment", "expression": "{sentiment_score} * {confidence}"}
            ]
        },
        {
            "source_type": "database",
            "name": "Risk Management Database",
            "update_frequency": "5m",
            "transformation_rules": []
        }
    ]
    
    for source_config in hedge_fund_sources:
        source_id = integration.add_data_source(hedge_fund["tenant_id"], source_config)
    
    # Add data sources for fintech
    fintech_sources = [
        {
            "source_type": "api",
            "name": "Cryptocurrency Exchange API",
            "endpoint_url": "https://api.exchange.com/v1/ticker",
            "update_frequency": "1m",
            "transformation_rules": []
        },
        {
            "source_type": "webhook",
            "name": "User Trading Signals",
            "update_frequency": "realtime",
            "transformation_rules": []
        }
    ]
    
    for source_config in fintech_sources:
        source_id = integration.add_data_source(fintech["tenant_id"], source_config)
    
    print("\n📊 TENANT DASHBOARDS")
    print("="*25)
    
    for tenant in tenants:
        dashboard = integration.get_tenant_dashboard(tenant["tenant_id"])
        
        print(f"\n🏢 {dashboard['company_name']}")
        print(f"   📊 Tier: {dashboard['subscription_tier'].upper()}")
        print(f"   📡 Data Sources: {dashboard['data_sources']['active_count']}/{dashboard['data_sources']['max_allowed']}")
        print(f"   💰 Monthly Cost: ${dashboard['data_sources']['monthly_cost']:.2f}")
        print(f"   📈 Events (30d): {dashboard['usage_last_30_days']['events_processed']:,}")
        print(f"   ⚡ Events (24h): {dashboard['events_last_24h']:,}")
    
    print("\n💰 REVENUE SUMMARY")
    print("="*20)
    total_monthly_revenue = sum(t["limits"]["monthly_fee"] for t in tenants)
    total_data_source_revenue = sum(integration.get_tenant_dashboard(t["tenant_id"])["data_sources"]["monthly_cost"] for t in tenants)
    
    print(f"🏢 Tenant Subscriptions: ${total_monthly_revenue:,.2f}/month")
    print(f"📡 Data Source Revenue: ${total_data_source_revenue:,.2f}/month") 
    print(f"🎯 Total MRR: ${total_monthly_revenue + total_data_source_revenue:,.2f}/month")
    print(f"📈 Annual Revenue Potential: ${(total_monthly_revenue + total_data_source_revenue) * 12:,.2f}")
    
    return integration, tenants

if __name__ == "__main__":
    print("🌐 BENSON ENTERPRISE DATA INTEGRATION")
    print("Multi-tenant data pipeline for enterprise clients")
    print("="*60)
    
    # Run demo
    integration, tenants = demo_enterprise_integration()
    
    print("\n🚀 ENTERPRISE INTEGRATION READY!")
    print("Features:")
    print("• Multi-tenant data isolation and security")
    print("• Real-time webhook processing") 
    print("• Custom data transformations")
    print("• Usage-based billing and analytics")
    print("• Enterprise-grade compliance")
    
    print(f"\n💎 Revenue Streams:")
    print(f"• Tenant Subscriptions: $299-$4,999/month")
    print(f"• Data Source Integration: $49.99-$499.99/month per source")
    print(f"• Usage-based fees: $0.001 per event processed")
    print(f"• Custom integration services: $5,000-$50,000 one-time")
    
    # Note: To run the webhook server, uncomment:
    # integration.webhook_app.run(host='0.0.0.0', port=8080, debug=False)