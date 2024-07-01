export const fetchAllowFilter = async () => {
  const response = await fetch("http://localhost:5050/api/get_allow_filter");
  const data = await response.json();
  return data;
};