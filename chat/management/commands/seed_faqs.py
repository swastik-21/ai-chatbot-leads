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
        
        # Swastik's AI Development Services FAQ
        faq_documents = [
            {
                'title': 'About Swastik - AI Developer',
                'content': 'Hi! I am Swastik, a specialized AI developer and freelancer. I build custom AI models, machine learning solutions, and complete AI projects from scratch. I have expertise in Python, TensorFlow, PyTorch, OpenAI API, and various AI frameworks. I can help you implement AI solutions for your business needs.'
            },
            {
                'title': 'AI Development Services',
                'content': 'I offer comprehensive AI development services including: Custom AI model development, Machine learning solutions, Natural language processing (NLP), Computer vision applications, Chatbot development, AI automation workflows, Data analysis and insights, Predictive analytics, Recommendation systems, and AI integration with existing systems.'
            },
            {
                'title': 'Automation Platform Expertise',
                'content': 'I specialize in automation platforms including Botpress for conversational AI, Make.com (formerly Integromat) for workflow automation, Zapier for app integrations, n8n for workflow automation, Microsoft Power Automate, and custom automation solutions. I can build complex workflows that connect multiple platforms and automate business processes.'
            },
            {
                'title': 'Full-Stack AI Projects',
                'content': 'I deliver complete AI projects including: Frontend development (React, Vue, Angular), Backend development (Django, Flask, FastAPI, Node.js), Database design and management, API development and integration, Cloud deployment (AWS, Google Cloud, Azure), Mobile app development, and Full-stack AI applications with user interfaces.'
            },
            {
                'title': 'AI Model Development',
                'content': 'I develop custom AI models for various use cases: Text classification and sentiment analysis, Image recognition and computer vision, Predictive modeling for business forecasting, Recommendation engines for e-commerce, Fraud detection systems, Customer behavior analysis, Natural language generation, and Custom neural networks for specific requirements.'
            },
            {
                'title': 'Chatbot and Conversational AI',
                'content': 'I create intelligent chatbots and conversational AI systems: Customer service chatbots, Lead qualification bots, FAQ automation, Multi-language support, Voice-enabled assistants, Integration with CRM systems, Analytics and performance tracking, and Custom training for domain-specific knowledge.'
            },
            {
                'title': 'Business Process Automation',
                'content': 'I automate business processes using AI and automation tools: Email marketing automation, Lead generation and qualification, Customer onboarding workflows, Data processing and analysis, Report generation, Social media management, Inventory management, and Custom business logic automation.'
            },
            {
                'title': 'Data Analysis and Insights',
                'content': 'I provide data analysis services: Data cleaning and preprocessing, Statistical analysis and modeling, Business intelligence dashboards, Predictive analytics, Customer segmentation, Market trend analysis, Performance metrics and KPIs, and Data visualization and reporting.'
            },
            {
                'title': 'Integration and APIs',
                'content': 'I specialize in system integrations: RESTful API development, Webhook implementations, Third-party service integrations, Database connections and migrations, Cloud service integrations, Payment gateway integrations, Social media API integrations, and Custom middleware development.'
            },
            {
                'title': 'Project Process and Timeline',
                'content': 'My development process includes: Initial consultation and requirements analysis, Project planning and timeline estimation, Regular progress updates and communication, Testing and quality assurance, Deployment and setup, Documentation and training, Ongoing support and maintenance, and Flexible project management approach.'
            },
            {
                'title': 'Pricing and Packages',
                'content': 'I offer flexible pricing options: Hourly rates for ongoing projects, Fixed-price packages for specific deliverables, Retainer agreements for long-term partnerships, Project-based pricing for complete solutions, Consultation sessions for planning and strategy, and Custom packages based on your specific needs and budget.'
            },
            {
                'title': 'Technologies and Tools',
                'content': 'I work with modern technologies: Python (Django, Flask, FastAPI), JavaScript (React, Vue, Node.js), Machine Learning (TensorFlow, PyTorch, Scikit-learn), Cloud platforms (AWS, Google Cloud, Azure), Databases (PostgreSQL, MongoDB, Redis), Automation tools (Botpress, Make.com, Zapier, n8n), AI APIs (OpenAI, Google AI, Anthropic), and DevOps tools (Docker, Kubernetes, CI/CD).'
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



