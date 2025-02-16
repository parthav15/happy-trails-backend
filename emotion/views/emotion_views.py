from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from deepface import DeepFace
from emotion.models import CustomUser, UploadedImage, Recommendation
from emotion.utils import jwt_decode, auth_user
import requests
import random

def analyze_emotions(image_path):
    analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    if isinstance(analysis, list):
        analysis = analysis[0]
    emotions = analysis.get('emotion', {})
    if not emotions:
        return None, None
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    dominant_emotion = sorted_emotions[0][0]
    secondary_emotion = sorted_emotions[1][0] if len(sorted_emotions) > 1 else None
    return dominant_emotion, secondary_emotion

def get_travel_destination_recommendations(dominant_emotion, secondary_emotion=None):
    api_key = "AIzaSyDIIydfxdqoslmjtw_tdYjO4Fo4zRp1DwE"
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    emotion_to_keywords = {
        "happy": ["vibrant city", "sunny beach", "festival"],
        "sad": ["serene retreat", "countryside escape", "wellness resort"],
        "angry": ["adventure travel", "extreme sports", "cultural immersion"],
        "surprised": ["off the beaten path", "hidden gem", "unusual destination"],
        "neutral": ["popular destinations", "must see places"],
        "fear": ["safe travel spots", "secure vacation"],
        "disgust": ["refreshing destination", "clean resort"]
    }
    keywords = []
    if dominant_emotion and dominant_emotion.lower() in emotion_to_keywords:
        keywords.extend(emotion_to_keywords[dominant_emotion.lower()])
    if secondary_emotion and secondary_emotion.lower() in emotion_to_keywords:
        keywords.extend(emotion_to_keywords[secondary_emotion.lower()])
    if keywords:
        selected_keyword = random.choice(keywords)
        query = f"{selected_keyword} travel destination"
    else:
        query = f"{dominant_emotion} travel destination" if dominant_emotion else "travel destination"
    params = {
        "query": query,
        "key": api_key,
        "fields": "formatted_address,name,place_id,photos",
        "language": "en"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    results = []
    for place in data.get('results', []):
        photo_ref = place.get('photos', [{}])[0].get('photo_reference', '')
        thumbnail = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}" if photo_ref else ''
        results.append({
            'name': place.get('name', 'Unknown'),
            'address': place.get('formatted_address', ''),
            'url': f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
            'thumbnail': thumbnail
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
        image = UploadedImage.objects.create(user=user, image=uploaded_file)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error uploading image: {e}"}, status=400)
    try:
        dominant_emotion, secondary_emotion = analyze_emotions(image.image.path)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Emotion detection failed: {e}"}, status=400)
    try:
        recommendations = get_travel_destination_recommendations(dominant_emotion, secondary_emotion)
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
        "success": True,
        "message": "Emotion detection and recommendation completed",
        "dominant_emotion": dominant_emotion.capitalize(),
        "secondary_emotion": secondary_emotion,
        "recommendations": saved_recommendations
    }, status=200)
