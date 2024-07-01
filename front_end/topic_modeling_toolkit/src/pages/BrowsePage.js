import React, { useState, useEffect } from 'react';
import Header from '../components/Header.js';
import Pagination from 'rc-pagination';
import ScaleLoader from 'react-spinners/ScaleLoader';
import 'rc-pagination/assets/index.css';
import { Link } from 'react-router-dom';
import { fetchAllTopics } from '../api/fetchAllTopics.js';
import { fetchSearchTopic } from '../api/fetchSearchTopic.js';
import Footer from '../components/Footer.js';

const BrowsePage = () => {
  const [topicLists, setTopicLists] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [query, setQuery] = useState('');
  const topicListsPerPage = 30;

  const handleOnChange = (e) => {
    setQuery(e.target.value);
  };

  const handleOnSubmit = (e) => {
    e.preventDefault();
    fetchSearchTopic(query).then((data) => {
      setTopicLists(data);
    });
  };

  useEffect(() => {
    fetchAllTopics().then((data) => {
      setTopicLists(data);
    });
  }, []);

  // If the 'topicLists' variable is undefined, render a loading spinner
  if (!topicLists) {
    return (
      <div className="flex items-center justify-center h-screen">
        <ScaleLoader color="gray" />
      </div>
    );
  } else {
    const indexOfLastDocument = currentPage * topicListsPerPage;
    const indexOfFirstDocument = indexOfLastDocument - topicListsPerPage;
    const currentDocuments = topicLists.slice(
      indexOfFirstDocument,
      indexOfLastDocument
    );
    const handlePageChange = (page) => {
      setCurrentPage(page);
    };

    const renderTopicLists = currentDocuments.map((topic) => {
      const topicId = topic.id;
      const topicsStr = topic.topic_list.toString().replaceAll(',', ', ');
      return (
        <Link
          key={topicId}
          to={`/documents/${topicId}`}
          state={{ topicName: topicsStr }}
          className="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
        >
          <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            Topic {topicId}
          </h5>
          <p className="font-normal text-gray-700 dark:text-gray-400">
            {topicsStr}
          </p>
        </Link>
      );
    });

    const pageNumbers = [];
    for (
      let i = 1;
      i <= Math.ceil(topicLists.length / topicListsPerPage);
      i++
    ) {
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

    return (
      <div>
        {/* Render header */}
        <Header />
        <div className="flex mx-auto max-w-4xl items-center space-x-4">
          {/* Render search bar */}
          <div className="flex-auto">{renderSearch()}</div>
        </div>

        {/* Render topicLists and page number */}
        <div className="container mx-auto max-w-4xl">
          <div className="grid grid-cols-3 gap-5 mt-5">{renderTopicLists}</div>
          <nav className="my-5">
            <ul className="flex justify-center space-x-2">
              <Pagination
                onChange={handlePageChange}
                current={currentPage}
                total={topicLists.length}
                pageSize={topicListsPerPage}
                showLessItems={true}
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
  }
};

export default BrowsePage;
