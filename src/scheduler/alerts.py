"""Alert system for change notifications."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from src.config import settings
from src.logger import scheduler_logger


class AlertManager:
    """Send alerts via email and logging."""

    async def send_alert(self, changes: List[Dict[str, Any]]) -> None:
        """
        Send alert for detected changes.

        Args:
            changes: List of detected changes
        """
        if not changes:
            return

        # Log all changes
        scheduler_logger.info(f"=== CHANGES DETECTED: {len(changes)} ===")
        for change in changes:
            scheduler_logger.info(f"  {change['change_type']}: {change['book_url']}")

        # Email alert if enabled
        if settings.alert_email_enabled and settings.alert_email_to:
            await self._send_email_alert(changes)

    async def _send_email_alert(self, changes: List[Dict[str, Any]]) -> None:
        """
        Send email alert with change details.

        Args:
            changes: List of changes to include in email
        """
        try:
            # Build email body
            body = self._format_changes_html(changes)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Books Scraper Alert: {len(changes)} Changes Detected"
            msg["From"] = settings.smtp_user
            msg["To"] = settings.alert_email_to

            msg.attach(MIMEText(body, "html"))

            # Send via SMTP
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)

            scheduler_logger.info(f"✉️ Alert email sent to {settings.alert_email_to}")

        except Exception as e:
            scheduler_logger.error(f"❌ Failed to send alert email: {e}", exc_info=True)

    @staticmethod
    def _format_changes_html(changes: List[Dict[str, Any]]) -> str:
        """
        Format changes as HTML email.

        Args:
            changes: List of changes

        Returns:
            HTML formatted email body
        """
        rows = ""
        for change in changes:
            change_type = change["change_type"]
            book_url = change["book_url"]
            old_val = str(change.get("old_value", "N/A"))
            new_val = str(change.get("new_value", "N/A"))
            rows += f"""
            <tr>
                <td>{change_type}</td>
                <td><a href="{book_url}">{book_url}</a></td>
                <td>{old_val}</td>
                <td>{new_val}</td>
            </tr>
            """

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>📊 Books Scraper Change Report</h2>
                <p>Detected <strong>{len(changes)}</strong> changes in your database.</p>
                <table border="1" cellpadding="10" cellspacing="0"
                       style="width: 100%; margin-top: 20px;">
                    <tr style="background-color: #f2f2f2;">
                        <th>Change Type</th>
                        <th>Book URL</th>
                        <th>Old Value</th>
                        <th>New Value</th>
                    </tr>
                    {rows}
                </table>
                <p style="margin-top: 20px; color: #666;">
                    This is an automated alert. Visit your API at
                    http://localhost:8000/api/v1/changes for more details.
                </p>
            </body>
        </html>
        """
