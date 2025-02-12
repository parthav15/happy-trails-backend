import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from emotion.models import CustomUser, Recommendation, Wishlist, WishlistItem

from emotion.utils import jwt_decode, auth_user

# =============================== #
# ======== Playlist API's ======= #
# =============================== #
@csrf_exempt
@require_http_methods(["POST"])
def create_wishlist_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    name = data.get('name')
    if not name:
        return JsonResponse({'success': False, 'message': 'Wishlist name is required.'}, status=400)

    try:
        wishlist = Wishlist.objects.create(
            user=user,
            name=name
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error creating wishlist: {e}"}, status=500)

    return JsonResponse({
        "id": wishlist.id,
        "name": wishlist.name,
        "created_at": wishlist.created_at.isoformat(),
        "updated_at": wishlist.updated_at.isoformat()
    }, status=201)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_wishlist_view(request, wishlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Wishlist not found.'}, status=404)
    
    wishlist.delete()
    return JsonResponse({'success': True}, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def get_wishlists_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    wishlists = Wishlist.objects.filter(user=user)
    data = []
    for wishlist in wishlists:
        data.append({
            "id": wishlist.id,
            "name": wishlist.name,
            "created_at": wishlist.created_at.isoformat(),
            "updated_at": wishlist.updated_at.isoformat()
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def get_wishlist_details_view(request, wishlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Wishlist not found."}, status=404)

    wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    data = []
    for wishlist_item in wishlist_items:
        data.append({
            "id": wishlist_item.id,
            "title": wishlist_item.recommendation.song_title,
            "url": wishlist_item.recommendation.song_url,
            "thumbnail_url": wishlist_item.recommendation.song_thumbnail,
            "added_at": wishlist_item.added_at.isoformat()
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def add_recommendation_to_wishlist_view(request, wishlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Wishlist not found."}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    recommendation_id = data.get('recommendation_id')

    if not recommendation_id:
        return JsonResponse({'success': False, 'message': 'Recommendation id is required.'}, status=400)

    try:
        recommendation = Recommendation.objects.get(id=recommendation_id)
    except Recommendation.DoesNotExist:
        return JsonResponse({"success": False, "message": "Recommendation not found."}, status=404)

    try:
        wishlist_item = WishlistItem.objects.create(
            wishlist=wishlist,
            recommendation=recommendation
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error adding recommendation to wishlist: {e}"}, status=500)

    return JsonResponse({
        "id": wishlist_item.id,
        "title": wishlist_item.recommendation.song_title,
        "url": wishlist_item.recommendation.song_url,
        "thumbnail_url": wishlist_item.recommendation.song_thumbnail,
        "added_at": wishlist_item.added_at.isoformat()
    }, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def delete_recommendation_from_wishlist_view(request, wishlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=user)
    except Wishlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Wishlist not found."}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    recommendation_id = data.get('recommendation_id')

    if not recommendation_id:
        return JsonResponse({'success': False, 'message': 'Recommendation id is required.'}, status=400)

    try:
        wishlist_item = WishlistItem.objects.get(id=recommendation_id, wishlist=wishlist)
        wishlist_item.delete()
    except WishlistItem.DoesNotExist:
        return JsonResponse({"success": False, "message": "Recommendation not found in wishlist."}, status=404)

    return JsonResponse({"success": True, "message": "Recommendation deleted from wishlist successfully."}, status=200)
