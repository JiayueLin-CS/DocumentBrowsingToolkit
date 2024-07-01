import java.io.*;
import java.nio.file.Paths;
import java.text.ParseException;
import java.util.*;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.*;
import org.apache.lucene.document.Field.Store;
import org.apache.lucene.index.*;
import org.apache.lucene.queryparser.classic.MultiFieldQueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.store.*;
import org.ini4j.Ini;
import org.json.JSONObject;
import py4j.GatewayServer;

public class Search {
    private static String pathOfJSON;
    private static String pathOfIndex;
    private static final String CONFIG_FILE =
            System.getProperty("user.dir") + File.separator + "TopicModelingKit/config.ini";

    /**
     * Initializes the lucene indexing process
     *
     * @throws IOException if there is an error during the indexing process
     */
    public static void init() throws IOException {
        System.out.println("Indexing the documents...");
        File file = new File(pathOfJSON);
        int docsCount = 0;
        // Use try-with-resources to automatically close the reader
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            Directory directory = FSDirectory.open(Paths.get(pathOfIndex));
            StandardAnalyzer analyzer = new StandardAnalyzer();
            IndexWriterConfig config = new IndexWriterConfig(analyzer);
            IndexWriter w = new IndexWriter(directory, config);

            // Check if the json file exists
            if (!file.exists()) {
                System.out.println("The JSON file does not exist");
                w.close();
                return;
            }

            String nextLine;
            while ((nextLine = br.readLine()) != null) {
                // Read json object from the json file
                JSONObject obj = new JSONObject(nextLine);

                // Check if the json object has the required fields
                if (!obj.has("id") || !obj.has("text")) {
                    throw new IOException("The JSON file is not in the correct format");
                }

                String id = obj.getString("id");
                // Use the title and abstract for lucene indexing
                String text = obj.getString("text");
                docsCount++;
                addDoc(w, id, text);
            }
            w.forceMerge(1);
            w.close();

            System.out.println("Number of documents in the index: " + docsCount);

        } catch (IOException e) {
            System.err.println("An error occurred while indexing the documents: " + e.getMessage());
        }
    }

    /**
     * Searches for documents that match the given query string
     *
     * @param searchMode the search mode, either "BM-25" or "TF-IDF"
     * @param hitsPerPage the maximum number of hits
     * @param query the query string
     * @return a list of Lucene document indexes that match the given query string
     * @throws IOException if an I/O exception occurs
     * @throws ParseException if a parsing exception occurs while parsing the query string
     * @throws org.apache.lucene.queryparser.classic.ParseException if a parsing exception occurs
     *         while parsing the query string
     */
    public static List<String> search(String searchMode, int hitsPerPage, String query)
            throws IOException, org.apache.lucene.queryparser.classic.ParseException {
        if (hitsPerPage <= 0) {
            throw new IllegalArgumentException("hitsPerPage must be greater than 0");
        }
        if (query == null || query.isEmpty()) {
            throw new IllegalArgumentException("query cannot be null or empty");
        }

        System.out.println("==============================================");

        try (StandardAnalyzer analyzer = new StandardAnalyzer();
                Directory directory = FSDirectory.open(Paths.get(pathOfIndex));
                IndexReader reader = DirectoryReader.open(directory)) {
            IndexSearcher searcher = new IndexSearcher(reader);
            MultiFieldQueryParser multiFieldParser =
                    new MultiFieldQueryParser(new String[] {"text"}, analyzer);

            // Set similarity with BM-25 or TF-IDF
            if (Objects.equals(searchMode, "BM-25")) {
                System.out.println("Searching mode: BM25");
                searcher.setSimilarity(new BM25Similarity(1.0f, 0.65f));
            } else {
                System.out.println("Searching mode: TF-IDF");
            }

            Query q = multiFieldParser.parse(query);
            TopDocs docs = searcher.search(q, hitsPerPage, Sort.RELEVANCE);
            ScoreDoc[] hits = docs.scoreDocs;

            System.out.println("Found " + hits.length + " hits.");

            List<String> list = new ArrayList<>();
            for (int i = 0; i < hits.length; ++i) {
                int docId = hits[i].doc;
                Document d = searcher.doc(docId);
                list.add(d.get("id"));
                System.out.println("#" + (i + 1) + " " + d.get("id"));
            }

            System.out.println("==============================================");
            return list;
        } catch (IOException | org.apache.lucene.queryparser.classic.ParseException e) {
            // Handle any exceptions that might occur
            System.err.println("Error occurred during search: " + e.getMessage());
            throw e;
        }
    }

    /**
     * Adds a document to an IndexWriter with the given id and text
     *
     * @param indexWriter the IndexWriter to add the document to
     * @param id the id of the document
     * @param text the text content of the document
     * @throws IOException if there is an error adding the document to the IndexWriter
     */
    private static void addDoc(IndexWriter w, String id, String text) throws IOException {
        Document doc = new Document();
        doc.add(new TextField("id", id, Store.YES));
        doc.add(new TextField("text", text, Store.YES));
        w.addDocument(doc);
    }

    /**
     * The main method
     *
     * @param args the command line arguments
     * @throws IOException if there is an error during the indexing process
     */
    public static void main(String[] args) throws IOException {
        Ini ini = new Ini(new File(CONFIG_FILE));
        pathOfJSON = ini.get("dataset", "pathOfJSON");
        pathOfIndex = ini.get("dataset", "pathOfIndex");
        System.out.println("==============================================");
        System.out.println("Reading the config file...");
        System.out.println("pathOfJSON: " + pathOfJSON + "\npathOfIndex: " + pathOfIndex);

        // Initialize the lucene indexing process, munually set the port number to avoid conflict
        GatewayServer gatewayServer = new GatewayServer(new Search(), 25333);
        gatewayServer.start();
        System.out.println("==============================================");
        System.out.println("Gateway Server Started");
        System.out.println("==============================================");

        boolean loadLuceneIndex = Boolean.parseBoolean(ini.get("model-training", "loadLuceneIndex"));
        if (!loadLuceneIndex) {
            System.out.println("Lucene Indexing Process");
            System.out.println("==============================================");
            init();
        } else {
            System.out.println("Load Lucene Index");
            System.out.println("==============================================");
        }
    }
}
