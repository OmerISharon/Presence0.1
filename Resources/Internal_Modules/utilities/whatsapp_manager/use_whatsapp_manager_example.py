import os
from whatsapp_manager import WhatsAppManager, Build_Text

mgr = WhatsAppManager()

os.environ["TWILIO_ACCOUNT_SID"] = "AC3829091076702fb378c5fb925927a6d4"
os.environ["TWILIO_AUTH_TOKEN"] = "30da66168f2acdf9d8e68b907a077e7c"
os.environ["PIXELDRAIN_API_KEY"] = "0e4ed83a-b290-4b74-a695-b4ba5c2627db"

msg_text = Build_Text("RedNBlack", "Youtube, Instagram", language="heb", enable_options=False, 
                      extra_text="תודה והמשך יום נעים", media_file=fr"D:\2025\Projects\Presence\Presence0.1\Channels\RedNBlack\Clips_Archive\1_20250227_220432\1_20250227_220432.mp4")
msg_sid = mgr.Send_Whatsapp(
    from_whatsapp="whatsapp:+14155238886",
    to_whatsapp="whatsapp:+972546205035",
    text=msg_text
)

print("Message SID:", msg_sid)