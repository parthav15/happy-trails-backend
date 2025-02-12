import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict

from emotion.models import CustomUser, Feedback

from emotion.utils import jwt_decode, auth_user

# =============================== #
# ======== Feedback API's ======= #
# =============================== #
@csrf_exempt
@require_http_methods(["POST"])
def add_feedback_view(request):
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
    
    comment = data.get('comment')
    rating = data.get('rating')

    if not comment or not rating:
        return JsonResponse({'success': False, 'message': 'Comment and rating are required.'}, status=400)

    try:
        feedback = Feedback.objects.create(
            user=user,
            comment=comment,
            rating=rating
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error adding feedback: {e}"}, status=500)

    return JsonResponse({"success": True, "message": "Feedback added successfully.", "feedback": model_to_dict(feedback)}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_publish_feedback_view(request):
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
    
    feedback_id = data.get('feedback_id')

    if not feedback_id:
        return JsonResponse({'success': False, 'message': 'Feedback id is required.'}, status=400)

    try:
        feedback = Feedback.objects.get(id=feedback_id, user=user)
        feedback.publish = not feedback.publish
        feedback.save()
    except Feedback.DoesNotExist:
        return JsonResponse({"success": False, "message": "Feedback not found."}, status=404)

    return JsonResponse({"success": True, "message": "Feedback publish status toggled successfully.", "feedback": model_to_dict(feedback)}, status=200)


@require_http_methods(["GET"])
def get_feedbacks_view(request):
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

    feedbacks = Feedback.objects.filter(user=user, publish=True)
    feedbacks = [model_to_dict(f) for f in feedbacks]

    return JsonResponse({"success": True, "message": "Feedbacks fetched successfully.", "feedbacks": feedbacks}, status=200)
