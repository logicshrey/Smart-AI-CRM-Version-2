from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm, UserUpdateForm
from .models import Record
from django.contrib.auth.decorators import login_required
from .ai_utils import analyze_sentiment, categorize_customer, smart_search
from .ai_engagement import (
    segment_customers, generate_recommendations, 
    create_smart_workflow, generate_dynamic_message
)
from .ai_features import AnomalyDetector, VirtualAgent, analyze_customer_behavior
from django.db.models import Avg, Count, Case, When, Value, IntegerField
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

def home(request):
    records = Record.objects.all()
    
    # Handle login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.error(request, "Error Logging In - Please Try Again...")
            return redirect('home')
    
    # Calculate statistics for authenticated users
    if request.user.is_authenticated:
        total_records = records.count()
        vip_count = records.filter(customer_category='vip').count()
        anomaly_count = records.filter(priority_score__gte=8).count()
        positive_sentiment = int(records.filter(sentiment_score__gt=0).count() / total_records * 100) if total_records > 0 else 0
        
        return render(request, 'home.html', {
            'records': records,
            'total_records': total_records,
            'vip_count': vip_count,
            'anomaly_count': anomaly_count,
            'positive_sentiment': positive_sentiment,
        })
    
    return render(request, 'home.html', {})

@login_required
def ai_dashboard(request):
    # Get search query from GET parameters
    query = request.GET.get('q', '')
    search_results = []
    
    if query:
        # Perform smart search if there's a query
        records = Record.objects.all()
        search_results = smart_search(query, records)
    
    # Calculate customer categories
    categories = Record.objects.values('customer_category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Convert to dictionary for template
    categories_dict = {cat['customer_category'] or 'Uncategorized': cat['count'] for cat in categories}
    
    # Calculate sentiment metrics
    sentiment_metrics = Record.objects.aggregate(
        avg_sentiment=Avg('sentiment_score'),
        positive_count=Count(Case(When(sentiment_score__gt=0, then=1))),
        negative_count=Count(Case(When(sentiment_score__lte=0, then=1)))
    )
    
    # Get priority customers (sorted by priority score)
    priority_customers = Record.objects.exclude(
        priority_score__isnull=True
    ).order_by('-priority_score')[:5]
    
    context = {
        'query': query,
        'search_results': search_results,
        'categories': categories_dict,
        'avg_sentiment': sentiment_metrics['avg_sentiment'] or 0,
        'positive_count': sentiment_metrics['positive_count'],
        'negative_count': sentiment_metrics['negative_count'],
        'priority_customers': priority_customers,
    }
    
    return render(request, 'ai_dashboard.html', context)

@login_required
def anomaly_detection(request):
    # Get recent transactions
    recent_records = Record.objects.all().order_by('-created_at')[:100]
    
    # Initialize and run anomaly detection
    detector = AnomalyDetector()
    anomaly_indices = detector.detect_anomalies(recent_records)
    
    # Get anomalous records
    anomalous_records = [recent_records[i] for i in anomaly_indices]
    
    return render(request, 'anomaly_detection.html', {
        'anomalous_records': anomalous_records,
        'total_analyzed': len(recent_records)
    })

@login_required
def customer_insights(request, customer_id):
    customer = Record.objects.get(id=customer_id)
    customer_records = Record.objects.filter(id=customer_id)
    
    # Get behavior analysis
    insights = analyze_customer_behavior(customer_records)
    
    return render(request, 'customer_insights.html', {
        'customer': customer,
        'insights': insights
    })

@csrf_exempt
def virtual_agent_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        agent = VirtualAgent()
        response = agent.get_response(message)
        
        return JsonResponse({'response': response})
    
    return render(request, 'virtual_agent.html')

@login_required
def ai_engagement(request):
    # Get all records
    records = Record.objects.all()
    
    # Segment customers
    segments = segment_customers(records)
    
    # Generate recommendations and messages for each record
    for record in records:
        record.recommendations = generate_recommendations(record)
        record.follow_up_message = generate_dynamic_message(record, 'follow_up')
        record.promo_message = generate_dynamic_message(record, 'promotion')
    
    context = {
        'segments': {record: segments.get(record.id) for record in records}
    }
    
    return render(request, 'ai_engagement.html', context)

@login_required
def smart_workflows(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        workflow_type = request.POST.get('workflow_type')
        
        if customer_id and workflow_type:
            record = Record.objects.get(id=customer_id)
            workflow = create_smart_workflow(record, workflow_type)
            messages.success(request, f"Created new {workflow_type} workflow for {record.first_name}")
            
    # Get all active workflows (for demo, we'll create some sample ones)
    active_workflows = []
    for record in Record.objects.all()[:5]:  # Limit to 5 for demo
        workflow_type = 'support' if record.sentiment_score and record.sentiment_score < 0 else 'sales'
        workflow = create_smart_workflow(record, workflow_type)
        if workflow:
            workflow['id'] = len(active_workflows) + 1
            workflow['record'] = record
            workflow['progress'] = 50  # Demo progress
            workflow['created_at'] = datetime.now()
            active_workflows.append(workflow)
    
    context = {
        'active_workflows': active_workflows,
        'customers': Record.objects.all()
    }
    
    return render(request, 'smart_workflows.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You Have Successfully Registered! Welcome!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form':form})

    return render(request, 'register.html', {'form':form})

@login_required
def customer_record(request, pk):
    if request.user.is_authenticated:
        # Look Up Records
        customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record':customer_record})
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')

@login_required
def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record Deleted Successfully...")
        return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')

@login_required
def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                record = form.save(commit=False)
                
                # Analyze sentiment from notes
                if record.notes:
                    record.sentiment_score = analyze_sentiment(record.notes)
                
                # Categorize customer
                record.customer_category = categorize_customer(record.email, record.notes)
                
                # Calculate priority score (1-10)
                record.priority_score = min(10, max(1, int((record.sentiment_score + 1) * 5)))
                
                record.save()
                messages.success(request, "Record Added...")
                return redirect('home')
        return render(request, 'add_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@login_required
def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            record = form.save(commit=False)
            
            # Update AI analysis
            if record.notes:
                record.sentiment_score = analyze_sentiment(record.notes)
            record.customer_category = categorize_customer(record.email, record.notes)
            record.priority_score = min(10, max(1, int((record.sentiment_score + 1) * 5)))
            
            record.save()
            messages.success(request, "Record Has Been Updated!")
            return redirect('home')
        return render(request, 'update_record.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@login_required
def update_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('home')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'update_user.html', {'form': form})
