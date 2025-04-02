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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from Levenshtein import ratio

import cv2
import os
import time
import numpy as np
from deepface import DeepFace
import pickle
from django.conf import settings

# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  



def send_mail(to_email):
    subject = 'Vote'
    body = f'Your Vote is recived'

    msg = MIMEMultipart()
    msg['From'] = 'project3290@gmail.com'  
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    smtp_server = 'smtp.gmail.com'  
    smtp_port = 587  

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login('project3290@gmail.com', 'wwod hbqe pbgq hhiv')  
        server.sendmail('project3290@gmail.com', to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"Error: {e}")
        raise


def submit_vote(request, session_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            voter_id = data.get("voter_id")
            candidate_id = data.get("candidate_id")

            candidate = get_object_or_404(Candidate, id=candidate_id)
            session = get_object_or_404(VotingSession, id=session_id)

            voter = get_object_or_404(Voter, id=voter_id)

            vote_count, created = VoteCount.objects.get_or_create(session=session, candidate=candidate)
            vote_count.total_votes += 1
            vote_count.save()

            send_mail(voter.email)

            voter_info = f"Voter: {voter.name}, Phone: {voter.phone_number}\n"
            # ser.write(voter_info.encode())

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
    camera = cv2.VideoCapture(0)
    if request.method == 'POST':
        form = VoterForm(request.POST, request.FILES)  
        if form.is_valid():
            voter = form.save()
            voter_folder = os.path.join('media/face_data', str(voter.id))
            os.makedirs(voter_folder, exist_ok=True)
            
            for i in range(5):
                success, frame = camera.read()
                if not success:
                    return JsonResponse({"message": "Camera error!", "success": False})
                
                image_path = os.path.join(voter_folder, f"{voter.id}_{i+1}.jpg")
                cv2.imwrite(image_path, frame)
                time.sleep(1)

            camera.release()
            cv2.destroyAllWindows()

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
    if request.method == "POST":
        form = VotingSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("staff_dash")
    else:
        form = VotingSessionForm()

    return render(request, "create_session.html", {"form": form})



def voting_interface(request, session_id):
    session = get_object_or_404(VotingSession, id=session_id)
    candidates = Candidate.objects.filter(constituency=session.constituency)

    return render(request, 'voting_interface.html', {'session': session, 'candidates': candidates})





def scan_biometric(request, session_id):
    return render(request, 'scan_biometric.html',{"session_id":session_id})




def is_biometric_match(stored_data, scanned_data, threshold=0.20):
    """Check similarity between stored and scanned biometric data."""
    # similarity = SequenceMatcher(None, stored_data, scanned_data).ratio()
    similarity = ratio(stored_data, scanned_data)

    print(similarity)
    return similarity >= threshold  


import json
from django.http import JsonResponse
from .models import Voter, VotingSession
def verify_biometrics(request):
    camera = cv2.VideoCapture(0)
    if request.method == "POST":
        data = json.loads(request.body)
        scanned_fingerprint = data.get("fingerprint")
        scanned_retina = data.get("retina")
        session_id = data.get("session_id")
        
        captured_image_path = os.path.join("media/temp", "scanned_face.jpg")
        success, frame = camera.read()
        if not success:
            return JsonResponse({"success": False, "message": "Camera error!"})
        
        
        cv2.imwrite(captured_image_path, frame)

        
        try:
            results = DeepFace.find(img_path=captured_image_path, db_path="media/face_data", model_name="Facenet512")
            if len(results[0]) > 0:
                matched_voter_id = os.path.basename(os.path.dirname(results[0]['identity'][0]))
                voter = Voter.objects.get(id=matched_voter_id)
                session = VotingSession.objects.get(id=session_id, status="Active")  

                camera.release()
                cv2.destroyAllWindows() 
                
                # Prepare user details response (moved outside the if condition)
                user_details = {
                    "name": voter.name,
                    "voter_id": voter.id,
                    "constituency": voter.constituency.constituency if voter.constituency else "N/A",
                    "address": voter.address,
                    "pin": voter.pin,
                    "phone_number": voter.phone_number,
                    "email": voter.email,
                    "aadhaar_num": voter.aadhaar_num,
                    "image_url": request.build_absolute_uri(voter.image.url) if voter.image else request.build_absolute_uri(settings.MEDIA_URL + 'voter_images/download.jpg')
                }

                
                if session.voted_users.filter(id=voter.id).exists():
                    return JsonResponse({
                        "success": False, 
                        "message": "You have already voted!",
                        "user": user_details,
                        "already_voted": True  # Flag to indicate already voted
                    })
            
                if is_biometric_match(voter.fingerprint_data, scanned_fingerprint):  
                    if is_biometric_match(voter.retina_data, scanned_retina):  
                        return JsonResponse({
                            "success": True,
                            "user": user_details,
                            "session_id": session_id,
                            "already_voted": False
                        })
                    else:
                        return JsonResponse({"success": False, "message": "Biometric Mismatch (Retina does not match)"})
                else:
                    return JsonResponse({"success": False, "message": "Biometric Mismatch (Fingerprint does not match)"})
            else:
                return JsonResponse({"success": False, "message": "Face not recognized"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {e}"})

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