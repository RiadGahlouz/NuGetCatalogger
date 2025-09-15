import os
import json
import requests
import aiohttp
import asyncio

def open_catalog_pages(count: int):
  registry = {}
  pages_folder = 'pages'
  if not os.path.exists(pages_folder):
    print(f"The folder {pages_folder} does not exist.")
    return
  
  for json_file_idx in range(count):
    json_file = f'page{json_file_idx}.json'
    file_path = os.path.join(pages_folder, json_file)
    with open(file_path, 'r') as f:
      data = json.load(f)
      print(f"==> Processing file {json_file}")
      for item in data["items"]:
        display_name = item['nuget:id']
        package_id = display_name.lower()
        package_version = item['nuget:version']
        if item['@type'] == 'nuget:PackageDetails':
          if(package_id not in registry):
            registry[package_id] = {}
            registry[package_id]["display_name"] = display_name
            registry[package_id]["versions"] = {}
          registry[package_id]["versions"][package_version] = item['@id']
        elif item['@type'] == 'nuget:PackageDelete':
          if package_id not in registry:
            # raise Exception(f'Package {package_id} not found in registry and trying to be deleted')
            continue
          if package_version not in registry[package_id]["versions"]:
            # raise Exception(f'Version {package_version} of package {package_id} not found in registry and trying to be deleted')
            continue
          del registry[package_id]["versions"][package_version]          
          if len(registry[package_id]["versions"]) == 0:
            del registry[package_id]
  output_file = 'registry.json'
  with open(output_file, 'w') as f:
    json.dump(registry, f, indent=2)
  print(f'Registry has been written to {output_file}')

def download_catalog():
  cat_url = 'https://api.nuget.org/v3/catalog0/index.json'
  response = requests.get(cat_url)
  if response.status_code != 200:
    raise Exception(f'Failed to download catalog index. Status code: {response.status_code}')
  
  with open('CatalogIndex.json', 'w') as f:
    json.dump(response.json(), f, indent=2)
  print('CatalogIndex.json has been downloaded and saved.')

async def download_cat_page_async(page_url: str, session: aiohttp.ClientSession):
  # The page is not downloaded yet
  page_name = page_url.split('/')[-1]
  if os.path.exists(f'pages/{page_name}'):
    print(f'Catalog page {page_name} already exists. Skipping download.')
    return
  try:
    async with session.get(url=page_url) as response:
      # resp = await response.read()
      json_content = await response.json(content_type=None)
      with open(f'pages/{page_name}', 'w') as f:
        json.dump(json_content, f, indent=2)
      print(f'Catalog page {page_name} has been downloaded and saved.')
  except Exception as e:
    print("Failed to download catalog page {} due to {}: {}".format(page_name, e.__class__, e))
  

async def download_cat_pages() -> int:
  download_catalog()
  if not os.path.exists('pages'):
    os.makedirs('pages')
  
  page_count = -1
  with open('CatalogIndex.json', 'r') as f:
    data = json.load(f)
    page_count = data['count']
    
  async with aiohttp.ClientSession() as session:
    ret = await asyncio.gather(*(download_cat_page_async(item['@id'], session) for item in data['items']))

  return page_count

if __name__ == "__main__":
  page_count = asyncio.run(download_cat_pages())
  open_catalog_pages(count=page_count)