from .models import StoreInfo

def store_info(request):
    try:
        # Get the first record (there should only be one)
        info = StoreInfo.objects.first()
        if not info:
            # Create a default if it doesn't exist
            info = StoreInfo.objects.create()
    except:
        info = None
        
    return {'store_info': info}
