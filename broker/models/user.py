from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Add custom related_name to avoid clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='broker_user_set',
        related_query_name='broker_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='broker_user_permissions_set',
        related_query_name='broker_user_permissions',
    )
    
    class UserRole(models.TextChoices):
        USER = 'USER', _('User')
        SELLS_AGENT = 'SELLS_AGENT', _('Sells Agent')
        ADMIN = 'ADMIN', _('Admin')
        MODERATOR = 'MODERATOR', _('Moderator')
        PREMIUM = 'PREMIUM', _('Premium')
        BUSINESS_OWNER = 'BUSINESS_OWNER', _('Business Owner')
        INFLUENCER = 'INFLUENCER', _('Influencer')

    class AuthProvider(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        GOOGLE = 'GOOGLE', _('Google')
        FACEBOOK = 'FACEBOOK', _('Facebook')

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    second_name = models.CharField(_('second name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30)
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    bio = models.TextField(_('bio'), blank=True, null=True)
    avatar_url = models.URLField(_('avatar URL'), blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    is_email_verified = models.BooleanField(_('email verified'), default=False)
    email_verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verification_expires = models.DateTimeField(blank=True, null=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_expires = models.DateTimeField(blank=True, null=True)
    role = models.CharField(_('role'), max_length=20, choices=UserRole.choices, default=UserRole.USER)
    auth_provider = models.CharField(_('auth provider'), max_length=20, choices=AuthProvider.choices, default=AuthProvider.EMAIL)
    premium_until = models.DateTimeField(_('premium until'), blank=True, null=True)
    points = models.IntegerField(_('points'), default=0)
    referral_code = models.CharField(_('referral code'), max_length=100, blank=True, null=True)
    refresh_token = models.TextField(_('refresh token'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email
    
    # Role-based helper methods
    def is_business_owner(self):
        """Check if user is a business owner"""
        return self.role == self.UserRole.BUSINESS_OWNER
    
    def is_influencer(self):
        """Check if user is an influencer"""
        return self.role == self.UserRole.INFLUENCER
    
    def is_sells_agent(self):
        """Check if user is a sells agent"""
        return self.role == self.UserRole.SELLS_AGENT
    
    def is_premium(self):
        """Check if user has premium access"""
        if self.role == self.UserRole.PREMIUM:
            if self.premium_until:
                return timezone.now() < self.premium_until
            return True
        return False
    
    def is_moderator(self):
        """Check if user is a moderator"""
        return self.role == self.UserRole.MODERATOR
    
    def is_admin_user(self):
        """Check if user is an admin (not superuser)"""
        return self.role == self.UserRole.ADMIN
    
    def get_role_display_name(self):
        """Get human-readable role name"""
        return self.get_role_display()
    
    def get_full_name(self):
        """Get user's full name"""
        if self.second_name:
            return f"{self.first_name} {self.second_name} {self.last_name}".strip()
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Get user's short name"""
        return self.first_name
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active"""
        if self.role == self.UserRole.PREMIUM and self.premium_until:
            return timezone.now() < self.premium_until
        return False
    
    @property
    def can_create_business(self):
        """Check if user can create a business profile"""
        return self.role in [
            self.UserRole.BUSINESS_OWNER,
            self.UserRole.PREMIUM,
            self.UserRole.INFLUENCER
        ]
    
    @property
    def can_moderate(self):
        """Check if user has moderation permissions"""
        return self.role in [
            self.UserRole.MODERATOR,
            self.UserRole.ADMIN
        ] or self.is_staff or self.is_superuser

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'role']),
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('bio'), blank=True, null=True)
    avatar = models.URLField(_('avatar URL'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    location = models.CharField(_('location'), max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"

class SocialLink(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='social_links')
    facebook_url = models.URLField(_('Facebook'), blank=True, null=True)
    instagram_url = models.URLField(_('Instagram'), blank=True, null=True)
    tiktok_url = models.URLField(_('TikTok'), blank=True, null=True)
    youtube_url = models.URLField(_('YouTube'), blank=True, null=True)
    linkedin_url = models.URLField(_('LinkedIn'), blank=True, null=True)
    twitter_url = models.URLField(_('Twitter'), blank=True, null=True)
    telegram_url = models.URLField(_('Telegram'), blank=True, null=True)
    whatsapp_number = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    website_url = models.URLField(_('Website'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f"{self.user_profile.user.email}'s social links"
