export const fetchSingleDocument = async (documentId) => {
  const response = await fetch(
    'http://localhost:5050/api/document/' + documentId
  );
  const data = await response.json();
  return data;
};
