from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.core.paginator import Paginator
import json
from difflib import SequenceMatcher 
import serial


ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust for Windows: COM3, COM4, etc.




def submit_vote(request, session_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            voter_id = data.get("voter_id")
            candidate_id = data.get("candidate_id")

            candidate = get_object_or_404(Candidate, id=candidate_id)
            session = get_object_or_404(VotingSession, id=session_id)

            # Ensure the voter exists
            voter = get_object_or_404(Voter, id=voter_id)

            # Check if the voter has already voted in this session
            if VoteCount.objects.filter(session=session, candidate=candidate, voter=voter).exists():
                return JsonResponse({"success": False, "message": "Voter has already voted in this session."}, status=400)

            # Record the vote
            vote_count, created = VoteCount.objects.get_or_create(session=session, candidate=candidate)
            vote_count.total_votes += 1
            vote_count.save()

            # Send voter details to Arduino via Serial Communication
            voter_info = f"Voter: {voter.name}, Phone: {voter.phone_number}, Email: {voter.email}\n"
            ser.write(voter_info.encode())

            return JsonResponse({"success": True, "message": "Vote recorded successfully!"})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


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
    constituencies = Constituency.objects.all()
    if request.method == 'POST':
        form = VoterForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = VoterForm()
    return render(request, 'add_voter.html', {'form': form, 'constituencies': constituencies})

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
        print(candidate,session)

        if session:
            vote_count, created = VoteCount.objects.get_or_create(session=session, candidate=candidate)
            vote_count.total_votes += 1
            vote_count.save()
            print(vote_count.total_votes)

        return redirect('staff_dash')

    return redirect('staff_dash')



def scan_biometric(request, session_id):
    return render(request, 'scan_biometric.html',{"session_id":session_id})




def is_biometric_match(stored_data, scanned_data, threshold=0.95):
    """Check similarity between stored and scanned biometric data."""
    similarity = SequenceMatcher(None, stored_data, scanned_data).ratio()
    return similarity >= threshold  # Match if similarity is 95% or higher


def verify_biometrics(request, session_id):
    if request.method == "POST":
        data = json.loads(request.body)
        scanned_fingerprint = data.get("fingerprint")
        scanned_retina = data.get("retina")

        # Search for a matching fingerprint in the voter database
        for voter in Voter.objects.all():
            if is_biometric_match(voter.fingerprint_data, scanned_fingerprint):  # Fingerprint matches
                if is_biometric_match(voter.retina_data, scanned_retina):  # Retina matches
                    return JsonResponse({
                        "success": True,
                        "user": {
                            "name": voter.name,
                            "age": voter.age,
                            "voter_id": voter.id,
                            "constituency": voter.constituency.name if voter.constituency else "N/A",
                            "address": voter.address,
                            "phone_number": voter.phone_number
                        },
                        "session_id": session_id
                    })
                else:
                    return JsonResponse({"success": False, "message": "Biometric Mismatch (Retina does not match)"})
        
        return JsonResponse({"success": False, "message": "Biometric Mismatch (Fingerprint not found)"})

    return JsonResponse({"success": False, "message": "Invalid request"})




def session_details(request, session_id):
    session = get_object_or_404(VotingSession, id=session_id)

    candidates_data = VoteCount.objects.filter(session=session).order_by('-total_votes')
    total_voters = session.constituency.voter_set.count()
    voters = Voter.objects.filter(constituency=session.constituency)

    total_votes = candidates_data.aggregate(total=models.Sum('total_votes'))['total'] or 0
    print("Candidates in session:", [f"{c.candidate.name} - {c.total_votes}" for c in candidates_data])


    context = {
        "session": session,
        "candidates": candidates_data,
        "total_voters": total_voters,
        "total_votes": total_votes,
        "voters":voters
    }
    return render(request, "session_details.html", context)