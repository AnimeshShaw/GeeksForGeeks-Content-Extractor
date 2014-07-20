from bs4 import BeautifulSoup
from urllib2 import urlopen
from xhtml2pdf import pisa
import os, httplib2, re


class G4GExtractor:
    __BASE_WEB_URL = 'http://www.geeksforgeeks.org/category/'
    __FILE_SAVE_PATH = ''
    __CURR_DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

    def __init__(self, path=''):
        """
        Main class constructor and contains methods for crawler and content extraction

        :param path: path where we need to save the files
        :raise Exception: When the path is invalid or write permission error.
        """
        if len(path.strip()) == 0:
            self.__FILE_SAVE_PATH = self.__CURR_DIR_PATH
        elif os.path.exists(path) and os.access(path, os.W_OK):
            self.__FILE_SAVE_PATH = path
        else:
            raise Exception("Either the supplied path doesn't exists or you don't "
                            "have write permissions. \n Check the directory write "
                            "permissions and try again later. Thank You")

    def set_filesave_path(self, path):
        """
        Sets the file save path where contents will be downloaded

        :param path: path to set
        :raise Exception: When the path is invalid or write permission error.
        """
        if os.path.exists(path) and os.access(path, os.W_OK):
            self.__FILE_SAVE_PATH = path
        else:
            raise Exception("Either the supplied path doesn't exists or you don't "
                            "have write permissions. \n Check the directory write "
                            "permissions and try again later. Thank You")

    def set_baseweburl_path(self, path):
        """
        Sets the base url path path which enables you to choose category
        download or download based on tags

        :param path: path to set
        :raise Exception: When the path is invalid or write permission error.
        """
        if os.path.exists(path) and os.access(path, os.W_OK):
            self.__BASE_WEB_URL = path
        else:
            raise Exception("Either the supplied path doesn't exists or you don't "
                            "have write permissions. \n Check the directory write "
                            "permissions and try again later. Thank You")

    @staticmethod
    def __valid_webpage(urllink):

        """
        Checks is a link is valid or not. returns true is Status is 200
        and false if status is 404.

        :param urllink: Link of page whose validity is to be checked
        :return: True if connection status is 200 else False when connection
            status is 404
        """
        h = httplib2.Http()
        resp = h.request(urllink, 'HEAD')
        return int(resp[0]['status']) == 200

    @staticmethod
    def __remove_non_ascii(text):
        """
        Remove unicode or ascii chars from html source

        :param text: Html source
        :return: string after cleaning text
        """
        return ''.join([i if ord(i) < 128 else '' for i in text])

    def extract_content_and_save(self, cat_list, pdf=False):
        """
        Returns a list of all the links whose content is to be crawled.
        This method takes care of the pagination and gets all links for
        tags or categories

        :param cat_list: List of the categories whose links are to be crawled
        :return: List of all gathered links
        """

        #List to store all the links.
        totallinks = []

        #String to store html code
        pagedata = ''

        #Iterate for each category
        for cat in cat_list:
            #Create Directory path.
            newpath = self.__FILE_SAVE_PATH + cat

            #Create Directory for each category.
            os.mkdir(newpath)

            #Prepare URL to extract number of pagination pages
            url = self.__BASE_WEB_URL + cat + "/"

            #Check if webpage exists and is valid
            if self.__valid_webpage(url):
                pagedata = urlopen(url).read()
                soup = BeautifulSoup(pagedata)

                #Get number of Pagination pages for each category
                pages = soup.find('span', {"class": "pages"})
                cat_content_pages = int(str(pages.text).split()[3])

                for i in range(1, cat_content_pages + 1):

                    listofLinks = []

                    #Prepare URL to extract links
                    if i == 1:
                        url = self.__BASE_WEB_URL + cat + "/"
                    else:
                        url = self.__BASE_WEB_URL + cat + "/page/" + str(i) + "/"

                    print("Working with %s" % url)

                    #Check if the webpages have Status 200 or 404
                    if self.__valid_webpage(url):
                        pagedata = urlopen(url).read()
                        soup = BeautifulSoup(pagedata)

                        #Find all the title links in the page
                        content_links = soup.findAll("h2", class_="post-title")

                        #Iterate every page and save the content links in a list
                        for link in content_links:
                            mainLink = \
                                str(link.findAll("a")[0]).split("<a href=")[1].split('rel="bookmark"')[0].strip(
                                    '"').split(
                                    '"')[0]
                            listofLinks.append(mainLink)
                            self.save_pages(listofLinks, newpath, pdf)
                        totallinks.append(listofLinks)
                    else:
                        print url + ' Returned Status 404'
            else:
                print url + ' Returned Status 404'

        return totallinks

    def save_pages(self, listoflinks, newpath, pdf=False):

        """
        Function to save the pages either as pdf or html files

        :param listoflinks: List of all the links to be saved
        :param newpath: Path to directory where files will be saved
        :param pdf: If True then pdf files are generated else files are saved as .html
        """
        for link in listoflinks:
            pagedata = urlopen(link).read()
            soup = BeautifulSoup(pagedata)
            title = soup.find('h2', {"class": "post-title"})

            #Create File name to be saved as
            filename = re.sub('[^a-zA-Z0-9\n\.]', '_', title.text)

            #If path ends with trailing slash then remove it.
            if newpath.endswith('/'):
                newpath = newpath[:len(newpath) - 1]

            try:
                if os.path.exists(newpath):
                    filePath = newpath + "/" + filename
                    if pdf:
                        self.convertHtmlToPdf(pagedata, filePath + '.pdf')
                    else:
                        with open(filePath + '.html', "wb") as f:
                            f.write(self.__remove_non_ascii(pagedata))

            except OSError as e:
                print(e.message)

    @staticmethod
    def convertHtmlToPdf(sourceHtml, outputFilename):
        """
         Open output file for writing (truncated binary) and
         converts HTML code into pdf file format

        :param sourceHtml: The html source to be converted to pdf
        :param outputFilename: Name of the output file as pdf
        :return: Error if pdf not generated successfully
        """
        resultFile = open(outputFilename, "w+b")

        # convert HTML to PDF
        pisaStatus = pisa.CreatePDF(sourceHtml, dest=resultFile)

        # close output file
        resultFile.close()

        # return True on success and False on errors
        return pisaStatus.err


def demo():
    """
    A demo run if this app.
    """
    demo_cat_list = ['c-puzzles','c-arrays']
    path = '/root/PycharmProjects/GeekForGeeks-Spider/'
    demo = G4GExtractor(path)
    totallinks = demo.extract_content_and_save(demo_cat_list)
    print("Number of links crawled and saved is %d" % totallinks)

if __name__ == '__main__':
    demo()
