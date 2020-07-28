import datetime

from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
from .serializers import CustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import login, authenticate


now = timezone.now()
def home(request):
   return render(request, 'portfolio/home.html',
                 {'portfolio': home})



@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html', {'customers': customer})

@login_required
def customer_edit(request, pk):
   customer = get_object_or_404(Customer, pk=pk)
   if request.method == "POST":
       # update
       form = CustomerForm(request.POST, instance=customer)
       if form.is_valid():
           customer = form.save(commit=False)
           customer.updated_date = timezone.now()
           customer.save()
           customer = Customer.objects.filter(created_date__lte=timezone.now())
           return render(request, 'portfolio/customer_list.html',
                         {'customers': customer})
   else:
        # edit
       form = CustomerForm(instance=customer)
   return render(request, 'portfolio/customer_edit.html', {'form': form})

@login_required
def customer_delete(request, pk):
   customer = get_object_or_404(Customer, pk=pk)
   customer.delete()
   return redirect('portfolio:customer_list')
@login_required
def stock_list(request):
   stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
   return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
@login_required
def stock_new(request):
   if request.method == "POST":
       form = StockForm(request.POST)
       if form.is_valid():
           stock = form.save(commit=False)
           stock.created_date = timezone.now()
           stock.save()
           stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
           return render(request, 'portfolio/stock_list.html',
                         {'stocks': stocks})
   else:
       form = StockForm()
       # print("Else")
   return render(request, 'portfolio/stock_new.html', {'form': form})

@login_required
def stock_edit(request, pk):
   stock = get_object_or_404(Stock, pk=pk)
   if request.method == "POST":
       form = StockForm(request.POST, instance=stock)
       if form.is_valid():
           stock = form.save()
           # stock.customer = stock.id
           stock.updated_date = timezone.now()
           stock.save()
           stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
           return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
   else:
       # print("else")
       form = StockForm(instance=stock)
   return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
   stock = get_object_or_404(Stock, pk=pk)
   stock.delete()
   return redirect('portfolio:stock_list')

@login_required
def investment_delete(request, pk):
   investment = get_object_or_404(Investment, pk=pk)
   investment.delete()
   return redirect('portfolio:investment_list')


@login_required
def investment_list(request):
   investment = Investment.objects.filter(recent_date__lte=timezone.now())
   return render(request, 'portfolio/investment_list.html', {'investments': investment})

@login_required
def investment_add(request):
   if request.method == "POST":
       form = InvestmentForm(request.POST)
       if form.is_valid():
           investment = form.save(commit=False)
           investment.created_date = timezone.now()
           investment.save()
           investment = Investment.objects.filter(recent_date__lte=timezone.now())
           return render(request, 'portfolio/investment_list.html',
                         {'investments': investment})
   else:
       form = InvestmentForm()
       # print("Else")
   return render(request, 'portfolio/investment_add.html', {'form': form})

@login_required
def investment_edit(request, pk):
   investment = get_object_or_404(Investment, pk=pk)
   if request.method == "POST":
       form = InvestmentForm(request.POST, instance=investment)
       if form.is_valid():
           investment = form.save()
           # stock.customer = stock.id
           investment.updated_date = timezone.now()
           investment.save()
           investment = Investment.objects.filter(recent_date__lte=timezone.now())
           return render(request, 'portfolio/investment_list.html', {'investments': investment})
   else:
       # print("else")
       form = InvestmentForm(instance=investment)
   return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def portfolio(request,pk):
   customer = get_object_or_404(Customer, pk=pk)
   customers = Customer.objects.filter(created_date__lte=timezone.now())
   investments =Investment.objects.filter(customer=pk)
   stocks = Stock.objects.filter(customer=pk)
   mutualfund = MutualFund.objects.filter(customer=pk)
   #sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
   sum_recent_value = Investment.objects.filter(customer=pk).aggregate(recent_sum=Sum('recent_value'))['recent_sum']
   #sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
   sum_acquired_value = Investment.objects.filter(customer=pk ).aggregate(acquired_sum=Sum('acquired_value'))['acquired_sum']
   sum_acquired_value_mf = MutualFund.objects.filter(customer=pk).aggregate(acquired_sum=Sum('acquired_value'))['acquired_sum']
   sum_recent_value_mf = MutualFund.objects.filter(customer=pk).aggregate(recent_sum=Sum('recent_value'))['recent_sum']

   #overall_investment_results = sum_recent_value-sum_acquired_value
   # Initialize the value of the stocks
   sum_current_stocks_value = 0
   sum_of_initial_stock_value = 0

   # Loop through each stock and add the value to the total
   for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()
   portfolio_initial_investments = float(sum_of_initial_stock_value) + float(sum_acquired_value) + float(
       sum_acquired_value_mf)
   portfolio_current_investments = float(sum_current_stocks_value) + float(sum_recent_value) + float(
       sum_recent_value_mf)

   return render(request, 'portfolio/portfolio.html', {'customers': customers,
                                                       'investments': investments,
                                                       'stocks': stocks,
                                                       'mutualfund':mutualfund,
                                                       'sum_acquired_value': sum_acquired_value,
                                                       'sum_recent_value': sum_recent_value,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                       'portfolio_initial_investments': portfolio_initial_investments,
                                                       'portfolio_current_investments': portfolio_current_investments,
                                                       'sum_acquired_value_mf':sum_acquired_value_mf,
                                                       'sum_recent_value_mf':sum_recent_value_mf


                                                       })
# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self,request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)



@login_required
def mutualfund_list(request):
    mutualfund = MutualFund.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/mutualfund_list.html', {'mutualfunds': mutualfund})

@login_required
def mutualfund_new(request):
   if request.method == "POST":
       form = MutualfundForm(request.POST)
       if form.is_valid():
           mutualfund = form.save(commit=False)
           mutualfund.created_date = timezone.now()
           mutualfund.save()
           mutualfund = MutualFund.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/mutualfund_list.html',
                         {'mutualfunds': mutualfund})
   else:
       form = MutualfundForm()
       # print("Else")
   return render(request, 'portfolio/mutualfund_new.html', {'form': form})


@login_required
def mutualfund_edit(request, pk):
   mutualfund = get_object_or_404(MutualFund, pk=pk)
   if request.method == "POST":
       # update
       form = MutualfundForm(request.POST, instance=mutualfund)
       if form.is_valid():
           mutualfund = form.save(commit=False)
           mutualfund.updated_date = timezone.now()
           mutualfund.save()
           mutualfund = MutualFund.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/mutualfund_list.html',
                         {'mutualfunds': mutualfund})
   else:
        # edit
       form = MutualfundForm(instance=mutualfund)
   return render(request, 'portfolio/mutualfund_edit.html', {'form': form})

@login_required
def mutualfund_delete(request, pk):
   mutualfund = get_object_or_404(MutualFund, pk=pk)
   mutualfund.delete()
   return redirect('portfolio:mutualfund_list')

def signup_view(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('portfolio:home')
    return render(request, 'registration/signup.html', {'form': form})