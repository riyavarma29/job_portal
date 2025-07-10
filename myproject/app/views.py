# app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, JobApplication, Profile
from .forms import JobForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UserRegisterForm

def home(request):
    return render(request, 'app/home.html')
# app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Profile
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)  
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You are registered!")
            return redirect('job_list')
    else:
        form = UserRegisterForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)
    return render(request, 'app/profile.html', {'user': request.user})


@login_required
def post_job(request):
    if request.user.profile.role != 'shop_owner':
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        print("✅ Received POST request")
        print("POST data:", request.POST)

        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            print("✅ Job saved:", job.title)
            return redirect('job_list')
        else:
            print("❌ Form errors:", form.errors)
    else:
        print("➡️ GET request to post_job")
        form = JobForm()

    return render(request, 'app/post_job.html', {'form': form})

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.posted_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobForm(instance=job)

    return render(request, 'app/edit_job.html', {'form': form})


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.posted_by != request.user:
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST':
        job.delete()
        return redirect('job_list')

    return render(request, 'app/delete_job.html', {'job': job})

from .models import SavedJob

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user.profile.role == 'developer':
        SavedJob.objects.get_or_create(developer=request.user, job=job)
    return redirect('job_list')

@login_required
def my_jobs(request):
    applied_jobs = JobApplication.objects.filter(developer=request.user).select_related('job')
    saved_jobs = SavedJob.objects.filter(developer=request.user).select_related('job')
    return render(request, 'app/my_jobs.html', {
        'applied_jobs': applied_jobs,
        'saved_jobs': saved_jobs,
    })
@login_required
def apply_to_job(request, job_id):
    if request.user.profile.role != 'developer':
        return HttpResponse("Unauthorized", status=401)

    job = get_object_or_404(Job, id=job_id)
    JobApplication.objects.get_or_create(job=job, developer=request.user)
    return redirect('job_list')

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'app/job_detail.html', {'job': job})

@login_required
def update_application_status(request, app_id, action):
    if request.user.profile.role != 'shop_owner':
        return HttpResponse("Unauthorized", status=401)

    application = get_object_or_404(JobApplication, id=app_id)
    if application.job.posted_by != request.user:
        return HttpResponse("Forbidden", status=403)

    if action == 'approve':
        application.status = 'approved'
    elif action == 'decline':
        application.status = 'declined'
    application.save()
    return redirect('view_applicants', job_id=application.job.id)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Job
def job_list(request):
    jobs = Job.objects.all()

    # Safely filter for shop_owner's own jobs
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role == 'shop_owner':
            jobs = jobs.filter(posted_by=request.user)

    # Filter logic
    title = request.GET.get('title')
    category = request.GET.get('category')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')

    if title:
        jobs = jobs.filter(title__icontains=title)
    if category:
        jobs = jobs.filter(category=category)
    if min_salary:
        jobs = jobs.filter(budget__gte=min_salary)
    if max_salary:
        jobs = jobs.filter(budget__lte=max_salary)

    return render(request, 'app/job_list.html', {'jobs': jobs})




@login_required
def remove_saved_job(request, job_id):
    SavedJob.objects.filter(developer=request.user, job_id=job_id).delete()
    return redirect('my_jobs')

@login_required
def discard_application(request, job_id):
    JobApplication.objects.filter(developer=request.user, job_id=job_id).delete()
    return redirect('my_jobs')
@login_required
def message_exchange(request, job_id, developer_id):
    job = get_object_or_404(Job, id=job_id)
    developer = get_object_or_404(User, id=developer_id)

    app = get_object_or_404(JobApplication, job=job, developer=developer)

    if request.method == 'POST' and 'content' in request.POST:
        Message.objects.create(
            sender=request.user,
            receiver=developer if request.user != developer else job.posted_by,
            job=job,
            content=request.POST['content']
        )

    messages = Message.objects.filter(
        job=job,
        sender__in=[request.user, developer],
        receiver__in=[request.user, developer]
    ).order_by('timestamp')

    return render(request, 'app/message_exchange.html', {
        'messages': messages,
        'job': job,
        'developer': developer,
        'app': app,  # 👈 pass application here
    })
@login_required
def view_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applications = JobApplication.objects.filter(job=job)
    return render(request, 'app/view_applicants.html', {
        'job': job,
        'applications': applications
    })

@login_required
def finalize_job(request, app_id, status):
    app = get_object_or_404(JobApplication, id=app_id)
    
    if request.user != app.job.posted_by:
        return redirect('job_list')

    if status in ['successful', 'rejected']:
        app.status = status
        app.save()

    return redirect('view_applicants', job_id=app.job.id)

from .models import Message
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
def get_room_name(user1, user2):
    sorted_ids = sorted([user1.id, user2.id])
    return f"chat_{sorted_ids[0]}_{sorted_ids[1]}"
from django.urls import reverse

@login_required
def start_chat(request, user_id):
    user1 = request.user
    user2 = get_object_or_404(User, id=user_id)

    room_name = get_room_name(user1, user2)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        file = request.FILES.get('file')

        if content or file:
            Message.objects.create(
                sender=request.user,
                receiver=user2,
                room_name=room_name,
                content=content,
                file=file
            )
        # Redirect to prevent form resubmission
        return redirect(reverse('start_chat', args=[user_id]))

    messages = Message.objects.filter(
        sender__in=[user1, user2],
        receiver__in=[user1, user2]
    ).order_by('timestamp')

    return render(request, 'app/chat.html', {
        'room_name': room_name,
        'receiver': user2,
        'messages': messages,
    })

@login_required
def chat_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    room_name = get_room_name(request.user, receiver)

    if request.method == "POST":
        file = request.FILES.get("file")
        content = request.POST.get("content", "").strip()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # AJAX call – do not redirect
            if file or content:
                Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    room_name=room_name,
                    content=content,
                    file=file
                )
            return JsonResponse({"status": "ok"})

        # Non-AJAX POST – redirect to prevent form resubmission
        if file or content:
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                room_name=room_name,
                content=content,
                file=file
            )
        return redirect(reverse('chat_view', args=[user_id]))

    messages = Message.objects.filter(room_name=room_name).order_by("timestamp")
    return render(request, "chat/chat.html", {
        "receiver": receiver,
        "messages": messages,
        "room_name": room_name,
    })
