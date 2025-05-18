from __future__ import annotations

import urllib
"""
whatsapp_manager.py  –  v1.2  (Pixeldrain with API Key Auth)
---------------------------------------------------------------------
A small utility around Twilio's WhatsApp API for content previews:
  • Build a customer-friendly preview message
  • Send text + optional media to WhatsApp via Twilio
  • Poll for replies from customers

New in v1.2:
  • Pixeldrain uploads now use API Key authentication
  • Set PIXELDRAIN_API_KEY in your environment for uploads

Env vars required:
  TWILIO_ACCOUNT_SID    – your Twilio Account SID
  TWILIO_AUTH_TOKEN     – your Twilio Auth Token
  PIXELDRAIN_API_KEY    – your Pixeldrain API Key (password in HTTP Basic)

Install:
  pip install twilio requests
---------------------------------------------------------------------
Usage:
>>> from whatsapp_manager import WhatsAppManager, Build_Text
>>> mgr = WhatsAppManager()
>>> txt = Build_Text("Instagram", "🚀 Here's your preview.")
>>> sid = mgr.Send_Whatsapp(
...     from_whatsapp="whatsapp:+14155238886",
...     to_whatsapp="whatsapp:+972501234567",
...     text=txt,
...     media_file=r"D:\Videos\clip.mp4",
... )
>>> print("SID:", sid)
>>> reply = mgr.Get_Response(sid, timeout=120)
>>> print("Reply:", reply)
"""

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, TYPE_CHECKING

import requests
from requests.auth import HTTPBasicAuth

if TYPE_CHECKING:
    from twilio.rest import Client
else:
    try:
        from twilio.rest import Client  # pragma: no cover
    except ImportError:
        Client = None  # type: ignore

os.environ["TWILIO_ACCOUNT_SID"] = "AC3829091076702fb378c5fb925927a6d4"
os.environ["TWILIO_AUTH_TOKEN"] = "30da66168f2acdf9d8e68b907a077e7c"
os.environ["PIXELDRAIN_API_KEY"] = "0e4ed83a-b290-4b74-a695-b4ba5c2627db"

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------
class WhatsAppManagerError(Exception): pass
class CredentialsError(WhatsAppManagerError): pass
class MessageError(WhatsAppManagerError): pass
class MediaUploadError(WhatsAppManagerError): pass

# ------------------------------------------------------------------
# Public helper
# ------------------------------------------------------------------
def Build_Text(channel_name: str,
               platforms: str = "all",
               language: str = "eng",
               enable_options: bool = True,
               extra_text: Optional[str] = None,
               media_file: Optional[str] = None) -> str:
    """
    Compose a preview message in English (default) or Hebrew.
    """

    if language.lower() == "eng":
        tpl = (
            "*{channel}*\n"
            "*Platforms: {platforms}*\n\n"
            "Preview your content!"
        )
    elif language.lower() == "heb":
        tpl = (
            "{channel}\n"
            "פלטפורמות: {platforms}\n"
            "תצוגה מוקדמת של תוכן"
        )
    msg = tpl.format(channel=channel_name.strip(),
                     platforms=platforms.strip())
    
    if enable_options and "accept" not in msg.lower():
            if language.lower() == "eng":
                msg += (
                    "\n\nReply with *accept* to approve, *redo* to regenerate, or *cancel*."
                )
            elif language.lower() == "heb":
                msg += (
                    "\n\nאנא השב *מאשר* לאישור, *שוב* ליצירה מחדש, או *ביטול* לביטול היצירה"
                )
    
    if media_file:
        url = _ensure_https_url(media_file)
        msg += f"\n\n📎 Media file: {url}"

    if extra_text:
        msg += f"\n\n{extra_text}"

    logger.debug("Built message: %s", msg.replace("\n", " | "))
    return msg

# ------------------------------------------------------------------
# Main class
# ------------------------------------------------------------------
@dataclass
class WhatsAppManager:
    """Lightweight helper around Twilio's Python SDK with auto‑upload."""

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    if not account_sid:
        raise MediaUploadError("Set TWILIO_ACCOUNT_SID env-var")
    
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token:
        raise MediaUploadError("Set TWILIO_AUTH_TOKEN env-var")

    client: Optional["Client"] = field(init=False, default=None)

    def __post_init__(self) -> None:
        if not self.account_sid or not self.auth_token:
            raise CredentialsError("Twilio credentials missing.")
        if Client is None:
            raise CredentialsError("Install the 'twilio' package: pip install twilio")
        self.client = Client(self.account_sid, self.auth_token)
        logger.info("WhatsAppManager ready – SID %s…", self.account_sid[:6])

    def Send_Whatsapp(
        self,
        from_whatsapp: str,
        to_whatsapp: str,
        text: str,
    ) -> str:
        """Send a WhatsApp message via Twilio"""
        kwargs: Dict[str, str | List[str]] = {
            "from_": from_whatsapp,
            "to":   to_whatsapp,
            "body": text,
        }

        try:
            msg = self.client.messages.create(**kwargs)  # type: ignore
        except Exception as exc:
            logger.exception("Send_Whatsapp error")
            raise MessageError(str(exc))
        logger.info("Message sent | SID=%s", msg.sid)
        return msg.sid

# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------
def _ensure_https_url(path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    return _upload_pixeldrain(path_or_url)

import urllib.parse

def _upload_pixeldrain(path: str) -> str:
    """
    Upload a file to Pixeldrain and return a media-compatible direct link.
    """
    if not os.path.isfile(path):
        raise MediaUploadError(f"File not found: {path}")
    
    api_key = os.getenv("PIXELDRAIN_API_KEY")
    if not api_key:
        raise MediaUploadError("Set PIXELDRAIN_API_KEY env-var")

    filename = urllib.parse.quote(os.path.basename(path))
    url = f"https://pixeldrain.com/api/file/{filename}"

    logger.info("Uploading %s → Pixeldrain …", filename)

    try:
        with open(path, "rb") as fh:
            resp = requests.put(
                url,
                data=fh,
                auth=HTTPBasicAuth("", api_key),
                headers={"Content-Type": "application/octet-stream"},
                timeout=600,
            )
        resp.raise_for_status()
        data = resp.json()
        file_id = data["id"]
    except Exception as exc:
        logger.exception("Pixeldrain upload failed")
        raise MediaUploadError(str(exc)) from exc

    # ✅ Use ?download for raw access
    direct_url = f"https://pixeldrain.com/api/file/{file_id}"
    logger.info("Uploaded – %s", direct_url)
    return direct_url


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

__all__ = ["Build_Text", "WhatsAppManager"]