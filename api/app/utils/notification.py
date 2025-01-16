from datetime import datetime
from typing import List
from fastapi_mail import FastMail, MessageSchema
from app.core.config import settings

async def send_reminder_email(
    email: str,
    pet_name: str,
    reminder_type: str,
    due_date: datetime,
    details: dict
):
    """发送提醒邮件"""
    message = MessageSchema(
        subject=f"Pet Health Reminder: {pet_name}",
        recipients=[email],
        body=f"""
        Dear pet owner,

        This is a reminder for your pet {pet_name}:
        
        Type: {reminder_type}
        Due Date: {due_date.strftime('%Y-%m-%d')}
        Days Left: {(due_date - datetime.utcnow()).days}
        
        Details:
        {details.get('notes', 'No additional notes')}
        
        Best regards,
        Your Pet Health Assistant
        """
    )
    
    fm = FastMail(settings.MAIL_CONFIG)
    await fm.send_message(message)

async def check_and_send_reminders(db: Session):
    """检查并发送所有需要的提醒"""
    now = datetime.utcnow()
    
    # 获取所有启用的提醒设置
    reminder_settings = db.query(ReminderSettings).filter(
        ReminderSettings.enabled == True
    ).all()
    
    for setting in reminder_settings:
        if setting.reminder_type == "vaccine":
            records = db.query(VaccineRecord).filter(
                VaccineRecord.pet_id == setting.pet_id,
                VaccineRecord.next_due_date > now,
                VaccineRecord.next_due_date <= now + timedelta(days=setting.days_before)
            ).all()
            
            for record in records:
                if setting.notification_method in ["email", "both"]:
                    await send_reminder_email(
                        setting.pet.owner.email,
                        setting.pet.name,
                        "Vaccine Due",
                        record.next_due_date,
                        {"notes": f"Vaccine: {record.vaccine_name}"}
                    ) 