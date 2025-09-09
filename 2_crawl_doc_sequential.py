import asyncio
from typing import List 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig 
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator 
import requests 
from xml.etree import ElementTree

async def crawl_sequential(urls: List[str]):
    print("\n\n== Sequential Crawling with Session Reuse ==\n\n")

    browser_config = BrowserConfig(
        headless = True, 
        # For better performance in docker or low-memory environments :
        # extra_args = ['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage'],
        
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator = DefaultMarkdownGenerator(),
    )

    # create the crawler (opens the browser)
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = 'session1' # Reuse the same session accross all the urls 
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id,
            )
            if result.success:
                print(f"Successfully crawled: {url}")
                # E.g. check markdown length
                print(f"Markdown length: {len(result.markdown.raw_markdown)}")




            #     # To save the markdown files seperately
            #     filename = url.replace("https://", "").replace("http://", "").replace("/", "_") + ".md"
            #     with open(filename, "w", encoding="utf-8") as f:
            #         f.write(result.markdown.raw_markdown)
            #     print(f"Markdown saved to {filename}")
            # else:
            #     print(f"Failed: {url} - Error: {result.error_message}")


            # To save the markdown files in one file
            output_file = "crawled_content.md"

            if result.success:
                print(f"Successfully crawled: {url}")
                print(f"Markdown length: {len(result.markdown.raw_markdown)}")

                # Define the section header
                section = f"\n\n# Content from: {url}\n\n"
                content = result.markdown.raw_markdown

                # Append to the markdown file
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(section)
                    f.write(content)

                print(f"Content from {url} appended to {output_file}")




    finally:
        # After all URLs are done, close the crawler (and the browser)
        await crawler.close()

def get_pydantic_ai_docs_urls():
    """
    Fetches all URLs from the Pydantic AI documentation.
    Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
    Returns:
        List[str]: List of URLs
    """            
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

async def main():
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_sequential(urls)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())