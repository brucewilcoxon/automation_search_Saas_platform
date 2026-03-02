"""
Email provider interface for sending letters.
Designed to be easily pluggable with different email providers.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmailProvider:
    """
    Base email provider interface.
    Implementations can be swapped for different providers (SendGrid, Mailgun, AWS SES, etc.)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize email provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}
        self.provider_name = "stub"  # Override in implementations
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            from_email: Sender email (optional, uses default if not provided)
            from_name: Sender name (optional)
            **kwargs: Additional provider-specific options
            
        Returns:
            Dictionary with send result (provider-specific)
            
        Raises:
            Exception: If sending fails
        """
        # Stub implementation - just logs
        logger.info(
            f"[EMAIL STUB] Would send email to {to} with subject '{subject}' "
            f"using {self.provider_name} provider"
        )
        logger.debug(f"Email body preview: {body[:200]}...")
        
        # Return stub result
        return {
            "status": "logged",
            "provider": self.provider_name,
            "to": to,
            "subject": subject,
            "message_id": f"stub-{hash(f'{to}{subject}')}",
            "note": "This is a stub implementation. Configure a real email provider to actually send emails."
        }


class SendGridProvider(EmailProvider):
    """
    SendGrid email provider implementation (placeholder).
    To implement:
    1. Install: pip install sendgrid
    2. Set SENDGRID_API_KEY environment variable
    3. Uncomment and implement the send_email method
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_name = "sendgrid"
        # self.api_key = config.get("api_key") or os.getenv("SENDGRID_API_KEY")
        # if not self.api_key:
        #     raise ValueError("SENDGRID_API_KEY not configured")
    
    def send_email(self, to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        # TODO: Implement SendGrid integration
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # 
        # message = Mail(
        #     from_email=kwargs.get("from_email", "noreply@example.com"),
        #     to_emails=to,
        #     subject=subject,
        #     html_content=body
        # )
        # 
        # sg = SendGridAPIClient(self.api_key)
        # response = sg.send(message)
        # 
        # return {
        #     "status": "sent",
        #     "provider": "sendgrid",
        #     "status_code": response.status_code,
        #     "message_id": response.headers.get("X-Message-Id")
        # }
        
        # Fallback to stub
        return super().send_email(to, subject, body, **kwargs)


class MailgunProvider(EmailProvider):
    """
    Mailgun email provider implementation (placeholder).
    To implement:
    1. Install: pip install requests
    2. Set MAILGUN_API_KEY and MAILGUN_DOMAIN environment variables
    3. Uncomment and implement the send_email method
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.provider_name = "mailgun"
        # self.api_key = config.get("api_key") or os.getenv("MAILGUN_API_KEY")
        # self.domain = config.get("domain") or os.getenv("MAILGUN_DOMAIN")
    
    def send_email(self, to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        # TODO: Implement Mailgun integration
        # import requests
        # 
        # response = requests.post(
        #     f"https://api.mailgun.net/v3/{self.domain}/messages",
        #     auth=("api", self.api_key),
        #     data={
        #         "from": kwargs.get("from_email", f"noreply@{self.domain}"),
        #         "to": to,
        #         "subject": subject,
        #         "html": body
        #     }
        # )
        # 
        # response.raise_for_status()
        # 
        # return {
        #     "status": "sent",
        #     "provider": "mailgun",
        #     "message_id": response.json().get("id")
        # }
        
        # Fallback to stub
        return super().send_email(to, subject, body, **kwargs)


def get_email_provider(provider_name: str = "stub", config: Optional[Dict[str, Any]] = None) -> EmailProvider:
    """
    Factory function to get an email provider instance.
    
    Args:
        provider_name: Name of the provider ("stub", "sendgrid", "mailgun", etc.)
        config: Provider-specific configuration
        
    Returns:
        EmailProvider instance
    """
    providers = {
        "stub": EmailProvider,
        "sendgrid": SendGridProvider,
        "mailgun": MailgunProvider,
    }
    
    provider_class = providers.get(provider_name.lower(), EmailProvider)
    return provider_class(config)
