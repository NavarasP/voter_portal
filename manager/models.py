from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone


class Constituency(models.Model):
    constituency = models.CharField(max_length=100, unique=True)  

    def __str__(self):
        return self.constituency


class Voter(models.Model):
    name = models.CharField(max_length=100)
    fingerprint_data = models.TextField()
    retina_data = models.TextField()
    is_registered = models.BooleanField(default=False)
    image = models.ImageField(upload_to='voter_images/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, null=True, blank=True)  
    pin = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    aadhaar_num = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            MinLengthValidator(12),
            RegexValidator(r'^\d{12}$', 'Aadhaar number must be 12 digits.')
        ],
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class VotingSession(models.Model):
    name = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, null=True, blank=True)  
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        default='Inactive'
    )
    voted_users = models.ManyToManyField(Voter, blank=True) 


    def __str__(self):
        return f"{self.name} ({self.constituency})"

    def is_active(self):
        """Checks if the voting session is currently active."""
        now = timezone.localtime(timezone.now())  
        return self.start_time <= now <= self.end_time


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='candidate_images/', blank=True, null=True)
    party = models.CharField(max_length=100)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"{self.name} ({self.party}) - {self.constituency}"


class VoteCount(models.Model):
    session = models.ForeignKey(VotingSession, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    total_votes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('session', 'candidate')

    def __str__(self):
        return f"{self.candidate.name} - {self.total_votes} votes in {self.session.name}"
