from G4GExtractor import G4GExtractor

d = G4GExtractor()
#You can set the path by calling a method or passing the path as constructor
d.set_filesave_path('/root/PycharmProjects/GeekForGeeks-Spider/')

#You can set the base url path for tag or category. Here we show an example with tag.
#Of Course tags much match the tags of the site else you will receive error.
d.set_baseweburl_path('http://www.geeksforgeeks.org/tag/')

#Set the tag list
tag_list = ['recursion','geometric-algorithms']

#call this function to save the files and if yoy send a second parameter as True
# then files will be saved as pdf.
totallinks = len(d.extract_content_and_save(tag_list, True))
print("Number of links crawled and saved is %d" % totallinks)
