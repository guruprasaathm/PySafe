import os
import zipfile

def retrieve_file_paths(dirName):
  filePaths = []
  for root, directories, files in os.walk(dirName):
    for filename in files:
        filePath = os.path.join(root, filename)
        filePaths.append(filePath)
  return filePaths
 
def main(dir_name, output_filename):
  filePaths = retrieve_file_paths(dir_name)
   
  zip_file = zipfile.ZipFile(output_filename+'.zip', 'w')
  with zip_file:
    for file in filePaths:
      zip_file.write(file)

main("my_dir", "my_dir_archived")