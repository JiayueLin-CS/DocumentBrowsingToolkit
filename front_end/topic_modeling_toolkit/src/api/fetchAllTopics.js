export const fetchAllTopics = async () => {
  const response = await fetch('http://localhost:5050/api/get_all_labels');
  const data = await response.json();
  return data;
};
