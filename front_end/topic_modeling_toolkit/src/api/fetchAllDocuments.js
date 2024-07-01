export const fetchAllDocuments = async () => {
  const response = await fetch('http://localhost:5050/api/docs');
  const data = await response.json();
  return data;
};
