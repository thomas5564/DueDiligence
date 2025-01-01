from django.shortcuts import render
from django.http import HttpResponseRedirect
from .Scrape import scrape
from .Finance import help,get_screen,construct_finviz_url,tabulate,sample
from .vis import plot_combined
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from django.http import HttpResponse

matplotlib.use('Agg')  # Use a non-interactive backend


def index(request):
    # Initialize or retrieve ScrapeMode from the session
    if 'ScrapeMode' not in request.session:
        request.session['ScrapeMode'] = True  # Default to True
    if 'tickers' not in request.session:
        request.session['tickers'] = []  # Initialize an empty list for tickers
    tickers = []  # Initialize an empty list for tickers
    data = []

    if request.method == 'POST':
        if 'url' in request.POST:  # Handle URL input
            if request.session['ScrapeMode']:
                url = request.POST.get('url')  # Get the URL from the form
                if url:
                    tickers = scrape(url)  # Call the scrape function
                    data = help(tickers)  # Process tickers with help()
                    print(data)  # Debugging
                    return render(request, 'myapp/index.html', {
                        'tickers': tickers,
                        'data': data,
                        'ScrapeMode': request.session['ScrapeMode']
                    })
            else:
                tickers = request.session['tickers']
                CurrentTicker = request.POST.get('url').upper()
                if CurrentTicker not in tickers:
                    tickers.append(CurrentTicker)
                request.session['tickers'] = tickers
                return render(request, 'myapp/index.html', {
                    'tickers': tickers,
                    'ScrapeMode': request.session['ScrapeMode']
                })
            
        if 'ScrapeMode' in request.POST:  # Toggle ScrapeMode
            request.session['ScrapeMode'] = not request.session['ScrapeMode']
            if request.session['ScrapeMode'] == False:
                request.session['tickers'] = []
        if 'dd' in request.POST:
            tickers = request.session['tickers']
            print(tickers)
            data = help(tickers)
            return render(request, 'myapp/index.html', {
        'tickers': tickers,
        'data': data,
        'ScrapeMode': request.session['ScrapeMode']
    })
        if 'clear' in request.POST:
            request.session['tickers'] = []
            return render(request, 'myapp/index.html', {
        'tickers': [],
        'data': [],
        'ScrapeMode': request.session['ScrapeMode']
    })

    # Render the template for GET or after handling POST
    return render(request, 'myapp/index.html', {
        'tickers': tickers,
        'data': data,
        'ScrapeMode': request.session['ScrapeMode']
    })

def details(request, ticker):
    screen = get_screen(ticker)
    link = construct_finviz_url(screen)
    competitors = scrape(link)
    basket = sample(competitors,ticker)
    data = tabulate(basket)
    deetslink = f"https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1"

    context = {
        'ticker': ticker,
        'details': f"Details about {ticker}",
        'data':data,
        'screen':screen,
        'link':deetslink
    }

    request.session['shared_data'] = data
    request.session['ticker'] = ticker
    return render(request, 'myapp/details.html', context)

def plot_tgt(request):
    ticker = request.session.get('ticker',"")
    data = request.session.get('shared_data', [])
    plot_combined(data,ticker)
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()  # Close the plot to free resources
    buffer.seek(0)
    
    # Serve the plot as a response
    return HttpResponse(buffer, content_type='image/png')



