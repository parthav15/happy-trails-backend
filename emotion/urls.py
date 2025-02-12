from django.urls import path
from emotion.views import emotion_views, feedback_views, wishlist_views, user_views

urlpatterns = [
    # USER URL'S
    path('user_register/', user_views.user_register, name='user_register'),
    path('user_login/', user_views.user_login, name='user_login'),
    path('edit_user/', user_views.edit_user, name='edit_user'),
    path('user_details/', user_views.user_details, name='user_details'),

    # EMOTION DETECTION URL'S
    path('emotion_detection/', emotion_views.emotion_detection_view, name='emotion_detection_view'),
    
    # FEEDBACK URL'S
    path('add_feedback/', feedback_views.add_feedback_view, name='add_feedback'),
    path('toggle_publish_feedback/', feedback_views.toggle_publish_feedback_view, name='toggle_publish_feedback'),
    path('get_feedbacks/', feedback_views.get_feedbacks_view, name='get_feedbacks'),
    
    # WISHLIST URL'S
    path('create_wishlist/', wishlist_views.create_wishlist_view, name='create_wishlist'),
    path('delete_wishlist/<int:wishlist_id>/', wishlist_views.delete_wishlist_view, name='delete_wishlist'),
    path('get_wishlists/', wishlist_views.get_wishlists_view, name='get_wishlists'),
    path('get_wishlist_details/<int:wishlist_id>/', wishlist_views.get_wishlist_details_view, name='get_wishlist_details'),
    path('add_recommendation_to_wishlist/<int:wishlist_id>/', wishlist_views.add_recommendation_to_wishlist_view, name='add_recommendation_to_wishlist'),
    path('delete_recommendation_from_wishlist/<int:wishlist_id>/', wishlist_views.delete_recommendation_from_wishlist_view, name='delete_recommendation_from_wishlist'),
]

