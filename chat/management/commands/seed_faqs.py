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
        
    # Swastik's AI Development Services FAQ - Focused on Chatbot and Services
    faq_documents = [
        {
            'title': 'About Swastik - AI Developer & Freelancer',
            'content': 'Hi! I am Swastik, a specialized AI developer and freelancer. I build custom AI models, chatbots, automation workflows, and complete AI projects from scratch. I have expertise in Python, Django, OpenAI API, and various AI frameworks. I can help you implement AI solutions for your business needs. Check out my Upwork profile for more details!'
        },
        {
            'title': 'AI Chatbot Development Services',
            'content': 'I specialize in building intelligent chatbots and conversational AI systems: Customer service chatbots, Lead qualification bots, FAQ automation, Multi-language support, Voice-enabled assistants, Integration with CRM systems, Analytics and performance tracking, Custom training for domain-specific knowledge. Perfect for businesses looking to automate customer interactions.'
        },
        {
            'title': 'Custom AI Model Development',
            'content': 'I develop custom AI models for various business use cases: Text classification and sentiment analysis, Image recognition and computer vision, Predictive modeling for business forecasting, Recommendation engines for e-commerce, Fraud detection systems, Customer behavior analysis, Natural language generation, Custom neural networks for specific requirements. All models are tailored to your specific business needs.'
        },
        {
            'title': 'Automation Platform Expertise',
            'content': 'I specialize in automation platforms including Botpress for conversational AI, Make.com (formerly Integromat) for workflow automation, Zapier for app integrations, n8n for workflow automation, Microsoft Power Automate, and custom automation solutions. I can build complex workflows that connect multiple platforms and automate business processes to save you time and money.'
        },
        {
            'title': 'Full-Stack AI Projects',
            'content': 'I deliver complete AI projects including: Frontend development (React, Vue, Angular), Backend development (Django, Flask, FastAPI, Node.js), Database design and management, API development and integration, Cloud deployment (AWS, Google Cloud, Azure), Mobile app development, and Full-stack AI applications with user interfaces. End-to-end solutions for your business.'
        },
        {
            'title': 'Business Process Automation',
            'content': 'I automate business processes using AI and automation tools: Email marketing automation, Lead generation and qualification, Customer onboarding workflows, Data processing and analysis, Report generation, Social media management, Inventory management, and Custom business logic automation. Perfect for scaling your business operations.'
        },
        {
            'title': 'Data Analysis and Insights',
            'content': 'I provide data analysis services: Data cleaning and preprocessing, Statistical analysis and modeling, Business intelligence dashboards, Predictive analytics, Customer segmentation, Market trend analysis, Performance metrics and KPIs, and Data visualization and reporting. Turn your data into actionable business insights.'
        },
        {
            'title': 'Integration and APIs',
            'content': 'I specialize in system integrations: RESTful API development, Webhook implementations, Third-party service integrations, Database connections and migrations, Cloud service integrations, Payment gateway integrations, Social media API integrations, and Custom middleware development. Connect all your business tools seamlessly.'
        },
        {
            'title': 'Project Process and Timeline',
            'content': 'My development process includes: Initial consultation and requirements analysis, Project planning and timeline estimation, Regular progress updates and communication, Testing and quality assurance, Deployment and setup, Documentation and training, Ongoing support and maintenance, and Flexible project management approach. Transparent and professional service delivery.'
        },
        {
            'title': 'Pricing and Packages - Budget-Friendly',
            'content': 'I offer competitive pricing for startups and small businesses: Consultation calls: $25/hour, Simple chatbot development: $150-300, Basic automation workflows: $200-400, Custom AI models: $300-600, Full-stack AI projects: $500-1200, Monthly retainer for ongoing support: $200-500/month, Rush projects (24-48 hours): +50% premium, Payment plans available for larger projects. All prices include initial consultation, development, testing, and 30-day support.'
        },
        {
            'title': 'Technologies and Tools I Use',
            'content': 'I work with modern technologies: Python (Django, Flask, FastAPI), JavaScript (React, Vue, Node.js), Machine Learning (TensorFlow, PyTorch, Scikit-learn), Cloud platforms (AWS, Google Cloud, Azure), Databases (PostgreSQL, MongoDB, Redis), Automation tools (Botpress, Make.com, Zapier, n8n), AI APIs (OpenAI, Google AI, Anthropic), and DevOps tools (Docker, Kubernetes, CI/CD).'
        },
        {
            'title': 'Budget-Friendly Options for Startups',
            'content': 'Perfect for startups and small businesses: Starter package: $150-300 for basic chatbot or simple automation, Standard package: $300-600 for custom AI models with basic features, Premium package: $600-1200 for full-stack AI applications, Pay-as-you-go: $25/hour for consultation and small tasks, Monthly maintenance: $50-150/month for ongoing support, Special startup discount: 20% off first project, Payment plans: Split into 2-3 installments for projects over $500.'
        },
        {
            'title': 'What\'s Included in Every Project',
            'content': 'Every project includes: Free initial consultation (30 minutes), Detailed project proposal and timeline, Regular progress updates, Complete testing and quality assurance, Deployment and setup, Documentation and user guide, 30-day bug fix guarantee, Source code delivery, Basic training session, and Ongoing email support. No hidden fees or surprise charges.'
        },
        {
            'title': 'Why Choose Swastik for AI Development',
            'content': 'I offer: Specialized AI expertise with practical business focus, Budget-friendly pricing perfect for startups, Quick turnaround times (2-4 weeks for most projects), Comprehensive support and maintenance, Modern tech stack and best practices, Transparent communication throughout the project, Flexible payment options, and Proven track record on Upwork. Check my profile for reviews and portfolio!'
        },
        {
            'title': 'Contact and Hiring Information',
            'content': 'Ready to start your AI project? Contact me through: Upwork profile: https://www.upwork.com/freelancers/~01a3695131c30e858f, GitHub portfolio: https://github.com/swastik-21, Email consultation: Available for project discussions, Free initial consultation: 30 minutes to discuss your needs, Flexible scheduling: Available for calls and meetings, Quick response time: Usually respond within 24 hours. Let\'s discuss how AI can help your business!'
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



