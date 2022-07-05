# Number-plate-lookup
Number-plate-lookup is an application which takes input from the webcam once a second as an image. With help of image-filtering and text-recognition the application tries to find a numberplate and extract
the text. I could not find a free API for a swedish numberplate-database so the application scrapes the information about the owner of the car from the websites "biluppgifter.se" and "merinfo.se".

### Good to know
1. The application scrapes the owner information directly from the websites, so if the websites changes structure it can result in the application breaking.
2. The plate recognition works best with clear images with the plate in a good angle.