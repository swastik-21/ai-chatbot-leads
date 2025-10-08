from django.core.management.base import BaseCommand
from chat.services.retriever import retriever


class Command(BaseCommand):
    help = 'Seed the FAISS index with sample FAQ documents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing index before seeding',
        )

    def handle(self, *args, **options):
        """Seed the FAISS index with sample FAQ documents."""
        
        if options['clear']:
            self.stdout.write('Clearing existing index...')
            # Clear existing index by creating a new one
            retriever.index = None
            retriever.documents = []
            retriever._load_or_create_index()
        
        # Sample FAQ documents
        faq_documents = [
            {
                'title': 'Product Information',
                'content': 'Our company offers premium software solutions for businesses. We provide cloud-based platforms, mobile applications, and custom development services. Our products are designed to increase productivity and streamline operations.'
            },
            {
                'title': 'Pricing Plans',
                'content': 'We offer three pricing tiers: Basic ($29/month), Professional ($79/month), and Enterprise ($199/month). All plans include 24/7 support, regular updates, and cloud storage. Enterprise plans include custom integrations and dedicated account management.'
            },
            {
                'title': 'Support and Contact',
                'content': 'Our support team is available 24/7 via email, chat, and phone. You can reach us at support@company.com or call 1-800-SUPPORT. We also have a comprehensive knowledge base and video tutorials available on our website.'
            },
            {
                'title': 'Features Overview',
                'content': 'Key features include: Real-time collaboration, Advanced analytics dashboard, Mobile app for iOS and Android, API access for integrations, Automated backups, Multi-language support, Custom branding options, and Advanced security features including 2FA and SSO.'
            },
            {
                'title': 'Getting Started',
                'content': 'To get started, simply sign up for a free trial account. You can import your existing data, invite team members, and customize your workspace. Our onboarding process includes guided tutorials and a dedicated success manager for Enterprise customers.'
            },
            {
                'title': 'Security and Compliance',
                'content': 'We take security seriously. Our platform is SOC 2 Type II compliant, uses end-to-end encryption, and follows industry best practices. We offer GDPR compliance tools, data residency options, and regular security audits. All data is backed up daily with 99.9% uptime guarantee.'
            },
            {
                'title': 'Integration Options',
                'content': 'Our platform integrates with popular tools including Salesforce, Slack, Microsoft Teams, Google Workspace, Zapier, and many others. We provide REST APIs, webhooks, and pre-built connectors. Custom integrations are available for Enterprise customers.'
            },
            {
                'title': 'Training and Resources',
                'content': 'We offer comprehensive training resources including live webinars, recorded tutorials, documentation, and certification programs. Our customer success team provides personalized training sessions and ongoing support to ensure your team gets the most value from our platform.'
            },
            {
                'title': 'Billing and Payments',
                'content': 'We accept all major credit cards, PayPal, and bank transfers. Billing is monthly or annual with discounts available for annual subscriptions. You can upgrade, downgrade, or cancel your subscription at any time through your account dashboard. Refunds are available within 30 days of purchase.'
            },
            {
                'title': 'System Requirements',
                'content': 'Our platform is web-based and works on all modern browsers including Chrome, Firefox, Safari, and Edge. Mobile apps are available for iOS 12+ and Android 8+. No special hardware requirements - just a stable internet connection. We recommend at least 4GB RAM and 2GB free disk space for optimal performance.'
            }
        ]
        
        self.stdout.write(f'Adding {len(faq_documents)} FAQ documents to FAISS index...')
        
        try:
            retriever.add_documents(faq_documents)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully seeded FAISS index with {len(faq_documents)} documents'
                )
            )
            
            # Test the index
            test_query = "What are your pricing plans?"
            results = retriever.search(test_query, top_k=3)
            
            self.stdout.write(f'\nTest search for "{test_query}":')
            for i, result in enumerate(results, 1):
                self.stdout.write(f'{i}. {result["title"]} (score: {result["score"]:.3f})')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding FAISS index: {str(e)}')
            )
            raise


