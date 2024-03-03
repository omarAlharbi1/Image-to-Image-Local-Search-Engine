# ImageR-Local-image-Search-Engine-using-image
search engine that search using image, (reverse image searching), used to find similar images to an image or to filter dataset from duplications, and much more

# This is the Beta Version.

Functionalities:
1. you can filter a dataset to get a similar images to a corseponding image,
2. you can seperate duplications in a dataset,
3. Planned for more

Usage:
  very simple, just run the tool and follow the instructions,
  if you face any problems with the color or the logo,
  add an argument to the main.py (--no_colors true) to remove colors and logo

you should note:
  if you want to check the duplication in a dataset, the way the tool work is to check

performance:
  the tool support multiprocessing, the number of process is half of the number of threads in your cpu,
  I am planning to allow the adjustion of number of cpus in the future,

  the tool will check the similarity of each image with other images,
  Images compared to others will be excluded from future comparisons.
  and that will make the tool complixity is exactly O(n^2 / 2),
  if you have 30 images,
  the number of processes will be (30+29+28 ... 3+2+1)
  
## Pictures

-<img width="889" src="https://github.com/omarAlharbi1/ImageR-image-Search-Engine-using-image/assets/127057011/76a4c78b-d210-466f-a45c-9cf5712e5a45">
-<img width="678" src="https://github.com/omarAlharbi1/ImageR-image-Search-Engine-using-image/assets/127057011/da5a47a6-f290-4f6e-909c-3ced9f54ccab">
