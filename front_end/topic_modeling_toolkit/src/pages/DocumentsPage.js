import React, { useState, useEffect } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import Header from '../components/Header.js';
import ScaleLoader from 'react-spinners/ScaleLoader';
import { Pagination, Alert, Button, Avatar } from 'flowbite-react';
import { fetchTopicDocuments } from '../api/fetchTopicDocuments';
import { fetchAllowSort } from '../api/fetchAllowSort';
import { fetchAllowFilter } from '../api/fetchAllowFilter';
import Footer from '../components/Footer';

const DocumentsPage = (props) => {
  const { topicId } = useParams();
  const [documents, setDocuments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [allowSort, setAllowSort] = useState([]);
  const [allowFilter, setAllowFilter] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('');
  const [selectedSort, setSelectedSort] = useState('');
  const [selectedOrder, setSelectedOrder] = useState('');
  const [filterInput, setFilterInput] = useState('');
  const documentsPerPage = 10;
  const { state } = useLocation();

  const createAvatar = (name) => {
    const reversedName = name.split(',').reverse().join(' ').trim();
    const url = `https://api.dicebear.com/5.x/initials/svg?seed=${reversedName}`;
    return url;
  };

  const handleOnClick = () => {
    console.log('button clicked');
    fetchTopicDocuments(
      topicId,
      selectedSort,
      selectedOrder,
      selectedFilter,
      filterInput
    ).then((data) => {
      setDocuments(data);
    });
  };

  useEffect(() => {
    fetchTopicDocuments(
      topicId,
      selectedSort,
      selectedOrder,
      selectedFilter,
      filterInput
    ).then((data) => {
      setDocuments(data);
    });
    fetchAllowSort().then((data) => {
      setAllowSort(data);
    });
    fetchAllowFilter().then((data) => {
      setAllowFilter(data);
    });
  }, [topicId, selectedSort, selectedOrder, selectedFilter, filterInput]);

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

  const pageNumbers = [];
  for (let i = 1; i <= Math.ceil(documents.length / documentsPerPage); i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="container mx-auto max-w-4xl">
      {/* Render header */}
      <Header />
      {/* Render topic name */}
      <div className="flex items-center justify-center py-4">
        <Alert color="info">
          <span className="font-bold">Topic: </span> {state.topicName}
        </Alert>
      </div>

      <div className="flex mx-auto max-w-4xl items-center space-x-4 my-5">
        {/* Render sort */}
        <div className="basis-1/4">{renderSort()}</div>
        {/* Render order */}
        <div className="basis-1/4">{renderOrder()}</div>
        <div className="basis-1/4">{renderFilter()}</div>
        <div className="basis-1/4">{renderFilterBy()}</div>
        {/* <div>
          <Button onClick={handleOnClick}>Apply</Button>
        </div> */}
      </div>
      {/* Render documents and page number */}
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
      {/* Render footer */}
      <Footer />
    </div>
  );
};

export default DocumentsPage;
