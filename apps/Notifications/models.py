from django.db import models
from accounts.models import CustomUser
# Create your models here.

class Notification(models.Model):
    TYPES = (
        ('SYSTEM','system'), #auto-generated
        ('CHAT', 'Chat'), # real-time chat notifications
        ('APPLIED', 'Job-Applied'), #candidate applied
        ('INTERVIEW', 'Interview'), #interview scheduled/rescheduled/completed
        ('OFFER', 'Offer'), #job offer created/accepted/rejected 
        ('COMPANY',"Company"), #company profile updates
        ('JOB',"Job"), #job updates
        ('KYC_SUBMITTED', 'KYC_Submitted'), 
        ('KYC_APPROVED', 'KYC_Approved'),
        ('KYC_REJECTED', 'KYC_Rejected'), 
        ('KYC_ROLLBACK', 'KYC_Rollback'),
        ('NEW_APPLICATION','New-Application'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW_SCHEDULED', 'Interview_Scheduled'), 
        ('INTERVIEW_RESCHEDULED', 'Interview_Rescheduled'), 
        ('INTERVIEW_COMPLETED', 'Interview_Completed'), 
        ('OFFER_CREATED', 'Offer_Created'), 
        ('OFFER_ACCEPTED', 'Offer_Accepted'),
        ('OFFER_REJECTED', 'Offer_Rejected'),
        ('OFFER_EXPIRED', 'Offer_Expired'),
        ('OFFER_WITHDRAWN', 'Offer_Withdrawn'),
        ('JOB_CREATED', 'Job_Created'), 
        ('JOB_UPDATE', 'Job_Updated'),
        ('JOB_DELETED', 'Job_Deleted'),
        ('JOB_PUBLISHED', 'Job_Published'),
        ('JOB_CLOSED', "Job_Closed"),
        ('JOB_EXPIRED', 'Job_Expired'),
        ('JOB_FEATURED', 'Job_Featured'), 
        ('JOB_UNFEATURED', 'Job_Unfeatured'), 
        ('JOB_APPLIED', "Job_Applied"),
        ('JOB_SHORTLISTED', 'Job_Shortlisted'),
        ('JOB_INTERVIEW_SCHEDULED', 'Job_Interview_Scheduled'), 
        ('JOB_INTERVIEW_RESCHEDULED', 'Job_Interview_Rescheduled'), 
        ('JOB_INTERVIEW_COMPLETED', 'Job_Interview_Completed'), 
        ('JOB_OFFER_CREATED', 'Job_offer_Created'),
        ('JOB_OFFER_ACCEPTED', 'Job_offer_Accepted'), 
        ('JOB_OFFER_REJECTED', 'Job_Offer_Rejected'), 
        ('JOB_OFFER_EXPIRED', 'Job_Offer_Expired'),
        ('JOB_OFFER_WITHDRAWN', 'Job_Offer_Withdrawn'),
        ('ACCOUNT_ACTIVATED', 'Account_Activated'), 
        ('ACCOUNT_DEACTIVATED', 'Account_Deactivated'),
        ('ACCOUNT_BANNED', 'Account_Banned'), 
        ('ACCOUNT_UNBANNED', 'Account_Unbanned')
        )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name= "notifications")
    notification_type = models.CharField(max_length=30, choices=TYPES) 
    title= models.CharField(max_length=255, blank=True) 
    message= models.TextField()
    link = models.URLField(null=True, blank=True)
    is_read=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)