export const fetchBottomRegion = async () => {
  const response = await fetch("http://localhost:5050/api/get_bottom_region");
  const data = await response.json();
  return data;
};