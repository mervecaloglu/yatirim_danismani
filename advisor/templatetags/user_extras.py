from django import template
from advisor.models import UserProfile

register = template.Library()

@register.filter
def has_profile(user):
    return UserProfile.objects.filter(user=user).exists()

