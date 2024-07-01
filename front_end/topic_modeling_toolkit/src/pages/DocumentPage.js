import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ScaleLoader from 'react-spinners/ScaleLoader';
import { fetchTopRegion } from '../api/fetchTopRegion';
import { fetchBottomRegion } from '../api/fetchBottomRegion';
import Footer from '../components/Footer';
import { fetchSimilarTopics } from '../api/fetchSimilarTopics';
import { fetchSingleDocument } from '../api/fetchSingleDocument';
import { Alert, Carousel } from 'flowbite-react';
import { fetchSimilarDocuments } from '../api/fetchSimilarDocuments';

function DocumentPage() {
  const { documentId } = useParams();
  const [document, setDocument] = useState(null);
  const [topRegion, setTopRegion] = useState([]);
  const [bottomRegion, setBottomRegion] = useState([]);
  const [similarTopics, setSimilarTopics] = useState([]);
  const [similarDocuments, setSimilarDocuments] = useState([]);

  useEffect(() => {
    fetchSingleDocument(documentId).then((data) => setDocument(data));
    fetchSimilarTopics(documentId).then((data) => setSimilarTopics(data));
    fetchSimilarDocuments(documentId).then((data) => setSimilarDocuments(data));
    fetchTopRegion().then((data) => setTopRegion(data));
    fetchBottomRegion().then((data) => setBottomRegion(data));
  }, [documentId]);

  if (!document || !topRegion || !bottomRegion || !similarTopics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <ScaleLoader color="gray" />
      </div>
    );
  }

  const createAvatar = (name) => {
    // remove commas and swap first and last name
    const reversedName = name.split(',').reverse().join(' ').trim();
    const url = `https://api.dicebear.com/5.x/initials/svg?seed=${reversedName}`;
    return url;
  };

  const renderTopRegion = topRegion.map((region) => {
    const regionName = document.metadata[region];
    return (
      <p
        key={region}
        className="text-base font-bold text-gray-900 dark:text-white"
      >
        {regionName}
      </p>
    );
  });

  const renderBottomRegion = bottomRegion.map((region) => {
    const regionName = document.metadata[region];
    const regionDisplayName = region.toUpperCase();
    return (
      <div key={region}>
        <h2 className="font-semibold text-2xl my-6">{regionDisplayName}</h2>
        <p>{regionName}</p>
      </div>
    );
  });

  const renderSlider = () => {
    const documentsGroups = [];
    for (let i = 0; i < similarDocuments.length; i += 4) {
      documentsGroups.push(similarDocuments.slice(i, i + 4));
    }

    return (
      <div className="h-96">
        <Carousel slide={false}>
          {documentsGroups.map((documents, index) => (
            <div
              key={index}
              className="flex h-full items-center justify-center bg-gray-400/50 dark:bg-gray-700 dark:text-white"
            >
              <div className="grid grid-cols-2 gap-5 mb-5 px-16">
                {documents.map((document) => {
                  const id = document.id;
                  const title = document.metadata.title;
                  return (
                    <Link
                      to={`/document/${id}`}
                      target="_blank"
                      key={id}
                      className="block max-w-sm p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700"
                    >
                      <h1 className="font-semibold text-gray-700 dark:text-gray-400">
                        {title}
                      </h1>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </Carousel>
      </div>
    );
  };

  const renderSimilarTopics = similarTopics.map((topic) => {
    const topicId = topic.id;
    const topicsStr = topic.topic_list.toString().replaceAll(',', ', ');
    console.log(topicsStr);
    return (
      <Link
        to={`/documents/${topicId}`}
        state={{ topicName: topicsStr }}

        key={topicId}
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

  const renderRecommendations = () => {
    if (similarTopics.length === 0) {
      return (
        <div>
          <h2 className="font-semibold text-2xl my-6">Recommendation</h2>
          <Alert color="info">
            <span>No recommendations available</span>
          </Alert>
        </div>
      );
    }
    return (
      <div>
        <h2 className="font-semibold text-2xl my-6">Related Topics</h2>
        <div className="grid grid-cols-2 gap-5 mt-5">{renderSimilarTopics}</div>
        <h2 className="font-semibold text-2xl my-6">Related Documents</h2>
        {renderSlider()}
      </div>
    );
  };

  return (
    <div className="container my-24 px-6 mx-auto max-w-4xl">
      <section className="mb-32 text-gray-800">
        <div className="inline-flex items-center mr-3 text-sm text-gray-900 dark:text-white">
          <img
            className="mr-4 w-16 h-16 rounded-full"
            src={createAvatar(document.metadata.author)}
            alt="avatar"
          />
          <div>{renderTopRegion}</div>
        </div>

        <h1 className="font-bold text-3xl my-6">
          <a
            href={document.metadata.URI}
            target="_blank"
            className="text-gray-900 dark:text-white hover:underline"
            rel="noreferrer"
          >
            {document.metadata.title}
          </a>
        </h1>

        {renderBottomRegion}
        {renderRecommendations()}
      </section>
      {/* Render footer */}
      <Footer />
    </div>
  );
}

export default DocumentPage;
