# -*- coding: utf-8 -*-
"""
fritz_monitor.py - PRODUCTION VERSION
Author: ddiplas
Version: 4.0 - Updated for LogistikoCRM Webhook
Date: 2025-12-03

CHANGES v4.0:
- Uses new /api/fritz-webhook/ endpoint
- Token-based authentication
- Compatible with LogistikoCRM Phase 1
"""

import socket
import re
import logging
import requests
import json
from datetime import datetime, timezone as dt_timezone
from typing import Optional, Dict, Any
import time

# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================
class Config:
    # Fritz!Box
    FRITZ_HOST = 'fritz.box'
    FRITZ_PORT = 1012

    # CRM API - Uses new webhook endpoint
    CRM_BASE_URL = 'http://127.0.0.1:8000/accounting'
    API_TOKEN = 'change-this-token-in-production'  # Must match FRITZ_API_TOKEN in Django settings

    # Timeouts & Retries
    API_TIMEOUT = 30
    API_MAX_RETRIES = 3
    RETRY_DELAY = 2

    # Statistics
    STATS_INTERVAL = 600

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_now() -> datetime:
    """Get current timezone-aware datetime in UTC"""
    return datetime.now(dt_timezone.utc)

def format_datetime(dt: datetime) -> str:
    """Format datetime as ISO string with timezone"""
    return dt.isoformat()

# ============================================
# API CLIENT με TOKEN AUTH
# ============================================
class CRMAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {Config.API_TOKEN}',
        })

        self.stats = {
            'total_calls': 0,
            'answered': 0,
            'missed': 0,
            'outgoing': 0,
            'errors': 0,
            'tickets_created': 0,
            'start_time': get_now(),
            'last_call_time': None,
            'active_calls': 0
        }

    def _make_request(self, data: Dict, retries: int = Config.API_MAX_RETRIES) -> Optional[Dict]:
        """Make API request to webhook with retry logic"""
        url = f"{Config.CRM_BASE_URL}/api/fritz-webhook/"

        for attempt in range(retries):
            try:
                response = self.session.post(url, json=data, timeout=Config.API_TIMEOUT)

                if response.status_code == 401:
                    logger.error("❌ Authentication failed! Check API_TOKEN in Config")
                    self.stats['errors'] += 1
                    return None

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ Timeout on attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(Config.RETRY_DELAY)
                    continue
                logger.error(f"❌ Failed after {retries} attempts: Timeout")
                self.stats['errors'] += 1
                return None

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request failed: {e}")
                if attempt < retries - 1:
                    time.sleep(Config.RETRY_DELAY)
                    continue
                self.stats['errors'] += 1
                return None

        return None

    def create_call(self, call_data: Dict) -> Optional[Dict]:
        """Create new call record via webhook"""
        call_data['action'] = 'create'
        result = self._make_request(call_data)
        if result and result.get('success'):
            client_name = result.get('client_name') or 'Άγνωστος'
            logger.info(f"✅ Call created: #{result.get('id')} - {client_name}")
        else:
            logger.error(f"❌ Failed to create call in CRM")
        return result

    def update_call(self, call_id: int, update_data: Dict) -> Optional[Dict]:
        """Update existing call record via webhook"""
        update_data['action'] = 'update'
        update_data['id'] = call_id
        result = self._make_request(update_data)
        if result and result.get('success'):
            logger.info(f"✅ Call #{call_id} updated → {update_data.get('status')}")
            if update_data.get('status') == 'missed':
                self.stats['tickets_created'] += 1
                logger.info(f"🎫 Ticket created automatically for follow-up")
        else:
            logger.error(f"❌ Failed to update call #{call_id}")
        return result

    def print_stats(self):
        """Print current statistics"""
        uptime = get_now() - self.stats['start_time']
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)

        last_call = "Never"
        if self.stats['last_call_time']:
            delta = get_now() - self.stats['last_call_time']
            last_call = f"{int(delta.total_seconds())}s ago"

        logger.info("=" * 60)
        logger.info(f"📊 STATISTICS - Uptime: {hours}h {minutes}m")
        logger.info(f"Total Calls: {self.stats['total_calls']}")
        logger.info(f"  ✅ Answered: {self.stats['answered']}")
        logger.info(f"  ❌ Missed: {self.stats['missed']}")
        logger.info(f"  ☎️ Outgoing: {self.stats['outgoing']}")
        logger.info(f"Active Calls: {self.stats['active_calls']}")
        logger.info(f"🎫 Tickets Created: {self.stats['tickets_created']}")
        logger.info(f"CRM Errors: {self.stats['errors']}")
        logger.info(f"Last Call: {last_call}")
        logger.info("=" * 60)

