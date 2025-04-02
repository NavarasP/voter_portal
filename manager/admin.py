from django.contrib import admin
from .models import *

admin.site.register(Voter)
admin.site.register(VotingSession)
admin.site.register(VoteCount)
admin.site.register(Candidate)
admin.site.register(Constituency)

