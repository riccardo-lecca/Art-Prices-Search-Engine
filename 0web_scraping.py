import time
import os
import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.common.by import By

# Anasaea Artowork Links Scraping
# Use Firefox as a driver and open the Anasaea page that displays all artworks
driver = webdriver.Firefox()
driver.get('https://anasaea.com/artworks')

# Time to load the page and set "Digital" as the method in the website filters
time.sleep(10)

# Collect links from the first page
linkelement = driver.find_element(By.CSS_SELECTOR, 'div[role="grid"].mt-s28')
links = linkelement.find_elements(By.TAG_NAME, 'a')
all_links = []
for link in links:
    if link.get_attribute('href').startswith('https://anasaea.com/viewArtPiece/'):
        all_links += [link.get_attribute('href')]

# Collect links from all results by scrolling
for i in range(200):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(8)
    linkelement = driver.find_element(By.CSS_SELECTOR, 'div[role="grid"].mt-s28')
    links = linkelement.find_elements(By.TAG_NAME, 'a')
    for link in links:
        if link.get_attribute('href').startswith('https://anasaea.com/viewArtPiece/'):
            all_links += [link.get_attribute('href')]

# Add all links to a txt file
with open('all_links_anasaea.txt', 'w') as file:
    for link in set(all_links):
        file.write(link + '\n')

driver.quit()

# Anasaea metadata and images scraping

# Create a directory where to store images if it doesn't exist
os.makedirs('downloaded_images', exist_ok=True)

# Open the link file and read links
with open("all_links_anasaea.txt", "r") as file:
    links = file.readlines()

# Create a pandas dataframe to store the data form the scraped artworks
df = pd.DataFrame(columns=["Title", "Artist", "Price", "Description", "Dimensions", "Style", "Link", "Image Path"])

# Use Firefox as the driver
driver = webdriver.Firefox()