# ============================================
# VOIP MONITOR
# ============================================
class VoIPMonitor:
    def __init__(self):
        self.api = CRMAPIClient()
        self.active_calls = {}
        self.last_stats_time = get_now()

    def connect_fritz(self) -> socket.socket:
        """Connect to Fritz!Box CallMonitor"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((Config.FRITZ_HOST, Config.FRITZ_PORT))
        logger.info(f"✅ Connected to Fritz!Box at {Config.FRITZ_HOST}:{Config.FRITZ_PORT}")
        return sock

    def parse_call_event(self, line: str) -> Optional[tuple]:
        """Parse Fritz!Box call event"""
        pattern = r'(\d{2}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2});(RING|CALL|CONNECT|DISCONNECT);(\d+);(.+);(.+);(.+);'
        match = re.match(pattern, line)
        if match:
            timestamp, event, connection_id, caller, called, line_id = match.groups()
            return event, connection_id, caller, called
        return None

    def generate_call_id(self, connection_id: str) -> str:
        """Generate unique call_id with timestamp"""
        timestamp = int(get_now().timestamp())
        return f"{connection_id}_{timestamp}"

    def handle_ring(self, connection_id: str, caller: str, called: str):
        """Handle incoming call ring"""
        logger.info(f"📞 INCOMING: {caller} → {called}")

        now = get_now()
        call_id = self.generate_call_id(connection_id)
        call_data = {
            'call_id': call_id,
            'phone_number': caller,
            'direction': 'incoming',
            'started_at': format_datetime(now)
        }

        result = self.api.create_call(call_data)
        if result and result.get('success'):
            self.active_calls[connection_id] = {
                'id': result.get('id'),
                'call_id': call_id,
                'phone_number': caller,
                'client_name': result.get('client_name') or 'Άγνωστος',
                'is_known': result.get('is_known', False),
                'direction': 'incoming',
                'started_at': now,
                'status': 'active'
            }
            self.api.stats['total_calls'] += 1
            self.api.stats['active_calls'] += 1
            self.api.stats['last_call_time'] = now

            client_info = f"👤 {result.get('client_name')}" if result.get('is_known') else "❓ Άγνωστος καλών"
            logger.info(f"   {client_info}")

            if (get_now() - self.last_stats_time).total_seconds() >= Config.STATS_INTERVAL:
                self.api.print_stats()
                self.last_stats_time = get_now()

    def handle_connect(self, connection_id: str):
        """Handle call answered"""
        if connection_id in self.active_calls:
            call = self.active_calls[connection_id]
            call['status'] = 'completed'
            self.api.stats['answered'] += 1
            logger.info(f"✅ ANSWERED: {call['phone_number']} ({call['client_name']})")

    def handle_disconnect(self, connection_id: str):
        """Handle call ended"""
        if connection_id not in self.active_calls:
            return

        call = self.active_calls[connection_id]
        now = get_now()
        duration = int((now - call['started_at']).total_seconds())

        if call['status'] == 'active':
            # Call was never answered → MISSED
            update_data = {
                'status': 'missed',
                'ended_at': format_datetime(now)
            }
            self.api.update_call(call['id'], update_data)
            self.api.stats['missed'] += 1
            logger.warning(f"❌ MISSED: {call['phone_number']} ({call['client_name']}) - rang {duration}s")
        else:
            # Call was answered → COMPLETED
            update_data = {
                'status': 'completed',
                'ended_at': format_datetime(now)
            }
            self.api.update_call(call['id'], update_data)
            logger.info(f"📴 ENDED: {call['phone_number']} - duration {duration}s")

        self.api.stats['active_calls'] -= 1
        del self.active_calls[connection_id]

    def handle_outgoing_call(self, connection_id: str, called: str):
        """Handle outgoing call"""
        logger.info(f"📞 OUTGOING: → {called}")

        now = get_now()
        call_id = self.generate_call_id(connection_id)
        call_data = {
            'call_id': call_id,
            'phone_number': called,
            'direction': 'outgoing',
            'started_at': format_datetime(now)
        }

        result = self.api.create_call(call_data)
        if result and result.get('success'):
            self.active_calls[connection_id] = {
                'id': result.get('id'),
                'call_id': call_id,
                'phone_number': called,
                'client_name': result.get('client_name') or 'Άγνωστος',
                'direction': 'outgoing',
                'started_at': now,
                'status': 'active'
            }
            self.api.stats['total_calls'] += 1
            self.api.stats['outgoing'] += 1
            self.api.stats['active_calls'] += 1
            self.api.stats['last_call_time'] = now

    def run(self):
        """Main monitoring loop"""
        logger.info("=" * 60)
        logger.info("🚀 Fritz!Box VoIP Monitor v4.0 - LogistikoCRM")
        logger.info(f"📡 Fritz: {Config.FRITZ_HOST}:{Config.FRITZ_PORT}")
        logger.info(f"🌐 CRM: {Config.CRM_BASE_URL}/api/fritz-webhook/")
        logger.info(f"🔐 Auth: Bearer Token")
        logger.info(f"🎫 Auto Tickets: Only for MISSED calls")
        logger.info("=" * 60)

        while True:
            try:
                sock = self.connect_fritz()

                while True:
                    data = sock.recv(1024).decode('utf-8').strip()
                    if not data:
                        continue

                    parsed = self.parse_call_event(data)
                    if not parsed:
                        continue

                    event, connection_id, caller, called = parsed

                    if event == 'RING':
                        self.handle_ring(connection_id, caller, called)
                    elif event == 'CALL':
                        self.handle_outgoing_call(connection_id, called)
                    elif event == 'CONNECT':
                        self.handle_connect(connection_id)
                    elif event == 'DISCONNECT':
                        self.handle_disconnect(connection_id)

            except KeyboardInterrupt:
                logger.info("\n👋 Shutting down gracefully...")
                self.api.print_stats()
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                logger.info("🔄 Reconnecting in 5 seconds...")
                time.sleep(5)

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    monitor = VoIPMonitor()
    monitor.run()
