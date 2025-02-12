from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    password = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            output_size = (200, 200)
            if img.height > 200 or img.width > 200:
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class UploadedImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_images')
    image = models.ImageField(upload_to='uploaded_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image by {self.user.username} - {self.uploaded_at}"


class RecommendationInteraction(models.Model):
    ACTIONS = (
        ('Clicked', 'Clicked'),
        ('Skipped', 'Skipped'),
        ('Liked', 'Liked'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class Recommendation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recommendations')
    uploaded_image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='recommendations')
    destination_name = models.CharField(max_length=255)
    destination_url = models.URLField()
    destination_thumbnail = models.URLField()
    recommended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination_name} for {self.user.username}"

class Feedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedbacks')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    publish = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback by {self.user.username} - {self.rating} Stars"
    
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=255)
    url = models.URLField()
    thumbnail_url = models.URLField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.wishlist.name}"
