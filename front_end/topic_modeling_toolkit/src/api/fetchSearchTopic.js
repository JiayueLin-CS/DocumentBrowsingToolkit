export const fetchSearchTopic = async (query) => {
  let url = 'http://localhost:5050/api/labels?topic_query=' + query;
  const response = await fetch(url);
  const data = await response.json();
  return data;
};
