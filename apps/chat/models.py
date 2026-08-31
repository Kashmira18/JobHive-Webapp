from django.db import models
from accounts.models import CustomUser
from job.models import JobPost

class ChatThread(models.Model):
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employer_threads')
    candidate = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='candidate_threads')
    job = models.ForeignKey(JobPost, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employer', 'candidate', 'job']
        ordering = ['-updated_at']

    def __str__(self):
        return f"Thread: {self.employer.username} & {self.candidate.username}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.timestamp}"
