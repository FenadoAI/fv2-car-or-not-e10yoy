import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const CarRater = () => {
  const [currentCar, setCurrentCar] = useState(null);
  const [showScore, setShowScore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState(null);
  const [voteResult, setVoteResult] = useState(null);

  // Initialize the database with sample cars
  const initializeCars = async () => {
    try {
      const response = await axios.post(`${API}/cars/initialize`);
      console.log(response.data.message);
      setInitialized(true);
      return true;
    } catch (e) {
      console.error("Error initializing cars:", e);
      if (e.response?.status === 500 && e.response?.data?.detail?.includes("already has")) {
        setInitialized(true);
        return true;
      }
      setError("Failed to initialize cars");
      return false;
    }
  };

  // Fetch a random car
  const fetchRandomCar = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/cars/random`);
      setCurrentCar(response.data);
      setShowScore(false);
      setVoteResult(null);
    } catch (e) {
      console.error("Error fetching car:", e);
      if (e.response?.status === 404) {
        // No cars in database, try to initialize
        const initSuccess = await initializeCars();
        if (initSuccess) {
          // Try fetching again after initialization
          setTimeout(fetchRandomCar, 500);
          return;
        }
      }
      setError("Failed to load car");
    } finally {
      setLoading(false);
    }
  };

  // Handle voting
  const handleVote = async (voteType) => {
    if (!currentCar) return;

    try {
      const response = await axios.post(`${API}/cars/${currentCar.id}/vote`, {
        car_id: currentCar.id,
        vote_type: voteType
      });

      setVoteResult(response.data);
      setShowScore(true);

      // Auto-advance to next car after 3 seconds
      setTimeout(() => {
        fetchRandomCar();
      }, 3000);

    } catch (e) {
      console.error("Error voting:", e);
      setError("Failed to record vote");
    }
  };

  useEffect(() => {
    fetchRandomCar();
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-400 mb-4">Error</h1>
          <p className="text-gray-300 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading || !currentCar) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-gray-300">Loading cars...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
            Car Rater
          </h1>
          <p className="text-gray-300">Rate cars as Hot 🔥 or Not ❄️</p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {showScore && voteResult ? (
            // Score Display
            <div className="text-center space-y-6">
              <div className="bg-gray-800 rounded-2xl p-8 shadow-2xl">
                <h2 className="text-2xl font-bold mb-4">
                  {currentCar.year} {currentCar.make} {currentCar.model}
                </h2>
                <div className="text-6xl font-bold mb-4 bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
                  {voteResult.car.hot_percentage}%
                </div>
                <p className="text-xl text-gray-300 mb-2">HOT</p>
                <p className="text-gray-400">
                  {voteResult.car.total_votes} total votes
                </p>
                <p className="text-green-400 mt-4">{voteResult.message}</p>
              </div>
              <p className="text-gray-400">Next car loading...</p>
            </div>
          ) : (
            // Car Display
            <div className="space-y-8">
              {/* Car Image */}
              <div className="bg-gray-800 rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src={currentCar.image_url}
                  alt={`${currentCar.make} ${currentCar.model}`}
                  className="w-full h-96 object-cover"
                  onError={(e) => {
                    e.target.src = 'https://via.placeholder.com/800x450/4B5563/FFFFFF?text=Car+Image';
                  }}
                />
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-center">
                    {currentCar.year} {currentCar.make} {currentCar.model}
                  </h2>
                </div>
              </div>

              {/* Voting Buttons */}
              <div className="flex gap-6 justify-center">
                <button
                  onClick={() => handleVote('not')}
                  className="px-12 py-4 bg-blue-600 text-white text-xl font-bold rounded-xl hover:bg-blue-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  ❄️ NOT
                </button>
                <button
                  onClick={() => handleVote('hot')}
                  className="px-12 py-4 bg-red-600 text-white text-xl font-bold rounded-xl hover:bg-red-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
                >
                  🔥 HOT
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CarRater />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
