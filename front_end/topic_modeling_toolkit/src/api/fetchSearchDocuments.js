export const fetchSearchDocuments = async (
  searchTerm,
  selectedSort,
  selectedOrder,
  selectedFilter,
  filterInput
) => {
  let url = 'http://localhost:5050/api/search?q=' + searchTerm;

  if (selectedSort !== '' && selectedOrder !== '') {
    url += '&sort=' + selectedSort + '&order=' + selectedOrder;
  }

  if (selectedFilter !== '' && filterInput !== '') {
    url += '&filter_field=' + selectedFilter + '&filter_input=' + filterInput;
  }

  const response = await fetch(url);
  const data = await response.json();
  return data;
};
