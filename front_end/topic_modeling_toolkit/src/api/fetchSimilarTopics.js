export const fetchSimilarTopics = async (docId) => {
  let url = 'http://127.0.0.1:5050/api/get_similar_topics?doc_id=' + docId;
  const response = await fetch(url);
  const data = await response.json();
  return data;
};
