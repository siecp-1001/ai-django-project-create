from django.http import JsonResponse

def list_products(request):
    return JsonResponse({'message': 'Hello from list_products'})

def create_product(request):
    return JsonResponse({'message': 'Hello from create_product'})

def get_product(request):
    return JsonResponse({'message': 'Hello from get_product'})

def update_product(request):
    return JsonResponse({'message': 'Hello from update_product'})

def delete_product(request):
    return JsonResponse({'message': 'Hello from delete_product'})

