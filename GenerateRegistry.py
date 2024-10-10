import os
import json
import requests

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
          # package_registration = {
          #   "version": package_version,
          #   "link": item['@id']
          # }
          # registry[package_id].append(package_registration)
        elif item['@type'] == 'nuget:PackageDelete':
          if package_id not in registry:
            # if package_id != 'cnova.nuget.dll':
              # raise Exception(f'Package {package_id} not found in registry and trying to be deleted')
            continue
          if package_version not in registry[package_id]["versions"]:
            # if (package_version != "1.0.0.0" and package_id != 'mmbotjenkins') and (package_version != "0.1.0.0001" and package_id != 'picoware.security.contracts') and (package_version != "1.0.25.0" and package_id != 'unblockapp.libcsharp'):
              # raise Exception(f'Version {package_version} of package {package_id} not found in registry and trying to be deleted')
            continue
          del registry[package_id]["versions"][package_version]          
          if len(registry[package_id]["versions"]) == 0:
            del registry[package_id]
          # print(f'Processing package {packageId} version {package_registration["version"]}')
  output_file = 'registry.json'
  with open(output_file, 'w') as f:
    json.dump(registry, f, indent=2)
  print(f'Registry has been written to {output_file}')

def download_catalog():
  cat_url = 'https://api.nuget.org/v3/catalog0/index.json'
  response = requests.get(cat_url)
  if response.status_code != 200:
    print(f'Failed to download catalog index. Status code: {response.status_code}')
  
  with open('CatalogIndex.json', 'w') as f:
    json.dump(response.json(), f, indent=2)
  print('CatalogIndex.json has been downloaded and saved.')
  
def download_cat_pages() -> int:
  download_catalog()
  if not os.path.exists('pages'):
    os.makedirs('pages')
  
  page_count = -1
  with open('CatalogIndex.json', 'r') as f:
    data = json.load(f)
    page_count = data['count']
    for i, item in enumerate(data['items']):
      page_url = item['@id']
      page_name = page_url.split('/')[-1]
      if os.path.exists(f'pages/{page_name}'):
        print(f'Catalog page {page_name} already exists. Skipping download.')
        continue
      
      # The page is not downloaded yet
      response = requests.get(page_url)
      if response.status_code != 200:
        print(f'Failed to download catalog page {page_name}. Status code: {response.status_code}')
        continue
      with open(f'pages/{page_name}', 'w') as f:
        json.dump(response.json(), f, indent=2)
      print(f'({i}/{page_count}) Catalog page {page_name} has been downloaded and saved.')
  return page_count

if __name__ == "__main__":
  page_count = download_cat_pages()
  open_catalog_pages(count=page_count)