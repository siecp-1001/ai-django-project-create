from django.http import JsonResponse

def list_products(request):
    return JsonResponse({'message': 'Hello from list_products'})

