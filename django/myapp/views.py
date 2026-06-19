from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from .models import PromoterRecord
from django.db.models import Count
from .forms import FastaUploadForm, ContactForm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from django.core.mail import EmailMessage, get_connection
from django.conf import settings

#helper
def parse_fasta(fasta_str):
    sequences = []
    header = None
    seq = []

    for line in fasta_str.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith(">"):
            if header:
                sequences.append({
                    "header": header,
                    "sequence": "".join(seq)
                })
            header = line[1:]
            seq = []
        else:
            seq.append(line)

    if header:
        sequences.append({
            "header": header,
            "sequence": "".join(seq)
        })

    return sequences

# Create your views here.
def home(request):
    return render(request, "myapp/home.html")

def query(request):
    return render(request, "myapp/query.html")

def resources(request):
    return render(request, "myapp/resources.html")

def about(request):
    return render(request, "myapp/about.html")

def group_summary_page(request):
    return render(request, "myapp/group_summary.html")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            collected_data = form.cleaned_data
            subject = collected_data.get('subject')
            email = collected_data.get('email')
            message = collected_data.get('message')

            with get_connection(
                host = settings.EMAIL_HOST,
                port = settings.EMAIL_PORT,
                username = settings.EMAIL_HOST_USER,
                password = settings.EMAIL_HOST_PASSWORD,
                use_ssl = settings.EMAIL_USE_SSL
            ) as connection:
                subject = f'CDBProm_{subject}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['eusebio.sganzerla@gmail.com']
                message = f'{message}\n{email}'

                email = EmailMessage(subject, message, email_from, recipient_list)
                email.send()

                return render(request, 'myapp/contact_success.html')




    
    else:
        form = ContactForm()
    return render(request, 'myapp/contact.html', {'form':form})

def predict(request):
    sequences = None

    if request.method == "POST":
        form = FastaUploadForm(request.POST, request.FILES)

        if form.is_valid():
            fasta_text = form.cleaned_data.get("fasta_text")
            fasta_file = form.cleaned_data.get("fasta_file")

            if fasta_file:
                fasta_text = fasta_file.read().decode("utf-8")

            sequences = parse_fasta(fasta_text)

    else:
        form = FastaUploadForm()

    return render(request, "myapp/predict.html", {
        "form": form,
        "sequences": sequences
    })

###Class-based API Views
class PromoterAPI(View):

    def get(self, request):

        qs = PromoterRecord.objects.all().order_by("id")

        bacterium = request.GET.get("bacterium")
        if bacterium:
            qs = qs.filter(bacterium_name_formatted__icontains=bacterium)

        group = request.GET.get("group")
        if group:
            qs = qs.filter(group__icontains=group)

        annotation = request.GET.get("annotation")
        if annotation:
            qs = qs.filter(annotation__icontains=annotation)

        
        ###stats
        unique_stats = qs.aggregate(
            unique_bacteria=Count("bacterium", distinct=True),
            unique_groups=Count("group", distinct=True)
        )

        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 50))

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        data = list(page_obj.object_list.values(
            "id",
            "bacterium",
            "score",
            "density",
            "combined",
            "tier",
            "group",
            "assembly",
            "bacterium_name_formatted",
            "annotation",
            "sequence"
        ))

        return JsonResponse({
            "count": paginator.count,
            "page": page,
            "page_size": page_size,
            "results": data,
            "stats": unique_stats
        })
    

class GroupSummary(View):
    def get(self, request):
        group_counts = (
            PromoterRecord.objects.values("group")
            .annotate(bacterium_count=Count("bacterium", distinct=True))
            .order_by("group")
        )

        data = list(group_counts)

        return JsonResponse({
            "results": data
        })

class PredictAPIView(APIView):

    def post(self, request):
        fasta = request.data.get("fasta", "")

        if not fasta:
            return Response(
                {"error": "No FASTA provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            resp = requests.post(
                "http://prediction_service:5000/predict",
                json={"fasta": fasta},
                timeout=30
            )

            return Response(resp.json(), status=resp.status_code)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Flask service unavailable", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )