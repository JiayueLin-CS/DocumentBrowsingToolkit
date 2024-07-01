export const fetchTopRegion = async () => {
  const response = await fetch("http://localhost:5050/api/get_top_region");
  const data = await response.json();
  return data;
};