# Loop over all links
for link in links:
    driver.get(link)
    # Time to load the page and to avoid bot detection
    time.sleep(7)

    title = driver.title
    description = ""
    pic_url = ""
    price = ""
    artist = ""
    dimensions = ""
    style = ""

    # If a page has this title, the artwork cannot load, so the page should be skipped
    if title == "Anasaea - The Universe of Art | Create Your Virtual Gallery and Showcase Your Art in VR":
        continue

    # Get data from the webpage
    else:
        try:
            description_element = driver.find_element(By.XPATH, "/html/head/meta[7]")
            description = description_element.get_attribute("content")
        except:
            continue

        try:
            pic_element = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']")
            pic_url = pic_element.get_attribute("content")
        except:
            continue

        try:
            price_element = driver.find_element(By.XPATH, "/html/body/div/div[1]/div/div[2]/div/button[1]")
            price = price_element.text[4:]  # Slicing to remove the word "BUY"
        except:
            continue

        try:
            artist_element = driver.find_element(By.XPATH, "/html/body/div/div[1]/nav/ol/li[2]/a")
            artist = artist_element.text
        except:
            continue

        try:
            dimensions_element = driver.find_elements(By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div[2]/div/div[1]")
            dimensions = dimensions_element[0].text[12:]
            # "tal" stands for "Mehtod: Digital" after slicing; if that's in place of the dimensions,
            # the artwork doesn't provide them. the location of style depends on this factor.
            if dimensions == "tal":
                dimensions = ""
                stylelement = driver.find_elements(By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div[2]/div/div[2]")
                style = stylelement[0].text[7:]
            else:
                stylelement = driver.find_elements(By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div[2]/div/div[3]")
                style = stylelement[0].text[7:]
        except:
            continue

        # Download the pictures and their path and the other data to the Dataframe.
        if pic_url:
            image_filename = os.path.join('downloaded_images', os.path.basename(pic_url.split('?')[0]))
            response = requests.get(pic_url)
            with open(image_filename, 'wb') as f:
                f.write(response.content)


            df.loc[len(df)] = [title, artist, price, description, dimensions, style, link.strip(), image_filename]
        else:

            df.loc[len(df)] = [title, artist, price, description, dimensions, style, link.strip(), ""]

driver.quit()
df.to_csv("anasaealinks.csv", index=False)

# Artmajeur Link and Image Name Scraping

# Create the final DataFrame
final_df = pd.DataFrame({'Link': all_links,'Image Path': all_image_paths})

driver = webdriver.Firefox()
base_url = "https://www.artmajeur.com/en/artworks/digital-arts?page="

page_number = 1

all_links = []
all_image_paths = []

# Create a directory where to store images if it doesn't exist
os.makedirs('downloaded_images', exist_ok=True)

# Loop to go through multiple pages
while True:

    url = base_url + str(page_number)

    # Load the webpage
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all the elements that contain the artworks
    artwork_divs = soup.find_all('div', class_='thumbnailCellWrapper')

    # If non are found break the loop
    if not artwork_divs:
        time.sleep(10)
        break

    # Extract data from the page
    links = []
    image_paths = []
    for artwork_div in artwork_divs:
        figure = artwork_div.find('figure')
        if figure:
            a_tag = figure.find('a')
            img_tag = figure.find('img')

            link = "https://www.artmajeur.com" + a_tag['href']
            img_url = img_tag['src']
            image_filename = os.path.join('downloaded_images', os.path.basename(img_url.split('?')[0]))

            # Append the data to the lists
            links.append(link)
            image_paths.append(image_filename)

    # Append the data to the final lists
    all_links.extend(links)
    all_image_paths.extend(image_paths)

    # Create a DataFrame for each page
    df = pd.DataFrame({'Link': links,'Image Path': image_paths})

    # Save the DataFrame to a CSV file for each page
    df.to_csv(f'artworks_page_{page_number}.csv', index=False)

    # Increase the page number to load the next page
    page_number += 1

    # Time to load the page and to avoid bot detection
    time.sleep(random.uniform(10, 30))

driver.quit()
final_df.to_csv('artmajeur_all_links.csv', index=False)

# Artmajeur Metadata Scraping

# Create DataFrame to store data from all pages
final_df = pd.DataFrame(columns=["Title", "Artist", "Price", "Themes", "Dimensions", "Style", "Description", "Link", "Image"])

# Path to the folder containing the CSV files scraped in the previous cell
folder_path = 'artmajeur_folder'

# Loop over all files in a folder - each for every page of the website
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        # Read the CSV file
        links_df = pd.read_csv(file_path)

        # Create DataFrame to store data for each page
        df = pd.DataFrame(columns=["Title", "Artist", "Price", "Themes", "Dimensions", "Style", "Description", "Link", "Image"])

        # Initialize the WebDriver - Undetected Chromedriver was used instead of Firefox to avoid bot detection
        driver = Driver(uc=True)

        # Iterate through each link in the CSV file
        for index, row in links_df.iterrows():
            link = row['Link']
            image = row['Image Path']

            driver.get(link)
            time.sleep(random.uniform(1, 3))  # Wait for the page to load

            # Get the page source and parse it with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Get data from the page
            information = driver.title
            regex_pattern = r"^(.*?),\s*.*?by\s*(.*?)\s*\|"
            match = re.match(regex_pattern, information)
            title = match.group(1).strip() if match else ''
            artist = match.group(2).strip() if match else ''
            description_element = soup.select_one("#short_description_text")
            description = description_element.get_text(strip=True) if description_element else ''
            price_meta_tag = soup.select_one("meta[property='product:price:amount']")
            price = price_meta_tag["content"] if price_meta_tag else ''
            try:
                dimension_element = driver.find_element(By.CSS_SELECTOR, "#artworkOriginal > div > div.small > span.image-dimensions")
                dimensions = dimension_element.text
            except:
                dimensions = ''
            categories_elements = soup.select("#my-page > main > div.mt-5.container-fluid.container-lg > div.row > div:nth-child(3) > div.border-top.mt-4.pt-4.d-none")
            categories_actual_elements = categories_elements[0].find_all('a')
            categories = [link.get_text(strip=True) for link in categories_actual_elements]

            # In this categories variable, the first item is usually relevant to the style, while the others describe the topic of the artwork
            style = categories[0] if categories else ''
            themes = categories[1:] if len(categories) > 1 else []

            # Add the extracted data to the Dataframe
            df.loc[len(df)] = [title, artist, price, themes, dimensions, style, description, link, image]

        # Save the results of each page as a separate csv file
        output_file_path = os.path.join(folder_path, f"scraped_{filename}")
        df.to_csv(output_file_path, index=False)

        # Add the extracted data to the final Dataframe
        final_df = pd.concat([final_df, df], ignore_index=True)

        driver.quit()

final_df.to_csv('artmajeur.csv', index=False)