from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from deepface import DeepFace

from emotion.models import CustomUser, UploadedImage, Recommendation

from googleapiclient.discovery import build

from emotion.utils import jwt_decode, auth_user

# =============================== #
# ======== Emotion API's ========== #
# =============================== #

def detect_emotion(image_path):
    obj = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    if obj:
        return obj[0]['dominant_emotion']
    return None

def get_travel_destination_recommendations(emotion):
    api_key = "AIzaSyCQBhcuRb3hLqK4XmBv7X0hT9KXbY6QhMZY"
    places_api = build('places', 'v1', developerKey=api_key)
    query = f"{emotion.lower()} travel destinations"
    request = places_api.textSearch(query=query)
    response = request.execute()
    results = []
    for result in response['results']:
        results.append({
            'name': result['name'],
            'address': result['formatted_address'],
            'url': f"https://www.google.com/maps/search/?api=1&query={result['name']}"
        })
    return results

@csrf_exempt
@require_http_methods(["POST"])
def emotion_detection_view(request):
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
    
    uploaded_file = request.FILES.get('image')
    if not uploaded_file:
        return JsonResponse({"success": False, "message": "No image uploaded"}, status=400)

    try:
        image = UploadedImage.objects.create(
            user=user,
            image=uploaded_file
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error uploading image: {e}"}, status=400)

    try:
        emotion = detect_emotion(image.image.path)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Emotion detection failed: {e}"}, status=400)

    try:
        recommendations = get_travel_destination_recommendations(emotion)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error getting travel recommendations: {e}"}, status=500)
    
    saved_recommendations = []
    for recommendation in recommendations:
        try:
            saved_recommendation = Recommendation.objects.create(
                user=user,
                uploaded_image=image,
                destination_name=recommendation['name'],
                destination_url=recommendation['url'],
                destination_thumbnail=recommendation.get('thumbnail', '')
            )
            saved_recommendations.append({
                "id": saved_recommendation.id,
                "destination_name": saved_recommendation.destination_name,
                "destination_url": saved_recommendation.destination_url,
                "destination_thumbnail": saved_recommendation.destination_thumbnail,
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error creating recommendation: {e}"}, status=500)

    return JsonResponse({
        "emotion": emotion,
        "recommendations": saved_recommendations
    }, status=200)

