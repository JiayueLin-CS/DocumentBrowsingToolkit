import React, { useState, useEffect } from 'react';
import { fetchAllDocuments } from '../api/fetchAllDocuments';
import { fetchSearchDocuments } from '../api/fetchSearchDocuments';
import { fetchAllowSort } from '../api/fetchAllowSort';
import { fetchAllowFilter } from '../api/fetchAllowFilter';
import { Link } from 'react-router-dom';
import Header from '../components/Header.js';
import ScaleLoader from 'react-spinners/ScaleLoader';
import Footer from '../components/Footer';
import { Pagination, Avatar } from 'flowbite-react';

const SearchPage = () => {
  const [documents, setDocuments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);

  const [allowSort, setAllowSort] = useState([]);
  const [allowFilter, setAllowFilter] = useState([]);

  const [query, setQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('');
  const [selectedSort, setSelectedSort] = useState('');
  const [selectedOrder, setSelectedOrder] = useState('');
  const [filterInput, setFilterInput] = useState('');
  const documentsPerPage = 30;

  const handleOnChange = (e) => {
    setQuery(e.target.value);
  };

  const handleOnSubmit = (e) => {
    e.preventDefault();
    fetchSearchDocuments(
      query,
      selectedSort,
      selectedOrder,
      selectedFilter,
      filterInput
    ).then((data) => {
      setDocuments(data);
    });
  };

  const createAvatar = (name) => {
    const reversedName = name.split(',').reverse().join(' ').trim();
    const url = `https://api.dicebear.com/5.x/initials/svg?seed=${reversedName}`;
    return url;
  };

  useEffect(() => {
    fetchAllDocuments().then((data) => {
      setDocuments(data);
    });
    fetchAllowSort().then((data) => {
      setAllowSort(data);
    });
    fetchAllowFilter().then((data) => {
      setAllowFilter(data);
    });
  }, []);

  if (!documents) {
    return (
      <div class="flex items-center justify-center h-screen">
        <ScaleLoader color="gray" />
      </div>
    );
  }

  const indexOfLastDocument = currentPage * documentsPerPage;
  const indexOfFirstDocument = indexOfLastDocument - documentsPerPage;
  const currentDocuments = documents.slice(
    indexOfFirstDocument,
    indexOfLastDocument
  );

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const renderDocuments = currentDocuments.map((document) => {
    const renderAvatar = () => {
      if (document.metadata.author) {
        return (
          <img
            alt="Author avatar"
            src={createAvatar(document.metadata.author)}
            className="h-14 w-14 rounded-lg object-cover"
          />
        );
      } else {
        return <Avatar />;
      }
    };

    const renderAbstract = () => {
      if (document.metadata.abstract) {
        return (
          <p className="line-clamp-5 text-sm text-gray-700">
            {document.metadata.abstract}
          </p>
        );
      } else {
        return (
          <p className="line-clamp-5 text-sm text-gray-700">
            No abstract available
          </p>
        );
      }
    };

    const renderDescription = () => {
      if (document.metadata.author && document.metadata.year) {
        return (
          <div className="mt-2 sm:flex sm:items-center sm:gap-2">
            <div className="flex items-center gap-1 text-gray-500">
              <p className="text-xs">{document.metadata.author}</p>
            </div>

            <span className="hidden sm:block" aria-hidden="true">
              &middot;
            </span>

            <p className="hidden sm:block sm:text-xs sm:text-gray-500">
              {document.metadata.year}
            </p>
          </div>
        );
      } else {
        return null;
      }
    };
    return (
      <article
        key={document.id}
        className="block bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
      >
        <div className="flex items-start gap-4 p-4 sm:p-6 lg:p-8">
          {renderAvatar()}

          <div>
            <h3 className="font-semibold sm:text-xl">
              <Link to={`/document/${document.id}`}>
                {document.metadata.title}
              </Link>
            </h3>

            {renderAbstract()}
            {renderDescription()}
          </div>
        </div>
      </article>
    );
  });

  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(documents.length / documentsPerPage); i++) {
    pageNumbers.push(i);
  }

  const renderSearch = () => {
    return (
      <form onSubmit={handleOnSubmit}>
        <label className="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">
          Search
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg
              aria-hidden="true"
              className="w-5 h-5 text-gray-500 dark:text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              ></path>
            </svg>
          </div>
          <input
            value={query}
            onChange={handleOnChange}
            type="search"
            id="default-search"
            className="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            placeholder="Search Documents..."
            required
          ></input>
          <button
            type="submit"
            className="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
          >
            Search
          </button>
        </div>
      </form>
    );
  };

  const renderOrder = () => {
    if (allowSort.length === 0) {
      return null;
    }
    return (
      <div className="relative max-w-xs mx-auto">
        <select
          id="order"
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          onChange={(event) => setSelectedOrder(event.target.value)}
        >
          <option defaultValue hidden>
            Order by
          </option>
          <option value="desc">Order by descending</option>
          <option value="asc">Order by ascending</option>
        </select>
      </div>
    );
  };

  const renderSort = () => {
    const sortOptions = allowSort.map((field) => (
      <option key={field} value={field}>
        Sort by {field}
      </option>
    ));

    if (allowSort.length === 0) {
      return null;
    }

    return (
      <div className="relative max-w-xs mx-auto">
        <select
          id="order"
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          onChange={(event) => setSelectedSort(event.target.value)}
        >
          <option defaultValue hidden>
            Sort by
          </option>
          {sortOptions}
        </select>
      </div>
    );
  };

  const renderFilter = () => {
    const filterOptions = allowFilter.map((field) => (
      <option key={field} value={field}>
        Filter by {field}
      </option>
    ));

    if (allowFilter.length === 0) {
      return null;
    }

    return (
      <div className="relative max-w-xs mx-auto">
        <select
          id="order"
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          onChange={(event) => setSelectedFilter(event.target.value)}
        >
          <option defaultValue hidden>
            Filter by
          </option>
          {filterOptions}
        </select>
      </div>
    );
  };

  const renderFilterBy = () => {
    let label = '';
    if (selectedFilter) {
      label = `Input ${selectedFilter}...`;
    } else {
      label = 'Input filter...';
    }

    if (allowFilter.length === 0) {
      return null;
    }

    return (
      <div className="">
        <input
          type="text"
          id="default-input"
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          onChange={(event) => setFilterInput(event.target.value)}
          placeholder={label}
        ></input>
      </div>
    );
  };

  return (
    <div>
      {/* Render header */}
      <Header />
      <div className="flex mx-auto max-w-4xl items-center space-x-4">
        {/* Render search bar */}
        <div className="flex-auto">{renderSearch()}</div>
      </div>

      <div className="flex mx-auto max-w-4xl items-center space-x-4 my-5">
        {/* Render sort */}
        <div className="basis-1/4">{renderSort()}</div>
        {/* Render order */}
        <div className="basis-1/4">{renderOrder()}</div>
        <div className="basis-1/4">{renderFilter()}</div>
        <div className="basis-1/4">{renderFilterBy()}</div>
      </div>

      {/* Render documents and page number */}
      <div className="container mx-auto max-w-4xl">
        <div className="grid grid-cols-1 gap-4">{renderDocuments}</div>
        <nav className="my-5">
          <ul className="flex justify-center space-x-2">
            <Pagination
              onPageChange={handlePageChange}
              currentPage={currentPage}
              totalPages={pageNumbers.length}
              showIcons={true}
            />
          </ul>
        </nav>
      </div>
      {/* Render footer */}
      <div className="container mx-auto max-w-4xl">
        <Footer />
      </div>
    </div>
  );
};

export default SearchPage;
