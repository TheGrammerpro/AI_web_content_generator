from langchain_community.llms import Ollama
import requests
import datetime as dt
from dotenv import load_dotenv
import os

load_dotenv()

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.getenv("NEWS_API")
NUMBER_OF_ARTICLES = 20

header = {
    "x-api-key": NEWS_API_KEY
}


class ArticleGenerate:
    def __init__(self, topic):
        # API parameters to check on the most popular articles in the past seven days
        self.parameters = {
            "from": (dt.datetime.now() - dt.timedelta(days=7)).strftime("%Y-%m-%d"),
            "to": dt.datetime.now().strftime("%Y-%m-%d"),
            "pageSize": NUMBER_OF_ARTICLES,
            "sortBy": "popularity",
            "excludeDomains": "removed.com, yahoo.com",
        }
        self.article_number = 1
        self.prompt = ""
        self.context_articles = ""
        self.titles = []
        self.authors = []
        self.descriptions = []
        self.urls = []
        self.image_urls = []
        self.result = ""
        self.refined_result = ""
        self.html_ready_result = ""
        self.prepare_prompt(topic)
        self.prepare_article(topic)

    def prepare_article(self, article_topic):
        """Prepares the data for processing by organizing titles, authors, descriptions, URLs, images
        and contents into lists"""
        self.parameters["q"] = article_topic,
        news_raw = requests.get(url=NEWS_ENDPOINT, params=self.parameters, headers=header).json()
        print(f"\nAPI response: {news_raw["status"]}\n")
        for article in news_raw["articles"]:
            self.context_articles += f"Article {self.article_number}:\n {article["title"]}\n{article["description"]}\n"
            self.titles.append(article["title"])
            self.authors.append(article["author"])
            self.descriptions.append(article["description"])
            self.urls.append(article["url"])
            self.image_urls.append(article["urlToImage"])
            self.article_number += 1

    def prepare_prompt(self, article_topic):
        """Create a prompt for LLM to create the most suitable prompt for the chosen topic"""
        ai_prompt = (f"Create a prompt for yourself in order to optimize your output in creating an article that "
                     f"matches the characteristics and the format of the best rated and most engaging articles in "
                     f"the field of {article_topic}. \nThe prompt should note that topic descriptions are "
                     f"gonna be provided above."
                     f"\nAnd an article that will contain all key points of these descriptions is the desired output."
                     f"\nIndicate that the desired output should be elaborated on in a fun and interesting way."
                     f"\nIndicate that the output should only contain the generated article. no introductions such as "
                     f"'Here is the article you requested' or any indication that states the instructions followed."
                     f"\nIndicate that the article should be between 1000 words and 2000 words and that is should be"
                     f"written following the format of the provided articles.")
        llm_prompt_gen = Ollama(model="llama3")
        self.prompt = llm_prompt_gen.invoke(ai_prompt)
        print(f"\nHere is the AI generated prompt:\n{self.prompt}\n")

    def create_article(self):
        """Creates an article based on the prompt and the provided article data"""
        print(f"\nHere are the articles: {self.context_articles}\n")
        create_prompt = f"""
            News articles:
    
            {self.context_articles}
    
            ---
    
            Answer based on the following prompt:
            {self.prompt}"""
        llm_article_generator = Ollama(model="llama3")
        self.result = llm_article_generator.invoke(create_prompt)

    def refine_article(self):
        """Refines and reviews the initial article using another instance of the LLM"""
        refine_prompt = f"""
                    First edition of the article:
                    
                    {self.result}
                    
                    ---
                    
                    Answer based on the following prompt:
                    You are professional news article editor who maximizes engagement and produces the finest articles.
                    Refine this article and make it production ready. Ensure it contains no odd characters and is 
                    readable with proper paragraphing and format. Your output should include only the article.
                    *Do not explain what you did or add any external introductions such as 'here is the article you
                    requested.' or 'here is the refined article'.
                    *Leave out any parts you think are not relevant to the main topic. Keep the article between 1200 
                    and 2500 words"""

        llm_article_refiner = Ollama(model="llama3")
        self.refined_result = llm_article_refiner.invoke(refine_prompt)

    def make_html_ready(self):
        """Formats the refined article into a html ready article"""
        html_prompt = f"""
                            Article to format:

                            {self.refined_result}

                            ---

                            Answer based on the following prompt:
                            You specialize in formatting text to html to be displayed properly in a website. Your output
                            should be be production ready. And set to be displayed on a website right away:
                            *Convert all formatting in the article above to html.
                            *Do not use <h1> or <h2>.
                            *Make the article comfortably readable with your formatting.
                            *Do not explain what you did or add any external introductions such as 'here is the article
                             you requested.' or 'here is the formatted article'"""

        llm_html_formatter = Ollama(model="llama3")
        html_ready_result = llm_html_formatter.invoke(html_prompt)
        return html_ready_result
