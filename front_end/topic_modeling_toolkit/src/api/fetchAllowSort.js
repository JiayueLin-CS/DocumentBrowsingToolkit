export const fetchAllowSort = async () => {
  const response = await fetch("http://localhost:5050/api/get_allow_sort");
  const data = await response.json();
  return data;
};