# Monkey-patch the real SMTP library so no real emails go out
class DummySMTP:
    sent = []

    def __init__(self, host, port):
        DummySMTP.host = host
        DummySMTP.port = port

    def starttls(self): pass
    def login(self, user, pwd):
        DummySMTP.user = user
        DummySMTP.pwd  = pwd

    def send_message(self, msg):
        DummySMTP.sent.append({
            "from": msg["From"],
            "to":   msg["To"],
            "subject": msg["Subject"],
            "body": msg.get_content()
        })

    def __enter__(self): return self
    def __exit__(self, *args): pass
