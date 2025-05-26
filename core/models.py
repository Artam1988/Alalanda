from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class ContactMessage(models.Model):
    """Model for storing contact form submissions"""
    SUBJECT_CHOICES = (
        ('inquiry', _('General Inquiry')),
        ('support', _('Customer Support')),
        ('complaint', _('Complaint')),
        ('feedback', _('Feedback')),
    )
    
    name = models.CharField(_('Full Name'), max_length=100)
    email = models.EmailField(_('Email Address'))
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True)
    subject = models.CharField(_('Subject'), max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"

class EmploymentApplication(models.Model):
    """Model for storing employment applications"""
    POSITION_CHOICES = (
        ('sales', _('Sales Associate')),
        ('customer-service', _('Customer Service')),
        ('warehouse', _('Warehouse Staff')),
        ('management', _('Management')),
        ('other', _('Other')),
    )
    
    EXPERIENCE_CHOICES = (
        ('0-1', _('0-1 years')),
        ('1-3', _('1-3 years')),
        ('3-5', _('3-5 years')),
        ('5+', _('5+ years')),
    )
    
    name = models.CharField(_('Full Name'), max_length=100)
    email = models.EmailField(_('Email Address'))
    phone = models.CharField(_('Phone Number'), max_length=20)
    position = models.CharField(_('Position of Interest'), max_length=20, choices=POSITION_CHOICES)
    experience = models.CharField(_('Years of Experience'), max_length=10, choices=EXPERIENCE_CHOICES)
    resume = models.FileField(_('Resume'), upload_to='resumes/%Y/%m/')
    cover_letter = models.TextField(_('Cover Letter'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Employment Application')
        verbose_name_plural = _('Employment Applications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"
