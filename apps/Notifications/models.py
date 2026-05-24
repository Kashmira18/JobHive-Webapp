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
        ('KYC_ROLLBACK', 'KVC_Rolledback'),
        ('NEW_APPLICATION','New-Application'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW SCHEDULED', 'Interview Scheduled'), 
        ('INTERVIEW_RESCHEDULED', 'Interview Rescheduled'), 
        ('INTERVIEW_COMPLETED', 'Interview Completed'), 
        ('OFFER_CREATED', 'Offer Created'), 
        ('OFFER_ACCEPTED', 'Offer Accepted'),
        ('OFFER_REJECTED', 'Offer Rejected'),
        ('OFFER_EXPIRED', 'Offer Expired'),
        ('OFFER_WITHDRAWN', 'Offer Withdrawn'),
        ('JOB_CREATED', 'Job Created'), 
        ('JOB_UPDATE, Job Updated'),
        ('JOB_DELETED', 'Job Deleted'),
        ('JOB_PUBLISHED', 'Job Published'),
        ('JOB_CLOSED', "Job Closed"),
        ('JOB_EXPIRED', 'Job Expired'),
        ('JOB_FEATURED', 'Job Featured'), 
        ('JOB_UNFEATURED', 'Job Unfeatured'), 
        ('JOB_APPLIED', "Job Applied"),
        ('JOB_SHORTLISTED', 'Job Shortlisted'),
        ('JOB_INTERVIEN SCHEDULED', 'Job Interview Scheduled'), 
        ('JOB_INTERVIEW_RESCHEDULED, Job Interview Rescheduled'), 
        ('JOB_INTERVIEW_COMPLETED', 'Job Interview Completed'), 
        ('JOB_OFFER CREATED', 'Job offer Created'),
        ('JOB OFFER ACCEPTED', 'Job offer Accepted'), 
        ('JOB_OFFER REJECTED', 'Job Offer Rejected'), 
        ('JOB_OFFER_EXPIRED', 'Job Offer Expired'),
        ('JOB_OFFER_WITHDRAWN', 'Job Offer Withdrawn'),
        ('ACCOUNT_ACTIVATED', 'Account Activated'), 
        ('ACCOUNT_DEACTIVATED', 'Account Deactivated'),
        ('ACCOUNT_BANNED', 'Account Banned'), 
        ('ACCOUNT_UNBANNED', 'Account Unbanned')
        )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name= "notifications")
    notification_type = models.CharField(max_length=20, choices=TYPES) 
    title= models.CharField(max_length=255, blank=True) 
    message= models.TextField()
    link = models.URLField(null=True, blank=True)
    is_read=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)