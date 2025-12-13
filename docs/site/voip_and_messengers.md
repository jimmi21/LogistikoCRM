## VoIP Telephony Systems

D.P. Economy supports **two separate VoIP integrations** for different use cases:

| Feature | Zadarma (voip app) | Fritz!Box (accounting app) |
|---------|-------------------|---------------------------|
| **Purpose** | Click-to-call & webhook notifications | Office phone monitoring |
| **Location** | `/voip/` app | `/accounting/` + `fritz_monitor.py` |
| **Protocol** | REST API + Webhooks | TR-064 / CallMonitor port 1012 |
| **Call Initiation** | Yes (callback) | No (monitoring only) |
| **Auto-match Clients** | Contacts/Leads/Deals | ClientProfile |
| **Ticket Creation** | Manual | Automatic (missed calls) |

---

## 1. Zadarma VoIP (voip app)

The `voip/` app integrates with **Zadarma** cloud PBX service for:

- **Click-to-call**: Initiate calls directly from CRM via callback request
- **Webhook notifications**: Receive real-time call events (NOTIFY_END, NOTIFY_OUT_END, NOTIFY_RECORD)
- **Auto-matching**: Links calls to Contacts, Leads, and active Deals

### Configuration

Set credentials in `voip/settings.py`:

```python
SECRET_ZADARMA_KEY = 'your-api-key'
SECRET_ZADARMA = 'your-api-secret'

VOIP = [
    {
        'BACKEND': 'voip.backends.zadarmabackend.ZadarmaAPI',
        'PROVIDER': 'Zadarma',
        'IP': '185.45.152.42',  # Zadarma webhook source IP
        'OPTIONS': {
            'key': SECRET_ZADARMA_KEY,
            'secret': SECRET_ZADARMA
        }
    }
]
```

### Setup Steps

1. Obtain API credentials from [zadarma.com](https://zadarma.com)
2. Configure `voip/settings.py` with your credentials
3. Add Connection objects for users: `Admin > Voip > Connections`
4. Configure Zadarma PBX to send webhooks to: `https://yourdomain.com/voip/zd/`

### Endpoints

- `GET /voip/get-callback/` - List user's VoIP connections
- `POST /voip/get-callback/` - Initiate callback request
- `POST /voip/zd/` - Webhook receiver for Zadarma notifications

### Adding Other Providers

To integrate a different VoIP provider:

1. Create backend in `voip/backends/`
2. Add webhook handler in `voip/views/`
3. Add provider config to `VOIP` list in `voip/settings.py`

---

## 2. Fritz!Box VoIP (accounting app)

The Fritz!Box integration monitors **office phone calls** via the router's CallMonitor feature:

- **Call logging**: Records all incoming/outgoing calls
- **Auto-match clients**: Links calls to ClientProfile by phone number
- **Ticket creation**: Automatically creates tickets for missed calls (via Celery)
- **Call history**: Full audit trail with VoIPCallLog

### Architecture

```
Fritz!Box ─────► fritz_monitor.py ─────► /accounting/api/fritz-webhook/
  (port 1012)     (persistent script)         (Django endpoint)
```

### Configuration

Set environment variables:

```bash
# Fritz!Box connection
FRITZ_HOST=192.168.178.1  # or fritz.box
FRITZ_PORT=1012           # CallMonitor port

# API authentication
FRITZ_API_TOKEN=your-secure-token-here  # In webcrm/settings.py
```

### Setup Steps

1. Enable CallMonitor on Fritz!Box: dial `#96*5*` from a connected phone
2. Configure `fritz_monitor.py` with your Fritz!Box IP
3. Set `FRITZ_API_TOKEN` in settings for webhook authentication
4. Run `fritz_monitor.py` as a system service (systemd recommended)
5. Ensure Celery worker is running for missed call ticket creation

### Endpoints

- `POST /accounting/api/fritz-webhook/` - Receives call events from fritz_monitor.py

### Models

- **VoIPCall**: Stores call records (call_id, phone_number, direction, status, duration)
- **VoIPCallLog**: Audit trail of call state changes
- **Ticket**: Auto-created tickets linked to missed calls

---

## Choosing the Right System

| Use Case | Recommended System |
|----------|-------------------|
| Cloud-based PBX | Zadarma (voip app) |
| Office landline via Fritz!Box | Fritz!Box (accounting app) |
| Click-to-call from CRM | Zadarma (voip app) |
| Automatic missed call tickets | Fritz!Box (accounting app) |
| Call recording integration | Zadarma (voip app) |

Both systems can run simultaneously for hybrid setups.

---

## CRM integration with messengers

Django CRM has the ability to send messages via messengers such as Viber and WhatsApp.
To use this feature, these applications must be installed on the user's device.
