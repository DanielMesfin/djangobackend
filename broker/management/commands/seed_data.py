"""
Django management command to seed the database with dummy data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import random
from decimal import Decimal

User = get_user_model()

try:
    from broker.models import (
        UserProfile, SocialLink, BusinessProfile, BusinessMember,
        Promotion, PromotionClaim, Transaction, Wallet,
        KYCVerification, BusinessDocument, Campaign, CampaignCollaborator,
        CampaignProduct, Listing, Conversation, Message, DraftOrder
    )
    from product.models import Product, Order, OrderItem, Review, Category
except ImportError as e:
    print(f"Import error: {e}")


class Command(BaseCommand):
    help = 'Seeds the database with dummy data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--businesses',
            type=int,
            default=20,
            help='Number of businesses to create (default: 20)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_users = options['users']
        num_businesses = options['businesses']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        # Create users
        self.stdout.write(f'Creating {num_users} users...')
        users = self.create_users(num_users)

        # Create businesses
        self.stdout.write(f'Creating {num_businesses} businesses...')
        businesses = self.create_businesses(num_businesses, users)

        # Create products and categories
        self.stdout.write('Creating products and categories...')
        categories = self.create_categories()
        products = self.create_products(users, categories)

        # Create orders
        self.stdout.write('Creating orders...')
        orders = self.create_orders(users, products)

        # Create transactions
        self.stdout.write('Creating transactions...')
        self.create_transactions(users)

        # Create campaigns
        self.stdout.write('Creating campaigns...')
        campaigns = self.create_campaigns(businesses, users)

        # Create promotions
        self.stdout.write('Creating promotions...')
        promotions = self.create_promotions(businesses)

        # Create listings
        self.stdout.write('Creating listings...')
        listings = self.create_listings(users, businesses)

        # Create conversations and messages
        self.stdout.write('Creating conversations...')
        self.create_conversations(users, listings)

        # Create KYC verifications
        self.stdout.write('Creating KYC verifications...')
        self.create_kyc_verifications(users)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully seeded database!'))
        self.stdout.write(f'   - {num_users} users created')
        self.stdout.write(f'   - {num_businesses} businesses created')
        self.stdout.write(f'   - {len(categories)} categories created')
        self.stdout.write(f'   - {len(products)} products created')
        self.stdout.write(f'   - {len(orders)} orders created')
        self.stdout.write(f'   - {len(campaigns)} campaigns created')
        self.stdout.write(f'   - {len(promotions)} promotions created')
        self.stdout.write(f'   - {len(listings)} listings created')

    def clear_data(self):
        """Clear existing data"""
        DraftOrder.objects.all().delete()
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        CampaignProduct.objects.all().delete()
        CampaignCollaborator.objects.all().delete()
        Campaign.objects.all().delete()
        PromotionClaim.objects.all().delete()
        Promotion.objects.all().delete()
        Listing.objects.all().delete()
        BusinessDocument.objects.all().delete()
        KYCVerification.objects.all().delete()
        Wallet.objects.all().delete()
        Transaction.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        BusinessMember.objects.all().delete()
        BusinessProfile.objects.all().delete()
        SocialLink.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count):
        """Create dummy users"""
        roles = [
            User.UserRole.USER,
            User.UserRole.BUSINESS_OWNER,
            User.UserRole.INFLUENCER,
            User.UserRole.SELLS_AGENT,
            User.UserRole.PREMIUM,
        ]
        
        users = []
        for i in range(count):
            # Check if user already exists
            email = f'user{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'password': 'pbkdf2_sha256$600000$dummy$dummy=',  # Will be set properly
                    'first_name': random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa']),
                    'last_name': random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']),
                    'phone': f'+1{random.randint(1000000000, 9999999999)}',
                    'role': random.choice(roles),
                    'is_verified': random.choice([True, False]),
                    'is_email_verified': random.choice([True, False]),
                    'is_active': True,
                    'date_joined': timezone.now() - timedelta(days=random.randint(0, 365)),
                }
            )
            
            # Set password if user was just created
            if created:
                user.set_password('password123')
                user.save()
            else:
                # Update existing user
                user.first_name = random.choice(['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa'])
                user.last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])
                user.role = random.choice(roles)
                user.is_verified = random.choice([True, False])
                user.save()
            
            # Update user profile (signal already creates it)
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': f'Bio for {user.first_name} {user.last_name}',
                    'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']),
                    'is_verified': random.choice([True, False]),
                }
            )
            # Update if it already existed
            if not profile_created:
                profile.bio = f'Bio for {user.first_name} {user.last_name}'
                profile.location = random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'])
                profile.is_verified = random.choice([True, False])
                profile.save()
            
            # Create or update wallet (signal might create it)
            wallet, wallet_created = Wallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': Decimal(str(random.uniform(0, 10000))),
                    'points': random.randint(0, 5000),
                }
            )
            # Update if it already existed
            if not wallet_created:
                wallet.balance = Decimal(str(random.uniform(0, 10000)))
                wallet.points = random.randint(0, 5000)
                wallet.save()
            
            users.append(user)
        
        return users

    def create_businesses(self, count, users):
        """Create dummy businesses"""
        business_types = [
            BusinessProfile.BusinessType.INDIVIDUAL,
            BusinessProfile.BusinessType.SMALL_BUSINESS,
            BusinessProfile.BusinessType.ENTERPRISE,
        ]
        
        industries = ['Technology', 'Finance', 'Healthcare', 'Retail', 'Food & Beverage', 'Fashion', 'Education']
        
        businesses = []
        # Get users who don't already have a business profile
        users_without_business = []
        for user in users:
            if not BusinessProfile.objects.filter(user=user).exists():
                users_without_business.append(user)
        
        # If we don't have enough users without businesses, we'll create fewer businesses
        if len(users_without_business) < count:
            self.stdout.write(self.style.WARNING(
                f'Only {len(users_without_business)} users available without businesses. Creating {len(users_without_business)} businesses instead of {count}.'
            ))
            count = len(users_without_business)
        
        # Shuffle to randomize selection
        random.shuffle(users_without_business)
        
        for i, owner in enumerate(users_without_business[:count]):
            # Double check the user doesn't have a business (race condition protection)
            if BusinessProfile.objects.filter(user=owner).exists():
                continue
            
            business, created = BusinessProfile.objects.get_or_create(
                user=owner,
                defaults={
                    'business_name': f"{random.choice(['Tech', 'Global', 'Premium', 'Elite', 'Pro'])} {random.choice(['Solutions', 'Corp', 'Group', 'Ltd', 'Inc'])} {i+1}",
                    'description': f"Leading {random.choice(industries)} company providing quality services.",
                    'industry': random.choice(industries),
                    'location': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston']),
                    'business_type': random.choice(business_types),
                    'is_verified': random.choice([True, False]),
                    'created_at': timezone.now() - timedelta(days=random.randint(0, 180)),
                }
            )
            
            # Update if it already existed (shouldn't happen, but just in case)
            if not created:
                business.business_name = f"{random.choice(['Tech', 'Global', 'Premium', 'Elite', 'Pro'])} {random.choice(['Solutions', 'Corp', 'Group', 'Ltd', 'Inc'])} {i+1}"
                business.description = f"Leading {random.choice(industries)} company providing quality services."
                business.industry = random.choice(industries)
                business.save()
            
            # Add business members
            for _ in range(random.randint(1, 5)):
                member = random.choice(users)
                if member != owner:
                    BusinessMember.objects.get_or_create(
                        business=business,
                        user=member,
                        defaults={'role': random.choice([BusinessMember.Role.OWNER, BusinessMember.Role.ADMIN, BusinessMember.Role.MANAGER, BusinessMember.Role.MEMBER])}
                    )
            
            businesses.append(business)
        
        return businesses

    def create_categories(self):
        """Create product categories"""
        categories = [
            'Electronics',
            'Clothing',
            'Food & Beverage',
            'Home & Garden',
            'Sports & Outdoors',
            'Books',
            'Toys & Games',
        ]
        
        created = []
        for name in categories:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'description': f'Products in {name} category'}
            )
            created.append(cat)
        
        return created

    def create_products(self, users, categories):
        """Create dummy products"""
        products = []
        sellers = [u for u in users if u.role in [User.UserRole.BUSINESS_OWNER, User.UserRole.SELLS_AGENT]]
        
        product_names = [
            'Premium Widget', 'Super Gadget', 'Ultra Device', 'Pro Tool',
            'Elite Product', 'Standard Item', 'Deluxe Model', 'Basic Unit'
        ]
        
        for i in range(100):
            product = Product.objects.create(
                seller=random.choice(sellers),
                category=random.choice(categories),
                name=f"{random.choice(product_names)} {i+1}",
                description=f"High-quality {random.choice(product_names).lower()} with excellent features.",
                price=Decimal(str(random.uniform(10, 1000))),
                stock=random.randint(0, 500),
                created_at=timezone.now() - timedelta(days=random.randint(0, 90)),
            )
            products.append(product)
        
        return products

    def create_orders(self, users, products):
        """Create dummy orders"""
        orders = []
        statuses = ['pending', 'processing', 'shipped', 'delivered']
        
        for _ in range(150):
            buyer = random.choice(users)
            order = Order.objects.create(
                buyer=buyer,
                order_date=timezone.now() - timedelta(days=random.randint(0, 60)),
                status=random.choice(statuses),
                total_amount=Decimal('0'),
                shipping_address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Park Blvd', 'Elm St'])}",
            )
            
            # Create order items
            total = Decimal('0')
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                price = product.price
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                )
                total += price * quantity
            
            order.total_amount = total
            order.save()
            orders.append(order)
        
        return orders

    def create_transactions(self, users):
        """Create dummy transactions"""
        transaction_types = ['deposit', 'withdrawal', 'purchase', 'refund', 'commission', 'bonus']
        statuses = ['pending', 'completed', 'failed', 'cancelled']
        
        for _ in range(200):
            Transaction.objects.create(
                user=random.choice(users),
                amount=Decimal(str(random.uniform(10, 5000))),
                transaction_type=random.choice(transaction_types),
                status=random.choice(statuses),
                reference=f"TXN{random.randint(100000, 999999)}",
                description=f"{random.choice(transaction_types).title()} transaction",
                created_at=timezone.now() - timedelta(days=random.randint(0, 90)),
            )

    def create_campaigns(self, businesses, users):
        """Create dummy campaigns"""
        campaigns = []
        statuses = ['DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED']
        
        for business in businesses[:10]:  # Create campaigns for first 10 businesses
            campaign = Campaign.objects.create(
                name=f"Campaign {business.business_name}",
                description=f"Marketing campaign for {business.business_name}",
                business=business,
                created_by=random.choice(users),
                status=random.choice(statuses),
                start_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90)),
                budget=Decimal(str(random.uniform(1000, 50000))),
            )
            
            # Add collaborators
            for _ in range(random.randint(1, 3)):
                collaborator = random.choice(users)
                CampaignCollaborator.objects.get_or_create(
                    campaign=campaign,
                    user=collaborator,
                    defaults={
                        'role': random.choice([CampaignCollaborator.CollaboratorRole.OWNER, CampaignCollaborator.CollaboratorRole.MANAGER, CampaignCollaborator.CollaboratorRole.CONTRIBUTOR]),
                        'status': random.choice([CampaignCollaborator.CollaboratorStatus.PENDING, CampaignCollaborator.CollaboratorStatus.ACCEPTED, CampaignCollaborator.CollaboratorStatus.REJECTED]),
                    }
                )
            
            campaigns.append(campaign)
        
        return campaigns

    def create_promotions(self, businesses):
        """Create dummy promotions"""
        promotions = []
        categories = ['FOOD', 'FASHION', 'ELECTRONICS', 'BEAUTY', 'HOME', 'SPORTS']
        
        for business in businesses[:15]:
            promotion = Promotion.objects.create(
                business=business,
                title=f"Special Offer - {business.business_name}",
                description=f"Limited time promotion from {business.business_name}",
                category=random.choice(categories),
                points_cost=random.randint(100, 1000),
                max_claims=random.randint(50, 500),
                current_claims=random.randint(0, 100),
                start_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                end_date=timezone.now() + timedelta(days=random.randint(30, 90)),
                is_active=random.choice([True, False]),
            )
            
            # Create some claims
            for _ in range(random.randint(0, 20)):
                user = random.choice(list(User.objects.all()[:50]))
                PromotionClaim.objects.get_or_create(
                    user=user,
                    promotion=promotion,
                    defaults={
                        'points': promotion.points_cost,
                        'shared_count': random.randint(0, 10),
                    }
                )
            
            promotions.append(promotion)
        
        return promotions

    def create_listings(self, users, businesses):
        """Create dummy listings"""
        listings = []
        listing_types = ['PRODUCT', 'SERVICE', 'JOB', 'EVENT']
        statuses = ['DRAFT', 'PUBLISHED', 'ARCHIVED', 'SOLD']
        
        for i in range(80):
            listing = Listing.objects.create(
                title=f"Listing {i+1} - {random.choice(['Premium', 'Standard', 'Elite'])}",
                description=f"High-quality listing with great features and benefits.",
                listing_type=random.choice(listing_types),
                price=Decimal(str(random.uniform(50, 5000))),
                category=random.choice(['Electronics', 'Services', 'Jobs', 'Events']),
                user=random.choice(users),
                business=random.choice(businesses) if random.choice([True, False]) else None,
                status=random.choice(statuses),
                is_active=random.choice([True, False]),
                quantity=random.randint(1, 100),
                created_at=timezone.now() - timedelta(days=random.randint(0, 60)),
            )
            listings.append(listing)
        
        return listings

    def create_conversations(self, users, listings):
        """Create dummy conversations and messages"""
        for listing in listings[:30]:
            buyer = random.choice(users)
            seller = listing.user if listing.user else random.choice(users)
            
            if buyer != seller:
                conversation, created = Conversation.objects.get_or_create(
                    listing=listing,
                    buyer=buyer,
                    seller=seller,
                    defaults={
                        'status': random.choice(['ACTIVE', 'ARCHIVED', 'COMPLETED']),
                    }
                )
                
                if created:
                    # Create some messages
                    for _ in range(random.randint(2, 10)):
                        Message.objects.create(
                            conversation=conversation,
                            sender=random.choice([buyer, seller]),
                            content=random.choice([
                                "Hello, I'm interested in this listing.",
                                "What's the condition?",
                                "Is this still available?",
                                "Can you provide more details?",
                                "What's the best price?",
                                "When can I pick it up?",
                            ]),
                            message_type='TEXT',
                            is_read=random.choice([True, False]),
                            created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                        )

    def create_kyc_verifications(self, users):
        """Create dummy KYC verifications"""
        document_types = ['PASSPORT', 'NATIONAL_ID', 'DRIVING_LICENSE', 'UTILITY_BILL']
        statuses = ['PENDING', 'APPROVED', 'REJECTED']
        
        for user in users[:30]:
            KYCVerification.objects.create(
                user=user,
                document_type=random.choice(document_types),
                document_number=f"DOC{random.randint(100000, 999999)}",
                document_front=f"https://example.com/docs/{user.id}/front.jpg",
                document_back=f"https://example.com/docs/{user.id}/back.jpg" if random.choice([True, False]) else None,
                status=random.choice(statuses),
                created_at=timezone.now() - timedelta(days=random.randint(0, 60)),
            )

