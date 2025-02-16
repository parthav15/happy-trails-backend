from django.urls import path
from community.views import comment_views, post_views, reply_views, like_views, savedpost_views, report_views

urlpatterns = [
    # POST API'S
    path('posts/', post_views.list_all_posts, name='list_all_posts'),
    path('posts/<int:post_id>/', post_views.get_post_by_id, name='get_post_by_id'),
    path('create_post/', post_views.create_post, name='create_post'),
    path('edit_post/<int:post_id>/', post_views.update_post, name='update_post'),
    path('delete_post/<int:post_id>/', post_views.delete_post, name='delete_post'),
    path('list_posts_by_user/', post_views.list_posts_by_user, name='list_posts_by_user'),

    # COMMENT API'S
    path('list_specific_comment/<int:comment_id>/', comment_views.retrieve_comment_view, name='retrieve_comment'),
    path('create_comment/<int:post_id>/', comment_views.create_comment_view, name='create_comment'),
    path('edit_comment/<int:comment_id>/', comment_views.update_comment_view, name='update_comment'),
    path('delete_comment/<int:comment_id>/', comment_views.delete_comment_view, name='delete_comment'),
    path('posts/<int:post_id>/comments/', comment_views.list_comments_for_post_view, name='list_comments_for_post'),

    # REPLY API'S
    path('replies/', reply_views.list_all_replies, name='list_all_replies'),
    path('list_specific_reply/<int:reply_id>/', reply_views.retrieve_reply, name='retrieve_reply'),
    path('create_reply/<int:comment_id>/', reply_views.create_reply, name='create_reply'),
    path('edit_reply/<int:reply_id>/', reply_views.update_reply, name='update_reply'),
    path('delete_reply/<int:reply_id>/', reply_views.delete_reply, name='delete_reply'),
    path('comments/<int:comment_id>/replies/', reply_views.list_replies_for_comment, name='list_replies_for_comment'),

    # LIKE API'S
    path('likes/', like_views.list_likes_view, name='list_likes_view'),
    path('toggle_like/<int:post_id>/', like_views.toggle_like_view, name='toggle_like_view'),
    path('users/<str:user_email>/likes/', like_views.list_posts_liked_by_user_view, name='list_posts_liked_by_user_view'),

    # SAVED POST API'S
    path('saved_posts/', savedpost_views.list_all_saved_posts, name='list_all_saved_posts'),
    path('users/saved_posts/<str:user_email>/', savedpost_views.list_saved_posts_by_user, name='list_saved_posts_by_user'),
    path('create_saved_posts/', savedpost_views.create_saved_post, name='create_saved_post'),
    path('delete_saved_posts/<int:post_id>/', savedpost_views.remove_saved_post, name='remove_saved_post'),

    # REPORT API'S
    path('reports/', report_views.list_all_reports_view, name='list_all_reports'),
    path('get_specific_report/<int:report_id>/', report_views.retrieve_report_view, name='retrieve_report'),
    path('create_report/', report_views.create_report_view, name='create_report'),
    path('edit_report/<int:report_id>/', report_views.update_report_view, name='update_report'),
    path('delete_report/<int:report_id>/', report_views.delete_report_view, name='delete_report'),
    path('posts/reports/<int:post_id>/', report_views.list_reports_for_post_view, name='list_reports_for_post'),
    path('comments/reports/<int:comment_id>/', report_views.list_reports_for_comment_view, name='list_reports_for_comment'),
    path('users/reports/<int:user_id>/', report_views.list_reports_by_user_view, name='list_reports_by_user'),
]

