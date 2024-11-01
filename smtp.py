import ssl
import os
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword

# Class for handling incoming SMTP requests
class SMTPHandler:
    def __init__(self, domain, check_id, callback) -> None:
        self.domain = domain
        self.callback = callback
        self.check_id = check_id
    
    # Handle address
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Forbid using non-related from addresses
        from_addr = envelope.mail_from.split("@")
        if len(from_addr) != 2 or from_addr[1] != self.domain:
            return "550 Can not send messages as '{}'!".format("@".join(from_addr))
        # Check target address and add it to the list
        to_addr = address.split("@")
        if len(to_addr) != 2:
            return "550 Incorrect target address: '{}'".format("@".join(to_addr))
        if not self.check_id(address):
            return "550 Target address not found: '{}'".format(address)
        envelope.rcpt_tos.append(address)
        # Return ok
        return '250 OK'

    # Handle incoming data
    async def handle_DATA(self, server, session, envelope):
        # Extract source and target addresses
        source_email = envelope.mail_from
        target_emails = envelope.rcpt_tos
        # Dummy data
        subject = "Undefined"
        message = ""
        # Loop through data line by line
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            # Remove trailing spaces
            ln = ln.strip()
            # Extract meta
            meta = ln.split(":")
            # Save subject
            if len(meta) > 1 and meta[0] == "Subject":
                subject = meta[1].strip()
                continue
            # Ignore other meta and empty lines
            elif len(meta) > 1 or len(ln) < 1:
                continue
            # Write message
            message += "\n{}".format(ln.strip())
        message = message.rstrip("\n")
        # Forward message data to callback function
        await self.callback(
            source = source_email, 
            targets = target_emails,
            subject = subject,
            message = message
        )
        # Return ok response
        return '250 Message accepted for delivery'

# SMTP authenticator class
class SMTPAuthenticator:
    def __init__(self, users):
        self.users = users
    
    # Auth mechanism
    def __call__(self, server, session, envelope, mechanism, auth_data):
        # Fail message
        fail_nothandled = AuthResult(success=False, handled=False)
        # Only allow plain login
        if mechanism not in ("LOGIN", "PLAIN"):
            return fail_nothandled
        # Check login data
        if not isinstance(auth_data, LoginPassword):
            return fail_nothandled
        # Parse username and password
        username = auth_data.login
        password = auth_data.password
        # Find username and password in list
        for user in self.users:
            if username == user["name"].encode() and password == user["password"].encode():
                return AuthResult(success=True)
        # Return auth error
        return fail_nothandled

# SMTP server class
class SMTP:
    def __init__(self, hostname, port, domain, require_tls = False, require_auth = False, tls_cert_chain = [], users = [], check_id = None, callback = None) -> None:
        # Initialize parameters
        self.hostname = hostname
        self.port = port
        self.domain = domain
        self.users = users
        # Define controller parameters
        controller_parameters = {
            "port": self.port,
            "hostname": self.hostname
        }
        # Load tls context
        if require_tls:
            if len(tls_cert_chain) != 2:
                raise Exception("Invalid TLS cert chain!")
            for path in tls_cert_chain:
                if not os.path.exists(path):
                    raise Exception("File not found: {}!".format(path))
            tls_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            tls_context.load_cert_chain(*tls_cert_chain)
            controller_parameters["require_starttls"] = True
            controller_parameters["tls_context"] = tls_context
        # Enable auth
        if require_auth:
            controller_parameters["auth_required"] = True
            controller_parameters["authenticator"] = SMTPAuthenticator(self.users)
        # Enable auth withhout tls
        if require_auth and not require_tls:
            controller_parameters["auth_require_tls"] = False
        # Initialize controller
        self.controller = Controller(
            SMTPHandler(self.domain, check_id = check_id, callback = callback), 
            **controller_parameters
        )
    def start(self):
        self.controller.start() #type: ignore
    def stop(self):
        self.controller.stop() #type: ignore
        
