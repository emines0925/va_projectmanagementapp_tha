from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members= models.ManyToManyField('auth.User', through='ProjectMembership', related_name='projects')

    def __str__(self):
        return self.name
    
class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('Owner', 'Owner'),
        ('Editor', 'Editor'),
        ('Reader', 'Reader'),
    ]
    project = models.ForeignKey(Project, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} in {self.project.name}"
    
    class Meta:
        unique_together = ('project', 'user')
        verbose_name = 'Project Membership'
        verbose_name_plural = 'Project Memberships'