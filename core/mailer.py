"""
Mailer module for 360 Emlak Platform
Sends transactional emails using Flask-Mail.
All sends are fire-and-forget; failures are logged, not re-raised.
"""
import logging
from flask import current_app, render_template_string
from flask_mail import Message

logger = logging.getLogger(__name__)

_SUBJECT_PREFIX = '[360 Emlak] '

_MSG_TEMPLATE = """\
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <div style="background:linear-gradient(135deg,#1E3A8A,#0ea5e9);padding:20px;border-radius:8px 8px 0 0;">
    <h2 style="color:white;margin:0;">360 Emlak</h2>
  </div>
  <div style="background:#f8f9fa;padding:24px;border-radius:0 0 8px 8px;border:1px solid #dee2e6;">
    {{ body | safe }}
    <hr style="border:none;border-top:1px solid #dee2e6;margin:24px 0;">
    <p style="color:#6c757d;font-size:12px;margin:0;">
      Bu e-posta 360 Emlak platformu tarafından otomatik olarak gönderilmiştir.
    </p>
  </div>
</body>
</html>"""


def _send(subject: str, recipients: list[str], body_html: str):
    """Internal send helper — silently skips if mail is not configured."""
    from app import mail
    if not current_app.config.get('MAIL_ENABLED'):
        logger.debug("Mail not configured, skipping: %s → %s", subject, recipients)
        return
    try:
        html = render_template_string(_MSG_TEMPLATE, body=body_html)
        msg = Message(
            subject=_SUBJECT_PREFIX + subject,
            recipients=recipients,
            html=html,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
        )
        mail.send(msg)
        logger.info("Email sent: %s → %s", subject, recipients)
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, recipients)


def send_new_message_notification(owner_email: str, owner_name: str,
                                   sender_name: str, property_title: str,
                                   message_preview: str):
    """Notify property owner when they receive a new contact message."""
    body = f"""
    <p>Merhaba <strong>{owner_name}</strong>,</p>
    <p><strong>{sender_name}</strong> adlı kullanıcı "<em>{property_title}</em>" ilanınız hakkında size mesaj gönderdi:</p>
    <blockquote style="border-left:4px solid #1E3A8A;padding:10px 16px;background:#e8eaf6;border-radius:4px;margin:16px 0;">
      {message_preview[:300]}{'…' if len(message_preview) > 300 else ''}
    </blockquote>
    <p>
      <a href="#" style="background:#1E3A8A;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block;">
        Mesajları Görüntüle
      </a>
    </p>
    """
    _send('Yeni Mesajınız Var', [owner_email], body)


def send_new_review_notification(owner_email: str, owner_name: str,
                                  reviewer_name: str, property_title: str,
                                  rating: int, comment: str):
    """Notify property owner when their listing receives a new review."""
    stars = '★' * rating + '☆' * (5 - rating)
    body = f"""
    <p>Merhaba <strong>{owner_name}</strong>,</p>
    <p>"<em>{property_title}</em>" ilanınıza <strong>{reviewer_name}</strong> tarafından yeni bir değerlendirme yapıldı.</p>
    <p style="font-size:1.4em;color:#F59E0B;">{stars} ({rating}/5)</p>
    <blockquote style="border-left:4px solid #0ea5e9;padding:10px 16px;background:#e0f2fe;border-radius:4px;margin:16px 0;">
      {comment[:300]}{'…' if len(comment) > 300 else ''}
    </blockquote>
    """
    _send('İlanınıza Yeni Değerlendirme', [owner_email], body)


def send_property_status_change(owner_email: str, owner_name: str,
                                 property_title: str, new_status: str):
    """Notify owner when admin changes a property's status."""
    status_labels = {
        'active': ('✅ Yayınlandı', '#059669'),
        'inactive': ('❌ Pasife Alındı', '#DC2626'),
        'pending': ('⏳ İnceleniyor', '#D97706'),
        'rejected': ('🚫 Reddedildi', '#DC2626'),
    }
    label, color = status_labels.get(new_status, (new_status, '#6B7280'))
    body = f"""
    <p>Merhaba <strong>{owner_name}</strong>,</p>
    <p>"<em>{property_title}</em>" ilanınızın durumu değiştirildi:</p>
    <p style="font-size:1.2em;font-weight:bold;color:{color};">{label}</p>
    """
    _send('İlan Durumu Değişti', [owner_email], body)
