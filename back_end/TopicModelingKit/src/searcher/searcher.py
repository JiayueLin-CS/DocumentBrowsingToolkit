from py4j.java_gateway import JavaGateway
# This line create the connection between python and JVM
gateway = JavaGateway()


class Searcher():
    # Set up the lucene index of the dataset and store in a fixed data path
    def setUpIndex(self):
        print("Setting up the index of text...")
        gateway.entry_point.init()
        return

    def search_TFIDF(self, size: int, query: str, page: int) -> list:
        """" search documents with a given query using TF-IDF """
        jList = gateway.entry_point.search("TF-IDF", size, query)
        # tuen the java arraylist to python list.
        pyList = list(jList)
        return pyList

    def search_BM25(self, size: int, query: str) -> list:
        """" search documents with a given query using BM_25 """
        # envoke the java lucene search method to get the document id list
        jList = gateway.entry_point.search("BM-25", size, query)
        # tuen the java arraylist to python list.
        pyList = list(jList)
        return pyList

# below is a sample test for the searcher method.
# test = Searcher()
# test.setUpIndex()
# result = test.search_BM25(1000, "mathematical")
# print(result)