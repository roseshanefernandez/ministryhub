"""
Custom Django Template Tags for Prayer Requests
Location: ministryhub/templatetags/prayer_tags.py

Updated with correct prayer categories from models.py
"""

from django import template

register = template.Library()


# ============================================
# FILTERS
# ============================================


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Custom filter to safely get dictionary items in templates.

    Usage in template (FILTER syntax):
    {% with category_prayers=prayer_requests_by_category|get_item:category_code %}
        {% if category_prayers %}
            ...
        {% endif %}
    {% endwith %}

    Args:
        dictionary: Dictionary object
        key: Key to retrieve from dictionary

    Returns:
        Value from dictionary or empty list if key not found
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []


@register.filter(name="category_display_name")
def category_display_name(category_code):
    """
    Convert category code to display name.

    Usage in template (FILTER syntax):
    {{ category|category_display_name }}

    Args:
        category_code: Category code

    Returns:
        Display name for the category
    """
    display_names = {
        "Thanksgiving": "Thanksgiving",
        "Healing and Good Health": "Healing and Good Health",
        "Souls": "Souls",
        "Safety and Protection": "Safety and Protection",
        "Financial Abundance": "Financial Abundance",
        "Guidance and Protection": "Guidance and Protection",
        "Special Intentions": "Special Intentions",
    }
    return display_names.get(category_code, category_code)


# ============================================
# SIMPLE TAGS (assignment tags)
# ============================================


@register.simple_tag
def get_prayer_count_for_category(prayers_dict, category):
    """
    Get number of prayers in a specific category.

    Usage in template (SIMPLE TAG syntax):
    {% get_prayer_count_for_category prayer_requests_by_category category_code as count %}

    Args:
        prayers_dict: Dictionary of prayers by category
        category: Category code

    Returns:
        Count of prayers in category
    """
    if isinstance(prayers_dict, dict):
        prayers = prayers_dict.get(category, [])
        return len(prayers) if prayers else 0
    return 0


# ============================================
# HELPER TAG (optional utility)
# ============================================


@register.simple_tag
def get_dict_item(dictionary, key, default=None):
    """
    Alternative simple tag for getting dictionary items.

    Usage in template:
    {% get_dict_item prayer_requests_by_category category_code as category_prayers %}

    Args:
        dictionary: Dictionary object
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value from dictionary or default
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, default or [])
    return default or []
