from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.core.paginator import Paginator




def home(request):
    return render(request, 'login.html')
    # return render(request, 'biometric_test.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            if request.user.is_staff:
                return redirect('dashboard') 
            else:
                return redirect('staff_dash')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')



@login_required
def dashboard(request):
    voters = Voter.objects.all()
    sessions = VotingSession.objects.all()
    candidates = Candidate.objects.all()
    constituencies = Constituency.objects.all()

    # Pagination for voters
    voter_paginator = Paginator(voters, 5)
    voter_page_number = request.GET.get('voter_page')
    voter_page_obj = voter_paginator.get_page(voter_page_number)

    # Pagination for sessions
    session_paginator = Paginator(sessions, 3)
    session_page_number = request.GET.get('session_page')
    session_page_obj = session_paginator.get_page(session_page_number)

    # Pagination for candidates
    candidate_paginator = Paginator(candidates, 5)
    candidate_page_number = request.GET.get('candidate_page')
    candidate_page_obj = candidate_paginator.get_page(candidate_page_number)

    # Pagination for constituencies
    constituency_paginator = Paginator(constituencies, 5)
    constituency_page_number = request.GET.get('constituency_page')
    constituency_page_obj = constituency_paginator.get_page(constituency_page_number)

    session_data = []
    for session in session_page_obj:
        candidates_data = VoteCount.objects.filter(session=session).order_by('-total_votes')
        total_votes = sum(candidate.total_votes for candidate in candidates_data)

        session_data.append({
            'session': session,
            'candidates_data': candidates_data,
            'total_votes': total_votes,
        })

    return render(request, 'dashboard.html', {
        'voter_page_obj': voter_page_obj,
        'session_page_obj': session_page_obj,
        'session_data': session_data,
        'candidate_page_obj': candidate_page_obj,
        'constituency_page_obj': constituency_page_obj,
    })



@login_required
def staff_dashboard(request):
    active_sessions = VotingSession.objects.filter(status="Active")
    session_data = []
    for session in active_sessions:
        candidates_data = VoteCount.objects.filter(session=session).order_by('-total_votes')
        total_votes = sum(candidate.total_votes for candidate in candidates_data)

        session_data.append({
            'session': session,
            'candidates_data': candidates_data,
            'total_votes': total_votes,
        })

    return render(request, 'staff_dashboard.html', {
        'session_data': session_data,
    })




def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')



def add_voter(request):
    if request.method == 'POST':
        form = VoterForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = VoterForm()
    return render(request, 'add_voter.html', {'form': form})

def add_candidate(request):
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = CandidateForm()

    return render(request, 'add_candidate.html', {'form': form})


def add_constituency(request):
    if request.method == "POST":
        form = ConstituencyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = ConstituencyForm()

    return render(request, 'add_constituency.html', {'form': form})


def create_session(request):
    return redirect('home')



def voting_interface(request, session_id):
    session = get_object_or_404(VotingSession, id=session_id)
    candidates = Candidate.objects.filter(constituency=session.constituency)

    return render(request, 'voting_interface.html', {'session': session, 'candidates': candidates})


@login_required
def submit_vote(request, candidate_id):
    if request.method == "POST":
        candidate = Candidate.objects.get(id=candidate_id)
        session = VotingSession.objects.filter(status="Active").first()

        if session:
            vote_count, created = VoteCount.objects.get_or_create(session=session, candidate=candidate)
            vote_count.total_votes += 1
            vote_count.save()

        return redirect('voting_interface')

    return redirect('voting_interface')



def scan_biometric(request, voter_id):
    """Render biometric scan page with voter ID."""
    voter = get_object_or_404(Voter, id=voter_id)
    return render(request, 'scan_biometric.html', {'voter_id': voter_id})




def validate_fingerprint(request, voter_id):
    """Validate the scanned fingerprint data."""
    if request.method == "POST":
        scanned_fingerprint = request.POST.get("fingerprint_data")
        voter = get_object_or_404(Voter, id=voter_id)

        # if voter.fingerprint_data == scanned_fingerprint:
        return JsonResponse({"status": "success", "message": "Fingerprint Matched ✅"})
        # else:
        #     return JsonResponse({"status": "error", "message": "Fingerprint Mismatch ❌"})

def validate_retina(request, voter_id):
    """Validate the scanned retina data."""
    if request.method == "POST":
        scanned_retina = request.POST.get("retina_data")
        voter = get_object_or_404(Voter, id=voter_id)

        # if voter.retina_data == scanned_retina:
        return JsonResponse({"status": "success", "message": "Retina Matched ✅"})
        # else:
        #     return JsonResponse({"status": "error", "message": "Retina Mismatch ❌"})



def session_details(request, session_id):
    session = get_object_or_404(VotingSession, id=session_id)

    candidates_data = VoteCount.objects.filter(session=session).order_by('-total_votes')
    total_voters = session.constituency.voter_set.count()
    voters = Voter.objects.filter(constituency=session.constituency)

    total_votes = candidates_data.aggregate(total=models.Sum('total_votes'))['total'] or 0


    context = {
        "session": session,
        "candidates": candidates_data,
        "total_voters": total_voters,
        "total_votes": total_votes,
        "voters":voters
    }
    return render(request, "session_details.html", context)